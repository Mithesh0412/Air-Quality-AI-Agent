from config.ai_config import client
from tools.openaq_tools import get_air_quality
from google import genai
from google.genai.types import Content, Part

tools =[get_air_quality]

def ask_agent(prompt: str):
    chat = client.chats.create(
        model="gemini-2.5-flash-lite"
    )

    tool_config = genai.types.GenerateContentConfig(
        tools=tools
    )

    print(f"Sending prompt: '{prompt}'")

    response = chat.send_message(
        prompt,
        config=tool_config
    )

    return response.text
