# AgentOS Architecture

This document describes the system architecture, component relationships, and data flows in AgentOS.

## System Overview

AgentOS is a production-ready API template for running AI agents built on the Agno framework. It provides a FastAPI-based web server that exposes AI agents capable of knowledge-based Q&A and tool execution.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebUI[Web UI<br/>os.agno.com]
        API_Client[API Clients]
        CLI[CLI Tools]
    end

    subgraph "API Gateway"
        FastAPI[FastAPI Server<br/>:8000]
    end

    subgraph "Agent Layer"
        AgentOS[AgentOS<br/>Orchestrator]
        KA[Knowledge Agent]
        MCP[MCP Agent]
    end

    subgraph "AI Services"
        LiteLLM[LiteLLM<br/>Multi-Provider]
        Embedder[Embeddings<br/>text-embedding-3-small]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>:5432)]
        PGVector[pgvector<br/>Extension]
        Redis[(Redis<br/>:6379<br/>Optional)]
    end

    WebUI --> FastAPI
    API_Client --> FastAPI
    CLI --> FastAPI

    FastAPI --> AgentOS
    AgentOS --> KA
    AgentOS --> MCP

    KA --> LiteLLM
    KA --> Embedder
    KA --> PGVector
    MCP --> LiteLLM

    Embedder --> PGVector
    PGVector --> PG
    KA --> PG
    KA -.-> Redis
    MCP --> PG
    MCP -.-> Redis

    classDef primary fill:#4a90d9,stroke:#2c5282,color:#fff
    classDef agent fill:#48bb78,stroke:#276749,color:#fff
    classDef data fill:#ed8936,stroke:#c05621,color:#fff
    classDef external fill:#9f7aea,stroke:#6b46c1,color:#fff
    classDef optional fill:#ed8936,stroke:#c05621,color:#fff,stroke-dasharray: 5 5

    class FastAPI,AgentOS primary
    class KA,MCP agent
    class PG,PGVector data
    class Redis optional
    class LiteLLM,Embedder,WebUI external
```

## Component Architecture

```mermaid
graph LR
    subgraph "app/"
        main[main.py]
        appconfig[config.py]
        config[config.yaml]
    end

    subgraph "agents/"
        ka[knowledge_agent.py]
        mcp[mcp_agent.py]
    end

    subgraph "db/"
        url[url.py]
        session[session.py]
    end

    main --> ka
    main --> mcp
    main --> config
    ka --> appconfig
    ka --> session
    mcp --> appconfig
    mcp --> session
    session --> url

    classDef entry fill:#4a90d9,stroke:#2c5282,color:#fff
    classDef agent fill:#48bb78,stroke:#276749,color:#fff
    classDef db fill:#ed8936,stroke:#c05621,color:#fff
    classDef cfg fill:#9f7aea,stroke:#6b46c1,color:#fff

    class main entry
    class ka,mcp agent
    class url,session db
    class appconfig,config cfg
```

## Data Flow Diagrams

### Chat Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant F as FastAPI
    participant A as Agent
    participant L as LiteLLM
    participant K as Knowledge Base
    participant D as PostgreSQL

    C->>F: POST /v1/chat/{agent}
    F->>A: Forward message

    alt Knowledge Agent
        A->>K: Search knowledge
        K->>D: Vector similarity query
        D-->>K: Relevant chunks
        K-->>A: Context documents
    end

    A->>L: Generate response
    L-->>A: LLM response
    A->>D: Store session/memory
    A-->>F: Response + sources
    F-->>C: JSON response
```

### Knowledge Ingestion Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Knowledge Agent
    participant E as Embedder
    participant V as pgvector
    participant D as PostgreSQL

    C->>A: Add knowledge (URL/text)
    A->>A: Fetch & chunk content

    loop For each chunk
        A->>E: Generate embedding
        E-->>A: Vector [1536 dims]
        A->>V: Store with metadata
        V->>D: INSERT embedding
    end

    A-->>C: Success + chunk count
```

## Component Details

### AgentOS Orchestrator

The central orchestrator that manages agent lifecycle and routing.

```mermaid
classDiagram
    class AgentOS {
        +name: str
        +agents: List[Agent]
        +config: str
        +get_app() FastAPI
        +serve(app, reload)
    }

    class Agent {
        +name: str
        +model: LLM
        +db: PostgresDb | RedisDb
        +instructions: str
        +knowledge: Knowledge
        +tools: List[Tool]
        +cli_app(stream)
    }

    class Knowledge {
        +name: str
        +vector_db: PgVector
        +max_results: int
        +insert(name, url)
        +search(query)
    }

    AgentOS "1" --> "*" Agent
    Agent "1" --> "0..1" Knowledge
