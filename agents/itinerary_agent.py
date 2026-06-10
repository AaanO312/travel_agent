"""Agent 2：行程规划 - 根据天气和偏好生成每日行程"""
from graph.state import TravelState
from graph.model import get_model
from utils.config_loader import load_prompt
from utils.logger import logger


def itinerary_agent(state: TravelState) -> dict:
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
    )

    response = model.invoke(prompt)
    content = response.content.strip()
    logger.info(f"[Itinerary Agent] 行程规划完成，{len(content)} 字符")
    return {"itinerary": content}
