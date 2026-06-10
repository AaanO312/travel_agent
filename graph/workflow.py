from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import TravelState
from agents.weather_agent import weather_agent
from agents.itinerary_agent import itinerary_agent
from agents.budget_agent import budget_agent
from agents.coordinator_agent import coordinator_agent


def build_graph() -> StateGraph:
    workflow = StateGraph(TravelState)

    workflow.add_node("weather", weather_agent)
    workflow.add_node("itinerary", itinerary_agent)
    workflow.add_node("budget", budget_agent)
    workflow.add_node("coordinator", coordinator_agent)

    workflow.set_entry_point("weather")

    # 天气 → 并行（行程 + 预算）
    workflow.add_edge("weather", "itinerary")
    workflow.add_edge("weather", "budget")

    # 两个都完成 → 协调审核
    workflow.add_edge("itinerary", "coordinator")
    workflow.add_edge("budget", "coordinator")

    # 智能循环：审核不通过 → 回到行程+预算重做（最多 3 轮）
    workflow.add_conditional_edges("coordinator", _route_after_review, {
        "revise": "itinerary",   # 回到 itinerary + budget 并行重做
        "done": END,
    })
    # 重做时 budget 也需要重新跑（因为行程可能变了）
    workflow.add_edge("itinerary", "coordinator")
    workflow.add_edge("budget", "coordinator")

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def _route_after_review(state: TravelState) -> str:
    """审核通过 → 结束；不通过且未超次数 → 重做"""
    if state.get("coordinator_approved"):
        return "done"
    return "revise"
