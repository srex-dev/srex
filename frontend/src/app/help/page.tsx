"use client";

import React, { useEffect, useState } from 'react';
import PageContainer from '@/components/layout/PageContainer';

interface HelpDoc {
  id: string;
  title: string;
  content: string;
  category: string;
}

export default function HelpPage() {
  const [docs, setDocs] = useState<HelpDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/help')
      .then(r => r.json())
      .then(data => {
        setDocs(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load help documentation');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading help documentation...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <PageContainer title="Help">
      {loading ? (
        <div className="text-gray-500">Loading help documentation...</div>
      ) : error ? (
        <div className="text-red">{error}</div>
      ) : docs.length === 0 ? (
        <div className="text-gray-500">No help documentation available.</div>
      ) : (
        <div className="space-y-4">
          {docs.map((doc) => (
            <div key={doc.id} className="rounded-lg shadow p-4 bg-cream text-navy">
              <h3 className="text-lg font-semibold mb-1">{doc.title}</h3>
              <div className="text-sm mb-2">Category: {doc.category}</div>
              <div>{doc.content}</div>
            </div>
          ))}
        </div>
      )}
    </PageContainer>
  );
} 