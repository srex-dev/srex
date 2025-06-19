from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from .models_llm import SessionLocal, LLMOutput

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/scorecard/overview")
async def get_scorecard_overview(
    service_name: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get overall scorecard overview"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = select(LLMOutput).where(
        LLMOutput.created_at >= start_date,
        LLMOutput.created_at <= end_date
    )
    
    if service_name:
        query = query.where(text("input::text LIKE :service_pattern"))
        query = query.params(service_pattern=f'%"service_name": "{service_name}"%')
    
    result = await db.execute(query)
    outputs = result.scalars().all()
    
    if not outputs:
        raise HTTPException(status_code=404, detail="No data found for scorecard analysis")
    
    scorecard_data = calculate_scorecard_metrics(outputs)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "total_analyses": len(outputs),
        "scorecard": scorecard_data
    }

@router.get("/scorecard/outputs-only")
async def get_outputs_only_scorecard(
    service_name: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get scorecard based only on SLI/SLO/alert/suggestion outputs (no AI confidence)"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = select(LLMOutput).where(
        LLMOutput.created_at >= start_date,
        LLMOutput.created_at <= end_date
    )
    
    if service_name:
        query = query.where(text("input::text LIKE :service_pattern"))
        query = query.params(service_pattern=f'%"service_name": "{service_name}"%')
    
    result = await db.execute(query)
    outputs = result.scalars().all()
    
    if not outputs:
        raise HTTPException(status_code=404, detail="No data found for scorecard analysis")
    
    # Calculate metrics (reuse existing functions)
    completeness_data = calculate_completeness_metrics(outputs)
    quality_data = calculate_quality_metrics(outputs)
    consistency_data = calculate_consistency_metrics(outputs)
    coverage_data = calculate_coverage_metrics(outputs)
    
    # Only use these four metrics
    weights = {
        "completeness": 0.3,
        "quality": 0.3,
        "consistency": 0.2,
        "coverage": 0.2
    }
    overall_score = (
        completeness_data["score"] * weights["completeness"] +
        quality_data["score"] * weights["quality"] +
        consistency_data["score"] * weights["consistency"] +
        coverage_data["score"] * weights["coverage"]
    )
    
    # Add grade
    if overall_score >= 90:
        grade = "A"
        grade_description = "Excellent"
    elif overall_score >= 80:
        grade = "B"
        grade_description = "Good"
    elif overall_score >= 70:
        grade = "C"
        grade_description = "Fair"
    elif overall_score >= 60:
        grade = "D"
        grade_description = "Poor"
    else:
        grade = "F"
        grade_description = "Failing"
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "total_analyses": len(outputs),
        "scorecard": {
            "completeness_score": completeness_data["score"],
            "quality_score": quality_data["score"],
            "consistency_score": consistency_data["score"],
            "coverage_score": coverage_data["score"],
            "overall_score": overall_score,
            "grade": grade,
            "grade_description": grade_description,
            "breakdown": {
                "completeness": completeness_data,
                "quality": quality_data,
                "consistency": consistency_data,
                "coverage": coverage_data
            }
        }
    }

