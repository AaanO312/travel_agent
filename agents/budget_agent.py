"""Agent 3：预算估算 - 根据行程+偏好+修订意见估算花费"""
from graph.state import TravelState
from graph.model import get_model
from utils.config_loader import load_prompt
from utils.logger import logger


def budget_agent(state: TravelState) -> dict:
    revision = state.get("revision_notes", "")
    if revision:
        logger.info("[Budget Agent] 收到修订指令，重新估算...")
    else:
        logger.info("[Budget Agent] 开始估算预算...")

    model = get_model()
    prompt_template = load_prompt("budget_prompt")
    prompt = prompt_template.format(
        destination=state["destination"],
        start_date=state["start_date"],
        end_date=state["end_date"],
        budget=state["budget"],
        num_people=state["num_people"],
        preferences=state["preferences"],
        itinerary=state.get("itinerary", ""),
        revision_notes=_format_revision(revision),
    )

    response = model.invoke(prompt)
    content = response.content.strip()
    logger.info(f"[Budget Agent] 预算{'重新' if revision else ''}估算完成，{len(content)} 字符")
    return {"budget_plan": content}


def _format_revision(notes: str) -> str:
    if not notes:
        return "（首轮规划，无特殊要求）"
    return f"**上一轮审核的修改要求，请务必遵守**：\n{notes}"
