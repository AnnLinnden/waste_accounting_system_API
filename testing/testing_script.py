from sqlmodel import Session, select
from database.sql_models import engine, Organization, Warehouse, WarehouseAvailability


def generate_test_data():
    with Session(engine) as session:
        if session.exec(select(Organization)).first() is not None:
            return "В базе данных уже есть записи"
        organizations = [
            Organization(name="ОО 1"),
            Organization(name="ОО 2"),
        ]
        session.add_all(organizations)
        session.commit()

        warehouses = [
            Warehouse(name="МНО 1", bio_limit=0, plastic_limit=100, glass_limit=300),
            Warehouse(name="МНО 2", bio_limit=150, plastic_limit=50, glass_limit=0),
            Warehouse(name="МНО 3", bio_limit=250, plastic_limit=10, glass_limit=0),
            Warehouse(name="МНО 5", bio_limit=25, plastic_limit=0, glass_limit=220),
            Warehouse(name="МНО 6", bio_limit=150, plastic_limit=0, glass_limit=100),
            Warehouse(name="МНО 7", bio_limit=250, plastic_limit=100, glass_limit=0),
            Warehouse(name="МНО 8", bio_limit=52, plastic_limit=25, glass_limit=35),
            Warehouse(name="МНО 9", bio_limit=20, plastic_limit=250, glass_limit=0),
        ]
        session.add_all(warehouses)
        session.commit()

        orgs = session.exec(select(Organization)).all()
        whs = session.exec(select(Warehouse)).all()
        warehouse_availabilities = [
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[0].id, dist=100),
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[1].id, dist=50),
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[2].id, dist=600),
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[3].id, dist=100),
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[4].id, dist=1200),
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[5].id, dist=650),
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[6].id, dist=600),
            WarehouseAvailability(org_id=orgs[0].id, warehouse_id=whs[7].id, dist=610),
            WarehouseAvailability(org_id=orgs[1].id, warehouse_id=whs[2].id, dist=50),
            WarehouseAvailability(org_id=orgs[1].id, warehouse_id=whs[4].id, dist=650),
            WarehouseAvailability(org_id=orgs[1].id, warehouse_id=whs[5].id, dist=100),
        ]

        session.add_all(warehouse_availabilities)
        session.commit()

