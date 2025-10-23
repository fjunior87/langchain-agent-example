# Example Requests

This file contains example requests you can use with the Harness Pipeline Agent API.

## Pipeline Generation Examples

### Simple CI Pipeline
```json
{
  "request": "Create a simple CI pipeline for a Python application with build and test stages"
}
```

### Full CI/CD Pipeline
```json
{
  "request": "Create a complete CI/CD pipeline with the following stages: 1) Clone repository, 2) Build Docker image, 3) Run unit tests, 4) Push to Docker registry, 5) Deploy to Kubernetes production environment"
}
```

### Multi-Environment Pipeline
```json
{
  "request": "Create a pipeline that deploys to dev, staging, and production environments sequentially with manual approval required before production"
}
```

### Microservices Pipeline
```json
{
  "request": "Generate a pipeline for a microservices architecture with 3 services: auth-service, api-service, and frontend. Each should be built, tested, and deployed independently"
}
```

## Connector Generation Examples

### GitHub Connector
```json
{
  "request": "Create a GitHub connector named 'my-github-repo' for repository https://github.com/myorg/myrepo with SSH authentication"
}
```

### Docker Registry Connector
```json
{
  "request": "Create a Docker connector for DockerHub registry with username/password authentication"
}
```

### Kubernetes Cluster Connector
```json
{
  "request": "Create a Kubernetes connector for my EKS cluster in us-east-1 region"
}
```

### AWS Connector
```json
{
  "request": "Create an AWS connector using IAM role authentication for account 123456789012"
}
```

## General Query Examples

### List Pipelines
```json
{
  "request": "List all pipelines in my account"
}
```

### Get Pipeline Details
```json
{
  "request": "Show me the details of the pipeline named 'production-deployment'"
}
```

### List Connectors by Type
```json
{
  "request": "Show all GitHub connectors in my account"
}
```

### Pipeline Recommendations
```json
{
  "request": "What are the best practices for creating a CI/CD pipeline for a Node.js application?"
}
```

## Complex Scenarios

### Blue-Green Deployment
```json
{
  "request": "Create a pipeline implementing blue-green deployment strategy for a containerized application on Kubernetes"
}
```

### Canary Deployment
```json
{
  "request": "Generate a pipeline with canary deployment that gradually shifts traffic from 10% to 100% with health checks at each step"
}
```

### Multi-Cloud Pipeline
```json
{
  "request": "Create a pipeline that deploys to both AWS EKS and Google GKE clusters simultaneously"
}
```

### Infrastructure as Code Pipeline
```json
{
  "request": "Create a pipeline that runs Terraform to provision infrastructure, then deploys the application to the newly created resources"
}
```

## Testing Examples with cURL

### Generate Pipeline
```bash
curl -X POST "http://localhost:8000/api/v1/generate/pipeline" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create a CI pipeline for a Python FastAPI application with pytest tests"
  }'
```

### Generate Connector
```bash
curl -X POST "http://localhost:8000/api/v1/generate/connector" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create a GitHub connector for repository https://github.com/user/repo"
  }'
```

### General Query
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "What connectors do I have configured?"
  }'
```

## Tips for Best Results

1. **Be Specific**: Include details about your technology stack, environments, and requirements
2. **Structure Your Request**: Break down complex pipelines into clear stages or steps
3. **Mention Constraints**: Include any specific requirements like approval gates, notifications, or conditions
4. **Provide Context**: Mention your deployment target (Kubernetes, VMs, etc.) and cloud provider if relevant
5. **Use Examples**: Reference similar pipelines or patterns you want to follow

## Expected Response Format

All endpoints return a JSON response with this structure:

```json
{
  "success": true,
  "output": "pipeline:\n  name: my-pipeline\n  stages:\n    - stage:\n        name: Build",
  "intermediate_steps": [],
  "error": null
}
```

Where:
- `success`: Boolean indicating if the request was successful
- `output`: The generated YAML or response text
- `intermediate_steps`: Array of agent's reasoning steps (optional)
- `error`: Error message if the request failed (null on success)
