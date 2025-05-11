from datetime import datetime

from fastapi.openapi.models import Schema
from pydantic import BaseModel, Field
from typing import List

"""Wszystkie klasy oparte na BseModel, które klient wymienia z serewerem"""


class UserBase(BaseModel):
    """Bazowa kalsa do serializacji danych o użytkowniku"""

    imie: str = Field(..., max_length=50)
    nazwisko:  str = Field(..., max_length=50)
    email: str
    haslo: str = Field(..., min_length=5)
    plec: str | None = Field(None, max_length=10)
    wzrost: float | None
    cel: str | None = Field(None, max_length=100)
    waga: float | None

    def values(self):
        return list(self.model_dump().values())

class UserOut(BaseModel):
    """Bazowa kalsa do serializacji publicznego id_użytkownika potwierdzajacego udaną operację"""
    id_uzytkownika: str

    def values(self):
        return list(self.model_dump().values())

class LoginData(Schema):
    """Bazowa kalsa do serializacji danych logoawania"""
    email: str
    haslo: str

    def values(self):
        return list(self.model_dump().values())

class UserWeight(BaseModel):
    """Bazowa klasa do serializacji danych nowej wagi danego użytkownika"""
    id: str
    waga: float

    def values(self):
        return list(self.model_dump().values())

class Exercise(BaseModel):
    name: str
    liczba_serii: int
    liczba_powtorzen: int

class NewExercise(BaseModel):
    nazwa: str
    kategoria: str

class TreningPlan(BaseModel):
    id_planu: int
    name: str
    cwiczenia: List[Exercise]


class ReguestPlan(BaseModel):
    liczbaDniTreningowych: int
    cel: str


class Trening(BaseModel):
    id_public: str
    id_trening_plan: int
    date: str
    made: List[Exercise]