import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from database import get_db, init_db, AsyncSession as Session
from models import Post, User, PostComment, Tag, PostTag
from faker import Faker
import random
from api import api_router

fake = Faker("ko_KR")
app = FastAPI()

app.include_router(api_router)


@app.get("/init")
async def create_database(db: Session = Depends(get_db)):
    await init_db()

    users = [{"name": fake.name()} for _ in range(10)]
    for user in users:
        print(user)
        add_user = User(**user)
        db.add(add_user)
    await db.commit()

    posts = [
        {
            "user_id": fake.pyint(1, 10),
            "title": fake.job(),  # fake.sentence()
            "content": fake.catch_phrase(),  # fake.paragraph()
        }
        for _ in range(30)
    ]
    for post in posts:
        add_post = Post(**post)
        db.add(add_post)
    await db.commit()

    taglist = list(set([fake.job().split()[0] for _ in range(100)]))

    tags = [{"name": taglist[i]} for i in range(30)]
    for tag in tags:
        add_tag = Tag(**tag)
        db.add(add_tag)
    await db.commit()

    tag_ids = list(range(1, 31))
    for post_id in range(1, 31):
        for tag_id in random.sample(tag_ids, random.randint(0, 5)):
            add_post_tag = PostTag(post_id=post_id, tag_id=tag_id)
            db.add(add_post_tag)
    await db.commit()

    comments = [
        {
            "post_id": fake.pyint(1, 30),
            "user_id": fake.pyint(1, 10),
            "text": fake.catch_phrase(),  # fake.sentence()
        }
        for _ in range(50)
    ]
    for comment in comments:
        add_comment = PostComment(**comment)
        db.add(add_comment)
    await db.commit()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8100, reload=True)
