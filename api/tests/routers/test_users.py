import pytest
from fastapi import tasks
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        '/register', json={"email": email, "password": password}
        )

@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.com","1234")
    assert response.status_code == 201
    assert "User created" in response.json()['detail']

@pytest.mark.anyio
async def test_confirm_user(async_client: AsyncClient, mocker):
    spy = mocker.spy(tasks, "send_registration_email")
    response = await register_user(async_client, "test@exmaple.com","1234")
    confirmation_url = str(spy.call_args[1]['confirmation_url'])
    response = await async_client.get(confirmation_url)
    assert response.status_code == 200
    assert "Email confirmed" in response.json()['detail']

@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get('/confirm/invalidtoken')
    assert response.status_code == 401

@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch("api.security.confirm_token_expire_minutes", return_value=-1)
    spy =  mocker.spy(tasks, "send_user_registration_email")
    response = await register_user(async_client, "test@example.com","1234")
    
    confirmation_url = str(spy.spy_return)
    response = await async_client.get(confirmation_url)
    assert response.status_code == 401

    assert "Token has expired" in response.json()['detail']


@pytest.mark.anyio
async def test_register_existing_user(async_client: AsyncClient, registered_user):
    response = await register_user(async_client, registered_user['email'],"1234")
    assert response.status_code == 400
    assert "already exists" in response.json()['detail']

@pytest.mark.anyio
async def test_login_user_not_confirmed(async_client: AsyncClient, registered_user):
    response = await async_client.post(
        '/token', 
         json={
            "email": registered_user['email'], 
            "password": registered_user['password']
        })
    assert response.status_code == 401
  

@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post('/token', json={"email":"test@example.net", "password":"1234"})
    assert response.status_code == 401

@pytest.mark.anyio
async def test_login_existing_user(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post('/token', json={"email":confirmed_user['email'], "password":confirmed_user['password']})
    assert response.status_code == 200