from pydantic import BaseModel, validator
from typing import List


class BaseArticle(BaseModel):
    id: int
    title: str
    text: str

    class Config:
        orm_mode = True


class Author(BaseModel):
    id: int
    name: str
    fullname: str
    article: List[BaseArticle]

    class Config:
        orm_mode = True


class AuthorCreate(BaseModel):
    id: int
    name: str
    fullname: str

    class Config:
        orm_mode = True


class AuthorUpdate(BaseModel):
    name: str
    fullname: str

    class Config:
        orm_mode = True


class ArticleCreate(BaseModel):
    id: int
    title: str
    text: str
    author: AuthorCreate

    @validator('title')
    def title_must_contain_space(cls, value):
        if value[0] != 'A':
            raise ValueError('title must start with letter A')
        return value

    @validator('text')
    def text_must_be_longer_then_20_letters(cls, value):
        if len(value) < 20:
            raise ValueError('text must be longer then 20 letters')
        return value

    class Config:
        orm_mode = True


class ArticleUpdate(BaseModel):
    title: str
    text: str
    author_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 44,
                "title": "A very nice Item",
                "text": "A very nice Item2",
                "author_id": 2,
            }
        }


article_create_examples = {
    "normal": {
        "description": "A **normal** item works correctly.",
        "value": {
            "id": 44,
            "title": "Normal title example ",
            "text": "Normal title example ",
            "author": {
                "id": 11,
                "name": "Author_name_1",
                "fullname": "Author_fullname_1",
            }
        },
    },
    "invalid": {
        "description": "Title too long",
        "value": {
            "id": 44,
            "title": "Title of invalid example",
            "text": "Text too short",
            "author": {
                "id": 11,
                "name": "Author_name_1",
                "fullname": "Author_fullname_1",
            }
        },

    }
}
