import os
from typing import Annotated, Optional, Dict, List
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy import false
from sqlmodel import Field, Session, SQLModel, create_engine
import config


# Данные об организации. Информации о типах отходов здесь нет, потому что они будут в запросах на утилизацию
class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # id будет присваиваться автоматически
    name: str = Field(default=..., description="Название организации")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Название организации",
                    "warehouses": {
                        1: 40,
                        2: 50,
                        3: 60
                    }
                }
            ]
        }
    }


class CreateOrganization(SQLModel):
    name: str
    warehouses: Dict[int, int]  # id склада, расстояние до него от организации
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Название организации",
                    "warehouses": {
                        1: 40,
                        2: 50,
                        3: 60
                    }
                }
            ]
        }
    }


class Warehouse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default=..., description="Название хранилища")
    bio_limit: int = Field(default=...)
    plastic_limit: int = Field(default=...)
    glass_limit: int = Field(default=...)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Название хранилища",
                    "bio_limit": 10,
                    "plastic_limit": 20,
                    "glass_limit": 30
                }
            ]
        }
    }


# Хранилища, доступные для конкретных организаций, расстояние между организациями и хранилищами
class WarehouseAvailability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: int = Field(default=..., index=True, foreign_key="organization.id")
    warehouse_id: int = Field(default=..., index=True, foreign_key="warehouse.id")
    dist: int = Field(default=...)


# Резервирование места в хранилищах. Нужно, чтобы сотрудник организации мог забронировать место.
# Если отходы не доставят, сотрудник хранилища укажет в accepted False, бронь отменится, лимиты обновятся.
# Каждая доставка сохраняется в отдельной строке (если ОО1 отдает 20 единиц стекла в МНО2 и 40 - в МНО3 в рамках
# одной отправки, будет создано 2 заказа - по одному на хранилище)
# Можно добавить функцию проверки для аналитики: сколько доставок отменили в конкретный период,
# какая организация делает это чаще всего.
class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_org: int = Field(default=..., foreign_key="organization.id")
    to_warehouse: int = Field(default=..., foreign_key="warehouse.id")
    waste_type: str = Field(default=..., description="Укажите тип отходов: стекло, пластик или биоотходы")
    quantity: int = Field(default=...)
    accepted: bool = Field(default=None)


# Для обновления accepted: получены отходы или нет
class ReservationUpdate(BaseModel):
    id: Optional[int] | None = None
    from_org: int | None = None
    to_warehouse: int | None = None
    waste_type: str | None = None
    quantity: int | None = None
    accepted: bool | None = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"accepted": False}
            ]
        }
    }


class WarehouseResponse(BaseModel):
    warehouse_id: int
    warehouse_name: str
    bio_limit: int
    plastic_limit: int
    glass_limit: int
    distance: int | list  # int для одного хранилища (get /orgs/), list для нескольких (get /warehouses/{warehouse_id}/)


class OrganizationsWithWarehousesResponse(BaseModel):
    organization_name: str
    organization_id: int
    warehouses: List[WarehouseResponse]


def create_db():
    if os.environ.get("TESTING") == "True":
        return create_engine(config.test_db_url)
    else:
        return create_engine(config.database_url)


engine = create_db()


def create_tables():
    SQLModel.metadata.create_all(engine)


def drop_tables():
    if os.environ.get("TESTING") == "True":
        SQLModel.metadata.drop_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
