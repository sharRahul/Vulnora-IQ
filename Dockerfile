FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VULNORAIQ_HOST=0.0.0.0 \
    VULNORAIQ_PORT=8787

WORKDIR /app

COPY pyproject.toml README.md ./
COPY agent_testing ./agent_testing
COPY benchmarks ./benchmarks
COPY config ./config
COPY core ./core
COPY dashboards ./dashboards
COPY examples ./examples
COPY integrations ./integrations
COPY modules ./modules
COPY payloads ./payloads
COPY rag_testing ./rag_testing
COPY reports ./reports
COPY scripts ./scripts
COPY webui ./webui

RUN pip install --no-cache-dir -e .

EXPOSE 8787

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/healthz', timeout=3).read()"

CMD ["sh", "-c", "vulnoraiq-web --host ${VULNORAIQ_HOST} --port ${VULNORAIQ_PORT}"]
