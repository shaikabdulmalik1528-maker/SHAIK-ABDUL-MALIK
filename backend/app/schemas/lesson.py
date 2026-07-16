from pydantic import BaseModel


class Lesson(BaseModel):
    id: int
    sign: str
    description: str
    meaning: str
    image: str
    difficulty: str