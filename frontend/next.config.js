/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  /**swcMinify: true,*/
  async rewrites() {
    return [
      {
        source: '/api/health',
        destination: 'http://localhost:8001/health',
      },
      {
        source: '/api/llm/:path*',
        destination: 'http://localhost:8001/api/llm/:path*',
      },
      {
        source: '/api/llm/components',
        destination: 'http://localhost:8001/api/v1/adapters/components',
      },
      {
        source: '/api/metrics/:path*',
        destination: 'http://localhost:8001/api/metrics/:path*',
      },
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8001/api/v1/:path*',
      },
      {
        source: '/api/drift/:path*',
        destination: 'http://localhost:8001/api/drift/:path*',
      },
      {
        source: '/api/scorecard/:path*',
        destination: 'http://localhost:8001/api/scorecard/:path*',
      },
      {
        source: '/api/test/:path*',
        destination: 'http://localhost:8001/api/test/:path*',
      },
      {
        source: '/api/policies/:path*',
        destination: 'http://localhost:8001/api/v1/policies/:path*',
      },
      {
        source: '/api/components',
        destination: 'http://localhost:8001/api/v1/adapters/components',
      },
      {
        source: '/api/alerts',
        destination: 'http://localhost:8001/api/v1/alerts',
      },
      {
        source: '/api/users',
        destination: 'http://localhost:8001/api/v1/users',
      },
      {
        source: '/api/logs',
        destination: 'http://localhost:8001/api/v1/logs',
      },
      {
        source: '/api/settings',
        destination: 'http://localhost:8001/api/v1/settings',
      },
      {
        source: '/api/help',
        destination: 'http://localhost:8001/api/v1/help',
      },
    ];
  },
}

module.exports = nextConfig 