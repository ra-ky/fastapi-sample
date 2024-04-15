from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)
    name: str
    comments: list["PostComment"] = Relationship(back_populates="user")
    posts: list["Post"] = Relationship(back_populates="user")


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int = Field(primary_key=True, index=True)
    name: str = Field(unique=True, index=True)

    posts: list["PostTag"] = Relationship(back_populates="tag")


class PostTag(SQLModel, table=True):
    __tablename__ = "posts_tags"

    tag_id: int = Field(primary_key=True, foreign_key="tags.id")
    post_id: int = Field(primary_key=True, foreign_key="posts.id")

    tag: Tag = Relationship(back_populates="posts")
    post: "Post" = Relationship(back_populates="tags")


class PostComment(SQLModel, table=True):
    __tablename__ = "posts_comments"

    id: int = Field(primary_key=True)
    text: str
    post_id: int = Field(foreign_key="posts.id")
    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="comments")
    post: "Post" = Relationship(back_populates="comments")


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str
    content: str
    comments: list[PostComment] = Relationship(back_populates="post")
    tags: list[PostTag] = Relationship(back_populates="post")
    user: User = Relationship(back_populates="posts")
