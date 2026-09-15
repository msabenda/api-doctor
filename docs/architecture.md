# Architecture

API Doctor is a monorepo with two independently testable applications:

- `backend`: FastAPI service and generated OpenAPI contract.
- `frontend`: React and TypeScript user interface.

Backend modules separate outbound HTTP transport, URL/network policy, diagnostic rules, secret redaction, and API models. The browser calls the backend rather than arbitrary APIs so security policy can be applied consistently.

## SSRF boundary

`backend/app/security.py` validates targets before transport use. It rejects localhost and every resolved address that is private, loopback, link-local, multicast, reserved, unspecified, or otherwise non-global. All DNS answers must pass—not merely the first one. IPv4, IPv6, IPv4-mapped IPv6, legacy numeric host forms, explicit ports, and DNS failures have dedicated tests.

Validation alone does not eliminate DNS rebinding between lookup and connection. Live outbound execution therefore remains disabled until the transport pins connections to a validated address and revalidates every redirect destination.
