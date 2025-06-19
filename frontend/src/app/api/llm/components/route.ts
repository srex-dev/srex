import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8001';
    const response = await fetch(`${backendUrl}/api/v1/adapters/components`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(1800000), // 30 minute timeout (1,800,000ms)
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const components = await response.json();
    return NextResponse.json(components);
  } catch (error) {
    console.error('Error fetching components:', error);
    return NextResponse.json(
      { error: 'Failed to fetch components from backend' },
      { status: 500 }
    );
  }
} 