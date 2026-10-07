from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.database import Base

config = context.config
config.set_main_option("sqlalchemy.url", "sqlite:///./floora.db")
target_metadata = Base.metadata
with config.engine.begin() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
