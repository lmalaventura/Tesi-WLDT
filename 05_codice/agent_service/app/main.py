from fastapi import FastAPI

from .config import get_settings
from .routes import router


settings = get_settings()

app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    description=(
        "Servizio per la traduzione di richieste in linguaggio naturale "
        "in chiamate REST verso il Persistence Service WLDT."
    ),
)

app.include_router(router)