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

    # 两个都完成 → 协调合并
    workflow.add_edge("itinerary", "coordinator")
    workflow.add_edge("budget", "coordinator")

    workflow.add_edge("coordinator", END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
