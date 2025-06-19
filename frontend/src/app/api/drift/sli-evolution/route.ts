import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8001';
    
    const response = await fetch(`${backendUrl}/api/drift/sli-evolution?${searchParams.toString()}`);
    
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error proxying SLI evolution request:', error);
    return NextResponse.json(
      { error: 'Failed to fetch SLI evolution' },
      { status: 500 }
    );
  }
} 