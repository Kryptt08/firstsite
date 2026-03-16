from fastapi import APIRouter, Query
from database import get_conn
from schemas import HistoryOut

router = APIRouter()


@router.get("/", response_model=list[HistoryOut])
def get_history(limit: int = Query(default=50, le=200)):
    """Get the most recent value changes across all pets."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM value_history ORDER BY changed_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{pet_id}", response_model=list[HistoryOut])
def get_pet_history(pet_id: int, limit: int = Query(default=20, le=100)):
    """Get value change history for a specific pet."""
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT * FROM value_history
        WHERE pet_id = ?
        ORDER BY changed_at DESC
        LIMIT ?
        """,
        (pet_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
