from config import get_db_config

try:
    import psycopg2
except ImportError:
    # If psycopg2 is not installed, we handle it nicely in the UI later.
    psycopg2 = None


class DatabaseError(Exception):
    """Raised when database work cannot be completed."""


def get_connection():
    """Create a new PostgreSQL connection."""
    if psycopg2 is None:
        raise DatabaseError("psycopg2 is not installed")

    try:
        return psycopg2.connect(**get_db_config())
    except Exception as error:
        raise DatabaseError(str(error))


def init_db():
    """Create the required tables if they do not already exist."""
    # Our mini schema: one player can have many game sessions.
    sql = """
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER   NOT NULL,
            level_reached INTEGER   NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
    except DatabaseError:
        raise
    except Exception as error:
        raise DatabaseError(str(error))


def get_or_create_player(username):
    """Return the player id, creating the player row when needed."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Upsert = no duplicate usernames, but still gives us the id.
                cur.execute(
                    """
                    INSERT INTO players (username)
                    VALUES (%s)
                    ON CONFLICT (username)
                    DO UPDATE SET username = EXCLUDED.username
                    RETURNING id;
                    """,
                    (username,)
                )
                return cur.fetchone()[0]
    except DatabaseError:
        raise
    except Exception as error:
        raise DatabaseError(str(error))


def save_game_session(username, score, level_reached):
    """Save one finished game session."""
    try:
        player_id = get_or_create_player(username)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO game_sessions (player_id, score, level_reached)
                    VALUES (%s, %s, %s);
                    """,
                    (player_id, score, level_reached)
                )
    except DatabaseError:
        raise
    except Exception as error:
        raise DatabaseError(str(error))


def get_personal_best(username):
    """Return a player's best score, or 0 if the player has no games."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(MAX(score), 0)
                    FROM game_sessions
                    JOIN players ON players.id = game_sessions.player_id
                    WHERE players.username = %s;
                    """,
                    (username,)
                )
                return cur.fetchone()[0]
    except DatabaseError:
        raise
    except Exception as error:
        raise DatabaseError(str(error))


def get_top_scores(limit=10):
    """Return the top all-time scores."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Higher score wins; level/date are just nice tie-breakers.
                cur.execute(
                    """
                    SELECT players.username, game_sessions.score,
                           game_sessions.level_reached, game_sessions.played_at
                    FROM game_sessions
                    JOIN players ON players.id = game_sessions.player_id
                    ORDER BY game_sessions.score DESC,
                             game_sessions.level_reached DESC,
                             game_sessions.played_at ASC
                    LIMIT %s;
                    """,
                    (limit,)
                )
                return cur.fetchall()
    except DatabaseError:
        raise
    except Exception as error:
        raise DatabaseError(str(error))
