import asyncio
from app.models.rag_pipeline import get_rag_response, model

async def main():
    try:
        chat = model.start_chat(enable_automatic_function_calling=True)
        res = await chat.send_message_async('should i visit delhi today?')
        with open('err.txt', 'w', encoding='utf-8') as f:
            f.write(res.text)
    except Exception as e:
        with open('err.txt', 'w', encoding='utf-8') as f:
            f.write(str(e))

asyncio.run(main())
