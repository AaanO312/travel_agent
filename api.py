"""FastAPI 接口：将旅行 Multi-Agent 包装为 REST API"""
from fastapi import FastAPI
from pydantic import BaseModel
from graph.workflow import build_graph

app = FastAPI(title="Travel Multi-Agent API")
graph = build_graph()


class TravelRequest(BaseModel):
    destination: str
    start_date: str       # YYYY-MM-DD
    end_date: str
    budget: int = 5000
    num_people: int = 2
    preferences: str = "美食+人文"


@app.post("/plan")
def plan_travel(req: TravelRequest):
    """旅行规划接口：输入需求，返回完整计划"""
    result = graph.invoke({
        "destination": req.destination,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "budget": req.budget,
        "num_people": req.num_people,
        "preferences": req.preferences,
    }, {"configurable": {"thread_id": f"api_{req.destination}"}})

    return {
        "weather": result.get("weather_summary", ""),
        "itinerary": result.get("itinerary", ""),
        "budget_plan": result.get("budget_plan", ""),
        "merged_plan": result.get("merged_plan", ""),
        "conflicts": result.get("conflicts", ""),
    }


@app.get("/health")
def health():
    return {"status": "ok"}
