from brain.llm import ask_llm

def sre_master_prompt(system_state, cost, logs):
    """🛡️ SRE Master Agent (Le garant de la survie du système L9)."""
    prompt = f"""
    YOU ARE AGICORE SRE MASTER ENGINEER (LEVEL 9).

    OBJECTIVES:
    - System must NEVER crash
    - Optimize cost aggressively
    - Ensure GitHub consistency
    - Prevent unsafe self-modification
    - Maintain production stability

    SYSTEM STATE:
    {system_state}

    COST METRICS:
    {cost}

    LOGS:
    {logs[-5:] if logs else "Aucun log"}

    OUTPUT FORMAT (STRICT JSON):
    {{
      "risk_level": "LOW | MEDIUM | HIGH",
      "actions": [
        "scale_down",
        "disable_agent",
        "optimize_memory",
        "rollback",
        "pause_self_modification",
        "continue"
      ],
      "reason": "..."
    }}
    """
    
    # Priority critical pour l'agent SRE
    return ask_llm(prompt, priority="critical")
