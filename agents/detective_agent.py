import json
from agents.base_agent import BaseAgent

class DetectiveAgent(BaseAgent):
    """
    Analyzes the payload to detect and classify threats.
    """
    def __init__(self, remediation_agent=None):
        super().__init__(name="DetectiveAgent")
        self.remediation_agent = remediation_agent

    def update(self, data: dict):
        print(f"\n[{self.name}] Analyzing payload from IP: {data['ip']}")
        threat_data = self.analyze_threat(data)
        
        if threat_data:
            print(f"[{self.name}] Threat Detected: {threat_data['classification']} (Risk: {threat_data['risk_score']}/10)")
            # Notify remediation agent directly (or through another observer pattern, but direct is fine for this scope)
            if self.remediation_agent:
                self.remediation_agent.handle_threat(threat_data, data)
        else:
            print(f"[{self.name}] No significant threat detected.")

    def analyze_threat(self, data: dict):
        """
        Calls Gemini API to analyze the log line.
        """
        prompt = f"""
        You are an expert cybersecurity analyst. Analyze the following network request payload.
        Is it a cyber attack (e.g. SQL Injection, XSS, Path Traversal, etc.)?
        
        Payload: {data['payload']}
        Raw Line: {data['raw_line']}
        
        Respond ONLY with a JSON object in the following format:
        {{"is_threat": bool, "classification": "Attack Type", "risk_score": int from 1 to 10, "reason": "brief reason"}}
        If it is not a threat, return {{"is_threat": false}}.
        """
        
        try:
            # We would normally call the API, but to avoid billing/hanging if key is not set,
            # we'll use a mocked response if key is missing, or actual API if present.
            if not self.config.get_api_key():
                # Mocked behavior for demonstration when no key is set
                if "OR" in data['payload'] or "1=1" in data['payload']:
                    return {"is_threat": True, "classification": "SQL Injection", "risk_score": 9, "reason": "SQL syntax found"}
                return {"is_threat": False}
                
            response = self.model.generate_content(prompt)
            # Simple json parsing (assuming model follows instructions)
            text = response.text.strip().replace("```json", "").replace("```", "")
            result = json.loads(text)
            
            if result.get("is_threat"):
                return result
            return None
        except Exception as e:
            print(f"[{self.name}] Analysis error: {str(e)}")
            return None
