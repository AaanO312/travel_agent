from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class TravelState(TypedDict):
    # 用户输入
    destination: str
    start_date: str
    end_date: str
    budget: int
    num_people: int
    preferences: str

    # 天气 Agent 输出
    weather_summary: str
    weather_daily: str

    # 行程 Agent 输出
    itinerary: str

    # 预算 Agent 输出
    budget_plan: str

    # 协调 Agent 输出
    conflicts: str
    merged_plan: str
    final_plan: str

    # 智能审核 + 自动重做
    coordinator_approved: bool     # 协调 Agent 是否通过
    revision_notes: str            # 协调 Agent 的修改指令（给行程/预算 Agent 参考）
    revision_count: int            # 已修订轮数

    # 用户反馈
    user_feedback: str

    # LangGraph 内置
    messages: Annotated[list[BaseMessage], add_messages]
