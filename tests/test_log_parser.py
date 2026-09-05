
import pytest

from log_parser import LogParser, Observer


# --- Mock Observer for Testing ---
class MockAgent(Observer):
    def __init__(self):
        self.notified_data = None
        self.notification_count = 0

    def update(self, data: dict):
        self.notified_data = data
        self.notification_count += 1

# --- Fixtures ---
@pytest.fixture
def parser(tmp_path):
    log_path = tmp_path / "test.log"
    # Create empty file
    log_path.write_text("")
    return LogParser(str(log_path))

# --- Tests ---
def test_extract_ip_and_payload_malicious(parser):
    line = '192.168.1.100 - - [10/Oct/2023:13:55:36 -0700] "GET /login?user=admin\' OR \'1\'=\'1 HTTP/1.1" 200 2326'
    data = parser.extract_ip_and_payload(line)
    
    assert data is not None
    assert data["ip"] == "192.168.1.100"
    assert "OR '1'='1" in data["payload"]

def test_extract_ip_and_payload_normal(parser):
    line = '10.0.0.5 - - [10/Oct/2023:13:56:00 -0700] "GET /index.html HTTP/1.1" 200 1024'
    data = parser.extract_ip_and_payload(line)
    
    assert data is not None
    assert data["ip"] == "10.0.0.5"
    assert data["payload"] == "/index.html"

def test_observer_pattern_notification(tmp_path):
    # Create a log file with one malicious line and one normal line
    log_path = tmp_path / "test_traffic.log"
    log_path.write_text(
        '10.0.0.1 - - [10/Oct:13:00] "GET /normal HTTP/1.1" 200 100\n'
        '192.168.1.5 - - [10/Oct:13:01] "GET /file?name=../../../etc/passwd HTTP/1.1" 200 100\n'
    )
    
    parser = LogParser(str(log_path))
    mock_agent = MockAgent()
    parser.attach(mock_agent)
    
    # Run the parser
    parser.parse_file()
    
    # Assert the agent was notified EXACTLY once (only for the malicious line)
    assert mock_agent.notification_count == 1
    assert mock_agent.notified_data["ip"] == "192.168.1.5"
    assert "../../../etc/passwd" in mock_agent.notified_data["payload"]

def test_parse_empty_file_does_not_crash(tmp_path):
    empty_log = tmp_path / "empty.log"
    empty_log.write_text("")
    
    parser = LogParser(str(empty_log))
    mock_agent = MockAgent()
    parser.attach(mock_agent)
    
    parser.parse_file() 
    
    assert mock_agent.notification_count == 0
