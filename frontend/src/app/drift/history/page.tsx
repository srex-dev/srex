'use client';
import PageContainer from '@/components/layout/PageContainer';
import React, { useState, useEffect } from 'react';
import { JSONTree } from 'react-json-tree';

export default function DriftHistoryPage() {
  const [driftHistory, setDriftHistory] = useState<any>(null);
  const [loading, setLoading] = useState(false);
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
    fetchDriftHistory();
  }, []);

  const fetchDriftHistory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        days: selectedDays.toString(),
        limit: '100',
        ...(selectedService && { service_name: selectedService })
      });
      
      const response = await fetch(`/api/drift/history?${params}`);
      if (response.ok) {
        const data = await response.json();
        setDriftHistory(data);
      } else {
        console.error('Failed to fetch drift history');
      }
    } catch (error) {
      console.error('Error fetching drift history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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
    <PageContainer title="Drift History">
      {/* Controls */}
      <div className="mb-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">History Controls</h3>
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
              onClick={fetchDriftHistory}
              disabled={loading}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Load History'}
            </button>
          </div>
        </div>
      </div>

      {/* Drift History Results */}
      {driftHistory && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Drift History
              <span className="ml-2 text-sm text-gray-500">
                ({driftHistory.period.start_date} to {driftHistory.period.end_date})
              </span>
            </h3>
            
            {driftHistory.drift_history.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No drift history found for the selected criteria.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {driftHistory.drift_history.map((record: any, index: number) => (
                  <div key={record.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          Analysis #{record.id} - {formatDate(record.analysis_date)}
                        </h4>
                        <p className="text-xs text-gray-500">
                          Period: {formatDate(record.period_start)} to {formatDate(record.period_end)} 
                          ({record.period_days} days)
                          {record.service_name && ` • Service: ${record.service_name}`}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900">
                          {record.total_analyses} analyses
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {/* Confidence Drift */}
                      <div className="bg-gray-50 rounded p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-gray-700">Confidence</span>
                          <span className={`text-xs ${getDriftStatusColor(record.confidence_drift.trend)}`}>
                            {getDriftStatusIcon(record.confidence_drift.trend)}
                          </span>
                        </div>
                        <div className="text-lg font-bold text-gray-900">
                          {record.confidence_drift.recent_avg_confidence?.toFixed(1) || 'N/A'}%
                        </div>
                        <div className="text-xs text-gray-500">
                          Drift: {record.confidence_drift.drift_percentage?.toFixed(1) || 'N/A'}%
                        </div>
                      </div>
                      
                      {/* Output Consistency */}
                      <div className="bg-gray-50 rounded p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-gray-700">Consistency</span>
                          <span className="text-xs text-blue-600">📊</span>
                        </div>
                        <div className="text-lg font-bold text-gray-900">
                          {record.output_consistency.consistency_percentage.toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500">
                          {record.output_consistency.consistent_structure}/{record.output_consistency.total_analyses} consistent
                        </div>
                      </div>
                      
                      {/* Quality Drift */}
                      <div className="bg-gray-50 rounded p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-gray-700">Quality</span>
                          <span className="text-xs text-blue-600">📊</span>
                        </div>
                        <div className="text-lg font-bold text-gray-900">
                          {record.quality_drift.avg_quality_score.toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500">
                          {record.quality_drift.complete_outputs}/{record.quality_drift.total_analyses} complete
                        </div>
                      </div>
                      
                      {/* Coverage Summary */}
                      <div className="bg-gray-50 rounded p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-gray-700">Coverage</span>
                          <span className="text-xs text-green-600">📈</span>
                        </div>
                        <div className="text-lg font-bold text-gray-900">
                          SLIs: {record.coverage_drift.recent_averages.slis?.toFixed(1) || 'N/A'}
                        </div>
                        <div className="text-xs text-gray-500">
                          SLOs: {record.coverage_drift.recent_averages.slos?.toFixed(1) || 'N/A'} | 
                          Alerts: {record.coverage_drift.recent_averages.alerts?.toFixed(1) || 'N/A'}
                        </div>
                      </div>
                    </div>
                    
                    {/* Coverage Trends */}
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <div className="text-xs font-medium text-gray-700 mb-2">Coverage Trends:</div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div>
                          <span className="text-gray-600">SLIs:</span> 
                          <span className={`ml-1 ${(record.coverage_drift.coverage_trends.slis.percentage_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {record.coverage_drift.coverage_trends.slis.percentage_change?.toFixed(1) || 'N/A'}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">SLOs:</span> 
                          <span className={`ml-1 ${(record.coverage_drift.coverage_trends.slos.percentage_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {record.coverage_drift.coverage_trends.slos.percentage_change?.toFixed(1) || 'N/A'}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Alerts:</span> 
                          <span className={`ml-1 ${(record.coverage_drift.coverage_trends.alerts.percentage_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {record.coverage_drift.coverage_trends.alerts.percentage_change?.toFixed(1) || 'N/A'}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Suggestions:</span> 
                          <span className={`ml-1 ${(record.coverage_drift.coverage_trends.suggestions.percentage_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {record.coverage_drift.coverage_trends.suggestions.percentage_change?.toFixed(1) || 'N/A'}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </PageContainer>
  );
} 