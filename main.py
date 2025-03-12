from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import privileged_routes
from app.endpoints import clientadmin_routes

app = FastAPI()

origins = ["https://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(privileged_routes.router, prefix="/privileged")
app.include_router(clientadmin_routes.router, prefix="/admin")


@app.get("/")
def root():
    return {"message": "Asset Tracking System API is running!"}