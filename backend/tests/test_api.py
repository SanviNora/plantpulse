def _token(client) -> str:
    response = client.post(
        "/api/auth/token",
        data={"username": "planner@plantpulse.example.com", "password": "planner-password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_queue_requires_auth(client):
    assert client.get("/api/exceptions").status_code == 401


def test_planner_reads_ranked_queue(client):
    token = _token(client)
    response = client.get("/api/exceptions", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["week"] == 12
    assert body["n"] >= 3
    dollars = [row["dollar_impact"] for row in body["exceptions"]]
    assert dollars == sorted(dollars, reverse=True)
    assert body["total_impact"] == round(sum(dollars), 2)


def test_ack_marks_an_exception(client):
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    queue = client.get("/api/exceptions", headers=headers).json()
    code = queue["exceptions"][0]["code"]
    acked = client.post("/api/exceptions/ack", headers=headers, json={"code": code})
    assert acked.status_code == 200
    assert acked.json()["acknowledged"] is True
    again = client.get("/api/exceptions", headers=headers).json()
    row = next(r for r in again["exceptions"] if r["code"] == code)
    assert row["acknowledged"] is True
