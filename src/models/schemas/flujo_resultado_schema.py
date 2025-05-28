from pydantic import BaseModel


class FlujoResultado(BaseModel):
    primas_recurrentes: list[float]
