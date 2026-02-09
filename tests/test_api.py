from fastapi.testclient import TestClient

def test_shorten_url(client: TestClient):
    response = client.post("/shorten", json={"url": "https://google.com/"})
    assert response.status_code == 201
    data = response.json()
    assert "short_url" in data
    assert data["original_url"] == "https://google.com/"
    assert len(data["short_code"]) == 6

def test_shorten_url_custom_code(client: TestClient):
    response = client.post("/shorten", json={"url": "https://google.com/", "custom_code": "google"})
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "google"

def test_shorten_url_duplicate_custom_code(client: TestClient):
    client.post("/shorten", json={"url": "https://google.com/", "custom_code": "google"})
    response = client.post("/shorten", json={"url": "https://yahoo.com/", "custom_code": "google"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_redirect_to_url(client: TestClient):
    shorten_resp = client.post("/shorten", json={"url": "https://google.com/", "custom_code": "googl"})
    assert shorten_resp.status_code == 201
    code = shorten_resp.json()["short_code"]
    
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://google.com/"

def test_redirect_not_found(client: TestClient):
    response = client.get("/nonexistent")
    assert response.status_code == 404

def test_update_link(client: TestClient):
    shorten_resp = client.post("/shorten", json={"url": "https://google.com/", "custom_code": "googl"})
    assert shorten_resp.status_code == 201
    response = client.patch("/googl", json={"url": "https://bing.com/"})
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://bing.com/"

def test_delete_link(client: TestClient):
    shorten_resp = client.post("/shorten", json={"url": "https://google.com/", "custom_code": "googl"})
    assert shorten_resp.status_code == 201
    response = client.delete("/googl")
    assert response.status_code == 204
    
    get_resp = client.get("/googl")
    assert get_resp.status_code == 404
