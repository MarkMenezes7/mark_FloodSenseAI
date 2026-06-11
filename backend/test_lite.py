import asyncio
import google.generativeai as genai
from app.models.rag_pipeline import get_rag_response, check_live_flood_risk

async def main():
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite", tools=[check_live_flood_risk])
        chat = model.start_chat(enable_automatic_function_calling=True)
        res = await chat.send_message_async('should i visit delhi today?')
        print('SUCCESS')
    except Exception as e:
        print("ERROR:", str(e))

asyncio.run(main())
