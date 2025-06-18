"use client";

import React, { useEffect, useState } from 'react';
import PageContainer from '@/components/layout/PageContainer';

interface Setting {
  id: string;
  key: string;
  value: string;
  description: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/settings')
      .then(r => r.json())
      .then(data => {
        setSettings(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load settings');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading settings...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <PageContainer title="Settings">
      {loading ? (
        <div className="text-cream/70">Loading settings...</div>
      ) : error ? (
        <div className="text-red">{error}</div>
      ) : settings.length === 0 ? (
        <div className="text-cream/70">No settings available.</div>
      ) : (
        <table className="min-w-full border rounded-lg shadow bg-cream text-navy">
          <thead>
            <tr>
              <th className="px-2 py-1 border">Key</th>
              <th className="px-2 py-1 border">Value</th>
              <th className="px-2 py-1 border">Description</th>
            </tr>
          </thead>
          <tbody>
            {settings.map((s) => (
              <tr key={s.key}>
                <td className="px-2 py-1 border">{s.key}</td>
                <td className="px-2 py-1 border">{s.value}</td>
                <td className="px-2 py-1 border">{s.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </PageContainer>
  );
} 