import requests
from ..klasy.userbases_to_comunicate import *
import os
from dotenv import load_dotenv
from ..klasy.enumValue import UserGoal, UserGender, KategoriesExercise
from ..klasy.userbases_to_comunicate import UserBase, Exercise
from pydantic import TypeAdapter



class User:
    """Klasa od strony klienta do komunikowania się z bazą danych"""


    def __init__(self):
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..","..",  'config', '.env'))
        self.__ENDPOINT_DB_URL = os.getenv("ENDPOINT_DB_URL")
        self.__ENDPOINT_AI_URL = os.getenv("ENDPOINT_AI_URL")

        self.planyUzytkownika = None

    def __print_all_users(self):
        """Funkicja administracyjna - pobranie oraz wyświetlenie wszystkich użytkowników z bazy danych"""
        response = requests.get(f"{self.__ENDPOINT_DB_URL}/users")
        if response.ok:
            print("Wszyscy uzytkownicy: ")
            for user_json in response.json():
                # print(user_json)
                user = UserBase(**user_json)
                print(user.values())
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

    def __wymuszona_zmiana_hasła(self, email, haslo):
        """Funkcja administracyjna - zmiana hasła użytkownikowi o podanym adresie email na hasło z argumentu"""
        uzytkownik = LoginData(email=email,haslo=haslo)
        response = requests.post(f"{self.__ENDPOINT_DB_URL}/admin/user/change_password", json=uzytkownik.model_dump())

        if response.ok:
            print(f"Hasło zmienione dla {email}: {response.status_code}")
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

    def pobierz_sesje(self):
        res = requests.get(
            f"{self.__ENDPOINT_DB_URL}/trainings_user",
            json={"user_id": self.__ID_PUBLIC}
        )
        # print(res.json())
        res.raise_for_status()

        sessions_json = res.json()
        print(sessions_json)

        sessions: List[Trening] = [Trening(**t) for t in sessions_json]
        return sessions


    def logowanie(self, email, password) -> str:
        """Funkcja logowania, po podaniu email i hasła natępujhe łączenie z serwerem gdy się powiedzie dostaję się publiczny toen identyfikacyjny w przeciwnym wypadku None i komunikat błędu."""

        szukanyUzytkownik = LoginData(email=email,
                                      haslo=password)

        response = requests.post(f"{self.__ENDPOINT_DB_URL}/user/login",
                                 json=szukanyUzytkownik.model_dump())
        if response.ok:
            data = response.json()
            self.__ID_PUBLIC =  data.get("id_uzytkownika")
            self.userInformation = self.pobierz_info_uzytkownika()
            self.planyUzytkownika = self.pobierz_plany_treningowe()
            self.sesje_treningowe = self.pobierz_sesje()
            print(self.sesje_treningowe)
            return  self.__ID_PUBLIC
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

        return None

    def rejestracja(self, name, surname, email:str, password:str, gender:UserGender, height:float, goal:UserGoal) -> str:
        """Po podaniu danych następuje rejestracja użytkownika. Gdy się powiedzie dokonuje się automatycznie logowanie. Związku z tym dostaje się publiczny identyfikator.
        albo None w wypadku błędu -> zostanie wyświetlony kod błędu.
        """
        wstawianyUzytkownik = UserBase(imie = name,
                                       nazwisko = surname,
                                       email = email,
                                       haslo = password,
                                       plec = gender.value,
                                       wzrost = height,
                                       cel = goal.value,
                                       waga = None)

        response = requests.post(f"{self.__ENDPOINT_DB_URL}/user/register",
                                 json=wstawianyUzytkownik.model_dump())
        if response.ok:
            userOut = UserOut(**response.json())
            # print(f"ID uzyskane po rejestracji: {userOut.model_dump()['id_uzytkownika']} kod: {response.status_code}")
            return userOut.model_dump()['id_uzytkownika'];
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

        return None

    def pobierz_info_uzytkownika(self) ->UserBase:
        response = requests.get(f"{self.__ENDPOINT_DB_URL}/user/{self.__ID_PUBLIC}")
        if response.ok:
            user_json = response.json()
            user = UserBase(**user_json)
            return user
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

        return None

    def zmiana_wagi(self, waga:float):
        """ZMiana wagi w systemie użytkownika"""
        nowaWaga = UserWeight(id= self.__ID_PUBLIC, waga=waga)
        requests.post(f"{self.__ENDPOINT_DB_URL}/user/change/weight",
                      json=nowaWaga.model_dump())

    def dodaj_pan_treningowy(self, plan: TreningPlan) -> int :
        """
        Wywołuje POST /new_plan i zwraca id nowo utworzonego planu (jeśli OK),
        w przeciwnym razie None.
        """
        print("dodaj_pan_treningowy:", plan)

        payload = {
            "plan": plan.model_dump(),
            "user_id":  self.__ID_PUBLIC
        }

        resp = requests.post(f"{self.__ENDPOINT_DB_URL}/new_plan", json=payload)
        if resp.ok:
            plan_id = resp.json()
            print(f"Utworzono plan o id: {plan_id}")
            return plan_id
        else:
            print(f"Błąd komunikacji z serwerem {resp.status_code}, treść: {resp.text}")
            return None

    def pobierz_plany_treningowe(self) -> List[TreningPlan]:
        payload = {"user_id": self.__ID_PUBLIC}

        resp = requests.get( f"{self.__ENDPOINT_DB_URL}/plans", json=payload)
        if not resp.ok:
            print(f"Błąd komunikacji z serwerem {resp.status_code}, treść: {resp.text}")
            return []

        try:
            adapter = TypeAdapter(List[TreningPlan])
            plans: List[TreningPlan] = adapter.validate_python( resp.json())
            return plans
        except Exception as e:
            print(f"Nie udało się zparsować odpowiedzi: {e}")
            return []

    def dodaj_cwiczenie(self, nazwaCwiczenia:str, kategorie:KategoriesExercise) -> int:
        """Dodaje cwiczenie do bay danych i zwraca id cwiczenia"""
        cwiczenei_nowe = NewExercise(nazwa = nazwaCwiczenia, kategoria = kategorie.value)

        response = requests.post(f"{self.__ENDPOINT_DB_URL}/new_exercise",
                                 json=cwiczenei_nowe.model_dump())
        if response.ok:
            exercise_id = response.json()
            return exercise_id
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

        return None

    def dodaj_sesje_treningowa(self, trening: Trening) -> bool:
        """Dodaje sesji treningowej do bazy danych"""

        response = requests.post(f"{self.__ENDPOINT_DB_URL}/new_trening_sesion",
                                 json=trening.model_dump())
        if response.ok:
            self.sesje_treningowe.append(trening)
            return True
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

        return False

    def zmien_cel(self):
        pass

    def generowanie_planu_treningowego_AI(self, liczba_dni_treningowych: int) -> TreningPlan:
        cel_user = self.userInformation.cel

        body = ReguestPlan(
            liczbaDniTreningowych=liczba_dni_treningowych,
            cel=cel_user
        ).model_dump()

        resp = requests.get(f"{self.__ENDPOINT_AI_URL}/trening_plan", json=body)
        print("Status:", resp.status_code, resp.ok)

        if not resp.ok:
            print(f"Błąd {resp.status_code}: {resp.text}")
            exit(1)

        try:
            plan = TreningPlan.model_validate(resp.json())
        except Exception as e:
            print("Błąd parsowania odpowiedzi:", e)
            exit(1)

        return plan


