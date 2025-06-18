import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/config/auth';
import { prisma } from '@/lib/prisma';

export async function GET(req: NextRequest) {
  // const session = await getServerSession(authOptions);
  // if (!session) {
  //   return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  // }
  const components = await prisma.component.findMany({
    select: {
      id: true,
      name: true,
      type: true,
      status: true,
      health: true,
      lastCheck: true,
      responseTime: true,
      createdAt: true,
      updatedAt: true
    },
    orderBy: { name: 'asc' },
  });
  return NextResponse.json(components);
} 