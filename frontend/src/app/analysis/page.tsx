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
  const [provider, setProvider] = useState('ollama');
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
  const [showConfidenceDetails, setShowConfidenceDetails] = useState(false);
  const [models, setModels] = useState<{ value: string; label: string }[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);

  const providerModels: Record<string, { value: string; label: string }[]> = {
    ollama: [
      { value: 'llama3.2:1b', label: 'Llama3.2 1B - Very Fast' },
      { value: 'phi3:mini', label: 'Phi3 Mini - Fast & Reliable' },
      { value: 'qwen2.5:7b', label: 'Qwen2.5 7B - Fast & High Quality' },
      { value: 'mistral:7b', label: 'Mistral 7B - Fast & Stable' },
      { value: 'llama2', label: 'Llama2 - Balanced' },
      { value: 'llama2:7b', label: 'Llama2 7B - Standard' },
      { value: 'codellama', label: 'CodeLlama - Code Focused' },
      { value: 'llama2:13b', label: 'Llama2 13B - High Quality' },
      { value: 'llama2:70b', label: 'Llama2 70B - Best Quality' },
    ],
    langchain: [
      { value: 'llama3.2:1b', label: 'Llama3.2 1B (LangChain)' },
      { value: 'mistral:7b', label: 'Mistral 7B (LangChain)' },
      { value: 'llama2', label: 'Llama2 (LangChain)' },
      { value: 'llama2:13b', label: 'Llama2 13B (LangChain)' },
    ],
    openai: [
      { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
      { value: 'gpt-4', label: 'GPT-4' },
      { value: 'gpt-4o', label: 'GPT-4o' },
    ],
  };

  // Fetch models from backend when provider changes
  useEffect(() => {
    let isMounted = true;
    setModelsLoading(true);
    fetch(`/api/llm/models?provider=${provider}`)
      .then(res => res.json())
      .then(data => {
        if (!isMounted) return;
        if (data.models && Array.isArray(data.models)) {
          // Map to value/label pairs
          const mapped = data.models.map((m: string) => ({ value: m, label: m }));
          setModels(mapped);
          if (mapped.length > 0) setModel(mapped[0].value);
        } else {
          setModels([]);
        }
        setModelsLoading(false);
      })
      .catch(() => {
        if (isMounted) {
          setModels([]);
          setModelsLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, [provider]);

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
          provider
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
          provider
        };

    console.log('Request body:', requestBody);

    try {
      const endpoint = use5Step ? '/api/llm/5step' : '/api/llm/generate';
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
        // Try to get error details from response
        let errorMessage = `HTTP error! status: ${res.status}`;
        try {
          const errorData = await res.json();
          if (errorData.error) {
            errorMessage = errorData.error;
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // If we can't parse the error response, use the status text
          errorMessage = `HTTP ${res.status}: ${res.statusText}`;
        }
        throw new Error(errorMessage);
      }
      
      let data;
      try {
        data = await res.json();
      } catch (parseError) {
        console.error("Failed to parse JSON response:", parseError);
        throw new Error("Invalid JSON response from server");
      }
      
      let output = data.output || data;
      
      // Handle 5-step response structure
      if (use5Step && output && output.final_data) {
        // 5-step process returns structured data
        output = {
          ...output.final_data,
          step_data: output.step_data,
          metadata: output.metadata
        };
      }
      
      // Check if the output contains an error
      if (output && output.error) {
        throw new Error(output.error);
      }
      
      // Try to parse output as JSON if it's a string
      if (typeof output === 'string') {
        try {
          output = JSON.parse(output);
        } catch {
          // Check if it's a conversational response
          const conversationalIndicators = [
            "hello", "hi", "how can i help", "what would you like", 
            "is there something", "can i help you", "let me help"
          ];
          const lowerOutput = output.toLowerCase();
          if (conversationalIndicators.some(indicator => lowerOutput.includes(indicator))) {
            throw new Error("LLM returned a conversational response instead of structured data. Please try again.");
          }
          // leave as string if not JSON
        }
      }
      
      setResult(output);
      console.log("Set LLM result:", output);
    } catch (error) {
      console.error("Error calling LLM:", error);
      
      // Provide more specific error messages
      let errorMessage = error.message;
      if (error.name === 'AbortError') {
        errorMessage = "Request timed out. Please try again with a simpler request.";
      } else if (error.message.includes('fetch failed')) {
        errorMessage = "Failed to connect to the server. Please check if the backend is running.";
      } else if (error.message.includes('conversational response')) {
        errorMessage = "The AI returned a conversational response instead of structured data. This usually means the prompt was too complex. Please try again or simplify your request.";
      }
      
      setResult({ 
        error: errorMessage,
        details: error.message,
        timestamp: new Date().toISOString()
      });
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

  // Helper to calculate AI confidence score
  const calculateConfidence = () => {
    if (!result || typeof result === 'string') return null;
    
    const data = result.final_data || result;
    
    // First, try to use the backend-provided ai_confidence
    if (data.ai_confidence !== undefined) {
      const score = data.ai_confidence;
      let level = 'Low';
      let color = 'red';
      if (score >= 80) {
        level = 'High';
        color = 'green';
      } else if (score >= 60) {
        level = 'Medium';
        color = 'yellow';
      } else if (score >= 40) {
        level = 'Fair';
        color = 'orange';
      }
      
      return {
        score,
        level,
        color,
        source: 'LLM Response',
        factors: {
          dataCompleteness: !!(data.sli && data.sli.length > 0 && data.slo && data.slo.length > 0 && data.alerts && data.alerts.length > 0 && data.llm_suggestions && data.llm_suggestions.length > 0),
          validation: !!data.validation_summary,
          stepCompleteness: result.step_data ? Object.keys(result.step_data).length : 0,
          quality: data.ai_confidence
        }
      };
    }
    
    // Fallback to structural calculation if ai_confidence is not available
    let confidence = 0;
    let factors = 0;
    
    // Factor 1: Data completeness (0-25 points)
    const hasSlis = data.sli && data.sli.length > 0;
    const hasSlos = data.slo && data.slo.length > 0;
    const hasAlerts = data.alerts && data.alerts.length > 0;
    const hasSuggestions = data.llm_suggestions && data.llm_suggestions.length > 0;
    
    if (hasSlis) confidence += 6;
    if (hasSlos) confidence += 6;
    if (hasAlerts) confidence += 6;
    if (hasSuggestions) confidence += 7;
    factors++;
    
    // Factor 2: Validation presence (0-25 points)
    if (data.validation_summary) {
      confidence += 25;
    }
    factors++;
    
    // Factor 3: Step data completeness for 5-step method (0-25 points)
    if (result.step_data && use5Step) {
      const stepCount = Object.keys(result.step_data).length;
      confidence += Math.min(25, (stepCount / 5) * 25);
    } else if (!use5Step) {
      confidence += 20; // Original method gets partial credit
    }
    factors++;
    
    // Factor 4: Data quality indicators (0-25 points)
    let qualityScore = 0;
    if (data.sli && data.sli.length >= 2) qualityScore += 8;
    if (data.slo && data.slo.length >= 1) qualityScore += 8;
    if (data.alerts && data.alerts.length >= 1) qualityScore += 9;
    confidence += qualityScore;
    factors++;
    
    // Calculate final percentage
    const finalConfidence = Math.round((confidence / (factors * 25)) * 100);
    
    // Determine confidence level and color
    let level = 'Low';
    let color = 'red';
    if (finalConfidence >= 80) {
      level = 'High';
      color = 'green';
    } else if (finalConfidence >= 60) {
      level = 'Medium';
      color = 'yellow';
    } else if (finalConfidence >= 40) {
      level = 'Fair';
      color = 'orange';
    }
    
    return {
      score: finalConfidence,
      level,
      color,
      source: 'Structural Analysis',
      factors: {
        dataCompleteness: hasSlis && hasSlos && hasAlerts && hasSuggestions,
        validation: !!data.validation_summary,
        stepCompleteness: result.step_data ? Object.keys(result.step_data).length : 0,
        quality: qualityScore
      }
    };
  };

  const resultSummary = getResultSummary();
  const confidence = calculateConfidence();

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

      {/* Provider & Model Selection */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">LLM Provider & Model</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="provider-select" className="block text-sm font-medium text-gray-700 mb-2">Provider</label>
            <select
              id="provider-select"
              value={provider}
              onChange={e => setProvider(e.target.value)}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            >
              <option value="ollama">Ollama</option>
              <option value="langchain">LangChain</option>
              <option value="openai">OpenAI</option>
            </select>
            {provider === 'langchain' && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4 mt-2">
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
          <div>
            <label htmlFor="model-select" className="block text-sm font-medium text-gray-700 mb-2">Model Selection</label>
            <select
              id="model-select"
              value={model}
              onChange={e => setModel(e.target.value)}
              className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              disabled={modelsLoading || models.length === 0}
            >
              {modelsLoading ? (
                <option>Loading models...</option>
              ) : models.length === 0 ? (
                <option>No models available</option>
              ) : (
                models.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))
              )}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Fast models (1B-7B) are 3-5x faster than larger models with similar quality for this task.
            </p>
          </div>
        </div>
      </div>

      {/* LLM Model & Speed Settings */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">LLM Model & Speed Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Results Summary</h3>
                {confidence && (
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-xs text-gray-500 mb-1">AI Confidence Score</div>
                      <div className="text-xs text-gray-400">({confidence.source})</div>
                    </div>
                    <div className={`relative inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold shadow-sm border-2 ${
                      confidence.color === 'green' ? 'bg-green-50 text-green-800 border-green-200' :
                      confidence.color === 'yellow' ? 'bg-yellow-50 text-yellow-800 border-yellow-200' :
                      confidence.color === 'orange' ? 'bg-orange-50 text-orange-800 border-orange-200' :
                      'bg-red-50 text-red-800 border-red-200'
                    }`}>
                      <span className={`w-3 h-3 rounded-full mr-3 ${
                        confidence.color === 'green' ? 'bg-green-500' :
                        confidence.color === 'yellow' ? 'bg-yellow-500' :
                        confidence.color === 'orange' ? 'bg-orange-500' :
                        'bg-red-500'
                      }`}></span>
                      <span className="text-lg font-bold">{confidence.score}%</span>
                      <span className="ml-2 text-sm font-medium">- {confidence.level}</span>
                      <div className={`absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-xs font-bold ${
                        confidence.color === 'green' ? 'bg-green-600 text-white' :
                        confidence.color === 'yellow' ? 'bg-yellow-600 text-white' :
                        confidence.color === 'orange' ? 'bg-orange-600 text-white' :
                        'bg-red-600 text-white'
                      }`}>
                        {confidence.score >= 80 ? '✓' : confidence.score >= 60 ? '!' : '?'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
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
              
              {/* Enhanced Confidence Details */}
              {confidence && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-md font-semibold text-gray-800">Confidence Analysis</h4>
                    <div className="text-xs text-gray-500">
                      {confidence.source === 'LLM Response' ? 'Direct from AI model' : 'Calculated from response structure'}
                    </div>
                  </div>
                  
                  {/* Confidence Level Explanation */}
                  <div className={`mb-4 p-3 rounded-lg ${
                    confidence.color === 'green' ? 'bg-green-50 border border-green-200' :
                    confidence.color === 'yellow' ? 'bg-yellow-50 border border-yellow-200' :
                    confidence.color === 'orange' ? 'bg-orange-50 border border-orange-200' :
                    'bg-red-50 border border-red-200'
                  }`}>
                    <div className="flex items-start">
                      <div className={`w-2 h-2 rounded-full mt-2 mr-3 flex-shrink-0 ${
                        confidence.color === 'green' ? 'bg-green-500' :
                        confidence.color === 'yellow' ? 'bg-yellow-500' :
                        confidence.color === 'orange' ? 'bg-orange-500' :
                        'bg-red-500'
                      }`}></div>
                      <div>
                        <div className={`text-sm font-medium ${
                          confidence.color === 'green' ? 'text-green-800' :
                          confidence.color === 'yellow' ? 'text-yellow-800' :
                          confidence.color === 'orange' ? 'text-orange-800' :
                          'text-red-800'
                        }`}>
                          {confidence.level} Confidence ({confidence.score}%)
                        </div>
                        <div className={`text-xs mt-1 ${
                          confidence.color === 'green' ? 'text-green-700' :
                          confidence.color === 'yellow' ? 'text-yellow-700' :
                          confidence.color === 'orange' ? 'text-orange-700' :
                          'text-red-700'
                        }`}>
                          {confidence.score >= 80 ? 'High confidence - Results are reliable and comprehensive' :
                           confidence.score >= 60 ? 'Medium confidence - Results are generally reliable with minor gaps' :
                           confidence.score >= 40 ? 'Fair confidence - Results may have some limitations or missing elements' :
                           'Low confidence - Results may be incomplete or unreliable'}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Confidence Calculation Details */}
                  <div className="mb-4 bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h5 className="text-sm font-medium text-gray-800">How Confidence is Calculated</h5>
                      <button
                        onClick={() => setShowConfidenceDetails(!showConfidenceDetails)}
                        className="text-xs text-indigo-600 hover:text-indigo-800"
                      >
                        {showConfidenceDetails ? 'Hide Details' : 'Show Details'}
                      </button>
                    </div>
                    
                    {showConfidenceDetails && (
                      <div className="space-y-3 text-xs text-gray-600">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <div className="font-medium text-gray-700 mb-2">Confidence Factors:</div>
                            <ul className="space-y-1">
                              <li>• <strong>Data Completeness:</strong> All required outputs present (+25%)</li>
                              <li>• <strong>Validation:</strong> Output passes validation checks (+25%)</li>
                              <li>• <strong>Structure Quality:</strong> Proper JSON structure and formatting (+20%)</li>
                              <li>• <strong>Content Quality:</strong> Meaningful and relevant content (+20%)</li>
                              <li>• <strong>LLM Confidence:</strong> Direct confidence from AI model (+10%)</li>
                            </ul>
                          </div>
                          <div>
                            <div className="font-medium text-gray-700 mb-2">Scoring Breakdown:</div>
                            <ul className="space-y-1">
                              <li>• <strong>80-100%:</strong> High confidence - Excellent reliability</li>
                              <li>• <strong>60-79%:</strong> Medium confidence - Good reliability</li>
                              <li>• <strong>40-59%:</strong> Fair confidence - Some limitations</li>
                              <li>• <strong>0-39%:</strong> Low confidence - Poor reliability</li>
                            </ul>
                          </div>
                        </div>
                        <div className="pt-2 border-t border-gray-200">
                          <div className="font-medium text-gray-700 mb-1">Current Analysis Factors:</div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                            <div className={`px-2 py-1 rounded text-xs ${
                              confidence.factors.dataCompleteness ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              Data: {confidence.factors.dataCompleteness ? '✓' : '✗'}
                            </div>
                            <div className={`px-2 py-1 rounded text-xs ${
                              confidence.factors.validation ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              Validation: {confidence.factors.validation ? '✓' : '✗'}
                            </div>
                            <div className={`px-2 py-1 rounded text-xs ${
                              confidence.factors.structureQuality ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              Structure: {confidence.factors.structureQuality ? '✓' : '✗'}
                            </div>
                            <div className={`px-2 py-1 rounded text-xs ${
                              confidence.factors.contentQuality ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              Content: {confidence.factors.contentQuality ? '✓' : '✗'}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Confidence Factors Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className={`p-3 rounded-lg border ${
                      confidence.factors.dataCompleteness ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-center mb-2">
                        <span className={`w-2 h-2 rounded-full mr-2 ${
                          confidence.factors.dataCompleteness ? 'bg-green-500' : 'bg-gray-300'
                        }`}></span>
                        <span className={`text-sm font-medium ${
                          confidence.factors.dataCompleteness ? 'text-green-800' : 'text-gray-500'
                        }`}>
                          Data Completeness
                        </span>
                      </div>
                      <div className={`text-xs ${
                        confidence.factors.dataCompleteness ? 'text-green-700' : 'text-gray-500'
                      }`}>
                        {confidence.factors.dataCompleteness ? 
                          'All required outputs present' : 
                          'Missing some required outputs'}
                      </div>
                    </div>
                    
                    <div className={`p-3 rounded-lg border ${
                      confidence.factors.validation ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-center mb-2">
                        <span className={`w-2 h-2 rounded-full mr-2 ${
                          confidence.factors.validation ? 'bg-green-500' : 'bg-gray-300'
                        }`}></span>
                        <span className={`text-sm font-medium ${
                          confidence.factors.validation ? 'text-green-800' : 'text-gray-500'
                        }`}>
                          Validation
                        </span>
                      </div>
                      <div className={`text-xs ${
                        confidence.factors.validation ? 'text-green-700' : 'text-gray-500'
                      }`}>
                        {confidence.factors.validation ? 
                          'Output passes validation checks' : 
                          'Failed validation checks'}
                      </div>
                    </div>
                    
                    <div className={`p-3 rounded-lg border ${
                      confidence.factors.structureQuality ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-center mb-2">
                        <span className={`w-2 h-2 rounded-full mr-2 ${
                          confidence.factors.structureQuality ? 'bg-green-500' : 'bg-gray-300'
                        }`}></span>
                        <span className={`text-sm font-medium ${
                          confidence.factors.structureQuality ? 'text-green-800' : 'text-gray-500'
                        }`}>
                          Structure Quality
                        </span>
                      </div>
                      <div className={`text-xs ${
                        confidence.factors.structureQuality ? 'text-green-700' : 'text-gray-500'
                      }`}>
                        {confidence.factors.structureQuality ? 
                          'Proper JSON structure' : 
                          'Structural issues detected'}
                      </div>
                    </div>
                    
                    <div className={`p-3 rounded-lg border ${
                      confidence.factors.contentQuality ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-center mb-2">
                        <span className={`w-2 h-2 rounded-full mr-2 ${
                          confidence.factors.contentQuality ? 'bg-green-500' : 'bg-gray-300'
                        }`}></span>
                        <span className={`text-sm font-medium ${
                          confidence.factors.contentQuality ? 'text-green-800' : 'text-gray-500'
                        }`}>
                          Content Quality
                        </span>
                      </div>
                      <div className={`text-xs ${
                        confidence.factors.contentQuality ? 'text-green-700' : 'text-gray-500'
                      }`}>
                        {confidence.factors.contentQuality ? 
                          'Meaningful content' : 
                          'Content quality issues'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
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