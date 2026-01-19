import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 1. LOAD SECRETS & CONFIGURE LOGGING
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if not os.getenv("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY not found in environment variables!")

# 2. DEFINE DATA MODELS WITH VALIDATION
MAX_LIST_LENGTH = 5
MAX_STRING_LENGTH = 100

class WheelInput(BaseModel):
    characters: list[str]
    locations: list[str]
    genres: list[str]
    creatives: list[str]

    @field_validator("characters", "locations", "genres", "creatives", mode="before")
    @classmethod
    def validate_list(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_LIST_LENGTH:
            raise ValueError(f"List cannot have more than {MAX_LIST_LENGTH} items")
        if not v:
            raise ValueError("List cannot be empty")
        for item in v:
            if len(item) > MAX_STRING_LENGTH:
                raise ValueError(f"Each item must be {MAX_STRING_LENGTH} characters or less")
            if not item.strip():
                raise ValueError("Items cannot be empty or whitespace only")
        return [item.strip() for item in v]

class MoviePitch(BaseModel):
    title: str = Field(description="A catchy title for the movie")
    tagline: str = Field(description="A short, memorable tagline for the poster")
    pitch: str = Field(description="A 1-3 sentence pitch of the plot")

# 3. SETUP AGENT
pitch_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=MoviePitch,
    system_prompt=(
        "You are a creative Hollywood scriptwriter. "
        "Your goal is to blend potentially clashing genres, characters, and settings "
        "into a cohesive, exciting movie pitch."
    ),
)

# 4. INITIALIZE APP WITH RATE LIMITING
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Movie Pitch Generator Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS from environment variable
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# 5. THE ENDPOINT
@app.post("/generate-pitch", response_model=MoviePitch)
@limiter.limit("10/minute")
async def generate_pitch(request: Request, input_data: WheelInput):
    # Join the lists into comma-separated strings for the prompt
    char_str = ", ".join(input_data.characters)
    loc_str = ", ".join(input_data.locations)
    genre_str = ", ".join(input_data.genres)
    creative_str = ", ".join(input_data.creatives)

    # Construct a robust prompt
    prompt = (
        f"Create a movie pitch based on this specific combination:\n"
        f"- Mix these Genres: {genre_str}\n"
        f"- Featuring these Characters: {char_str}\n"
        f"- Set in these Locations: {loc_str}\n"
        f"- In the style of: {creative_str}\n\n"
        f"Ensure the plot makes sense despite the chaotic mix."
    )

    try:
        logger.info("Generating pitch for: genres=%s, characters=%s", genre_str, char_str)
        result = await pitch_agent.run(prompt)
        logger.info("Successfully generated pitch: %s", result.output.title)
        return result.output

    except Exception as e:
        logger.error("Error generating pitch: %s", str(e))
        raise HTTPException(status_code=500, detail="AI generation failed.")

# 6. HEALTH CHECK ENDPOINT
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)