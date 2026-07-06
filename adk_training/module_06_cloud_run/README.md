# Module 6: Cloud Run Deployment - "Launching the Ship"

## 🎯 Learning Objectives

By the end of this module, you will:
- Deploy an ADK agent to Google Cloud Run
- Understand container requirements for ADK agents
- Configure environment variables for cloud deployment
- Test your deployed agent via the web UI

## ⏱️ Duration: 45 minutes

- Theory: 15 minutes
- Hands-on: 25 minutes
- Break: 5 minutes

---

## 📚 Prerequisites

1. **GCP Project** with billing enabled
2. **APIs Enabled:**
   - Cloud Run API
   - Artifact Registry API
   - Vertex AI API
3. **gcloud CLI** installed and configured
4. **ADK CLI** installed (`pip install google-adk>=1.18.0`)

---

## 🏗️ Module Structure

```
module_06_cloud_run/
├── agent.py          # Deployable pirate navigator agent
├── Dockerfile        # Custom container configuration (optional)
├── requirements.txt  # Python dependencies
├── deploy.sh         # Deployment script
├── .env.template     # Environment variable template
└── README.md         # This file
```

---

## 🚀 Quick Start

### Step 1: Configure Environment

```bash
# Copy template and edit with your values
cp .env.template .env

# Edit .env file with your GCP project details
```

### Step 2: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
adk web
```

### Step 3: Deploy to Cloud Run

```bash
# Simple deployment with ADK CLI
adk deploy cloud_run \
    --project=YOUR_PROJECT_ID \
    --region=us-central1 \
    --service_name=pirate-navigator \
    --app_name=pirate_navigator \
    --with_ui \
    --adk_version="1.18.0" \
    .
```

---

## 📖 Key Concepts

### ADK Deployment Requirements

1. **Agent file must be named `agent.py`**
2. **Agent must be named `root_agent`**
3. **Include `requirements.txt`** for dependencies

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `1` to use Vertex AI |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | GCP region (e.g., `us-central1`) |

### ADK Deploy Command Options

| Option | Description |
|--------|-------------|
| `--project` | GCP project ID |
| `--region` | Cloud Run region |
| `--service_name` | Cloud Run service name |
| `--app_name` | Application name |
| `--with_ui` | Include web UI |
| `--adk_version` | ADK version to use |

---

## 🧪 Exercises

### Exercise 1: Basic Deployment
Deploy the pirate navigator agent to Cloud Run and test it.

### Exercise 2: Custom Tool
Add a new tool to the agent, redeploy, and verify it works.

### Exercise 3: Environment Variables
Add a custom environment variable and use it in your agent.

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Permission denied" | Check IAM roles: Cloud Run Admin, Artifact Registry Writer |
| "API not enabled" | Enable Cloud Run and Artifact Registry APIs |
| "Agent not found" | Ensure `root_agent` is defined in `agent.py` |

---

## 🏴‍☠️ Pirate Wisdom

> "A ship in harbor is safe, but that is not what ships are built for!"
> — Deploy your agents to the cloud and let them sail the digital seas!

---

## 📎 Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [ADK Deployment Guide](https://google.github.io/adk-docs/deploy/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

