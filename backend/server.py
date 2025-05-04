import os
import uvicorn
import asyncio
from dotenv import load_dotenv

"""Plik odpoweidialny za uruchomienie wszystkich usług serwerowych"""


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))
DATABASE_URL = os.getenv("DATABASE_URL")


if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the .env file")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    uvicorn.run(
        "endpoint.db:db_app",
        host="0.0.0.0",
        port=int(os.getenv("ENDPOINT_DB_PORT", 8888)),
        reload=True,
        workers=1
    )

    uvicorn.run(
        "endpoint.cohere_ai:ai_app",
        host="0.0.0.0",
        port=int(os.getenv("ENDPOINT_AI_PORT", 8890)),
        reload=True,
        workers=1
    )