def __test_generowania_planu_ai(user :User):
    plan = user.generowanie_planu_treningowego_AI(4)
    __wyswietl_plan(plan)


def __dodaj_cwiczenia(user: User):

    user.dodaj_cwiczenie("Martwy ciąg", KategoriesExercise.LEGS )
    user.dodaj_cwiczenie("Wiosłowanie sztangą", KategoriesExercise.BACK )
    user.dodaj_cwiczenie("Wyciskanie sztangi nad głowę", KategoriesExercise.ARMS )
    user.dodaj_cwiczenie("Skakanka (interwały 30s praca/30s odpoczynek)", KategoriesExercise.CARDIO )
    user.dodaj_cwiczenie("Przysiad bułgarski (z hantlami)", KategoriesExercise.LEGS )
    user.dodaj_cwiczenie("Wyprost nóg na maszynie", KategoriesExercise.LEGS )
    user.dodaj_cwiczenie( "Uginanie nóg leżąc", KategoriesExercise.LEGS )
    user.dodaj_cwiczenie("Podciąganie nóg w zwisie" , KategoriesExercise.LEGS )
    user.dodaj_cwiczenie( "Bieganie na bieżni (interwały 1min szybki/1min wolny)", KategoriesExercise.CARDIO )
    user.dodaj_cwiczenie("Wyciskanie hantli na ławce skośnej", KategoriesExercise.CHEST )
    user.dodaj_cwiczenie("Rozpiętki na maszynie", KategoriesExercise.CHEST )
    user.dodaj_cwiczenie( "Podciąganie na drążku (asystowane jeśli potrzeba)", KategoriesExercise.BACK )
    user.dodaj_cwiczenie( "Wiosłowanie hantlami", KategoriesExercise.BACK )

    user.dodaj_cwiczenie("Pompki na poręczach", KategoriesExercise.CHEST )
    user.dodaj_cwiczenie("Rower stacjonarny (interwały 30s sprint/30s odpoczynek)", KategoriesExercise.CARDIO)

