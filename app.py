import streamlit as st
import os
import uuid
from graph.workflow import build_graph
from utils.logger import logger

# API Key
try:
    if "DASHSCOPE_API_KEY" in st.secrets:
        os.environ["DASHSCOPE_API_KEY"] = st.secrets["DASHSCOPE_API_KEY"]
except Exception:
    pass

st.set_page_config(page_title="Multi-Agent 旅行规划", page_icon="")
st.title("Multi-Agent 旅行规划")
st.caption("表单填入需求 → 生成方案 → 对话式微调，直到满意")

# ---- 初始化 ----
if "graph" not in st.session_state:
    st.session_state["graph"] = build_graph()
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = uuid.uuid4().hex
if "phase" not in st.session_state:
    st.session_state["phase"] = "input"       # input | weather | running | review | chat | done
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ---- 侧边栏：信息输入 ----
with st.sidebar:
    st.header("旅行信息")

    destination = st.text_input("目的地", placeholder="如：成都", disabled=(st.session_state["phase"] != "input"))
    start_date = st.date_input("出发日期", disabled=(st.session_state["phase"] != "input"))
    end_date = st.date_input("返程日期", disabled=(st.session_state["phase"] != "input"))
    budget = st.number_input("总预算（元）", 500, 100000, 5000, 500, disabled=(st.session_state["phase"] != "input"))
    num_people = st.number_input("人数", 1, 10, 2, disabled=(st.session_state["phase"] != "input"))
    preferences = st.selectbox("偏好", ["美食+人文", "自然风光", "购物+都市", "亲子乐园", "小众深度游"], disabled=(st.session_state["phase"] != "input"))

    if st.session_state["phase"] == "input":
        run_btn = st.button("开始规划", type="primary", use_container_width=True)
    else:
        st.success("信息已提交")

    st.divider()
    show_weather = st.checkbox("显示天气详情", value=False, disabled=(st.session_state["phase"] in ("input", "running")))

# ---- 阶段1：收集信息 → 查天气 ----
if "run_btn" in locals() and run_btn:
    if not destination.strip():
        st.error("请输入目的地")
    elif end_date <= start_date:
        st.error("返程日期必须晚于出发日期")
    else:
        st.session_state["phase"] = "weather"
        graph = st.session_state["graph"]
        config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

        with st.spinner("正在查询天气..."):
            events = graph.stream({
                "destination": destination.strip(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "budget": budget,
                "num_people": num_people,
                "preferences": preferences,
            }, config, stream_mode="values")
            for _ in events:
                pass

        snap = graph.get_state(config)
        weather = snap.values.get("weather_summary", "")
        st.session_state["weather_data"] = weather
        st.rerun()

# ---- 阶段2：展示天气，用户确认 ----
if st.session_state["phase"] == "weather":
    weather = st.session_state.get("weather_data", "")
    st.info("### 天气查询结果")
    st.markdown(weather)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("继续规划", type="primary", use_container_width=True):
            st.session_state["phase"] = "running"
            st.rerun()
    with col2:
        if st.button("重新输入", use_container_width=True):
            st.session_state["phase"] = "input"
            st.session_state["thread_id"] = uuid.uuid4().hex
            st.rerun()

# ---- 阶段3：生成行程+预算+协调 ----
if st.session_state["phase"] == "running":
    with st.spinner("4 个 Agent 协作中...\n\n行程 Agent + 预算 Agent 并行执行"):
        graph = st.session_state["graph"]
        config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

        events = graph.stream(None, config, stream_mode="values")
        for _ in events:
            pass

        snap = graph.get_state(config)
        st.session_state["plan_data"] = {
            "merged_plan": snap.values.get("merged_plan", ""),
            "conflicts": snap.values.get("conflicts", ""),
            "itinerary": snap.values.get("itinerary", ""),
            "budget_plan": snap.values.get("budget_plan", ""),
        }
        st.session_state["phase"] = "review"
        st.rerun()

# ---- 阶段4：展示方案 + 对话式调整 ----
if st.session_state["phase"] in ("review", "chat"):
    plan = st.session_state.get("plan_data", {})

    # 冲突警告
    if plan.get("conflicts") and "警告" in plan["conflicts"]:
        st.warning(plan["conflicts"])

    # 展示方案
    tab1, tab2, tab3 = st.tabs(["完整计划", "行程详情", "预算明细"])
    with tab1:
        st.markdown(plan.get("merged_plan", ""))
    with tab2:
        st.markdown(plan.get("itinerary", ""))
    with tab3:
        st.markdown(plan.get("budget_plan", ""))

    if show_weather and st.session_state.get("weather_data"):
        with st.expander("天气详情"):
            st.markdown(st.session_state["weather_data"])

    st.divider()
    st.caption("对方案不满意？直接说哪里要改——'第一天太赶了'、'预算超了'、'换个酒店'")

    # 对话式调整
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    feedback = st.chat_input("说你想怎么改...")

    if feedback:
        st.session_state["chat_history"].append({"role": "user", "content": feedback})

        with st.spinner("协调 Agent 正在调整方案..."):
            from agents.coordinator_agent import coordinator_agent
            from graph.state import TravelState
            import copy

            # 把用户反馈注入到协调 Agent 重新生成
            snap = st.session_state["graph"].get_state(
                {"configurable": {"thread_id": st.session_state["thread_id"]}}
            )
            current = dict(snap.values)
            current["user_feedback"] = feedback

            result = coordinator_agent(current)
            new_plan = result.get("merged_plan", "")

            st.session_state["plan_data"]["merged_plan"] = result.get("merged_plan", new_plan)
            st.session_state["plan_data"]["conflicts"] = result.get("conflicts", "")
            st.session_state["phase"] = "chat"

        st.session_state["chat_history"].append({"role": "assistant", "content": "已根据你的反馈调整方案，看看现在的版本～"})
        st.rerun()

    # 满意按钮
    if st.button("满意，输出最终方案", type="primary"):
        st.session_state["phase"] = "done"
        st.rerun()

# ---- 阶段5：完成 ----
if st.session_state["phase"] == "done":
    st.success("Final Plan Ready")
    st.markdown(st.session_state.get("plan_data", {}).get("merged_plan", ""))

    if st.button("开始新规划", use_container_width=True):
        st.session_state["phase"] = "input"
        st.session_state["thread_id"] = uuid.uuid4().hex
        st.session_state["chat_history"] = []
        st.session_state["plan_data"] = {}
        st.session_state["weather_data"] = ""
        st.rerun()
