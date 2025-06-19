import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Template
from llm.interface import call_llm
from backend.core.logger import logger
from backend.api.models_policy import Policy, SessionLocal
from sqlalchemy.future import select

class PolicyGenerator:
    def __init__(self, model: str = "llama2", temperature: float = 0.3):
        self.model = model
        self.temperature = temperature
        self.template_dir = Path("llm/prompt_templates")
    
    def _load_policy_template(self, policy_type: str) -> str:
        """Load the policy generation template."""
        template_path = self.template_dir / "policy_generation.j2"
        if not template_path.exists():
            raise FileNotFoundError(f"Policy template not found: {template_path}")
        
        return template_path.read_text()
    
    def _render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Render the policy template with context."""
        template = Template(template_content)
        return template.render(**context)
    
    def _extract_policy_content(self, llm_response: str) -> str:
        """Extract policy content from LLM response."""
        # Remove any markdown code blocks
        if "```" in llm_response:
            lines = llm_response.split("\n")
            in_code_block = False
            content_lines = []
            
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    content_lines.append(line)
            
            return "\n".join(content_lines).strip()
        
        return llm_response.strip()
    
    async def generate_policy(
        self,
        description: str,
        policy_type: str = "rego",
        name: Optional[str] = None,
        additional_context: Optional[str] = None,
        examples: Optional[str] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a policy from description.
        
        Args:
            description: Plain English policy description
            policy_type: Type of policy (rego, yaml, json)
            name: Optional name for the policy
            additional_context: Additional context for generation
            examples: Example policies to reference
            save_to_db: Whether to save the policy to database
        
        Returns:
            Dict with policy generation results
        """
        try:
            # Load and render template
            template_content = self._load_policy_template(policy_type)
            
            context = {
                "description": description,
                "policy_type": policy_type,
                "package_name": "main",
                "soc2_compliance": "A.14.2.2",
                "iso27001_compliance": "ISO27001_A.14.2.2",
                "additional_context": additional_context,
                "examples": examples
            }
            
            prompt = self._render_template(template_content, context)
            
            logger.info(f"Generating {policy_type} policy from description: {description}")
            
            # Call LLM
            llm_response = call_llm(
                prompt=prompt,
                model=self.model,
                temperature=self.temperature,
                explain=False
            )
            
            # Extract policy content
            policy_content = self._extract_policy_content(llm_response)
            
            if not policy_content:
                raise ValueError("Generated policy content is empty")
            
            # Generate filename and save to file
            timestamp = int(time.time())
            filename = f"generated_{policy_type}_{timestamp}.{policy_type}"
            output_path = Path("output") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(policy_content)
            
            # Generate policy name if not provided
            if not name:
                name = f"Policy_{policy_type}_{timestamp}"
            
            # Prepare result
            result = {
                "status": "success",
                "policy_path": str(output_path),
                "policy_content": policy_content,
                "name": name,
                "description": description,
                "policy_type": policy_type,
                "model": self.model,
                "temperature": self.temperature,
                "meta": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "file_size": len(policy_content),
                    "template_used": "policy_generation.j2"
                }
            }
            
            # Save to database if requested
            if save_to_db:
                await self._save_policy_to_db(result)
            
            logger.info(f"Policy generated successfully: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating policy: {str(e)}")
            raise
    
    async def _save_policy_to_db(self, policy_data: Dict[str, Any]) -> None:
        """Save policy to database."""
        try:
            async with SessionLocal() as db:
                policy = Policy(
                    name=policy_data["name"],
                    description=policy_data["description"],
                    policy_type=policy_data["policy_type"],
                    content=policy_data["policy_content"],
                    file_path=policy_data["policy_path"],
                    model=policy_data["model"],
                    temperature=policy_data["temperature"],
                    meta=policy_data["meta"]
                )
                
                db.add(policy)
                await db.commit()
                
                logger.info(f"Policy saved to database with ID: {policy.id}")
                
        except Exception as e:
            logger.error(f"Error saving policy to database: {str(e)}")
            raise
    
    async def list_policies(
        self,
        skip: int = 0,
        limit: int = 50,
        policy_type: Optional[str] = None,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """List policies from database."""
        try:
            async with SessionLocal() as db:
                query = select(Policy)
                
                if policy_type:
                    query = query.where(Policy.policy_type == policy_type)
                
                if active_only:
                    query = query.where(Policy.is_active == True)
                
                query = query.order_by(Policy.created_at.desc()).offset(skip).limit(limit)
                
                result = await db.execute(query)
                policies = result.scalars().all()
                
                return {
                    "policies": [policy.to_dict() for policy in policies],
                    "total": len(policies),
                    "skip": skip,
                    "limit": limit
                }
                
        except Exception as e:
            logger.error(f"Error listing policies: {str(e)}")
            raise
    
    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific policy by ID."""
        try:
            async with SessionLocal() as db:
                query = select(Policy).where(Policy.id == policy_id)
                result = await db.execute(query)
                policy = result.scalar_one_or_none()
                
                return policy.to_dict() if policy else None
                
        except Exception as e:
            logger.error(f"Error getting policy: {str(e)}")
            raise
    
    async def delete_policy(self, policy_id: str) -> bool:
        """Delete a policy (soft delete by setting is_active to False)."""
        try:
            async with SessionLocal() as db:
                query = select(Policy).where(Policy.id == policy_id)
                result = await db.execute(query)
                policy = result.scalar_one_or_none()
                
                if not policy:
                    return False
                
                policy.is_active = False
                await db.commit()
                
                logger.info(f"Policy {policy_id} marked as inactive")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting policy: {str(e)}")
            raise 