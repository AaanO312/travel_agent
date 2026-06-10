"""Agent 4：智能质量审核 + 自动修订决策"""
from typing import Generator
from graph.state import TravelState
from graph.model import get_model
from utils.config_loader import load_prompt
from utils.logger import logger

MAX_REVISIONS = 3


def build_coordinator_prompt(state: dict) -> str:
    """构建协调 Agent 的 prompt（供图执行和流式调用共用）"""
    prompt_template = load_prompt("coordinator_prompt")

    feedback = state.get("user_feedback", "")
    feedback_section = f"\n**用户反馈**：\n{feedback}\n" if feedback else ""

    return prompt_template.format(
        destination=state["destination"],
        start_date=state["start_date"],
        end_date=state["end_date"],
        budget=state["budget"],
        weather_summary=state["weather_summary"],
        itinerary=state["itinerary"],
        budget_plan=state["budget_plan"],
        feedback_section=feedback_section,
    )


def stream_coordinator_response(state: dict) -> Generator[str, None, str]:
    """流式生成协调 Agent 的回复，逐 chunk yield 给 Streamlit 展示"""
    model = get_model()
    prompt = build_coordinator_prompt(state)

    full_content = ""
    for chunk in model.stream(prompt):
        full_content += chunk.content
        yield chunk.content

    return full_content


def coordinator_agent(state: TravelState) -> dict:
    revision_count = state.get("revision_count", 0)
    logger.info(f"[Coordinator Agent] 第 {revision_count + 1} 轮审核...")

    model = get_model()
    prompt = build_coordinator_prompt(state)

    # 流式调用 LLM，边生成边累积（为后续迁移到 astream_events 做准备）
    content = ""
    for chunk in model.stream(prompt):
        content += chunk.content
    content = content.strip()
    logger.info(f"[Coordinator Agent] 审核完成，{len(content)} 字符")

    # 判断是否通过
    approved = "审核通过" in content or "PASS" in content
    is_final = approved or revision_count >= MAX_REVISIONS - 1

    if is_final:
        # 最终输出：去掉内部标记，润色为交付版本
        final_plan = clean_for_output(content)
        return {
            "merged_plan": final_plan,
            "final_plan": final_plan,
            "coordinator_approved": True,
            "conflicts": extract_issues(content),
        }
    else:
        # 未通过，生成修改指令发给行程/预算 Agent
        return {
            "coordinator_approved": False,
            "revision_notes": content,
            "revision_count": revision_count + 1,
            "conflicts": extract_issues(content),
        }


def extract_issues(content: str) -> str:
    """提取审核发现的问题"""
    issues = []
    for line in content.split("\n"):
        if any(kw in line for kw in ["问题", "冲突", "超支", "过密", "警告", "建议", "修改"]):
            issues.append(line.strip())
    return "\n".join(issues[:5]) if issues else ""


def clean_for_output(text: str) -> str:
    """去掉内部审核标记，输出干净版本"""
    lines = []
    for line in text.split("\n"):
        if line.strip().startswith("【内部") or line.strip().startswith("修订指令"):
            continue
        lines.append(line)
    return "\n".join(lines)
