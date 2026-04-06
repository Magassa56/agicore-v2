from brain.llm import ask_llm

def negotiate(client_request):
    """🤝 Sales Negotiator : L'agent de vente d'AGIcore."""
    prompt = f"""
    You are AGIcore AI Sales Negotiator (Level 12).

    CLIENT REQUEST:
    {client_request}

    OBJECTIVES:
    - Maximize net profit.
    - Close the deal successfully.
    - Maintain long-term brand trust.

    GENERATE:
    1. Offer Price (justify it based on complexity).
    2. Sales Argumentation (why choose AGIcore?).
    3. Upsell Opportunity (propose an additional service).
    """
    
    # Priority critical pour la signature de contrats
    return ask_llm(prompt, priority="critical")
