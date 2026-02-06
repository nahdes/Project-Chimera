# Skill: Analyze Trends

## Overview

**Skill Name:** `skill_analyze_trends`  
**Purpose:** Detect and analyze emerging trends from multiple data sources to inform content strategy  
**Version:** 1.0.0  
**Status:** Specification Complete | Implementation Pending

---

## Description

This skill enables Chimera agents to autonomously detect trending topics across news sources, social media platforms, and domain-specific feeds. It aggregates data, performs semantic clustering to identify themes, and provides actionable recommendations for content creation.

**Key Capabilities:**

- Multi-source trend detection (news APIs, Twitter, Reddit, etc.)
- Semantic clustering to group related topics
- Relevance scoring based on agent's domain/persona
- Time-series analysis to detect emerging vs declining trends
- Actionable content recommendations

---

## Input/Output Contract

### Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal

class AnalyzeTrendsInput(BaseModel):
    """Input parameters for trend analysis"""

    topic_category: str = Field(
        ...,
        description="Category to analyze (e.g., 'technology', 'fashion', 'Ethiopian culture')",
        min_length=2,
        max_length=100
    )

    timeframe_hours: int = Field(
        default=24,
        description="How far back to look for trends (1-168 hours / 1-7 days)",
        ge=1,
        le=168
    )

    min_relevance_score: float = Field(
        default=0.7,
        description="Minimum relevance score (0.0-1.0) for a topic to be included",
        ge=0.0,
        le=1.0
    )

    max_results: int = Field(
        default=10,
        description="Maximum number of trending topics to return",
        ge=1,
        le=50
    )

    sources: list[Literal["news", "twitter", "reddit", "google_trends"]] = Field(
        default=["news", "twitter"],
        description="Data sources to analyze"
    )

    agent_persona_context: str | None = Field(
        default=None,
        description="Agent's persona summary for relevance filtering"
    )
```

**Example Input:**

```json
{
  "topic_category": "artificial intelligence",
  "timeframe_hours": 48,
  "min_relevance_score": 0.75,
  "max_results": 5,
  "sources": ["news", "twitter"],
  "agent_persona_context": "Tech influencer focused on AI ethics and practical applications"
}
```

---

### Output Schema

```python
from pydantic import BaseModel
from typing import List
from datetime import datetime

class TrendingTopic(BaseModel):
    """Individual trending topic"""

    topic: str = Field(..., description="Topic name/description")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="How relevant to agent's domain")
    momentum: Literal["rising", "stable", "declining"] = Field(..., description="Trend trajectory")
    volume: int = Field(..., description="Number of mentions/articles")
    sentiment: Literal["positive", "neutral", "negative"] = Field(..., description="Overall sentiment")

    key_phrases: List[str] = Field(..., description="Representative phrases")
    source_urls: List[str] = Field(default=[], description="Example source links")
    related_topics: List[str] = Field(default=[], description="Connected topics")

    first_seen: datetime = Field(..., description="When trend first emerged")
    peak_time: datetime | None = Field(default=None, description="When trend peaked")

class ContentRecommendation(BaseModel):
    """Suggested content action"""

    action_type: Literal["create_post", "create_thread", "create_video"] = Field(...)
    topic: str = Field(..., description="What to create content about")
    angle: str = Field(..., description="Suggested content angle/perspective")
    estimated_engagement: float = Field(..., ge=0.0, le=1.0, description="Predicted engagement score")
    urgency: Literal["low", "medium", "high"] = Field(..., description="Time sensitivity")
    reasoning: str = Field(..., description="Why this recommendation was made")

class AnalyzeTrendsOutput(BaseModel):
    """Output from trend analysis"""

    success: bool = Field(..., description="Whether analysis completed successfully")
    error_message: str | None = Field(default=None, description="Error details if failed")

    trending_topics: List[TrendingTopic] = Field(default=[], description="Detected trends")

    insights: str = Field(
        default="",
        description="Natural language summary of trend analysis"
    )

    content_recommendations: List[ContentRecommendation] = Field(
        default=[],
        description="Suggested actions for content creation"
    )

    metadata: dict = Field(
        default={},
        description="Execution metadata (sources queried, processing time, etc.)"
    )
