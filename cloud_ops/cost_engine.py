from brain.llm import ask_llm

def cloud_sre_prompt(metrics):
    """☁️ FinOps SRE Engine : Optimisation des coûts Cloud."""
    prompt = f"""
    You are Cloud FinOps SRE Master.

    Reduce cost without breaking system:

    METRICS:
    {metrics}

    ACTIONS:
    - shutdown idle GPU
    - downgrade model
    - batch processing
    - cache results

    Output JSON only.
    """
    return ask_llm(prompt, priority="low")
