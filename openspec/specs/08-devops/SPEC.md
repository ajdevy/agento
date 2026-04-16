# Phase 8: DevOps

## Overview

DevOps phase implements CI/CD integration (GitHub Actions, GitLab CI), Docker operations, Kubernetes management, and cloud deployment tools.

## Objectives

1. Implement GitHub Actions integration
2. Implement GitLab CI integration
3. Create Docker operations
4. Implement Kubernetes tools
5. Add cloud deployment adapters

## Deliverables

### 8.1 CI/CD Integration

| Component | File | Description |
|-----------|------|-------------|
| GitHub Actions | `infrastructure/devops/github_actions.py` | Workflow creation |
| GitLab CI | `infrastructure/devops/gitlab_ci.py` | Pipeline creation |
| Template Engine | `infrastructure/devops/templates.py` | CI/CD templates |

### 8.2 Docker Tools

| Component | File | Description |
|-----------|------|-------------|
| Docker Builder | `infrastructure/devops/docker.py` | Build/push images |
| Compose Manager | `infrastructure/devops/compose.py` | Docker Compose |
| Dockerfile Gen | `infrastructure/devops/dockerfile_gen.py` | Generate Dockerfiles |

### 8.3 Kubernetes Tools

| Component | File | Description |
|-----------|------|-------------|
| K8s Deployer | `infrastructure/devops/k8s.py` | Deploy manifests |
| Helm Manager | `infrastructure/devops/helm.py` | Helm operations |
| K8s Monitor | `infrastructure/devops/k8s_monitor.py` | Status/logs |

### 8.4 Cloud Adapters

| Component | File | Description |
|-----------|------|-------------|
| AWS Adapter | `infrastructure/devops/cloud/aws.py` | AWS deployments |
| GCP Adapter | `infrastructure/devops/cloud/gcp.py` | GCP deployments |
| Azure Adapter | `infrastructure/devops/cloud/azure.py` | Azure deployments |

### 8.5 Commands

#### GitHub Actions
```
/devops gh-workflow create    # Create workflow
/devops gh-workflow list     # List workflows
/devops gh-workflow run      # Trigger workflow
/devops gh-workflow status   # Check status
/devops gh-secrets add       # Add secret
```

#### GitLab CI
```
/devops gl-pipeline create   # Create pipeline
/devops gl-pipeline list     # List pipelines
/devops gl-pipeline run      # Trigger pipeline
/devops gl-vars add          # Add variable
```

#### Docker
```
/devops docker build <img>   # Build image
/devops docker push <img>    # Push image
/devops docker run <img>     # Run container
/devops dockerfile generate  # Generate Dockerfile
```

#### Kubernetes
```
/devops k8s deploy <file>   # Deploy manifest
/devops k8s scale <dep>     # Scale deployment
/devops k8s status          # Cluster status
/devops k8s logs <pod>      # Pod logs
/devops helm install <chart> # Install chart
```

## Language Templates

### Python
```yaml
stages: [test, build, deploy]
test:
  script: [pytest, black, mypy, coverage]
build:
  script: [docker build]
deploy:
  script: [docker push]
```

### Node.js
```yaml
stages: [test, build, deploy]
test:
  script: [npm test, eslint]
build:
  script: [npm run build]
deploy:
  script: [docker build]
```

### Rust
```yaml
stages: [test, build, deploy]
test:
  script: [cargo test, cargo clippy]
build:
  script: [cargo build --release]
deploy:
  script: [docker build]
```

### Go
```yaml
stages: [test, build, deploy]
test:
  script: [go test, golangci-lint]
build:
  script: [go build]
deploy:
  script: [docker build]
```

## Acceptance Criteria

- [ ] GitHub Actions workflows created
- [ ] GitLab CI pipelines created
- [ ] Docker build/push works
- [ ] Kubernetes deploy works
- [ ] Cloud deployments functional
- [ ] CI/CD templates generated

## Test Requirements

| Test File | Coverage Target |
|-----------|----------------|
| `test_github_actions.py` | 95% |
| `test_gitlab_ci.py` | 95% |
| `test_docker_ops.py` | 90% |
| `test_k8s.py` | 90% |
| `test_cloud.py` | 90% |

## Commit Structure

```
feat(devops): implement GitHub Actions integration
feat(devops): implement GitLab CI integration
feat(devops): add Docker operations
feat(devops): implement Kubernetes tools
feat(devops): add AWS adapter
feat(devops): add GCP adapter
feat(devops): add Azure adapter
feat(devops): create CI/CD templates
test(devops): add GitHub Actions tests
test(devops): add GitLab CI tests
test(devops): add Docker tests
test(devops): add K8s tests
docs(specs): add devops phase specification
```

## Dependencies

- Phase 4: Tools (completed)
- Phase 6: Multi-Agent (for DevOps agent)

## Time Estimate

40 hours / 1 week
