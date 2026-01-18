# 🐢 TurboShells

**A persistent turtle racing simulation with real-time web multiplayer.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev)
[![PixiJS](https://img.shields.io/badge/PixiJS-8-E91E63.svg)](https://pixijs.com)

---

## 🏗️ Architecture

TurboShells uses a **Hexagonal Architecture** to decouple simulation from rendering:

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌─────────────┐  ┌───────────────┐  ┌───────────────────┐  │
│  │ useRaceSocket│  │ Paper Doll   │  │ RaceStage (PixiJS)│  │
│  │   (30Hz)    │  │ Assembler    │  │   Interpolation   │  │
│  └──────┬──────┘  └───────────────┘  └───────────────────┘  │
└─────────┼───────────────────────────────────────────────────┘
          │ WebSocket
┌─────────┴───────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ RaceOrchestrator│  │ConnectionManager│  │ REST /api/*  │  │
│  │   60Hz→30Hz    │  │  Zombie Cleanup │  │   Roster     │  │
│  └────────┬────────┘  └────────────────┘  └──────────────┘  │
└───────────┼─────────────────────────────────────────────────┘
            │
┌───────────┴─────────────────────────────────────────────────┐
│                    Core Engine (Python)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ RaceEngine  │  │ TurtleState │  │  GenomeCodec        │  │
│  │  (60Hz)     │  │  (Pydantic) │  │  B1-S2-P0-CFF0000   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────┴────────────────────────────────┐│
│  │              SQLite (turboshells.db)                    ││
│  │  TurtleDB │ RaceResultDB                                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+

### Backend
```bash
# Install dependencies
pip install -e ".[server]"

# Start server
uvicorn src.server.app:app --port 8765
```

### Frontend
```bash
cd web
npm install
npm run dev
```

Open `http://localhost:5173` and click **Start Race**!

---

## 📁 Project Structure

```
src/
├── engine/              # Headless simulation core
│   ├── race_engine.py   # 60Hz tick-based physics
│   ├── models.py        # Pydantic: TurtleState, RaceSnapshot
│   ├── genome_codec.py  # Paper Doll encoding
│   └── persistence.py   # SQLModel: TurtleDB, RaceResultDB
├── server/              # FastAPI WebSocket bridge
│   ├── app.py           # CORS, lifespan, routes
│   ├── websocket_manager.py
│   ├── race_orchestrator.py
│   └── routes/
│       ├── race.py      # /ws/race WebSocket
│       └── roster.py    # /api/turtles REST
└── game/                # Original game entities

web/
├── src/
│   ├── hooks/           # useRaceSocket
│   ├── lib/             # paperDoll, interpolation
│   ├── components/      # RaceStage (PixiJS)
│   └── types/           # TypeScript interfaces
└── vite.config.ts
```

---

## 🔌 API Reference

### WebSocket: `/ws/race`
```json
// Server → Client (30Hz)
{"tick": 150, "turtles": [...], "finished": false}

// Client → Server
{"action": "start"}
{"action": "stop"}
```

### REST Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/turtles` | GET | List all turtles |
| `/api/turtles` | POST | Create turtle |
| `/api/history` | GET | Race history |
| `/api/stats/{id}` | GET | Turtle statistics |

---

## 🧬 Paper Doll System

Turtles are rendered from a compact **genome string**:

```
B1-S2-P0-CFF0000
│  │  │  └─ Color (hex)
│  │  └──── Pattern type
│  └─────── Shell type
└────────── Body type
```

The frontend parses this into layered sprites with dynamic tinting.

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Physics tick rate | 60 Hz |
| Network broadcast | 30 Hz |
| JSON per turtle | ~172 bytes |
| Interpolation | Linear lerp |

---

## 🧪 Testing

```bash
# Backend tests
pytest tests/ -v

# Frontend build verification
cd web && npm run build
```

---

## 📜 License

MIT