from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class TravelState(TypedDict):
    # 用户输入
    destination: str
    start_date: str
    end_date: str
    budget: int               # 总预算（元）
    num_people: int
    preferences: str          # 偏好：美食/人文/自然/购物/亲子

    # 天气 Agent 输出
    weather_summary: str      # 天气概况
    weather_daily: str        # 每日详细天气

    # 行程 Agent 输出（并行）
    itinerary: str            # 每日行程安排

    # 预算 Agent 输出（并行）
    budget_plan: str          # 预算明细

    # 协调 Agent 输出
    conflicts: str            # 检测到的冲突
    merged_plan: str          # 合并后的完整计划

    # 人工审核
    approved: bool            # 用户是否确认
    user_feedback: str        # 用户修改意见

    # 最终输出
    final_plan: str

    # LangGraph 内置
    messages: Annotated[list[BaseMessage], add_messages]
