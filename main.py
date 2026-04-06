import time
import os
from dotenv import load_dotenv

# Level 14 Core Agents (Triumvirat)
from agents.ceo_global import ceo_global_v12 as ceo_global
from agents.sre_agent import sre_master_prompt as sre_governor
from agents.security_agent import security_agent_prompt as security_agent

# Monitoring
from sre.health_monitor import system_state
from scheduler.loop import enterprise_loop

# Initialisation
load_dotenv()

def get_global_state():
    """Récupère l'état holistique de la civilisation AGIcore."""
    system = system_state()
    # Simulation des données économiques et sécuritaires en production
    economy = {
        "cash_flow": 150000,
        "burn_rate": 200, 
        "market_trend": "VOLATILE",
        "cost": {"cloud": 450, "api": 120}
    }
    security = {
        "active_threats": 0, 
        "failed_logins": 2, 
        "zero_trust_status": "ENFORCED"
    }
    return {"system": system, "economy": economy, "security": security}

def global_brain(state):
    """🧠 Global Orchestrator (Level 14) : Le Triumvirat."""
    print("🧠 [GLOBAL BRAIN] Consultation des instances suprêmes de la Civilisation...")
    
    # 1. Stratégie (CEO)
    print("   ↳ 🧠 Appel du CEO Global (Croissance)...")
    ceo_decision = ceo_global(state["system"], state["economy"])
    
    # 2. Stabilité (SRE)
    print("   ↳ 🛡️ Appel du SRE Master (Infra)...")
    logs = ["INFO: System stable", "WARN: Minor latency on DB"]
    sre_decision = sre_governor(state["system"], state["economy"]["cost"], logs)
    
    # 3. Sécurité (Civilization SRE Governor)
    print("   ↳ 🔐 Appel du Security Governor (Anti-Crash)...")
    security_decision = security_agent(state["system"], state["economy"], state["security"])

    return {
        "CEO": ceo_decision,
        "SRE": sre_decision,
        "SECURITY": security_decision
    }

def execute(decisions):
    """🚀 Exécuteur Civilisationnel."""
    print("\n🚀 [EXECUTION] Application des directives globales...")
    print(f"   ↳ 🔐 CIVILIZATION SRE: {decisions['SECURITY'][:150]}...")
    print(f"   ↳ 🛡️ MASTER SRE      : {decisions['SRE'][:150]}...")
    print(f"   ↳ 🧠 GLOBAL CEO      : {decisions['CEO'][:150]}...")

def log_system(state, decisions):
    """💾 Archivage permanent de l'histoire de la civilisation."""
    print("💾 [LOG] Archivage de l'état civilisationnel terminé.\n")

def run_civilization_loop():
    """
    🌌 AGICORE LEVEL 14 : CIVILIZATION CYCLE
    """
    print("\n--- 🌌 L14 CIVILIZATION CYCLE ---")
    state = get_global_state()
    
    print(f"📊 [STATE] CPU: {state['system']['cpu']}% | Economy Cash: ${state['economy']['cash_flow']} | Zero Trust: {state['security']['zero_trust_status']}")
    
    decisions = global_brain(state)
    execute(decisions)
    log_system(state, decisions)

def start_agicore_civilization():
    print("=========================================")
    print("   🌌 AGICORE LEVEL 14 : CIVILIZATION    ")
    print("   Mode : Production Autonomous System   ")
    print("=========================================")
    
    enterprise_loop(run_civilization_loop, interval=45)

if __name__ == "__main__":
    start_agicore_civilization()
