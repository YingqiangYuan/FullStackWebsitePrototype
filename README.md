# Apex Full-Stack Microservices Architecture

## Overview
This project demonstrates a production-minded, containerized full-stack system designed using modern enterprise architecture principles. The system is composed of multiple independently deployable services, orchestrated using Docker Compose, and communicates through well-defined HTTP/JSON APIs.

The goal of this project is to showcase scalable system design, clean service boundaries, secure authentication, and cloud-ready deployment practices.

---

## Architecture Overview

The system consists of the following components:

### Frontend (React)
- A standalone React application built with modern tooling.
- Communicates exclusively with the API Gateway via HTTP/JSON.
- Decoupled from backend implementation details.

### API Gateway
- Central entry point for all client requests.
- Handles routing, request validation, and service aggregation.
- Abstracts internal backend service complexity.

### Auth Service
- Dedicated authentication and authorization service.
- Isolates security logic from business functionality.
- Designed to map cleanly to Spring Security or Node.js middleware patterns.

### Data Service
- Responsible for data access and manipulation.
- Exposes controlled APIs instead of direct database access.
- Supports scalable enterprise data workflows.

### Visualization Service
- Handles data transformation and visualization logic.
- Separated from raw data ingestion for extensibility.

### Database
- Centralized persistence layer.
- Configuration managed via environment variables.
- Treated as a shared enterprise resource.

---

## Docker & Deployment Model

Each service runs inside its own Docker container:
- Independent runtime environments
- Clear dependency isolation
- Reproducible deployments

Docker Compose is used to:
- Orchestrate multi-service startup
- Manage service networking
- Inject environment variables

This setup mirrors real-world cloud deployments and prepares the system for Kubernetes-based scaling.

---

## Running the Project

### Prerequisites
- Docker
- Docker Compose

### Run All Services
```bash
docker-compose up --build
```

Once running:
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000

---

## Running Individual Services

Each service can be run independently for development:

```bash
cd auth_service
docker build -t auth_service .
docker run -p 5001:5001 auth_service
```

Repeat similarly for `data_service`, `viz_service`, and `gateway`.

---

## Testing

Each backend service includes isolated tests.

Run tests inside a service container:
```bash
docker exec -it <container_name> pytest
```

Testing validates:
- API correctness
- Authentication behavior
- Integration boundaries

---

## Future Enhancements

Potential next steps include:
- Replace gateway with Node.js / Express implementation
- Migrate backend services to Spring Boot
- Add centralized logging and monitoring
- Introduce CI/CD pipelines
- Deploy to Kubernetes (EKS/GKE)
- Implement role-based access control
- Add API rate limiting and caching

---
