from pydantic import BaseModel
from typing import Optional


class PetOut(BaseModel):
    id: int
    name: str
    rarity: str
    value: float
    shiny_value: Optional[float]
    note: Optional[str]
    updated_at: str


class PetCreate(BaseModel):
    name: str
    rarity: str
    value: float = 0
    shiny_value: Optional[float] = None
    note: Optional[str] = None


class PetUpdate(BaseModel):
    value: float
    shiny_value: Optional[float] = None
    note: Optional[str] = None
    reason: Optional[str] = None


class HistoryOut(BaseModel):
    id: int
    pet_id: int
    pet_name: str
    old_value: float
    new_value: float
    old_shiny: Optional[float]
    new_shiny: Optional[float]
    changed_by: str
    reason: Optional[str]
    changed_at: str