from brain.llm import ask_llm

def sre_global_governor(state):
    """🧯 SRE Global Governor : Surveille la santé du réseau distribué."""
    prompt = f"""
    You are AGIcore SRE GLOBAL GOVERNOR.

    RULES:
    - Prevent distributed system failure (split-brain).
    - Avoid cloud cost explosion on multi-nodes.
    - Block unsafe node behavior.
    - Enforce global rollback policies.

    NETWORK STATE:
    {state}

    OUTPUT (STRICT JSON):
    {{
      "scale_up_nodes": [],
      "shutdown_nodes": [],
      "risk_level": 0-100,
      "action": "allow | restrict | emergency_stop",
      "reason": "..."
    }}
    """
    return ask_llm(prompt, priority="critical")
