from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine
from datetime import datetime
import config


# Данные об организации. Информации о типах отходов здесь нет, потому что они будут в post-запросах
class Organizations(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(default=..., description="Название организации")


# Данные о хранилищах, включая актуальные лимиты по каждому типу отходов
class Warehouses(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(default=..., description="Название хранилища")
    bio_limit: int = Field(default=...)
    plastic_limit: int = Field(default=...)
    glass_limit: int = Field(default=...)


# Хранилища, доступные для конкретных организаций, расстояние между организациями и хранилищами
class WarehousesAvailability(SQLModel, table=True):
    id: int = Field(primary_key=True)
    org_id: int = Field(default=..., index=True, foreign_key="organizations.id")
    warehouse_id: int = Field(default=..., index=True, foreign_key="warehouses.id")
    dist: int = Field(default=...)


# Информация о резервировании места в хранилищах. Нужно, чтобы сотрудник организации мог забронировать место.
# Если отходы не доставят, сотрудник хранилища укажет в accepted False, бронь отменится, лимиты обновятся.
# Можно добавить функцию проверки для аналитики: сколько доставок отменили в конкретный период,
# какая организация делает это чаще всего.
class Reservation(SQLModel, table=True):
    id: int = Field(primary_key=True)
    from_org: int = Field(default=..., foreign_key="organizations.id")
    to_warehouse: int = Field(default=..., foreign_key="warehouses.id")
    waste_type: str = Field(default=..., description='Укажите glass, plastic или bio')
    quantity: int = Field(default=...)
    date: datetime.today() = Field(default=...)
    accepted: bool = Field()


engine = create_engine(config.database_url)


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]