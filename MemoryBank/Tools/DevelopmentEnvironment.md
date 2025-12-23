# Development Environment

This document defines the standard environment configuration and commands for running the MCP Server.

## Docker Configuration

*   **Image Name:** `dev-cycle-manager`
*   **Container Name:** `dev-cycle-manager-instance`
*   **Port Mapping:** Host `8000` -> Container `8000`

## Commands

### Build Image
```bash
docker build -t dev-cycle-manager .
```

### Run Container (Background)
```bash
docker run -d -p 8000:8000 --name dev-cycle-manager-instance dev-cycle-manager
```

### Stop & Remove Container
```bash
docker rm -f dev-cycle-manager-instance
```

### View Logs
```bash
docker logs -f dev-cycle-manager-instance
```

### Troubleshooting
If port 8000 is in use, check for old containers:
```bash
docker ps -a
```
