'use client';
import PageContainer from '@/components/layout/PageContainer';
import React, { useState, useEffect } from 'react';
import { JSONTree } from 'react-json-tree';

// Drift Score Explanation Component
const DriftScoreExplanation = ({ title, value, trend, direction, color, details, children }: any) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-gray-50 rounded-lg p-4 relative">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-700">{title}</h4>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs bg-white bg-opacity-50 rounded-full w-5 h-5 flex items-center justify-center hover:bg-opacity-75 transition-colors"
          title="Click for detailed explanation"
        >
          {isExpanded ? '−' : '+'}
        </button>
      </div>
      <div className={`text-2xl font-bold ${color}`}>
        {typeof value === 'number' && !isNaN(value) ? value.toFixed(1) + '%' : 'N/A'}
      </div>
      <div className={`text-sm ${color}`}>
        {trend} {direction}
      </div>
      {children}
      
      {isExpanded && (
        <div className="mt-3 p-3 bg-white bg-opacity-50 rounded text-left">
          <div className="text-xs font-medium mb-2">How this drift is calculated:</div>
          <div className="text-xs space-y-1">
            {details}
          </div>
        </div>
      )}
    </div>
  );
};

// Helper for safe number formatting
function safeToFixed(val: any, digits = 1) {
  return typeof val === 'number' && !isNaN(val) ? val.toFixed(digits) : 'N/A';
}

