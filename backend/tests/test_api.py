import json
import os
import sys
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_seed():
    from scripts.seed_data import seed_database, seeded_threats, seeded_transactions, seeded_alerts, seeded_policies

    global _seeded_flag
    if not getattr(setup_seed, "_seeded", False):
        seed_database()
        setup_seed._seeded = True


class TestHealth:
    def test_health_endpoint(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "ml_models" in data
        assert "version" in data

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "ShieldNet API"
        assert "endpoints" in data

    def test_root_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ShieldNet"


class TestAuthentication:
    def test_login_success(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "admin"

    def test_login_invalid_credentials(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong_password"},
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent_user", "password": "SomePass123!"},
        )
        assert response.status_code == 401

    def test_register_success(self):
        ts = datetime.utcnow().timestamp()
        username = f"testuser_{int(ts)}"
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": "TestPassword123!",
                "full_name": "Test User",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == username

    def test_register_duplicate(self):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "admin",
                "email": "admin2@test.com",
                "password": "AnotherPass123!",
            },
        )
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    def test_register_short_password(self):
        ts = datetime.utcnow().timestamp()
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": f"user_{int(ts)}",
                "email": f"user_{int(ts)}@test.com",
                "password": "short",
                "full_name": "Short Password User",
            },
        )
        assert response.status_code == 422


