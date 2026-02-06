"""
Test Suite: Skills Interface Contracts

Per research/tooling_strategy.md and skills/README.md, all skills must:
- Have defined input/output schemas (Pydantic models)
- Implement execute() method returning SkillOutput
- Handle errors gracefully
- Be stateless

These tests validate the interface contracts defined in:
- skills/skill_analyze_trends/README.md
- skills/skill_generate_social_post/README.md
- skills/skill_generate_character_image/README.md

These tests WILL FAIL initially - this is correct TDD behavior.
"""

import pytest
from pydantic import ValidationError


class TestSkillBaseInterface:
    """Test that all skills implement the base Skill interface"""

    def test_skill_has_name_property(self):
        """
        Per skills/README.md: Every skill must have a name property
        
        This test WILL FAIL until Skill base class is implemented.
        """
        from chimera.skills.base import Skill
        from chimera.skills.skill_analyze_trends import AnalyzeTrendsSkill
        
        skill = AnalyzeTrendsSkill()
        
        assert hasattr(skill, 'name')
        assert isinstance(skill.name, str)
        assert len(skill.name) > 0

    def test_skill_has_description_property(self):
        """
        Per skills/README.md: Every skill must have a description property
        
        This test WILL FAIL until Skill base class is implemented.
        """
        from chimera.skills.skill_analyze_trends import AnalyzeTrendsSkill
        
        skill = AnalyzeTrendsSkill()
        
        assert hasattr(skill, 'description')
        assert isinstance(skill.description, str)
        assert len(skill.description) > 0

    def test_skill_has_execute_method(self):
        """
        Per skills/README.md: Every skill must implement execute() method
        
        This test WILL FAIL until Skill base class is implemented.
        """
        from chimera.skills.skill_analyze_trends import AnalyzeTrendsSkill
        import inspect
        
        skill = AnalyzeTrendsSkill()
        
        assert hasattr(skill, 'execute')
        assert callable(skill.execute)
        
        # Should be async
        assert inspect.iscoroutinefunction(skill.execute)

    def test_skill_has_schema_methods(self):
        """
        Per skills/README.md: Skills must expose input/output schemas
        
        This test WILL FAIL until Skill base class is implemented.
        """
        from chimera.skills.skill_analyze_trends import AnalyzeTrendsSkill
        
        skill = AnalyzeTrendsSkill()
        
        assert hasattr(skill, 'get_input_schema')
        assert hasattr(skill, 'get_output_schema')
        assert callable(skill.get_input_schema)
        assert callable(skill.get_output_schema)


class TestAnalyzeTrendsSkill:
    """
    Test skill_analyze_trends interface contract
    
    Per skills/skill_analyze_trends/README.md
    """

    def test_input_schema_validation(self):
        """
        Input schema from README.md must include:
        - topic_category (str)
        - timeframe_hours (int, default 24)
        - min_relevance_score (float, default 0.7)
        - max_results (int, default 10)
        - sources (list)
        
        This test WILL FAIL until AnalyzeTrendsInput is implemented.
        """
        from chimera.skills.skill_analyze_trends.schema import AnalyzeTrendsInput
        
        # Valid input should pass
        valid_input = AnalyzeTrendsInput(
            topic_category="artificial intelligence",
            timeframe_hours=24
        )
        
        assert valid_input.topic_category == "artificial intelligence"
        assert valid_input.timeframe_hours == 24
        assert valid_input.min_relevance_score == 0.7  # default
        assert valid_input.max_results == 10  # default

    def test_input_schema_rejects_invalid_data(self):
        """
        Input validation should reject invalid data
        
        This test WILL FAIL until AnalyzeTrendsInput is implemented.
        """
        from chimera.skills.skill_analyze_trends.schema import AnalyzeTrendsInput
        
        # Empty topic_category should fail
        with pytest.raises(ValidationError):
            AnalyzeTrendsInput(topic_category="")
        
        # Invalid timeframe should fail
        with pytest.raises(ValidationError):
            AnalyzeTrendsInput(
                topic_category="test",
                timeframe_hours=0  # Must be >= 1
            )
        
        # Invalid relevance score should fail
        with pytest.raises(ValidationError):
            AnalyzeTrendsInput(
                topic_category="test",
                min_relevance_score=1.5  # Must be <= 1.0
            )

    def test_output_schema_structure(self):
        """
        Output schema from README.md must include:
        - success (bool)
        - error_message (str | None)
        - trending_topics (List[TrendingTopic])
        - insights (str)
        - content_recommendations (List[ContentRecommendation])
        
        This test WILL FAIL until AnalyzeTrendsOutput is implemented.
        """
        from chimera.skills.skill_analyze_trends.schema import (
            AnalyzeTrendsOutput,
            TrendingTopic
        )
        
        # Create minimal valid output
        output = AnalyzeTrendsOutput(
            success=True,
            trending_topics=[],
            insights="Test insights",
            content_recommendations=[]
        )
        
        assert output.success is True
        assert output.error_message is None
        assert isinstance(output.trending_topics, list)
        assert isinstance(output.insights, str)

    @pytest.mark.asyncio
    async def test_skill_execute_signature(self):
        """
        execute() method must accept AnalyzeTrendsInput and return AnalyzeTrendsOutput
        
        This test WILL FAIL until AnalyzeTrendsSkill is implemented.
        """
        from chimera.skills.skill_analyze_trends import AnalyzeTrendsSkill
        from chimera.skills.skill_analyze_trends.schema import (
            AnalyzeTrendsInput,
            AnalyzeTrendsOutput
        )
        
        skill = AnalyzeTrendsSkill()
        
        input_data = AnalyzeTrendsInput(
            topic_category="test",
            timeframe_hours=24
        )
        
        # This will fail because skill isn't implemented yet
        # But the contract should be correct
        result = await skill.execute(input_data)
        
        assert isinstance(result, AnalyzeTrendsOutput)
        assert hasattr(result, 'success')


