# referenced my website project bc i've done this backend fastapi setup before
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routes import breed_routes, player_routes, care_routes

app = FastAPI()

origins = [
    "http://localhost:8000",
    # insert cloudfront url here later
]
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["*"], 
    allow_headers=["*"]
)


app.include_router(breed_routes.breed_router)
app.include_router(player_routes.adopter_router)
app.include_router(care_routes.care_router)


handler = Mangum(app)