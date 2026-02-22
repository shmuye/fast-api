import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException

from api.database import comment_table, database, post_table
from api.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComment,
)
from api.models.user import User
from api.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)

@router.post('/', response_model=UserPost, status_code=201)
async def createPost(post: UserPostIn, current_user: Annotated[User, get_current_user ]):
       
    
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return  { **data, "id":last_record_id}

@router.get('/', response_model=list[UserPost])
async def get_all_posts():

    logger.info("Getting all posts")
    query = post_table.select()
    
    logger.debug(query)

    return await database.fetch_all(query)


@router.post('/comment', response_model=Comment, status_code=201)
async def createComment(comment:CommentIn, current_user: Annotated[User, get_current_user]):
    
    post = await find_post(comment.post_id)
    
    if not post:

        raise HTTPException(status_code=404, detail='post not found')


    data = {**comment.model_dump(), "user_id": current_user.id }
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    
    return { **data, "id": last_record_id}

@router.get('/{post_id}/comment', response_model=list[Comment])
async def get_all_post_comments(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)
   
@router.get("/{post_id}", response_model=UserPostWithComment)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    return {
        "post": post,
        "comment": await get_all_post_comments(post_id)
    }