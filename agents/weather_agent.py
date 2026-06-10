import requests
from graph.state import TravelState
from utils.logger import logger

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def weather_agent(state: TravelState) -> dict:
    """Agent 1：查询目的地真实天气"""
    logger.info(f"[Weather Agent] 查询 {state['destination']} 天气...")

    city = state["destination"]
    start = state["start_date"]
    end = state["end_date"]

    # Step 1: 地理编码 city → lat/lon
    geo_resp = requests.get(GEOCODING_URL, params={"name": city, "count": 1, "language": "zh"})
    geo_data = geo_resp.json()

    if not geo_data.get("results"):
        logger.warning(f"[Weather Agent] 未找到城市 {city}，使用模拟数据")
        return _mock_weather(state)

    loc = geo_data["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    city_name = loc.get("name", city)

    # Step 2: 获取天气预报
    weather_resp = requests.get(WEATHER_URL, params={
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weather_code"],
        "timezone": "Asia/Shanghai",
    })

    if weather_resp.status_code != 200:
        logger.warning(f"[Weather Agent] 天气API失败，使用模拟数据")
        return _mock_weather(state)

    wdata = weather_resp.json()
    daily = wdata.get("daily", {})

    # Step 3: 格式化天气摘要
    lines = [f"**{city_name} {start} 至 {end} 天气预报**\n"]
    for i, date_str in enumerate(daily.get("time", [])):
        tmax = daily["temperature_2m_max"][i]
        tmin = daily["temperature_2m_min"][i]
        rain = daily["precipitation_sum"][i]
        code = daily["weather_code"][i]
        desc = _weather_code_desc(code)
        rain_note = f"，降水 {rain}mm" if rain > 0 else ""
        lines.append(f"- {date_str}：{desc}，{tmin}°C ~ {tmax}°C{rain_note}")

    summary = "\n".join(lines)
    logger.info(f"[Weather Agent] 天气查询完成")

    return {
        "weather_summary": summary,
        "weather_daily": summary,
    }


def _weather_code_desc(code: int) -> str:
    """WMO 天气码转中文"""
    mapping = {0: "晴", 1: "大部晴", 2: "多云", 3: "阴",
               45: "雾", 48: "雾凇", 51: "小雨", 53: "中雨", 55: "大雨",
               61: "阵雨", 63: "中阵雨", 65: "大阵雨",
               71: "小雪", 73: "中雪", 75: "大雪",
               80: "阵雨", 81: "中阵雨", 82: "大阵雨",
               95: "雷暴", 96: "雷暴+冰雹", 99: "强雷暴+冰雹"}
    return mapping.get(code, f"多云({code})")


def _mock_weather(state: TravelState) -> dict:
    """模拟天气数据（API失败时兜底）"""
    lines = [f"**{state['destination']} {state['start_date']} 至 {state['end_date']} 天气（模拟）**\n"]
    from datetime import datetime, timedelta
    s = datetime.fromisoformat(state["start_date"])
    e = datetime.fromisoformat(state["end_date"])
    days = (e - s).days + 1
    import random
    for i in range(days):
        d = s + timedelta(days=i)
        tmax = random.randint(22, 33)
        tmin = random.randint(15, 22)
        desc = random.choice(["晴", "多云", "阵雨"])
        lines.append(f"- {d.strftime('%Y-%m-%d')}：{desc}，{tmin}°C ~ {tmax}°C")
    summary = "\n".join(lines)
    return {"weather_summary": summary, "weather_daily": summary}
