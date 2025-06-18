-- CreateTable
CREATE TABLE "LLMOutput" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "task" TEXT NOT NULL,
    "input" JSONB NOT NULL,
    "output" JSONB NOT NULL,
    "confidence" DOUBLE PRECISION,
    "explanation" TEXT,

    CONSTRAINT "LLMOutput_pkey" PRIMARY KEY ("id")
);
