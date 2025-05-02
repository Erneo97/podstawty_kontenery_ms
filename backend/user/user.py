import requests
from backend.klasy.userbases_to_comunicate import *
import os
from dotenv import load_dotenv
from backend.klasy.enumValue import UserGoal, UserGender
from backend.klasy.userbases_to_comunicate import UserBase


class User:
    """Klasa od strony klienta do komunikowania się z bazą danych"""
    def __init__(self):
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..","..",  'config', '.env'))
        self.__ENDPOINT_DB_URL = os.getenv("ENDPOINT_DB_URL")

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

    def logowanie(self, email, password) -> str:
        """Funkcja logowania, po podaniu email i hasła natępujhe łączenie z serwerem gdy się powiedzie dostaję się publiczny toen identyfikacyjny w przeciwnym wypadku None i komunikat błędu."""

        szukanyUzytkownik = LoginData(email=email,
                                      haslo=password)

        response = requests.post(f"{self.__ENDPOINT_DB_URL}/user/login",
                                 json=szukanyUzytkownik.model_dump())
        if response.ok:
            data = response.json()
            self.__ID_PUBLIC =  data.get("id_uzytkownika")
            return  self.__ID_PUBLIC
        else:
            print(f"Blad komunikacji z serwerem {response.status_code} komunikat: {response.text}")

        return None

    def rejestracja(self, name, surname, email:str, password:str, gender:UserGender, height, goal:UserGoal) -> str:
        """Po podaniu danych następuje rejestracja użytkownika. Gdy się powiedzie dokonuje się automatycznie logowanie. Związku z tym dostaje się publiczny identyfikator.
        albo None w wypadku błędu -> zostanie wyświetlony kod błędu.
        """
        wstawianyUzytkownik = UserBase(imie = name,
                                       nazwisko = surname,
                                       email = email,
                                       haslo = password,
                                       plec = gender.value,
                                       wzrost = height,
                                       cel = goal.value)

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

    def dodaj_nowy_trening(self):
        pass

    def dodaj_sesje_treningowa(self):
        pass

    def zmien_cel(self):
        pass

    def zmiana_wagi(self, waga:float):
        """ZMiana wagi w systemie użytkownika"""
        nowaWaga = UserWeight(id= self.__ID_PUBLIC, waga=waga)
        requests.post(f"{self.__ENDPOINT_DB_URL}/user/change/weight",
                                 json=nowaWaga.model_dump())


if __name__ == "__main__":
    user = User()
    # user._User__print_all_users()
    # user._User__wymuszona_zmiana_hasła("jan.kowalski@example.com", "123456")
    # user._User__wymuszona_zmiana_hasła("anna.nowak@example.com", "123456")
    #
    id = user.logowanie("jan.kowalski@example.com", "123456")

    if id is not None:
        print(f"Użytkownik zalogowany pomyślnie id {id}")
        infoUser = user.pobierz_info_uzytkownika()
        print(infoUser.values())

        wagaNowa = 212.1
        print("Zmiana wagi na ", wagaNowa)
        user.zmiana_wagi(wagaNowa)

        infoUser = user.pobierz_info_uzytkownika()
        print("po zmianie wagi: ", infoUser.values())


    else:
        print("Nie udało się zalogować :-(")