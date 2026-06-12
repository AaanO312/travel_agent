# ---- 基础镜像 ----
FROM python:3.12-slim

# 设置工作目录（容器里所有命令默认在这里执行）
WORKDIR /app

# ---- 安装依赖 ----
# 先复制 requirements.txt（单独一层，改代码不用重装依赖）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# ---- 复制项目代码 ----
COPY . .

# ---- 暴露端口 ----
# FastAPI 默认 8000，Streamlit 默认 8501
EXPOSE 8000 8501

# ---- 启动命令（由 docker-compose 覆盖，这里给个默认值） ----
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
