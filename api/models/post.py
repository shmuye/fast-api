from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    id: int


class CommentIn(BaseModel):
    body: str
    postId: int

class Comment(CommentIn):
    id: int


class UserPostWithComment(BaseModel):
    post: UserPost
    comment: list[Comment]