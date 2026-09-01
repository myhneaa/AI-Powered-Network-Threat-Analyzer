import streamlit as st
import os
import glob
import time
from log_parser import LogParser
from agents.detective_agent import DetectiveAgent
from agents.remediation_agent import RemediationAgent
from config import Config

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NetworkGuard SOC", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR HACKER AESTHETIC ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
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
            for file in reversed(sorted(report_files)): # Show newest first
                with open(file, "r") as f:
                    content = f.read()
                
                # Extract IP from filename for the expander title
                ip = os.path.basename(file).replace("incident_", "").replace(".txt", "").replace("_", ".")
                
                with st.expander(f"🔴 Critical Threat Prevented: {ip}", expanded=False):
                    st.code(content, language="markdown")
        else:
            st.info("System Secure. No incidents detected in the current logs.")
    else:
        st.info("System Secure. No incidents detected in the current logs.")

# Column 2: System Status & Metrics
with col2:
    st.subheader("📡 System Status")
    st.info("Monitoring Interface: **eth0**\n\nLog Source: **access.log**")
    
    if os.path.exists("reports"):
        threat_count = len(glob.glob("reports/*.txt"))
    else:
        threat_count = 0
        
    st.metric(label="Threats Remediated", value=threat_count, delta=f"+{threat_count}" if threat_count > 0 else None, delta_color="inverse")

# --- TRIGGER BACKEND ANALYSIS ---
if st.session_state.get('run_analysis', False):
    with st.spinner("Initiating Multi-Agent AI Analysis (Parsing logs...)"):
        
        # Ensure log file exists
        log_file = "access.log"
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                f.write('192.168.1.100 - - [10/Oct/2023:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 1234\n')
                f.write('10.0.0.5 - - [10/Oct/2023:13:56:00 -0700] "GET /login?user=admin\' OR \'1\'=\'1 HTTP/1.1" 200 456\n')

        # Run the backend architecture
        parser = LogParser(log_file)
        remediation_agent = RemediationAgent()
        detective_agent = DetectiveAgent(remediation_agent=remediation_agent)
        
        parser.attach(detective_agent)
        
        # Execute parsing
        parser.parse_file()
        
    # Reset state and refresh UI to display new reports
    st.session_state['run_analysis'] = False
    st.success("Analysis Complete!")
    time.sleep(1)
    st.rerun()
