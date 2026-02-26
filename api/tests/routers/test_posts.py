
import pytest
from httpx import AsyncClient

from api import security


async def create_post(body: str, async_client: AsyncClient, logged_in_token: str) -> dict:
    
    response = await async_client.post(
        '/post', 
        json={"body": body}, 
        headers={
            "Authorization": f"Bearer {logged_in_token}"
    })
    return response.json()

async def create_comment(body: str,post_id: int, async_client: AsyncClient, logged_in_token: str) -> dict:
    
    response = await async_client.post(
        '/comment', 
        json={"body": body, "post_id": post_id},
        headers={
            "Authorization": f"Bearer {logged_in_token}"
        }
        )
    return response.json()

async def like_post(post_id: int, async_client: AsyncClient, logged_in_token: str) -> dict:
    
    response = await async_client.post(
        '/like', 
        json={"post_id": post_id},
        headers={ "Authorization": f"Bearer {logged_in_token}" }
)
    return response.json()

@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return await create_post('Test Post', async_client, logged_in_token)


@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict, logged_in_token: str):
    return await create_comment('Greate Post', created_post['id'], async_client, logged_in_token)


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient, confirmed_user: dict, logged_in_token: str):

    body = "Test Post"
    response = await async_client.post(
        '/post', 
        json={ "body": body},
        headers={
            "Authorization": f"Bearer {logged_in_token}"
        }
        )

    assert response.status_code == 201
    assert { "id": 1, "body": body, 'user_id': confirmed_user['id']}.items() <= response.json().items()

@pytest.mark.anyio
async def test_like_post(async_client: AsyncClient, created_post: dict, logged_in_token: str, registered_user: dict):
    response = await like_post(
        created_post['id'], 
        async_client, 
        logged_in_token
    )

    assert response.status_code == 201
    assert {
        "id": 1,
        "post_id": created_post['id'],
        "user_id": registered_user['id']
    }.items() <= response.json().items()

@pytest.mark.anyio
async def test_create_post_expired_token(
    async_client: AsyncClient, confirmed_user, mocker
):
    mocker.patch("api.security.access_token_expire_minutes", return_value=-1)
    token = security.create_access_token(confirmed_user['email'])

    response = await async_client.post(
        '/post', 
        json={ "body": "Test body"},
        headers={
            "Authorization": f"Bearer {token}"
        }
        )
    assert response.status_code == 401
    assert "Token has expired" in response.json()['detail']
    


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, confirmed_user: dict, created_post: str):

    body = "Test Post"
    response = await async_client.post('/comment', json={
         "body": body,
         "post_id": created_post['id'] 
        })

    assert response.status_code == 201
    assert { 
          "id": 1, 
          "body": body,
          "post_id": created_post['id'],
          "user_id": confirmed_user['id']

          }.items() <= response.json().items()

@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.post(
        '/post', 
         json={},
         headers={
            "Authorization": f"Bearer {logged_in_token}"
        }
        )

    assert response.status_code == 422

@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post):
    response = await async_client.get('/post')

    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
@pytest.mark.parametrize("sorting, expected_order", [
    ("newest", [2, 1]),  # Assuming the second created post has id 2 and the first has id 1
    ("oldest", [1, 2])   # Assuming the first created post has more likes than the second
])
async def test_get_all_posts_sorted(
    async_client: AsyncClient, 
    logged_in_token,
    sorting: str,
    expected_order: list[int]
    ):
    # Create 3 posts with some delay to ensure different timestamps
    await create_post('First Post', async_client, logged_in_token)
    await create_post('Second Post', async_client, logged_in_token)

    response = await async_client.get('/post', params={"sorting": sorting})

    assert response.status_code == 200
    actual_order = [post['id'] for post in response.json()]
    assert actual_order == expected_order


async def test_get_all_posts_sorted_likes(
    async_client: AsyncClient, 
    logged_in_token,
):
    # Create 3 posts with some delay to ensure different timestamps
    await create_post('First Post', async_client, logged_in_token)
    await create_post('Second Post', async_client, logged_in_token)
    await like_post(1, async_client, logged_in_token)
    response = await async_client.get('/post', params={"sorting": "most_liked"})

    assert response.status_code == 200
    expected_order = [1, 2]  # Assuming the first created post has more likes than the second
    actual_order = [post['id'] for post in response.json()]
    assert actual_order == expected_order
           

@pytest.mark.anyio
async def test_get_all_post_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comment")

    assert response.status_code == 200
    assert response.json() == [created_comment]

@pytest.mark.anyio
async def test_get_all_post_comments_empty(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comment")

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}")

    assert response.status_code == 200
    assert response.json() == {"post": {**created_post, "likes": 0}, "comment": [created_comment]}


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/post/2")

    assert response.status_code == 404
  
     