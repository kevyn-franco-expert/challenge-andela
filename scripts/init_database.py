import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database import init_db

async def setup():
    print("Creating database tables...")
    await init_db()
    print("Done. All tables created.")

if __name__ == "__main__":
    asyncio.run(setup())
