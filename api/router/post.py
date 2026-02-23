import logging
from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException

from api.database import comment_table, database, like_table, post_table
from api.models.post import (
    Comment,
    CommentIn,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComment,
)
from api.models.user import User
from api.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

select_post_and_likes = sqlalchemy.select(
    post_table,
    sqlalchemy.func.count(like_table.c.id).label("likes")
).select_from(post_table.outerjoin(like_table)).group_by(post_table.c.id)

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
    query = select_post_and_likes.order_by(sqlalchemy.desc('likes'))
    
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
    logger.info(f"Getting post with id {post_id} and its comments")
    query = select_post_and_likes.where(post_table.c.id == post_id)

    logger.debug(f"Executing query: {query}")

    post = await database.fetch_one(query)

    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    return {
        "post": post,
        "comment": await get_all_post_comments(post_id)
    }

@router.post('/like', status_code=201)
async def like_post(like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"User {current_user.id} is liking post {like.post_id}")
    post = await find_post(like.post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail='post not found')

    data = {**like.model_dump(), "user_id": current_user.id }
    query = like_table.insert().values(data)

    logger.debug(f"Executing query: {query}")

    last_record_id = await database.execute(query)
    return { **data, "id": last_record_id}


