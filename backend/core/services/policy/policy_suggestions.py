import json
from typing import List, Dict, Any
from datetime import datetime
from llm.interface import call_llm
from backend.core.logger import logger
from backend.api.models_llm import LLMOutput, SessionLocal
from sqlalchemy.future import select

class PolicySuggestionsService:
    def __init__(self, model: str = "llama2", temperature: float = 0.3):
        self.model = model
        self.temperature = temperature
    
    def _get_suggestions_prompt(self, service_name: str = None, category: str = None) -> str:
        """Generate a prompt for policy suggestions."""
        prompt = """You are an expert in cloud governance and policy-as-code. Generate 5 policy suggestions for improving cloud security and compliance.

Each suggestion should include:
- category: The type of policy (security, compliance, cost, performance, etc.)
- title: A clear, descriptive title
- description: A detailed description of what the policy should enforce
- priority: high, medium, or low
- effort: high, medium, or low (implementation effort)
- impact: high, medium, or low (business impact)
- examples: 2-3 specific examples of what the policy would catch
- rationale: Why this policy is important

Focus on practical, actionable policies that can be implemented with tools like OPA, AWS Config, or similar.

Respond with a JSON array of suggestions in this format:
[
  {
    "category": "security",
    "title": "Ensure S3 buckets have encryption enabled",
    "description": "All S3 buckets must have server-side encryption enabled to protect data at rest",
    "priority": "high",
    "effort": "medium",
    "impact": "high",
    "examples": [
      "S3 bucket without encryption settings",
      "S3 bucket with encryption disabled",
      "S3 bucket missing encryption configuration"
    ],
    "rationale": "Encryption at rest is a fundamental security requirement for protecting sensitive data"
  }
]"""

        if service_name:
            prompt += f"\n\nFocus on policies related to {service_name} services."
        
        if category:
            prompt += f"\n\nFocus on {category} policies."
        
        return prompt
    
    async def generate_suggestions(
        self,
        service_name: str = None,
        category: str = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Generate policy suggestions using LLM."""
        try:
            prompt = self._get_suggestions_prompt(service_name, category)
            
            logger.info(f"Generating policy suggestions for service: {service_name}, category: {category}")
            
            # Call LLM
            llm_response = call_llm(
                prompt=prompt,
                model=self.model,
                temperature=self.temperature,
                explain=False
            )
            
            # Parse the response
            try:
                suggestions = json.loads(llm_response)
                if not isinstance(suggestions, list):
                    suggestions = [suggestions]
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e}")
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
                if json_match:
                    try:
                        suggestions = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        # If still failing, create a fallback suggestion
                        logger.warning("Could not parse JSON from LLM response, creating fallback suggestion")
                        suggestions = [{
                            "category": "general",
                            "title": "Policy Suggestion",
                            "description": "A policy suggestion based on your requirements",
                            "priority": "medium",
                            "effort": "medium",
                            "impact": "medium",
                            "examples": ["Example configuration"],
                            "rationale": "This policy helps improve security and compliance"
                        }]
                else:
                    # Create a fallback suggestion if no JSON found
                    logger.warning("No JSON found in LLM response, creating fallback suggestion")
                    suggestions = [{
                        "category": "general",
                        "title": "Policy Suggestion",
                        "description": "A policy suggestion based on your requirements",
                        "priority": "medium",
                        "effort": "medium",
                        "impact": "medium",
                        "examples": ["Example configuration"],
                        "rationale": "This policy helps improve security and compliance"
                    }]
            
            # Validate and clean suggestions
            cleaned_suggestions = []
            for suggestion in suggestions:
                if isinstance(suggestion, dict):
                    cleaned_suggestion = {
                        "category": suggestion.get("category", "general"),
                        "title": suggestion.get("title", "Untitled Policy"),
                        "description": suggestion.get("description", ""),
                        "priority": suggestion.get("priority", "medium"),
                        "effort": suggestion.get("effort", "medium"),
                        "impact": suggestion.get("impact", "medium"),
                        "examples": suggestion.get("examples", []),
                        "rationale": suggestion.get("rationale", "")
                    }
                    cleaned_suggestions.append(cleaned_suggestion)
            
            result = {
                "status": "success",
                "suggestions": cleaned_suggestions,
                "total": len(cleaned_suggestions),
                "service_name": service_name,
                "category": category,
                "model": self.model,
                "temperature": self.temperature,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Save to database if requested
            if save_to_db:
                await self._save_suggestions_to_db(result)
            
            logger.info(f"Generated {len(cleaned_suggestions)} policy suggestions")
            return result
            
        except Exception as e:
            logger.error(f"Error generating policy suggestions: {str(e)}")
            raise
    
    async def _save_suggestions_to_db(self, suggestions_data: Dict[str, Any]) -> None:
        """Save suggestions to database."""
        try:
            async with SessionLocal() as db:
                llm_output = LLMOutput(
                    task="policy_suggestions",
                    input={
                        "service_name": suggestions_data.get("service_name"),
                        "category": suggestions_data.get("category"),
                        "model": suggestions_data.get("model"),
                        "temperature": suggestions_data.get("temperature")
                    },
                    output=suggestions_data,
                    confidence=0.8
                )
                
                db.add(llm_output)
                await db.commit()
                
                logger.info(f"Policy suggestions saved to database with ID: {llm_output.id}")
                
        except Exception as e:
            logger.error(f"Error saving suggestions to database: {str(e)}")
            raise
    
    async def get_suggestions(
        self,
        service_name: str = None,
        category: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get existing suggestions from database."""
        try:
            async with SessionLocal() as db:
                query = select(LLMOutput).where(LLMOutput.task == "policy_suggestions")
                
                query = query.order_by(LLMOutput.created_at.desc()).limit(limit)
                
                result = await db.execute(query)
                outputs = result.scalars().all()
                
                all_suggestions = []
                for output in outputs:
                    try:
                        if output.output and isinstance(output.output, dict):
                            suggestions = output.output.get("suggestions", [])
                            for suggestion in suggestions:
                                suggestion["llm_output_id"] = output.id
                                suggestion["created_at"] = output.created_at.isoformat()
                                all_suggestions.append(suggestion)
                    except Exception as e:
                        logger.warning(f"Error parsing suggestion from output {output.id}: {e}")
                
                # Filter by service_name if provided
                if service_name:
                    all_suggestions = [s for s in all_suggestions if s.get("service_name") == service_name]
                
                # Filter by category if provided
                if category:
                    all_suggestions = [s for s in all_suggestions if s.get("category") == category]
                
                return all_suggestions
                
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            raise 