from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_CONFIG

# Формируем URL подключения
engine_url = (
    "{engine}://{user}:{password}@{host}:{port}/{database}?charset=utf8".format(
        **DATABASE_CONFIG
    )
)

# Создаем движок
engine = create_engine(engine_url)

# Создаем локальные сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для декларативного синтаксиса
Base = declarative_base()
