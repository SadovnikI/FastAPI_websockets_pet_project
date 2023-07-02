import time

from fastapi import FastAPI, Depends, Body
from starlette.websockets import WebSocketDisconnect

import schemas
import models
from fastapi import WebSocket
from fastapi.responses import HTMLResponse
from manager.websocket_manager import websocket_manager
from database import engine, get_session
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# ///////////////

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Posts</title>
    </head>
    <body>
        <h1>Post List</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="postTitle" autocomplete="off">Input Title</input>
            <input type="text" id="postText" autocomplete="off">Input Text</input>
            <input type="text" id="postUserId" autocomplete="off">Input Text</input>
            <button>Create new post</button>
        </form>
        <ul id='messages'>
            <li id='progress'>Empty</li>
        </ul>
        <script>
            function sendMessage(event) {
            
            function getRandomInt(max) {
              return Math.floor(Math.random() * max);
            }
            var post_author = document.getElementById("postUserId").value
            var ws = new WebSocket(`ws://localhost:8000/article/${post_author}/ws`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
                document.getElementById("progress").innerHTML = "Finished"
            };
            
                var post_title = document.getElementById("postTitle").value
                var post_text = document.getElementById("postText").value
                
                var data = {
                    "id": getRandomInt(10000),
                    "title": post_title,
                    "text": post_text,
                    "author_id": post_author
                }
                console.log(data)
                ws.onopen = () => ws.send(JSON.stringify(data));

                document.getElementById("progress").innerHTML = "Started"
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/article/{token}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    session=Depends(get_session)
):
    await websocket_manager.update_connection(websocket, str(token))
    try:
        while True:
            data = await websocket.receive_json()
            article = models.Article(**data)
            session.add(article)
            session.commit()
            session.refresh(article)
            time.sleep(3)
            article.status = models.StatusEnum.finished.value
            session.commit()
    except WebSocketDisconnect:
        websocket_manager.remove_connections(websocket, str(token))


@app.get("/authors")
def getAuthors(session: Session = Depends(get_session)):
    authors = session.query(models.Author).all()
    return authors


@app.post("/author")
def addAuthor(author: schemas.AuthorCreate, session=Depends(get_session)):
    author = models.Author(**author.dict())
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@app.get("/author/{id}")
def getAuthor(id: int, session: Session = Depends(get_session)):
    author = session.query(models.Author).get(id)
    return author


@app.put("/author/{id}")
def updateAuthor(id: int, author: schemas.AuthorUpdate, session=Depends(get_session)):
    authorObject = session.query(models.Author).get(id)
    authorObject.name = author.name
    authorObject.fullname = author.fullname
    session.commit()
    return authorObject


@app.delete("/author/{id}")
def deleteAuthor(id: int, session=Depends(get_session)):
    authorObject = session.query(models.Author).get(id)
    session.delete(authorObject)
    session.commit()
    session.close()
    return 'Author was deleted'


@app.get("/{author_id}/articles")
def getArticles(author_id:int, session: Session = Depends(get_session)):
    articles = session.query(models.Article).filter(models.Article.author_id == author_id)
    return articles


@app.post("/article")
def addArticle(article: schemas.ArticleCreate = Body(..., examples=schemas.article_create_examples),
               session=Depends(get_session)):
    article_data = article.dict()
    article = models.Article(
        id=article_data.get('id'), title=article_data.get('title'),
        text=article_data.get('title'), author_id=article_data['author']['id'])
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


@app.get("/article/{id}")
def getArticle(id: int, session: Session = Depends(get_session)):
    article = session.query(models.Article).get(id)
    return article


@app.put("/article/{id}")
def updateArticle(id: int, article: schemas.ArticleUpdate, session=Depends(get_session)):
    articleObject = session.query(models.Article).get(id)
    articleObject.title = article.title
    articleObject.text = article.text
    articleObject.author_id = article.author_id
    session.commit()
    return articleObject


@app.delete("/article/{id}")
def deleteArticle(id: int, session=Depends(get_session)):
    articleObject = session.query(models.Article).get(id)
    session.delete(articleObject)
    session.commit()
    session.close()
    return 'Article was deleted'
