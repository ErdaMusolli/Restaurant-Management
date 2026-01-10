from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/restaurant_db"
engine = create_async_engine(DATABASE_URL, echo=True)

async def add_restaurant_column():
    async with engine.begin() as conn:
        # Shto kolonën nëse nuk ekziston
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS restaurant_id INTEGER;")
        )
        # Shto foreign key **vetëm një herë** (pa IF NOT EXISTS)
        try:
            await conn.execute(
                text("""
                    ALTER TABLE users
                    ADD CONSTRAINT fk_users_restaurant
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id);
                """)
            )
        except Exception as e:
            print("Constraint already exists or error:", e)

        await conn.commit()
        print("Tabela users përditësuar!")

asyncio.run(add_restaurant_column())
