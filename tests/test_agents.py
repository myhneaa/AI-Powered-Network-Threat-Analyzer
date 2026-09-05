from agents.detective_agent import DetectiveAgent
from agents.remediation_agent import RemediationAgent
from config import Config


def test_agent_initialization():
    """
    Test that agents can be instantiated and have the correct names and shared configs.
    """
    # Reset config singleton
    Config._instance = None
    
    remediation_agent = RemediationAgent()
    detective_agent = DetectiveAgent(remediation_agent=remediation_agent)
    
    assert remediation_agent.name == "SOCAnalyst"
    # Both agents should share the exact same config instance (Singleton pattern)
    assert remediation_agent.config is detective_agent.config

def test_remediation_agent_mock_behavior():
    """
    Test the fallback mock behavior when API keys are missing.
    """
    Config._instance = None
    agent = RemediationAgent()
    
    # Ensure it doesn't crash without keys
    threat_data = {"classification": "SQL Injection", "risk_score": 9, "reason": "Test"}
    original_data = {"ip": "1.2.3.4"}
    
    # Force mock mode by pretending there's no API key
    agent.config.get_groq_api_key = lambda: None
    
    result = agent.generate_remediation(threat_data, original_data)
    
    assert "iptables -A INPUT -s 1.2.3.4 -j DROP" in result["firewall_rule"]
    assert "SQL Injection" in result["incident_report"]
