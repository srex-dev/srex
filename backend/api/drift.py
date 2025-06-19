from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from .models_llm import SessionLocal, LLMOutput, DriftAnalysis

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/drift/analysis")
async def get_drift_analysis(
    service_name: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Analyze drift in LLM outputs over time"""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Build query
    query = select(LLMOutput).where(
        LLMOutput.created_at >= start_date,
        LLMOutput.created_at <= end_date
    )
    
    if service_name:
        query = query.where(text("input::text LIKE :service_pattern"))
        query = query.params(service_pattern=f'%"service_name": "{service_name}"%')
    
    query = query.order_by(LLMOutput.created_at.desc())
    
    result = await db.execute(query)
    outputs = result.scalars().all()
    
    if not outputs:
        raise HTTPException(status_code=404, detail="No data found for drift analysis")
    
    # Analyze drift
    drift_data = analyze_drift(outputs)
    
    # Generate LLM suggestions based on drift data
    suggestions = await generate_drift_suggestions(drift_data, service_name, days)
    
    # Store drift analysis in database
    await store_drift_analysis(db, start_date, end_date, days, service_name, len(outputs), drift_data)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "total_analyses": len(outputs),
        "drift_analysis": drift_data,
        "suggestions": suggestions
    }

async def store_drift_analysis(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime, 
    days: int, 
    service_name: Optional[str], 
    total_analyses: int, 
    drift_data: Dict[str, Any]
):
    """Store drift analysis results in the database"""
    
    # Extract confidence drift data
    confidence_drift = drift_data.get("confidence_drift", {})
    
    # Extract output consistency data
    output_consistency = drift_data.get("output_consistency", {})
    missing_fields = output_consistency.get("missing_fields", {})
    
    # Extract coverage drift data
    coverage_drift = drift_data.get("coverage_drift", {})
    recent_averages = coverage_drift.get("recent_averages", {})
    older_averages = coverage_drift.get("older_averages", {})
    coverage_trends = coverage_drift.get("coverage_trends", {})
    
    # Extract quality drift data
    quality_drift = drift_data.get("quality_drift", {})
    
    # Create drift analysis record
    drift_record = DriftAnalysis(
        analysis_date=datetime.utcnow(),
        period_start=start_date,
        period_end=end_date,
        period_days=days,
        service_name=service_name,
        total_analyses=total_analyses,
        
        # Confidence Drift
        confidence_status=confidence_drift.get("status", "unknown"),
        recent_avg_confidence=confidence_drift.get("recent_avg_confidence"),
        older_avg_confidence=confidence_drift.get("older_avg_confidence"),
        confidence_drift_percentage=confidence_drift.get("drift_percentage"),
        confidence_drift_direction=confidence_drift.get("drift_direction"),
        confidence_trend=confidence_drift.get("trend"),
        
        # Output Consistency
        consistency_percentage=output_consistency.get("consistency_percentage", 0),
        consistent_structure_count=output_consistency.get("consistent_structure", 0),
        structure_variations_count=output_consistency.get("structure_variations", 0),
        missing_fields_sli=missing_fields.get("sli", 0),
        missing_fields_slo=missing_fields.get("slo", 0),
        missing_fields_alerts=missing_fields.get("alerts", 0),
        missing_fields_suggestions=missing_fields.get("llm_suggestions", 0),
        
        # Coverage Drift
        coverage_status=coverage_drift.get("status", "unknown"),
        recent_avg_slis=recent_averages.get("slis"),
        recent_avg_slos=recent_averages.get("slos"),
        recent_avg_alerts=recent_averages.get("alerts"),
        recent_avg_suggestions=recent_averages.get("suggestions"),
        older_avg_slis=older_averages.get("slis"),
        older_avg_slos=older_averages.get("slos"),
        older_avg_alerts=older_averages.get("alerts"),
        older_avg_suggestions=older_averages.get("suggestions"),
        slis_change=coverage_trends.get("slis", {}).get("change"),
        slis_percentage_change=coverage_trends.get("slis", {}).get("percentage_change"),
        slos_change=coverage_trends.get("slos", {}).get("change"),
        slos_percentage_change=coverage_trends.get("slos", {}).get("percentage_change"),
        alerts_change=coverage_trends.get("alerts", {}).get("change"),
        alerts_percentage_change=coverage_trends.get("alerts", {}).get("percentage_change"),
        suggestions_change=coverage_trends.get("suggestions", {}).get("change"),
        suggestions_percentage_change=coverage_trends.get("suggestions", {}).get("percentage_change"),
        
        # Quality Drift
        avg_quality_score=quality_drift.get("avg_quality_score", 0),
        validation_present_count=quality_drift.get("validation_present", 0),
        complete_outputs_count=quality_drift.get("complete_outputs", 0),
        validation_percentage=quality_drift.get("validation_percentage", 0),
        completeness_percentage=quality_drift.get("completeness_percentage", 0),
    )
    
    db.add(drift_record)
    await db.commit()

@router.get("/drift/history")
async def get_drift_history(
    service_name: Optional[str] = None,
    days: int = 30,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get historical drift analysis data"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = select(DriftAnalysis).where(
        DriftAnalysis.analysis_date >= start_date,
        DriftAnalysis.analysis_date <= end_date
    )
    
    if service_name:
        query = query.where(DriftAnalysis.service_name == service_name)
    
    query = query.order_by(DriftAnalysis.analysis_date.desc()).limit(limit)
    
    result = await db.execute(query)
    drift_records = result.scalars().all()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "drift_history": [
            {
                "id": record.id,
                "analysis_date": record.analysis_date.isoformat(),
                "period_start": record.period_start.isoformat(),
                "period_end": record.period_end.isoformat(),
                "period_days": record.period_days,
                "service_name": record.service_name,
                "total_analyses": record.total_analyses,
                "confidence_drift": {
                    "status": record.confidence_status,
                    "recent_avg_confidence": record.recent_avg_confidence,
                    "older_avg_confidence": record.older_avg_confidence,
                    "drift_percentage": record.confidence_drift_percentage,
                    "drift_direction": record.confidence_drift_direction,
                    "trend": record.confidence_trend
                },
                "output_consistency": {
                    "consistency_percentage": record.consistency_percentage,
                    "consistent_structure": record.consistent_structure_count,
                    "total_analyses": record.total_analyses,
                    "structure_variations": record.structure_variations_count,
                    "missing_fields": {
                        "sli": record.missing_fields_sli,
                        "slo": record.missing_fields_slo,
                        "alerts": record.missing_fields_alerts,
                        "llm_suggestions": record.missing_fields_suggestions
                    }
                },
                "coverage_drift": {
                    "status": record.coverage_status,
                    "recent_averages": {
                        "slis": record.recent_avg_slis,
                        "slos": record.recent_avg_slos,
                        "alerts": record.recent_avg_alerts,
                        "suggestions": record.recent_avg_suggestions
                    },
                    "older_averages": {
                        "slis": record.older_avg_slis,
                        "slos": record.older_avg_slos,
                        "alerts": record.older_avg_alerts,
                        "suggestions": record.older_avg_suggestions
                    },
                    "coverage_trends": {
                        "slis": {
                            "change": record.slis_change,
                            "percentage_change": record.slis_percentage_change
                        },
                        "slos": {
                            "change": record.slos_change,
                            "percentage_change": record.slos_percentage_change
                        },
                        "alerts": {
                            "change": record.alerts_change,
                            "percentage_change": record.alerts_percentage_change
                        },
                        "suggestions": {
                            "change": record.suggestions_change,
                            "percentage_change": record.suggestions_percentage_change
                        }
                    }
                },
                "quality_drift": {
                    "total_analyses": record.total_analyses,
                    "validation_present": record.validation_present_count,
                    "complete_outputs": record.complete_outputs_count,
                    "avg_quality_score": record.avg_quality_score,
                    "validation_percentage": record.validation_percentage,
                    "completeness_percentage": record.completeness_percentage
                }
            }
            for record in drift_records
        ]
    }

@router.get("/drift/confidence-trend")
async def get_confidence_trend(
    service_name: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get confidence score trends over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = select(
        func.date_trunc('day', LLMOutput.created_at).label('date'),
        func.avg(LLMOutput.confidence).label('avg_confidence'),
        func.count(LLMOutput.id).label('analysis_count')
    ).where(
        LLMOutput.created_at >= start_date,
        LLMOutput.created_at <= end_date
    )
    
    if service_name:
        query = query.where(text("input::text LIKE :service_pattern"))
        query = query.params(service_pattern=f'%"service_name": "{service_name}"%')
    
    query = query.group_by(text("date")).order_by(text("date"))
    
    result = await db.execute(query)
    trends = result.fetchall()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "confidence_trend": [
            {
                "date": row.date.isoformat(),
                "avg_confidence": round(float(row.avg_confidence), 2) if row.avg_confidence else 0,
                "analysis_count": row.analysis_count
            }
            for row in trends
        ]
    }

@router.get("/drift/sli-evolution")
async def get_sli_evolution(
    service_name: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Track how SLI definitions evolve over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = select(LLMOutput).where(
        LLMOutput.created_at >= start_date,
        LLMOutput.created_at <= end_date
    )
    
    if service_name:
        query = query.where(text("input::text LIKE :service_pattern"))
        query = query.params(service_pattern=f'%"service_name": "{service_name}"%')
    
    query = query.order_by(LLMOutput.created_at.desc())
    
    result = await db.execute(query)
    outputs = result.scalars().all()
    
    sli_evolution = analyze_sli_evolution(outputs)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "sli_evolution": sli_evolution
    }

def analyze_drift(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Analyze drift in LLM outputs"""
    
    drift_metrics = {
        "confidence_drift": analyze_confidence_drift(outputs),
        "output_consistency": analyze_output_consistency(outputs),
        "coverage_drift": analyze_coverage_drift(outputs),
        "quality_drift": analyze_quality_drift(outputs)
    }
    
    return drift_metrics

def analyze_confidence_drift(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Analyze confidence score drift"""
    
    confidences = [output.confidence for output in outputs if output.confidence is not None]
    
    if not confidences:
        return {"status": "no_data", "message": "No confidence data available"}
    
    # Calculate drift metrics
    recent_confidences = confidences[:len(confidences)//3]  # Last third
    older_confidences = confidences[len(confidences)//3:]   # First two thirds
    
    if not recent_confidences or not older_confidences:
        return {"status": "insufficient_data", "message": "Need more data for drift analysis"}
    
    recent_avg = sum(recent_confidences) / len(recent_confidences)
    older_avg = sum(older_confidences) / len(older_confidences)
    
    drift_percentage = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
    
    return {
        "status": "analyzed",
        "recent_avg_confidence": round(recent_avg, 2),
        "older_avg_confidence": round(older_avg, 2),
        "drift_percentage": round(drift_percentage, 2),
        "drift_direction": "improving" if drift_percentage > 0 else "declining",
        "trend": "positive" if abs(drift_percentage) < 10 else "concerning"
    }

def analyze_output_consistency(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Analyze consistency of output structure"""
    
    consistency_metrics = {
        "total_analyses": len(outputs),
        "consistent_structure": 0,
        "missing_fields": {},
        "structure_variations": 0
    }
    
    expected_fields = ["sli", "slo", "alerts", "llm_suggestions"]
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        
        # Check for expected fields
        missing_fields = []
        for field in expected_fields:
            if field not in output_data or not output_data[field]:
                missing_fields.append(field)
        
        if not missing_fields:
            consistency_metrics["consistent_structure"] += 1
        else:
            consistency_metrics["structure_variations"] += 1
            for field in missing_fields:
                consistency_metrics["missing_fields"][field] = consistency_metrics["missing_fields"].get(field, 0) + 1
    
    consistency_metrics["consistency_percentage"] = round(
        (consistency_metrics["consistent_structure"] / consistency_metrics["total_analyses"] * 100), 2
    ) if consistency_metrics["total_analyses"] > 0 else 0
    
    return consistency_metrics

def analyze_coverage_drift(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Analyze drift in coverage (number of SLIs, SLOs, alerts)"""
    
    coverage_data = []
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        
        coverage = {
            "date": output.created_at.isoformat(),
            "slis_count": len(output_data.get("sli", [])),
            "slos_count": len(output_data.get("slo", [])),
            "alerts_count": len(output_data.get("alerts", [])),
            "suggestions_count": len(output_data.get("llm_suggestions", []))
        }
        coverage_data.append(coverage)
    
    if not coverage_data:
        return {"status": "no_data", "message": "No coverage data available"}
    
    # Calculate trends
    recent_coverage = coverage_data[:len(coverage_data)//3]
    older_coverage = coverage_data[len(coverage_data)//3:]
    
    if not recent_coverage or not older_coverage:
        return {"status": "insufficient_data", "message": "Need more data for coverage analysis"}
    
    # Calculate averages with proper rounding
    recent_avg = {
        "slis": round(sum(c["slis_count"] for c in recent_coverage) / len(recent_coverage), 2),
        "slos": round(sum(c["slos_count"] for c in recent_coverage) / len(recent_coverage), 2),
        "alerts": round(sum(c["alerts_count"] for c in recent_coverage) / len(recent_coverage), 2),
        "suggestions": round(sum(c["suggestions_count"] for c in recent_coverage) / len(recent_coverage), 2)
    }
    
    older_avg = {
        "slis": round(sum(c["slis_count"] for c in older_coverage) / len(older_coverage), 2),
        "slos": round(sum(c["slos_count"] for c in older_coverage) / len(older_coverage), 2),
        "alerts": round(sum(c["alerts_count"] for c in older_coverage) / len(older_coverage), 2),
        "suggestions": round(sum(c["suggestions_count"] for c in older_coverage) / len(older_coverage), 2)
    }
    
    return {
        "status": "analyzed",
        "recent_averages": recent_avg,
        "older_averages": older_avg,
        "coverage_trends": {
            "slis": {
                "change": round(recent_avg["slis"] - older_avg["slis"], 2),
                "percentage_change": round(((recent_avg["slis"] - older_avg["slis"]) / older_avg["slis"] * 100), 2) if older_avg["slis"] > 0 else 0
            },
            "slos": {
                "change": round(recent_avg["slos"] - older_avg["slos"], 2),
                "percentage_change": round(((recent_avg["slos"] - older_avg["slos"]) / older_avg["slos"] * 100), 2) if older_avg["slos"] > 0 else 0
            },
            "alerts": {
                "change": round(recent_avg["alerts"] - older_avg["alerts"], 2),
                "percentage_change": round(((recent_avg["alerts"] - older_avg["alerts"]) / older_avg["alerts"] * 100), 2) if older_avg["alerts"] > 0 else 0
            },
            "suggestions": {
                "change": round(recent_avg["suggestions"] - older_avg["suggestions"], 2),
                "percentage_change": round(((recent_avg["suggestions"] - older_avg["suggestions"]) / older_avg["suggestions"] * 100), 2) if older_avg["suggestions"] > 0 else 0
            }
        }
    }

def analyze_quality_drift(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Analyze quality drift based on validation and completeness"""
    
    quality_metrics = {
        "total_analyses": len(outputs),
        "validation_present": 0,
        "complete_outputs": 0,
        "quality_scores": []
    }
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        
        # Check for validation
        if "validation_summary" in output_data:
            quality_metrics["validation_present"] += 1
        
        # Check completeness
        has_slis = bool(output_data.get("sli"))
        has_slos = bool(output_data.get("slo"))
        has_alerts = bool(output_data.get("alerts"))
        has_suggestions = bool(output_data.get("llm_suggestions"))
        
        if has_slis and has_slos and has_alerts and has_suggestions:
            quality_metrics["complete_outputs"] += 1
        
        # Calculate quality score
        quality_score = 0
        if has_slis: quality_score += 25
        if has_slos: quality_score += 25
        if has_alerts: quality_score += 25
        if has_suggestions: quality_score += 25
        
        quality_metrics["quality_scores"].append(quality_score)
    
    if quality_metrics["quality_scores"]:
        quality_metrics["avg_quality_score"] = round(sum(quality_metrics["quality_scores"]) / len(quality_metrics["quality_scores"]), 2)
        quality_metrics["validation_percentage"] = round((quality_metrics["validation_present"] / quality_metrics["total_analyses"]) * 100, 2)
        quality_metrics["completeness_percentage"] = round((quality_metrics["complete_outputs"] / quality_metrics["total_analyses"]) * 100, 2)
    else:
        quality_metrics["avg_quality_score"] = 0
        quality_metrics["validation_percentage"] = 0
        quality_metrics["completeness_percentage"] = 0
    
    return quality_metrics

def analyze_sli_evolution(outputs: List[LLMOutput]) -> Dict[str, Any]:
    """Analyze how SLI definitions evolve over time"""
    
    sli_evolution = {
        "total_analyses": len(outputs),
        "sli_definitions": {},
        "evolution_timeline": []
    }
    
    for output in outputs:
        if not output.output:
            continue
            
        output_data = output.output.get("final_data", output.output)
        slis = output_data.get("sli", [])
        
        timeline_entry = {
            "date": output.created_at.isoformat(),
            "slis_count": len(slis),
            "sli_names": [sli.get("name", "unknown") for sli in slis],
            "sli_types": [sli.get("type", "unknown") for sli in slis]
        }
        sli_evolution["evolution_timeline"].append(timeline_entry)
        
        # Track individual SLI definitions
        for sli in slis:
            sli_name = sli.get("name", "unknown")
            if sli_name not in sli_evolution["sli_definitions"]:
                sli_evolution["sli_definitions"][sli_name] = {
                    "first_seen": output.created_at.isoformat(),
                    "last_seen": output.created_at.isoformat(),
                    "appearances": 0,
                    "type": sli.get("type", "unknown"),
                    "definitions": []
                }
            
            sli_evolution["sli_definitions"][sli_name]["appearances"] += 1
            sli_evolution["sli_definitions"][sli_name]["last_seen"] = output.created_at.isoformat()
            sli_evolution["sli_definitions"][sli_name]["definitions"].append({
                "date": output.created_at.isoformat(),
                "definition": sli
            })
    
    # Sort timeline by date
    sli_evolution["evolution_timeline"].sort(key=lambda x: x["date"])
    
    return sli_evolution

async def generate_drift_suggestions(drift_data: Dict[str, Any], service_name: Optional[str], days: int) -> Dict[str, Any]:
    """Generate LLM suggestions based on drift analysis data"""
    try:
        # Import here to avoid circular imports
        from backend.core.services.prompt.prompt_engine import generate_prompt_response
        
        # Prepare the prompt for drift-based suggestions
        prompt_data = {
            "task": "drift_suggestions",
            "drift_data": drift_data,
            "service_name": service_name,
            "analysis_period_days": days,
            "current_timestamp": datetime.utcnow().isoformat()
        }
        
        # Generate suggestions using the LLM
        response = await generate_prompt_response(prompt_data)
        return response
    except Exception as e:
        # Fallback to basic suggestions if LLM fails
        return generate_drift_fallback_suggestions(drift_data)

def generate_drift_fallback_suggestions(drift_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic suggestions when LLM is unavailable for drift analysis"""
    
    suggestions = {
        "ai_confidence": 0.0,
        "priority_actions": [],
        "improvement_areas": [],
        "suggestions": [],
        "root_causes": [],
        "success_metrics": [],
        "explanation": "Generated basic suggestions based on drift analysis"
    }
    
    # Analyze confidence drift
    confidence_drift = drift_data.get("confidence_drift", {})
    confidence_trend = confidence_drift.get("trend", "unknown")
    confidence_percentage = confidence_drift.get("drift_percentage", 0)
    
    if confidence_trend == "concerning":
        suggestions["priority_actions"].append("Investigate causes of declining confidence")
        suggestions["improvement_areas"].append("AI Confidence")
        suggestions["suggestions"].append(f"Confidence is declining by {abs(confidence_percentage):.1f}%. Focus on improving AI model confidence.")
        suggestions["root_causes"].append("Potential model degradation or data drift")
        suggestions["success_metrics"].append("Improvement in confidence scores over time")
    
    # Analyze output consistency
    output_consistency = drift_data.get("output_consistency", {})
    consistency_percentage = output_consistency.get("consistency_percentage", 0)
    
    if consistency_percentage < 80:
        suggestions["priority_actions"].append("Standardize output structure and field naming")
        suggestions["improvement_areas"].append("Output Consistency")
        suggestions["suggestions"].append(f"Output consistency is {consistency_percentage:.1f}%. Standardize output formats.")
        suggestions["root_causes"].append("Inconsistent prompt templates or model behavior")
        suggestions["success_metrics"].append("Increase in consistency percentage")
    
    # Analyze quality drift
    quality_drift = drift_data.get("quality_drift", {})
    quality_score = quality_drift.get("avg_quality_score", 0)
    
    if quality_score < 80:
        suggestions["priority_actions"].append("Enhance output validation and quality checks")
        suggestions["improvement_areas"].append("Output Quality")
        suggestions["suggestions"].append(f"Quality score is {quality_score:.1f}%. Improve output validation and completeness.")
        suggestions["root_causes"].append("Insufficient validation or incomplete outputs")
        suggestions["success_metrics"].append("Higher average quality scores")
    
    # Analyze coverage drift
    coverage_drift = drift_data.get("coverage_drift", {})
    coverage_trends = coverage_drift.get("coverage_trends", {})
    
    # Check SLI coverage
    slis_change = coverage_trends.get("slis", {}).get("percentage_change", 0)
    if slis_change < 0:
        suggestions["improvement_areas"].append("SLI Coverage")
        suggestions["suggestions"].append(f"SLI coverage is declining by {abs(slis_change):.1f}%. Ensure comprehensive SLI generation.")
        suggestions["success_metrics"].append("Stable or increasing SLI coverage")
    
    # Check SLO coverage
    slos_change = coverage_trends.get("slos", {}).get("percentage_change", 0)
    if slos_change < 0:
        suggestions["improvement_areas"].append("SLO Coverage")
        suggestions["suggestions"].append(f"SLO coverage is declining by {abs(slos_change):.1f}%. Maintain SLO generation consistency.")
        suggestions["success_metrics"].append("Stable or increasing SLO coverage")
    
    # Add positive feedback for good trends
    if confidence_trend == "positive" and consistency_percentage >= 80 and quality_score >= 80:
        suggestions["suggestions"].append("Excellent drift performance! Consider fine-tuning for even better results.")
        suggestions["success_metrics"].append("Maintain current performance levels")
    
    return suggestions 