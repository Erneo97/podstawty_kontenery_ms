from fastapi import FastAPI, HTTPException
import os
from backend.klasy.userbases_to_comunicate import *


from dotenv import load_dotenv
load_dotenv()

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', 'config', '.env'))


ai_app = FastAPI()

import cohere
from backend.AI.key import APIkey
import json
import re

co = cohere.ClientV2(APIkey)

@ai_app.get("/trening_plan", response_model=TreningPlan)
def plan(warunki: ReguestPlan):
    prompt = (
        f"Ułóż plan treningowy na siłownię na {warunki.liczbaDniTreningowych} dni w tygodniu. "
        f"Cel: {warunki.cel}. "
        f"Zwróć dane jako JSON w formacie: "
        f'{{"name": "Plan X", "cwiczenia": [{{"name": "...", "liczba_serii": ..., "liczba_powtorzen": ...}}]}}'
        f'gdzie liczba_powtorzen oraz liczba_serii jest tylko liczba i występuje zawsze'
    )

    response = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}]
    )

    content_items = response.message.content
    text = next((item.text for item in content_items if item.type == "text"), "")

    match = re.search(r"```json\n(.*?)```", text, re.DOTALL)
    if not match:
        raise ValueError("Nie znaleziono poprawnego JSON-a w odpowiedzi AI.")

    json_str = match.group(1)
    parsed = json.loads(json_str)


    flattened_cwiczenia = []
    for dzien in parsed.get("cwiczenia", []):
        for cw in dzien.get("cwiczenia", []):
            try:
                cw["liczba_powtorzen"] = int(cw["liczba_powtorzen"])
            except (ValueError, TypeError):
                cw["liczba_powtorzen"] = 0

            try:
                cw["liczba_serii"] = int(cw["liczba_serii"])
            except (ValueError, TypeError):
                cw["liczba_serii"] = 0

            flattened_cwiczenia.append(cw)

    return TreningPlan(
            name=parsed.get("name", "Plan bez nazwy"),
            cwiczenia=[Exercise(**cw) for cw in flattened_cwiczenia]
        )


