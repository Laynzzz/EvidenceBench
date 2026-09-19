from fastapi.testclient import TestClient


def test_api_contracts_and_dependency_readiness():
    from evidencebench.serving.app import create_app

    class Pipeline:
        versions = {"release": "fixture"}
        healthy = True

        def ready(self):
            return self.healthy

        def retrieve(self, query, filters, k):
            return {"status": "ok", "evidence": [], "versions": self.versions}

        def ask(self, query, filters):
            return {
                "status": "refused",
                "reason": "insufficient_evidence",
                "answer": "",
                "citations": [],
                "versions": self.versions,
            }

    pipeline = Pipeline()
    with TestClient(create_app(pipeline)) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 200
        assert client.get("/api/v1/models/current").json()["release"] == "fixture"
        response = client.post("/api/v1/query", json={"query": "Which optimizer?"})
        assert response.status_code == 200 and response.json()["status"] == "refused"
        assert response.json()["request_id"]
        assert client.post("/api/v1/query", json={"query": " "}).status_code == 422
        assert client.post("/api/v1/retrieve", json={"query": "x", "k": 101}).status_code == 422
        pipeline.healthy = False
        assert client.get("/health/ready").status_code == 503


def test_api_does_not_expose_dependency_exception_details():
    from evidencebench.serving.app import create_app

    class Pipeline:
        versions = {}

        def ask(self, *args):
            raise RuntimeError("private connection details")

    with TestClient(create_app(Pipeline())) as client:
        response = client.post("/api/v1/query", json={"query": "example"})
        assert response.status_code == 503
        assert "private" not in response.text


def test_busy_requests_are_counted_in_logs(monkeypatch):
    import threading
    from concurrent.futures import ThreadPoolExecutor

    from evidencebench.serving.app import create_app, logger

    entered, release = threading.Event(), threading.Event()
    records = []
    monkeypatch.setattr(logger, "info", records.append)

    class Pipeline:
        versions = {}

        def ask(self, *args):
            entered.set()
            release.wait(5)
            return {"status": "refused"}

    with TestClient(create_app(Pipeline())) as client, ThreadPoolExecutor() as pool:
        pending = pool.submit(client.post, "/api/v1/query", json={"query": "first"})
        assert entered.wait(3)
        try:
            assert client.post("/api/v1/query", json={"query": "second"}).status_code == 429
        finally:
            release.set()
        assert pending.result().status_code == 200
    import json

    assert len(records) == 2
    assert sorted(json.loads(row)["http_status"] for row in records) == [200, 429]
