"""Agent 2：行程规划 - 根据天气+偏好+修订意见生成每日行程"""
from graph.state import TravelState
from graph.model import get_model
from utils.config_loader import load_prompt
from utils.logger import logger


def itinerary_agent(state: TravelState) -> dict:
    revision = state.get("revision_notes", "")
    if revision:
        logger.info("[Itinerary Agent] 收到修订指令，重新规划...")
    else:
        logger.info("[Itinerary Agent] 开始规划行程...")

    model = get_model()
    prompt_template = load_prompt("itinerary_prompt")
    prompt = prompt_template.format(
        destination=state["destination"],
        start_date=state["start_date"],
        end_date=state["end_date"],
        preferences=state["preferences"],
        num_people=state["num_people"],
        weather_summary=state["weather_summary"],
        revision_notes=_format_revision(revision),
        budget_plan=state.get("budget_plan", ""),
    )

    response = model.invoke(prompt)
    content = response.content.strip()
    logger.info(f"[Itinerary Agent] 行程{'重新' if revision else ''}规划完成，{len(content)} 字符")
    return {"itinerary": content}


def _format_revision(notes: str) -> str:
    if not notes:
        return "（首轮规划，无特殊要求）"
    return f"**上一轮审核的修改要求，请务必遵守**：\n{notes}"
