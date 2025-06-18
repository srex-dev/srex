import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    // Get recent system events and incidents
    const recentEvents = await prisma.systemEvent.findMany({
      take: 10,
      orderBy: {
        timestamp: 'desc',
      },
      include: {
        incident: true,
      },
    });

    // Format the events for the frontend
    const formattedEvents = recentEvents.map(event => ({
      id: event.id,
      event: event.description,
      status: event.incident?.status || 'resolved',
      time: formatTimeAgo(event.timestamp),
    }));

    return NextResponse.json(formattedEvents);
  } catch (error) {
    console.error('Error fetching recent activity:', error);
    return NextResponse.json(
      { error: 'Failed to fetch recent activity' },
      { status: 500 }
    );
  }
}

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return `${diffInSeconds} seconds ago`;
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minutes ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hours ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays} days ago`;
} 