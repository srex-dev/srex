import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    // Get system health metrics from the database
    const healthMetrics = await prisma.systemHealth.findFirst({
      orderBy: {
        timestamp: 'desc',
      },
    });

    // Get active incidents count
    const activeIncidents = await prisma.incident.count({
      where: {
        status: 'active',
      },
    });

    // Calculate uptime for the last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const uptimeData = await prisma.systemUptime.findMany({
      where: {
        timestamp: {
          gte: thirtyDaysAgo,
        },
      },
    });

    const totalMinutes = 30 * 24 * 60; // 30 days in minutes
    const downtimeMinutes = uptimeData.reduce((acc, curr) => {
      return acc + (curr.status === 'down' ? curr.duration : 0);
    }, 0);

    const uptimePercentage = ((totalMinutes - downtimeMinutes) / totalMinutes) * 100;

    return NextResponse.json({
      status: healthMetrics?.status || 'healthy',
      percentage: healthMetrics?.healthPercentage || 100,
      activeIncidents,
      uptime: uptimePercentage.toFixed(2),
    });
  } catch (error) {
    console.error('API /api/metrics/health error:', error, error?.stack);
    return NextResponse.json({ error: 'Internal Server Error', details: String(error) }, { status: 500 });
  }
} 