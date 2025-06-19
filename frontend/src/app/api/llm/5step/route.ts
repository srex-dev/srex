import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const { input, model = "llama2", temperature = 0.7, provider = "ollama" } = await req.json();

  try {
    const res = await fetch(`http://localhost:8001/llm/5step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input, model, temperature, provider }),
      signal: AbortSignal.timeout(1800000), // 30 minute timeout (1,800,000ms)
    });

    if (!res.ok) {
      const error = await res.text();
      return NextResponse.json({ error }, { status: res.status });
    }

    const data = await res.json();
    // Always wrap in { output: ... }
    return NextResponse.json({ output: data.output ?? data });
  } catch (error) {
    console.error('Error in 5step API route:', error);
    return NextResponse.json(
      { error: 'Failed to process 5step request' },
      { status: 500 }
    );
  }
} 