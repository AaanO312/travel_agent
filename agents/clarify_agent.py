"""Agent 0：需求澄清 - 对话式收集用户旅行需求"""
import json
from graph.state import TravelState
from graph.model import get_model
from utils.config_loader import load_prompt
from utils.logger import logger


def clarify_agent(state: TravelState) -> dict:
    logger.info("[Clarify Agent] 检查信息完整性...")

    model = get_model()
    prompt_template = load_prompt("clarify_prompt")

    # 已收集的信息
    collected = {
        "destination": state.get("destination", ""),
        "start_date": state.get("start_date", ""),
        "end_date": state.get("end_date", ""),
        "budget": state.get("budget", 0),
        "num_people": state.get("num_people", 1),
        "preferences": state.get("preferences", ""),
    }

    # 最新用户消息
    user_message = ""
    if state.get("messages"):
        user_message = state["messages"][-1].content

    prompt = prompt_template.format(
        collected=json.dumps(collected, ensure_ascii=False),
        user_message=user_message,
    )

    response = model.invoke(prompt)
    content = response.content.strip()
    logger.info(f"[Clarify Agent] 判断结果: {content[:200]}")

    # 解析 LLM 输出
    info_complete = "完整" in content or "COMPLETE" in content

    if info_complete:
        # 尝试从用户消息中提取结构化信息
        extracted = _extract_info(content)
        return {
            "phase": "weather_review",
            "info_complete": True,
            "clarify_question": "",
            **extracted,
        }
    else:
        return {
            "phase": "clarify",
            "info_complete": False,
            "clarify_question": content,
        }


def _extract_info(output: str) -> dict:
    """尝试从 LLM 输出中解析结构化字段"""
    result = {}
    try:
        # LLM 可能在最后输出 JSON
        if "{" in output and "}" in output:
            start = output.index("{")
            end = output.rindex("}") + 1
            data = json.loads(output[start:end])
            for key in ["destination", "start_date", "end_date", "budget", "num_people", "preferences"]:
                if key in data and data[key]:
                    result[key] = data[key]
    except Exception:
        pass
    return result
