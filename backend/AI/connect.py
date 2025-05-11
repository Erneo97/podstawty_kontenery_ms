import cohere
from key import APIkey
import json
import re
from ..klasy.userbases_to_comunicate import *

warunki = ReguestPlan
warunki.cel = "Redukcja"
warunki.liczbaDniTreningowych = 3

co = cohere.ClientV2(APIkey)
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

print(response)
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
        # Upewnij się, że liczba_powtorzen to liczba
        try:
            cw["liczba_powtorzen"] = int(cw["liczba_powtorzen"])
        except (ValueError, TypeError):
            cw["liczba_powtorzen"] = 0  # domyślna wartość

        try:
            cw["liczba_serii"] = int(cw["liczba_serii"])
        except (ValueError, TypeError):
            cw["liczba_serii"] = 0  # domyślna wartość

        flattened_cwiczenia.append(cw)


trening_plan = TreningPlan(
    name=parsed.get("name", "Plan bez nazwy"),
    cwiczenia=[Exercise(**cw) for cw in flattened_cwiczenia]
)


# Zapisz dane
with open("plan.txt", "w", encoding="utf-8") as f:
    f.write(text)

with open("plan_full.json", "w", encoding="utf-8") as f:
    json.dump(trening_plan.model_dump(), f, ensure_ascii=False, indent=2)

