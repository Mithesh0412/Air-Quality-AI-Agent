from config.ai_config import client
from tools.openaq_tools import get_air_quality, get_historical_average
from google import genai

tools =[get_air_quality, get_historical_average]

def ask_agent(prompt: str):
    chat = client.chats.create(
        model="gemini-2.5-flash-lite"
    )

    # System prompt instructing AI how to use tools
    system_instruction = (
        "You are an environmental AI assistant. "
        "You can access real-time air quality data using the 'get_air_quality' tool "
        "and historical yearly PM2.5 averages using the 'get_historical_average' tool. "
        "Use these tools ONLY when the user asks about air quality, PM2.5, AQI, pollution, "
        "respiratory health, or related topics. "
        "For all other questions, answer using your own knowledge without calling any tools."
    )

    tool_config = genai.types.GenerateContentConfig(
        tools=tools
    )

    print(f"Sending prompt: '{prompt}'")

    response = chat.send_message(
        f"{system_instruction}\nUser: {prompt}",
        config=tool_config
    )

    return response.text