```

### Database Schema

```mermaid
erDiagram
    AGENT_SESSIONS {
        uuid id PK
        string agent_id
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }

    AGENT_MEMORY {
        uuid id PK
        uuid session_id FK
        string role
        text content
        jsonb metadata
        timestamp created_at
    }

    KNOWLEDGE_AGENT_DOCS {
        uuid id PK
        string name
        text content
        vector embedding
        jsonb metadata
        timestamp created_at
    }

    AGENT_SESSIONS ||--o{ AGENT_MEMORY : contains
```

## Deployment Architecture

### Docker Compose Stack

```mermaid
graph TB
    subgraph "Docker Network: agentos"
        subgraph "agentos-api"
            FastAPI[FastAPI<br/>uvicorn]
            Python[Python 3.12]
            AppCode[/app volume]
        end

        subgraph "agentos-db"
            Postgres[PostgreSQL 18]
            PGVector[pgvector ext]
            DBData[/pgdata volume]
        end

        subgraph "agentos-redis [Optional]"
            RedisServer[Redis 7]
            RedisData[/redisdata volume]
        end
    end

    subgraph "External"
        Host[Host Machine]
        LiteLLM_API[LiteLLM API/Proxy]
    end

    Host -->|:8000| FastAPI
    Host -->|:5432| Postgres
    Host -.->|:6379| RedisServer
    FastAPI -->|internal:5432| Postgres
    FastAPI -.->|internal:6379| RedisServer
    FastAPI -->|HTTPS| LiteLLM_API

    classDef container fill:#4a90d9,stroke:#2c5282,color:#fff
    classDef volume fill:#48bb78,stroke:#276749,color:#fff
    classDef external fill:#9f7aea,stroke:#6b46c1,color:#fff
    classDef optional fill:#4a90d9,stroke:#2c5282,color:#fff,stroke-dasharray: 5 5

    class FastAPI,Python,Postgres,PGVector container
    class RedisServer optional
    class AppCode,DBData,RedisData volume
    class Host,LiteLLM_API external
```

### Production Deployment

```mermaid
graph TB
    subgraph "Internet"
        Users[Users]
    end

    subgraph "Load Balancer"
        LB[nginx/ALB]
    end

    subgraph "Container Orchestration"
        subgraph "API Replicas"
            API1[agentos-api-1]
            API2[agentos-api-2]
            API3[agentos-api-3]
        end
    end

    subgraph "Database"
        PG_Primary[(PostgreSQL<br/>Primary)]
        PG_Replica[(PostgreSQL<br/>Replica)]
    end

    subgraph "Cache"
        Redis[(Redis)]
    end

    Users --> LB
    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> PG_Primary
    API2 --> PG_Primary
    API3 --> PG_Primary
    API1 --> Redis
    API2 --> Redis
    API3 --> Redis

    PG_Primary --> PG_Replica
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| API Framework | FastAPI | High-performance async web server |
| Agent Framework | Agno | AI agent orchestration |
| LLM Provider | LiteLLM | Multi-provider model gateway (SDK or Proxy) |
| Embeddings | text-embedding-3-small | Vector embeddings for search |
| Database | PostgreSQL 18 | Primary data store + knowledge base |
| Vector Search | pgvector | Similarity search extension |
| Session Storage | PostgreSQL / Redis | Agent sessions (Redis optional) |
| Container | Docker | Application packaging |
| Orchestration | Docker Compose | Local development stack |
| Dev Workflow | mise | Python/venv/task management |

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network"
            TLS[TLS 1.3]
            Firewall[Firewall Rules]
        end

        subgraph "Authentication"
            APIKey[API Key Auth]
            JWT[JWT Tokens]
        end

        subgraph "Authorization"
            RBAC[Role-Based Access]
            RateLimit[Rate Limiting]
        end

        subgraph "Data"
            Encryption[Encryption at Rest]
            Secrets[Secret Management]
        end
    end

    TLS --> APIKey
    APIKey --> RBAC
    RBAC --> Encryption
```

## Scalability Considerations

### Horizontal Scaling

- **API Layer**: Stateless, can scale horizontally behind load balancer
- **Database**: Read replicas for query distribution
- **Vector Search**: Partitioning by tenant/namespace

### Performance Optimization

- **Connection Pooling**: SQLAlchemy with `pool_pre_ping`
- **Async Operations**: FastAPI async endpoints
- **Caching**: Optional Redis for session storage (start with `--profile redis`)
- **Streaming**: SSE for real-time responses
- **Configuration**: Environment-driven model selection (per-agent or default)

## Monitoring & Observability

```mermaid
graph LR
    subgraph "Metrics"
        Prometheus[Prometheus]
        Grafana[Grafana]
    end

    subgraph "Logging"
        Logs[Application Logs]
        ELK[ELK Stack]
    end

    subgraph "Tracing"
        OTel[OpenTelemetry]
        Jaeger[Jaeger]
    end

    App[AgentOS] --> Prometheus
    App --> Logs
    App --> OTel

    Prometheus --> Grafana
    Logs --> ELK
    OTel --> Jaeger
```

## Future Architecture

Planned enhancements:

1. **Multi-tenancy**: Isolated agent environments per tenant
2. **Agent Teams**: Collaborative multi-agent workflows
3. **Event Sourcing**: Full audit trail of agent interactions
4. **Plugin System**: Dynamic tool loading
5. **Federation**: Distributed agent networks
