from fastapi.testclient import TestClient
import os

os.environ['TESTING'] = 'True'  # Эту строку нельзя переносить ниже, иначе app создастся до включения тестового режима
from main import app

client = TestClient(app)


def db_reset():
    client.delete("/testing/")
    client.put("/testing/")


def test_read_main():
    db_reset()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message":
            "Рекомендации по использованию API здесь: https://github.com/AnnLinnden/waste_accounting_system_API"
    }


def test_create_warehouse():
    db_reset()
    response = client.post("/warehouses/",
                           json={"name": "Название", "bio_limit": 10, "plastic_limit": 20, "glass_limit": 30})
    assert response.status_code == 201
    assert response.json() == {"bio_limit": 10, "name": "Название", "glass_limit": 30, "id": 9, "plastic_limit": 20}


def test_create_warehouse_bad_request():
    db_reset()
    response = client.post("/warehouses/",
                           json={"name": "Название", "bio_limit": "10т", "plastic_limit": "20т", "glass_limit": "30т"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Указывая лимиты отходов, используйте только числа"
                               }


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
                                 "Хранилище 2": "20 км",
                                 "Хранилище 3": "30 км"}
                            }
                           )
    assert response.status_code == 422
    assert response.json() == {"detail":
                                   [{"type": "int_parsing", "loc":
                                       ["body", "warehouses", "Хранилище 1", "[key]"],
                                     "msg": "Input should be a valid integer, unable to parse string as an integer",
                                     "input": "Хранилище 1"},
                                    {"type": "int_parsing",
                                     "loc": [
                                         "body",
                                         "warehouses",
                                         "Хранилище 1"
                                     ],
                                     "msg": "Input should be a valid integer, unable to parse string as an integer",
                                     "input": "10 км"
                                     },
                                    {
                                        "type": "int_parsing",
                                        "loc": [
                                            "body",
                                            "warehouses",
                                            "Хранилище 2",
                                            "[key]"
                                        ],
                                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                                        "input": "Хранилище 2"
                                    },
                                    {
                                        "type": "int_parsing",
                                        "loc": [
                                            "body",
                                            "warehouses",
                                            "Хранилище 2"
                                        ],
                                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                                        "input": "20 км"
                                    },
                                    {
                                        "type": "int_parsing",
                                        "loc": [
                                            "body",
                                            "warehouses",
                                            "Хранилище 3",
                                            "[key]"
                                        ],
                                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                                        "input": "Хранилище 3"
                                    },
                                    {
                                        "type": "int_parsing",
                                        "loc": [
                                            "body",
                                            "warehouses",
                                            "Хранилище 3"
                                        ],
                                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                                        "input": "30 км"
                                    }
                                    ]
                               }


def test_create_org_not_found():
    db_reset()
    response = client.post("/orgs/",
                           json={"name": "Название организации", "warehouses": {"1000": 10, "20": 20, "30": 30}})
    assert response.status_code == 404
    assert response.json() == {"detail": "Хранилище 1000 не найдено"}


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


def test_get_specific_org():
    db_reset()
    response = client.get("/orgs/2")
    assert response.status_code == 200
    assert response.json() == {
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


def test_not_found_specific_org():
    db_reset()
    response = client.get("/orgs/200")
    assert response.status_code == 404
    assert response.json() == {"detail": "Организации с id 200 нет в базе данных"}


def test_get_specific_warehouse():
    db_reset()
    response = client.get("/warehouses/2")
    assert response.status_code == 200
    assert response.json() == {
        "warehouse_id": 2,
        "warehouse_name": "МНО 2",
        "bio_limit": 150,
        "plastic_limit": 50,
        "glass_limit": 0,
        "distance": [
            {
                "org_id": 1,
                "distance": 50
            }
        ]
    }


def test_not_found_specific_warehouse():
    db_reset()
    response = client.get("/warehouses/200")
    assert response.status_code == 404
    assert response.json() == {"detail": "Хранилища с id 200 нет в базе данных"}


def test_create_transfer():
    db_reset()
    response = client.post("/transfer_waste/?org_id=1&waste_type=bio&quantity=30")
    assert response.status_code == 200
    assert response.json() == {
        "organization_id": 1,
        "waste_type": "bio",
        "initial_quantity": 30,
        "transfer_data": [
            {
                "warehouse_id": 2,
                "warehouse_name": "МНО 2",
                "delivered_quantity": 30,
                "distance": 50
            }
        ]
    }


def test_transfer_bad_request():
    db_reset()
    response = client.post("/transfer_waste/?org_id=1&waste_type=biomio&quantity=30")
    assert response.status_code == 400
    assert response.json() == {"detail": "Неверный тип отходов. Укажите 'glass', 'plastic' или 'bio'"}


def test_transfer_too_much_waste():
    db_reset()
    response = client.post("/transfer_waste/?org_id=2&waste_type=bio&quantity=1000")
    assert response.status_code == 400
    assert response.json() == {
        "detail":
            "Невозможно переработать 350 из 1000 единиц отходов: места в хранилищах недостаточно. "
            "Запрос на отправку отходов отменен"}
