from pydantic import BaseModel, Field
from faker import Faker

# from sqlmodel import SQLModel
fake = Faker("ko_KR")


class UserOut(BaseModel):
    id: int
    name: str


class PostCommentOut(BaseModel):
    id: int
    text: str
    user_id: int
    user: UserOut | None = Field(None)


class TagOut(BaseModel):
    id: int
    name: str


class PostTagOut(BaseModel):
    post_id: int
    tag_id: int
    tag: TagOut


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    comments: list[PostCommentOut] | None = Field(None)
    user: UserOut | None = Field(None)
    tags: list[PostTagOut] | None = Field(None)


class PostsOut(BaseModel):
    total_count: int
    data: list[PostOut]


class PostCommentIn(BaseModel):
    text: str = Field(fake.catch_phrase())
    user_id: int = Field(fake.pyint(1, 10))


class PostIn(BaseModel):
    title: str = Field(examples=[fake.job()])
    content: str = Field(examples=[fake.catch_phrase()])
    user_id: int = Field(examples=[fake.pyint(1, 10)])
    tags: list[str] | None = Field(
        None,
        examples=[
            [fake.job().split()[0], fake.job().split()[0], fake.job().split()[0]]
        ],
    )
