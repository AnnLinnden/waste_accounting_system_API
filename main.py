from fastapi import FastAPI, HTTPException
from sqlmodel import select
from typing import List, Dict
import database.sql_models as sql
from testing.testing_script import generate_test_data

app = FastAPI()


@app.on_event("startup")  # если базы данных нет, она создается при запуске приложения
def on_startup():
    try:
        sql.create_tables()
    except FileExistsError:
        pass


@app.put("/testing/")  # Если таблица пуста, в нее можно добавить тестовые данные
def generate_data():
    generate_test_data()
    return {"message": "Данные добавлены, можно тестировать"}


@app.post("/orgs/")  # добавляем новую организацию
def add_org(org: sql.CreateOrganization, session: sql.SessionDep) -> sql.Organization:
    new_org = sql.Organization(name=org.name)  # id добавится автоматически
    session.add(new_org)
    session.commit()
    session.refresh(new_org)

    warehouses = session.exec(select(sql.Warehouse)).all()
    warehouses_id_list = [warehouse.id for warehouse in warehouses]

    # в warehouse_availability добавляем список доступных хранилищ и расстояний до них
    for warehouse_id, distance in org.warehouses.items():
        if warehouse_id in warehouses_id_list:
            warehouse_availability = sql.WarehouseAvailability(
                org_id=new_org.id,
                warehouse_id=warehouse_id,
                dist=distance
            )
            session.add(warehouse_availability)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Хранилище {warehouse_id} не найдено"
            )
    session.commit()
    return new_org


@app.post("/warehouses/")
def add_warehouse(warehouse: sql.Warehouse, session: sql.SessionDep) -> sql.Warehouse:
    session.add(warehouse)
    session.commit()
    session.refresh(warehouse)
    return warehouse


@app.get("/orgs/")
def get_org_and_warehouses(session: sql.SessionDep) -> List[sql.OrganizationsWithWarehousesResponse]:
    orgs = session.exec(select(sql.Organization)).all()
    response = []
    for organization in orgs:
        query = (
            select(sql.Warehouse)
            .join(sql.WarehouseAvailability, sql.WarehouseAvailability.warehouse_id == sql.Warehouse.id)
            .where(sql.WarehouseAvailability.org_id == organization.id)
        )

        warehouses = session.exec(query).all()
        warehouses_response = []
        for warehouse in warehouses:
            availability = session.exec(
                select(sql.WarehouseAvailability)
                .where(
                    sql.WarehouseAvailability.warehouse_id == warehouse.id,
                    sql.WarehouseAvailability.org_id == organization.id
                )
            ).one_or_none()
            if availability:
                warehouses_response.append(
                    sql.WarehouseResponse(
                        warehouse_id=warehouse.id,
                        warehouse_name=warehouse.name,
                        distance=availability.dist,
                        bio_limit=warehouse.bio_limit,
                        plastic_limit=warehouse.plastic_limit,
                        glass_limit=warehouse.glass_limit,
                    )
                )

        response.append(
            sql.OrganizationsWithWarehousesResponse(
                organization_name=organization.name,
                organization_id=organization.id,
                warehouses=warehouses_response
            )
        )
    return response


@app.get("/orgs/{org_id}/")
def get_specific_org(org_id: int, session: sql.SessionDep) -> sql.OrganizationsWithWarehousesResponse:
    org = session.get(sql.Organization, org_id)
    if not org:
        raise HTTPException(
            status_code=404,
            detail=f"Организации с id {org_id} нет в базе данных"
        )

    query = (
        select(sql.Warehouse)
        .join(sql.WarehouseAvailability, sql.WarehouseAvailability.warehouse_id == sql.Warehouse.id)
        .where(sql.WarehouseAvailability.org_id == org.id)
    )
    warehouses = session.exec(query).all()
    warehouses_response = []
    for warehouse in warehouses:
        availability = session.exec(
            select(sql.WarehouseAvailability)
            .where(
                sql.WarehouseAvailability.warehouse_id == warehouse.id,
                sql.WarehouseAvailability.org_id == org.id
            )
        ).one_or_none()
        if availability:
            warehouses_response.append(
                sql.WarehouseResponse(
                    warehouse_id=warehouse.id,
                    warehouse_name=warehouse.name,
                    distance=availability.dist,
                    bio_limit=warehouse.bio_limit,
                    plastic_limit=warehouse.plastic_limit,
                    glass_limit=warehouse.glass_limit,
                )
            )

    response = sql.OrganizationsWithWarehousesResponse(
            organization_name=org.name,
            organization_id=org.id,
            warehouses=warehouses_response
        )
    return response


