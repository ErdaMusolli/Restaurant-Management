from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/restaurant_db"
engine = create_async_engine(DATABASE_URL, echo=True)

async def add_restaurant_column_to_dish():
    async with engine.begin() as conn:
        # 1️⃣ Shto kolonën restaurant_id në dishes
        await conn.execute(
            text("ALTER TABLE dishes ADD COLUMN IF NOT EXISTS restaurant_id INTEGER;")
        )

        # 2️⃣ Shto foreign key (kap exception nëse ekziston)
        try:
            await conn.execute(
                text("""
                    ALTER TABLE dishes
                    ADD CONSTRAINT fk_dish_restaurant
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id);
                """)
            )
        except Exception as e:
            print("Constraint already exists or ka gabim:", e)

        await conn.commit()
        print("Tabela dishes është përditësuar me restaurant_id!")

# Ekzekuto funksionin
asyncio.run(add_restaurant_column_to_dish())
