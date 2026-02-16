from fastapi import APIRouter, HTTPException

from api.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComment,
)

router = APIRouter()

post_table = {}

comment_table = {}

def find_post(postId: int):
    return post_table.get(postId)

@router.post('/post', response_model=UserPost, status_code=201)
def createPost(post: UserPostIn):

    data = post.model_dump()

    last_record_id = len(post_table)

    new_post = { **data, "id": last_record_id}

    post_table[last_record_id] = new_post

    return new_post

@router.get('/post', response_model=list[UserPost])
async def get_all_posts():
    return list(post_table.values())


@router.post('/comment', response_model=Comment, status_code=201)
def createComment(comment:CommentIn ):

    post = find_post(comment.postId)

    if not post:

        raise HTTPException(status_code=404, detail='post not found')


    data = comment.model_dump()

    last_record_id = len(comment_table)
    
    new_comment = { **data, "id": last_record_id}

    comment_table[last_record_id] = new_comment

    return new_comment


@router.get('/post/{postId}/comment', response_model=list[Comment])
async def get_all_post_comments(postId: int):

    return [
        comment for comment in comment_table.values() if comment['postId'] == postId
    ]

@router.get("/post/{postId}", response_model=UserPostWithComment)
async def get_post_with_comments(postId: int):
    post = find_post(postId)

    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    return {
        "post": post,
        "comment": await get_all_post_comments(postId)
    }