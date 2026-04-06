import unittest
from optimizer.prompts.sre_master import SRE_ORCHESTRATOR, PROMPTS

class TestSREPrompts(unittest.TestCase):
    def test_sre_orchestrator_formatting(self):
        """Test that the SRE Orchestrator prompt can be correctly formatted with logs."""
        mock_logs = "ERROR: connection timeout at 10:45 UTC\nWARNING: High memory usage in service 'agicore-mcp'"
        
        # Method 1: Direct constant access
        formatted_prompt = SRE_ORCHESTRATOR.format(logs_systeme=mock_logs)
        
        self.assertIn("Tu es AGIcore SRE Orchestrator.", formatted_prompt)
        self.assertIn(mock_logs, formatted_prompt)
        print("\n--- Formatted SRE Orchestrator Prompt ---")
        print(formatted_prompt)

    def test_prompt_dictionary_access(self):
        """Test that prompts can be accessed dynamically via the PROMPTS dictionary."""
        prompt_key = "cost_optimizer"
        self.assertIn(prompt_key, PROMPTS)
        
        mock_metrics = "CPU: 85%, RAM: 4GB, Monthly Cost: $150"
        formatted_prompt = PROMPTS[prompt_key].format(usage_metrics=mock_metrics)
        
        self.assertIn("expert FinOps", formatted_prompt)
        self.assertIn(mock_metrics, formatted_prompt)
        print(f"\n--- Formatted {prompt_key.upper()} Prompt ---")
        print(formatted_prompt)

if __name__ == "__main__":
    unittest.main()
