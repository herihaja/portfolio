from .application import app
from .database import init_db
from .routes import router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app_instance):
    # startup phase
    init_db()

    yield

app.router.lifespan_context = lifespan
app.include_router(router)
