from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. IMPORT SECURE ENGINE MODELS AND DECLARATIVE BASE
from app.database import Base, SQLALCHEMY_DATABASE_URL
# from app.models import User, Product, Inventory, CartItem, Order, OrderItem, Review, Category
# to register each model class or tables we could just import models instead of seperately importing each model
from app import models # Register all SQLAlchemy models for Alembic autogenerate
#now Base.metadata knows about each models since they are registered with Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# interpret the config file for Python logging.
# this line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. ASSIGN SECURE METADATA FOR AUTOGENERATE TO DETECT MODELS
# set this to Base.metadata instead of None!
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # We can override the alembic.ini connection string dynamically 
    # to load from a secure local environment variable
    configuration = config.get_section(config.config_ini_section) or {}

    configuration["sqlalchemy.url"] = SQLALCHEMY_DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()