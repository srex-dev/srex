"use client";

import React, { useEffect, useState } from 'react';
import PageContainer from '@/components/layout/PageContainer';

interface Metric {
  id: string;
  componentId: string;
  name: string;
  value: number;
  timestamp: string;
}

export default function ReportsPage() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/metrics')
      .then(r => r.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load metrics');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading reports...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <PageContainer title="Reports">
      {loading ? (
        <div className="text-gray-500">Loading metrics...</div>
      ) : error ? (
        <div className="text-red">{error}</div>
      ) : metrics.length === 0 ? (
        <div className="text-gray-500">No metrics available.</div>
      ) : (
        <table className="min-w-full border rounded-lg shadow bg-cream text-navy">
          <thead>
            <tr>
              <th className="px-2 py-1 border">Component ID</th>
              <th className="px-2 py-1 border">Metric</th>
              <th className="px-2 py-1 border">Value</th>
              <th className="px-2 py-1 border">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => (
              <tr key={m.id}>
                <td className="px-2 py-1 border">{m.componentId}</td>
                <td className="px-2 py-1 border">{m.name}</td>
                <td className="px-2 py-1 border">{m.value}</td>
                <td className="px-2 py-1 border text-xs">{new Date(m.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </PageContainer>
  );
} 