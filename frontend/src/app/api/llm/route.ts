import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const { task, input, method = "original", model = "llama2", temperature = 0.7, provider = "ollama" } = await req.json();

  try {
    // Choose endpoint based on method
    const endpoint = method === "5step" ? "/llm/5step" : "/llm";
    const requestBody = method === "5step" 
      ? { input, model, temperature, provider }
      : { task, input, provider };

    const res = await fetch(`http://localhost:8001${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
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
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
} 