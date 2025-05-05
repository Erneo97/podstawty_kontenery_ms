import os
import uvicorn
from dotenv import load_dotenv

"""Plik odpoweidialny za uruchomienie usług związanych z cohere AI do generowania planów"""

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

if __name__ == "__main__":

    uvicorn.run(
        "endpoint.cohere_ai:ai_app",
        host="0.0.0.0",
        port=int(os.getenv("ENDPOINT_AI_PORT", 8890)),
        reload=True,
        workers=1
    )
