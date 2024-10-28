from typing import Annotated, Optional, Dict, List
from pydantic import BaseModel
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine
import config


# Данные об организации. Информации о типах отходов здесь нет, потому что они будут в запросах на утилизацию
class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # id будет присваиваться автоматически
    name: str = Field(default=..., description="Название организации")


class CreateOrganization(SQLModel):  # при создании организации пользователь задает расстояние до хранилищ
    name: str
    warehouses: Dict[int, int]  # id склада, расстояние до него от организации


# Данные о хранилищах, включая актуальные лимиты по каждому типу отходов
class Warehouse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default=..., description="Название хранилища")
    bio_limit: int = Field(default=...)
    plastic_limit: int = Field(default=...)
    glass_limit: int = Field(default=...)


# Хранилища, доступные для конкретных организаций, расстояние между организациями и хранилищами
class WarehouseAvailability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: int = Field(default=..., index=True, foreign_key="organization.id")
    warehouse_id: int = Field(default=..., index=True, foreign_key="warehouse.id")
    dist: int = Field(default=...)


# Информация о резервировании места в хранилищах. Нужно, чтобы сотрудник организации мог забронировать место.
# Если отходы не доставят, сотрудник хранилища укажет в accepted False, бронь отменится, лимиты обновятся.
# Можно добавить функцию проверки для аналитики: сколько доставок отменили в конкретный период,
# какая организация делает это чаще всего.
class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_org: int = Field(default=..., foreign_key="organization.id")
    to_warehouse: int = Field(default=..., foreign_key="warehouse.id")
    waste_type: str = Field(default=..., description='Укажите glass, plastic или bio')
    quantity: int = Field(default=...)
    accepted: bool = Field()


# Модель создания списка складов в удобном для пользователя формате
class WarehouseResponse(BaseModel):
    warehouse_id: int
    warehouse_name: str
    distance: int
    bio_limit: int
    plastic_limit: int
    glass_limit: int


# Модель возвращает список доступных складов и информацию о них для каждой организации
class OrganizationsWithWarehousesResponse(BaseModel):
    organization_name: str
    warehouses: List[WarehouseResponse]


engine = create_engine(config.database_url)


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
