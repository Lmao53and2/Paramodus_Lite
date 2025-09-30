from agno.db.sqlite import SqliteDb
import os

def load_session_storage():
    """Load appropriate storage based on environment"""
    storage_path = os.getenv("AGENT_STORAGE_PATH", "business_agent.db")
    return SqliteDb(
        table_name="client_sessions",
        db_file=storage_path
    )

def load_personality_storage():
    """Separate storage for personality analysis"""
    storage_path = os.getenv("PERSONALITY_STORAGE_PATH", "personality_data.db")
    return SqliteDb(
        table_name="personality_sessions",
        db_file=storage_path
    )

def load_task_storage():
    """Separate storage for task extraction"""
    storage_path = os.getenv("TASK_STORAGE_PATH", "task_data.db")
    return SqliteDb(
        table_name="task_sessions",
        db_file=storage_path
    )