from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    id: int
    user_id: int
    model_config = {
       "from_attributes": True
    }


class CommentIn(BaseModel):
    body: str
    post_id: int

class Comment(CommentIn):
    id: int
    user_id: int
    model_config = {
       "from_attributes": True
    }



class UserPostWithComment(BaseModel):
    post: UserPost
    comment: list[Comment]