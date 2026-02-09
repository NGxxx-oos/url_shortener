import logging
from typing import Optional
from app.database import get_db_connection
from app.utils import generate_short_code

logger = logging.getLogger(__name__)

def create_short_link(original_url: str, custom_code: Optional[str] = None) -> str:
    with get_db_connection() as conn:
        if custom_code:
            # Check if custom code exists
            cursor = conn.execute("SELECT 1 FROM links WHERE short_code = ?", (custom_code,))
            if cursor.fetchone():
                raise ValueError(f"Short code '{custom_code}' already exists")
            short_code = custom_code
        else:
            # Generate unique code
            while True:
                short_code = generate_short_code()
                cursor = conn.execute("SELECT 1 FROM links WHERE short_code = ?", (short_code,))
                if not cursor.fetchone():
                    break
        
        conn.execute(
            "INSERT INTO links (original_url, short_code) VALUES (?, ?)",
            (original_url, short_code)
        )
        conn.commit()
        logger.info(f"Created short link: {original_url} -> {short_code}")
        return short_code

def get_original_url(short_code: str) -> Optional[str]:
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT original_url FROM links WHERE short_code = ?", (short_code,))
        row = cursor.fetchone()
        if row:
            return row["original_url"]
        return None

def update_short_link(short_code: str, new_url: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("UPDATE links SET original_url = ? WHERE short_code = ?", (new_url, short_code))
        conn.commit()
        return cursor.rowcount > 0

def delete_short_link(short_code: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM links WHERE short_code = ?", (short_code,))
        conn.commit()
        return cursor.rowcount > 0
