from log_parser import LogParser
from agents.detective_agent import DetectiveAgent
from agents.remediation_agent import RemediationAgent
from config import Config
import os

def main():
    print("="*50)
    print("NetworkGuard - AI-Powered Threat Analyzer")
    print("="*50)

    # Make sure we have a dummy log file to parse if none exists
    log_file = "access.log"
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write('192.168.1.100 - - [10/Oct/2023:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 1234\n')
            f.write('10.0.0.5 - - [10/Oct/2023:13:56:00 -0700] "GET /login?user=admin\' OR \'1\'=\'1 HTTP/1.1" 200 456\n')

    # Initialize Config
    config = Config()
    if not config.get_gemini_api_key() or not config.get_groq_api_key():
        print("[WARNING] One or more API keys (Gemini/Groq) are missing in .env. Using mocked AI responses for those agents.")
    else:
        print("[INFO] All API Keys loaded successfully.")

    # Initialize components
    parser = LogParser(log_file)
    
    # Initialize agents
    remediation_agent = RemediationAgent()
    detective_agent = DetectiveAgent(remediation_agent=remediation_agent)
    
    # Set up Observer pattern
    # The LogParser notifies the DetectiveAgent when a suspicious payload is found
    parser.attach(detective_agent)
    
    print("\n[System] Monitoring started...")
    # Start parsing
    parser.parse_file()
    print("[System] Finished processing log file.")

if __name__ == "__main__":
    main()