def __test_logowania(user: User):
    user._User__print_all_users()
    user._User__wymuszona_zmiana_hasła("jan.kowalski@example.com", "123456")
    user._User__wymuszona_zmiana_hasła("anna.nowak@example.com", "123456")

    id = user.logowanie("jan.kowalski@example.com", "123456")

    if id is not None:
        print(f"Użytkownik zalogowany pomyślnie id {id}")
        infoUser = user.pobierz_info_uzytkownika()
        print(infoUser.values())

        wagaNowa = 200.1
        print("Zmiana wagi na ", wagaNowa)
        user.zmiana_wagi(wagaNowa)

        infoUser = user.pobierz_info_uzytkownika()
        print("po zmianie wagi: ", infoUser.values())


    else:
        print("Nie udało się zalogować :-(")

def __test_dodawania_planu(user: User):
    plan = TreningPlan(
        name="Plan Redukcja 2.0",
        cwiczenia=[
            Exercise(name="Martwy ciąg", liczba_serii=4, liczba_powtorzen=10),
            Exercise(name="Przysiad bułgarski (z hantlami)", liczba_serii=3, liczba_powtorzen=12),
            Exercise(name="Rozpiętki na maszynie", liczba_serii=3, liczba_powtorzen=12),
            Exercise(name="Wiosłowanie hantlami", liczba_serii=3, liczba_powtorzen=12),
        ]
    )
    id_planu = user.dodaj_pan_treningowy(plan)
    print(id_planu)

def __wyswietl_plan(plan: TreningPlan):
    print(f"nazwa planu: ", plan.name)
    i = 0
    print("{0:2s})  {1:50s} - {2:2s} - {3:2s}".format("nr", "nazwa", "liczba serii" , "liczba powtorzen"))

    for cwiczenie in plan.cwiczenia:
        print("{0:2s})  {1:50s} - {2:2d} - {3:2d}".format(
            chr(ord('a') + i),
            cwiczenie.name,
            cwiczenie.liczba_serii,
            cwiczenie.liczba_powtorzen
        ))
        i+=1

def __test_pobieranie_palnow(user: User):
    ret = user.pobierz_plany_treningowe()
    print("Twoje plany:")
    nr_panu = 1
    for plan in ret:
        print(f"{nr_panu}) ")
        nr_panu += 1
        __wyswietl_plan(plan)


def __test_dodaj_sesje_treningowa(user: User):
    e1 = Exercise(name="Deska", liczba_serii=95, liczba_powtorzen=10)
    e2 = Exercise(name="Skakanka", liczba_serii=95, liczba_powtorzen=12)
    e3 = Exercise(name="Uginanie nóg leżąc", liczba_serii=55, liczba_powtorzen=12)

    list_exercise = [e1, e2, e3]

    trening = Trening(id_public = user._User__ID_PUBLIC, id_trening_plan= 38,
        date= "2025-05-09",
        made= list_exercise)
    print(trening)

    user.dodaj_sesje_treningowa(trening)



if __name__ == "__main__":
    user = User()

    # __test_logowania(user)
    # __dodaj_cwiczenia(user)
    user.logowanie("mk@example.pl", "123456")
    # __test_dodawania_planu(user)
    # __test_pobieranie_palnow(user)
    # __test_generowania_planu_ai(user)
    # __test_dodaj_sesje_treningowa(user)