class TestGenerateSocialPostSkill:
    """
    Test skill_generate_social_post interface contract
    
    Per skills/skill_generate_social_post/README.md
    """

    def test_input_schema_has_required_fields(self):
        """
        Per README.md, input must include:
        - topic (str)
        - platform (Literal["twitter", "instagram", "tiktok"])
        - agent_persona (dict)
        
        This test WILL FAIL until GenerateSocialPostInput is implemented.
        """
        from chimera.skills.skill_generate_social_post.schema import GenerateSocialPostInput
        
        valid_input = GenerateSocialPostInput(
            topic="AI trends",
            platform="twitter",
            agent_persona={"voice_tone": ["professional"]}
        )
        
        assert valid_input.topic == "AI trends"
        assert valid_input.platform == "twitter"
        assert isinstance(valid_input.agent_persona, dict)

    def test_platform_enum_validation(self):
        """
        Platform must be one of: twitter, instagram, tiktok
        
        This test WILL FAIL until GenerateSocialPostInput is implemented.
        """
        from chimera.skills.skill_generate_social_post.schema import GenerateSocialPostInput
        
        # Invalid platform should raise error
        with pytest.raises(ValidationError):
            GenerateSocialPostInput(
                topic="test",
                platform="facebook",  # Not in allowed list
                agent_persona={}
            )

    def test_output_includes_engagement_score(self):
        """
        Per README.md, output must include estimated_engagement_score
        
        This test WILL FAIL until GenerateSocialPostOutput is implemented.
        """
        from CONTENT.skills.skill_generate_social_post.schema import GenerateSocialPostOutput
        
        output = GenerateSocialPostOutput(
            success=True,
            text_content="Test post",
            hashtags=["#AI"],
            estimated_engagement_score=0.85
        )
        
        assert hasattr(output, 'estimated_engagement_score')
        assert 0.0 <= output.estimated_engagement_score <= 1.0


class TestGenerateCharacterImageSkill:
    """
    Test skill_generate_character_image interface contract
    
    Per skills/skill_generate_character_image/README.md
    """

    def test_input_requires_character_reference(self):
        """
        Per README.md, character_reference_id is required for consistency
        
        This test WILL FAIL until GenerateCharacterImageInput is implemented.
        """
        from chimera.skills.skill_generate_character_image.schema import (
            GenerateCharacterImageInput
        )
        
        valid_input = GenerateCharacterImageInput(
            prompt="Portrait of character in formal attire",
            character_reference_id="char_ref_123"
        )
        
        assert valid_input.character_reference_id == "char_ref_123"

    def test_output_includes_safety_check(self):
        """
        Per README.md, output must include safety_passed flag
        
        This test WILL FAIL until GenerateCharacterImageOutput is implemented.
        """
        from chimera.skills.skill_generate_character_image.schema import (
            GenerateCharacterImageOutput
        )
        
        output = GenerateCharacterImageOutput(
            success=True,
            image_url="https://example.com/image.jpg",
            safety_passed=True
        )
        
        assert hasattr(output, 'safety_passed')
        assert isinstance(output.safety_passed, bool)


class TestSkillErrorHandling:
    """Test that skills handle errors gracefully"""

    @pytest.mark.asyncio
    async def test_skill_returns_error_output_on_failure(self):
        """
        Per skills/README.md: Skills must return SkillOutput with success=False
        on errors, not raise exceptions
        
        This test WILL FAIL until skills are implemented with error handling.
        """
        from chimera.skills.skill_analyze_trends import AnalyzeTrendsSkill
        from chimera.skills.skill_analyze_trends.schema import AnalyzeTrendsInput
        
        skill = AnalyzeTrendsSkill()
        
        # Provide input that will cause failure (e.g., empty topic)
        input_data = AnalyzeTrendsInput(
            topic_category="",  # Invalid
            timeframe_hours=24
        )
        
        # Should return error output, not raise exception
        result = await skill.execute(input_data)
        
        assert result.success is False
        assert result.error_message is not None
        assert len(result.error_message) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
