from config.ai_config import client
from tools.openaq_tools import get_air_quality, get_historical_average
from google import genai

# Create a single global chat session
chat_session = client.chats.create(model="gemini-2.5-flash-lite")

tools = [get_air_quality, get_historical_average]

system_instruction = (
    "You are an environmental AI assistant. "
    "You can access real-time air quality data using the 'get_air_quality' tool "
    "and historical yearly PM2.5 averages using the 'get_historical_average' tool. "
    "Use these tools ONLY when the user asks about air quality, PM2.5, AQI, pollution, "
    "respiratory health, or related topics. "
    "For all other questions, answer using your own knowledge without calling any tools."
    "DO NOT refuse to answer other questions that are not based on air quality"
)

def ask_agent(prompt: str):
    """
    Send messages to the same chat session so that Gemini maintains context.
    """
    tool_config = genai.types.GenerateContentConfig(tools=tools)

    # Send the prompt to the same session
    response = chat_session.send_message(
        f"{system_instruction}\nUser: {prompt}",
        config=tool_config
    )

    return response.text
