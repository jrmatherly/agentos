# AgentOS Documentation

Welcome to the AgentOS documentation. This documentation covers everything you need to know about running, developing, and extending AgentOS.

## Documentation Index

### Getting Started

- [**Getting Started Guide**](./guides/GETTING_STARTED.md) - Quick setup and first steps
- [**Creating Agents**](./guides/CREATING_AGENTS.md) - Build custom AI agents
- [**Developer Guide**](./guides/DEVELOPER_GUIDE.md) - Local development setup

### Reference

- [**API Documentation**](./api/index.html) - Interactive API reference (Swagger UI)
- [**OpenAPI Spec**](./api/openapi.yaml) - Machine-readable API specification
- [**Code Reference**](./CODE_REFERENCE.md) - Complete module and function documentation

### Architecture

- [**Architecture Overview**](./architecture/ARCHITECTURE.md) - System design and diagrams

### Project Files

- [**Project Index**](../PROJECT_INDEX.md) - Quick reference for the codebase
- [**README**](../README.md) - Main project README

## Quick Links

| Resource | Description |
|----------|-------------|
| [API Docs](http://localhost:8000/docs) | Live API documentation (when running) |
| [Control Plane](https://os.agno.com) | Agno control plane |
| [Agno Docs](https://docs.agno.com) | Agno framework documentation |
| [Discord](https://agno.link/discord) | Community support |

## Documentation Structure

```tree
docs/
├── README.md              # This file
├── CODE_REFERENCE.md      # Complete code reference
├── api/
│   ├── index.html         # Swagger UI
│   └── openapi.yaml       # OpenAPI specification
├── architecture/
│   └── ARCHITECTURE.md    # System architecture
└── guides/
    ├── GETTING_STARTED.md # Quick start guide
    ├── CREATING_AGENTS.md # Agent creation guide
    └── DEVELOPER_GUIDE.md # Development guide
```

## Contributing to Documentation

Documentation improvements are welcome! To contribute:

1. Fork the repository
2. Edit documentation files in `/docs`
3. Submit a pull request

### Style Guidelines

- Use clear, concise language
- Include code examples where helpful
- Keep formatting consistent with existing docs
- Test all code examples before submitting

## Generating Documentation

### API Documentation

The OpenAPI specification is manually maintained in `docs/api/openapi.yaml`. To view it:

1. Start AgentOS: `docker compose up -d`
2. Open http://localhost:8000/docs

Or open `docs/api/index.html` locally (requires a web server for CORS).

### Architecture Diagrams

Diagrams use [Mermaid](https://mermaid.js.org/) syntax and render automatically in:

- GitHub Markdown previews
- VS Code with Mermaid extension
- Most documentation platforms

## Feedback

Found an issue or have a suggestion? [Open an issue](https://github.com/agno-agi/agentos-docker-template/issues) on GitHub.
