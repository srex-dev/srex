import React from 'react';

interface PageContainerProps {
  children: React.ReactNode;
  title?: string;
  actions?: React.ReactNode;
}

export default function PageContainer({ children, title, actions }: PageContainerProps) {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        {(title || actions) && (
          <div className="flex justify-between items-center mb-6">
            {title && <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>}
            {actions && <div className="flex space-x-3">{actions}</div>}
          </div>
        )}
        {children}
      </div>
    </div>
  );
} 