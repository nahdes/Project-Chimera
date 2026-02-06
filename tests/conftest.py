import os
import sys

# Ensure the src/ directory is on sys.path so imports like `import chimera` work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
# Ensure '/tmp' exists on Windows so tests that write to /tmp succeed
try:
    tmp_root = os.path.join(os.path.abspath(os.sep), "tmp")
    os.makedirs(tmp_root, exist_ok=True)
except Exception:
    pass
"""
Pytest Configuration and Fixtures for Project Chimera

This file contains shared fixtures and configuration for all tests.
"""

import pytest
from pathlib import Path
import tempfile
import os


@pytest.fixture
def temp_soul_md():
    """
    Create a temporary SOUL.md file for testing
    
    Returns path to temporary file that is automatically cleaned up
    """
    content = """
# Test Agent Persona

## Backstory
This is a test agent created for unit testing purposes.

## Voice & Tone
- Professional
- Technical
- Clear

## Core Beliefs
- Transparency in AI
- User privacy matters
- Quality over quantity

## Values
- Honesty
- Reliability
- Innovation

## Directives
- Always identify as AI
- Maintain consistency
- Follow ethical guidelines
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_agent_profile():
    """
    Provide sample agent profile data matching specs/technical.md schema
    """
    return {
        "agent_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "TestAgent",
        "bio": "A test agent for unit testing",
        "persona": {
            "soul_md_path": "/path/to/SOUL.md",
            "voice_tone": ["professional", "technical"],
            "core_values": ["transparency", "innovation"],
            "directives": ["disclose AI nature", "maintain consistency"]
        },
        "social_handles": {
            "twitter": "@testagent",
            "instagram": "testagent"
        },
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "character_reference_id": "char_ref_test_001",
        "status": "active"
    }


@pytest.fixture
def sample_task_object():
    """
    Provide sample task object matching specs/technical.md schema
    """
    return {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "agent_id": "650e8400-e29b-41d4-a716-446655440000",
        "type": "generate_post",
        "priority": 5,
        "status": "pending",
        "input_data": {
            "topic": "AI regulation updates",
            "platform": "twitter",
            "max_length": 280
        },
        "dependencies": [],
        "retry_count": 0,
        "max_retries": 3,
        "trace_id": "trace_test_001"
    }


@pytest.fixture
def mock_mcp_client(monkeypatch):
    """
    Mock MCP client for testing without external dependencies
    """
    class MockMCPClient:
        async def call_tool(self, server, tool, params):
            """Mock tool call - returns dummy data"""
            return {"status": "success", "data": "mock_response"}
        
        async def read_resource(self, server, resource):
            """Mock resource read - returns dummy data"""
            return {"status": "success", "data": []}
    
    return MockMCPClient()


@pytest.fixture(scope="session")
def test_db_url():
    """
    Provide test database URL (separate from production)
    """
    return "postgresql+asyncpg://chimera:password@localhost:5432/chimera_test"


# Pytest configuration
def pytest_configure(config):
    """
    Custom pytest configuration
    """
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "benchmark: Performance benchmarks")


def pytest_collection_modifyitems(config, items):
    """
    Automatically mark tests based on their location
    """
    for item in items:
        # Mark tests by directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
