import re
import time
from typing import List, Dict, Any

class Observer:
    """
    Observer interface for receiving updates from the Subject.
    """
    def update(self, data: Dict[str, Any]):
        pass

class Subject:
    """
    Subject interface for managing Observers.
    """
    def attach(self, observer: Observer):
        pass

    def detach(self, observer: Observer):
        pass

    def notify(self, data: Dict[str, Any]):
        pass

class LogParser(Subject):
    """
    Reads network logs and notifies observers when a potentially malicious
    payload is found. Implements the Subject role in the Observer pattern.
    """
    def __init__(self, filepath: str):
        self._observers: List[Observer] = []
        self.filepath = filepath

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, data: Dict[str, Any]):
        for observer in self._observers:
            observer.update(data)

    def extract_ip_and_payload(self, line: str) -> Dict[str, str]:
        """
        Simple extraction logic for Apache-like logs.
        Example format: 192.168.1.100 - - [10/Oct/2023:13:55:36 -0700] "GET /login?user=admin' OR '1'='1 HTTP/1.1" 200 2326
        """
        # Very basic regex to grab IP and the request string
        ip_match = re.search(r'^(\d{1,3}\.){3}\d{1,3}', line)
        request_match = re.search(r'"(GET|POST|PUT|DELETE)\s(.*?)\sHTTP', line)

        ip = ip_match.group(0) if ip_match else "Unknown IP"
        payload = request_match.group(2) if request_match else ""
        
        return {"ip": ip, "payload": payload, "raw_line": line}

    def is_suspicious(self, payload: str) -> bool:
        """
        Acts as a fast heuristic pre-filter.
        Checks for common cyber attack signatures before sending to the AI.
        """
        payload_upper = payload.upper()
        
        # 1. SQL Injection Signatures
        sqli_patterns = ["'", '"', "UNION", "SELECT", "INSERT", "OR 1=1", "OR '1'='1"]
        if any(pattern in payload_upper for pattern in sqli_patterns):
            return True
            
        # 2. Path Traversal Signatures
        traversal_patterns = ["../", "..\\", "/ETC/PASSWD", "SYSTEM.INI", "%2E%2E%2F"]
        if any(pattern in payload_upper for pattern in traversal_patterns):
            return True
            
        # 3. Cross-Site Scripting (XSS) Signatures
        xss_patterns = ["<SCRIPT>", "JAVASCRIPT:", "ONERROR=", "ONLOAD=", "%3CSCRIPT%3E"]
        if any(pattern in payload_upper for pattern in xss_patterns):
            return True
            
        # 4. Command Injection Signatures
        cmd_patterns = [";", "|", "&&", "$(", "`"]
        # Basic check to avoid flagging normal URLs with query params too aggressively, 
        # but in a security context, we flag and let AI decide.
        if any(pattern in payload_upper for pattern in cmd_patterns):
            return True
            
        return False

    def parse_file(self):
        """
        Reads the file line by line and triggers the analysis.
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    # Skip empty lines
                    if not line.strip():
                        continue
                        
                    data = self.extract_ip_and_payload(line)
                    
                    # Pre-filter: Only notify the heavy AI agents if the heuristic engine flags it
                    if self.is_suspicious(data["payload"]):
                        print(f"[LogParser] Heuristic signature matched from IP {data['ip']}. Forwarding to AI for deep analysis...")
                        self.notify(data)
                        
                    time.sleep(0.5) # Simulate real-time log reading
        except FileNotFoundError:
            print(f"[Error] File not found: {self.filepath}")
            raise
