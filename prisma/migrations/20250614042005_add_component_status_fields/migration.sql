-- AlterTable
ALTER TABLE "Component" ADD COLUMN     "health" TEXT,
ADD COLUMN     "lastCheck" TIMESTAMP(3),
ADD COLUMN     "responseTime" DOUBLE PRECISION;
