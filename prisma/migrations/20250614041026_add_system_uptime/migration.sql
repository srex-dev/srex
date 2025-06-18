-- CreateTable
CREATE TABLE "SystemUptime" (
    "id" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "duration" INTEGER,
    "metadata" JSONB,

    CONSTRAINT "SystemUptime_pkey" PRIMARY KEY ("id")
);
