from pydantic import BaseModel

class Message(BaseModel):
    text: str = "Text to Speech documentation"