"""Five bounded, read-only API routes with local structured request logs."""

import json
import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import Field

from evidencebench.schemas import Record

logger = logging.getLogger("evidencebench.requests")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.propagate = False


class QueryRequest(Record):
    query: str = Field(min_length=1, max_length=2000)
    document_id: str | None = Field(default=None, max_length=100)


class RetrieveRequest(QueryRequest):
    k: int = Field(default=10, ge=1, le=100)


def create_app(pipeline=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        if pipeline is None:
            from pathlib import Path

            from evidencebench.serving.pipeline import load_runtime

            app.state.pipeline = load_runtime(
                Path(os.environ.get("EVIDENCEBENCH_RELEASE", "configs/release.yaml"))
            )
        yield

    app = FastAPI(title="EvidenceBench", version="0.1.0", lifespan=lifespan)
    app.state.pipeline = pipeline
    lock = threading.Lock()

    def execute(request, operation):
        request_id = uuid4().hex
        started = time.perf_counter()
        if not lock.acquire(blocking=False):
            logger.info(
                json.dumps(
                    {
                        "request_id": request_id,
                        "operation": operation,
                        "status": "failure",
                        "reason": "busy",
                        "http_status": 429,
                        "elapsed_ms": (time.perf_counter() - started) * 1000,
                    }
                )
            )
            return JSONResponse(
                {"request_id": request_id, "status": "failure", "reason": "busy"}, 429
            )
        try:
            filters = {"document_id": request.document_id} if request.document_id else {}
            current = app.state.pipeline
            result = (
                current.ask(request.query, filters)
                if operation == "query"
                else current.retrieve(request.query, filters, request.k)
            )
            result["request_id"] = request_id
            status_code = 200
            if result["status"] == "failure":
                status_code = 504 if result.get("reason") == "generation_timeout" else 502
        except Exception as exc:
            logger.error(json.dumps({"request_id": request_id, "error_type": type(exc).__name__}))
            result = {"request_id": request_id, "status": "failure", "reason": "dependency_failure"}
            status_code = 503
        finally:
            lock.release()
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "operation": operation,
                    "status": result["status"],
                    "http_status": status_code,
                    "reason": result.get("reason"),
                    "elapsed_ms": (time.perf_counter() - started) * 1000,
                    "versions": result.get("versions", {}),
                    "timings": result.get("timings", {}),
                    "output_tokens": result.get("output_tokens"),
                }
            )
        )
        return JSONResponse(result, status_code)

    @app.post("/api/v1/query")
    def query(request: QueryRequest):
        return execute(request, "query")

    @app.post("/api/v1/retrieve")
    def retrieve(request: RetrieveRequest):
        return execute(request, "retrieve")

    @app.get("/api/v1/models/current")
    def current():
        return app.state.pipeline.versions

    @app.get("/health/live")
    def live():
        return {"status": "live"}

    @app.get("/health/ready")
    def ready():
        try:
            if app.state.pipeline.ready():
                return {"status": "ready"}
        except Exception:
            pass
        return JSONResponse({"status": "not_ready"}, 503)

    return app


app = create_app()
