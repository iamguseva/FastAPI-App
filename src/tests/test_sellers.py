import pytest
from fastapi import status
from sqlalchemy import select

from src.models import essences



# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    data = {"first_name": "james", "last_name": "bond", "email": "JamesBond@mail.com", "password": "password"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    all_sellers = await db_session.execute(select(essences.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 1


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller1 = essences.Seller(id=1, first_name="James", last_name="Bond", email="JamesBond@mail.com", password="password")
    seller2 = essences.Seller(id=2, first_name="Harry", last_name="Potter", email="HarryPotter@mail.com" , password="password")


    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [{"id": seller1.id, "first_name": "James", "last_name": "Bond", "email": "JamesBond@mail.com"},
                  {"id": seller2.id, "first_name": "Harry", "last_name": "Potter", "email": "HarryPotter@mail.com"},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):

    seller = essences.Seller(id=1, first_name="James", last_name="Bond", email="JamesBond@mail.com", password="password")
    db_session.add(seller)
    
    book = essences.Book(id=333, author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=1)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {"id": seller.id,
                               "first_name": "James",
                               "last_name": "Bond",
                               "email": "JamesBond@mail.com",
                               "books": [{
                                    "id": 333,
                                    "author": "Pushkin",
                                    "title": "Eugeny Onegin",
                                    "year": 2001,
                                    "count_pages": 104
                                    }]
                               }

# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):

    seller = essences.Seller(id=1, first_name="James", last_name="Bond", email="JamesBond@mail.com", password="password")

    db_session.add(seller)
    
    book = essences.Book(id=333, author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=1)

    db_session.add(book)

    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(essences.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0
    
    all_sellers = await db_session.execute(select(essences.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0
    
    all_seller_books = await db_session.execute(select(essences.Book).where(essences.Book.seller_id == seller.id))
    res = all_seller_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):

    seller = essences.Seller(id=1, first_name="James", last_name="Bond", email="JamesBond@mail.com", password="password")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={"first_name": "james", "last_name": "bond", "email": "JamesBond@mail.com", "id": seller.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(essences.Seller, seller.id)
    assert res.first_name == "james"
    assert res.last_name == "bond"
    assert res.email == "JamesBond@mail.com"
    assert res.id == seller.id
    
    
    
