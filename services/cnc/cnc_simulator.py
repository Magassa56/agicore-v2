# services/cnc/cnc_simulator.py

import logging
import random
from typing import Dict, Any, List

logger = logging.getLogger("agicore_cnc_qa")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("ops/logs/cnc_qa.log")
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class CNCQAAgent:
    """
    Simulates G-code execution to detect risks before they become physical problems.
    Calculates failure probability and a risk score.
    """

    @staticmethod
    async def simulate_gcode(gcode_data: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates the G-code against the plan and machine limits.

        Args:
            gcode_data (Dict[str, Any]): The G-code and metadata from the Coder Agent.
            plan (Dict[str, Any]): The original manufacturing plan.

        Returns:
            Dict[str, Any]: A QA report with approval status, risk scores, and issues.
        """
        gcode = gcode_data["gcode"]
        plan_id = plan["plan_id"]
        logger.info(f"CNC-QA: Starting simulation for plan {plan_id}")

        issues = []
        collision_detected = False
        
        # Highly simplified simulation logic
        # In reality, this would use a proper physics/kinematics engine (e.g., Pybullet, a CAM library)
        
        # 1. Check for known risky moves (e.g., rapid move to a low Z)
        if "G0 Z-1" in gcode or "G0 Z-2" in gcode:
            issues.append("Critical risk: Rapid move (G0) detected below Z=0. Potential for crash.")
            collision_detected = True

        # 2. Check if tool is appropriate for material (dummy check)
        if "Aluminum" in plan["material"] and "wood_router_bit" in " ".join(gcode_data["metadata"]["tool_ids"]):
             issues.append("Tool-Material mismatch: Wood router bit specified for Aluminum.")

        # 3. Calculate a risk score based on plan complexity and G-code length
        base_risk = plan.get("estimated_risk_score", 1.0)
        gcode_length_factor = len(gcode.split('\n')) / 100 # Add risk for longer programs
        risk_score = base_risk + gcode_length_factor
        
        if collision_detected:
            risk_score += 5.0 # Major penalty for collision risk

        # 4. Calculate failure probability
        # This is a placeholder. A real system would use historical data from MemoryAgent.
        failure_probability = risk_score / 50.0 + random.uniform(-0.005, 0.005)
        failure_probability = max(0.0, min(failure_probability, 1.0)) # clamp between 0 and 1

        # 5. Final approval decision
        approved = not collision_detected and failure_probability <= 0.01 and risk_score <= 7 # Allow up to risk 7, but Sentinel will gatekeep at 3
        
        if not approved:
            logger.warning(f"CNC-QA: Plan {plan_id} REJECTED. Risk Score: {risk_score:.2f}, Failure Prob: {failure_probability:.2%}")
        else:
            logger.info(f"CNC-QA: Plan {plan_id} approved. Risk Score: {risk_score:.2f}, Failure Prob: {failure_probability:.2%}")

        report = {
            "plan_id": plan_id,
            "collision_detected": collision_detected,
            "failure_probability": failure_probability,
            "risk_score": risk_score,
            "issues": issues,
            "approved_by_qa": approved
        }
        
        return report
