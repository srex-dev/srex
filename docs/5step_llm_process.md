# 5-Step LLM Process for Observability Generation

## Overview

The 5-step LLM process is an improved approach to generating observability configurations (SLIs, SLOs, and alerts) by breaking down the complex task into 5 focused, specialized steps. This approach provides better quality, reliability, and maintainability compared to the original single-prompt method.

## Architecture

### Step 1: SLI Discovery & Validation
**Template**: `step1_sli_discovery.j2`
**Purpose**: Analyze raw metrics data and identify valid Service Level Indicators
**Input**: Raw metrics data, service context
**Output**: Validated SLI definitions with proper types, units, and queries
**Focus**: Data quality, proper categorization, query validation

### Step 2: SLO Generation
**Template**: `step2_slo_generation.j2`
**Purpose**: Create Service Level Objectives based on validated SLIs
**Input**: Validated SLIs, business context, service criticality
**Output**: SLOs with appropriate targets, time windows, and descriptions
**Focus**: Business alignment, realistic targets, proper time windows

### Step 3: Alert Rule Creation
**Template**: `step3_alert_creation.j2`
**Purpose**: Generate actionable alerting policies
**Input**: SLOs, SLIs, service context
**Output**: Alert rules with thresholds, durations, severity levels
**Focus**: Actionable thresholds, proper escalation, noise reduction

### Step 4: Analysis & Recommendations
**Template**: `step4_analysis_recommendations.j2`
**Purpose**: Provide insights and improvement suggestions
**Input**: Complete SLI/SLO/Alert set, historical context
**Output**: Explanations, optimization suggestions, risk assessments
**Focus**: Strategic insights, actionable improvements, risk mitigation

### Step 5: Validation & Integration
**Template**: `step5_validation_integration.j2`
**Purpose**: Final validation and integration of all components
**Input**: All previous outputs
**Output**: Final validated JSON with consistency checks
**Focus**: Data consistency, JSON validation, cross-reference validation

## Benefits

1. **Better Quality**: Each step focuses on one aspect without cognitive overload
2. **Easier Debugging**: Issues can be isolated to specific steps
3. **Improved Reliability**: Smaller, focused prompts are less likely to fail
4. **Better Validation**: Each step can validate the previous step's output
5. **Flexibility**: Steps can be run independently or in different orders
6. **Maintainability**: Easier to update individual components

## Usage

### Backend API

#### Original Method (Single Prompt)
```bash
POST /llm
{
  "task": "default",
  "input": {
    "service_name": "my-service",
    "timeframe": "5min"
  }
}
```

#### 5-Step Method
```bash
POST /llm/5step
{
  "input": {
    "service_name": "my-service",
    "description": "A critical API service",
    "timeframe": "5min"
  },
  "model": "llama2",
  "temperature": 0.7
}
```

### Frontend

The frontend analysis page now includes a toggle to choose between the original and 5-step methods:

1. **Original Method**: Uses the traditional single-prompt approach
2. **5-Step Method**: Uses the new 5-step process with additional configuration options

### Configuration Options

When using the 5-step method, you can configure:

- **Model**: Choose between llama2, mistral, codellama
- **Temperature**: Control creativity (0.0 to 1.0)
- **Timeframe**: Data collection period (3m to 30d)

## Implementation Details

### Template Structure

Each step template follows a consistent pattern:
- Clear input context definition
- Specific output format requirements
- Validation rules and guidelines
- Example outputs for reference

### Error Handling

- Each step includes comprehensive error handling
- Debug information is saved to `debug/` directory
- Failed steps are logged with detailed error messages
- Graceful degradation when individual steps fail

### Data Flow

```
Raw Input → Step 1 (SLI Discovery) → Step 2 (SLO Generation) → 
Step 3 (Alert Creation) → Step 4 (Analysis) → Step 5 (Validation) → Final Output
```

### Validation

The final step performs comprehensive validation:
- Cross-reference validation (SLOs reference valid SLIs)
- Data consistency checks
- JSON syntax validation
- Business logic validation
- Completeness checks

## Testing

Run the test script to verify the 5-step process:

```bash
python test_5step_llm.py
```

## Debugging

Debug information is saved for each step:
- `debug/step1_sli_discovery.txt`
- `debug/step2_slo_generation.txt`
- `debug/step3_alert_creation.txt`
- `debug/step4_analysis_recommendations.txt`
- `debug/step5_validation_integration.txt`

## Migration from Original Method

The original method is preserved as `default_original.j2` and continues to work. The 5-step method is an enhancement that can be used alongside or instead of the original method.

## Performance Considerations

- The 5-step method requires 5 LLM calls instead of 1
- Total processing time is approximately 3-5x longer
- Each step is optimized for its specific task
- Results are generally higher quality and more reliable

## Future Enhancements

Potential improvements for the 5-step process:
1. Parallel execution of independent steps
2. Caching of intermediate results
3. Step-specific model selection
4. Dynamic step ordering based on input complexity
5. A/B testing between original and 5-step methods 