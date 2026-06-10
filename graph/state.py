from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class TravelState(TypedDict):
    # 对话阶段：clarify → weather_review → running → plan_review → done
    phase: str

    # 用户输入
    destination: str
    start_date: str
    end_date: str
    budget: int
    num_people: int
    preferences: str

    # 澄清阶段：LLM 向用户追问
    clarify_question: str      # Agent 向用户问的问题
    info_complete: bool        # 信息是否齐全

    # 天气 Agent 输出
    weather_summary: str
    weather_daily: str

    # 行程 Agent 输出（并行）
    itinerary: str

    # 预算 Agent 输出（并行）
    budget_plan: str

    # 协调 Agent 输出
    conflicts: str
    merged_plan: str
    final_plan: str

    # 用户确认标记
    weather_confirmed: bool
    plan_confirmed: bool

    # 用户反馈
    user_feedback: str

    # LangGraph 内置
    messages: Annotated[list[BaseMessage], add_messages]
