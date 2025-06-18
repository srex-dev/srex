import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(req: NextRequest) {
  try {
    const logs = await prisma.log.findMany({
      take: 50,
      orderBy: { timestamp: 'desc' },
    });
    return NextResponse.json(logs);
  } catch (error) {
    console.error('API /api/logs error:', error);
    return NextResponse.json({ error: 'Internal Server Error', details: String(error) }, { status: 500 });
  }
} 