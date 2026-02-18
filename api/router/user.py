import logging

from fastapi import APIRouter, HTTPException

from api.database import database, user_table
from api.models.user import UserIn
from api.security import get_password_hash, get_user

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