```

**Example Output:**

```json
{
  "success": true,
  "trending_topics": [
    {
      "topic": "AI Regulation in Europe",
      "relevance_score": 0.92,
      "momentum": "rising",
      "volume": 1247,
      "sentiment": "neutral",
      "key_phrases": [
        "EU AI Act",
        "algorithmic transparency",
        "regulatory framework"
      ],
      "source_urls": ["https://...", "https://..."],
      "related_topics": ["AI safety", "Tech policy"],
      "first_seen": "2026-02-04T08:00:00Z",
      "peak_time": null
    }
  ],
  "insights": "AI regulation is gaining momentum with the EU AI Act implementation. There's significant debate around enforcement mechanisms and impact on innovation.",
  "content_recommendations": [
    {
      "action_type": "create_thread",
      "topic": "EU AI Act",
      "angle": "Practical implications for AI developers and startups",
      "estimated_engagement": 0.85,
      "urgency": "high",
      "reasoning": "Breaking news with high relevance to tech audience, limited expert commentary available"
    }
  ],
  "metadata": {
    "sources_queried": ["news", "twitter"],
    "total_articles_analyzed": 3421,
    "processing_time_seconds": 42.3,
    "llm_model_used": "gemini-3-pro"
  }
}
```

---

## Execution Flow

```
1. Input Validation
   ├─> Validate topic_category (not empty, reasonable length)
   ├─> Validate timeframe (1-168 hours)
   └─> Validate relevance threshold (0.0-1.0)

2. Data Collection (MCP Resources)
   ├─> Query news://trending?category={topic_category}&hours={timeframe}
   ├─> Query twitter://search?q={topic_category}&since={start_time}
   └─> Query reddit://r/{relevant_subreddits}/hot

3. Data Aggregation & Clustering
   ├─> Combine all articles/posts into single dataset
   ├─> Extract key phrases using NLP (spaCy or NLTK)
   ├─> Cluster similar topics using sentence embeddings
   └─> Calculate cluster sizes (volume)

4. Trend Analysis
   ├─> Calculate relevance scores (semantic similarity to agent persona)
   ├─> Determine momentum (rising/stable/declining) via time-series analysis
   ├─> Perform sentiment analysis (positive/neutral/negative)
   └─> Filter by min_relevance_score

5. Generate Recommendations
   ├─> LLM analyzes top trends with agent persona context
   ├─> Generate content angles unique to agent's voice
   ├─> Estimate engagement based on historical data
   └─> Rank by urgency (time-sensitivity + opportunity)

6. Return Results
   └─> Package as AnalyzeTrendsOutput
```

---

## MCP Tools Used

### 1. mcp-server-news

```python
news_data = await mcp_client.call_tool(
    server="mcp-server-news",
    tool="query_news",
    params={
        "category": input_data.topic_category,
        "hours_back": input_data.timeframe_hours,
        "max_articles": 500
    }
)
```

### 2. mcp-server-twitter

```python
twitter_data = await mcp_client.call_tool(
    server="mcp-server-twitter",
    tool="search_tweets",
    params={
        "query": input_data.topic_category,
        "since": start_time,
        "max_results": 1000
    }
)
```

### 3. mcp-server-weaviate (for semantic search)

```python
# Check if similar trends analyzed recently
similar_analyses = await mcp_client.call_tool(
    server="mcp-server-weaviate",
    tool="semantic_search",
    params={
        "collection": "trend_analyses",
        "query": input_data.topic_category,
        "limit": 5
    }
)
```

---

## Implementation Pseudocode

```python
from skills.base import Skill, SkillInput, SkillOutput
import asyncio
from typing import List

