import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/test", tags=["test"])

@router.get("/stream")
def test_stream():
    async def agen():
        for ch in "Hello, streaming!\nLine 2...\n":
            yield ch
            await asyncio.sleep(0.2)
    return StreamingResponse(
        agen(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