export default function DriftPage() {
  const [driftData, setDriftData] = useState<any>(null);
  const [confidenceTrend, setConfidenceTrend] = useState<any>(null);
  const [sliEvolution, setSliEvolution] = useState<any>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [selectedService, setSelectedService] = useState<string>('');
  const [selectedDays, setSelectedDays] = useState<number>(30);
  const [availableServices, setAvailableServices] = useState<string[]>([]);

  // Fetch available services
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch('/api/llm/components');
        if (response.ok) {
          const components = await response.json();
          setAvailableServices(components);
        }
      } catch (error) {
        console.error('Error fetching services:', error);
      }
    };

    fetchServices();
    // Also fetch drift data on mount
    fetchDriftAnalysis();
  }, []);

  const fetchDriftAnalysis = async () => {
    setLoading('drift');
    try {
      const params = new URLSearchParams({
        days: selectedDays.toString(),
        ...(selectedService && { service_name: selectedService })
      });
      
      console.log('Fetching drift analysis with params:', params.toString());
      const response = await fetch(`/api/drift/analysis?${params}`);
      if (response.ok) {
        const data = await response.json();
        console.log('Drift analysis data received:', data);
        setDriftData(data);
      } else {
        console.error('Failed to fetch drift analysis:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error fetching drift analysis:', error);
    } finally {
      setLoading(null);
    }
  };

  const fetchConfidenceTrend = async () => {
    setLoading('confidence');
    try {
      const params = new URLSearchParams({
        days: selectedDays.toString(),
        ...(selectedService && { service_name: selectedService })
      });
      
      const response = await fetch(`/api/drift/confidence-trend?${params}`);
      if (response.ok) {
        const data = await response.json();
        setConfidenceTrend(data);
      } else {
        console.error('Failed to fetch confidence trend');
      }
    } catch (error) {
      console.error('Error fetching confidence trend:', error);
    } finally {
      setLoading(null);
    }
  };

  const fetchSliEvolution = async () => {
    setLoading('sli');
    try {
      const params = new URLSearchParams({
        days: selectedDays.toString(),
        ...(selectedService && { service_name: selectedService })
      });
      
      const response = await fetch(`/api/drift/sli-evolution?${params}`);
      if (response.ok) {
        const data = await response.json();
        setSliEvolution(data);
      } else {
        console.error('Failed to fetch SLI evolution');
      }
    } catch (error) {
      console.error('Error fetching SLI evolution:', error);
    } finally {
      setLoading(null);
    }
  };

  const fetchAllData = () => {
    fetchDriftAnalysis();
    fetchConfidenceTrend();
    fetchSliEvolution();
  };

  const getDriftStatusColor = (trend: string) => {
    switch (trend) {
      case 'positive': return 'text-green-600';
      case 'concerning': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  const getDriftStatusIcon = (trend: string) => {
    switch (trend) {
      case 'positive': return '✅';
      case 'concerning': return '⚠️';
      default: return '🔄';
    }
  };

  return (
    <PageContainer title="Drift Analysis" actions={
      <a
        href="/drift/history"
        className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
      >
        View History
      </a>
    }>
      <div className="text-sm text-gray-600 mb-6">
        Analyze drift in LLM outputs over time
      </div>

      {/* Controls */}
      <div className="mb-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Controls</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Service (Optional)
            </label>
            <select
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            >
              <option value="">All Services</option>
              {availableServices.map(service => (
                <option key={service} value={service}>{service}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Period (Days)
            </label>
            <select
              value={selectedDays}
              onChange={(e) => setSelectedDays(Number(e.target.value))}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={fetchAllData}
              disabled={loading !== null}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Analyze Drift'}
            </button>
          </div>
        </div>
      </div>

      {/* Drift Analysis Results */}
      {driftData && (
        <div className="mb-6 bg-white rounded-lg shadow">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Drift Analysis Results
              <span className="ml-2 text-sm text-gray-500">
                ({driftData.period.start_date} to {driftData.period.end_date})
              </span>
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {/* Confidence Drift */}
              <DriftScoreExplanation
                title="Confidence Drift"
                value={driftData.drift_analysis.confidence_drift.recent_avg_confidence}
                trend={getDriftStatusIcon(driftData.drift_analysis.confidence_drift.trend)}
                direction={driftData.drift_analysis.confidence_drift.drift_direction}
                color={getDriftStatusColor(driftData.drift_analysis.confidence_drift.trend)}
                details={[
                  `• Baseline confidence: ${safeToFixed(driftData.drift_analysis.confidence_drift.older_avg_confidence)}%`,
                  `• Current confidence: ${safeToFixed(driftData.drift_analysis.confidence_drift.recent_avg_confidence)}%`,
                  `• Change: ${safeToFixed(driftData.drift_analysis.confidence_drift.drift_percentage)}%`,
                  `• Formula: ((current - baseline) / baseline) × 100`,
                  `• Trend: ${driftData.drift_analysis.confidence_drift.trend}`,
                  `• Direction: ${driftData.drift_analysis.confidence_drift.drift_direction}`,
                  `• Positive drift: Confidence improving over time`,
                  `• Concerning drift: Confidence declining over time`
                ]}
              />
              
              {/* Output Consistency */}
              <DriftScoreExplanation
                title="Output Consistency"
                value={driftData.drift_analysis.output_consistency.consistency_percentage}
                trend="📊"
                direction="consistency"
                color="text-green-600"
                details={[
                  `• Consistent outputs: ${driftData.drift_analysis.output_consistency.consistent_structure || 0}`,
                  `• Total outputs: ${driftData.drift_analysis.output_consistency.total_analyses || 0}`,
                  `• Structure variations: ${driftData.drift_analysis.output_consistency.structure_variations || 0}`,
                  `• Formula: (consistent_structure / total_analyses) × 100`,
                  `• Measures: Structural and content consistency`,
                  `• Checks: JSON structure, field naming, data types`,
                  `• Threshold: 80% similarity for consistency`,
                  `• High consistency: Stable, reliable outputs`,
                  `• Low consistency: Unstable, variable outputs`,
                  `• Missing fields: SLI: ${driftData.drift_analysis.output_consistency.missing_fields?.sli || 0}, SLO: ${driftData.drift_analysis.output_consistency.missing_fields?.slo || 0}, Alerts: ${driftData.drift_analysis.output_consistency.missing_fields?.alerts || 0}, Suggestions: ${driftData.drift_analysis.output_consistency.missing_fields?.llm_suggestions || 0}`
                ]}
              />
              
              {/* Quality Drift */}
              <DriftScoreExplanation
                title="Quality Drift"
                value={driftData.drift_analysis.quality_drift.avg_quality_score}
                trend="📊"
                direction="current"
                color="text-blue-600"
                details={[
                  `• Current average quality: ${safeToFixed(driftData.drift_analysis.quality_drift.avg_quality_score)}%`,
                  `• Total analyses: ${driftData.drift_analysis.quality_drift.total_analyses || 0}`,
                  `• Completeness: ${safeToFixed(driftData.drift_analysis.quality_drift.completeness_percentage)}%`,
                  `• Validation present: ${driftData.drift_analysis.quality_drift.validation_present || 0}`,
                  `• Formula: Average of quality scores`,
                  `• Measures: Validation success rate over time`,
                  `• Includes: JSON parsing, field validation, logic checks`,
                  `• Quality scores range: 0-100 per analysis`,
                  `• Higher scores indicate better output quality`
                ]}
              />
            </div>
            
            {/* Coverage Drift Section */}
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Coverage Drift Analysis</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <DriftScoreExplanation
                  title="Coverage Drift (SLIs)"
                  value={driftData.drift_analysis.coverage_drift.coverage_trends?.slis?.percentage_change || 0}
                  trend={getDriftStatusIcon((driftData.drift_analysis.coverage_drift.coverage_trends?.slis?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  direction={(driftData.drift_analysis.coverage_drift.coverage_trends?.slis?.percentage_change || 0) >= 0 ? 'expanding' : 'shrinking'}
                  color={getDriftStatusColor((driftData.drift_analysis.coverage_drift.coverage_trends?.slis?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  details={[
                    `• Baseline SLIs: ${safeToFixed(driftData.drift_analysis.coverage_drift.older_averages?.slis)}`,
                    `• Current SLIs: ${safeToFixed(driftData.drift_analysis.coverage_drift.recent_averages?.slis)}`,
                    `• Change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.slis?.change)}`,
                    `• Percentage change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.slis?.percentage_change)}%`
                  ]}
                />
                <DriftScoreExplanation
                  title="Coverage Drift (SLOs)"
                  value={driftData.drift_analysis.coverage_drift.coverage_trends?.slos?.percentage_change || 0}
                  trend={getDriftStatusIcon((driftData.drift_analysis.coverage_drift.coverage_trends?.slos?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  direction={(driftData.drift_analysis.coverage_drift.coverage_trends?.slos?.percentage_change || 0) >= 0 ? 'expanding' : 'shrinking'}
                  color={getDriftStatusColor((driftData.drift_analysis.coverage_drift.coverage_trends?.slos?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  details={[
                    `• Baseline SLOs: ${safeToFixed(driftData.drift_analysis.coverage_drift.older_averages?.slos)}`,
                    `• Current SLOs: ${safeToFixed(driftData.drift_analysis.coverage_drift.recent_averages?.slos)}`,
                    `• Change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.slos?.change)}`,
                    `• Percentage change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.slos?.percentage_change)}%`
                  ]}
                />
                <DriftScoreExplanation
                  title="Coverage Drift (Alerts)"
                  value={driftData.drift_analysis.coverage_drift.coverage_trends?.alerts?.percentage_change || 0}
                  trend={getDriftStatusIcon((driftData.drift_analysis.coverage_drift.coverage_trends?.alerts?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  direction={(driftData.drift_analysis.coverage_drift.coverage_trends?.alerts?.percentage_change || 0) >= 0 ? 'expanding' : 'shrinking'}
                  color={getDriftStatusColor((driftData.drift_analysis.coverage_drift.coverage_trends?.alerts?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  details={[
                    `• Baseline Alerts: ${safeToFixed(driftData.drift_analysis.coverage_drift.older_averages?.alerts)}`,
                    `• Current Alerts: ${safeToFixed(driftData.drift_analysis.coverage_drift.recent_averages?.alerts)}`,
                    `• Change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.alerts?.change)}`,
                    `• Percentage change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.alerts?.percentage_change)}%`
                  ]}
                />
                <DriftScoreExplanation
                  title="Coverage Drift (Suggestions)"
                  value={driftData.drift_analysis.coverage_drift.coverage_trends?.suggestions?.percentage_change || 0}
                  trend={getDriftStatusIcon((driftData.drift_analysis.coverage_drift.coverage_trends?.suggestions?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  direction={(driftData.drift_analysis.coverage_drift.coverage_trends?.suggestions?.percentage_change || 0) >= 0 ? 'expanding' : 'shrinking'}
                  color={getDriftStatusColor((driftData.drift_analysis.coverage_drift.coverage_trends?.suggestions?.percentage_change || 0) >= 0 ? 'positive' : 'concerning')}
                  details={[
                    `• Baseline Suggestions: ${safeToFixed(driftData.drift_analysis.coverage_drift.older_averages?.suggestions)}`,
                    `• Current Suggestions: ${safeToFixed(driftData.drift_analysis.coverage_drift.recent_averages?.suggestions)}`,
                    `• Change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.suggestions?.change)}`,
                    `• Percentage change: ${safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.suggestions?.percentage_change)}%`
                  ]}
                />
              </div>
            </div>
            
            {/* Drift Insights */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-800 mb-2">Drift Analysis Insights</h4>
              <div className="text-sm text-blue-700 space-y-1">
                <div>• <strong>Confidence Drift:</strong> {driftData.drift_analysis.confidence_drift.trend === 'positive' ? 'Improving' : 'Declining'} AI confidence over time ({safeToFixed(driftData.drift_analysis.confidence_drift.drift_percentage)}% change)</div>
                <div>• <strong>Output Consistency:</strong> {driftData.drift_analysis.output_consistency.consistency_percentage >= 80 ? 'High' : 'Moderate'} consistency in analysis outputs ({driftData.drift_analysis.output_consistency.consistency_percentage}%)</div>
                <div>• <strong>Quality Drift:</strong> Average quality score of {safeToFixed(driftData.drift_analysis.quality_drift.avg_quality_score)}% across {driftData.drift_analysis.quality_drift.total_analyses} analyses</div>
                <div>• <strong>Coverage Drift:</strong> SLIs: {safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.slis?.percentage_change)}%, SLOs: {safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.slos?.percentage_change)}%, Alerts: {safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.alerts?.percentage_change)}%, Suggestions: {safeToFixed(driftData.drift_analysis.coverage_drift.coverage_trends?.suggestions?.percentage_change)}%</div>
              </div>
            </div>
            
            {/* AI Suggestions */}
            {driftData.suggestions && (
              <div className="mt-6 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-medium text-purple-800">AI-Powered Suggestions</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-purple-600">AI Confidence:</span>
                    <span className="text-sm font-medium text-purple-800">
                      {typeof driftData.suggestions.ai_confidence === 'number' 
                        ? (driftData.suggestions.ai_confidence * 100).toFixed(1) + '%' 
                        : 'N/A'}
                    </span>
                  </div>
                </div>
                
                {driftData.suggestions.explanation && (
                  <div className="mb-4 p-3 bg-white bg-opacity-50 rounded-lg">
                    <p className="text-sm text-purple-700">{driftData.suggestions.explanation}</p>
                  </div>
                )}
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Priority Actions */}
                  {driftData.suggestions.priority_actions && driftData.suggestions.priority_actions.length > 0 && (
                    <div>
                      <h5 className="text-sm font-semibold text-purple-800 mb-3 flex items-center">
                        <span className="mr-2">🎯</span>
                        Priority Actions
                      </h5>
                      <ul className="space-y-2">
                        {driftData.suggestions.priority_actions.map((action: string, index: number) => (
                          <li key={index} className="flex items-start">
                            <span className="text-purple-500 mr-2 mt-1">•</span>
                            <span className="text-sm text-purple-700">{action}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Improvement Areas */}
                  {driftData.suggestions.improvement_areas && driftData.suggestions.improvement_areas.length > 0 && (
                    <div>
                      <h5 className="text-sm font-semibold text-purple-800 mb-3 flex items-center">
                        <span className="mr-2">🔧</span>
                        Improvement Areas
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {driftData.suggestions.improvement_areas.map((area: string, index: number) => (
                          <span key={index} className="px-3 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                            {area}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Detailed Suggestions */}
                {driftData.suggestions.suggestions && driftData.suggestions.suggestions.length > 0 && (
                  <div className="mt-6">
                    <h5 className="text-sm font-semibold text-purple-800 mb-3 flex items-center">
                      <span className="mr-2">💡</span>
                      Detailed Suggestions
                    </h5>
                    <div className="space-y-3">
                      {driftData.suggestions.suggestions.map((suggestion: string, index: number) => (
                        <div key={index} className="p-3 bg-white bg-opacity-50 rounded-lg border-l-4 border-purple-300">
                          <p className="text-sm text-purple-700">{suggestion}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Root Causes */}
                {driftData.suggestions.root_causes && driftData.suggestions.root_causes.length > 0 && (
                  <div className="mt-6">
                    <h5 className="text-sm font-semibold text-purple-800 mb-3 flex items-center">
                      <span className="mr-2">🔍</span>
                      Root Cause Analysis
                    </h5>
                    <ul className="space-y-2">
                      {driftData.suggestions.root_causes.map((cause: string, index: number) => (
                        <li key={index} className="flex items-start">
                          <span className="text-purple-500 mr-2 mt-1">•</span>
                          <span className="text-sm text-purple-700">{cause}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Success Metrics */}
                {driftData.suggestions.success_metrics && driftData.suggestions.success_metrics.length > 0 && (
                  <div className="mt-6">
                    <h5 className="text-sm font-semibold text-purple-800 mb-3 flex items-center">
                      <span className="mr-2">📊</span>
                      Success Metrics
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {driftData.suggestions.success_metrics.map((metric: string, index: number) => (
                        <span key={index} className="px-3 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                          {metric}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confidence Trend Analysis */}
      {confidenceTrend && (
        <div className="mb-6 bg-white rounded-lg shadow">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Confidence Trend Analysis</h3>
            <div className="bg-gray-100 rounded-lg p-4 max-h-96 overflow-y-auto">
              <JSONTree 
                data={confidenceTrend} 
                theme="tomorrow"
                shouldExpandNode={() => true}
                shouldExpandNodeInitially={() => false}
              />
            </div>
          </div>
        </div>
      )}

      {/* SLI Evolution Analysis */}
      {sliEvolution && (
        <div className="mb-6 bg-white rounded-lg shadow">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">SLI Evolution Analysis</h3>
            <div className="bg-gray-100 rounded-lg p-4 max-h-96 overflow-y-auto">
              <JSONTree 
                data={sliEvolution} 
                theme="tomorrow"
                shouldExpandNode={() => true}
                shouldExpandNodeInitially={() => false}
              />
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
