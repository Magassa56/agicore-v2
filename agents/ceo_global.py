from brain.llm import ask_llm

def ceo_global_v12(system_state, economy_state):
    """🧠 Global CEO V12 : Pilote le conglomérat d'entreprises IA."""
    prompt = f"""
    You are AGIcore Global CEO (Level 12).
    You manage a CONGLOMERATE of AI-driven business units.

    BUSINESS UNITS:
    - CAD Company (3D products)
    - AI SaaS (API Services)
    - Trading Fund (Capital management)
    - Content Studio (Marketing acquisition)

    STATE: {system_state}
    ECONOMY: {economy_state}

    OUTPUT:
    - Expansion plan for internal startups.
    - Resource allocation between units.
    - New market entry decisions.
    """
    return ask_llm(prompt, priority="critical")
