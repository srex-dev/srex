import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Create a user
  const user = await prisma.user.create({
    data: {
      name: 'Demo User',
      email: 'demo@example.com',
      role: 'admin',
      lastLogin: new Date(),
      image: 'https://i.pravatar.cc/150?img=1',
    },
  });

  // Create components
  const componentA = await prisma.component.create({
    data: {
      name: 'API Server',
      type: 'backend',
      status: 'operational',
      health: 'good',
      lastCheck: new Date(),
      responseTime: 120.5,
    },
  });
  const componentB = await prisma.component.create({
    data: {
      name: 'Frontend App',
      type: 'frontend',
      status: 'degraded',
      health: 'warning',
      lastCheck: new Date(),
      responseTime: 350.2,
    },
  });

  // Create metrics
  await prisma.metric.createMany({
    data: [
      { componentId: componentA.id, value: 99.9, timestamp: new Date() },
      { componentId: componentB.id, value: 95.2, timestamp: new Date() },
    ],
  });

  // Create alerts
  await prisma.alert.createMany({
    data: [
      { componentId: componentB.id, type: 'error', status: 'active', message: 'Frontend error detected', createdAt: new Date(), userId: user.id },
      { componentId: componentA.id, type: 'warning', status: 'resolved', message: 'API latency high', createdAt: new Date(), resolvedAt: new Date(), userId: user.id },
    ],
  });

  // Create logs
  await prisma.log.create({
    data: {
      level: 'info',
      message: 'System started',
      source: 'system',
      userId: user.id,
      timestamp: new Date(),
    },
  });

  // Create an incident
  const incident = await prisma.incident.create({
    data: {
      title: 'Database Outage',
      description: 'The database was unreachable for 10 minutes.',
      status: 'active',
      severity: 'critical',
      createdAt: new Date(),
    },
  });

  // Create a system event linked to the incident
  await prisma.systemEvent.create({
    data: {
      type: 'outage',
      description: 'Database outage detected',
      severity: 'critical',
      timestamp: new Date(),
      incidentId: incident.id,
    },
  });

  // Create system health
  await prisma.systemHealth.create({
    data: {
      status: 'degraded',
      cpuUsage: 85.5,
      memoryUsage: 78.2,
      diskUsage: 90.1,
      timestamp: new Date(),
    },
  });

  // Create system uptime
  await prisma.systemUptime.create({
    data: {
      status: 'up',
      duration: 86400, // 1 day in seconds
      timestamp: new Date(),
    },
  });

  // Create a setting
  await prisma.setting.create({
    data: {
      key: 'siteTitle',
      value: 'SREX Demo',
      description: 'The title of the site',
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  });

  // Seed help documentation
  await prisma.helpDoc.createMany({
    data: [
      {
        title: 'Getting Started',
        content: 'Welcome to SREX! This guide will help you get started.',
        category: 'General',
        createdAt: new Date(),
      },
      {
        title: 'Troubleshooting',
        content: 'If you encounter issues, check the logs and system status.',
        category: 'Support',
        createdAt: new Date(),
      },
      {
        title: 'Contact Support',
        content: 'For further assistance, contact support@srex.com.',
        category: 'Support',
        createdAt: new Date(),
      },
    ],
  });
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  }); 