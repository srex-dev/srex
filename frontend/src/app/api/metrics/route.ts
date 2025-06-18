import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/config/auth';
import { prisma } from '@/lib/prisma';

export async function GET(req: NextRequest) {
  // const session = await getServerSession(authOptions);
  // if (!session) {
  //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  // }
  // Get latest metric for each component
  const metrics = await prisma.$queryRaw`SELECT DISTINCT ON ("componentId") * FROM "Metric" ORDER BY "componentId", "timestamp" DESC`;
  return NextResponse.json(metrics);
} 