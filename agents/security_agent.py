from brain.llm import ask_llm

def security_agent_prompt(system_state, economy_state, security_state):
    """🔐 Civilization SRE Governor : Empêche les défaillances en cascade de l'écosystème."""
    prompt = f"""
    You are AGIcore Civilization SRE Governor.

    You control a global AI ecosystem.

    OBJECTIVES:
    - ensure system stability across all AGI nodes
    - prevent cascading failures
    - enforce zero trust security
    - optimize global cost and performance
    - maintain economic balance

    SYSTEM:
    {system_state}

    ECONOMY:
    {economy_state}

    SECURITY:
    {security_state}

    RETURN JSON:
    {{
      "global_risk": "LOW | MEDIUM | HIGH | CRITICAL",
      "actions": [
        "isolate_node",
        "scale_cluster",
        "reduce_cost",
        "pause_economy",
        "rotate_keys"
      ],
      "strategy": "..."
    }}
    """
    return ask_llm(prompt, priority="critical")
