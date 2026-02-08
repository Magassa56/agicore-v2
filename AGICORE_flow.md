
```mermaid
graph TD
    subgraph User Input
        A[High-Level Goal / User Prompt]
    end

    subgraph AGICORE
        subgraph "Multi-Cognitive Planner (MCP)"
            B(agicore-mcp)
        end

        subgraph "Micro-Agents"
            C(agicore-trader)
            D(agicore-mediamaker)
            E(agicore-analytics)
            F(agicore-storage)
            G(SIMA2 Agent)
        end

        subgraph "SRE / Auto-Healing"
            H(operator)
        end
    end

    subgraph External Systems & Models
        I[Generative AI API - Gemini]
        J[Image Generation - Nano Banana]
        K[3D Virtual World]
        L[Financial Brokerage API]
        M[Data Sources]
        N[Cloud Storage]
    end

    A --> B;
    B --> C;
    B --> D;
    B --> E;
    B --> F;
    B --> G;

    C --> L;
    D --> J;
    E --> M;
    F --> N;
    G --> K;

    B -- "Uses" --> I;
    G -- "Powered by" --> I;

    H -- "Monitors & Remediates" --> B;
    H -- "Monitors & Remediates" --> C;
    H -- "Monitors & Remediates" --> D;
    H -- "Monitors & Remediates" --> E;
    H -- "Monitors & Remediates" --> F;
    H -- "Monitors & Remediates" --> G;

    style B fill:#f9f,stroke:#333,stroke-width:2px;
    style H fill:#ccf,stroke:#333,stroke-width:2px;
    style I fill:#f6d,stroke:#333,stroke-width:2px;
    style J fill:#f6d,stroke:#333,stroke-width:2px;
    style K fill:#d6f,stroke:#333,stroke-width:2px;
```

### Flow Description

1.  **User Input:** The process begins with a high-level goal or prompt provided by the user.

2.  **MCP (Multi-Cognitive Planner):** The `agicore-mcp` receives the user's goal. Powered by the **Gemini** language model, it breaks down the goal into a sequence of tasks (a plan).

3.  **Task Delegation:** The `agicore-mcp` delegates these tasks to the appropriate specialized micro-agents:
    *   **agicore-trader:** For financial tasks, it interacts with a **Brokerage API**.
    *   **agicore-mediamaker:** For media generation ("Génération Automatisée"), it uses the **Nano Banana** (Gemini 2.5 Flash Image) model to create images.
    *   **agicore-analytics:** For data analysis, it pulls data from various **Data Sources**.
    *   **agicore-storage:** For storage-related tasks, it interacts with **Cloud Storage**.
    *   **SIMA2 Agent:** For tasks within a simulated 3D environment, it interacts with a **3D Virtual World**. The SIMA2 agent is itself powered by **Gemini**.

4.  **Auto-Healing:** The `operator` agent continuously monitors the health of all other AGICORE services. If an agent becomes unhealthy, the `operator` automatically takes corrective action, such as restarting the service.

This unified schema illustrates how AGICORE, Gemini, SIMA2, and Nano Banana work together to form a comprehensive, autonomous, and resilient multi-agent system.
