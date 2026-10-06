from pydantic import BaseModel, ConfigDict


class AddInputModel(BaseModel):
    model_config = ConfigDict(strict=True)

    a: float
    b: float
    