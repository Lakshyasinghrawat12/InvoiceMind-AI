from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from utils.logger import setup_logger
from utils.pdf_helper import DATA_DIR, process_pdf

FRONTEND_DIR = Path(__file__).resolve().parent / "Frontend"

logger = setup_logger("API")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    page = FRONTEND_DIR / "index.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="Frontend page not found")
    return FileResponse(page)


@app.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for file in files:
        filename = Path(file.filename or "").name
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"{filename or 'unnamed file'} is not a PDF",
            )

        dest = DATA_DIR / filename
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail=f"{filename} is empty")

        dest.write_bytes(content)
        logger.info(f"Saved uploaded PDF to {dest}")

        try:
            result = process_pdf(dest)
        except Exception as exc:
            logger.exception(f"Failed to convert {filename}")
            raise HTTPException(
                status_code=500,
                detail=f"Saved {filename} but failed to convert it: {exc}",
            ) from exc

        results.append(result)

    return {
        "uploaded": len(results),
        "files": results,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
