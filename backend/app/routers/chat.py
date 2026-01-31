from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# System prompt for the HVAC assistant
SYSTEM_PROMPT = """You are an AI assistant for a Smart FCU (Fan Coil Unit) Control System dashboard. 
You help users understand and manage their HVAC (Heating, Ventilation, and Air Conditioning) system.

Key features of this system:
- Real-time temperature monitoring across multiple zones (Server Room at 18°C, Open Office at 23°C)
- Adaptive temperature control that learns from usage patterns
- FCU (Fan Coil Unit) control with fan speed and mode settings
- Temperature predictions using machine learning
- Plug-and-play device discovery for sensors and FCUs

You can help with:
- Explaining HVAC concepts (temperature setpoints, humidity, CO2 levels)
- Understanding the dashboard features
- Troubleshooting common issues
- Energy efficiency tips
- Explaining what FCUs are and how they work

Keep responses concise and helpful. If asked about specific system data, remind users to check the dashboard for real-time information."""


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    response: str
    error: str | None = None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the AI assistant and get a response."""
    settings = get_settings()

    if not settings.gemini_api_key:
        return ChatResponse(
            response="",
            error="Gemini API key not configured. Please set GEMINI_API_KEY environment variable.",
        )

    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)

        # Build conversation history
        contents = []
        for msg in request.messages:
            contents.append(
                {
                    "role": "user" if msg.role == "user" else "model",
                    "parts": [{"text": msg.content}],
                }
            )

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.7,
                "max_output_tokens": 500,
            },
        )

        return ChatResponse(response=response.text)

    except Exception as e:
        print(f"Gemini API error: {e}")
        return ChatResponse(response="", error=f"Failed to get response: {str(e)}")


@router.get("/status")
async def chat_status():
    """Check if chat is available (API key configured)."""
    settings = get_settings()
    has_key = bool(settings.gemini_api_key and settings.gemini_api_key.strip())
    return {
        "available": has_key,
        "model": "gemini-3-flash-preview",
    }