class TestThreats:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_get_threats(self):
        response = client.get("/api/v1/threats", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0

    def test_get_threats_with_pagination(self):
        response = client.get(
            "/api/v1/threats?page=1&page_size=2",
            headers=self.auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_get_threats_filter_by_severity(self):
        response = client.get(
            "/api/v1/threats?severity=critical",
            headers=self.auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["severity"] == "critical"

    def test_get_threats_filter_by_type(self):
        response = client.get(
            "/api/v1/threats?threat_type=phishing",
            headers=self.auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["threat_type"] == "phishing"

    def test_get_specific_threat(self):
        response = client.get("/api/v1/threats", headers=self.auth_headers)
        assert response.status_code == 200
        all_threats = response.json()["items"]
        if all_threats:
            threat_id = all_threats[0]["id"]
            response = client.get(
                f"/api/v1/threats/{threat_id}",
                headers=self.auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == threat_id

    def test_get_nonexistent_threat(self):
        response = client.get(
            "/api/v1/threats/nonexistent-id-12345",
            headers=self.auth_headers,
        )
        assert response.status_code == 404

    def test_analyze_threat(self):
        response = client.post(
            "/api/v1/threats/analyze",
            headers=self.auth_headers,
            json={
                "title": "Test SQL Injection",
                "description": "SQL injection attempt on login endpoint",
                "severity": "high",
                "threat_type": "sql_injection",
                "source_ip": "192.168.1.100",
                "target": "api.example.com/login",
                "indicators": ["192.168.1.100", "test.exe"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "threat_id" in data
        assert "analysis_results" in data
        assert "recommended_actions" in data
        assert "confidence_score" in data

    def test_threat_unauthorized(self):
        response = client.get("/api/v1/threats")
        assert response.status_code == 401


class TestDashboard:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_dashboard_stats(self):
        response = client.get("/api/v1/dashboard/stats", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_threats" in data
        assert "active_threats" in data
        assert "network_uptime" in data
        assert "threat_trend" in data
        assert "transaction_volume" in data

    def test_dashboard_stats_values(self):
        response = client.get("/api/v1/dashboard/stats", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_threats"] > 0
        assert data["network_uptime"] > 0
        assert len(data["threat_trend"]) > 0


class TestBlockchain:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_smart_contract_audit(self):
        response = client.post(
            "/api/v1/smart-contract/audit?address=0x1234567890abcdef1234567890abcdef12345678&chain=ethereum",
            headers=self.auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "contract_address" in data
        assert "vulnerabilities" in data
        assert "overall_risk" in data
        assert "risk_score" in data

    def test_smart_contract_audit_minimal_params(self):
        response = client.post(
            "/api/v1/smart-contract/audit?address=0xabcd",
            headers=self.auth_headers,
        )
        assert response.status_code == 200

    def test_get_transactions(self):
        response = client.get("/api/v1/transactions", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

    def test_get_transactions_filter_chain(self):
        response = client.get(
            "/api/v1/transactions?chain=ethereum",
            headers=self.auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        for tx in data["items"]:
            assert tx["chain"] == "ethereum"


class TestRiskAndFraud:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_risk_score(self):
        response = client.post(
            "/api/v1/risk/score",
            headers=self.auth_headers,
            json={
                "tx_volume": 50000,
                "tx_frequency": 15,
                "avg_tx_value": 5000,
                "account_age_days": 120,
                "failed_tx_ratio": 0.1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert 0 <= data["overall_score"] <= 1
        assert "factors" in data

    def test_fraud_detection(self):
        response = client.post(
            "/api/v1/fraud/detect",
            headers=self.auth_headers,
            json={
                "id": "TX-test-123",
                "amount": 25000,
                "hour_of_day": 3,
                "is_international": 1,
                "is_new_recipient": 1,
                "tx_count_last_hour": 10,
                "device_risk_score": 0.8,
                "ip_risk_score": 0.7,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_fraudulent" in data
        assert "fraud_score" in data
        assert 0 <= data["fraud_score"] <= 1

    def test_compliance_check(self):
        response = client.post(
            "/api/v1/compliance/check?frameworks=gdpr&frameworks=soc2",
            headers=self.auth_headers,
            json={"entity_id": "test-org-123", "entity_type": "organization"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "score" in data
        assert "violations" in data


class TestAlerts:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_get_alerts(self):
        response = client.get("/api/v1/alerts", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

    def test_acknowledge_alert(self):
        response = client.get("/api/v1/alerts", headers=self.auth_headers)
        alerts = response.json()["items"]
        if alerts:
            alert_id = alerts[0]["id"]
            response = client.post(
                f"/api/v1/alerts/{alert_id}/acknowledge",
                headers=self.auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "acknowledged"
            assert data["acknowledged_by"] == "admin"

    def test_acknowledge_nonexistent_alert(self):
        response = client.post(
            "/api/v1/alerts/nonexistent-alert-id/acknowledge",
            headers=self.auth_headers,
        )
        assert response.status_code == 404


class TestNetwork:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_network_status(self):
        response = client.get("/api/v1/network/status", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "active_nodes" in data
        assert "gas_price_gwei" in data

    def test_portfolio_risk(self):
        response = client.get("/api/v1/portfolio/risk", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "recommendations" in data


class TestIdentityAndInsurance:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_verify_identity(self):
        response = client.get(
            "/api/v1/identity/verify?user_id=test-user-123",
            headers=self.auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "verified" in data
        assert "verification_level" in data

    def test_submit_insurance_claim(self):
        response = client.post(
            "/api/v1/insurance/claim",
            headers=self.auth_headers,
            json={
                "policy_id": "POL-123456",
                "amount": 5000,
                "description": "Loss due to smart contract exploit",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "under_review"


class TestAnalytics:
    auth_headers = {}

    @pytest.fixture(autouse=True)
    def auth(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@1234"},
        )
        token = response.json()["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {token}"}

    def test_predictions(self):
        response = client.get("/api/v1/analytics/predictions", headers=self.auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for pred in data:
            assert "prediction" in pred
            assert "confidence" in pred
            assert "model_name" in pred


class TestWebSocket:
    def test_websocket_connection(self):
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connection_established"

    def test_websocket_ping_pong(self):
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()
            websocket.send_json({"type": "ping"})
            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_websocket_subscribe(self):
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()
            websocket.send_json({
                "type": "subscribe",
                "channels": ["threats", "transactions"],
            })
            response = websocket.receive_json()
            assert response["type"] == "subscribed"
            assert "threats" in response["data"]["channels"]

    def test_websocket_invalid_json(self):
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()
            websocket.send_text("not valid json")
            response = websocket.receive_json()
            assert response["type"] == "error"

    def test_websocket_get_status(self):
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()
            websocket.send_json({"type": "get_status"})
            response = websocket.receive_json()
            assert response["type"] == "status_update"
            assert "gas_prices" in response["data"]


class TestAuthorization:
    def test_endpoints_require_auth(self):
        protected_endpoints = [
            ("GET", "/api/v1/threats"),
            ("GET", "/api/v1/dashboard/stats"),
            ("GET", "/api/v1/network/status"),
            ("GET", "/api/v1/transactions"),
            ("GET", "/api/v1/alerts"),
            ("GET", "/api/v1/analytics/predictions"),
        ]
        for method, path in protected_endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                continue
            assert response.status_code == 401, f"{method} {path} should require auth"

    def test_auth_with_api_key(self):
        response = client.get(
            "/api/v1/threats",
            headers={"X-API-Key": "sn_valid_test_api_key_12345"},
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main(["-v", __file__])
