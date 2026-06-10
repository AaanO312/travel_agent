"""Agent 4：协调合并 + 冲突检测 + 最终润色"""
from graph.state import TravelState
from graph.model import get_model
from utils.config_loader import load_prompt
from utils.logger import logger


def coordinator_agent(state: TravelState) -> dict:
    logger.info("[Coordinator Agent] 开始合并与冲突检测...")

    model = get_model()
    prompt_template = load_prompt("coordinator_prompt")

    feedback = state.get("user_feedback", "")
    feedback_section = f"\n**用户反馈**：\n{feedback}\n" if feedback else ""

    prompt = prompt_template.format(
        destination=state["destination"],
        start_date=state["start_date"],
        end_date=state["end_date"],
        budget=state["budget"],
        weather_summary=state["weather_summary"],
        itinerary=state["itinerary"],
        budget_plan=state["budget_plan"],
        feedback_section=feedback_section,
    )

    response = model.invoke(prompt)
    content = response.content.strip()
    logger.info(f"[Coordinator Agent] 合并完成，{len(content)} 字符")

    # 检测天气冲突关键词
    conflicts = _detect_conflicts(state, content)

    return {
        "merged_plan": content,
        "conflicts": conflicts,
        "final_plan": content,
    }


def _detect_conflicts(state: TravelState, plan: str) -> str:
    """简单冲突检测：雨天+户外活动"""
    conflicts = []
    weather = state["weather_summary"].lower()
    has_rain = any(w in weather for w in ["雨", "雷", "雪"])

    if has_rain:
        outdoor = ["爬山", "徒步", "海滩", "游乐园", "日出", "缆车", "漂流", "露营", "骑行", "观景台"]
        for keyword in outdoor:
            if keyword in plan:
                conflicts.append(f"警告：天气有雨但计划含户外项目「{keyword}」，建议准备备选方案")

    return "\n".join(conflicts) if conflicts else "未检测到明显冲突"
