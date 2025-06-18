"use client";

import React, { useEffect, useState } from 'react';
import PageContainer from '@/components/layout/PageContainer';

interface Component {
  id: string;
  name: string;
  type: string;
  status: string;
  health: number;
  lastChecked: string;
}

export default function ComponentsPage() {
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/components')
      .then(r => r.json())
      .then(data => {
        setComponents(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load components');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading components...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <PageContainer title="Components">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {components.map((c) => (
          <div key={c.id} className="border rounded p-4 shadow bg-white">
            <div className="font-semibold">{c.name}</div>
            <div className="text-sm text-gray-500">{c.type}</div>
            <div className="mt-2">Status: <span className={`font-bold ${c.status === 'HEALTHY' ? 'text-green-600' : c.status === 'DEGRADED' ? 'text-yellow-600' : 'text-red-600'}`}>{c.status}</span></div>
            <div className="mt-1">Health: {c.health}%</div>
            <div className="mt-1 text-xs text-gray-500">Last checked: {new Date(c.lastChecked).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </PageContainer>
  );
} 