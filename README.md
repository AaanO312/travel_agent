# Multi-Agent 旅行规划系统

基于 LangGraph 的 4 Agent 协作旅行规划系统——天气查询、行程规划、预算估算、协调合并，真实天气 API + LLM 路由。

## 架构

```
用户输入：目的地、日期、预算、偏好
              │
              ▼
      ┌──────────────┐
      │ 天气 Agent    │  ← Open-Meteo API（免费实时天气）
      │ 地理编码 +      │
      │ 天气预报查询    │
      └──────┬───────┘
             │
             ▼
      ┌─────────────────────────┐
      │     并行 Fan-out         │
      │  ┌──────────┐ ┌───────┐ │
      │  │行程 Agent │ │预算   │ │
      │  │每日安排    │ │Agent  │ │
      │  │景点+交通   │ │花费估算│ │
      │  └────┬─────┘ └──┬────┘ │
      └───────┼──────────┼──────┘
              │          │
              ▼          ▼
      ┌──────────────────────────┐
      │   协调 Agent              │
      │   合并 + 冲突检测 + 润色   │
      │   雨天户外？自动提醒       │
      └──────────┬───────────────┘
                 │
                 ▼
      ┌──────────────────┐
      │   最终旅行计划      │
      │   天气+行程+预算    │
      └──────────────────┘
```

## 技术栈

- **Agent 框架**: LangGraph（StateGraph + 并行 Fan-out + MemorySaver）
- **LLM**: 通义千问 qwen-plus
- **实时数据**: Open-Meteo API（地理编码 + 天气预报，免费无需 Key）
- **前端**: Streamlit
- **并发**: LangGraph 原生并行（行程 Agent 与预算 Agent 同时运行）

## 项目结构

```
travel_agent/
├── app.py                     # Streamlit 前端
├── graph/
│   ├── state.py               # TravelState 定义
│   ├── workflow.py            # 状态图：weather → (itinerary ∥ budget) → coordinator
│   └── model.py               # LLM 单例
├── agents/
│   ├── weather_agent.py       # 真实天气 API 调用
│   ├── itinerary_agent.py     # 每日行程规划
│   ├── budget_agent.py        # 分项预算估算
│   └── coordinator_agent.py   # 合并 + 冲突检测
├── prompts/                   # 3 个 Prompt 模板
├── config/settings.yml
├── utils/
└── requirements.txt
```

## 与普通 Pipeline 的区别

| | Pipeline（链式） | 本系统（Multi-Agent） |
|---|---|---|
| 执行模式 | A→B→C→D 串行 | 天气→(行程∥预算)→协调 |
| 并行能力 | 无 | 行程+预算同时运行 |
| 外部数据 | 无 | 真实天气 API |
| Agent 数量 | 1 个 | 4 个各司其职 |
| 冲突检测 | 无 | 协调 Agent 自动检测 |

## 运行

```powershell
cd travel_agent
.\.venv\Scripts\activate
$env:DASHSCOPE_API_KEY = "your_key"
streamlit run app.py
```
