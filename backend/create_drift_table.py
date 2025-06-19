#!/usr/bin/env python3
"""
Script to create the drift_analyses table in the database.
Run this script to add the new table for storing drift analysis results.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from api.models_llm import engine, Base, DriftAnalysis
from sqlalchemy import text

async def create_drift_table():
    """Create the drift_analyses table"""
    try:
        async with engine.begin() as conn:
            # Check if table already exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'drift_analyses'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ Table 'drift_analyses' already exists")
                return
            
            # Create the table
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Successfully created 'drift_analyses' table")
            
            # Verify the table was created
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'drift_analyses'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print(f"📋 Table 'drift_analyses' has {len(columns)} columns:")
            for column in columns:
                nullable = "NULL" if column.is_nullable == "YES" else "NOT NULL"
                print(f"   • {column.column_name}: {column.data_type} ({nullable})")
                
    except Exception as e:
        print(f"❌ Error creating drift_analyses table: {e}")
        raise

async def main():
    """Main function"""
    print("🚀 Creating drift_analyses table...")
    await create_drift_table()
    print("✅ Database setup complete!")

if __name__ == "__main__":
    asyncio.run(main()) 