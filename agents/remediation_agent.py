import os
from agents.base_agent import BaseAgent

class RemediationAgent(BaseAgent):
    """
    Generates remediation steps and reports based on the threat analysis.
    """
    def __init__(self):
        super().__init__(name="SOCAnalyst")

    def handle_threat(self, threat_data: dict, original_data: dict):
        print(f"[{self.name}] Generating incident report and mitigation steps for IP {original_data['ip']}...")
        
        report = self.generate_remediation(threat_data, original_data)
        
        print(f"[{self.name}] Mitigation Action Generated: {report['firewall_rule']}")
        
        # Save incident report
        if not os.path.exists("reports"):
            os.makedirs("reports")
        
        report_path = f"reports/incident_{original_data['ip'].replace('.', '_')}.txt"
        with open(report_path, "w") as f:
            f.write(report['incident_report'])
        
        print(f"[{self.name}] Full report saved to {report_path}\n")

    def generate_remediation(self, threat_data: dict, original_data: dict):
        """
        Uses Gemini to generate firewall rules and a formal report.
        """
        prompt = f"""
        You are a SOC Analyst. We detected a {threat_data['classification']} attack with a risk score of {threat_data['risk_score']}/10.
        The attacker IP is {original_data['ip']}.
        
        1. Generate a Linux iptables command to block this IP.
        2. Write a short, formal incident report.
        
        Format the response with exact markers:
        ---FIREWALL RULE---
        <iptables command>
        ---REPORT---
        <formal report text>
        """
        
        try:
            if not self.config.get_api_key():
                # Mocked behavior
                rule = f"iptables -A INPUT -s {original_data['ip']} -j DROP"
                report = f"INCIDENT REPORT\nType: {threat_data['classification']}\nIP: {original_data['ip']}\nRisk: {threat_data['risk_score']}/10\nReason: {threat_data['reason']}"
                return {"firewall_rule": rule, "incident_report": report}
                
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            text = response.text
            
            rule = "iptables command not found"
            report_text = "Report not found"
            
            if "---FIREWALL RULE---" in text and "---REPORT---" in text:
                parts = text.split("---REPORT---")
                rule = parts[0].replace("---FIREWALL RULE---", "").strip()
                report_text = parts[1].strip()
                
            return {"firewall_rule": rule, "incident_report": report_text}
        except Exception as e:
            print(f"[{self.name}] Remediation generation error: {str(e)}")
            return {"firewall_rule": f"iptables -A INPUT -s {original_data['ip']} -j DROP", "incident_report": f"Error formatting report: {str(e)}"}
