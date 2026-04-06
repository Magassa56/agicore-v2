def create_api_service(name, function_ref):
    """🌐 API Layer : Expose les capacités d'AGIcore en tant que services SaaS."""
    endpoint = f"/api/v1/{name.lower()}"
    print(f"🔌 [API] Endpoint exposé : {endpoint}")
    return {
        "service": name,
        "endpoint": endpoint,
        "handler": function_ref
    }

def expose_core_services():
    """Initialise le catalogue de services API."""
    services = [
        create_api_service("CAD_Generator", "cad_maker.generate"),
        create_api_service("Market_Analysis", "trader.analyze"),
        create_api_service("Content_Automation", "content_studio.create")
    ]
    return services
