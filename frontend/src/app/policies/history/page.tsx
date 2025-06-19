'use client';

import React, { useState, useEffect } from 'react';
import PageContainer from '@/components/layout/PageContainer';
import { JSONTree } from 'react-json-tree';

interface Policy {
  id: string;
  name: string;
  description: string;
  policy_type: string;
  content: string;
  file_path: string;
  model: string;
  temperature: number;
  meta: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function PolicyHistoryPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null);
  const [filters, setFilters] = useState({
    policy_type: '',
    active_only: true
  });

  useEffect(() => {
    fetchPolicies();
  }, [filters]);

  const fetchPolicies = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.policy_type) params.append('policy_type', filters.policy_type);
      if (filters.active_only !== undefined) params.append('active_only', filters.active_only.toString());

      const response = await fetch(`/api/v1/policies/list?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setPolicies(data.policies || []);
      } else {
        console.error('Failed to fetch policies');
      }
    } catch (error) {
      console.error('Error fetching policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const deletePolicy = async (policyId: string) => {
    if (!confirm('Are you sure you want to delete this policy?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/policies/${policyId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        // Remove from local state
        setPolicies(policies.filter(p => p.id !== policyId));
        if (selectedPolicy?.id === policyId) {
          setSelectedPolicy(null);
        }
      } else {
        alert('Failed to delete policy');
      }
    } catch (error) {
      console.error('Error deleting policy:', error);
      alert('Error deleting policy');
    }
  };

  const downloadPolicy = (policy: Policy) => {
    const blob = new Blob([policy.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${policy.name}.${policy.policy_type}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getPolicyTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'rego': return 'text-purple-600 bg-purple-50';
      case 'yaml': return 'text-blue-600 bg-blue-50';
      case 'json': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <PageContainer title="Policy History">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">Loading policies...</div>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer title="Policy History">
      <div className="space-y-6">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="policy-type-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Policy Type
              </label>
              <select
                id="policy-type-filter"
                value={filters.policy_type}
                onChange={(e) => setFilters(prev => ({ ...prev, policy_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">All Types</option>
                <option value="rego">Rego</option>
                <option value="yaml">YAML</option>
                <option value="json">JSON</option>
              </select>
            </div>
            <div>
              <label htmlFor="active-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                id="active-filter"
                value={filters.active_only.toString()}
                onChange={(e) => setFilters(prev => ({ ...prev, active_only: e.target.value === 'true' }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="true">Active Only</option>
                <option value="false">All Policies</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={fetchPolicies}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Policies List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Generated Policies ({policies.length})
            </h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {policies.map((policy) => (
              <div
                key={policy.id}
                className={`p-6 cursor-pointer transition-colors ${
                  selectedPolicy?.id === policy.id
                    ? 'bg-indigo-50 border-l-4 border-indigo-500'
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedPolicy(policy)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-lg font-medium text-gray-900">{policy.name}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getPolicyTypeColor(policy.policy_type)}`}>
                        {policy.policy_type.toUpperCase()}
                      </span>
                      {!policy.is_active && (
                        <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800">
                          DELETED
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{policy.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>Model: {policy.model}</span>
                      <span>Temperature: {policy.temperature}</span>
                      <span>Created: {formatDate(policy.created_at)}</span>
                      <span>Size: {policy.content.length} chars</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        downloadPolicy(policy);
                      }}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Download
                    </button>
                    {policy.is_active && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deletePolicy(policy.id);
                        }}
                        className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {policies.length === 0 && (
              <div className="p-6 text-center text-gray-500">
                No policies found. Generate some policies first!
              </div>
            )}
          </div>
        </div>

        {/* Policy Details */}
        {selectedPolicy && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Policy Details</h3>
              <button
                onClick={() => setSelectedPolicy(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Name:</span>
                  <div className="font-medium">{selectedPolicy.name}</div>
                </div>
                <div>
                  <span className="text-gray-500">Type:</span>
                  <div className="font-medium">{selectedPolicy.policy_type}</div>
                </div>
                <div>
                  <span className="text-gray-500">Model:</span>
                  <div className="font-medium">{selectedPolicy.model}</div>
                </div>
                <div>
                  <span className="text-gray-500">Temperature:</span>
                  <div className="font-medium">{selectedPolicy.temperature}</div>
                </div>
              </div>
              
              <div>
                <span className="text-gray-500">Description:</span>
                <div className="font-medium">{selectedPolicy.description}</div>
              </div>
              
              <div>
                <span className="text-gray-500">File Path:</span>
                <div className="font-medium font-mono text-sm">{selectedPolicy.file_path}</div>
              </div>
              
              <div>
                <span className="text-gray-500">Policy Content:</span>
                <div className="mt-2 bg-gray-50 rounded-md p-4">
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-x-auto">
                    {selectedPolicy.content}
                  </pre>
                </div>
              </div>
              
              {selectedPolicy.meta && (
                <div>
                  <span className="text-gray-500">Metadata:</span>
                  <div className="mt-2">
                    <JSONTree data={selectedPolicy.meta} />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
} 