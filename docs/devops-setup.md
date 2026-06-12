# DevOps Tool Installation & Setup (D: drive only)

All tools and caches stay on **D:** so C: is not filled (you have ~6 GB free there).

## 1. GitHub

| Item | Setup |
|------|--------|
| Repository | Push this project to GitHub |
| Jenkins access | Add repo URL in Jenkins job (Pipeline from SCM) |
| Branch | `main` or your working branch |

No install path — code lives in `D:\Engineering\6th sem\DevOps\solar-panel-devops`.

## 2. Jenkins (already configured — do not change)

| Item | Value |
|------|--------|
| Location | `D:\Jenkins` |
| Port | **8088** |
| Start | `java -jar jenkins.war --httpPort=8088` |

**Pipeline:** `Jenkinsfile` in repo root (8 stages: checkout → test → MLflow → report).

**Before build:** Start MLflow (Terminal 2 below).

## 3. MLflow (already configured — do not change)

| Item | Value |
|------|--------|
| DB | `D:\mlflow\mlflow.db` |
| Artifacts | `D:\mlflow\artifacts` |
| Port | **5000** |

```powershell
mlflow server --backend-store-uri sqlite:///D:/mlflow/mlflow.db --default-artifact-root file:///D:/mlflow/artifacts --host 127.0.0.1 --port 5000
```

## 4. Python / Flask web app

| Item | Value |
|------|--------|
| Project | `D:\Engineering\6th sem\DevOps\solar-panel-devops` |
| Venv | `.venv` (on D: with project) |
| Port | **8000** |
| Pip cache | `D:\pip-cache` |
| Temp | `D:\temp` |

**First time only:**

```powershell
cd "D:\Engineering\6th sem\DevOps\solar-panel-devops"
.\scripts\setup_venv.ps1
```

**Your usual start (unchanged):**

```powershell
cd "D:\Engineering\6th sem\DevOps\solar-panel-devops"
python web_app.py
```

Faster option (same app, explicit env vars):

```powershell
.\scripts\start_web_app.ps1
```

## 5. Docker

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and set **disk image location** to D: in Settings → Resources → Advanced.

```powershell
cd "D:\Engineering\6th sem\DevOps\solar-panel-devops"
docker build -t solar-panel-devops .
docker run -p 8000:8000 -v "${PWD}/models:/app/models" solar-panel-devops
```

Or app + MLflow together:

```powershell
docker compose up -d
```

## 6. AWS (planning + deploy)

| Service | Role |
|---------|------|
| EC2 | Run containers in production |
| ECR | Store Docker images from Jenkins builds |
| S3 | MLflow artifacts backup |
| IAM + Security Group | Access without hard-coded keys |

Full guide: **`docs/aws-deployment.md`**

## 7. Ansible

| File | Purpose |
|------|---------|
| `ansible/deploy.yml` | Pull ECR image, run `docker compose` on EC2 |
| `ansible/inventory.ini` | EC2 IP + ECR URI (edit before deploy) |
| `ansible/ansible.cfg` | Defaults |

```bash
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
```

## Three terminals (your workflow)

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

## URLs

| Service | URL |
|---------|-----|
| Web app | http://127.0.0.1:8000 |
| Health | http://127.0.0.1:8000/health |
| MLflow | http://127.0.0.1:5000 |
| Jenkins | http://127.0.0.1:8088 |
