from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.cards import router as cards_router
from api.routers.games import router as games_router
from api.routers.users import router as users_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(cards_router, prefix="/api/v1/cards", tags=["cards"])
app.include_router(games_router, prefix="/api/v1/game", tags=["game"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
