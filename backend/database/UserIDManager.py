import uuid
from typing import Optional

class UserIDManager:
    """Klasa odpowiedzialna za zarządzanie tokenami użytkowników po zalogowaniu. Nie pozwala operować ID użytkownika z bazy danych
    Wykorzystywane w RESTAPi do komynikacji z klientem"""

    # public_id → db_id
    _public_to_db: dict[str, int] = {}
    # db_id → public_id
    _db_to_public: dict[int, str] = {}

    @classmethod
    def generate_public_id(cls, db_id: int) -> str:
        """
        Jeśli dla db_id mamy już public_id, zwracamy je.
        W przeciwnym razie generujemy nowe i zapisujemy oba mapowania.
        """
        # Jeśli już wcześniej wygenerowaliśmy public_id dla tego db_id,
        # po prostu je zwróć:
        if db_id in cls._db_to_public:
            return cls._db_to_public[db_id]

        public_id = str(uuid.uuid4())
        while public_id in cls._public_to_db:
            public_id = str(uuid.uuid4())

        cls._public_to_db[public_id] = db_id
        cls._db_to_public[db_id]   = public_id
        return public_id

    @classmethod
    def get_db_id(cls, public_id: str) -> Optional[int]:
        """
        Zwraca oryginalne db_id skojarzone z public_id.
        Jeśli nie ma takiego klucza, zwraca None.
        """
        return cls._public_to_db.get(public_id)

    @classmethod
    def invalidate_public_id(cls, public_id: str) -> None:
        """
        Usuwa mapowanie, np. po wylogowaniu.
        """
        db_id = cls._public_to_db.pop(public_id, None)
        if db_id is not None:
            cls._db_to_public.pop(db_id, None)


