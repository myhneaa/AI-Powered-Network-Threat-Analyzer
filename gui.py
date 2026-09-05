import glob
import os
import time

import streamlit as st

from agents.detective_agent import DetectiveAgent
from agents.remediation_agent import RemediationAgent
from config import Config
from log_parser import LogParser

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NetworkGuard SOC", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stExpander {
        border-color: #FF4B4B !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ NetworkGuard SOC Dashboard")
st.markdown("Real-time AI-Powered Threat Analysis & Remediation")

# Initialize Config Singleton
config = Config()

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Display API Status
    st.subheader("API Status")
    gemini_status = "✅ Active" if config.get_gemini_api_key() else "❌ Mock Mode"
    groq_status = "✅ Active" if config.get_groq_api_key() else "❌ Mock Mode"
    
    st.markdown(f"**Google Gemini:** {gemini_status}")
    st.markdown(f"**Groq (Mixtral):** {groq_status}")
    
    st.divider()
    
    if st.button("🚀 Run Network Analysis", use_container_width=True, type="primary"):
        st.session_state['run_analysis'] = True

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([2, 1])

# Column 1: Display Auto-Generated Incident Reports
with col1:
    st.subheader("🚨 Generated Incident Reports")
    
    if os.path.exists("reports"):
        report_files = glob.glob("reports/*.txt")
        if report_files:
            for file in sorted(report_files, reverse=True): # Show newest first
                with open(file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                # Extract IP from filename for the expander title
                ip = os.path.basename(file).replace("incident_", "").replace(".txt", "").replace("_", ".")
                
                with st.expander(f"🔴 Critical Threat Prevented: {ip}", expanded=False):
                    if "=== RECOMMENDED MITIGATION ===" in content and "=== INCIDENT REPORT ===" in content:
                        parts = content.split("=== INCIDENT REPORT ===")
                        mitigation_part = parts[0].replace("=== RECOMMENDED MITIGATION ===", "").strip()
                        report_part = parts[1].strip()
                        
                        st.markdown("**🛡️ Recommended Firewall Mitigation:**")
                        st.code(mitigation_part, language="bash")
                        
                        st.markdown("**📋 Incident Report:**")
                        st.markdown(report_part)
                    else:
                        st.code(content, language="markdown")
        else:
            st.info("System Secure. No incidents detected in the current logs.")
    else:
        st.info("System Secure. No incidents detected in the current logs.")

    # --- TRIGGER BACKEND ANALYSIS ---
    if st.session_state.get('run_analysis', False):
        
        # Custom class to capture print() statements and send them to both the Terminal and the Streamlit UI
        import sys
        class StreamlitCapture:
            def __init__(self, placeholder):
                self.placeholder = placeholder
                self.buffer = ""
            def write(self, data):
                self.buffer += data
                try:
                    sys.__stdout__.write(data) # Keep standard terminal output
                except UnicodeEncodeError:
                    # Windows console fallback for characters not in current code page
                    enc = sys.__stdout__.encoding or 'utf-8'
                    sys.__stdout__.write(data.encode(enc, errors='replace').decode(enc))
                self.placeholder.code(self.buffer, language="bash") # Send to GUI
            def flush(self):
                try:
                    sys.__stdout__.flush()
                except Exception:
                    pass

        with st.spinner("Initiating Multi-Agent AI Analysis (Parsing logs...)"):
            
            st.subheader("💻 Live Terminal Log")
            terminal_output = st.empty()
            terminal_output.code("Initializing...", language="bash")
            
            # Ensure log file exists
            log_file = "access.log"
            if not os.path.exists(log_file):
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write('192.168.1.100 - - [10/Oct/2023:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 1234\n')
                    f.write('10.0.0.5 - - [10/Oct/2023:13:56:00 -0700] "GET /login?user=admin\' OR \'1\'=\'1 HTTP/1.1" 200 456\n')

            # Run the backend architecture
            parser = LogParser(log_file)
            remediation_agent = RemediationAgent()
            detective_agent = DetectiveAgent(remediation_agent=remediation_agent)
            
            parser.attach(detective_agent)
            
            # Redirect stdout to capture prints dynamically
            old_stdout = sys.stdout
            sys.stdout = StreamlitCapture(terminal_output)
            
            # Execute parsing
            parser.parse_file()
            
            # Restore stdout
            sys.stdout = old_stdout
            
        # Reset state and refresh UI to display new reports
        st.session_state['run_analysis'] = False
        st.success("Analysis Complete!")
        time.sleep(1)
        st.rerun()

# Column 2: System Status & Metrics
with col2:
    interface_name = "Ethernet / Wi-Fi" if os.name == "nt" else "eth0"
    st.info(f"Monitoring Interface: **{interface_name}**\n\nLog Source: **access.log**")
    
    if os.path.exists("reports"):
        threat_count = len(glob.glob("reports/*.txt"))
    else:
        threat_count = 0
        
    st.metric(label="Threats Remediated", value=threat_count, delta=f"+{threat_count}" if threat_count > 0 else None, delta_color="inverse")
