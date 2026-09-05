import datetime
import random


def generate_logs(filename="access.log", num_lines=500):
    # Normal endpoints and user agents
    endpoints = ["/index.html", "/about", "/contact", "/images/logo.png", "/css/style.css", "/api/v1/status"]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)"
    ]
    
    # The cyber attacks we want to hide in the logs
    malicious_payloads = [
        # SQL Injection
        {"ip": "185.15.22.4", "payload": "/login?user=admin' OR '1'='1'--"},
        # Cross-Site Scripting (XSS)
        {"ip": "104.22.14.9", "payload": "/search?q=<script>alert('XSS')</script>"},
        # Directory Traversal (LFI)
        {"ip": "92.11.45.2", "payload": "/download?file=../../../../etc/passwd"}
    ]

    logs = []
    base_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)

    print(f"Generating {num_lines} lines of normal traffic...")
    
    # Generate normal traffic
    for i in range(num_lines):
        ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        endpoint = random.choice(endpoints)
        agent = random.choice(user_agents)
        time_str = (base_time + datetime.timedelta(minutes=i)).strftime("%d/%b/%Y:%H:%M:%S +0000")
        
        log_line = f'{ip} - - [{time_str}] "GET {endpoint} HTTP/1.1" 200 {random.randint(200, 5000)} "-" "{agent}"\n'
        logs.append(log_line)

    print("Injecting cyber attacks into the traffic...")
    
    # Inject the malicious payloads at random positions
    for attack in malicious_payloads:
        time_str = (base_time + datetime.timedelta(minutes=random.randint(1, num_lines))).strftime("%d/%b/%Y:%H:%M:%S +0000")
        malicious_line = f'{attack["ip"]} - - [{time_str}] "GET {attack["payload"]} HTTP/1.1" 200 1024 "-" "curl/7.68.0"\n'
        
        # Insert at a random position
        insert_idx = random.randint(0, len(logs) - 1)
        logs.insert(insert_idx, malicious_line)

    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(logs)
        
    print(f"\nSuccess! '{filename}' has been generated.")
    print("Hidden Attacks to look out for:")
    for attack in malicious_payloads:
        print(f"- IP: {attack['ip']} | Type: {attack['payload']}")

if __name__ == "__main__":
    generate_logs()
