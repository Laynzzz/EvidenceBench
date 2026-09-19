FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_LINK_MODE=copy \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_CACHE=/models \
    MLFLOW_DISABLE_AGENT_HINT=1 OMP_NUM_THREADS=4
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.17
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --frozen --extra ml --no-dev --no-editable --no-cache
COPY configs ./configs
RUN useradd --uid 10001 --create-home evidencebench
USER evidencebench
EXPOSE 8000
CMD [".venv/bin/uvicorn", "evidencebench.serving.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
