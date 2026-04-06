from brain.llm import ask_llm

def agent_creator_prompt(goal, current_agents):
    """🧬 Agent Creator : Conçoit de nouveaux employés IA pour AGICore."""
    prompt = f"""
    You are AGIcore Agent Creator (reproduction module).

    OBJECTIVE:
    Design a new specialized AI agent to achieve this goal:
    {goal}

    CURRENT WORKFORCE:
    {current_agents}

    OUTPUT:
    - Agent Name
    - Core Responsibilities
    - Specialized Tools needed
    - SRE Safety Constraints
    - Input/Output schema
    """
    
    return ask_llm(prompt, priority="critical")
