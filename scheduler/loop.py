import time

def run_loop(step_function, interval=15):
    """⏱️ Scheduler Level 5."""
    try:
        while True:
            start_time = time.time()
            step_function()
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass

def enterprise_loop(step_function, interval=60):
    """⏱️ Scheduler Level 8 (Entreprise Autonome)."""
    print(f"--- 🏢 AGIcore L8 Enterprise Loop Started (Interval: {interval}s) ---")
    try:
        while True:
            start_time = time.time()
            step_function()
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            
            print(f"😴 Fin d'itération L8. Attente {sleep_time:.1f}s...")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n👋 🏢 Arrêt de la boucle Entreprise L8.")
