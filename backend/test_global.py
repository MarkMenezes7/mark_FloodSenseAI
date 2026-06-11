import asyncio
from app.models.rag_pipeline import get_rag_response

async def main():
    res = await get_rag_response('which city has the highest flood risk right now')
    with open('test_global.txt', 'w', encoding='utf-8') as f:
        f.write(res)
    print("Done!")

asyncio.run(main())
