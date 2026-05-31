import json
import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from api.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
    fake_users_db,
    rate_limit,
    decode_access_token,
)
from models.schemas import (
    Alert, AlertCreate, AuditResult, Claim, ComplianceResult, DashboardStats,
    FraudDetectionResult, NetworkStatus, PaginatedResponse, PredictionResult,
    RiskAssessment, RiskScore, Threat, ThreatAnalysis, ThreatCreate,
    TokenResponse, Transaction, TransactionCreate, User, UserCreate, UserLogin,
    Vulnerability,
)
from services.threat_intel import threat_intel_service
from services.blockchain_service import blockchain_service
from services.fintech_service import fintech_service

from ml.threat_detection import threat_detection_ml
from ml.risk_scoring import risk_scoring_ml
from ml.fraud_detection import fraud_detection_ml
from ml.nlp_threat_intel import nlp_threat_intel
from scripts.seed_data import (
    seed_database, get_seeded_data, seeded_threats, seeded_transactions,
    seeded_alerts, seeded_policies,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

_seeded = False


def ensure_seeded():
    global _seeded
    if not _seeded:
        seed_database()
        _seeded = True


@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "ShieldNet API",
        "ml_models": {
            "threat_detection": "trained" if threat_detection_ml.is_trained else "not_trained",
            "risk_scoring": "trained" if risk_scoring_ml.is_trained else "not_trained",
            "fraud_detection": "trained" if fraud_detection_ml.is_trained else "not_trained",
            "nlp_threat_intel": "trained" if nlp_threat_intel.is_trained else "not_trained",
        },
        "uptime_seconds": 0,
    }


