# AGENTS.md - Smart FCU Simulator

Guidelines for AI coding agents working in this repository.

## Project Overview

Non-intrusive Plug-and-Play Adaptive HVAC Control System prototype:
- **Backend**: Python FastAPI, SQLAlchemy async, uv package manager
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Database**: SQLite with async support
- **Real-time**: WebSocket for live sensor data

## Build/Run Commands

### Docker (Recommended)
```bash
bun run dev           # Start all services (development)
bun run prod          # Production mode
bun run down          # Stop containers
bun run logs          # View all logs
```

### Frontend (from /frontend)
```bash
bun install && bun run dev    # Install + dev server (port 5173)
bun run build                 # TypeScript check + production build
bun run lint                  # ESLint
```

### Backend (from /backend)
```bash
uv sync                                              # Install dependencies
uv run uvicorn app.main:app --reload --port 8000     # Dev server
```

### Testing
```bash
# Backend
uv run pytest                        # All tests
uv run pytest tests/test_api.py      # Single file
uv run pytest -k "test_zones"        # Pattern match
uv run pytest -x                     # Stop on first failure

# Frontend
bun run test                                         # All tests
bun run test -- src/hooks/useWebSocket.test.ts       # Single file
```

## Code Style - Python

### Import Order
```python
# 1. Standard library
from datetime import datetime
from typing import List, Optional

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local (always use 'app.' prefix)
from app.database import get_db
from app.models import Zone
```

### Conventions
- **Files**: `snake_case.py` | **Classes**: `PascalCase` | **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE` | **Private**: `_underscore_prefix`
- Always type annotate function parameters and return types
- Use `Optional[T]` for nullable, `Mapped[T]` for SQLAlchemy columns

### FastAPI Pattern
```python
router = APIRouter(prefix="/api/zones", tags=["zones"])

@router.get("", response_model=List[ZoneResponse])
async def get_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone))
    return result.scalars().all()
```

### Pydantic Schema
```python
class ZoneBase(BaseModel):
    name: str

class ZoneResponse(ZoneBase):
    id: str
    class Config:
        from_attributes = True  # ORM mode
```

### Error Handling
```python
if not zone:
    raise HTTPException(status_code=404, detail="Zone not found")
```

## Code Style - TypeScript/React

### Import Order
```typescript
// 1. React
import { useState, useEffect } from 'react'
// 2. Third-party
import { LineChart } from "recharts"
// 3. UI components
import { Card } from "@/components/ui/card"
// 4. Local components, hooks, utils
import { SensorCard } from "./SensorCard"
import { cn } from "@/lib/utils"
// 5. Icons
import { Server } from "lucide-react"
```

### Conventions
- **Components**: `PascalCase.tsx` | **Utilities/hooks**: `camelCase.ts`
- **Interfaces**: `PascalCase` with Props suffix (e.g., `ZonePanelProps`)
- 2-space indent, no semicolons, single quotes for imports

### Component Pattern
```typescript
interface ZonePanelProps {
  zone: Zone
  onUpdate?: (zone: Zone) => void
}

export function ZonePanel({ zone, onUpdate }: ZonePanelProps) {
  const [loading, setLoading] = useState(false)
  return <Card>{/* content */}</Card>
}
```

### Exports
- Named exports: `export function Component() {}`
- Default only for App.tsx

## Project Structure

- `backend/app/`: main.py (FastAPI), database.py, models/, schemas/, routers/, services/
- `frontend/src/`: App.tsx, components/ (ui/, dashboard/, charts/), hooks/, lib/

## Key Details

- **uv** package manager for Python (not pip/poetry)
- SQLAlchemy 2.0 async: `await db.execute(select(...))`
- Path alias: `@/` maps to `src/`
- Vite proxies `/api/*` and `/ws/*` to backend
- WebSocket endpoint: `/ws/sensors`

## API Endpoints

- `GET /api/zones` - List zones
- `GET /api/devices` - List devices (?zone_id=)
- `GET /api/sensors/{zone_id}/readings` - Sensor readings
- `GET /api/predictions/{zone_id}/latest` - Latest prediction
- `POST /api/chat` - AI assistant chat (requires GEMINI_API_KEY)
- `GET /api/chat/status` - Check if chat is available
- `WS /ws/sensors` - Real-time data stream
- `GET /health` - Health check

## Common Tasks

**New API endpoint**: schema in `schemas/` → route in `routers/` → register in `main.py`
**New component**: Create in `components/` subfolder, use shadcn/ui, named export
**Add shadcn component**: `cd frontend && bunx shadcn@latest add <name>`

## Notes

- No authentication (demo dashboard)
- Backend uses print() for logging
- Default zones: "Server Room" (18°C), "Open Office" (23°C)