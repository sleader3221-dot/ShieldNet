# ShieldNet - AI-Powered Decentralized Cybersecurity & Fintech Intelligence Platform

[![Vortexa Hackathon](https://img.shields.io/badge/Vortexa-Hackathon-blueviolet)](https://hackhere.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-yellow)](https://www.python.org/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.24-lightgrey)](https://soliditylang.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🌟 Overview

ShieldNet is the world's most advanced **AI-Powered Decentralized Cybersecurity & Fintech Intelligence Platform**. Built for the **Vortexa Hackathon** by Hackhere, it combines cutting-edge Artificial Intelligence, Blockchain Technology, Cybersecurity protocols, and Fintech innovation into a unified, production-ready platform.

### 🏆 Why ShieldNet Wins

| Criteria | How ShieldNet Excels |
|----------|---------------------|
| **Innovation & Creativity** | Novel integration of 5 AI/ML models + 5 smart contracts + real-time threat intelligence |
| **Technical Implementation** | Full-stack Next.js + FastAPI + Solidity with WebSocket real-time updates |
| **Impact & Practicality** | Solves real cybersecurity threats, financial fraud, and compliance automation |
| **Design & UX** | Stunning dark-themed cyber UI with glass morphism, 3D visualizations, animations |
| **Scalability** | Microservices architecture, cloud-ready, blockchain-based, horizontally scalable |
| **Presentation** | Complete demo with real-time data, interactive dashboards, live simulations |

---

## 🚀 30+ Ultra-Advanced Features

### 🤖 AI & Machine Learning
1. **AI-Powered Threat Detection** - Real-time anomaly detection using Isolation Forest & Random Forest
2. **Predictive Risk Scoring** - Multi-factor risk assessment with Gradient Boosting
3. **Fraud Detection Engine** - XGBoost + Logistic Regression ensemble with SHAP explanations
4. **NLP Threat Intelligence** - Entity extraction, sentiment analysis, topic modeling
5. **AI Chatbot Assistant** - Intelligent security assistant with natural language understanding
6. **Automated Vulnerability Prediction** - ML-based vulnerability scoring
7. **Behavioral Analytics** - User behavior pattern analysis
8. **Threat Correlation Engine** - Cross-reference multiple threat sources

### 🔗 Blockchain & Web3
9. **ShieldNet Token (SHLD)** - ERC20 with mint/burn, transfer fees, merkle airdrop
10. **Decentralized Insurance** - Smart contract cyber insurance with multi-sig claims
11. **Threat Intelligence DAO** - Decentralized threat reporting with staking/slashing
12. **Decentralized Identity (DID)** - Self-sovereign identity with social recovery
13. **Governance DAO** - Token-weighted voting with timelock execution
14. **Smart Contract Auditor** - Automated vulnerability scanning (8 vulnerability types)
15. **Multi-Signature Wallet** - Enhanced wallet security
16. **Cross-Chain Bridge Monitor** - Multi-chain transaction tracking

### 🛡️ Cybersecurity
17. **Real-time Threat Map** - Live global threat visualization
18. **Smart Contract Vulnerability Scanner** - Detect reentrancy, overflow, access control issues
19. **Phishing Detection** - ML-powered phishing URL/content analysis
20. **Network Traffic Analysis** - Real-time traffic pattern monitoring
21. **Penetration Testing Automation** - Automated security testing
22. **Incident Response System** - Automated alert triage and response
23. **Malware Analysis** - Behavioral malware detection
24. **Compliance Engine** - GDPR, SOC2, PCI-DSS compliance automation

### 💰 Fintech
25. **Portfolio Risk Analytics** - Real-time portfolio risk assessment
26. **KYC/AML Verification** - Automated identity verification
27. **Transaction Monitoring** - Real-time fraud detection on transactions
28. **Insurance Policy Management** - Decentralized cyber insurance
29. **Token Economics Simulator** - Tokenomics modeling and simulation
30. **Financial Health Scoring** - Comprehensive financial risk scoring

### 📊 Visualization & UX
31. **3D Network Visualization** - Interactive Three.js threat network graph
32. **Real-time Charts** - Live updating charts with Recharts
33. **Interactive Threat Map** - Canvas-based global threat heatmap
34. **AI Prediction Dashboard** - Model confidence and feature importance visualization
35. **Glass Morphism UI** - Stunning dark glass design system

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                    │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Landing │ │Dashboard │ │  Threat  │ │  Blockchain   │  │
│  │  Page   │ │  Page    │ │  Intel   │ │    Page       │  │
│  └─────────┘ └──────────┘ └──────────┘ └───────────────┘  │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Fintech │ │Analytics │ │Components│ │  Hooks/Utils  │  │
│  │  Page   │ │  Page    │ │  (12)    │ │    (5)        │  │
│  └─────────┘ └──────────┘ └──────────┘ └───────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API + WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend (FastAPI/Python)                   │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐  │
│  │  API Routes  │ │  Auth/JWT    │ │  WebSocket Feed   │  │
│  │   (18 APIs)  │ │  Security    │ │   (Real-time)     │  │
│  └──────────────┘ └──────────────┘ └───────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐  │
│  │   Services   │ │   ML Models  │ │   Database/SQL    │  │
│  │   (4 svcs)   │ │   (4 models) │ │   (SQLite/PG)     │  │
│  └──────────────┘ └──────────────┘ └───────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Web3 + Events
┌──────────────────────▼──────────────────────────────────────┐
│                  Blockchain (Solidity/Hardhat)               │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐  │
│  │SHLD Token    │ │  Insurance   │ │  Threat Intel     │  │
│  │   (ERC20)    │ │   Contract   │ │   Contract        │  │
│  └──────────────┘ └──────────────┘ └───────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐                        │
│  │  DID         │ │  Governance  │                        │
│  │  Contract    │ │   DAO        │                        │
│  └──────────────┘ └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript 5.4
- **Styling**: Tailwind CSS 3.4
- **Animations**: Framer Motion 11
- **Charts**: Recharts 2.12
- **3D**: Three.js / React Three Fiber
- **Icons**: Lucide React
- **State**: Zustand 4
- **Web3**: Ethers.js 6
- **Real-time**: Socket.IO Client

### Backend
- **Framework**: FastAPI 0.111
- **Language**: Python 3.11
- **ML**: scikit-learn, TensorFlow, XGBoost
- **NLP**: Transformers, NLTK, spaCy
- **Auth**: JWT, OAuth2, bcrypt
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Real-time**: WebSockets

### Blockchain
- **Language**: Solidity 0.8.24
- **Framework**: Hardhat 2.22
- **Standards**: ERC20, ERC165, ERC173
- **Libraries**: OpenZeppelin 5.0
- **Testing**: Hardhat Toolbox, Chai, Ethers

---

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ 
- Python 3.11+
- npm or yarn
- MetaMask (for blockchain features)

### 1️⃣ Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

### 2️⃣ Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 3️⃣ Blockchain Setup
```bash
cd blockchain/hardhat
npm install
npx hardhat compile
npx hardhat test
npx hardhat run ../scripts/deploy.js --network localhost
```

### 4️⃣ Environment Variables
Create `.env` in backend/:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./shieldnet.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🎯 Demo Walkthrough

### Landing Page
- Hero section with animated gradient text
- 30+ feature cards with icons
- Live threat counter animation
- Real-time stats showcase

### Dashboard
- **Stats Overview**: 4 metric cards (threats blocked, active threats, risk score, system health)
- **Threat Map**: Canvas-based global threat visualization with severity indicators
- **Activity Charts**: Real-time line/area charts
- **Alert Feed**: Live security alerts with severity filtering
- **Quick Actions**: Threat scan, contract audit, compliance check

### Threat Intelligence
- **Threat Search**: Search and filter threats
- **Threat Table**: Sortable with severity badges
- **AI Analysis**: ML-powered threat prediction
- **MITRE ATT&CK**: Framework mapping
- **IOC Feed**: Indicators of compromise

### Blockchain
- **Wallet Connect**: MetaMask/WalletConnect/Coinbase integration
- **Network Status**: Multi-chain health monitoring
- **Transaction Monitor**: Real-time transaction tracking
- **Smart Contract Auditor**: Paste code to analyze vulnerabilities
- **DeFi Dashboard**: Protocol health metrics

### Fintech
- **Portfolio Overview**: Risk analysis dashboard
- **Insurance Panel**: Policy management
- **KYC/AML Status**: Verification tracking
- **Compliance Dashboard**: Regulatory status
- **Fraud Alerts**: Real-time fraud detection

### Analytics
- **AI Predictions**: Model confidence visualization
- **Trend Analysis**: Historical threat patterns
- **3D Visualization**: Interactive network graph
- **Custom Reports**: Exportable analytics

---

## 📊 Judging Criteria Coverage

| Criteria | Implementation |
|----------|---------------|
| **Innovation & Creativity** | 30+ integrated features across AI, blockchain, cybersecurity, fintech |
| **Technical Implementation** | Full-stack with ML models, smart contracts, real-time WebSocket, 3D viz |
| **Impact & Practicality** | Real-world threat detection, fraud prevention, compliance automation |
| **Design & UX** | Glass morphism, dark theme, animations, responsive, accessible |
| **Presentation & Pitch** | Complete demo with interactive walkthrough, API docs, test suites |
| **Scalability** | Microservices, cloud-native, blockchain-based, horizontally scalable |

---

## 👥 Team Details

### Project: ShieldNet
- **Category**: Blockchain | Cybersecurity | Fintech | AI
- **Hackathon**: Vortexa by Hackhere
- **Duration**: 24 Hours
- **Team Size**: 1-4 Members

### Setup Instructions
1. Clone the repository
2. Follow the installation steps above
3. Start backend: `cd backend && uvicorn main:app --reload`
4. Start frontend: `cd frontend && npm run dev`
5. Open http://localhost:3000

### Links
- **GitHub**: [Repository Link]
- **Demo Video**: [Link to Demo]
- **Presentation**: [Link to PPT]

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Hackhere** for organizing the Vortexa Hackathon
- **OpenZeppelin** for secure smart contract libraries
- **Next.js** and **FastAPI** teams for amazing frameworks
- All open-source contributors whose libraries made this possible

---

<p align="center">Built with ❤️ for the Vortexa Hackathon by Hackhere</p>
