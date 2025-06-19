'use client';
import PageContainer from '@/components/layout/PageContainer';
import React, { useState, useEffect } from 'react';
import { JSONTree } from 'react-json-tree';
import Link from 'next/link';

export default function PoliciesPage() {
  const [activeTab, setActiveTab] = useState('generate');
  const [loading, setLoading] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  
  // Policy Generation State
  const [policyInput, setPolicyInput] = useState('');
  const [policyType, setPolicyType] = useState('rego');
  const [model, setModel] = useState('llama2');
  const [temperature, setTemperature] = useState(0.3);
  
  // Policy Validation State
  const [infraData, setInfraData] = useState('');
  const [policyPath, setPolicyPath] = useState('');
  const [validationResult, setValidationResult] = useState<any>(null);
  
  // Policy Testing State
  const [testData, setTestData] = useState('');
  const [testPolicyPath, setTestPolicyPath] = useState('');
  const [testResult, setTestResult] = useState<any>(null);
  
  // Templates State
  const [templates, setTemplates] = useState<any>(null);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedTemplateIndex, setSelectedTemplateIndex] = useState(0);
  
  // LLM Suggestions State
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState<any>(null);
  const [suggestionPolicyType, setSuggestionPolicyType] = useState('rego');
  const [suggestionModel, setSuggestionModel] = useState('llama2');
  const [suggestionTemperature, setSuggestionTemperature] = useState(0.3);
  const [suggestionFilters, setSuggestionFilters] = useState({
    service_name: '',
    category: ''
  });
  
  // Available Models
  const availableModels = [
    'llama2',
    'llama3.2:1b',
    'phi3:mini',
    'qwen2.5:7b',
    'mistral:7b'
  ];

  // Sample Infrastructure Data
  const sampleInfraData = {
    "s3_buckets": [
      {
        "name": "my-bucket",
        "encryption": {
          "enabled": false,
          "algorithm": null
        },
        "versioning": {
          "enabled": false
        },
        "public_access": {
          "block_all": false
        }
      }
    ],
    "iam_users": [
      {
        "name": "test-user",
        "mfa_enabled": false,
        "access_keys": 2
      }
    ]
  };

  // Sample Test Data
  const sampleTestData = {
    "valid_configuration": {
      "s3_bucket": {
        "name": "compliant-bucket",
        "encryption": {
          "enabled": true,
          "algorithm": "AES256"
        },
        "versioning": {
          "enabled": true
        }
      }
    },
    "invalid_configuration": {
      "s3_bucket": {
        "name": "non-compliant-bucket",
        "encryption": {
          "enabled": false
        },
        "versioning": {
          "enabled": false
        }
      }
    }
  };

  useEffect(() => {
    fetchTemplates();
    fetchSuggestions();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/v1/policies/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || {});
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const params = new URLSearchParams();
      if (suggestionFilters.service_name) {
        params.append('service_name', suggestionFilters.service_name);
      }
      if (suggestionFilters.category) {
        params.append('category', suggestionFilters.category);
      }
      
      const response = await fetch(`/api/v1/policies/suggestions?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const generateSuggestions = async () => {
    setLoading('suggestions');
    try {
      const response = await fetch('/api/v1/policies/generate-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_name: suggestionFilters.service_name || undefined,
          category: suggestionFilters.category || undefined,
          model: 'llama2',
          temperature: 0.3
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      } else {
        const error = await response.json();
        console.error('Failed to generate suggestions:', error);
      }
    } catch (error) {
      console.error('Error generating suggestions:', error);
    } finally {
      setLoading(null);
    }
  };

  const generatePolicy = async () => {
    if (!policyInput.trim()) {
      alert('Please enter a policy description');
      return;
    }

    setLoading('generate');
    setResult(null);

    try {
      const response = await fetch('/api/v1/policies/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: policyInput,
          policy_type: policyType,
          model,
          temperature,
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const error = await response.json();
        setResult({ error: error.detail || 'Failed to generate policy' });
      }
    } catch (error) {
      setResult({ error: `Error: ${error}` });
    } finally {
      setLoading(null);
    }
  };

  const validatePolicy = async () => {
    if (!infraData.trim() || !policyPath.trim()) {
      alert('Please provide both infrastructure data and policy path');
      return;
    }

    setLoading('validate');
    setValidationResult(null);

    try {
      const response = await fetch('/api/v1/policies/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          infra: infraData,
          policy: policyPath,
          policy_type: policyType
        })
      });

      if (response.ok) {
        const data = await response.json();
        setValidationResult(data);
      } else {
        const error = await response.json();
        setValidationResult({ error: error.detail || 'Failed to validate policy' });
      }
    } catch (error) {
      setValidationResult({ error: `Error: ${error}` });
    } finally {
      setLoading(null);
    }
  };

  const testPolicy = async () => {
    if (!testData.trim() || !testPolicyPath.trim()) {
      alert('Please provide both test data and policy path');
      return;
    }

    setLoading('test');
    setTestResult(null);

    try {
      const response = await fetch('/api/v1/policies/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          policy: testPolicyPath,
          test_data: testData,
          policy_type: policyType
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTestResult(data);
      } else {
        const error = await response.json();
        setTestResult({ error: error.detail || 'Failed to test policy' });
      }
    } catch (error) {
      setTestResult({ error: `Error: ${error}` });
    } finally {
      setLoading(null);
    }
  };

  const createFromTemplate = async () => {
    if (!selectedTemplate) {
      alert('Please select a template');
      return;
    }

    setLoading('template');
    setResult(null);

    try {
      const response = await fetch('/api/v1/policies/create-from-template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_name: selectedTemplate,
          template_index: selectedTemplateIndex,
          output: `output/${selectedTemplate}_policy_${Date.now()}.rego`
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const error = await response.json();
        setResult({ error: error.detail || 'Failed to create policy from template' });
      }
    } catch (error) {
      setResult({ error: `Error: ${error}` });
    } finally {
      setLoading(null);
    }
  };

  const createPolicyFromSuggestion = async () => {
    if (!selectedSuggestion) {
      alert('Please select a suggestion first');
      return;
    }

    setLoading('suggestion');
    setResult(null);

    try {
      const response = await fetch('/api/v1/policies/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: selectedSuggestion.description,
          policy_type: suggestionPolicyType,
          model: suggestionModel,
          temperature: suggestionTemperature,
          name: `Policy_${selectedSuggestion.title.replace(/\s+/g, '_')}`,
          additional_context: selectedSuggestion.rationale
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const error = await response.json();
        setResult({ error: error.detail || 'Failed to create policy from suggestion' });
      }
    } catch (error) {
      setResult({ error: `Error: ${error}` });
    } finally {
      setLoading(null);
    }
  };

  const loadSampleData = (type: 'infra' | 'test') => {
    if (type === 'infra') {
      setInfraData(JSON.stringify(sampleInfraData, null, 2));
    } else {
      setTestData(JSON.stringify(sampleTestData, null, 2));
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category?.toLowerCase()) {
      case 'risk': return 'text-red-600 bg-red-50';
      case 'coverage': return 'text-blue-600 bg-blue-50';
      case 'optimization': return 'text-green-600 bg-green-50';
      case 'best_practice': return 'text-purple-600 bg-purple-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <PageContainer title="Policy Management">
      {/* Navigation to Policy History */}
      <div className="mb-4">
        <Link 
          href="/policies/history"
          className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          📋 View Policy History
        </Link>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'generate', name: 'Generate Policy', icon: '🔧' },
              { id: 'validate', name: 'Validate Policy', icon: '✅' },
              { id: 'test', name: 'Test Policy', icon: '🧪' },
              { id: 'templates', name: 'Templates', icon: '📋' },
              { id: 'suggestions', name: 'LLM Suggestions', icon: '💡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon} {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Policy Generation Tab */}
      {activeTab === 'generate' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Generate Policy from Description</h3>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="policy-description" className="block text-sm font-medium text-gray-700 mb-2">
                  Policy Description (Plain English)
                </label>
                <textarea
                  id="policy-description"
                  name="policy-description"
                  value={policyInput}
                  onChange={(e) => setPolicyInput(e.target.value)}
                  placeholder="e.g., Ensure all S3 buckets have encryption enabled"
                  className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label htmlFor="policy-type" className="block text-sm font-medium text-gray-700 mb-2">Policy Type</label>
                  <select
                    id="policy-type"
                    name="policy-type"
                    value={policyType}
                    onChange={(e) => setPolicyType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="rego">Rego (OPA)</option>
                    <option value="yaml">YAML</option>
                    <option value="json">JSON</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="policy-model" className="block text-sm font-medium text-gray-700 mb-2">Model</label>
                  <select
                    id="policy-model"
                    name="policy-model"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    {availableModels.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="policy-temperature" className="block text-sm font-medium text-gray-700 mb-2">
                    Temperature: {temperature}
                  </label>
                  <input
                    id="policy-temperature"
                    name="policy-temperature"
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>

              <button
                onClick={generatePolicy}
                disabled={loading !== null}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading === 'generate' ? 'Generating...' : 'Generate Policy'}
              </button>
            </div>
          </div>

          {result && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Generated Policy</h3>
              {result.error ? (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="text-red-800">
                    {typeof result.error === 'string' 
                      ? result.error 
                      : JSON.stringify(result.error, null, 2)
                    }
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-md p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Policy Content</h4>
                    <div className="max-h-96 overflow-y-auto border border-gray-200 rounded">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap p-4 m-0">
                        {result.policy_content}
                      </pre>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div className="md:col-span-2 lg:col-span-1">
                      <span className="text-gray-500">File:</span>
                      <div className="font-medium break-all text-xs">{result.policy_path}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Size:</span>
                      <div className="font-medium">{result.metadata?.file_size} chars</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Model:</span>
                      <div className="font-medium">{result.metadata?.model}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Type:</span>
                      <div className="font-medium">{result.metadata?.policy_type}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Policy Validation Tab */}
      {activeTab === 'validate' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Validate Infrastructure Against Policy</h3>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="infra-data" className="block text-sm font-medium text-gray-700 mb-2">
                  Infrastructure Data (JSON)
                </label>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-gray-500">Paste JSON infrastructure data or use sample</span>
                  <button
                    type="button"
                    onClick={() => loadSampleData('infra')}
                    className="text-xs text-indigo-600 hover:text-indigo-800"
                  >
                    Load Sample
                  </button>
                </div>
                <textarea
                  id="infra-data"
                  name="infra-data"
                  value={infraData}
                  onChange={(e) => setInfraData(e.target.value)}
                  placeholder="Paste JSON infrastructure data here..."
                  className="w-full h-48 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                />
              </div>

              <div>
                <label htmlFor="policy-path" className="block text-sm font-medium text-gray-700 mb-2">Policy File Path</label>
                <input
                  id="policy-path"
                  name="policy-path"
                  type="text"
                  value={policyPath}
                  onChange={(e) => setPolicyPath(e.target.value)}
                  placeholder="e.g., output/generated_policy.rego"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="validate-policy-type" className="block text-sm font-medium text-gray-700 mb-2">Policy Type</label>
                <select
                  id="validate-policy-type"
                  name="validate-policy-type"
                  value={policyType}
                  onChange={(e) => setPolicyType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="rego">Rego (OPA)</option>
                  <option value="yaml">YAML</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <button
                onClick={validatePolicy}
                disabled={loading !== null}
                className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                {loading === 'validate' ? 'Validating...' : 'Validate Policy'}
              </button>
            </div>
          </div>

          {validationResult && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Validation Results</h3>
              {validationResult.error ? (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="text-red-800">
                    {typeof validationResult.error === 'string' 
                      ? validationResult.error 
                      : JSON.stringify(validationResult.error, null, 2)
                    }
                  </div>
                </div>
              ) : (
                <div>
                  {validationResult.violations && validationResult.violations.length > 0 ? (
                    <div className="space-y-4">
                      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                        <div className="text-yellow-800 font-medium">
                          Found {validationResult.violations.length} violation(s)
                        </div>
                      </div>
                      <div className="space-y-2">
                        {validationResult.violations.map((violation: any, index: number) => (
                          <div key={index} className="border border-gray-200 rounded-md p-3">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-gray-900">{violation.resource}</span>
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                violation.severity === 'high' ? 'bg-red-100 text-red-800' :
                                violation.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-blue-100 text-blue-800'
                              }`}>
                                {violation.severity}
                              </span>
                            </div>
                            <div className="text-sm text-gray-600 mt-1">{violation.message}</div>
                            <div className="text-xs text-gray-500 mt-1">Rule: {violation.rule}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-green-50 border border-green-200 rounded-md p-4">
                      <div className="text-green-800 font-medium">
                        ✅ No violations found - infrastructure complies with policy
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Policy Testing Tab */}
      {activeTab === 'test' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Test Policy Against Sample Data</h3>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="test-data" className="block text-sm font-medium text-gray-700 mb-2">
                  Test Data (JSON)
                </label>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-gray-500">Paste JSON test data or use sample</span>
                  <button
                    type="button"
                    onClick={() => loadSampleData('test')}
                    className="text-xs text-indigo-600 hover:text-indigo-800"
                  >
                    Load Sample
                  </button>
                </div>
                <textarea
                  id="test-data"
                  name="test-data"
                  value={testData}
                  onChange={(e) => setTestData(e.target.value)}
                  placeholder="Paste JSON test data here..."
                  className="w-full h-48 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                />
              </div>

              <div>
                <label htmlFor="test-policy-path" className="block text-sm font-medium text-gray-700 mb-2">Policy File Path</label>
                <input
                  id="test-policy-path"
                  name="test-policy-path"
                  type="text"
                  value={testPolicyPath}
                  onChange={(e) => setTestPolicyPath(e.target.value)}
                  placeholder="e.g., output/generated_policy.rego"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="test-policy-type" className="block text-sm font-medium text-gray-700 mb-2">Policy Type</label>
                <select
                  id="test-policy-type"
                  name="test-policy-type"
                  value={policyType}
                  onChange={(e) => setPolicyType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="rego">Rego (OPA)</option>
                  <option value="yaml">YAML</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <button
                onClick={testPolicy}
                disabled={loading !== null}
                className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
              >
                {loading === 'test' ? 'Testing...' : 'Test Policy'}
              </button>
            </div>
          </div>

          {testResult && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Test Results</h3>
              {testResult.error ? (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="text-red-800">
                    {typeof testResult.error === 'string' 
                      ? testResult.error 
                      : JSON.stringify(testResult.error, null, 2)
                    }
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-50 rounded-md p-3 text-center">
                      <div className="text-2xl font-bold text-gray-900">{testResult.summary?.total_tests}</div>
                      <div className="text-sm text-gray-600">Total Tests</div>
                    </div>
                    <div className="bg-green-50 rounded-md p-3 text-center">
                      <div className="text-2xl font-bold text-green-600">{testResult.summary?.passed}</div>
                      <div className="text-sm text-green-600">Passed</div>
                    </div>
                    <div className="bg-red-50 rounded-md p-3 text-center">
                      <div className="text-2xl font-bold text-red-600">{testResult.summary?.failed}</div>
                      <div className="text-sm text-red-600">Failed</div>
                    </div>
                    <div className="bg-blue-50 rounded-md p-3 text-center">
                      <div className="text-2xl font-bold text-blue-600">{testResult.summary?.success_rate}%</div>
                      <div className="text-sm text-blue-600">Success Rate</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {testResult.results?.map((result: any, index: number) => (
                      <div key={index} className={`border rounded-md p-3 ${
                        result.status === 'pass' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                      }`}>
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-gray-900">{result.test_case}</span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            result.status === 'pass' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {result.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">{result.message}</div>
                        {result.violations && (
                          <div className="mt-2">
                            <div className="text-xs font-medium text-gray-700 mb-1">Violations:</div>
                            {result.violations.map((violation: any, vIndex: number) => (
                              <div key={vIndex} className="text-xs text-gray-600 ml-2">
                                • {violation.message}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Policy Templates</h3>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="template-category" className="block text-sm font-medium text-gray-700 mb-2">Template Category</label>
                  <select
                    id="template-category"
                    name="template-category"
                    value={selectedTemplate}
                    onChange={(e) => {
                      setSelectedTemplate(e.target.value);
                      setSelectedTemplateIndex(0);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select a template category</option>
                    {templates && Object.keys(templates).map(key => (
                      <option key={key} value={key}>{templates[key].name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="template-index" className="block text-sm font-medium text-gray-700 mb-2">Template</label>
                  <select
                    id="template-index"
                    name="template-index"
                    value={selectedTemplateIndex}
                    onChange={(e) => setSelectedTemplateIndex(parseInt(e.target.value))}
                    disabled={!selectedTemplate}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 disabled:opacity-50"
                  >
                    {selectedTemplate && templates && templates[selectedTemplate]?.templates.map((template: string, index: number) => (
                      <option key={index} value={index}>{template}</option>
                    ))}
                  </select>
                </div>
              </div>

              {selectedTemplate && templates && (
                <div className="bg-gray-50 rounded-md p-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Template</h4>
                  <div className="text-sm text-gray-800">
                    {templates[selectedTemplate].templates[selectedTemplateIndex]}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {templates[selectedTemplate].description}
                  </div>
                </div>
              )}

              <button
                onClick={createFromTemplate}
                disabled={loading !== null || !selectedTemplate}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading === 'template' ? 'Creating...' : 'Create Policy from Template'}
              </button>
            </div>
          </div>

          {templates && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Available Templates</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(templates).map(([key, template]: [string, any]) => (
                  <div key={key} className="border border-gray-200 rounded-md p-4">
                    <h4 className="font-medium text-gray-900 mb-2">{template.name}</h4>
                    <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                    <div className="space-y-1">
                      {template.templates.map((policy: string, index: number) => (
                        <div key={index} className="text-xs text-gray-700 bg-gray-50 p-2 rounded">
                          {index}: {policy}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Generated Policy from Template</h3>
              {result.error ? (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="text-red-800">
                    {typeof result.error === 'string' 
                      ? result.error 
                      : JSON.stringify(result.error, null, 2)
                    }
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-md p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Policy Content</h4>
                    <div className="max-h-96 overflow-y-auto border border-gray-200 rounded">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap p-4 m-0">
                        {result.policy_content}
                      </pre>
                    </div>
                  </div>
                  <div className="text-sm text-gray-600">
                    Generated: {result.policy_path}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* LLM Suggestions Tab */}
      {activeTab === 'suggestions' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create Policies from LLM Suggestions</h3>
            
            <div className="space-y-4">
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="service-filter" className="block text-sm font-medium text-gray-700 mb-2">Filter by Service</label>
                  <input
                    id="service-filter"
                    name="service-filter"
                    type="text"
                    value={suggestionFilters.service_name}
                    onChange={(e) => setSuggestionFilters(prev => ({ ...prev, service_name: e.target.value }))}
                    placeholder="Enter service name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label htmlFor="category-filter" className="block text-sm font-medium text-gray-700 mb-2">Filter by Category</label>
                  <select
                    id="category-filter"
                    name="category-filter"
                    value={suggestionFilters.category}
                    onChange={(e) => setSuggestionFilters(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">All Categories</option>
                    <option value="risk">Risk</option>
                    <option value="coverage">Coverage</option>
                    <option value="optimization">Optimization</option>
                    <option value="best_practice">Best Practice</option>
                  </select>
                </div>
              </div>

              <button
                onClick={generateSuggestions}
                disabled={loading === 'suggestions'}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading === 'suggestions' ? 'Generating...' : 'Generate New Suggestions'}
              </button>

              <button
                onClick={fetchSuggestions}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Refresh Suggestions
              </button>
            </div>
          </div>

          {/* Suggestions List */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Available Suggestions ({suggestions.length})</h3>
            
            <div className="space-y-4">
              {suggestions.map((suggestion, index) => (
                <div
                  key={`${suggestion.llm_output_id || index}-${suggestion.suggestion_index || index}`}
                  className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedSuggestion?.title === suggestion.title
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedSuggestion(suggestion)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getCategoryColor(suggestion.category)}`}>
                        {suggestion.category}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(suggestion.priority)}`}>
                        {suggestion.priority}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">
                      {suggestion.created_at ? new Date(suggestion.created_at).toLocaleDateString() : 'Recent'}
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <div className="text-sm font-medium text-gray-900">{suggestion.title}</div>
                    <div className="text-sm text-gray-600">{suggestion.description}</div>
                  </div>
                  
                  <div className="text-sm text-gray-700 mb-2">
                    {suggestion.rationale}
                  </div>
                  
                  {suggestion.examples && suggestion.examples.length > 0 && (
                    <div className="text-sm text-gray-600 mb-2">
                      <strong>Examples:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {suggestion.examples.map((example, i) => (
                          <li key={i}>{example}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center space-x-4">
                      <span>Effort: {suggestion.effort}</span>
                      <span>Impact: {suggestion.impact}</span>
                    </div>
                  </div>
                </div>
              ))}
              
              {suggestions.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No suggestions found. Try adjusting your filters or run the 5-step analysis first.
                </div>
              )}
            </div>
          </div>

          {/* Policy Generation from Selected Suggestion */}
          {selectedSuggestion && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Policy from Selected Suggestion</h3>
              
              <div className="bg-gray-50 rounded-md p-4 mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Suggestion</h4>
                <div className="text-sm text-gray-800 mb-2">
                  <strong>Title:</strong> {selectedSuggestion.title}
                </div>
                <div className="text-sm text-gray-800 mb-2">
                  <strong>Category:</strong> {selectedSuggestion.category}
                </div>
                <div className="text-sm text-gray-800 mb-2">
                  <strong>Description:</strong> {selectedSuggestion.description}
                </div>
                <div className="text-sm text-gray-800">
                  <strong>Rationale:</strong> {selectedSuggestion.rationale}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label htmlFor="suggestion-policy-type" className="block text-sm font-medium text-gray-700 mb-2">Policy Type</label>
                  <select
                    id="suggestion-policy-type"
                    name="suggestion-policy-type"
                    value={suggestionPolicyType}
                    onChange={(e) => setSuggestionPolicyType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="rego">Rego (OPA)</option>
                    <option value="yaml">YAML</option>
                    <option value="json">JSON</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="suggestion-model" className="block text-sm font-medium text-gray-700 mb-2">Model</label>
                  <select
                    id="suggestion-model"
                    name="suggestion-model"
                    value={suggestionModel}
                    onChange={(e) => setSuggestionModel(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    {availableModels.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="suggestion-temperature" className="block text-sm font-medium text-gray-700 mb-2">
                    Temperature: {suggestionTemperature}
                  </label>
                  <input
                    id="suggestion-temperature"
                    name="suggestion-temperature"
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={suggestionTemperature}
                    onChange={(e) => setSuggestionTemperature(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>

              <button
                onClick={createPolicyFromSuggestion}
                disabled={loading !== null}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading === 'suggestion' ? 'Creating Policy...' : 'Create Policy from Suggestion'}
              </button>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Generated Policy from Suggestion</h3>
              {result.error ? (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="text-red-800">
                    {typeof result.error === 'string' 
                      ? result.error 
                      : JSON.stringify(result.error, null, 2)
                    }
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-md p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Policy Content</h4>
                    <div className="max-h-96 overflow-y-auto border border-gray-200 rounded">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap p-4 m-0">
                        {result.policy_content}
                      </pre>
                    </div>
                  </div>
                  <div className="text-sm text-gray-600">
                    Generated: {result.policy_path}
                  </div>
                  {result.metadata && (
                    <div className="bg-blue-50 rounded-md p-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Metadata</h4>
                      <JSONTree data={result.metadata} />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </PageContainer>
  );
} 