from fastapi.testclient import TestClient
import os
from main import app

os.environ['TESTING'] = 'True'
client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message":
            "Рекомендации по использованию API здесь: https://github.com/AnnLinnden/waste_accounting_system_API"
    }


def db_reset():
    client.delete("/testing/")
    client.put("/testing/")


def test_get_all():
    db_reset()
    response = client.get("/orgs/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "organization_name": "ОО 1",
            "organization_id": 1,
            "warehouses": [
                {
                    "warehouse_id": 1,
                    "warehouse_name": "МНО 1",
                    "bio_limit": 0,
                    "plastic_limit": 100,
                    "glass_limit": 300,
                    "distance": 100
                },
                {
                    "warehouse_id": 2,
                    "warehouse_name": "МНО 2",
                    "bio_limit": 150,
                    "plastic_limit": 50,
                    "glass_limit": 0,
                    "distance": 50
                },
                {
                    "warehouse_id": 3,
                    "warehouse_name": "МНО 3",
                    "bio_limit": 250,
                    "plastic_limit": 10,
                    "glass_limit": 0,
                    "distance": 600
                },
                {
                    "warehouse_id": 4,
                    "warehouse_name": "МНО 5",
                    "bio_limit": 25,
                    "plastic_limit": 0,
                    "glass_limit": 220,
                    "distance": 100
                },
                {
                    "warehouse_id": 5,
                    "warehouse_name": "МНО 6",
                    "bio_limit": 150,
                    "plastic_limit": 0,
                    "glass_limit": 100,
                    "distance": 1200
                },
                {
                    "warehouse_id": 6,
                    "warehouse_name": "МНО 7",
                    "bio_limit": 250,
                    "plastic_limit": 100,
                    "glass_limit": 0,
                    "distance": 650
                },
                {
                    "warehouse_id": 7,
                    "warehouse_name": "МНО 8",
                    "bio_limit": 52,
                    "plastic_limit": 25,
                    "glass_limit": 35,
                    "distance": 600
                },
                {
                    "warehouse_id": 8,
                    "warehouse_name": "МНО 9",
                    "bio_limit": 20,
                    "plastic_limit": 250,
                    "glass_limit": 0,
                    "distance": 610
                }
            ]
        },
        {
            "organization_name": "ОО 2",
            "organization_id": 2,
            "warehouses": [
                {
                    "warehouse_id": 3,
                    "warehouse_name": "МНО 3",
                    "bio_limit": 250,
                    "plastic_limit": 10,
                    "glass_limit": 0,
                    "distance": 50
                },
                {
                    "warehouse_id": 5,
                    "warehouse_name": "МНО 6",
                    "bio_limit": 150,
                    "plastic_limit": 0,
                    "glass_limit": 100,
                    "distance": 650
                },
                {
                    "warehouse_id": 6,
                    "warehouse_name": "МНО 7",
                    "bio_limit": 250,
                    "plastic_limit": 100,
                    "glass_limit": 0,
                    "distance": 100
                }
            ]
        }
    ]


def test_create_org():
    db_reset()
    response = client.post("/orgs/",
                           json={"name": "Название организации", "warehouses": {"1": 10, "2": 20, "3": 30}})
    assert response.status_code == 201
    assert response.json() == {}


def test_create_org_bad_request():
    db_reset()
    response = client.post("/orgs/",
                           json=
                           {"name": "Название организации",
                            "warehouses":
                                {"Хранилище 1": "10 км",
                                 "Хранилище 2": 20,
                                 "3": 30}
                            }
                           )
    assert response.status_code == 422
    assert response.json() == {"message": "Указывая id хранилища и расстояние, используйте только целые числа"}