@app.get("/warehouses/{warehouse_id}/")
def get_specific_warehouse(warehouse_id: int, session: sql.SessionDep) -> sql.WarehouseResponse:
    warehouse = session.get(sql.Warehouse, warehouse_id)
    if not warehouse:
        raise HTTPException(
            status_code=404,
            detail=f"Хранилища с id {warehouse_id} нет в базе данных"
        )
    query = (
        select(sql.WarehouseAvailability.org_id, sql.WarehouseAvailability.dist)
        .where(sql.WarehouseAvailability.warehouse_id == warehouse_id)
    )
    distances = session.exec(query).all()
    warehouse_response = sql.WarehouseResponse(
        warehouse_id=warehouse_id,
        warehouse_name=warehouse.name,
        bio_limit=warehouse.bio_limit,
        plastic_limit=warehouse.plastic_limit,
        glass_limit=warehouse.glass_limit,
        distance=[{"org_id": dist.org_id, "distance": dist.dist} for dist in distances]
    )
    return warehouse_response


@app.post("/transfer_waste/")
def transfer_waste(org_id: int, waste_type: str, quantity: int, session: sql.SessionDep):
    if waste_type not in ["glass", "plastic", "bio"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный тип отходов. Укажите 'glass', 'plastic' или 'bio'"
        )
    available_warehouses = session.exec(  # получили список доступных хранилищ, отсортированных по расстоянию
        select(sql.Warehouse, sql.WarehouseAvailability.dist)
        .join(sql.WarehouseAvailability, sql.Warehouse.id == sql.WarehouseAvailability.warehouse_id)
        .where(sql.WarehouseAvailability.org_id == org_id)
        .order_by(sql.WarehouseAvailability.dist)
    ).all()
    if not available_warehouses:
        raise HTTPException(
            status_code=404,
            detail=f"Нет доступных хранилищ для организации с id {org_id}"
        )

    remaining_quantity = quantity
    transfer_data = []  # Список словарей: куда отправили, в каком количестве, на какое расстояние
    reservations_to_add = []  # Хранение Reservation до коммита (на случай, если распределить отходы не удастся)
    for warehouse, distance in available_warehouses:
        if remaining_quantity <= 0:
            break

        current_limit = getattr(warehouse, f"{waste_type}_limit")
        if current_limit > 0:
            deliver_quantity = min(current_limit, remaining_quantity)
            remaining_quantity -= deliver_quantity
            setattr(warehouse, f"{waste_type}_limit", current_limit - deliver_quantity)
            session.add(warehouse)  # пока что добавляем без коммита

            reservations_to_add.append(
                sql.Reservation(
                    from_org=org_id,
                    to_warehouse=warehouse.id,
                    waste_type=waste_type,
                    quantity=deliver_quantity,
                    accepted=True
                )
            )

            transfer_data.append({
                "warehouse_id": warehouse.id,
                "warehouse_name": warehouse.name,
                "delivered_quantity": deliver_quantity,
                "distance": distance
            })

    # Проверяем, удалось ли распределить все отходы
    if remaining_quantity > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Невозможно переработать {remaining_quantity} из {quantity} единиц отходов: "
                   f"места в хранилищах недостаточно. Запрос на отправку отходов отменен"
        )

    # Если отходы распределены, добавляем записи в Reservation: по одной строке на каждую доставку отходов
    for reservation in reservations_to_add:
        session.add(reservation)
    session.commit()

    return {
        "organization_id": org_id,
        "waste_type": waste_type,
        "initial_quantity": quantity,
        "transfer_data": transfer_data
    }


@app.patch("/order/{order_id}")  # Передаем только значение accepted!
def delivery_confirmed(order_id: int, update: sql.ReservationUpdate, session: sql.SessionDep):
    reserve = session.get(sql.Reservation, order_id)
    if not reserve:
        raise HTTPException(
            status_code=404,
            detail=f"Заказа с id {order_id} нет в базе данных"
        )
    new_order_data = update.model_dump(exclude_unset=True)
    reserve.sqlmodel_update(new_order_data)
    if reserve.accepted == False:  # возвращаем лимиты, но оставляем саму запись о заказе
        warehouse = session.get(sql.Warehouse, reserve.to_warehouse)
        if not warehouse:
            raise HTTPException(
                status_code=404,
                detail=f"Хранилища с id {reserve.to_warehouse} нет в базе данных"
            )

        waste_limit_field = f"{reserve.waste_type}_limit"
        current_limit = getattr(warehouse, waste_limit_field, None)

        if current_limit is not None:
            setattr(warehouse, waste_limit_field, current_limit + reserve.quantity)
            session.add(warehouse)
    session.add(reserve)
    session.commit()
    session.refresh(reserve)
    return new_order_data
