# Solar Panel Defect Detection — DevOps/MLOps Project

Automated solar panel defect detection using EfficientNet-B0 with a full DevOps toolchain: GitHub, Jenkins, MLflow, Docker, AWS, and Ansible.

## Project checklist (all requirements)

| # | Requirement | Status | Location |
|---|-------------|--------|----------|
| 1 | Architecture & workflow | Done | `docs/architecture.md` |
| 2 | DevOps tool setup (GitHub, Jenkins, Docker, AWS, Ansible) | Done | `docs/devops-setup.md`, `ansible/`, `docs/aws-deployment.md` |
| 3 | Jenkins pipeline | Done | `Jenkinsfile` |
| 4 | Containerization | Done | `Dockerfile`, `docker-compose.yml` |
| 5 | AWS deployment planning | Done | `docs/aws-deployment.md` |

## How to run locally (your existing commands)

**Important:** Keep Jenkins and MLflow exactly as you run them today. All installs use **D: drive** — not C:.

```powershell
# Terminal 1: Jenkins (PORT 8088)
cd D:\Jenkins
java -jar jenkins.war --httpPort=8088

# Terminal 2: MLflow (PORT 5000)
mlflow server --backend-store-uri sqlite:///D:/mlflow/mlflow.db --default-artifact-root file:///D:/mlflow/artifacts --host 127.0.0.1 --port 5000

# Terminal 3: Web App (PORT 8000)
cd "D:\Engineering\6th sem\DevOps\solar-panel-devops"
python web_app.py
```

### First-time Python setup (D: drive only)

```powershell
cd "D:\Engineering\6th sem\DevOps\solar-panel-devops"
.\scripts\setup_venv.ps1
```

This creates `.venv` in the project folder and redirects pip cache to `D:\pip-cache`.

### Faster image analysis on localhost

The app now:
- Opens the UI **immediately** (model loads in background)
- Skips slow per-request MLflow logging by default
- Compresses large photos in the browser before upload
- Keeps PyTorch caches on **D:** not C:

Your command stays the same: `python web_app.py`

Optional helper (same behavior, explicit env vars):

```powershell
.\scripts\start_web_app.ps1
```

After the model finishes loading, check timing in results: **Model: Xms | Total: Yms**.

## URLs

| Service | URL |
|---------|-----|
| Web app | http://127.0.0.1:8000 |
| MLflow UI | http://127.0.0.1:5000 |
| Jenkins | http://127.0.0.1:8088 |
| Health check | http://127.0.0.1:8000/health |

## Architecture

```
User → Flask (8000) → TorchScript model → defect + recommendation
                    → MLflow (5000) [optional background logging]
GitHub → Jenkins (8088) → MLflow register + prediction tests
Docker image → AWS ECR → EC2 ← Ansible deploy.yml
```

Full diagram: `docs/architecture.md`

## Jenkins pipeline

`Jenkinsfile` runs 8 stages: checkout → Python setup → model verify → MLflow experiment → log training → register model → 6 prediction tests → report.

**Prerequisite:** Start MLflow (Terminal 2) before running the Jenkins job.

## Docker

```powershell
docker build -t solar-panel-devops .
docker run -p 8000:8000 -v "${PWD}/models:/app/models" solar-panel-devops
```

Or both app + MLflow:

```powershell
docker compose up -d
```

## AWS & Ansible

- **Strategy:** `docs/aws-deployment.md` (EC2 + ECR + S3)
- **Deploy playbook:** `ansible/deploy.yml`
- **Inventory:** `ansible/inventory.ini` (set your EC2 IP and ECR URI)

## Model details

| Property | Value |
|----------|-------|
| Architecture | EfficientNet-B0 |
| Classes | bird-drop, clean, dusty, electrical-damage, physical-damage, snow |
| Format | TorchScript (`models/solar_panel_android.pt`) |
| Size | ~16.76 MB |
| Accuracy | 96.49% (test set) |

## Avoid using C: drive

| What | Use instead |
|------|-------------|
| Python packages | Project `.venv` on D: |
| Pip cache | `D:\pip-cache` |
| Temp files | `D:\temp` |
| MLflow data | `D:\mlflow\` |
| Jenkins | `D:\Jenkins` |

Set in PowerShell before any `pip install`:

```powershell
$env:PIP_CACHE_DIR = "D:\pip-cache"
$env:TEMP = "D:\temp"
$env:TMP = "D:\temp"
```
