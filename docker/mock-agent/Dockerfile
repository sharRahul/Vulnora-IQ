FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MOCK_AGENT_HOST=0.0.0.0 MOCK_AGENT_PORT=9090
WORKDIR /app
RUN groupadd --system mockagent && useradd --system --gid mockagent --home-dir /app --shell /usr/sbin/nologin mockagent
COPY app.py /app/app.py
USER mockagent
EXPOSE 9090
CMD ["python", "/app/app.py"]
