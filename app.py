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
st.caption("4 个 AI Agent 协作：天气查询 -> 行程 + 预算并行 -> 协调合并")

# ---- 初始化 ----
if "graph" not in st.session_state:
    st.session_state["graph"] = build_graph()
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = uuid.uuid4().hex
if "result" not in st.session_state:
    st.session_state["result"] = None

# ---- 输入区 ----
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        destination = st.text_input("目的地", placeholder="如：成都")
        budget = st.number_input("总预算（元）", min_value=500, max_value=100000, value=5000, step=500)
    with col2:
        start_date = st.date_input("出发日期")
        end_date = st.date_input("返程日期")
    with col3:
        preferences = st.selectbox("旅行偏好", ["美食+人文", "自然风光", "购物+都市", "亲子乐园", "小众深度游"])
        num_people = st.number_input("人数", min_value=1, max_value=10, value=2)

    run_btn = st.button("开始规划", type="primary", use_container_width=True)

# ---- 执行 ----
if run_btn:
    if not destination:
        st.error("请输入目的地")
    elif end_date <= start_date:
        st.error("返程日期必须晚于出发日期")
    else:
        with st.spinner("Multi-Agent 协作中..."):
            try:
                graph = st.session_state["graph"]
                config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

                final = graph.invoke({
                    "destination": destination.strip(),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "budget": budget,
                    "num_people": num_people,
                    "preferences": preferences,
                }, config)

                st.session_state["result"] = final
                logger.info(f"旅行规划完成：{destination}")
                st.rerun()

            except Exception as e:
                logger.error(f"执行失败：{e}")
                st.error(f"出错了：{e}")

# ---- 结果展示 ----
if st.session_state["result"]:
    r = st.session_state["result"]

    # 进度展示
    st.divider()
    st.subheader("Agent 执行状态")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("天气 Agent", "完成" if r.get("weather_summary") else "等待")
    c2.metric("行程 Agent", "完成" if r.get("itinerary") else "等待")
    c3.metric("预算 Agent", "完成" if r.get("budget_plan") else "等待")
    c4.metric("协调 Agent", "完成" if r.get("merged_plan") else "等待")

    st.divider()

    # 冲突提示
    if r.get("conflicts") and "警告" in r["conflicts"]:
        st.warning(r["conflicts"])

    # 标签页：分别展示各 Agent 输出
    tab1, tab2, tab3, tab4 = st.tabs(["完整计划", "天气详情", "行程方案", "预算明细"])

    with tab1:
        st.markdown(r.get("merged_plan", r.get("final_plan", "规划中...")))

    with tab2:
        if r.get("weather_summary"):
            st.markdown(r["weather_summary"])
        else:
            st.info("天气数据获取中...")

    with tab3:
        if r.get("itinerary"):
            st.markdown(r["itinerary"])
        else:
            st.info("行程规划中...")

    with tab4:
        if r.get("budget_plan"):
            st.markdown(r["budget_plan"])
        else:
            st.info("预算估算中...")

    if st.button("重新规划", use_container_width=True):
        st.session_state["result"] = None
        st.session_state["thread_id"] = uuid.uuid4().hex
        st.rerun()

    st.caption("天气数据：Open-Meteo API（免费实时数据）| LLM：通义千问 qwen-plus")
