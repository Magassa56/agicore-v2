from sre.safety_engine import validate_patch
from git_guard.snapshot import create_snapshot
from execution_sandbox.sandbox import run_in_sandbox
from core.policy_engine import safe_self_modify
from brain.llm import ask_llm
from memory.vector_db.semantic_memory import memory_engine
import time

def propose_improvement(system_state, logs):
    """🧠 Propose une amélioration via LLM + VectorDB."""
    query = f"Amélioration de performance pour CPU {system_state['cpu']}%"
    past_experiences = memory_engine.query_memory(query, n_results=2)
    
    context_str = ""
    if past_experiences['documents']:
        context_str = "\n--- EXPÉRIENCES PASSÉES PERTINENTES ---\n"
        for i, doc in enumerate(past_experiences['documents'][0]):
            meta = past_experiences['metadatas'][0][i]
            context_str += f"- Expérience {i+1} (Type: {meta['type']}, Résultat: {meta['result']}): {doc[:100]}...\n"

    prompt = f"""
    Tu es AGIcore Self-Improver (Level 9 + Semantic Memory).

    Analyse le système :
    {system_state}

    Logs récents :
    {logs[-5:] if logs else "Aucun log"}
    {context_str}

    Propose UNE amélioration de code sûre (fonction Python complète).
    Donne uniquement du code Python pur prêt à être exécuté.
    """
    return ask_llm(prompt, priority="critical")

def apply_self_modification(patch, sre_decision):
    """🔥 Applique le patch (avec validation SRE Master + Git Guard + Sandbox)."""
    print("🔥 [SELF IMPROVER] Tentative d'application du patch...")
    
    # 1. 🛡️ Validation SRE Master (Level 9 Policy Engine)
    policy_check = safe_self_modify(patch, sre_decision)
    if policy_check != "PATCH CLEARED FOR EXECUTION":
        memory_engine.add_memory(patch, {"type": "patch_attempt", "result": policy_check, "timestamp": time.time()})
        return policy_check

    # 2. 🧯 SÉCURITÉ Code (Mots-clés)
    if not validate_patch(patch):
        memory_engine.add_memory(patch, {"type": "patch_attempt", "result": "REJECTED_SAFETY", "timestamp": time.time()})
        return "PATCH REJETÉ (unsafe keywords)"

    # 3. 💾 SNAPSHOT
    create_snapshot()

    # 4. 💉 EXÉCUTION SANDBOX
    result = run_in_sandbox(patch)
    
    if isinstance(result, str):
         memory_engine.add_memory(patch, {"type": "patch_attempt", "result": f"FAILED_{result[:50]}", "timestamp": time.time()})
         return f"PATCH ÉCHOUÉ : {result}"
    
    memory_engine.add_memory(patch, {"type": "patch_attempt", "result": "SUCCESS", "timestamp": time.time()})
    return "PATCH APPLIQUÉ (Sandbox + Mémorisé)"
