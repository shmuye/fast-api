import logging

from fastapi import APIRouter, HTTPException

from api.database import database, user_table
from api.models.user import UserIn
from api.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_subject_for_token_type,
    get_user,
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post('/register', status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException (
            status_code=400,
            detail="A user with that email already exists"
        )
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    logger.debug(query)

    await database.execute(query)

    return { "detail": "User created"}

@router.post('/token')
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"accessToken": access_token, "token_type": "bearer"}

@router.get('/confirm/{token}')
async def confirm(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = user_table.update().where(user_table.c.email == email).values(confirmed=True)

    logger.debug(query)
    await database.execute(query)
    return {"detail": "Email confirmed"}
