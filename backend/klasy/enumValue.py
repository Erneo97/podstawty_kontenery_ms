from enum import Enum

class UserGoal(str, Enum):
    """Enumerate Celów jakie użytkownicy chcą osiągnąć
        dostępne 3 cele:
        1) Redukacja masy ciała
        2) Budowa masy mięścniowej
        3) Utrzymanie wagi

    Umożliwia porównanie enum ze stringiem orzymanym bezpośrednio z bazy
        """
    WEIGHT_REDUCE = "Redukcja" #redukacja masy ciała
    MASS_BUILDING = "Budowa masy"
    WEIGHT_CONST = "const"

class UserGender(str, Enum):
    """Wartość enumerate dostępnych płci dla uzytkowników. Posiada 3 wartości
    mężczyzna, kobieta, ora inna.
    Umożliwia porównanie enum ze stringiem orzymanym bezpośrednio z bazy
    """
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

class KategoriesExercise(str, Enum):
    """Wartość enumerate dostępnych kategorii grup mięśniwoych"""
    CHEST = "Klatka piersiowa"
    BELLY = "Brzuch"
    LEGS = "Nogi"
    BACK = "Plecy"
    ARMS = "Ramiona"
    CARDIO = "Cardio"
    NOT_DEFINED = "Nie zdefiniowano"
