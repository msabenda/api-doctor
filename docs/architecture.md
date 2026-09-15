# Architecture

API Doctor is a monorepo with two independently testable applications:

- `backend`: FastAPI service and generated OpenAPI contract.
- `frontend`: React and TypeScript user interface.

Future backend modules will separate outbound HTTP transport, URL/network policy, diagnostic rules, secret redaction, and API models. The browser will call the backend rather than arbitrary APIs so security policy can be applied consistently.
