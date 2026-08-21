"""Database connection helper for the museums project.

The original project used fixed PostgreSQL credentials. This version keeps the
same defaults so existing scripts still work, while also allowing environment
variables for easier deployment on AutoDL or local machines.
"""

from __future__ import annotations

import os
from sqlalchemy import create_engine


def get_engine():
    user = os.getenv("MUSEUM_DB_USER", "postgres")
    password = os.getenv("MUSEUM_DB_PASSWORD", "wodegnome")
    host = os.getenv("MUSEUM_DB_HOST", "localhost")
    port = os.getenv("MUSEUM_DB_PORT", "5432")
    db_name = os.getenv("MUSEUM_DB_NAME", "museums_db")
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
    return engine
