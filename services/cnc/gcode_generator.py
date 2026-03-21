# services/cnc/gcode_generator.py

import logging
import hashlib
from typing import Dict, Any, List

logger = logging.getLogger("agicore_cnc_coder")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("ops/logs/cnc_coder.log")
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class CNCCoderAgent:
    """
    Generates deterministic, machine-safe G-code from a validated CNC ActionPlan.
    """

    @staticmethod
    async def generate_gcode(plan: Dict[str, Any], target_machine: str = "GRBL") -> Dict[str, Any]:
        """
        Transforms a list of operations from a plan into a G-code file.

        Args:
            plan (Dict[str, Any]): The manufacturing plan from CNC-Architect.
            target_machine (str): The target machine standard (e.g., GRBL, Fanuc).

        Returns:
            Dict[str, Any]: A dictionary containing the G-code, metadata, and hash.
        """
        logger.info(f"CNC-Coder: Generating G-code for plan {plan['plan_id']} targeting {target_machine}")

        gcode_lines = [
            f"( G-code for plan: {plan['plan_id']} )",
            f"( Target: {target_machine} )",
            f"( Material: {plan['material']} )",
            "G90 G54 G17 G21",  # Absolute, Work Offset 1, XY Plane, Millimeters
            "G94",             # Feed per minute
            "S1000 M3",        # Spindle speed 1000 RPM, Spindle ON clockwise
            "G0 Z10",          # Rapid move to a safe Z height
        ]

        for op in plan.get("operations", []):
            gcode_lines.append(f"\n( Operation: {op['operation']} )")
            gcode_lines.append(f"( Tool: {op['tool_id']} )")
            # This is a highly simplified simulation of G-code generation
            if "roughing" in op["operation"]:
                gcode_lines.extend([
                    "T1",
                    "G0 X10 Y10",
                    "G1 Z-2 F150",
                    "G1 X50 Y50 F300",
                ])
            elif "finishing" in op["operation"]:
                gcode_lines.extend([
                    "T2",
                    "G0 X10 Y10",
                    "G1 Z-1 F100",
                    "G2 X20 Y20 I5 J5 F200", # Example arc
                ])
            elif "drilling" in op["operation"]:
                 gcode_lines.extend([
                    "T3",
                    "G0 X30 Y30",
                    "G81 Z-5 R2 F50", # Canned drilling cycle
                ])

        gcode_lines.extend([
            "\nG0 Z10", # Retract
            "M5",       # Spindle OFF
            "G0 X0 Y0", # Go home
            "M30",      # End of program
        ])

        gcode_content = "\n".join(gcode_lines)
        gcode_hash = hashlib.sha256(gcode_content.encode('utf-8')).hexdigest()

        output = {
            "gcode": gcode_content,
            "metadata": {
                "plan_id": plan['plan_id'],
                "tool_ids": [op['tool_id'] for op in plan.get("operations", [])],
                "target_machine": target_machine,
            },
            "hash": gcode_hash
        }

        logger.info(f"CNC-Coder: G-code generated with hash {gcode_hash}")
        
        # In a real system, this would be saved to a file, not just returned.
        with open(f"ops/gcode_output/{plan['plan_id']}.gcode", "w") as f:
            f.write(gcode_content)
            
        return output
