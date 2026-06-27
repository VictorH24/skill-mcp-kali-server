# Security Policy

This project can execute arbitrary terminal commands through its API and MCP tools. Treat access to the service as equivalent to shell access on the host or container.

## Safe Deployment

- Bind services to localhost by default.
- Do not expose the API or MCP bridge to untrusted networks.
- Add authentication, authorization, TLS, and network filtering before any remote deployment.
- Do not commit runtime logs, `.env` files, keys, certificates, scan outputs, or target-specific data.

## Authorized Use

Use this project only in environments you own or where you have explicit permission to perform security testing.

