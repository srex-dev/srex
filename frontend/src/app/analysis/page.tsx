'use client';
import PageContainer from '@/components/layout/PageContainer';
import React, { useState, useEffect } from 'react';
import { JSONTree } from 'react-json-tree';

export default function AnalysisPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [selectedTask, setSelectedTask] = useState('default');
  const [timeframe, setTimeframe] = useState('5min');
  const [use5Step, setUse5Step] = useState(false);
  const [model, setModel] = useState('llama3.2:1b');
  const [temperature, setTemperature] = useState(0.3);
  const [methodUsed, setMethodUsed] = useState<string>('');
  const [serviceName, setServiceName] = useState('service');
  const [availableComponents, setAvailableComponents] = useState<string[]>([]);
  const [loadingComponents, setLoadingComponents] = useState(false);
  const [showStepDetails, setShowStepDetails] = useState(false);
  const [useLangChain, setUseLangChain] = useState(false);
  const [sliQuantity, setSliQuantity] = useState(5);
  const [sloQuantity, setSloQuantity] = useState(3);
  const [alertQuantity, setAlertQuantity] = useState(3);
  const [suggestionQuantity, setSuggestionQuantity] = useState(5);

  // Fetch available components from backend
  useEffect(() => {
    const fetchComponents = async () => {
      setLoadingComponents(true);
      try {
        const response = await fetch('/api/llm/components');
        if (response.ok) {
          const components = await response.json();
          console.log('Fetched components:', components);
          console.log('Current serviceName:', serviceName);
          setAvailableComponents(components);
          // Set first component as default if available
          if (components.length > 0 && !components.includes(serviceName)) {
            console.log('Setting serviceName to first component:', components[0]);
            setServiceName(components[0]);
          } else {
            console.log('Not changing serviceName, condition not met');
          }
        } else {
          console.warn('Failed to fetch components, using default');
          setAvailableComponents(['service', 'user-service', 'payment-gateway']); // fallback
        }
      } catch (error) {
        console.warn('Error fetching components:', error);
        setAvailableComponents(['service', 'user-service', 'payment-gateway']); // fallback
      } finally {
        setLoadingComponents(false);
      }
    };

    fetchComponents();
  }, []);

  const handleLLM = async (task?: string) => {
    const currentTask = task || selectedTask;
    setLoading(currentTask);
    setResult(null);
    setMethodUsed(use5Step ? '5-Step Method' : 'Original Method');
    
    console.log('handleLLM called with serviceName:', serviceName);
    
    const requestBody = use5Step 
      ? {
          method: "5step",
          input: { 
            service_name: serviceName,
            description: `A ${serviceName} service for observability analysis`,
            timeframe,
            sli_quantity: sliQuantity,
            slo_quantity: sloQuantity,
            alert_quantity: alertQuantity,
            suggestion_quantity: suggestionQuantity
          },
          model,
          temperature,
          provider: useLangChain ? "langchain" : "ollama"
        }
      : {
          task: currentTask,
          input: { 
            service_name: serviceName,
            timeframe,
            sli_quantity: sliQuantity,
            slo_quantity: sloQuantity,
            alert_quantity: alertQuantity,
            suggestion_quantity: suggestionQuantity
          },
          provider: useLangChain ? "langchain" : "ollama"
        };

    console.log('Request body:', requestBody);

    try {
      const endpoint = use5Step ? '/api/llm/5step' : '/api/llm';
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1800000); // 30 minute timeout
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      let output = data.output;
      
      // Handle 5-step response structure
      if (use5Step && output && output.final_data) {
        // 5-step process returns structured data
        output = {
          ...output.final_data,
          step_data: output.step_data,
          metadata: output.metadata
        };
      }
      
      // Try to parse output as JSON if it's a string
      if (typeof output === 'string') {
        try {
          output = JSON.parse(output);
        } catch {
          // leave as string if not JSON
        }
      }
      
      setResult(output);
      console.log("Set LLM result:", output);
    } catch (error) {
      console.error("Error calling LLM:", error);
      setResult({ error: `Failed to generate: ${error}` });
    } finally {
      setLoading(null);
    }
  };

  // Helper to download the result as a .txt file
  const downloadResult = () => {
    if (!result) return;
    const blob = new Blob([
      typeof result === 'string' ? result : JSON.stringify(result, null, 2)
    ], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `llm_output_${methodUsed.toLowerCase().replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Helper to get result summary
  const getResultSummary = () => {
    if (!result || typeof result === 'string') return null;
    
    // Handle both old and new response formats
    const data = result.final_data || result;
    
    const summary = {
      slis: data.sli?.length || 0,
      slos: data.slo?.length || 0,
      alerts: data.alerts?.length || 0,
      suggestions: data.llm_suggestions?.length || 0,
      hasValidation: !!data.validation_summary,
      method: methodUsed
    };
    
    return summary;
  };

  const resultSummary = getResultSummary();

  return (
    <PageContainer title="System Analysis">
      {/* Method Selection */}
      <div className="mb-6">
        <div className="flex items-center space-x-4 mb-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="method"
              checked={!use5Step}
              onChange={() => setUse5Step(false)}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">Original Method</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="method"
              checked={use5Step}
              onChange={() => setUse5Step(true)}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">5-Step Method</span>
          </label>
        </div>
        
        {use5Step && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
            <h3 className="text-sm font-medium text-blue-800 mb-2">5-Step LLM Process</h3>
            <p className="text-sm text-blue-700 mb-3">
              Uses 5 focused LLM calls for better quality and reliability:
            </p>
            <ol className="text-sm text-blue-700 list-decimal list-inside space-y-1">
              <li>SLI Discovery & Validation</li>
              <li>SLO Generation</li>
              <li>Alert Rule Creation</li>
              <li>Analysis & Recommendations</li>
              <li>Validation & Integration</li>
            </ol>
          </div>
        )}
      </div>

      {/* Provider Selection */}
      <div className="mb-6">
        <div className="flex items-center space-x-4 mb-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="provider"
              checked={!useLangChain}
              onChange={() => setUseLangChain(false)}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">Custom Provider</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="provider"
              checked={useLangChain}
              onChange={() => setUseLangChain(true)}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">LangChain Provider</span>
          </label>
        </div>
        
        {useLangChain && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-4">
            <h3 className="text-sm font-medium text-green-800 mb-2">LangChain Provider</h3>
            <p className="text-sm text-green-700 mb-3">
              Uses LangChain framework for enhanced features:
            </p>
            <ul className="text-sm text-green-700 list-disc list-inside space-y-1">
              <li>Advanced prompt management</li>
              <li>Built-in retry logic</li>
              <li>Output parsing</li>
              <li>Memory management</li>
              <li>Chain composition</li>
            </ul>
          </div>
        )}
      </div>

      {/* LLM Model & Speed Settings */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">LLM Model & Speed Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="model-select" className="block text-sm font-medium text-gray-700 mb-2">Model Selection</label>
            <select
              id="model-select"
              value={model}
              onChange={e => setModel(e.target.value)}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            >
              <optgroup label="Fast Models (Recommended)">
                <option value="llama3.2:1b">Llama3.2 1B - Very Fast</option>
                <option value="phi3:mini">Phi3 Mini - Fast & Reliable</option>
                <option value="qwen2.5:7b">Qwen2.5 7B - Fast & High Quality</option>
                <option value="mistral:7b">Mistral 7B - Fast & Stable</option>
              </optgroup>
              <optgroup label="Standard Models">
                <option value="llama2">Llama2 - Balanced</option>
                <option value="llama2:7b">Llama2 7B - Standard</option>
                <option value="codellama">CodeLlama - Code Focused</option>
              </optgroup>
              <optgroup label="High Quality (Slower)">
                <option value="llama2:13b">Llama2 13B - High Quality</option>
                <option value="llama2:70b">Llama2 70B - Best Quality</option>
              </optgroup>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Fast models (1B-7B) are 3-5x faster than larger models with similar quality for this task.
            </p>
          </div>
          
          <div>
            <label htmlFor="temperature-control" className="block text-sm font-medium text-gray-700 mb-2">
              Temperature: {temperature}
            </label>
            <input
              type="range"
              id="temperature-control"
              min="0"
              max="1"
              step="0.1"
              value={temperature}
              onChange={e => setTemperature(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0.0 (Fast)</span>
              <span>0.3 (Balanced)</span>
              <span>0.7 (Creative)</span>
              <span>1.0 (Slow)</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Lower temperature = faster, more consistent results. Higher = more creative but slower.
            </p>
          </div>
        </div>
        
        {/* Speed Recommendations */}
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-yellow-800 mb-2">🚀 Speed Recommendations</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-yellow-700">
            <div>
              <strong>Fast Mode:</strong>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li>Model: Llama3.2 1B or Phi3 Mini</li>
                <li>Temperature: 0.1-0.3</li>
                <li>Speed: 3-5x faster</li>
              </ul>
            </div>
            <div>
              <strong>Balanced Mode:</strong>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li>Model: Qwen2.5 7B or Mistral 7B</li>
                <li>Temperature: 0.3-0.5</li>
                <li>Speed: 2-3x faster</li>
              </ul>
            </div>
            <div>
              <strong>Quality Mode:</strong>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li>Model: Llama2 13B+</li>
                <li>Temperature: 0.5-0.7</li>
                <li>Speed: Standard</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Quantity Controls */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Quantity Controls</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <label htmlFor="sli-quantity" className="block text-sm font-medium text-gray-700 mb-2">
              SLI Quantity: {sliQuantity}
            </label>
            <input
              type="range"
              id="sli-quantity"
              min="1"
              max="20"
              step="1"
              value={sliQuantity}
              onChange={e => setSliQuantity(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>10</span>
              <span>20</span>
            </div>
          </div>
          
          <div>
            <label htmlFor="slo-quantity" className="block text-sm font-medium text-gray-700 mb-2">
              SLO Quantity: {sloQuantity}
            </label>
            <input
              type="range"
              id="slo-quantity"
              min="1"
              max="15"
              step="1"
              value={sloQuantity}
              onChange={e => setSloQuantity(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>8</span>
              <span>15</span>
            </div>
          </div>
          
          <div>
            <label htmlFor="alert-quantity" className="block text-sm font-medium text-gray-700 mb-2">
              Alert Quantity: {alertQuantity}
            </label>
            <input
              type="range"
              id="alert-quantity"
              min="1"
              max="10"
              step="1"
              value={alertQuantity}
              onChange={e => setAlertQuantity(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>5</span>
              <span>10</span>
            </div>
          </div>
          
          <div>
            <label htmlFor="suggestion-quantity" className="block text-sm font-medium text-gray-700 mb-2">
              Suggestion Quantity: {suggestionQuantity}
            </label>
            <input
              type="range"
              id="suggestion-quantity"
              min="1"
              max="15"
              step="1"
              value={suggestionQuantity}
              onChange={e => setSuggestionQuantity(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>8</span>
              <span>15</span>
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Adjust these sliders to control how many SLIs, SLOs, alerts, and suggestions the LLM will generate for your analysis.
        </p>
      </div>

      {/* Service Configuration */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label htmlFor="service-name" className="block text-sm font-medium text-gray-700 mb-1">
              Service Name
              {loadingComponents && <span className="ml-2 text-xs text-gray-500">(loading...)</span>}
            </label>
            <select
              id="service-name"
              value={serviceName}
              onChange={e => setServiceName(e.target.value)}
              disabled={loadingComponents}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm disabled:opacity-50"
            >
              {loadingComponents ? (
                <option>Loading services...</option>
              ) : availableComponents.length > 0 ? (
                availableComponents.map(component => (
                  <option key={component} value={component}>{component}</option>
                ))
              ) : (
                <option value="service">service (fallback)</option>
              )}
            </select>
            {availableComponents.length === 0 && !loadingComponents && (
              <p className="mt-1 text-xs text-gray-500">
                No services found in Prometheus. Using fallback options.
              </p>
            )}
          </div>
          
          <div>
            <label htmlFor="timeframe" className="block text-sm font-medium text-gray-700 mb-1">Timeframe</label>
            <select
              id="timeframe"
              value={timeframe}
              onChange={e => setTimeframe(e.target.value)}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            >
              <option value="3m">3 minutes</option>
              <option value="5min">5 minutes</option>
              <option value="30min">30 minutes</option>
              <option value="1hr">1 hour</option>
              <option value="1d">1 day</option>
              <option value="7d">7 days</option>
              <option value="30d">30 days</option>
            </select>
          </div>
        </div>
      </div>

      {/* LLM Generation Controls */}
      <div className="mb-6 flex flex-wrap gap-4 items-end">
        {!use5Step && (
          <div>
            <label htmlFor="llm-task" className="block text-sm font-medium text-gray-700 mb-1">Select Template</label>
            <select
              id="llm-task"
              value={selectedTask}
              onChange={e => setSelectedTask(e.target.value)}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            >
              <option value="default">Default</option>
              <option value="slo">SLO</option>
              <option value="sli">SLI</option>
              <option value="alerting">Alerting</option>
              <option value="availability">Availability</option>
              <option value="automation">Automation</option>
              <option value="observability">Observability</option>
              <option value="reliability">Reliability</option>
              <option value="summarize">Summary</option>
            </select>
          </div>
        )}
        
        <button
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
          onClick={() => handleLLM()}
          disabled={loading !== null}
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </div>

      {/* Quick Analysis Buttons */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Service Health</h4>
            <button
              className="w-full px-3 py-2 bg-green-100 text-green-800 rounded hover:bg-green-200 disabled:opacity-50"
              onClick={() => handleLLM('health')}
              disabled={loading !== null}
            >
              {loading === 'health' ? 'Analyzing...' : 'Analyze Health'}
            </button>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Performance</h4>
            <button
              className="w-full px-3 py-2 bg-blue-100 text-blue-800 rounded hover:bg-blue-200 disabled:opacity-50"
              onClick={() => handleLLM('performance')}
              disabled={loading !== null}
            >
              {loading === 'performance' ? 'Analyzing...' : 'Analyze Performance'}
            </button>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Security</h4>
            <button
              className="w-full px-3 py-2 bg-red-100 text-red-800 rounded hover:bg-red-200 disabled:opacity-50"
              onClick={() => handleLLM('security')}
              disabled={loading !== null}
            >
              {loading === 'security' ? 'Analyzing...' : 'Analyze Security'}
            </button>
          </div>
        </div>
      </div>

      {/* Results Display */}
      {result && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Analysis Results {methodUsed && `(${methodUsed})`}
            </h2>
            <div className="flex space-x-2">
              {result.step_data && (
                <button
                  onClick={() => setShowStepDetails(!showStepDetails)}
                  className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                >
                  {showStepDetails ? 'Hide' : 'Show'} Step Details
                </button>
              )}
              <button
                onClick={downloadResult}
                className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors"
              >
                Download Results
              </button>
            </div>
          </div>

          {/* Step-by-Step Details */}
          {showStepDetails && result.step_data && (
            <div className="mb-6 bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">5-Step Process Details</h3>
              <div className="space-y-4">
                {Object.entries(result.step_data).map(([stepKey, stepInfo]: [string, any]) => (
                  <div key={stepKey} className="bg-white rounded-md p-4 border">
                    <h4 className="text-md font-medium text-gray-800 mb-2">
                      {stepInfo.description || stepKey}
                    </h4>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Processed Data</h5>
                        <div className="bg-gray-100 rounded p-2 max-h-64 overflow-y-auto">
                          <JSONTree 
                            data={stepInfo.processed_data || stepInfo} 
                            theme="tomorrow"
                            shouldExpandNode={() => true}
                            shouldExpandNodeInitially={() => true}
                          />
                        </div>
                      </div>
                      <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Raw LLM Output</h5>
                        <div className="bg-gray-100 rounded p-2 max-h-64 overflow-y-auto">
                          <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                            {stepInfo.raw_output || 'No raw output available'}
                          </pre>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Final Results Summary */}
          {resultSummary && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Results Summary</h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{resultSummary.slis}</div>
                  <div className="text-sm text-gray-600">SLIs</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{resultSummary.slos}</div>
                  <div className="text-sm text-gray-600">SLOs</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{resultSummary.alerts}</div>
                  <div className="text-sm text-gray-600">Alerts</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{resultSummary.suggestions}</div>
                  <div className="text-sm text-gray-600">Suggestions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{resultSummary.hasValidation ? 'Yes' : 'No'}</div>
                  <div className="text-sm text-gray-600">Validation</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-600">{resultSummary.method}</div>
                  <div className="text-sm text-gray-600">Method</div>
                </div>
              </div>
            </div>
          )}

          {/* Full Results */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Complete Analysis Results</h3>
              <div className="bg-gray-100 rounded-lg p-4 max-h-96 overflow-y-auto">
                <JSONTree 
                  data={result} 
                  theme="tomorrow"
                  shouldExpandNode={() => true}
                  shouldExpandNodeInitially={() => true}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
} 