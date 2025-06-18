/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  /**swcMinify: true,*/
  async rewrites() {
    return [
      {
        source: '/api/llm/:path*',
        destination: 'http://localhost:8001/llm/:path*',
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
    ];
  },
}

module.exports = nextConfig 