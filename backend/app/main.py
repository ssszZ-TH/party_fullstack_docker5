from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.database import database


load_dotenv()

# Define lifespan event handler for FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database when the application starts
    await database.connect()
    # Yield control back to FastAPI to handle requests
    yield
    # Disconnect from the database when the application shuts down
    await database.disconnect()

# Initialize FastAPI app with lifespan event handler
app = FastAPI(lifespan=lifespan)

# Configure CORS to allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message": "FastAPI Backend", "github": "https://github.com/ssszZ-TH/party_fullstack_docker4"}