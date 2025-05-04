
-- 1. Tabela ćwiczeń
CREATE TABLE cwiczenia (
                           id_cwiczenia     SERIAL PRIMARY KEY,
                           nazwa            VARCHAR(100) NOT NULL,
                           kategoaria       VARCHAR(100) NOT NULL
);

-- 2. Tabela użytkowników
CREATE TABLE uzytkownicy (
                             id_uzytkownika SERIAL PRIMARY KEY,
                             imie           VARCHAR(50)  NOT NULL,
                             nazwisko       VARCHAR(50)  NOT NULL,
                             email          VARCHAR(100) UNIQUE NOT NULL,
                             haslo          VARCHAR(255) NOT NULL,
                             plec           VARCHAR(10),
                             wzrost         REAL,
                             cel            VARCHAR(100)
);

-- 3. Pomiar wagi
CREATE TABLE pomiar_wagi (
                             id_pomiaru     SERIAL PRIMARY KEY,
                             id_uzytkownika INTEGER NOT NULL
                                 REFERENCES uzytkownicy(id_uzytkownika),
                             wartosc        NUMERIC(5,2) NOT NULL,
                             data           DATE         NOT NULL
);

-- 4. Plany treningowe (nagłówek)
CREATE TABLE plany_treningowe (
                                  id_planu           SERIAL PRIMARY KEY,
                                  id_uzytkownika     INTEGER NOT NULL
                                      REFERENCES uzytkownicy(id_uzytkownika),
                                  nazwa               VARCHAR(100) NOT NULL,
                                  cwiczenia_w_planie INTEGER
);

-- 5. Treningi
CREATE TABLE treningi (
                          id_treningu    SERIAL PRIMARY KEY,
                          id_uzytkownika INTEGER NOT NULL
                              REFERENCES uzytkownicy(id_uzytkownika),
                          id_planu INTEGER NOT NULL
                              REFERENCES plany_treningowe(id_planu),
                          data           DATE NOT NULL
);

-- 6. Serie
CREATE TABLE serie (
                       id_serii       SERIAL PRIMARY KEY,
                       id_treningu    INTEGER NOT NULL
                           REFERENCES treningi(id_treningu),
                       id_cwiczenia   INTEGER NOT NULL
                           REFERENCES cwiczenia(id_cwiczenia),
                       obciazenie     NUMERIC(5,2),
                       powtorzenia    INTEGER
);



-- 7. Ćwiczenia w planie treningowym (szczegóły)
CREATE TABLE cwiczenia_w_planie_treningowym (
                                                id_cwiczenia_wpt      SERIAL PRIMARY KEY,
                                                id_planu_treningowego INTEGER NOT NULL
                                                    REFERENCES plany_treningowe(id_planu),
                                                id_cwiczenia          INTEGER NOT NULL
                                                    REFERENCES cwiczenia(id_cwiczenia),
                                                liczba_serii          INTEGER,
                                                liczba_powtorzen      INTEGER
);

-- ########################################
-- ###### przykładowe dane (INSERTy) ######
-- ########################################


-- 1. Ćwiczenia
INSERT INTO cwiczenia (nazwa, kategoaria) VALUES
                                                   ('Wyciskanie sztangi na ławce poziomej', 'Klatka pierwsiowa'),
                                                   ('Martwy ciąg',                          'Plecy');

-- 2. Użytkownicy
INSERT INTO uzytkownicy (imie, nazwisko, email, haslo, plec, wzrost, cel) VALUES
                                                                              ('Jan', 'Kowalski',  'jan.kowalski@example.com', 'hash1', 'M', 180.5, 'Redukcja'),
                                                                              ('Anna','Nowak',     'anna.nowak@example.com',    'hash2', 'K', 165.0, 'Budowa masy');

-- 3. Pomiar wagi
INSERT INTO pomiar_wagi (id_uzytkownika, wartosc, data) VALUES
                                                            (1, 80.5, '2023-09-01'),
                                                            (1, 79.8, '2023-09-15'),
                                                            (2, 60.2, '2023-09-10');

-- 4. Plany treningowe
INSERT INTO plany_treningowe (id_uzytkownika, nazwa, cwiczenia_w_planie) VALUES
                                                                             (1, 'Plan Forma', 2),
                                                                             (2, 'Plan Próbny', 1);

-- 5. Treningi
INSERT INTO treningi (id_uzytkownika, id_planu, data) VALUES
                                                (1, 1, '2023-09-05'),
                                                (2, 2, '2023-09-07');

-- 6. Serie
INSERT INTO serie (id_treningu, id_cwiczenia, obciazenie, powtorzenia) VALUES
                                                                           (1, 1, 60.0, 8),
                                                                           (1, 2, 100.0, 5),
                                                                           (2, 1, 40.0, 12);

-- 7. Ćwiczenia w planie treningowym
INSERT INTO cwiczenia_w_planie_treningowym
(id_planu_treningowego, id_cwiczenia, liczba_serii, liczba_powtorzen) VALUES
                                                                          (1, 1, 3, 10),
                                                                          (1, 2, 3, 8),
                                                                          (2, 1, 4, 12);
