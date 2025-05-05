from fastapi import FastAPI, Body, HTTPException
from databases import Database
import os

from passlib.context import CryptContext
from starlette import status

from backend.klasy.userbases_to_comunicate import *
from backend.database.UserIDManager import UserIDManager

from datetime import date, datetime
def __get_date_for_db():
    """Zwraca dzisiejszą date w formacie wymaganym przez bazę dancyh"""
    return datetime.now().date()


# Konfiguracja bazy danych

from dotenv import load_dotenv
load_dotenv()

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', 'config', '.env'))
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
        raise ValueError("DATABASE_URL is not set in the .env file")
print(f"url bazy: { DATABASE_URL}")
database = Database(DATABASE_URL)

# Szyfrowanie haseł
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


"""Fast API do obsługi bazy danych"""

db_app = FastAPI()


@db_app.on_event("startup")
async def startup():
    await database.connect()

@db_app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# ---------------    Obsługa tabeli użytkownika

@db_app.get("/users", response_model=list[UserBase])
async def get_users():
    query = """SELECT u.*,
           pw.wartosc as waga
    FROM uzytkownicy u
    LEFT JOIN (
      SELECT DISTINCT ON (id_uzytkownika)
             id_pomiaru,
             id_uzytkownika,
             wartosc,
             data
      FROM pomiar_wagi
      ORDER BY id_uzytkownika, data DESC
    ) pw
      ON u.id_uzytkownika = pw.id_uzytkownika
  """
    result = await database.fetch_all(query)

    if not result:
        raise HTTPException(status_code=404, detail="No users found")

    return result


@db_app.get("/user/{public_id}", response_model=UserBase)
async def get_user_by_id(public_id: str):
    """Dodaje nowy rekord do tabeli z pomiarem wagi"""
    db_id = UserIDManager.get_db_id(public_id)
    if db_id is None:
        raise HTTPException(status_code=404, detail="Invalid public_id")
    query = """SELECT u.*,
       pw.wartosc AS waga,
       pw.data
FROM uzytkownicy u
LEFT JOIN (
    SELECT DISTINCT ON (id_uzytkownika)
           id_uzytkownika,
           wartosc,
           data
    FROM pomiar_wagi
    ORDER BY id_uzytkownika, data DESC, id_pomiaru DESC
) pw
ON u.id_uzytkownika = pw.id_uzytkownika
WHERE u.id_uzytkownika = :id_uzytkownika;
    """

    result = await database.fetch_one(query,
                                      values={"id_uzytkownika": db_id})

    print(result)
    if not result:
        raise HTTPException(status_code=404, detail="No user found")

    return result

@db_app.post("/user/login", response_model=UserOut)
async def login(data: LoginData):
    query = """SELECT id_uzytkownika, haslo
            FROM uzytkownicy 
            WHERE email = :email"""

    user = await database.fetch_one(query=query, values={"email": data.email})
    print(user)
    hashed_password_from_db = user["haslo"]
    if not user or not pwd_context.verify(data.haslo, hashed_password_from_db):
        raise HTTPException(status_code=401, detail="Unauthorized: Złe hasło bądź login")

    id = UserIDManager.generate_public_id(user["id_uzytkownika"])
    print("Id użytkownika", id)
    return UserOut(id_uzytkownika=id)

