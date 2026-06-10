"""Agent 3：预算估算 - 交通/住宿/餐饮/门票分项估算"""
from graph.state import TravelState
from graph.model import get_model
from utils.config_loader import load_prompt
from utils.logger import logger


def budget_agent(state: TravelState) -> dict:
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
    )

    response = model.invoke(prompt)
    content = response.content.strip()
    logger.info(f"[Budget Agent] 预算估算完成，{len(content)} 字符")
    return {"budget_plan": content}