class AnalyzeTrendsSkill(Skill):
    name = "analyze_trends"
    description = "Detect and analyze emerging trends for content strategy"

    def get_input_schema(self):
        return AnalyzeTrendsInput

    def get_output_schema(self):
        return AnalyzeTrendsOutput

    async def execute(self, input_data: AnalyzeTrendsInput) -> AnalyzeTrendsOutput:
        try:
            # Step 1: Collect data from multiple sources
            data_sources = await asyncio.gather(
                self._fetch_news_data(input_data),
                self._fetch_social_data(input_data),
                return_exceptions=True
            )

            # Step 2: Aggregate and deduplicate
            all_content = self._aggregate_content(data_sources)

            # Step 3: Cluster topics
            topic_clusters = await self._cluster_topics(all_content)

            # Step 4: Analyze each cluster
            trending_topics = []
            for cluster in topic_clusters:
                topic = await self._analyze_cluster(cluster, input_data)
                if topic.relevance_score >= input_data.min_relevance_score:
                    trending_topics.append(topic)

            # Step 5: Sort by relevance and limit
            trending_topics.sort(key=lambda t: t.relevance_score, reverse=True)
            trending_topics = trending_topics[:input_data.max_results]

            # Step 6: Generate insights and recommendations
            insights = await self._generate_insights(trending_topics, input_data)
            recommendations = await self._generate_recommendations(
                trending_topics,
                input_data.agent_persona_context
            )

            return AnalyzeTrendsOutput(
                success=True,
                trending_topics=trending_topics,
                insights=insights,
                content_recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}", exc_info=True)
            return AnalyzeTrendsOutput(
                success=False,
                error_message=str(e)
            )

    async def _fetch_news_data(self, input_data):
        """Fetch news articles from news APIs"""
        # Implementation using mcp-server-news
        pass

    async def _fetch_social_data(self, input_data):
        """Fetch social media mentions"""
        # Implementation using mcp-server-twitter
        pass

    def _aggregate_content(self, data_sources):
        """Combine and deduplicate content from multiple sources"""
        # Dedupe logic
        pass

    async def _cluster_topics(self, content):
        """Group similar content into topic clusters"""
        # Use embeddings + clustering (e.g., HDBSCAN)
        pass

    async def _analyze_cluster(self, cluster, input_data):
        """Analyze a single topic cluster"""
        # Calculate metrics: relevance, momentum, sentiment
        pass

    async def _generate_insights(self, topics, input_data):
        """Generate natural language summary"""
        # LLM call to summarize trends
        pass

    async def _generate_recommendations(self, topics, persona):
        """Generate content recommendations"""
        # LLM call with persona context
        pass
```

---

## Testing Strategy

### Unit Tests

```python
@pytest.mark.asyncio
async def test_analyze_trends_with_valid_input():
    skill = AnalyzeTrendsSkill()
    input_data = AnalyzeTrendsInput(
        topic_category="artificial intelligence",
        timeframe_hours=24
    )

    # Mock MCP responses
    skill.mcp_client = MockMCPClient()

    result = await skill.execute(input_data)

    assert result.success is True
    assert len(result.trending_topics) > 0
    assert all(t.relevance_score >= 0.7 for t in result.trending_topics)

@pytest.mark.asyncio
async def test_analyze_trends_handles_api_failure():
    skill = AnalyzeTrendsSkill()
    input_data = AnalyzeTrendsInput(topic_category="test")

    # Mock API failure
    skill.mcp_client.call_tool = AsyncMock(side_effect=TimeoutError())

    result = await skill.execute(input_data)

    assert result.success is False
    assert "timeout" in result.error_message.lower()
```

### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_trends_end_to_end():
    """Test with real MCP servers (slower)"""
    skill = AnalyzeTrendsSkill()
    input_data = AnalyzeTrendsInput(
        topic_category="Python programming",
        timeframe_hours=48,
        sources=["news"]
    )

    result = await skill.execute(input_data)

    assert result.success is True
    assert len(result.trending_topics) >= 1
    assert result.insights != ""
```

---

## Performance Characteristics

**Expected Execution Time:**

- Minimum: 20 seconds (cached data, single source)
- Typical: 40-60 seconds (multiple sources, full analysis)
- Maximum: 120 seconds (timeout threshold)

**Cost Breakdown:**

- News API calls: $0.001 per query
- Twitter API: $0.01 per 1000 tweets
- LLM inference (analysis): $0.03-0.05
- **Total per execution: ~$0.05**

**Resource Usage:**

- Memory: ~500MB (for embedding calculations)
- Network: 2-5MB download (depending on result count)

---

## Error Handling

| Error Type      | Handling Strategy                                             |
| --------------- | ------------------------------------------------------------- |
| Invalid input   | Return immediate error with validation details                |
| API timeout     | Retry up to 3x with exponential backoff, then partial results |
| Rate limit      | Respect retry-after header, queue for later execution         |
| No trends found | Return success=True with empty trending_topics list           |
| LLM failure     | Return topics without insights/recommendations                |

---

## Future Enhancements

- **Predictive Trending:** Use ML to predict topics that will trend in next 24-48 hours
- **Cross-Domain Detection:** Identify trends spanning multiple categories
- **Competitor Analysis:** Track what topics competitors are covering
- **Trend Lifecycle:** Track trends over weeks/months to understand full lifecycle

---

## Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "pydantic>=2.5.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",  # For clustering
    "sentence-transformers>=2.2.0",  # For embeddings
    "spacy>=3.7.0",  # For NLP
]
```

---

_"Trends are opportunities. Analysis is the map. Action is the journey."_
