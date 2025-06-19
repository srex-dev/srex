'use client';
import PageContainer from '@/components/layout/PageContainer';
import React, { useState, useEffect } from 'react';
import { JSONTree } from 'react-json-tree';

// Utility functions
const getScoreColor = (score: number) => {
  if (score >= 90) return 'text-green-600';
  if (score >= 80) return 'text-blue-600';
  if (score >= 70) return 'text-yellow-600';
  if (score >= 60) return 'text-orange-600';
  return 'text-red-600';
};

const getGradeColor = (grade: string) => {
  switch (grade) {
    case 'A': return 'text-green-600';
    case 'B': return 'text-blue-600';
    case 'C': return 'text-yellow-600';
    case 'D': return 'text-orange-600';
    case 'F': return 'text-red-600';
    default: return 'text-gray-600';
  }
};

// Score explanation component
const ScoreExplanation = ({ title, score, details, color, children }: any) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`${color} rounded-lg p-4 text-center relative`}>
      <div className="flex items-center justify-center mb-2">
        <h4 className="text-sm font-medium">{title}</h4>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-2 text-xs bg-white bg-opacity-50 rounded-full w-5 h-5 flex items-center justify-center hover:bg-opacity-75 transition-colors"
          title="Click for detailed explanation"
        >
          {isExpanded ? '−' : '+'}
        </button>
      </div>
      <div className={`text-2xl font-bold ${getScoreColor(score)}`}>
        {score.toFixed(1)}%
      </div>
      {children}
      
      {isExpanded && (
        <div className="mt-3 p-3 bg-white bg-opacity-50 rounded text-left">
          <div className="text-xs font-medium mb-2">How this score is calculated:</div>
          <div className="text-xs space-y-1">
            {details}
          </div>
        </div>
      )}
    </div>
  );
};

