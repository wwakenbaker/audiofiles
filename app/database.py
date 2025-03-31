from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base, User

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres"

engine = create_async_engine(url=DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def create_db():
    """ Инициализация базы данных """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Создание суперпользователя
    async with SessionLocal() as session:
        session.add(
            User(
                user_id="000",
                username="admin",
                grade="admin",
                access_token="000",
                refresh_token="000",
            )
        )
        await session.commit()


async def get_session():
    """ Получение сессии для работы с базой данных """
    async with SessionLocal() as db:
        yield db
