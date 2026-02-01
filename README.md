# Inventix AI - Intelligent Research & Patent Analysis Platform

> **AI-powered platform for academic research validation and patent novelty analysis**

[![Phase](https://img.shields.io/badge/Phase-10%20Complete-brightgreen)](https://github.com)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](https://github.com)

---

## 📋 Problem Statement

**The Challenge:**
Researchers and innovators face significant barriers when validating the novelty of their ideas:


## INVENTEX -AI 
1. **Information Overload**: Millions of research papers and patents exist, making manual review impossible
2. **Expertise Gap**: Understanding patent claims requires legal expertise most researchers lack
3. **Costly Mistakes**: Filing patents without proper prior art search leads to rejections and wasted resources
4. **Time Constraints**: Traditional novelty searches take weeks; innovation moves in days

**Our Solution:**
Inventix AI provides an **evidence-based, AI-assisted platform** that:
- Automatically retrieves relevant prior art from Semantic Scholar and USPTO
- Computes semantic similarity using deterministic algorithms
- Classifies novelty risk (GREEN/YELLOW/RED) with transparent thresholds
- Generates conceptual patent claim structures for attorney review
- Never claims legal validity — all outputs are clearly marked as assistive

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INVENTIX AI PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         ┌──────────────┐ │
│  │   React Frontend │ ◄─────► │   FastAPI Backend │ ◄─────► │   SQLite DB  │ │
│  │   (Port 5173)    │  REST   │   (Port 8000)     │         │  (Local)     │ │
│  └──────────────────┘         └────────┬─────────┘         └──────────────┘ │
│                                        │                                     │
│                    ┌───────────────────┼───────────────────┐                │
│                    ▼                   ▼                   ▼                │
│           ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│           │   Semantic   │    │    USPTO     │    │   LLM API    │         │
│           │   Scholar    │    │    Patents   │    │  (Hugging    │         │
│           │     API      │    │     API      │    │    Face)     │         │
│           └──────────────┘    └──────────────┘    └──────────────┘         │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           CORE PROCESSING PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │
│  │ Upload  │──►│ Extract │──►│Retrieve │──►│Similarity│──►│ Classify │      │
│  │Document │   │  Text   │   │Evidence │   │ Compute  │   │ Novelty  │      │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘       │
│                                                                   │          │
│                    ┌──────────────────────────────────────────────┘          │
│                    ▼                                                         │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐                      │
│  │  Draft  │──►│  Venue  │──►│ Patent  │──►│  Human  │                      │
│  │Optimize │   │Recommend│   │ Claims  │   │Feedback │                      │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI Framework |
| **Vite** | Build Tool & Dev Server |
| **Framer Motion** | Animations |
| **Axios** | HTTP Client |
| **TailwindCSS** | Utility-first Styling |

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Runtime |
| **FastAPI** | REST API Framework |
| **SQLAlchemy** | ORM |
| **SQLite** | Database |
| **Pydantic** | Data Validation |
| **PyPDF2 / python-docx** | Document Parsing |

### AI & ML
| Technology | Purpose |
|------------|---------|
| **Hugging Face Inference API** | LLM Access (Qwen3-32B) |
| **Sentence Transformers** | Text Embeddings |
| **Scikit-learn** | Cosine Similarity |

### External APIs
| Service | Purpose |
|---------|---------|
| **Semantic Scholar API** | Research Paper Retrieval |
| **USPTO API** | Patent Search |

---

## 🚀 Setup Instructions

### Option 1: Docker (Recommended - Easy Setup)
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Run `deploy.bat` (Windows) or see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for other platforms
3. Access the app at http://localhost:3000

### Option 2: Manual Setup

#### Prerequisites
- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **Git** (for version control)

### 1. Clone the Repository
```bash
git clone https://github.com/QuirkyIdea/vibecraft-2.0.git
cd vibecraft-2.0
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your HUGGINGFACE_API_KEY
```

### 3. Frontend Setup
```bash
# Navigate to project root
cd ..

# Install dependencies
npm install
```

### 4. Environment Variables

**Backend (.env):**
```env
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
LLM_MODEL=Qwen/Qwen3-32B
ENVIRONMENT=development
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate  # Windows
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### 6. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🤖 AI Tools Used

| Tool | How We Used It |
|------|----------------|
| **Hugging Face Inference API** | Primary LLM for text analysis, claim generation, and comparative analysis using Qwen3-32B model |
| **Sentence Transformers** | Generate embeddings for semantic similarity computation between user ideas and prior art |
| **Gemini Code Assist** | Development assistant for code generation, debugging, and architecture planning |

### LLM Configuration
```python
# Model: Qwen/Qwen3-32B via Hugging Face
# Temperature: 0.3 (low for consistency)
# Max Tokens: 4096
# Reasoning Mode: /no_think for structured outputs
```

---

## 🧠 Prompt Strategy Summary

### Core Principles

1. **Evidence Grounding**
   - All LLM outputs must reference specific evidence from retrieved documents
   - No hallucinated statistics or claims

2. **Structured Output**
   - JSON-formatted responses for programmatic parsing
   - Explicit field requirements in prompts

3. **Uncertainty Acknowledgment**
   - Prompts explicitly require confidence levels
   - "UNKNOWN" is a valid response when data is insufficient

4. **Legal Boundaries**
   - Never claim patentability or legal validity
   - Include disclaimers in all legal-adjacent outputs

### Prompt Templates

#### Comparative Analysis Prompt
```
You are a research analysis assistant. Analyze the overlap between:
USER IDEA: {idea_text}
EVIDENCE: {evidence_summaries}

Return JSON with:
- existing_landscape: Summary of existing work
- key_overlaps: [{concept, evidence_titles}]
- potential_differentiators: [{aspect, description, uncertainty}]
- novelty_risk: GREEN | YELLOW | RED
- confidence_level: low | medium | high
```

#### Patent Claim Generation Prompt
```
You are a patent drafting assistant. Generate CONCEPTUAL claim structures.
⚠️ These are NOT legal claims. They require attorney review.

IDEA: {idea_text}
PRIOR ART CONTEXT: {overlap_context}

Return structured claims with:
- Independent claims (broader)
- Dependent claims (specific)
- Risk annotations per claim
```

### Safety Guardrails
- **Max tokens capped** to prevent runaway generation
- **Temperature = 0.3** for reproducible outputs
- **Prompt versioning** tracked in audit logs
- **Compliance Mode** can disable risky features

---

## 🔧 Draft Refinement Enhancements
- **Context-aware analysis** that preserves author intent
- **Targeted, reversible suggestions** with confidence levels
- **Patent-focused clarity and structure improvements**

---

## 📁 Source Code Structure

```
vibecraft-2.0/
├── backend/                    # Python FastAPI Backend
│   ├── main.py                 # API endpoints & app setup
│   ├── models.py               # SQLAlchemy database models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── crud.py                 # Database CRUD operations
│   ├── database.py             # DB connection & session
│   ├── config.py               # Environment configuration
│   │
│   ├── ai_service.py           # LLM integration (Hugging Face)
│   ├── retrieval_service.py    # Semantic Scholar & USPTO APIs
│   ├── similarity_service.py   # Embedding & similarity computation
│   ├── claim_service.py        # Patent claim generation
│   ├── draft_service.py        # Draft optimization
│   ├── recommendation_service.py # Venue recommendations
│   ├── feedback_service.py     # Human feedback loop
│   ├── audit_service.py        # Immutable audit logging
│   └── compliance_service.py   # Feature restriction rules
│
├── src/                        # React Frontend
│   ├── api/
│   │   ├── client.js           # Axios HTTP client
│   │   └── endpoints.js        # API endpoint definitions
│   │
│   ├── components/
│   │   ├── dashboard/          # Dashboard views
│   │   ├── workflow/           # Project creation flow
│   │   ├── CommandCenter.jsx   # Main control panel
│   │   ├── PatentStudio.jsx    # Patent analysis UI
│   │   └── ResearchStudio.jsx  # Research analysis UI
│   │
│   ├── context/
│   │   └── WorkflowContext.jsx # Global state management
│   │
│   └── App.jsx                 # Root component
│
├── package.json                # Frontend dependencies
└── README.md                   # This file
```

---

## 📊 Feature Phases

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Backend Foundation & Persistence | ✅ Complete |
| 2 | Controlled SLM Integration | ✅ Complete |
| 3 | Evidence Retrieval (Semantic Scholar + USPTO) | ✅ Complete |
| 4 | Similarity Engine & Novelty Classification | ✅ Complete |
| 5 | Comparative Analysis & Summarization | ✅ Complete |
| 6 | Draft Optimization (Localized Suggestions) | ✅ Complete |
| 7 | Venue Recommendations | ✅ Complete |
| 8 | Patent Claim Structuring | ✅ Complete |
| 9 | Human Feedback & Confidence Calibration | ✅ Complete |
| 10 | Audit Logs, Compliance Mode & Production Hardening | ✅ Complete |

---

## ⚠️ Disclaimers

> **NOT LEGAL ADVICE**: This platform provides AI-assisted analysis for educational and research purposes only. All outputs regarding patents, claims, or legal matters are conceptual drafts that require review by a registered patent attorney.

> **NO PATENTABILITY CLAIMS**: The platform never claims that an idea is patentable or novel in a legal sense. All risk classifications are based on semantic similarity and should be validated by human experts.

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

---

*Built with ❤️ for researchers and innovators*
