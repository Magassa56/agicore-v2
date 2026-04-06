from brain.llm import ask_llm

def business_factory(input_idea):
    """🏭 Business Factory (Le département de création de valeur)."""
    prompt = f"""
    You are AGIcore Business Factory AI.

    Create a full business plan:

    INPUT:
    {input_idea}

    OUTPUT:
    - product idea (CAD / digital / service)
    - target audience
    - pricing model
    - acquisition strategy
    - automation plan
    """
    
    return ask_llm(prompt, priority="low")
