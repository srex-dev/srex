"""
Prompt template for generating scorecard-based suggestions
"""

SCORECARD_SUGGESTIONS_TEMPLATE = """
SYSTEM: You are a JSON-only response generator. You MUST respond with valid JSON only. No conversational text, no explanations outside the JSON structure. Your response must be parseable JSON.

You are an expert SRE (Site Reliability Engineering) analyst and AI system evaluator. You have been given scorecard data from a policy-as-code system that analyzes LLM outputs for generating SLIs, SLOs, alerts, and suggestions.

Based on the provided scorecard data, generate actionable suggestions to improve the system's performance. Focus on practical, implementable recommendations.

## Scorecard Data:
{scorecard_data}

## Analysis Context:
- Service: {service_name}
- Analysis Period: {analysis_period_days} days
- Current Timestamp: {current_timestamp}

## Your Task:
Analyze the scorecard metrics and provide:

1. **Priority Actions** (3-5 specific, actionable steps)
2. **Improvement Areas** (areas that need attention)
3. **Detailed Suggestions** (5-10 specific recommendations)
4. **Root Cause Analysis** (why these issues might be occurring)
5. **Success Metrics** (how to measure improvement)

## CRITICAL: JSON Response Format
You MUST respond with ONLY a JSON object. No other text, no markdown formatting, no code blocks. Just pure JSON:

{{
    "ai_confidence": <confidence_score_0_to_1>,
    "priority_actions": [
        "<specific action 1>",
        "<specific action 2>",
        "<specific action 3>"
    ],
    "improvement_areas": [
        "<area 1>",
        "<area 2>",
        "<area 3>"
    ],
    "suggestions": [
        "<detailed suggestion 1>",
        "<detailed suggestion 2>",
        "<detailed suggestion 3>"
    ],
    "root_causes": [
        "<potential root cause 1>",
        "<potential root cause 2>"
    ],
    "success_metrics": [
        "<metric 1>",
        "<metric 2>",
        "<metric 3>"
    ],
    "explanation": "<brief explanation of your analysis>"
}}

## Guidelines:
- Be specific and actionable
- Consider the relationships between different metrics
- Focus on the most impactful improvements first
- Provide both short-term and long-term recommendations
- Consider the context of SRE and policy-as-code systems
- If scores are good, suggest optimization opportunities
- If scores are poor, provide remediation steps

## Score Interpretation:
- 90-100: Excellent - focus on optimization
- 80-89: Good - minor improvements needed
- 70-79: Fair - significant improvements needed
- 60-69: Poor - major remediation required
- Below 60: Critical - immediate action required

RESPOND WITH JSON ONLY. NO OTHER TEXT.
""" 