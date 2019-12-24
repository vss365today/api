import os.path
import sqlite3
from typing import Dict, List, Optional

from src.core.config import load_app_config
from src.core.models.v1.Prompt import Prompt
from src.core.models.v1.Writer import Writer


__all__ = [
    "create_new_database",
    "create_prompt",
    "update_prompt",
    "delete_prompt",
    "create_subscription_email",
    "delete_subscription_email",
    "get_subscription_list",
    "is_auth_token_valid",
    "get_admin_user",
    "get_prompt_by_date",
    "get_prompt_years",
    "get_prompts_by_date",
    "get_prompts_by_writer",
    "get_writer_by_id",
    "get_writers_by_year",
    "get_writers_by_date",
    "search_for_prompt"
]


def __flatten_tuple_list(tup) -> list:
    """Flatten a list of tuples into a list of actual data."""
    return [item[0] for item in tup]


def __connect_to_db() -> sqlite3.Connection:
    """Create a connection to the database."""
    config = load_app_config()
    conn = sqlite3.connect(config["DB_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


def create_new_database() -> None:
    """Create a new database if needed."""
    try:
        # If the database exists and is loaded, this will succeed
        sql = "SELECT COUNT(*) FROM writers"
        with __connect_to_db() as db:
            db.execute(sql)

    # The database doesn't exist
    except sqlite3.OperationalError:
        # Get the db schema
        schema = os.path.abspath(
            os.path.join("db", "schema.sql")
        )
        with open(schema, "rt") as f:
            sql = f.read()

        # Create the database according to the schema
        with __connect_to_db() as db:
            db.executescript(sql)


def create_prompt(prompt: Dict[str, Optional[str]]) -> bool:
    """Record a new prompt."""
    sql = """
    INSERT INTO tweets (
        tweet_id, date, uid, content, word, media
    )
    VALUES (
        :tweet_id, :date, :uid, :content, :word, :media
    )
    """
    try:
        with __connect_to_db() as db:
            db.execute(sql, prompt)
            return True

    # A prompt with this ID already exists
    except sqlite3.IntegrityError as exc:
        print(f"Prompt creation exception: {exc}")
        print(prompt)
        return False


def create_subscription_email(addr: str) -> bool:
    """Add a subscription email address."""
    try:
        sql = "INSERT INTO emails (email) VALUES (:addr)"
        with __connect_to_db() as db:
            db.execute(sql, {"addr": addr.lower()})
        return True

    # Some error occurred
    except Exception as err:
        print(err)
        return False


def delete_prompt(prompt_id: str) -> None:
    """Delete an existing prompt."""
    sql = "DELETE FROM tweets WHERE tweet_id = :tweet_id"
    with __connect_to_db() as db:
        db.execute(sql, {"tweet_id": prompt_id})


def delete_subscription_email(addr: str) -> bool:
    """Remove a subscription email address."""
    sql = "DELETE FROM emails WHERE email = :addr"
    with __connect_to_db() as db:
        db.execute(sql, {"addr": addr})
    return True


def is_auth_token_valid(user: str, token: str) -> bool:
    """Check if the given username and auth token combo is valid."""
    sql = "SELECT 1 FROM users WHERE username = :user AND token = :token"
    with __connect_to_db() as db:
        return bool(db.execute(sql, {"user": user, "token": token}).fetchone())


def find_existing_prompt(prompt_id: str) -> bool:
    """Find an existing prompt."""
    sql = "SELECT 1 FROM tweets WHERE tweet_id = :tweet_id"
    with __connect_to_db() as db:
        return bool(db.execute(sql, {"tweet_id": prompt_id}).fetchone())


def get_admin_user(user: str, password: str) -> Optional[sqlite3.Row]:
    sql = """SELECT username, token
    FROM users
    WHERE username = :user AND password = :password
    """
    with __connect_to_db() as db:
        user_record = db.execute(
            sql,
            {"user": user, "password": password}
        ).fetchone()
    if not user_record:
        return None

    # We have a user, update their last sign in date/time
    with __connect_to_db() as db:
        sql = """
        UPDATE users
        SET last_signin = date('now')
        WHERE username = :user
        """
        db.execute(sql, {"user": user})
    return user_record


def get_latest_prompt() -> List[Prompt]:
    """Get the newest prompt."""
    sql = """
    SELECT tweets.*, writers.handle AS writer_handle
    FROM tweets
        JOIN writers ON tweets.uid = writers.uid
    ORDER BY date DESC
    LIMIT 1
    """
    with __connect_to_db() as db:
        return [Prompt(record) for record in db.execute(sql)]


def get_prompt_years() -> List[str]:
    """Get a list of years of recorded prompts."""
    sql = """
    SELECT DISTINCT SUBSTR(date, 1, 4)
    FROM writer_dates
    WHERE SUBSTR(date, 1, 4) <= strftime('%Y','now')
    ORDER BY date ASC
    """
    with __connect_to_db() as db:
        r = db.execute(sql).fetchall()
    return __flatten_tuple_list(r)


def get_prompt_by_date(date: str) -> List[Prompt]:
    """Get a prompt tweet by the date it was posted."""
    sql = """
    SELECT tweets.*, writers.handle AS writer_handle
    FROM tweets
        JOIN writers ON writers.uid = tweets.uid
    WHERE tweets.date = :date
        AND :date <= date('now')
    """
    with __connect_to_db() as db:
        return [Prompt(record) for record in db.execute(sql, {"date": date})]


def get_prompts_by_writer(handle: str) -> List[Prompt]:
    """Get a prompt tweet by the writer who prompted it."""
    sql = """
    SELECT tweets.*, writers.handle AS writer_handle
    FROM tweets
        JOIN writers ON writers.uid = tweets.uid
    WHERE tweets.date <= date('now')
        AND writers.handle = :handle
    """
    with __connect_to_db() as db:
        return [
            Prompt(record) for record in db.execute(sql, {"handle": handle})
        ]


def get_subscription_list() -> list:
    """Get all emails in the subscription list."""
    sql = "SELECT email FROM emails"
    with __connect_to_db() as db:
        return __flatten_tuple_list(db.execute(sql).fetchall())


def get_writer_by_id(*, uid: str, handle: str) -> Optional[List[Writer]]:
    """Get Writer info by either their Twitter ID or handle."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date || '-01' AS date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE
        SUBSTR(writer_dates.date, 1, 8) <= strftime('%Y-%m','now') AND
        (writers.uid = :uid OR UPPER(handle) == UPPER(:handle))
    ORDER BY date DESC
    """
    with __connect_to_db() as db:
        return [
            Writer(writer)
            for writer in db.execute(sql, {"uid": uid, "handle": handle})
        ]


def get_writers_by_year(year: str) -> List[Writer]:
    """Get a list of all Writers for a particular year."""
    sql = """
    SELECT writers.uid, handle, writer_dates.date || '-01' AS date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE SUBSTR(date, 1, 4) = :year
        AND SUBSTR(date, 1, 8) <= strftime('%Y-%m','now')
    ORDER BY writer_dates.date ASC
    """
    with __connect_to_db() as db:
        return [Writer(writer) for writer in db.execute(sql, {"year": year})]


def get_writers_by_date(date: str) -> List[Writer]:
    """Get a Writer by the month-year they delievered the prompts. """
    sql = """
    SELECT writers.uid, handle, writer_dates.date || '-01' AS date
    FROM writers
        JOIN writer_dates ON writer_dates.uid = writers.uid
    WHERE writer_dates.date = :date
    """
    with __connect_to_db() as db:
        return [Writer(writer) for writer in db.execute(sql, {"date":  date})]


def get_prompts_by_date(date: str) -> List[Prompt]:
    """Get all prompts in a given date range."""
    sql = f"""
    SELECT tweets.*, writers.handle as writer_handle
    FROM tweets
        JOIN writers ON tweets.uid = writers.uid
    WHERE tweets.date <= date('now')
        AND SUBSTR(tweets.date, 1, 7) = :date
    ORDER BY tweets.date ASC
    """
    with __connect_to_db() as db:
        return [Prompt(prompt) for prompt in db.execute(sql, {"date": date})]


def search_for_prompt(word: str) -> List[Prompt]:
    """Search for prompts by partial or full word."""
    sql = """
    SELECT tweets.*, writers.handle AS writer_handle
    FROM tweets
        JOIN writers ON writers.uid = tweets.uid
    WHERE tweets.date <= date('now')
        AND tweets.word LIKE '%' || :word || '%'
    ORDER BY UPPER(word)
    """
    with __connect_to_db() as db:
        return [Prompt(record) for record in db.execute(sql, {"word": word})]


def update_prompt(prompt: Dict[str, Optional[str]]) -> None:
    """Update an existing prompt."""
    sql = """
    UPDATE tweets
    SET
        tweet_id = :tweet_id,
        date = :date,
        content = :content,
        word = :word,
        media =  :media
    WHERE tweet_id = :tweet_id
    """
    with __connect_to_db() as db:
        db.execute(sql, prompt)
