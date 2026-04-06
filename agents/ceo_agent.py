from brain.llm import ask_llm

def ceo_prompt(state, market, products):
    """🧠 CEO Agent (Le garant de la rentabilité)."""
    prompt = f"""
    You are AGIcore CEO Agent.

    Build strategy:
    - maximize revenue
    - prioritize CAD products
    - optimize trading + content synergy

    STATE:
    {state}

    MARKET:
    {market}

    PRODUCTS:
    {products[-5:] if products else "Aucun"}

    Output:
    - next business move
    - product to build
    - marketing strategy
    """
    
    return ask_llm(prompt, priority="critical")
