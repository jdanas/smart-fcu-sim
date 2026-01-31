# Smart FCU Simulator

Non-intrusive Plug-and-Play Adaptive HVAC Control System - Research Dashboard Prototype

## Quick Start

### Development Mode
```bash
bun run dev
```
This will start:
- Backend (FastAPI) at http://localhost:8000
- Frontend (React/Vite) at http://localhost:5173

### Production Mode
```bash
bun run prod
```

### Other Commands
```bash
bun run down          # Stop all containers
bun run clean         # Stop and remove volumes/images
bun run logs          # View all logs
bun run logs:backend  # View backend logs only
bun run logs:frontend # View frontend logs only
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │
│  React + Vite   │     │    FastAPI      │
│   Port: 5173    │◀────│   Port: 8000    │
└─────────────────┘ WS  └─────────────────┘
                              │
                              ▼
                        ┌───────────┐
                        │  SQLite   │
                        └───────────┘
```

## Features

- Real-time sensor data visualization
- AI-predicted temperature (linear regression)
- Plug-and-play device discovery simulation
- Adaptive HVAC control interface
- Monotone research dashboard aesthetic

## Zones

| Zone | Setpoint | Sensors |
|------|----------|---------|
| Server Room | 18°C | Temperature, Humidity |
| Open Office | 23°C | Temperature, Humidity |