@router.get("/threats", response_model=PaginatedResponse, tags=["Threats"])
@rate_limit(max_calls=100, window_seconds=60)
async def get_threats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    threat_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    ensure_seeded()
    threats = list(seeded_threats)
    if severity:
        threats = [t for t in threats if t["severity"] == severity]
    if threat_type:
        threats = [t for t in threats if t["threat_type"] == threat_type]
    if status:
        threats = [t for t in threats if t["status"] == status]

    total = len(threats)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size

    return PaginatedResponse(
        items=threats[start:end],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/threats/{threat_id}", response_model=Threat, tags=["Threats"])
async def get_threat(
    threat_id: str,
    current_user: dict = Depends(get_current_user),
):
    ensure_seeded()
    for t in seeded_threats:
        if t["id"] == threat_id:
            return Threat(**t)
    raise HTTPException(status_code=404, detail="Threat not found")


@router.post("/threats/analyze", response_model=ThreatAnalysis, tags=["Threats"])
@rate_limit(max_calls=30, window_seconds=60)
async def analyze_threat(
    threat_data: ThreatCreate,
    current_user: dict = Depends(get_current_user),
):
    threat_dict = threat_data.model_dump()
    threat_dict["id"] = f"THR-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
    threat_dict["detected_at"] = datetime.utcnow().isoformat()

    ml_result = threat_detection_ml.predict_threat_score(threat_dict)
    analysis = threat_intel_service.analyze_threat(threat_dict)

    return ThreatAnalysis(
        threat_id=threat_dict["id"],
        analysis_results={
            "ml_analysis": ml_result,
            "threat_intel": analysis,
            "ioc_analysis": {
                "total_iocs": analysis.get("ioc_count", 0),
                "malicious_iocs": random.randint(0, analysis.get("ioc_count", 1)),
                "suspicious_iocs": random.randint(0, 3),
            },
        },
        recommended_actions=analysis.get("recommended_actions", []),
        confidence_score=ml_result.get("confidence", 0.5),
    )


@router.get("/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    ensure_seeded()
    active = sum(1 for t in seeded_threats if t["status"] == "active")
    unread = sum(1 for a in seeded_alerts if a["status"] == "unread")
    flagged = sum(1 for t in seeded_transactions if t.get("risk_score", 0) > 0.5)
    risk_scores = [t["score"] for t in seeded_threats]
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0

    now = datetime.utcnow()
    threat_trend = []
    for i in range(7):
        day = now - timedelta(days=i)
        day_threats = [t for t in seeded_threats
                      if datetime.fromisoformat(t["detected_at"]).date() == day.date()]
        threat_trend.append({
            "date": day.date().isoformat(),
            "count": len(day_threats) + random.randint(-2, 3),
            "critical": sum(1 for t in day_threats if t["severity"] == "critical") + random.randint(0, 1),
            "high": sum(1 for t in day_threats if t["severity"] == "high") + random.randint(0, 2),
        })

    tx_volume = []
    for i in range(7):
        day = now - timedelta(days=i)
        tx_volume.append({
            "date": day.date().isoformat(),
            "count": random.randint(50, 500),
            "volume_usd": round(random.uniform(10000, 5000000), 2),
        })

    return DashboardStats(
        total_threats=len(seeded_threats),
        active_threats=active,
        blocked_attacks=random.randint(100, 1000),
        total_transactions=len(seeded_transactions) + random.randint(50, 200),
        flagged_transactions=flagged,
        total_alerts=len(seeded_alerts),
        unread_alerts=unread,
        avg_risk_score=round(avg_risk, 4),
        network_uptime=99.97,
        active_nodes=random.randint(10, 50),
        smart_contracts_audited=random.randint(50, 200),
        vulnerabilities_found=random.randint(150, 500),
        insurance_policies=len(seeded_policies),
        total_claims=random.randint(5, 30),
        pending_claims=random.randint(1, 10),
        threat_trend=threat_trend,
        transaction_volume=tx_volume,
    )


@router.get("/network/status", response_model=NetworkStatus, tags=["Network"])
async def get_network_status(current_user: dict = Depends(get_current_user)):
    return NetworkStatus(
        status="operational",
        active_nodes=random.randint(15, 45),
        total_nodes=50,
        avg_latency_ms=round(random.uniform(12, 85), 1),
        throughput_tps=round(random.uniform(150, 450), 1),
        connected_peers=random.randint(8, 30),
        block_height=random.randint(18000000, 19000000),
        gas_price_gwei=round(random.uniform(8, 45), 2),
        services={
            "api": "operational",
            "database": "operational",
            "ml_engine": "operational",
            "websocket": "operational",
            "blockchain_indexer": random.choice(["operational", "operational", "operational", "degraded"]),
            "threat_feed": "operational",
        },
    )


@router.post("/smart-contract/audit", response_model=AuditResult, tags=["Blockchain"])
@rate_limit(max_calls=20, window_seconds=60)
async def audit_smart_contract(
    address: str = Query(..., description="Contract address to audit"),
    chain: str = Query("ethereum", description="Blockchain network"),
    current_user: dict = Depends(get_current_user),
):
    result = await blockchain_service.audit_smart_contract(address, chain)
    return AuditResult(
        contract_id=f"CTR-{random.randint(10000, 99999)}",
        contract_address=address,
        chain=chain,
        overall_risk=result["overall_risk"],
        risk_score=result["risk_score"],
        vulnerabilities=[Vulnerability(**v) for v in result["vulnerabilities"]],
        gas_optimizations=result["gas_optimizations"],
        compliance_checks=result["compliance_checks"],
        audited_at=datetime.fromisoformat(result["audited_at"]),
    )


@router.get("/transactions", response_model=PaginatedResponse, tags=["Blockchain"])
async def get_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    chain: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    ensure_seeded()
    txs = list(seeded_transactions)
    if chain:
        txs = [t for t in txs if t["chain"] == chain]

    total = len(txs)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size

    return PaginatedResponse(
        items=txs[start:end],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/risk/score", response_model=RiskScore, tags=["Risk"])
@rate_limit(max_calls=50, window_seconds=60)
async def calculate_risk_score(
    risk_data: dict,
    current_user: dict = Depends(get_current_user),
):
    ml_result = risk_scoring_ml.calculate_risk(risk_data)
    return RiskScore(
        overall_score=ml_result["risk_score"],
        factors=ml_result.get("factors", {}),
        category="financial",
        recommendations=ml_result.get("recommendations", []),
    )


@router.post("/fraud/detect", response_model=FraudDetectionResult, tags=["Fraud"])
@rate_limit(max_calls=50, window_seconds=60)
async def detect_fraud(
    transaction_data: dict,
    current_user: dict = Depends(get_current_user),
):
    ml_result = fraud_detection_ml.predict_fraud(transaction_data)
    service_result = await fintech_service.detect_fraud(transaction_data)

    combined_score = (ml_result["fraud_score"] * 0.6 + service_result["fraud_score"] * 0.4)
    is_fraudulent = combined_score > 0.6

    return FraudDetectionResult(
        transaction_id=transaction_data.get("id", "unknown"),
        is_fraudulent=is_fraudulent,
        fraud_score=round(combined_score, 4),
        risk_factors=list(set(
            ml_result.get("risk_factors", []) + service_result.get("risk_factors", [])
        )),
        model_confidence=max(
            ml_result.get("model_confidence", 0.5),
            service_result.get("model_confidence", 0.5),
        ),
        recommendation="block" if is_fraudulent else "review" if combined_score > 0.3 else "approve",
    )


@router.post("/compliance/check", response_model=ComplianceResult, tags=["Compliance"])
@rate_limit(max_calls=30, window_seconds=60)
async def check_compliance(
    entity_data: dict,
    frameworks: List[str] = Query(["gdpr", "soc2"], description="Compliance frameworks"),
    current_user: dict = Depends(get_current_user),
):
    result = await fintech_service.check_compliance(entity_data, frameworks)
    return ComplianceResult(
        entity_id=result["entity_id"],
        checks=result["checks"],
        overall_status=result["overall_status"],
        score=result["score"],
        violations=result["violations"],
        recommendations=result["recommendations"],
    )


@router.get("/analytics/predictions", response_model=List[PredictionResult], tags=["Analytics"])
async def get_predictions(current_user: dict = Depends(get_current_user)):
    now = datetime.utcnow()
    predictions = []

    threat_ml = threat_detection_ml.predict_threat_score({
        "severity": "medium",
        "threat_type": "phishing",
        "source_ip": "185.220.101.45",
        "target": "api.shieldnet.io",
        "indicators": ["malicious.com", "5.5.5.5"],
        "confidence": 0.75,
    })
    predictions.append(PredictionResult(
        prediction=threat_ml,
        confidence=threat_ml.get("confidence", 0.85),
        model_name="ThreatDetectionEnsemble",
        features_used=threat_detection_ml.feature_columns,
        explanation={"feature_importance": threat_detection_ml.get_feature_importance()},
    ))

    risk_pred = risk_scoring_ml.calculate_risk({
        "tx_volume": 50000,
        "tx_frequency": 15,
        "avg_tx_value": 5000,
        "account_age_days": 120,
        "unique_counterparties": 25,
        "failed_tx_ratio": 0.1,
        "high_risk_interactions": 3,
        "portfolio_value": 250000,
        "leverage_ratio": 1.5,
        "cross_border_tx": 1,
    })
    predictions.append(PredictionResult(
        prediction=risk_pred,
        confidence=0.88,
        model_name="RiskScoringGBM",
        features_used=risk_scoring_ml._synthetic_training_data.__code__.co_varnames[:10] if hasattr(risk_scoring_ml, '_synthetic_training_data') else [],
    ))

    fraud_pred = fraud_detection_ml.predict_fraud({
        "amount": 15000,
        "hour_of_day": 3,
        "is_international": 1,
        "is_new_recipient": 1,
        "tx_count_last_hour": 8,
        "avg_tx_amount_24h": 200,
        "distance_from_avg": 75,
        "device_risk_score": 0.6,
        "ip_risk_score": 0.7,
    })
    predictions.append(PredictionResult(
        prediction=fraud_pred,
        confidence=fraud_pred.get("model_confidence", 0.82),
        model_name="FraudDetectionEnsemble",
        features_used=fraud_detection_ml.feature_names,
        explanation={"shap_values": fraud_pred.get("explanation", {})},
    ))

    return predictions


# --- Analysis endpoints matching frontend useAIAnalysis hook ---

@router.get("/analysis/threat/{threat_id}", tags=["Analysis"])
@rate_limit(max_calls=60, window_seconds=60)
async def get_threat_analysis(threat_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    ensure_seeded()
    threat = None
    for t in seeded_threats:
        if t["id"] == threat_id:
            threat = t
            break
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    ml_result = threat_detection_ml.predict_threat_score(threat)
    return {
        "id": threat["id"],
        "type": threat["threat_type"],
        "severity": threat["severity"],
        "confidence": ml_result.get("confidence", 0.85),
        "description": threat["description"],
        "source": threat["source_ip"],
        "timestamp": threat["detected_at"],
        "metadata": {"ml_score": threat["score"], "indicators": threat.get("indicators", [])},
    }


@router.post("/analysis/predict", tags=["Analysis"])
@rate_limit(max_calls=30, window_seconds=60)
async def predict_analysis(params: dict = {}, request: Request = None, current_user: dict = Depends(get_current_user)):
    risk_pred = risk_scoring_ml.calculate_risk({
        "tx_volume": params.get("tx_volume", 50000),
        "tx_frequency": params.get("tx_frequency", 15),
        "avg_tx_value": params.get("avg_tx_value", 5000),
        "account_age_days": params.get("account_age_days", 120),
        "unique_counterparties": params.get("unique_counterparties", 25),
        "failed_tx_ratio": params.get("failed_tx_ratio", 0.1),
        "high_risk_interactions": params.get("high_risk_interactions", 3),
        "portfolio_value": params.get("portfolio_value", 250000),
        "leverage_ratio": params.get("leverage_ratio", 1.5),
        "cross_border_tx": params.get("cross_border_tx", 1),
    })
    return {
        "prediction": risk_pred.get("risk_level", "medium"),
        "probability": 1.0 - risk_pred.get("risk_score", 0.5),
        "factors": [{"name": k, "weight": v} for k, v in risk_pred.get("factors", {}).items()],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/analysis/threats/recent", response_model=List[dict], tags=["Analysis"])
@rate_limit(max_calls=60, window_seconds=60)
async def get_recent_threats(limit: int = Query(20, ge=1, le=100), request: Request = None, current_user: dict = Depends(get_current_user)):
    ensure_seeded()
    threats = sorted(seeded_threats, key=lambda t: t["detected_at"], reverse=True)[:limit]
    result = []
    for t in threats:
        ml_result = threat_detection_ml.predict_threat_score(t)
        result.append({
            "id": t["id"],
            "type": t["threat_type"],
            "severity": t["severity"],
            "confidence": ml_result.get("confidence", 0.85),
            "description": t["description"],
            "source": t["source_ip"],
            "timestamp": t["detected_at"],
            "metadata": {"ml_score": t["score"]},
        })
    return result


@router.get("/alerts", response_model=PaginatedResponse, tags=["Alerts"])
async def get_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    ensure_seeded()
    alerts = list(seeded_alerts)
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    if status:
        alerts = [a for a in alerts if a["status"] == status]

    total = len(alerts)
    start = (page - 1) * page_size
    end = start + page_size

    return PaginatedResponse(
        items=alerts[start:end],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.post("/alerts/{alert_id}/acknowledge", response_model=Alert, tags=["Alerts"])
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
):
    ensure_seeded()
    for alert in seeded_alerts:
        if alert["id"] == alert_id:
            alert["status"] = "acknowledged"
            alert["acknowledged_at"] = datetime.utcnow().isoformat()
            alert["acknowledged_by"] = current_user.get("username")
            return Alert(**alert)
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/identity/verify", tags=["Identity"])
@rate_limit(max_calls=20, window_seconds=60)
async def verify_identity(
    user_id: str = Query(..., description="User ID to verify"),
    current_user: dict = Depends(get_current_user),
):
    result = await fintech_service.kyc_verify({"user_id": user_id})
    return result


@router.post("/insurance/claim", response_model=Claim, tags=["Insurance"])
@rate_limit(max_calls=10, window_seconds=60)
async def submit_insurance_claim(
    claim_data: dict,
    current_user: dict = Depends(get_current_user),
):
    result = await fintech_service.submit_claim(claim_data)
    return Claim(
        id=result["id"],
        policy_id=result["policy_id"],
        amount=result["amount"],
        description=result["description"],
        status=result["status"],
        submitted_at=datetime.fromisoformat(result["submitted_at"]),
    )


@router.get("/portfolio/risk", response_model=RiskScore, tags=["Portfolio"])
async def get_portfolio_risk(
    current_user: dict = Depends(get_current_user),
):
    portfolio_data = {
        "total_value": 250000,
        "allocations": {
            "bitcoin": 0.3,
            "ethereum": 0.25,
            "defi_tokens": 0.15,
            "stablecoins": 0.2,
            "nft": 0.1,
        },
    }
    result = await fintech_service.calculate_portfolio_risk(portfolio_data)
    return RiskScore(
        overall_score=result["overall_risk_score"],
        factors=result["risk_factors"],
        category="portfolio",
        recommendations=result["recommendations"],
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(login_data: UserLogin):
    username = login_data.username
    password = login_data.password

    ensure_seeded()

    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(data={"sub": username, "role": user["role"]})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600,
        user=User(
            id=str(hash(username) % 1000000),
            username=username,
            email=user["email"],
            full_name=user.get("full_name", ""),
            role=user["role"],
            is_active=user.get("is_active", True),
        ),
    )


@router.post("/auth/register", response_model=TokenResponse, tags=["Authentication"])
@rate_limit(max_calls=5, window_seconds=300)
async def register(register_data: UserCreate):
    ensure_seeded()

    if register_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    hashed = hash_password(register_data.password)
    fake_users_db[register_data.username] = {
        "username": register_data.username,
        "email": register_data.email,
        "password": hashed,
        "full_name": register_data.full_name,
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
    }

    token = create_access_token(data={"sub": register_data.username, "role": "user"})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600,
        user=User(
            id=str(hash(register_data.username) % 1000000),
            username=register_data.username,
            email=register_data.email,
            full_name=register_data.full_name,
            role="user",
            is_active=True,
        ),
    )


@router.get("/user/profile", response_model=User, tags=["User"])
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    return User(
        id=str(hash(current_user.get("username", "")) % 1000000),
        username=current_user.get("username", ""),
        email=current_user.get("email", ""),
        full_name=current_user.get("full_name", ""),
        role=current_user.get("role", "user"),
        is_active=current_user.get("is_active", True),
    )
