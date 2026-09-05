import json
import re
from agents.base_agent import BaseAgent
from log_parser import Observer

class DetectiveAgent(BaseAgent, Observer):
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
        Calls Gemini API to analyze the log line with model fallback.
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
            if not self.config.get_gemini_api_key():
                # Mocked behavior for demonstration when no key is set
                if "OR" in data['payload'] or "1=1" in data['payload'] or "etc/passwd" in data['payload']:
                    classification = "SQL Injection" if "OR" in data['payload'] else "Path Traversal"
                    return {"is_threat": True, "classification": classification, "risk_score": 9, "reason": "Suspicious payload syntax found"}
                return {"is_threat": False}

            response_text = None
            for model_name in ["gemini-3.5-flash-lite", "gemini-3.6-flash"]:
                try:
                    chat = self.gemini_client.chats.create(model=model_name)
                    response = chat.send_message(prompt)
                    if response and response.text:
                        response_text = response.text.strip()
                        break
                except Exception as model_err:
                    print(f"[{self.name}] Warning: {model_name} busy or rate-limited ({str(model_err)}), trying fallback...")

            if not response_text:
                return None

            # Extract JSON from potential markdown formatting
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            json_str = match.group(0) if match else response_text
            result = json.loads(json_str)
            
            if result.get("is_threat"):
                return result
            return None
        except Exception as e:
            print(f"[{self.name}] Analysis error: {str(e)}")
            return None
