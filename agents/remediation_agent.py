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
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=== RECOMMENDED MITIGATION ===\n")
            f.write(f"{report['firewall_rule']}\n\n")
            f.write("=== INCIDENT REPORT ===\n")
            f.write(report['incident_report'])
        
        print(f"[{self.name}] Full report saved to {report_path}\n")

    def generate_remediation(self, threat_data: dict, original_data: dict):
        """
        Uses Groq (e.g. Llama-3) to generate firewall rules and a formal report.
        """
        prompt = f"""
        You are a SOC Analyst. A {threat_data['classification']} attack was detected with risk {threat_data['risk_score']}/10 from IP {original_data['ip']}.
        
        1. Generate a Linux iptables command to block this IP.
        2. Write a concise, complete incident report.
        
        Format the response with exact markers:
        ---FIREWALL RULE---
        <iptables command>
        ---REPORT---
        <report text>
        """
        
        try:
            if not self.config.get_groq_api_key():
                # Mocked behavior
                rule = f"iptables -A INPUT -s {original_data['ip']} -j DROP"
                report = f"INCIDENT REPORT\nType: {threat_data['classification']}\nIP: {original_data['ip']}\nRisk: {threat_data['risk_score']}/10\nReason: {threat_data['reason']}"
                return {"firewall_rule": rule, "incident_report": report}
                
            # Use gpt-oss-20b for higher rate limits (8000 OTPM vs 1000 OTPM) with low reasoning effort
            response = None
            try:
                response = self.groq_client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": "You are a concise SOC analyst. Output ONLY the requested markers and text. Do not add commentary."},
                        {"role": "user", "content": prompt}
                    ],
                    reasoning_effort="low",
                    max_tokens=400
                )
            except Exception as e:
                # Fallback to qwen if needed
                response = self.groq_client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    messages=[
                        {"role": "system", "content": "You are a concise SOC analyst. Output ONLY the requested markers and text."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400
                )
            text = response.choices[0].message.content or ""
            
            # Remove <think> blocks if they exist (used by deepseek/qwen reasoning models)
            import re
            text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            
            rule = f"iptables -A INPUT -s {original_data['ip']} -j DROP"
            report_text = text
            
            # Flexible marker search (tolerating optional markdown bold like **---FIREWALL RULE---**)
            rule_match = re.search(r'---FIREWALL RULE---\s*([\s\S]*?)\s*---REPORT---', text, re.IGNORECASE)
            if rule_match:
                extracted_rule = rule_match.group(1).strip()
                if extracted_rule:
                    rule = extracted_rule
                report_start = text.upper().find("---REPORT---") + len("---REPORT---")
                report_text = text[report_start:].strip()
            elif "iptables" in text.lower():
                # Extract the iptables command line if markers were omitted
                for line in text.splitlines():
                    if "iptables" in line.lower():
                        rule = line.strip("`* ")
                        break
                report_text = text.replace(rule, "").strip()
                
            return {"firewall_rule": rule, "incident_report": report_text}
        except Exception as e:
            print(f"[{self.name}] Remediation generation error: {str(e)}")
            return {"firewall_rule": f"iptables -A INPUT -s {original_data['ip']} -j DROP", "incident_report": f"Error formatting report: {str(e)}"}
