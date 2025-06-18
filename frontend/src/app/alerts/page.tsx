"use client";

import React, { useEffect, useState } from 'react';
import PageContainer from '@/components/layout/PageContainer';

interface Alert {
  id: string;
  type: string;
  severity: string;
  message: string;
  status: string;
  createdAt: string;
  component: { id: string; name: string; type: string };
  user: { id: string; email: string; name: string };
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/alerts')
      .then(r => r.json())
      .then(data => {
        setAlerts(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load alerts');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading alerts...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <PageContainer title="Alerts">
      {alerts.length === 0 ? (
        <div className="text-gray-500">No active alerts.</div>
      ) : (
        <table className="min-w-full border rounded-lg shadow bg-cream text-navy">
          <thead>
            <tr>
              <th className="px-2 py-1 border">Type</th>
              <th className="px-2 py-1 border">Severity</th>
              <th className="px-2 py-1 border">Message</th>
              <th className="px-2 py-1 border">Component</th>
              <th className="px-2 py-1 border">User</th>
              <th className="px-2 py-1 border">Created</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id}>
                <td className="px-2 py-1 border">{a.type}</td>
                <td className="px-2 py-1 border font-bold text-red">{a.severity}</td>
                <td className="px-2 py-1 border">{a.message}</td>
                <td className="px-2 py-1 border">{a.component?.name}</td>
                <td className="px-2 py-1 border">{a.user?.email}</td>
                <td className="px-2 py-1 border text-xs">{new Date(a.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </PageContainer>
  );
} 