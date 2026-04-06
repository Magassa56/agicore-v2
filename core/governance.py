from brain.llm import ask_llm

def sre_governance_prompt(system_state, growth_request):
    """🧯 SRE Governor : Le régulateur éthique et technique du Niveau 10."""
    prompt = f"""
    You are AGIcore SRE GOVERNOR (Level 10).

    RULES:
    - NEVER allow system instability.
    - CAP agent creation rate (anti-spawning).
    - BLOCK cost explosion.
    - ENFORCE rollback policies.

    CURRENT SYSTEM STATE:
    {system_state}

    GROWTH REQUEST:
    {growth_request}

    OUTPUT (STRICT JSON):
    {{
      "allow_spawn_agent": true/false,
      "kill_agents": [],
      "scale_resources": ["up", "down", "stable"],
      "risk_score": 0-100,
      "reason": "..."
    }}
    """
    return ask_llm(prompt, priority="critical")
