# API Doctor

API Doctor helps developers understand why an API request failed and how to fix it securely.

Iteration 1 provides a FastAPI health endpoint, a React landing page, local containers, and baseline CI quality gates. Request execution and diagnosis will be added incrementally.

## Prerequisites

- Python 3.12+
- Node.js 22+
- Docker with Compose (optional)

## Local development

### Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

The API is available at <http://localhost:8000>; OpenAPI docs are at `/docs`.

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

The UI is available at <http://localhost:5173>.

### Docker Compose

```bash
docker compose up --build
```

## Quality gates

```bash
cd backend && ruff check . && ruff format --check . && pytest
cd frontend && npm run lint && npm run format:check && npm run typecheck && npm test -- --run && npm run build
```

## Security

Do not use this iteration to send requests to arbitrary URLs. The request endpoint will only be introduced after transport boundaries and SSRF controls have tests. See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
