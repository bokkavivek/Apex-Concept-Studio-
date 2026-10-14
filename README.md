# Apex Concept Studio 🏎️✨

**Apex Concept Studio** is an autonomous AI-powered automotive design, engineering, and prototyping agent built on the Google Agent Development Kit (ADK) and Vertex AI Agent Platform. It assists automotive designers and engineers in exploring, benchmarking, simulating aerodynamics, visualizing, and cataloging next-generation concept vehicles.

---

## 🌟 Key Features & Wired Capabilities

- **Automotive Prototyping & Database**: Queries, retrieves, and catalogs concept and prototype vehicle spec sheets stored in **Google Cloud Firestore**.
- **Real-World Benchmarking**: Integrates with the public **NHTSA vPIC API** to benchmark concept specifications against real-world production vehicle lineups and global manufacturers.
- **Aerodynamics & Physics Sandbox Simulations**: Executes Python-based aerodynamics and performance physics calculations safely in an isolated **Vertex AI Code Sandbox** (`AgentEngineSandboxCodeExecutor`).
- **Concept Visual Generation**: Synthesizes studio-grade concept vehicle renders using **Vertex AI Imagen 3** (`imagen-3.0-generate-002`) and publishes them to a Google Cloud Storage bucket.
- **Cross-Session Long-Term Memory**: Uses **Vertex AI Memory Bank** to automatically persist and recall designer preferences, past vehicle concepts, and constraints across sessions.
- **Full-Stack A2A Chat Interface**: Built-in minimal **FastAPI proxy** and plain HTML/CSS/JS frontend communicating directly over the **A2A Protocol** with **A2UI card rendering**.

---

## 🏗️ Architecture

```
                                  ┌───────────────────────────┐
                                  │   Web Browser (Chat UI)   │
                                  └─────────────┬─────────────┘
                                                │ (HTTP / JSON)
                                                ▼
                                  ┌───────────────────────────┐
                                  │    FastAPI A2A Proxy      │
                                  │      (frontend/)          │
                                  └─────────────┬─────────────┘
                                                │ (A2A Protocol / gRPC-HTTP)
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Vertex AI Agent Platform (Agent Runtime)                        │
│                                                                                        │
│                                    ┌──────────────┐                                    │
│                                    │  root_agent  │                                    │
│                                    └──────┬───────┘                                    │
│                                           │                                            │
│        ┌───────────────────┬──────────────┼──────────────┬───────────────────┐         │
│        ▼                   ▼              ▼              ▼                   ▼         │
│  PreloadMemoryTool   list_vehicles   query_nhtsa    generate_render    Code Sandbox    │
│  (Memory Bank)       (Firestore)     (NHTSA API)    (Imagen 3 + GCS)   (Aerodynamics)  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
Apex-Concept-Studio-/
├── app/
│   ├── agent.py               # Core ADK agent, tools, callbacks, and sandbox wiring
│   ├── fast_api_app.py        # FastAPI agent runner
│   └── app_utils/             # Memory Bank services, A2A routes, and helpers
├── frontend/
│   ├── main.py                # Lightweight FastAPI A2A proxy
│   ├── requirements.txt       # Frontend proxy dependencies
│   └── static/
│       └── index.html         # Plain Chat UI with native A2UI card renderer
├── agents-cli-manifest.yaml   # Agent manifest configuration
├── pyproject.toml             # Python dependencies and build config
└── README.md                  # Project overview and documentation
```

---

## 🛠️ Tools & Integrations

| Tool | Purpose | Integration |
| --- | --- | --- |
| `list_concept_vehicles` | Retrieve vehicle specs from Firestore | Google Cloud Firestore |
| `get_concept_vehicle` | Fetch detailed specs for a specific prototype | Google Cloud Firestore |
| `save_concept_vehicle` | Catalog a new concept vehicle | Google Cloud Firestore |
| `query_nhtsa_models` | Search real-world manufacturer lineups | NHTSA vPIC REST API |
| `generate_concept_render` | Synthesize photorealistic visual renders | Vertex AI Imagen 3 + Cloud Storage |
| `code_execution` | Execute aerodynamic & physics calculations | Vertex AI Sandbox Code Executor |
| `preload_memory` | Retrieve salient facts across sessions | Vertex AI Memory Bank |

---

## 🚀 Running Locally

### 1. Requirements
- Python 3.11+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `gcloud` CLI with active Google Cloud credentials (`gcloud auth application-default login`)

### 2. Backend Agent
```bash
# Install dependencies
uv sync

# Launch ADK Web playground with Memory Bank
uv run adk web . --port 8080 --reload_agents
```

### 3. Frontend Chat UI
```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
python main.py
```
Open **http://localhost:8080** in your browser to chat with your studio agent!
