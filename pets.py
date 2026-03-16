from fastapi import APIRouter, HTTPException
from typing import Optional, List
from database import get_conn
from schemas import PetOut

router = APIRouter()


@router.get("/", response_model=List[PetOut])
def get_all_pets(
    rarity: Optional[str] = None,
    sort: Optional[str] = "value_desc",
):
    """
    Get all pets. Optional filters:
    - rarity: Limited | Secret | Legendary | Rare
    - sort: value_desc | value_asc | name_asc | name_desc
    """
    conn = get_conn()
    cur = conn.cursor()

    query = "SELECT * FROM pets"
    params = []

    if rarity:
        query += " WHERE rarity = ?"
        params.append(rarity)

    order_map = {
        "value_desc": "value DESC",
        "value_asc":  "value ASC",
        "name_asc":   "name ASC",
        "name_desc":  "name DESC",
    }
    order = order_map.get(sort, "value DESC")
    query += f" ORDER BY {order}"

    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{pet_id}", response_model=PetOut)
def get_pet(pet_id: int):
    """Get a single pet by ID."""
    conn = get_conn()
    row = conn.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Pet not found")
    return dict(row)
