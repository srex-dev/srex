import PageContainer from '@/components/layout/PageContainer';

export default function DocumentationPage() {
  return (
    <PageContainer title="Documentation">
      {/* Quick Links */}
      <div>
        <h2 className="text-lg font-medium text-gray-900">Quick Links</h2>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <a href="#getting-started" className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <span className="absolute inset-0" aria-hidden="true" />
              <p className="text-sm font-medium text-gray-900">Getting Started</p>
              <p className="text-sm text-gray-500">Quick start guide and basic concepts</p>
            </div>
          </a>

          <a href="#components" className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <span className="absolute inset-0" aria-hidden="true" />
              <p className="text-sm font-medium text-gray-900">Components</p>
              <p className="text-sm text-gray-500">System components and their functions</p>
            </div>
          </a>

          <a href="#api" className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <span className="absolute inset-0" aria-hidden="true" />
              <p className="text-sm font-medium text-gray-900">API Reference</p>
              <p className="text-sm text-gray-500">API endpoints and usage examples</p>
            </div>
          </a>
        </div>
      </div>

      {/* Documentation Sections */}
      <div className="mt-8 space-y-8">
        <section id="getting-started">
          <h2 className="text-xl font-semibold text-gray-900">Getting Started</h2>
          <div className="mt-4 prose prose-indigo">
            <p>
              Welcome to the SREX documentation. This guide will help you get started with monitoring and managing your system reliability.
            </p>
            <h3>Prerequisites</h3>
            <ul>
              <li>Node.js 16.x or later</li>
              <li>npm or yarn package manager</li>
              <li>Access to your system's monitoring endpoints</li>
            </ul>
            <h3>Installation</h3>
            <pre className="bg-gray-50 p-4 rounded-md">
              npm install srex
            </pre>
          </div>
        </section>

        <section id="components">
          <h2 className="text-xl font-semibold text-gray-900">Components</h2>
          <div className="mt-4 prose prose-indigo">
            <p>
              SREX consists of several key components that work together to provide comprehensive system monitoring and management.
            </p>
            <h3>Core Components</h3>
            <ul>
              <li>Metrics Collector</li>
              <li>Alert Manager</li>
              <li>Dashboard</li>
              <li>API Server</li>
            </ul>
          </div>
        </section>

        <section id="api">
          <h2 className="text-xl font-semibold text-gray-900">API Reference</h2>
          <div className="mt-4 prose prose-indigo">
            <p>
              The SREX API provides endpoints for accessing metrics, managing alerts, and configuring the system.
            </p>
            <h3>Authentication</h3>
            <p>
              All API requests require authentication using JWT tokens. Include the token in the Authorization header:
            </p>
            <pre className="bg-gray-50 p-4 rounded-md">
              Authorization: Bearer your-token-here
            </pre>
          </div>
        </section>
      </div>
    </PageContainer>
  );
} 