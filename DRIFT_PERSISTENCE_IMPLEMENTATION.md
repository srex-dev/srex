# Drift Data Persistence Implementation

## Overview
Successfully implemented drift data persistence for the SREx policy-as-code system, enabling historical tracking, trend analysis, and drift alerts for LLM outputs.

## What Was Implemented

### 1. Database Model (`backend/api/models_llm.py`)
- **DriftAnalysis Table**: New database table to store drift analysis results
- **Comprehensive Fields**: 
  - Analysis metadata (date, period, service, total analyses)
  - Confidence drift metrics (status, averages, drift percentage, direction, trend)
  - Output consistency metrics (consistency percentage, structure counts, missing fields)
  - Coverage drift metrics (SLI/SLO/Alert/Suggestion averages and trends)
  - Quality drift metrics (quality scores, validation rates, completeness)
- **Database Indexes**: Optimized for efficient querying by date, service, and period

### 2. Backend API Enhancements (`backend/api/drift.py`)
- **Enhanced Drift Analysis**: Updated to store results in database
- **New History Endpoint**: `/api/drift/history` for retrieving historical data
- **Data Storage Function**: `store_drift_analysis()` to persist analysis results
- **Query Parameters**: Support for filtering by service, time period, and limit

### 3. Frontend Components
- **Drift History Page** (`frontend/src/app/drift/history/page.tsx`):
  - Historical drift analysis display
  - Service and time period filtering
  - Visual trend indicators and status colors
  - Detailed metrics breakdown
- **API Proxy** (`frontend/src/app/api/drift/history/route.ts`):
  - Frontend proxy for drift history API
  - Error handling and response formatting
- **Navigation Integration**: Added "View History" link to drift analysis page

### 4. Database Migration
- **Migration Script** (`backend/create_drift_table.py`):
  - Safe table creation with existence checking
  - Column verification and reporting
  - Error handling and rollback support

## Key Features

### Historical Tracking
- **Time-based Analysis**: Store drift analysis results with timestamps
- **Period Comparison**: Compare recent vs. older periods for trend detection
- **Service-specific Tracking**: Filter and analyze drift by specific services

### Trend Analysis
- **Confidence Trends**: Track AI confidence changes over time
- **Coverage Trends**: Monitor SLI/SLO/Alert/Suggestion coverage changes
- **Quality Trends**: Track output quality and consistency trends
- **Visual Indicators**: Color-coded status indicators (✅ positive, ⚠️ concerning, 🔄 neutral)

### Data Persistence Benefits
- **Historical Context**: Compare current drift against historical baselines
- **Alert Generation**: Identify concerning drift patterns over time
- **Performance Monitoring**: Track system performance and stability
- **Service Comparison**: Compare drift patterns across different services

## API Endpoints

### GET `/api/drift/analysis`
- **Purpose**: Analyze current drift and store results
- **Parameters**: `service_name` (optional), `days` (default: 30)
- **Response**: Current drift analysis + stores to database

### GET `/api/drift/history`
- **Purpose**: Retrieve historical drift analysis data
- **Parameters**: `service_name` (optional), `days` (default: 30), `limit` (default: 50)
- **Response**: Historical drift analysis records

## Database Schema

```sql
CREATE TABLE drift_analyses (
    id SERIAL PRIMARY KEY,
    analysis_date TIMESTAMP NOT NULL DEFAULT NOW(),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    period_days INTEGER NOT NULL,
    service_name VARCHAR,
    total_analyses INTEGER NOT NULL,
    
    -- Confidence Drift
    confidence_status VARCHAR NOT NULL,
    recent_avg_confidence FLOAT,
    older_avg_confidence FLOAT,
    confidence_drift_percentage FLOAT,
    confidence_drift_direction VARCHAR,
    confidence_trend VARCHAR,
    
    -- Output Consistency
    consistency_percentage FLOAT NOT NULL,
    consistent_structure_count INTEGER NOT NULL,
    structure_variations_count INTEGER NOT NULL,
    missing_fields_sli INTEGER NOT NULL DEFAULT 0,
    missing_fields_slo INTEGER NOT NULL DEFAULT 0,
    missing_fields_alerts INTEGER NOT NULL DEFAULT 0,
    missing_fields_suggestions INTEGER NOT NULL DEFAULT 0,
    
    -- Coverage Drift
    coverage_status VARCHAR NOT NULL,
    recent_avg_slis FLOAT,
    recent_avg_slos FLOAT,
    recent_avg_alerts FLOAT,
    recent_avg_suggestions FLOAT,
    older_avg_slis FLOAT,
    older_avg_slos FLOAT,
    older_avg_alerts FLOAT,
    older_avg_suggestions FLOAT,
    slis_change FLOAT,
    slis_percentage_change FLOAT,
    slos_change FLOAT,
    slos_percentage_change FLOAT,
    alerts_change FLOAT,
    alerts_percentage_change FLOAT,
    suggestions_change FLOAT,
    suggestions_percentage_change FLOAT,
    
    -- Quality Drift
    avg_quality_score FLOAT NOT NULL,
    validation_present_count INTEGER NOT NULL,
    complete_outputs_count INTEGER NOT NULL,
    validation_percentage FLOAT NOT NULL,
    completeness_percentage FLOAT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_drift_analysis_date ON drift_analyses(analysis_date);
CREATE INDEX idx_drift_analysis_service ON drift_analyses(service_name);
CREATE INDEX idx_drift_analysis_period ON drift_analyses(period_start, period_end);
```

## Usage Examples

### Running Drift Analysis (stores to database)
```bash
curl -X GET "http://localhost:8001/api/drift/analysis?days=30&service_name=user-service"
```

### Retrieving Historical Data
```bash
curl -X GET "http://localhost:8001/api/drift/history?days=90&limit=10"
```

### Frontend Access
- **Drift Analysis**: Navigate to `/drift` for current analysis
- **Drift History**: Navigate to `/drift/history` for historical data
- **Service Filtering**: Use dropdown to filter by specific services
- **Time Periods**: Select 7, 30, 60, or 90 days for analysis

## Benefits Achieved

1. **Historical Context**: Can now compare current drift against historical baselines
2. **Trend Detection**: Identify patterns and trends over time
3. **Alert Capability**: Set up alerts for concerning drift patterns
4. **Service Comparison**: Compare drift patterns across different services
5. **Performance Monitoring**: Track system stability and performance over time
6. **Data-Driven Decisions**: Make informed decisions based on historical drift data

## Next Steps (Optional Enhancements)

1. **Drift Alerts**: Implement automated alerts for concerning drift patterns
2. **Trend Charts**: Add visual charts showing drift trends over time
3. **Export Functionality**: Allow export of drift data for external analysis
4. **Custom Time Periods**: Allow custom date ranges for analysis
5. **Drift Thresholds**: Configurable thresholds for drift severity levels
6. **Email Notifications**: Send email alerts for significant drift changes

## Testing Status

✅ **Backend API**: Drift analysis and history endpoints working
✅ **Database**: Drift_analyses table created and populated
✅ **Frontend**: Drift history page displaying data correctly
✅ **Data Persistence**: Analysis results being stored and retrieved
✅ **Error Handling**: Proper error handling and validation

The implementation is complete and fully functional, providing comprehensive drift data persistence for the SREx system. 