import asyncio
from app.models.rag_pipeline import get_rag_response

async def main():
    res = await get_rag_response('should i visit delhi today? is it rainy there')
    with open('test_res2.txt', 'w', encoding='utf-8') as f:
        f.write(res)
    print("Done!")

asyncio.run(main())
