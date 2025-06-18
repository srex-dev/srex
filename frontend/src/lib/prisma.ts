import { PrismaClient } from '@prisma/client'

declare global {
  var prisma: PrismaClient | undefined
}

const prisma = global.prisma || new PrismaClient()

if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma
}

// Handle connection errors
prisma.$connect().catch((error) => {
  console.error('Failed to connect to database:', error)
  process.exit(1)
})

export { prisma } 