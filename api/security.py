import datetime
import logging
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from api.database import database, user_table

logger = logging.getLogger(__name__)

SECRET_KEY = "1687279dcea2670abec685e93d478671"
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
)

def access_token_expire_minutes()-> int:
    return 30 

def confirm_token_expire_minutes()-> int:
    return 1440 # 24 hours


def create_access_token(email: str):
    logger.debug("creating access token", extra={"email": email})
    
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )


    jwt_data = {
        "sub": email,
        "exp": expire,
        "type": "access"
    }

    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_confirmation_token(email: str):
    logger.debug("creating access token", extra={"email": email})
    
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=confirm_token_expire_minutes()
    )


    jwt_data = {
        "sub": email,
        "exp": expire,
        "type": "confirmation"
    }

    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_subject_for_token_type(token: str, token_type: Literal["access", "confirmation"]) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       
        
    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token has expired") from e
    except JWTError as e:
        raise create_credentials_exception("invalid Token") from e
    
    email = payload.get('sub')
    if email is None:
        raise create_credentials_exception("Token is missing 'sub' field")
    token_type = payload.get('type')

    if type is None or token_type != type:
        raise create_credentials_exception(f"Token is not of type {type}")
        
    return email


pwd_context = CryptContext(schemes=['bcrypt'])

def get_password_hash(password: str):
    return pwd_context.hash(password)
  
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    
    logger.debug("fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result =  await database.fetch_one(query)

    if result:
        return result

async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise create_credentials_exception("User not found")
    if not verify_password(password, user.password):
        raise create_credentials_exception("Incorrect email or password")
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme())]):
    email = get_subject_for_token_type(token, "access")
    user = await get_user(email=email)
    if not user:
        raise create_credentials_exception("User not found")
    return user
