### docker build and push

```
$ docker build -t fastapi .
$ docker tag fastapi localhost:5000/fastapi
$ docker push localhost:5000/fastapi
```