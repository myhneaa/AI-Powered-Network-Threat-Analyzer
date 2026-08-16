import pytest
import os
from log_parser import LogParser

@pytest.fixture
def dummy_log_file(tmp_path):
    log_path = tmp_path / "test.log"
    content = '192.168.1.100 - - [10/Oct/2023:13:55:36 -0700] "GET /login?user=admin\' OR \'1\'=\'1 HTTP/1.1" 200 2326'
    log_path.write_text(content)
    return str(log_path)

def test_extract_ip_and_payload(dummy_log_file):
    parser = LogParser(dummy_log_file)
    with open(dummy_log_file, 'r') as f:
        line = f.readline()
        
    data = parser.extract_ip_and_payload(line)
    
    assert data["ip"] == "192.168.1.100"
    assert "OR '1'='1" in data["payload"]

# Bug Injection: Test fails if reading empty file?
def test_parse_empty_file(tmp_path):
    empty_log = tmp_path / "empty.log"
    empty_log.write_text("")
    
    parser = LogParser(str(empty_log))
    # It should not crash, it should just do nothing
    parser.parse_file() 
