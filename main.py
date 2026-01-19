import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# 1. LOAD SECRETS
load_dotenv() 

if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment variables!")

# 2. DEFINE DATA MODELS
class WheelInput(BaseModel):
    characters: list[str]
    locations: list[str]
    genres: list[str] 
    creatives: list[str]

class MoviePitch(BaseModel):
    title: str = Field(description="A catchy title for the movie")
    tagline: str = Field(description="A short, memorable tagline for the poster")
    pitch: str = Field(description="A 1-3 sentence pitch of the plot")

# 3. SETUP AGENT
pitch_agent = Agent(
    'openai:gpt-5-nano',
    output_type=MoviePitch, 
    system_prompt=(
        "You are a creative Hollywood scriptwriter. "
        "Your goal is to blend potentially clashing genres, characters, and settings "
        "into a cohesive, exciting movie pitch."
    ),
)

# 4. INITIALIZE APP
app = FastAPI(title="SpinTheWheel Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. THE ENDPOINT
@app.post("/generate-pitch", response_model=MoviePitch)
async def generate_pitch(input_data: WheelInput):
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
        # Run the agent
        result = await pitch_agent.run(prompt)
        return result.output

    except Exception as e:
        print(f"Error generating pitch: {e}")
        raise HTTPException(status_code=500, detail="AI generation failed.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)