from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, func
from sqlalchemy.orm import selectinload
from database import get_db, AsyncSession as Session
from models import Post, PostComment, PostTag, Tag
from schemas import PostsOut, PostOut, PostIn, PostCommentIn
from logger import LoggingAPIRoute

router = APIRouter(route_class=LoggingAPIRoute)


@router.get("/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)) -> PostOut:
    stmt = (
        select(Post)
        .options(
            selectinload(Post.user),
            selectinload(Post.comments).selectinload(PostComment.user),
            selectinload(Post.tags).selectinload(PostTag.tag),
        )
        .where(Post.id == post_id)
    )
    post = (await db.exec(stmt)).first()
    """
    -- posts id select
    SELECT posts.id, posts.user_id, posts.title, posts.content
    FROM posts
    WHERE posts.id = %s

    -- users id(posts.user_id) select
    SELECT users.id AS users_id, users.name AS users_name
    FROM users
    WHERE users.id IN (%s)

    -- posts_tags post_id(posts.id) select
    SELECT
        posts_tags.post_id AS posts_tags_post_id,
        posts_tags.tag_id AS posts_tags_tag_id
    FROM posts_tags
    WHERE posts_tags.post_id IN (%s)

    -- tags id(posts_tags.tag_id) select
    SELECT tags.id AS tags_id, tags.name AS tags_name
    FROM tags
    WHERE tags.id IN (%s, %s)

    -- posts_comments post_id(posts.id) select
    SELECT
        posts_comments.post_id AS posts_comments_post_id,
        posts_comments.id AS posts_comments_id,
        posts_comments.text AS posts_comments_text,
        posts_comments.user_id AS posts_comments_user_id
    FROM posts_comments
    WHERE posts_comments.post_id IN (%s)

    -- users id(posts_comments.user_id) select
    SELECT users.id AS users_id, users.name AS users_name
    FROM users
    WHERE users.id IN (%s, %s, %s)
    """

    # print(post.tags)
    # result = PostOut(**post.model_dump())
    # result.comments = post.comments
    # result.user = post.user
    # result.tags = []
    # for row in post.tags:
    #     result.tags.append(TagOut(**row.tag.model_dump()))

    return post


@router.get("")
async def get_posts(db: Session = Depends(get_db)) -> PostsOut:
    stmt = select(Post).options(
        selectinload(Post.user),
        selectinload(Post.comments).options(selectinload(PostComment.user)),
        selectinload(Post.tags).selectinload(PostTag.tag),
    )
    stmt = stmt.limit(5).offset(0)
    posts = (await db.exec(stmt)).all()
    result = PostsOut(data=[], total_count=len(posts))
    for post in posts:
        result.data.append(post)

    """
    -- posts select
    SELECT posts.id, posts.user_id, posts.title, posts.content
    FROM posts
    LIMIT %s, %s
    
    -- users id(posts.user_id) select
    SELECT users.id AS users_id, users.name AS users_name
    FROM users
    WHERE users.id IN (%s, %s, %s, %s, %s)

    -- posts_tags post_id(posts.id) select
    SELECT posts_tags.post_id AS posts_tags_post_id, posts_tags.tag_id AS posts_tags_tag_id
    FROM posts_tags
    WHERE posts_tags.post_id IN (%s, %s, %s, %s, %s)

    -- tags id(posts_tags.tag_id) select
    SELECT tags.id AS tags_id, tags.name AS tags_name
    FROM tags
    WHERE tags.id IN (%s, %s, %s, %s, %s, %s, %s, %s, %s)

    -- posts_comments post_id(posts.id) select
    SELECT posts_comments.post_id AS posts_comments_post_id, posts_comments.id AS posts_comments_id, posts_comments.text AS posts_comments_text, posts_comments.user_id AS posts_comments_user_id
    FROM posts_comments
    WHERE posts_comments.post_id IN (%s, %s, %s, %s, %s)

    -- users id(posts_comments.user_id) select
    SELECT users.id AS users_id, users.name AS users_name
    FROM users
    WHERE users.id IN (%s, %s, %s, %s, %s)
    """
    return result


@router.post("")
async def create_post(post: PostIn, db: Session = Depends(get_db)) -> PostOut:
    post_dict = post.model_dump()
    tags = post_dict.pop("tags", [])
    add_post = Post(**post_dict)

    stmt = select(Tag).where(Tag.name.in_(tags))
    select_tags = []
    for tag in (await db.exec(stmt)).all():
        select_tags.append(tag.name)
        add_post.tags.append(PostTag(tag=tag))
    for tag in list(set(tags) - set(select_tags)):
        add_post.tags.append(PostTag(tag=Tag(name=tag)))

    db.add(add_post)
    await db.commit()
    # await db.refresh(add_post)

    """
    -- tags body.tags select
    SELECT tags.id, tags.name
    FROM tags
    WHERE tags.name IN (%s, %s, %s)

    -- posts insert    
    INSERT INTO posts (user_id, title, content)
    VALUES (%s, %s, %s)

    -- tags not select insert
    INSERT INTO tags (name)
    VALUES (%s), (%s)
    RETURNING tags.id, tags.id AS id__1

    -- posts_tags insert
    INSERT INTO posts_tags (tag_id, post_id) VALUES (%s, %s)
    """

    result = PostOut(**add_post.model_dump(), comments=[], tags=[])
    for row in add_post.tags:
        result.tags.append(row)

    return result


@router.put("/{post_id}")
async def update_post(
    post_id: int, param: PostIn, db: Session = Depends(get_db)
) -> PostOut:
    stmt = (
        select(Post)
        .options(
            selectinload(Post.tags).selectinload(PostTag.tag),
        )
        .where(Post.id == post_id)
    )
    post = (await db.exec(stmt)).first()
    post.title = param.title
    post.content = param.content

    # tag 와 기존 tag 비교 해서 없는 tag 삭제
    if param.tags:
        tags_list = []
        for row in post.tags:
            if row.tag.name in param.tags:
                tags_list.append(row.tag.name)
            else:
                await db.delete(row)

        param.tags = list(set(param.tags) - set(tags_list))

    # 추가된 tag 가 있다면 변경
    if param.tags:
        stmt = select(Tag).where(Tag.name.in_(param.tags))
        select_tags = []
        for tag in (await db.exec(stmt)).all():
            select_tags.append(tag.name)
            post.tags.append(PostTag(tag=tag))
        for tag in list(set(param.tags) - set(select_tags)):
            post.tags.append(PostTag(tag=Tag(name=tag)))

    await db.commit()
    await db.refresh(post)

    """
    SELECT posts.id, posts.user_id, posts.title, posts.content
    FROM posts
    WHERE posts.id = %s

    SELECT posts_tags.post_id AS posts_tags_post_id, posts_tags.tag_id AS posts_tags_tag_id
    FROM posts_tags
    WHERE posts_tags.post_id IN (%s)

    SELECT tags.id AS tags_id, tags.name AS tags_name
    FROM tags
    WHERE tags.id IN (%s, %s, %s, %s)

    UPDATE posts SET title=%s, content=%s WHERE posts.id = %s

    DELETE FROM posts_tags WHERE posts_tags.tag_id = %s AND posts_tags.post_id = %s

    SELECT tags.id, tags.name
    FROM tags
    WHERE tags.name IN (%s, %s, %s)

    INSERT INTO tags (name) VALUES (%s), (%s) RETURNING tags.id, tags.id AS id__1

    INSERT INTO posts_tags (tag_id, post_id) VALUES (%s, %s)

    COMMIT 

    SELECT posts.id, posts.user_id, posts.title, posts.content
    FROM posts
    WHERE posts.id = %s

    SELECT posts_tags.tag_id AS posts_tags_tag_id, posts_tags.post_id AS posts_tags_post_id
    FROM posts_tags
    WHERE %s = posts_tags.post_id

    SELECT tags.id AS tags_id, tags.name AS tags_name
    FROM tags
    WHERE tags.id IN (%s, %s, %s)
    """

    result = PostOut(**post.model_dump(), comments=[], tags=[])
    for row in post.tags:
        result.tags.append(row)

    return result


@router.post("/{post_id}/comment")
async def create_post_comment(
    post_id: int, comment: PostCommentIn, db: Session = Depends(get_db)
):
    add_comment = PostComment(**comment.model_dump(), post_id=post_id)
    db.add(add_comment)

    await db.commit()
    # await db.refresh(add_comment)

    """
    INSERT INTO posts_comments (text, post_id, user_id) VALUES (%s, %s, %s)
    """

    return add_comment