@db_app.post("/user/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserBase):
    hashed_password = pwd_context.hash(data.haslo)

    query = """
    INSERT INTO uzytkownicy (imie, nazwisko, email, haslo, plec, wzrost, cel)
    VALUES (:imie, :nazwisko, :email, :haslo, :plec, :wzrost, :cel)
    RETURNING id_uzytkownika
    """
    values = {
        "imie":      data.imie,
        "nazwisko":  data.nazwisko,
        "email":     data.email,
        "haslo":     hashed_password,
        "plec":      data.plec,
        "wzrost":    data.wzrost,
        "cel":       data.cel,
    }
    try:
        record = await database.fetch_one(query=query, values=values)
    except Exception as e:
        if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email już istnieje")
        raise HTTPException(status_code=500, detail="Błąd serwera przy rejestracji")
    print(f"register:   ", record['id_uzytkownika'])

    return UserOut(id_uzytkownika=UserIDManager.generate_public_id(record['id_uzytkownika']))

@db_app.post("/user/change/weight", status_code=status.HTTP_201_CREATED)
async def change_weight(data: UserWeight):
    id_uzytkownika = UserIDManager.get_db_id(data.id)
    if id_uzytkownika is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nieprawidłowe public_id"
        )

    query = """ 
    INSERT INTO pomiar_wagi (id_uzytkownika, wartosc, data)
    VALUES (:id_uzytkownika, :wartosc, :data)
    """
    values = {
        "id_uzytkownika":      id_uzytkownika,
        "wartosc":  data.waga,
        "data":     __get_date_for_db(),
    }
    try:
        print("→ db_id:", id_uzytkownika, "wartosc:", data.waga, "data:", __get_date_for_db())
        await database.execute(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Błąd serwera dodawaniu rekordu wagi")


@db_app.post("/admin/user/change_password", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def change_user_password(data: LoginData):
    hashed_password = pwd_context.hash(data.haslo)

    query = """
    UPDATE uzytkownicy
    SET haslo = :haslo
    WHERE email = :email
    RETURNING id_uzytkownika
    """
    value = {"haslo": hashed_password,
             "email": data.email}

    try:
        record = await database.fetch_one(query=query, values=value)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Błąd serwera przy zmianie hasła jako Admin")


    return UserOut(id_uzytkownika=UserIDManager.generate_public_id(record['id_uzytkownika']))


#   ----------------        Cześć Planowa / treningowa ------------------------


async def _get_exercise_id(name: str) -> int:
    select_q = """
        SELECT id_cwiczenia
          FROM cwiczenia
         WHERE nazwa = :nazwa
        """
    existing = await database.fetch_one(query=select_q, values={"nazwa": name})
    return existing["id_cwiczenia"]

@db_app.post("/new_exercise", response_model=int, status_code=status.HTTP_201_CREATED)
async def new_exercise(data: NewExercise):
    """Dodawanie nowego ćwiczenia do tabeli pytań. Jeżeni ćwiczenie o podanej nazwie istnieje tozwraca istniejące id_cwiczenia jak nie to dodaje to ćwiczenie i zwraca id_cwiczenia"""
    existing = await _get_exercise_id(data.nazwa)
    if existing:
        return existing

    query = """
    INSERT INTO cwiczenia (nazwa, kategoaria)
    VALUES (:nazwa, :kategoria)
    RETURNING id_cwiczenia
    """
    values = {"nazwa": data.nazwa, "kategoria": data.kategoria}
    print(values)
    try:
        record = await database.fetch_one(query=query, values=values)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd serwera przy dodawaniu ćwiczenia"
        )
    return record["id_cwiczenia"]

@db_app.post(
    "/new_plan",
    response_model=int,
    status_code=status.HTTP_201_CREATED
)
async def create_plan(
        plan: TreningPlan,
        user_id: str = Body(...),
):

    # 3.1 Wstaw nagłówek planu
    insert_plan_q = """
    INSERT INTO plany_treningowe (id_uzytkownika, nazwa, cwiczenia_w_planie)
    VALUES (:id_uzytkownika, :nazwa, :cwiczenia_w_planie)
    RETURNING id_planu
    """
    user_id = UserIDManager.get_db_id(user_id)
    header_vals = {
        "id_uzytkownika": int(user_id),
        "nazwa": plan.name,
        "cwiczenia_w_planie": len(plan.cwiczenia)
    }
    try:
        rec = await database.fetch_one(query=insert_plan_q, values=header_vals)
        plan_id = rec["id_planu"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    # 3.2 Wstaw szczegóły: każde ćwiczenie w planie


    insert_detail_q = """
    INSERT INTO cwiczenia_w_planie_treningowym
      (id_planu_treningowego, id_cwiczenia, liczba_serii, liczba_powtorzen)
    VALUES (:id_planu_treningowego, :id_cwiczenia, :serie, :powtorzenia)
    """
    for ex in plan.cwiczenia:
        id_cwiczenie = await _get_exercise_id(ex.name)
        print("id_cwiczenie: ", id_cwiczenie)
        detail_vals = {
            "id_planu_treningowego": plan_id,
            "id_cwiczenia": id_cwiczenie,
            "serie": ex.liczba_serii,
            "powtorzenia": ex.liczba_powtorzen
        }
        try:
            await database.execute(query=insert_detail_q, values=detail_vals)
        except Exception as e:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


    return plan_id


@db_app.get(
    "/plans",
    response_model=List[TreningPlan],
    status_code=status.HTTP_200_OK
)
async def get_all_plans(user_id: str = Body(..., embed=True)):
    """Zwraca Listę wszystkich planów danego użytkownika"""
    try:
        db_user_id = UserIDManager.get_db_id(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowe user_id: {e}")

    select_plans_q = """
    SELECT id_planu, nazwa
      FROM plany_treningowe
     WHERE id_uzytkownika = :uid
    """
    try:
        plan_headers = await database.fetch_all(
            query=select_plans_q,
            values={"uid": int(db_user_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd przy pobieraniu planów: {e}")

    # 2.3. Dla każdego planu pobierz ćwiczenia i złóż model TreningPlan
    plans: List[TreningPlan] = []
    detail_q = """
    SELECT c.nazwa    AS exercise_name,
           d.liczba_serii   AS serie,
           d.liczba_powtorzen AS powtorzenia
      FROM cwiczenia_w_planie_treningowym d
      JOIN cwiczenia c
        ON c.id_cwiczenia = d.id_cwiczenia
     WHERE d.id_planu_treningowego = :plan_id
    """

    for hdr in plan_headers:
        rows = await database.fetch_all(
            query=detail_q,
            values={"plan_id": hdr["id_planu"]}
        )

        exercises = [
            Exercise(
                name=row["exercise_name"],
                liczba_serii=row["serie"],
                liczba_powtorzen=row["powtorzenia"]
            )
            for row in rows
        ]

        plans.append(
            TreningPlan(
                name=hdr["nazwa"],
                cwiczenia=exercises
            )
        )

    return plans
