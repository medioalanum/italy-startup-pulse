from fastapi.testclient import TestClient


def test_dashboard_routes(test_database_url: str, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", test_database_url)
    monkeypatch.setenv("SOURCE_MODE", "sample")

    from startup_pulse.ingest import ingest
    from startup_pulse.web.app import app

    ingest()
    with TestClient(app) as client:
        dashboard = client.get("/")
        anomalies = client.get("/anomalies")

    assert dashboard.status_code == 200
    assert "Italy Startup Pulse" in dashboard.text
    assert anomalies.status_code == 200
    assert "Anomalies" in anomalies.text
    assert client.get("/health").json() == {"status": "ok"}