export default function ScorecardPage() {
  const [scorecardData, setScorecardData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedService, setSelectedService] = useState<string>('');
  const [selectedDays, setSelectedDays] = useState<number>(30);
  const [availableServices, setAvailableServices] = useState<string[]>([]);
  const [showOverallDetails, setShowOverallDetails] = useState(false);
  const [showConfidenceDetails, setShowConfidenceDetails] = useState(false);
  const [suggestions, setSuggestions] = useState<any>(null);
  const [generatingSuggestions, setGeneratingSuggestions] = useState(false);

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
  }, []);

  const fetchScorecard = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        days: selectedDays.toString(),
        ...(selectedService && { service_name: selectedService })
      });
      
      const response = await fetch(`/api/scorecard/overview?${params}`);
      if (response.ok) {
        const data = await response.json();
        setScorecardData(data);
        // Clear previous suggestions when new scorecard is loaded
        setSuggestions(null);
      } else {
        console.error('Failed to fetch scorecard');
      }
    } catch (error) {
      console.error('Error fetching scorecard:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSuggestions = async () => {
    if (!scorecardData) return;
    
    setGeneratingSuggestions(true);
    try {
      const response = await fetch('/api/scorecard/suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service_name: selectedService || null,
          days: selectedDays,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data);
      } else {
        console.error('Failed to generate suggestions');
      }
    } catch (error) {
      console.error('Error generating suggestions:', error);
    } finally {
      setGeneratingSuggestions(false);
    }
  };

  return (
    <PageContainer title="Scorecard">
      {/* Controls */}
      <div className="mb-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Scorecard Controls</h3>
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
              onClick={fetchScorecard}
              disabled={loading}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Generate Scorecard'}
            </button>
          </div>
        </div>
      </div>

      {/* Scorecard Results */}
      {scorecardData && (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Overall Scorecard
                <span className="ml-2 text-sm text-gray-500">
                  ({scorecardData.period.start_date} to {scorecardData.period.end_date})
                </span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Overall Grade */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 text-center relative">
                  <div className="flex items-center justify-center mb-2">
                    <h4 className="text-sm font-medium text-gray-700">Overall Grade</h4>
                    <button
                      onClick={() => setShowOverallDetails(!showOverallDetails)}
                      className="ml-2 text-xs bg-white bg-opacity-50 rounded-full w-5 h-5 flex items-center justify-center hover:bg-opacity-75 transition-colors"
                      title="Click for detailed explanation"
                    >
                      {showOverallDetails ? '−' : '+'}
                    </button>
                  </div>
                  <div className={`text-4xl font-bold ${getGradeColor(scorecardData.scorecard.grade)}`}>
                    {scorecardData.scorecard.grade}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {scorecardData.scorecard.grade_description}
                  </div>
                  <div className={`text-2xl font-bold mt-2 ${getScoreColor(scorecardData.scorecard.overall_score)}`}>
                    {scorecardData.scorecard.overall_score.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Weighted average of all metrics
                  </div>
                  
                  {showOverallDetails && (
                    <div className="mt-4 p-3 bg-white bg-opacity-50 rounded text-left">
                      <div className="text-xs font-medium mb-2">How the overall score is calculated:</div>
                      <div className="text-xs space-y-1">
                        <div>• <strong>Formula:</strong> Weighted average of all metrics</div>
                        <div>• <strong>Weights:</strong></div>
                        <div className="ml-2">
                          <div>• Completeness: 25%</div>
                          <div>• Quality: 25%</div>
                          <div>• Consistency: 20%</div>
                          <div>• Coverage: 20%</div>
                          <div>• Confidence: 10%</div>
                        </div>
                        <div className="mt-2">• <strong>Calculation:</strong></div>
                        <div className="ml-2 font-mono text-xs">
                          ({scorecardData.scorecard.completeness_score.toFixed(1)} × 0.25) +<br/>
                          ({scorecardData.scorecard.quality_score.toFixed(1)} × 0.25) +<br/>
                          ({scorecardData.scorecard.consistency_score.toFixed(1)} × 0.20) +<br/>
                          ({scorecardData.scorecard.coverage_score.toFixed(1)} × 0.20) +<br/>
                          ({scorecardData.scorecard.confidence_score.toFixed(1)} × 0.10) =<br/>
                          <strong>{scorecardData.scorecard.overall_score.toFixed(1)}%</strong>
                        </div>
                        <div className="mt-2">• <strong>Grade Thresholds:</strong></div>
                        <div className="ml-2">
                          <div>• A (90%+): Excellent</div>
                          <div>• B (80-89%): Good</div>
                          <div>• C (70-79%): Fair</div>
                          <div>• D (60-69%): Poor</div>
                          <div>• F (&lt;60%): Failing</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Total Analyses */}
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Total Analyses</h4>
                  <div className="text-3xl font-bold text-gray-900">
                    {scorecardData.total_analyses}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    in {scorecardData.period.days} days
                  </div>
                </div>
                
                {/* Period */}
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Analysis Period</h4>
                  <div className="text-lg font-medium text-gray-900">
                    {scorecardData.period.days} days
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {scorecardData.period.start_date.split('T')[0]} to {scorecardData.period.end_date.split('T')[0]}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Scores */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed Scores</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {/* Completeness */}
                <ScoreExplanation
                  title="Completeness"
                  score={scorecardData.scorecard.completeness_score}
                  color="bg-green-50"
                  details={[
                    `• Complete outputs: ${scorecardData.scorecard.breakdown.completeness.details.complete_outputs}`,
                    `• Total analyses: ${scorecardData.scorecard.breakdown.completeness.details.total_analyses}`,
                    `• Formula: (complete_outputs / total_analyses) × 100`,
                    `• Measures: All required fields present in analysis output`,
                    `• Includes: SLIs, SLOs, alerts, and suggestions`
                  ]}
                >
                  <div className="text-xs text-green-700 mt-1">
                    {scorecardData.scorecard.breakdown.completeness.details.complete_outputs} / {scorecardData.scorecard.breakdown.completeness.details.total_analyses} complete
                  </div>
                </ScoreExplanation>
                
                {/* Quality */}
                <ScoreExplanation
                  title="Quality"
                  score={scorecardData.scorecard.quality_score}
                  color="bg-blue-50"
                  details={[
                    `• Quality score: ${scorecardData.scorecard.quality_score.toFixed(1)}/100`,
                    `• Validation present: ${scorecardData.scorecard.breakdown.quality.details.validation_percentage.toFixed(1)}% of outputs`,
                    `• Structure quality: ${scorecardData.scorecard.breakdown.quality.details.quality_breakdown?.structure?.toFixed(1) || 0}%`,
                    `• Content quality: ${scorecardData.scorecard.breakdown.quality.details.quality_breakdown?.content?.toFixed(1) || 0}%`,
                    `• Total analyses: ${scorecardData.scorecard.breakdown.quality.details.total_analyses || scorecardData.total_analyses}`,
                    `• With validation: ${scorecardData.scorecard.breakdown.quality.details.validation_present || 0}`,
                    `• Formula: Average of individual quality scores (0-100)`,
                    `• Factors: Structure (40%), Content (40%), Validation (40%) or Bonus (20%)`,
                    `• Structure: Proper array types for all fields`,
                    `• Content: Non-empty arrays for all fields`,
                    `• Bonus: +20 points when both structure and content are good`
                  ]}
                >
                  <div className="text-xs text-blue-700 mt-1">
                    {scorecardData.scorecard.breakdown.quality.details.validation_percentage.toFixed(1)}% with validation
                  </div>
                </ScoreExplanation>
                
                {/* Consistency */}
                <ScoreExplanation
                  title="Consistency"
                  score={scorecardData.scorecard.consistency_score}
                  color="bg-purple-50"
                  details={[
                    `• Consistent outputs: ${scorecardData.scorecard.breakdown.consistency.details.consistent_outputs}`,
                    `• Total analyses: ${scorecardData.scorecard.breakdown.consistency.details.total_analyses}`,
                    `• Formula: (consistent_outputs / total_analyses) × 100`,
                    `• Measures: Output consistency across similar analyses`,
                    `• Checks: Field naming, structure patterns, value ranges`,
                    `• Threshold: 80% similarity for consistency`
                  ]}
                >
                  <div className="text-xs text-purple-700 mt-1">
                    {scorecardData.scorecard.breakdown.consistency.details.consistent_outputs} / {scorecardData.scorecard.breakdown.consistency.details.total_analyses} consistent
                  </div>
                </ScoreExplanation>
                
                {/* Coverage */}
                <ScoreExplanation
                  title="Coverage"
                  score={scorecardData.scorecard.coverage_score}
                  color="bg-orange-50"
                  details={[
                    `• Average SLIs: ${scorecardData.scorecard.breakdown.coverage.details.average_counts.slis.toFixed(1)}`,
                    `• Average SLOs: ${scorecardData.scorecard.breakdown.coverage.details.average_counts.slos.toFixed(1)}`,
                    `• Average alerts: ${scorecardData.scorecard.breakdown.coverage.details.average_counts.alerts?.toFixed(1) || 'N/A'}`,
                    `• Formula: Based on comprehensive coverage metrics`,
                    `• Measures: Breadth and depth of analysis output`,
                    `• Target: 5+ SLIs, 3+ SLOs, 2+ alerts per analysis`
                  ]}
                >
                  <div className="text-xs text-orange-700 mt-1">
                    Avg: {scorecardData.scorecard.breakdown.coverage.details.average_counts.slis.toFixed(1)} SLIs, {scorecardData.scorecard.breakdown.coverage.details.average_counts.slos.toFixed(1)} SLOs
                  </div>
                </ScoreExplanation>
                
                {/* Confidence */}
                <ScoreExplanation
                  title="Confidence"
                  score={scorecardData.scorecard.confidence_score}
                  color="bg-indigo-50"
                  details={[
                    `• With confidence: ${scorecardData.scorecard.breakdown.confidence.details.total_with_confidence}`,
                    `• Total analyses: ${scorecardData.total_analyses}`,
                    `• Formula: Average confidence across all analyses`,
                    `• Measures: AI model confidence in analysis results`,
                    `• Range: 0-100% confidence per analysis`,
                    `• High confidence: 80%+, Medium: 60-79%, Low: &lt;60%`
                  ]}
                >
                  <div className="text-xs text-indigo-700 mt-1">
                    {scorecardData.scorecard.breakdown.confidence.details.total_with_confidence} with confidence
                  </div>
                </ScoreExplanation>
              </div>
            </div>
          </div>

          {/* Enhanced Confidence Analysis */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">AI Confidence Analysis</h3>
                <div className="flex items-center space-x-2">
                  <div className="text-sm text-gray-500">
                    Average confidence across all analyses
                  </div>
                  <button
                    onClick={() => setShowConfidenceDetails(!showConfidenceDetails)}
                    className="text-xs bg-gray-100 hover:bg-gray-200 rounded-full w-5 h-5 flex items-center justify-center transition-colors"
                    title="Click for detailed explanation"
                  >
                    {showConfidenceDetails ? '−' : '+'}
                  </button>
                </div>
              </div>
              
              {showConfidenceDetails && (
                <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-sm font-medium text-blue-800 mb-3">How AI Confidence is Calculated:</div>
                  <div className="text-xs text-blue-700 space-y-2">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="font-medium mb-1">Confidence Sources:</div>
                        <ul className="space-y-1">
                          <li>• <strong>Direct LLM Confidence:</strong> When AI model provides confidence score</li>
                          <li>• <strong>Calculated Confidence:</strong> Based on output quality and completeness</li>
                          <li>• <strong>Structure Analysis:</strong> JSON validity and field presence</li>
                          <li>• <strong>Content Analysis:</strong> Meaningfulness and relevance of outputs</li>
                        </ul>
                      </div>
                      <div>
                        <div className="font-medium mb-1">Confidence Levels:</div>
                        <ul className="space-y-1">
                          <li>• <strong>High (80%+):</strong> Excellent reliability</li>
                          <li>• <strong>Medium (60-79%):</strong> Good reliability</li>
                          <li>• <strong>Low (&lt;60%):</strong> Poor reliability</li>
                        </ul>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-blue-300">
                      <div className="font-medium mb-1">Current Analysis:</div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        <div className="bg-white bg-opacity-50 px-2 py-1 rounded text-xs">
                          <strong>Average:</strong> {scorecardData.scorecard.confidence_score.toFixed(1)}%
                        </div>
                        <div className="bg-white bg-opacity-50 px-2 py-1 rounded text-xs">
                          <strong>High:</strong> {scorecardData.scorecard.breakdown.confidence.details.confidence_distribution?.high || 0}
                        </div>
                        <div className="bg-white bg-opacity-50 px-2 py-1 rounded text-xs">
                          <strong>Medium:</strong> {scorecardData.scorecard.breakdown.confidence.details.confidence_distribution?.medium || 0}
                        </div>
                        <div className="bg-white bg-opacity-50 px-2 py-1 rounded text-xs">
                          <strong>Low:</strong> {scorecardData.scorecard.breakdown.confidence.details.confidence_distribution?.low || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Confidence Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                {/* Average Confidence */}
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-6 text-center">
                  <h4 className="text-sm font-medium text-indigo-800 mb-2">Average Confidence</h4>
                  <div className={`text-3xl font-bold ${getScoreColor(scorecardData.scorecard.confidence_score)}`}>
                    {scorecardData.scorecard.confidence_score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-indigo-700 mt-1">
                    {scorecardData.scorecard.confidence_score >= 80 ? 'High Reliability' :
                     scorecardData.scorecard.confidence_score >= 60 ? 'Good Reliability' :
                     scorecardData.scorecard.confidence_score >= 40 ? 'Fair Reliability' :
                     'Low Reliability'}
                  </div>
                </div>
                
                {/* Confidence Distribution */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-3 text-center">Confidence Distribution</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">High (80%+)</span>
                      <span className="text-sm font-medium text-green-600">
                        {scorecardData.scorecard.breakdown.confidence.details.confidence_distribution?.high || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Medium (60-79%)</span>
                      <span className="text-sm font-medium text-yellow-600">
                        {scorecardData.scorecard.breakdown.confidence.details.confidence_distribution?.medium || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Low (&lt;60%)</span>
                      <span className="text-sm font-medium text-red-600">
                        {scorecardData.scorecard.breakdown.confidence.details.confidence_distribution?.low || 0}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Coverage Stats */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-3 text-center">Coverage</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">With Confidence</span>
                      <span className="text-sm font-medium text-indigo-600">
                        {scorecardData.scorecard.breakdown.confidence.details.total_with_confidence}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Total Analyses</span>
                      <span className="text-sm font-medium text-gray-600">
                        {scorecardData.total_analyses}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Coverage %</span>
                      <span className="text-sm font-medium text-indigo-600">
                        {scorecardData.total_analyses > 0 ? 
                          ((scorecardData.scorecard.breakdown.confidence.details.total_with_confidence / scorecardData.total_analyses) * 100).toFixed(1) : 0}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Confidence Insights */}
              <div className={`p-4 rounded-lg border ${
                scorecardData.scorecard.confidence_score >= 80 ? 'bg-green-50 border-green-200' :
                scorecardData.scorecard.confidence_score >= 60 ? 'bg-yellow-50 border-yellow-200' :
                scorecardData.scorecard.confidence_score >= 40 ? 'bg-orange-50 border-orange-200' :
                'bg-red-50 border-red-200'
              }`}>
                <div className="flex items-start">
                  <div className={`w-2 h-2 rounded-full mt-2 mr-3 flex-shrink-0 ${
                    scorecardData.scorecard.confidence_score >= 80 ? 'bg-green-500' :
                    scorecardData.scorecard.confidence_score >= 60 ? 'bg-yellow-500' :
                    scorecardData.scorecard.confidence_score >= 40 ? 'bg-orange-500' :
                    'bg-red-500'
                  }`}></div>
                  <div>
                    <div className={`text-sm font-medium ${
                      scorecardData.scorecard.confidence_score >= 80 ? 'text-green-800' :
                      scorecardData.scorecard.confidence_score >= 60 ? 'text-yellow-800' :
                      scorecardData.scorecard.confidence_score >= 40 ? 'text-orange-800' :
                      'text-red-800'
                    }`}>
                      Confidence Assessment
                    </div>
                    <div className={`text-xs mt-1 ${
                      scorecardData.scorecard.confidence_score >= 80 ? 'text-green-700' :
                      scorecardData.scorecard.confidence_score >= 60 ? 'text-yellow-700' :
                      scorecardData.scorecard.confidence_score >= 40 ? 'text-orange-700' :
                      'text-red-700'
                    }`}>
                      {scorecardData.scorecard.confidence_score >= 80 ? 
                        'Excellent confidence levels across analyses. Results are highly reliable and comprehensive.' :
                       scorecardData.scorecard.confidence_score >= 60 ? 
                        'Good confidence levels. Most analyses are reliable with minor gaps in some cases.' :
                       scorecardData.scorecard.confidence_score >= 40 ? 
                        'Fair confidence levels. Some analyses may have limitations or missing elements.' :
                        'Low confidence levels. Many analyses may be incomplete or unreliable. Consider reviewing analysis methods.'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Suggestions */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">AI-Powered Suggestions</h3>
                <button
                  onClick={generateSuggestions}
                  disabled={generatingSuggestions || !scorecardData}
                  className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {generatingSuggestions ? 'Generating...' : 'Generate Suggestions'}
                </button>
              </div>
              
              {suggestions ? (
                <div className="space-y-6">
                  {/* AI Confidence */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-medium text-blue-800">AI Confidence</div>
                      <div className="text-sm font-bold text-blue-600">
                        {(suggestions.suggestions.ai_confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  {/* Priority Actions */}
                  {suggestions.suggestions.priority_actions && suggestions.suggestions.priority_actions.length > 0 && (
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-3">Priority Actions</h4>
                      <div className="space-y-2">
                        {suggestions.suggestions.priority_actions.map((action: string, index: number) => (
                          <div key={index} className="flex items-start">
                            <div className="w-2 h-2 bg-red-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                            <div className="text-sm text-gray-700">{action}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Improvement Areas */}
                  {suggestions.suggestions.improvement_areas && suggestions.suggestions.improvement_areas.length > 0 && (
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-3">Areas for Improvement</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {suggestions.suggestions.improvement_areas.map((area: string, index: number) => (
                          <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                            <div className="text-sm font-medium text-yellow-800">{area}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Detailed Suggestions */}
                  {suggestions.suggestions.suggestions && suggestions.suggestions.suggestions.length > 0 && (
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-3">Detailed Suggestions</h4>
                      <div className="space-y-3">
                        {suggestions.suggestions.suggestions.map((suggestion: string, index: number) => (
                          <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start">
                              <div className="w-2 h-2 bg-indigo-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                              <div className="text-sm text-gray-700">{suggestion}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Root Causes */}
                  {suggestions.suggestions.root_causes && suggestions.suggestions.root_causes.length > 0 && (
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-3">Potential Root Causes</h4>
                      <div className="space-y-2">
                        {suggestions.suggestions.root_causes.map((cause: string, index: number) => (
                          <div key={index} className="flex items-start">
                            <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                            <div className="text-sm text-gray-700">{cause}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Success Metrics */}
                  {suggestions.suggestions.success_metrics && suggestions.suggestions.success_metrics.length > 0 && (
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-3">Success Metrics</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {suggestions.suggestions.success_metrics.map((metric: string, index: number) => (
                          <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                            <div className="text-sm font-medium text-green-800">{metric}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Explanation */}
                  {suggestions.suggestions.explanation && (
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                      <div className="text-sm font-medium text-indigo-800 mb-2">Analysis Summary</div>
                      <div className="text-sm text-indigo-700">{suggestions.suggestions.explanation}</div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-500 mb-4">
                    Click "Generate Suggestions" to get AI-powered recommendations based on your scorecard data.
                  </div>
                  <div className="text-xs text-gray-400">
                    Suggestions will analyze your completeness, quality, consistency, coverage, and confidence scores to provide actionable improvements.
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Raw Data */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Raw Data</h3>
              <div className="bg-gray-100 rounded-lg p-4 max-h-96 overflow-y-auto">
                <JSONTree 
                  data={scorecardData} 
                  theme="tomorrow"
                  shouldExpandNode={() => true}
                  shouldExpandNodeInitially={() => false}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
