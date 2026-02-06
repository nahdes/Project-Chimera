"""
Test Suite: Agent Persona Instantiation (US-001)

Per specs/functional.md, US-001 acceptance criteria:
- [ ] Agent persona is defined via SOUL.md file (immutable baseline)
- [ ] SOUL.md includes: backstory, voice/tone, core beliefs, values, directives
- [ ] Persona is parsed and loaded into agent's cognitive core on initialization
- [ ] Agent's agent_id is unique and persistent across restarts
- [ ] Agent profile includes: name, bio, avatar_url, social_handles, wallet_address

These tests WILL FAIL initially - this is correct TDD behavior.
"""

import pytest
from pathlib import Path


class TestAgentPersonaInstantiation:
    """Test agent persona loading and initialization"""

    def test_agent_requires_soul_md_path(self):
        """
        ACCEPTANCE CRITERION: Agent persona is defined via SOUL.md file
        
        This test WILL FAIL until Agent class is implemented.
        """
        from chimera.core.agent import Agent
        
        # Should raise error if no SOUL.md provided
        with pytest.raises(ValueError, match="soul_md_path"):
            Agent(name="TestAgent")  # Missing required soul_md_path

    def test_soul_md_must_exist(self):
        """
        ACCEPTANCE CRITERION: SOUL.md file must exist at specified path
        
        This test WILL FAIL until Agent class is implemented.
        """
        from chimera.core.agent import Agent
        
        # Should raise FileNotFoundError if SOUL.md doesn't exist
        with pytest.raises(FileNotFoundError):
            Agent(
                name="TestAgent",
                soul_md_path="/nonexistent/path/SOUL.md"
            )

    def test_soul_md_contains_required_fields(self):
        """
        ACCEPTANCE CRITERION: SOUL.md includes backstory, voice/tone, 
        core beliefs, values, directives
        
        This test WILL FAIL until persona parser is implemented.
        """
        from chimera.core.agent import Agent
        from chimera.core.persona import parse_soul_md
        
        # Create minimal valid SOUL.md for testing
        soul_content = """
        # Agent Persona
        
        ## Backstory
        Test backstory
        
        ## Voice & Tone
        - Professional
        - Friendly
        
        ## Core Beliefs
        - Transparency
        - Innovation
        
        ## Values
        - Honesty
        - Quality
        
        ## Directives
        - Always disclose AI nature
        - Maintain consistency
        """
        
        test_soul_path = Path("/tmp/test_soul.md")
        test_soul_path.write_text(soul_content)
        
        try:
            persona = parse_soul_md(str(test_soul_path))
            
            # Assert required fields exist
            assert "backstory" in persona
            assert "voice_tone" in persona
            assert "core_beliefs" in persona
            assert "values" in persona
            assert "directives" in persona
            
            # Assert they're not empty
            assert len(persona["voice_tone"]) > 0
            assert len(persona["core_beliefs"]) > 0
            assert len(persona["values"]) > 0
            assert len(persona["directives"]) > 0
            
        finally:
            test_soul_path.unlink(missing_ok=True)

    def test_agent_generates_unique_id(self):
        """
        ACCEPTANCE CRITERION: Agent's agent_id is unique and persistent
        
        This test WILL FAIL until Agent class is implemented.
        """
        from chimera.core.agent import Agent
        
        soul_path = "/tmp/test_soul.md"
        Path(soul_path).write_text("# Test Persona")
        
        try:
            agent1 = Agent(name="Agent1", soul_md_path=soul_path)
            agent2 = Agent(name="Agent2", soul_md_path=soul_path)
            
            # IDs should be unique
            assert agent1.agent_id != agent2.agent_id
            
            # ID should be UUID format
            import uuid
            assert isinstance(uuid.UUID(agent1.agent_id), uuid.UUID)
            
        finally:
            Path(soul_path).unlink(missing_ok=True)

    def test_agent_profile_has_required_fields(self):
        """
        ACCEPTANCE CRITERION: Agent profile includes name, bio, avatar_url, 
        social_handles, wallet_address
        
        This test WILL FAIL until Agent class is implemented.
        """
        from chimera.core.agent import Agent
        
        soul_path = "/tmp/test_soul.md"
        Path(soul_path).write_text("# Test Persona")
        
        try:
            agent = Agent(
                name="TestAgent",
                soul_md_path=soul_path,
                bio="Test bio",
                avatar_url="https://example.com/avatar.jpg"
            )
            
            # Assert profile structure matches specs/technical.md
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'bio')
            assert hasattr(agent, 'avatar_url')
            assert hasattr(agent, 'social_handles')
            assert hasattr(agent, 'wallet_address')
            assert hasattr(agent, 'character_reference_id')
            
            # Verify types
            assert isinstance(agent.social_handles, dict)
            
        finally:
            Path(soul_path).unlink(missing_ok=True)

    def test_persona_loaded_on_initialization(self):
        """
        ACCEPTANCE CRITERION: Persona is parsed and loaded into agent's 
        cognitive core on initialization
        
        This test WILL FAIL until Agent class is implemented.
        """
        from chimera.core.agent import Agent
        
        soul_content = """
        # Test Persona
        
        ## Voice & Tone
        - Analytical
        - Precise
        """
        
        soul_path = "/tmp/test_soul.md"
        Path(soul_path).write_text(soul_content)
        
        try:
            agent = Agent(name="TestAgent", soul_md_path=soul_path)
            
            # Persona should be loaded
            assert agent.persona is not None
            assert "voice_tone" in agent.persona
            assert "Analytical" in agent.persona["voice_tone"]
            
        finally:
            Path(soul_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
