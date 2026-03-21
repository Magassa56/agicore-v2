# services/cnc/sentinel.py

import logging
from typing import Dict, Any

logger = logging.getLogger("agicore_cnc_sentinel")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("ops/logs/security_audit.log")
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class CNCSentinel:
    """
    The final gatekeeper. Protects the physical machine, the human operators, and assets.
    Makes the final binary decision: ALLOW, HALT, or REQUIRE_HUMAN_CONFIRMATION.
    """
    
    # Non-negotiable safety thresholds
    MAX_FAILURE_PROBABILITY = 0.01  # 1%
    MAX_RISK_FOR_AUTO_APPROVAL = 3.0

    @staticmethod
    async def decide(qa_report: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """
        Makes the final go/no-go decision based on the QA report.

        Args:
            qa_report (Dict[str, Any]): The report from the CNC-QA Agent.
            plan (Dict[str, Any]): The original manufacturing plan.

        Returns:
            str: The final decision: "ALLOW", "HALT", or "HUMAN_CONFIRMATION".
        """
        plan_id = qa_report["plan_id"]
        risk_score = qa_report["risk_score"]
        failure_prob = qa_report["failure_probability"]
        collision = qa_report["collision_detected"]
        
        # Rule 1: Any collision risk is an immediate HALT.
        if collision:
            logger.critical(f"SENTINEL HALT ({plan_id}): Collision detected. Execution is forbidden.")
            # Here, we would trigger alerts to human operators.
            return "HALT"
            
        # Rule 2: Failure probability above threshold is an immediate HALT.
        if failure_prob > CNCSentinel.MAX_FAILURE_PROBABILITY:
            logger.critical(f"SENTINEL HALT ({plan_id}): Failure probability {failure_prob:.2%} exceeds threshold of {CNCSentinel.MAX_FAILURE_PROBABILITY:.2%}.")
            return "HALT"
            
        # Rule 3: Risk score above the human confirmation threshold requires manual sign-off.
        if risk_score > CNCSentinel.MAX_RISK_FOR_AUTO_APPROVAL:
            logger.warning(f"SENTINEL HUMAN_CONFIRMATION ({plan_id}): Risk score {risk_score:.2f} exceeds auto-approval threshold of {CNCSentinel.MAX_RISK_FOR_AUTO_APPROVAL:.2f}.")
            # In a real system, this would flag the job in a UI for a manager to review.
            return "HUMAN_CONFIRMATION"

        # If all checks pass, the operation is allowed.
        logger.info(f"SENTINEL ALLOW ({plan_id}): All safety checks passed. Risk score {risk_score:.2f} and failure probability {failure_prob:.2%} are within acceptable limits.")
        return "ALLOW"