def calculate_scorecard_metrics(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Calculate overall scorecard metrics"""
    
    total_analyses = len(outputs)
    if total_analyses == 0:
        return {"error": "No analyses found"}
    
    # Initialize metrics
    metrics = {
        "completeness_score": 0,
        "quality_score": 0,
        "consistency_score": 0,
        "coverage_score": 0,
        "confidence_score": 0,
        "overall_score": 0,
        "breakdown": {
            "completeness": {"score": 0, "details": {}},
            "quality": {"score": 0, "details": {}},
            "consistency": {"score": 0, "details": {}},
            "coverage": {"score": 0, "details": {}},
            "confidence": {"score": 0, "details": {}}
        }
    }
    
    # Calculate completeness
    completeness_data = calculate_completeness_metrics(outputs)
    metrics["completeness_score"] = completeness_data["score"]
    metrics["breakdown"]["completeness"] = completeness_data
    
    # Calculate quality
    quality_data = calculate_quality_metrics(outputs)
    metrics["quality_score"] = quality_data["score"]
    metrics["breakdown"]["quality"] = quality_data
    
    # Calculate consistency
    consistency_data = calculate_consistency_metrics(outputs)
    metrics["consistency_score"] = consistency_data["score"]
    metrics["breakdown"]["consistency"] = consistency_data
    
    # Calculate coverage
    coverage_data = calculate_coverage_metrics(outputs)
    metrics["coverage_score"] = coverage_data["score"]
    metrics["breakdown"]["coverage"] = coverage_data
    
    # Calculate confidence
    confidence_data = calculate_confidence_metrics(outputs)
    metrics["confidence_score"] = confidence_data["score"]
    metrics["breakdown"]["confidence"] = confidence_data
    
    # Calculate overall score (weighted average)
    weights = {
        "completeness": 0.25,
        "quality": 0.25,
        "consistency": 0.20,
        "coverage": 0.20,
        "confidence": 0.10
    }
    
    metrics["overall_score"] = (
        metrics["completeness_score"] * weights["completeness"] +
        metrics["quality_score"] * weights["quality"] +
        metrics["consistency_score"] * weights["consistency"] +
        metrics["coverage_score"] * weights["coverage"] +
        metrics["confidence_score"] * weights["confidence"]
    )
    
    # Add grade
    if metrics["overall_score"] >= 90:
        metrics["grade"] = "A"
        metrics["grade_description"] = "Excellent"
    elif metrics["overall_score"] >= 80:
        metrics["grade"] = "B"
        metrics["grade_description"] = "Good"
    elif metrics["overall_score"] >= 70:
        metrics["grade"] = "C"
        metrics["grade_description"] = "Fair"
    elif metrics["overall_score"] >= 60:
        metrics["grade"] = "D"
        metrics["grade_description"] = "Poor"
    else:
        metrics["grade"] = "F"
        metrics["grade_description"] = "Failing"
    
    return metrics

def calculate_completeness_metrics(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Calculate completeness score"""
    
    total_analyses = len(outputs)
    complete_outputs = 0
    field_completeness = {
        "sli": 0,
        "slo": 0,
        "alerts": 0,
        "llm_suggestions": 0,
        "explanation": 0
    }
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        
        # Check each field
        has_sli = bool(output_data.get("sli"))
        has_slo = bool(output_data.get("slo"))
        has_alerts = bool(output_data.get("alerts"))
        has_suggestions = bool(output_data.get("llm_suggestions"))
        has_explanation = bool(output_data.get("explanation"))
        
        if has_sli: field_completeness["sli"] += 1
        if has_slo: field_completeness["slo"] += 1
        if has_alerts: field_completeness["alerts"] += 1
        if has_suggestions: field_completeness["llm_suggestions"] += 1
        if has_explanation: field_completeness["explanation"] += 1
        
        # Check if all required fields are present
        if has_sli and has_slo and has_alerts and has_suggestions:
            complete_outputs += 1
    
    # Calculate percentages
    field_percentages = {
        field: (count / total_analyses * 100) if total_analyses > 0 else 0
        for field, count in field_completeness.items()
    }
    
    overall_completeness = (complete_outputs / total_analyses * 100) if total_analyses > 0 else 0
    
    return {
        "score": overall_completeness,
        "details": {
            "complete_outputs": complete_outputs,
            "total_analyses": total_analyses,
            "field_completeness": field_percentages,
            "required_fields": ["sli", "slo", "alerts", "llm_suggestions"]
        }
    }

def calculate_quality_metrics(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Calculate quality score"""
    
    total_analyses = len(outputs)
    quality_scores = []
    validation_present = 0
    detailed_quality = {
        "validation": 0,
        "structure": 0,
        "content": 0
    }
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        
        # Check validation - look for various validation indicators
        has_validation = (
            "validation_summary" in output_data or
            "validation" in output_data or
            "validation_status" in output_data or
            "validation_result" in output_data or
            "validation_errors" in output_data or
            "validation_warnings" in output_data or
            "validation_passed" in output_data or
            "validation_failed" in output_data
        )
        if has_validation:
            validation_present += 1
            detailed_quality["validation"] += 1
        
        # Check structure quality - ensure all required fields are arrays
        has_proper_structure = all(
            isinstance(output_data.get(field), list) 
            for field in ["sli", "slo", "alerts", "llm_suggestions"]
        )
        if has_proper_structure:
            detailed_quality["structure"] += 1
        
        # Check content quality - ensure arrays have content
        has_content = all(
            len(output_data.get(field, [])) > 0
            for field in ["sli", "slo", "alerts", "llm_suggestions"]
        )
        if has_content:
            detailed_quality["content"] += 1
        
        # Calculate individual quality score
        # Since validation is not currently implemented, adjust weights
        quality_score = 0
        if has_validation: 
            quality_score += 40
        else:
            # If no validation, give bonus points for good structure and content
            if has_proper_structure and has_content:
                quality_score += 20  # Bonus for both structure and content
        
        if has_proper_structure: quality_score += 40  # Increased weight
        if has_content: quality_score += 40  # Increased weight
        
        quality_scores.append(quality_score)
    
    # Calculate percentages
    quality_percentages = {
        field: (count / total_analyses * 100) if total_analyses > 0 else 0
        for field, count in detailed_quality.items()
    }
    
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    return {
        "score": avg_quality,
        "details": {
            "validation_percentage": (validation_present / total_analyses * 100) if total_analyses > 0 else 0,
            "quality_breakdown": quality_percentages,
            "individual_scores": quality_scores,
            "total_analyses": total_analyses,
            "validation_present": validation_present
        }
    }

def calculate_consistency_metrics(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Calculate consistency score"""
    
    total_analyses = len(outputs)
    consistent_outputs = 0
    structure_variations = 0
    field_consistency = {
        "sli": 0,
        "slo": 0,
        "alerts": 0,
        "llm_suggestions": 0
    }
    
    expected_structure = {
        "sli": list,
        "slo": list,
        "alerts": list,
        "llm_suggestions": list
    }
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        
        # Check structure consistency
        is_consistent = True
        for field, expected_type in expected_structure.items():
            field_value = output_data.get(field)
            if isinstance(field_value, expected_type):
                field_consistency[field] += 1
            else:
                is_consistent = False
        
        if is_consistent:
            consistent_outputs += 1
        else:
            structure_variations += 1
    
    # Calculate percentages
    consistency_percentages = {
        field: (count / total_analyses * 100) if total_analyses > 0 else 0
        for field, count in field_consistency.items()
    }
    
    overall_consistency = (consistent_outputs / total_analyses * 100) if total_analyses > 0 else 0
    
    return {
        "score": overall_consistency,
        "details": {
            "consistent_outputs": consistent_outputs,
            "structure_variations": structure_variations,
            "field_consistency": consistency_percentages
        }
    }

def calculate_coverage_metrics(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Calculate coverage score"""
    
    total_analyses = len(outputs)
    coverage_scores = []
    avg_counts = {
        "slis": 0,
        "slos": 0,
        "alerts": 0,
        "suggestions": 0
    }
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        
        # Count items
        sli_count = len(output_data.get("sli", []))
        slo_count = len(output_data.get("slo", []))
        alert_count = len(output_data.get("alerts", []))
        suggestion_count = len(output_data.get("llm_suggestions", []))
        
        avg_counts["slis"] += sli_count
        avg_counts["slos"] += slo_count
        avg_counts["alerts"] += alert_count
        avg_counts["suggestions"] += suggestion_count
        
        # Calculate coverage score (based on having reasonable number of items)
        coverage_score = 0
        if sli_count >= 2: coverage_score += 25
        if slo_count >= 1: coverage_score += 25
        if alert_count >= 1: coverage_score += 25
        if suggestion_count >= 1: coverage_score += 25
        
        coverage_scores.append(coverage_score)
    
    # Calculate averages
    for key in avg_counts:
        avg_counts[key] = avg_counts[key] / total_analyses if total_analyses > 0 else 0
    
    avg_coverage = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0
    
    return {
        "score": avg_coverage,
        "details": {
            "average_counts": avg_counts,
            "coverage_scores": coverage_scores,
            "targets": {
                "slis": "≥2",
                "slos": "≥1",
                "alerts": "≥1",
                "suggestions": "≥1"
            }
        }
    }

def calculate_confidence_metrics(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Calculate confidence score"""
    
    confidences = [output.confidence for output in outputs if output.confidence is not None]
    
    if not confidences:
        return {
            "score": 0,
            "details": {
                "message": "No confidence data available",
                "avg_confidence": 0,
                "confidence_distribution": {}
            }
        }
    
    avg_confidence = sum(confidences) / len(confidences)
    
    # Calculate distribution
    distribution = {
        "high": len([c for c in confidences if c >= 80]),
        "medium": len([c for c in confidences if 60 <= c < 80]),
        "low": len([c for c in confidences if c < 60])
    }
    
    return {
        "score": avg_confidence,
        "details": {
            "avg_confidence": avg_confidence,
            "confidence_distribution": distribution,
            "total_with_confidence": len(confidences)
        }
    }

@router.post("/scorecard/suggestions")
async def generate_scorecard_suggestions(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Generate LLM suggestions based on scorecard analysis"""
    try:
        body = await request.json()
        service_name = body.get("service_name")
        days = body.get("days", 30)
        
        # Get scorecard data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = select(LLMOutput).where(
            LLMOutput.created_at >= start_date,
            LLMOutput.created_at <= end_date
        )
        
        if service_name:
            query = query.where(text("input::text LIKE :service_pattern"))
            query = query.params(service_pattern=f'%"service_name": "{service_name}"%')
        
        result = await db.execute(query)
        outputs = result.scalars().all()
        
        if not outputs:
            raise HTTPException(status_code=404, detail="No data found for scorecard analysis")
        
        # Calculate scorecard metrics
        scorecard_data = calculate_scorecard_metrics(outputs)
        
        # Generate LLM suggestions
        suggestions = await generate_llm_suggestions(scorecard_data, service_name, days)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "service_name": service_name,
            "total_analyses": len(outputs),
            "scorecard_data": scorecard_data,
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")

async def generate_llm_suggestions(scorecard_data: Dict[str, Any], service_name: Optional[str], days: int) -> Dict[str, Any]:
    """Generate LLM suggestions based on scorecard metrics"""
    
    # Import here to avoid circular imports
    from backend.core.services.prompt.prompt_engine import generate_prompt_response
    
    # Prepare the prompt for LLM suggestions
    prompt_data = {
        "task": "scorecard_suggestions",
        "scorecard_data": scorecard_data,
        "service_name": service_name,
        "analysis_period_days": days,
        "current_timestamp": datetime.utcnow().isoformat()
    }
    
    # Generate suggestions using the LLM
    try:
        response = await generate_prompt_response(prompt_data)
        return response
    except Exception as e:
        # Fallback to basic suggestions if LLM fails
        return generate_fallback_suggestions(scorecard_data)

def generate_fallback_suggestions(scorecard_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic suggestions when LLM is unavailable"""
    
    suggestions = {
        "ai_confidence": 0.0,
        "suggestions": [],
        "priority_actions": [],
        "improvement_areas": [],
        "explanation": "Generated basic suggestions based on scorecard analysis"
    }
    
    overall_score = scorecard_data.get("overall_score", 0)
    breakdown = scorecard_data.get("breakdown", {})
    
    # Generate suggestions based on scores
    if overall_score < 70:
        suggestions["suggestions"].append("Overall score is below 70%. Focus on improving the lowest-scoring areas first.")
        suggestions["priority_actions"].append("Review and improve data quality and completeness")
    
    # Check completeness
    completeness_score = breakdown.get("completeness", {}).get("score", 0)
    if completeness_score < 80:
        suggestions["suggestions"].append(f"Completeness score is {completeness_score:.1f}%. Ensure all required fields are present in outputs.")
        suggestions["improvement_areas"].append("Output completeness")
    
    # Check quality
    quality_score = breakdown.get("quality", {}).get("score", 0)
    if quality_score < 80:
        suggestions["suggestions"].append(f"Quality score is {quality_score:.1f}%. Focus on improving output validation and accuracy.")
        suggestions["improvement_areas"].append("Output quality")
    
    # Check consistency
    consistency_score = breakdown.get("consistency", {}).get("score", 0)
    if consistency_score < 80:
        suggestions["suggestions"].append(f"Consistency score is {consistency_score:.1f}%. Standardize output formats and structures.")
        suggestions["improvement_areas"].append("Output consistency")
    
    # Check coverage
    coverage_score = breakdown.get("coverage", {}).get("score", 0)
    if coverage_score < 80:
        suggestions["suggestions"].append(f"Coverage score is {coverage_score:.1f}%. Ensure comprehensive SLI/SLO/Alert coverage.")
        suggestions["improvement_areas"].append("Coverage breadth")
    
    # Check confidence
    confidence_score = breakdown.get("confidence", {}).get("score", 0)
    if confidence_score < 80:
        suggestions["suggestions"].append(f"Confidence score is {confidence_score:.1f}%. Work on improving AI model confidence.")
        suggestions["improvement_areas"].append("AI confidence")
    
    # Add positive feedback for good scores
    if overall_score >= 85:
        suggestions["suggestions"].append("Excellent overall performance! Consider fine-tuning for even better results.")
    
    return suggestions
