
import tkinter as tk
from tkinter import ttk, messagebox

from backend.klasy.userbases_to_comunicate import TreningPlan, Trening, Exercise
from user import User, UserGender, UserGoal

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.user_client = User()

        self.title("TreningApp z Zakładkami")
        self.geometry("500x750")

        self.frames = {}

        self.frames["login"] = LoginPage(
            self,
            on_login_success=self.start_tabs,
            on_register_click=self.show_registration,
            user_client=self.user_client
        )

        self.frames["register"] = RegistrationPage(
            self,
            on_register_success=self.start_tabs,
            on_back=self.show_login,
            user_client=self.user_client
        )


        self.show_login()

    def show_login(self):
        self._hide_all()
        self.frames["login"].pack(fill="both", expand=True)

    def show_registration(self):
        self._hide_all()
        self.frames["register"].pack(fill="both", expand=True)

    def start_tabs(self, public_id):
        self.frames["tabs"] = TabView(
            self,
            user_client=self.user_client
        )
        tabs = self.frames["tabs"]
        tabs.profile_tab.load_user_info()



        tabs.bmi_tab.load_user_data()

        self._hide_all()
        self.frames["tabs"].pack(fill="both", expand=True)

    def _hide_all(self):
        for frame in self.frames.values():
            frame.pack_forget()


class LoginPage(tk.Frame):
    def __init__(self, parent,
                 on_login_success,
                 on_register_click,
                 user_client):
        super().__init__(parent)
        self.user_client = user_client
        self.on_login_success = on_login_success
        tk.Label(self, text="Logowanie", font=("Arial", 16)).pack(pady=20)

        tk.Label(self, text="E-mail:").pack(anchor="w", padx=20)
        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.pack(padx=20, pady=(0,10))

        tk.Label(self, text="Hasło:").pack(anchor="w", padx=20)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(padx=20, pady=(0,20))

        tk.Button(self, text="Zaloguj", command=self.login).pack(pady=5)
        tk.Button(self, text="Rejestracja", width=15, command=on_register_click).pack(pady=5)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Błąd", "Wypełnij oba pola.")
            return

        try:
            token = self.user_client.logowanie(email, password)
        except Exception as e:
            messagebox.showerror("Błąd sieci", f"Problem z połączeniem:\n{e}")
            return

        if token:
            self.on_login_success(token)
        else:
            messagebox.showwarning("Błąd", "Niepoprawny e‑mail lub hasło")


class RegistrationPage(tk.Frame):
    def __init__(self, parent, on_register_success, on_back, user_client):
        super().__init__(parent)
        self.on_register_success = on_register_success
        self.on_back = on_back
        self.user_client = user_client

        tk.Label(self, text="Rejestracja", font=("Arial", 16)).pack(pady=10)

        fields = ["Imię", "Nazwisko", "E-mail", "Hasło", "Wzrost (cm)", "Waga (kg)"]
        self.entries = {}
        for label, show in [("Imię", None), ("Nazwisko", None), ("E-mail", None), ("Hasło", "*"), ("Wzrost (cm)", None), ("Waga (kg)", None)]:
            tk.Label(self, text=f"{label}:").pack(anchor="w", padx=20)
            ent = tk.Entry(self, width=30, show=show) if show else tk.Entry(self, width=30)
            ent.pack(padx=20, pady=(0,5))
            self.entries[label] = ent

        tk.Label(self, text="Płeć:").pack(anchor="w", padx=20)
        self.gender_cb = ttk.Combobox(self,
                                      values=[g.name for g in UserGender],
                                      state="readonly")
        self.gender_cb.pack(padx=20, pady=(0,5))
        self.gender_cb.current(0)

        tk.Label(self, text="Cel:").pack(anchor="w", padx=20)
        self.goal_cb = ttk.Combobox(self,
                                    values=[g.name for g in UserGoal],
                                    state="readonly")
        self.goal_cb.pack(padx=20, pady=(0,10))
        self.goal_cb.current(0)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Zarejestruj", width=12, command=self.register).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Wróć", width=12, command=self.on_back).pack(side="left", padx=5)

    def register(self):
        data = {label: ent.get().strip() for label, ent in self.entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola.")
            return
        try:
            hgt = float(data["Wzrost (cm)"])
            weight = float(data["Waga (kg)"])
        except ValueError:
            messagebox.showerror("Błąd", "Wzrost i waga muszą być liczbami.")
            return
        gender = UserGender[self.gender_cb.get()]
        goal = UserGoal[self.goal_cb.get()]

        try:
            public_id = self.user_client.rejestracja(
                data["Imię"], data["Nazwisko"], data["E-mail"], data["Hasło"],
                gender, hgt, goal, weight
            )
        except Exception as e:
            messagebox.showerror("Błąd sieci", f"Problem z rejestracją:\n{e}")
            return

        if public_id:
            messagebox.showinfo("Sukces", "Rejestracja udana!")
            self.on_register_success(public_id)
        else:
            messagebox.showerror("Błąd", "Rejestracja nie powiodła się.")


class TabView(tk.Frame):
    def __init__(self, parent, user_client):
        super().__init__(parent)
        self.user_client = user_client
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.profile_tab = UserPage(self.notebook, self.user_client)
        self.bmi_tab = BMIPPMPage(self.notebook, self.user_client)
        self.plan_select_tab = PlanSelectionPage(self.notebook, self.show_plan, user_client)

        self.notebook.add(self.profile_tab, text="Profil")
        self.notebook.add(self.bmi_tab, text="BMI & PPM")
        self.notebook.add(self.plan_select_tab, text="Plan Treningowy")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        tab = event.widget.tab(event.widget.select(), "text")
        if tab == "Profil":
            self.profile_tab.load_user_info()

    def show_plan(self, plan: TreningPlan):
        self.plan_select_tab.pack_forget()
        self.training_view = TrainingPlanPage(self, self.plan_select_tab)
        self.training_view.set_plan(plan)
        self.training_view.pack(fill="both", expand=True)

    def select_tab(self, tab_name: str):
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == tab_name:
                self.notebook.select(tab_id)
                break


class UserPage(tk.Frame):
    def __init__(self, parent, user_client):
        super().__init__(parent)
        self.user_client = user_client
        tk.Label(self, text="Profil użytkownika", font=("Arial", 14)).pack(pady=10)

        info_frame = tk.Frame(self)
        info_frame.pack(pady=5, anchor="w", padx=20)
        self.labels = {}
        for field in ("Imię", "Nazwisko", "E-mail", "Płeć", "Wzrost (cm)", "Cel", "Waga (kg)"):
            lbl = tk.Label(info_frame, text=f"{field}: ", anchor="w")
            lbl.pack(fill="x")
            self.labels[field] = lbl

        weight_frame = tk.Frame(self)
        weight_frame.pack(pady=10)
        tk.Label(weight_frame, text="Nowa waga (kg):").grid(row=0, column=0, padx=5)
        self.new_weight_entry = tk.Entry(weight_frame, width=10)
        self.new_weight_entry.grid(row=0, column=1, padx=5)
        self.save_weight_btn = tk.Button(weight_frame, text="Zapisz wagę", command=self.save_weight)
        self.save_weight_btn.grid(row=0, column=2, padx=5)

    def load_user_info(self):
        public_id = getattr(self.user_client, '_User__ID_PUBLIC', None)
        if not public_id:
            return
        user = self.user_client.pobierz_info_uzytkownika()
        if not user:
            messagebox.showerror("Błąd", "Nie udało się pobrać danych.")
            return
        self.labels["Imię"].config(text=f"Imię: {user.imie}")
        self.labels["Nazwisko"].config(text=f"Nazwisko: {user.nazwisko}")
        self.labels["E-mail"].config(text=f"E-mail: {user.email}")
        self.labels["Płeć"].config(text=f"Płeć: {user.plec}")
        self.labels["Wzrost (cm)"].config(text=f"Wzrost (cm): {user.wzrost}")
        self.labels["Cel"].config(text=f"Cel: {user.cel}")
        waga = user.waga if user.waga not in (None, 0) else "—"
        self.labels["Waga (kg)"].config(text=f"Waga (kg): {waga}")

    def save_weight(self):
        new_weight_txt = self.new_weight_entry.get().strip()
        try:
            new_weight = float(new_weight_txt)
            if new_weight <= 0:
                raise ValueError

            self.user_client.zmiana_wagi(new_weight)

            messagebox.showinfo("Sukces", "Waga została zaktualizowana.")
            self.load_user_info()
            self.new_weight_entry.select_clear()

        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną wartość liczbową większą od zera.")

class BMIPPMPage(tk.Frame):
    def __init__(self, parent, user_client):
        super().__init__(parent)
        self.user_client = user_client
        self.weight = 0
        self.height = 0

        tk.Label(self, text="BMI i PPM", font=("Arial", 14)).pack(pady=10)
        self.info_label = tk.Label(self, text="Brak danych użytkownika.")
        self.info_label.pack(pady=5)

        self.age_entry = self._add_entry("Wiek (lata)")
        tk.Button(self, text="Oblicz", command=self.calculate).pack(pady=10)
        self.result = tk.Label(self, text="")
        self.result.pack()

    def load_user_data(self):
        user = self.user_client.pobierz_info_uzytkownika()
        if user:
            self.weight = user.waga or 0
            self.height = user.wzrost or 0
            self.info_label.config(text=f"Waga: {self.weight} kg | Wzrost: {self.height} cm")
        else:
            self.info_label.config(text="Nie udało się pobrać danych użytkownika.")

    def _add_entry(self, label_text):
        tk.Label(self, text=label_text).pack()
        entry = tk.Entry(self)
        entry.pack()
        return entry

    def calculate(self):
        try:
            height_cm = float(self.height)
            h = height_cm / 100
            w = self.weight
            a = float(self.age_entry.get())
            bmi = w / (h ** 2) if h > 0 else 0
            ppm = 10 * w + 6.25 * height_cm - 5 * a + 5
            self.result.config(text=f"BMI: {bmi:.2f} | PPM: {ppm:.0f}")
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawny wiek (lata).")

import tkinter as tk
from tkinter import ttk, messagebox

from backend.klasy.userbases_to_comunicate import TreningPlan


class TrainingPlanPage(tk.Frame):
    def __init__(self, parent, return_view, user_client):
        super().__init__(parent)
        self.return_view = return_view
        self.user_client = user_client
        self.current_plan = None

        # Title
        tk.Label(self, text="Plan treningowy", font=("Arial", 14)).pack(pady=10)

        # Plan details
        self.details = tk.Label(self, text="", justify="left")
        self.details.pack(pady=5)

        # Sessions label
        tk.Label(self, text="Sesje treningowe:", font=("Arial", 12)).pack(pady=(10, 0))

        # Scrollable area for sessions
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=20, pady=5)

        self.sessions_canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.sessions_canvas.yview)
        self.sessions_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.sessions_canvas.pack(side="left", fill="both", expand=True)

        # This frame holds the session items
        self.sessions_frame = tk.Frame(self.sessions_canvas)
        self.sessions_frame.bind(
            "<Configure>",
            lambda e: self.sessions_canvas.configure(
                scrollregion=self.sessions_canvas.bbox("all")
            )
        )
        self.sessions_canvas.create_window((0, 0), window=self.sessions_frame, anchor="nw")

        # Add session button
        tk.Button(self, text="Dodaj nową sesję", command=self.add_session_dialog).pack(pady=5)
        tk.Button(self, text="Wróć", command=self._go_back).pack(pady=10)

    def set_plan(self, plan: TreningPlan):
        self.current_plan = plan
        self.details.config(text=f"Plan: {plan.name}\n" + (
            "Brak ćwiczeń w tym planie." if not plan.cwiczenia else
            "\n".join(
                f"{chr(ord('a')+i)}) {ex.name} - {ex.liczba_serii}x{ex.liczba_powtorzen}"
                for i, ex in enumerate(plan.cwiczenia)
            )
        ))
        self.load_sessions()

    def load_sessions(self):
        # Clear current
        for widget in self.sessions_frame.winfo_children():
            widget.destroy()

        # Fetch and filter sessions
        try:
            all_sessions = self.user_client.pobierz_sesje()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać sesji: {e}")
            return

        sessions = [s for s in all_sessions if s.id_trening_plan == self.current_plan.id_planu]
        if not sessions:
            tk.Label(self.sessions_frame, text="Brak sesji.").pack(anchor="w")
            return

        for sess in sessions:
            tk.Label(self.sessions_frame,
                     text=f"Data: {sess.date} - wykonane ćwiczenia:",
                     anchor="w").pack(fill="x", pady=(5,0))
            for ex in sess.made:
                tk.Label(self.sessions_frame,
                         text=f"   - {ex.name}: {ex.liczba_serii}x{ex.liczba_powtorzen}",
                         anchor="w").pack(fill="x")

    def add_session_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Nowa sesja")

        tk.Label(dialog, text="Data sesji (RRRR-MM-DD):").pack(padx=10, pady=(10, 0))
        date_entry = tk.Entry(dialog)
        date_entry.pack(padx=10, pady=5)

        def save():
            date = date_entry.get().strip()
            if not date:
                messagebox.showwarning("Błąd", "Podaj datę.")
                return
            trening = Trening(
                id_public=self.user_client._User__ID_PUBLIC,
                id_trening_plan=self.current_plan.id_planu,
                date=date,
                made=self.current_plan.cwiczenia
            )
            try:
                if self.user_client.dodaj_sesje_treningowa(trening):
                    messagebox.showinfo("Sukces", "Sesja została dodana.")
                    dialog.destroy()
                    self.load_sessions()
                else:
                    messagebox.showerror("Błąd", "Nie udało się dodać sesji.")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się dodać sesji: {e}")

        tk.Button(dialog, text="Zapisz", command=save).pack(pady=10)
        tk.Button(dialog, text="Anuluj", command=dialog.destroy).pack()

    def _go_back(self):
        self.pack_forget()
        self.return_view.pack(fill="both", expand=True)

class PlanSelectionPage(tk.Frame):
    def __init__(self, parent, on_plan_select, user_client):
        super().__init__(parent)
        self.on_plan_select = on_plan_select
        self.user_client = user_client

        tk.Label(self, text="Wybierz plan treningowy", font=("Arial", 14)).pack(pady=10)

        params_frame = tk.Frame(self)
        params_frame.pack(pady=5)
        tk.Label(params_frame, text="Liczba dni treningowych:").grid(row=0, column=0, padx=5)
        self.days_spin = tk.Spinbox(params_frame, from_=1, to=7, width=5)
        self.days_spin.grid(row=0, column=1, padx=5)
        tk.Button(params_frame, text="Generuj nowy plan", command=self.generate_plan).grid(row=0, column=2, padx=10)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(fill="both", expand=True)

        self.detail_view = TrainingPlanPage(self, return_view=self.buttons_frame, user_client=self.user_client)
        self.detail_view.pack_forget()

        self.refresh_plans()

    def refresh_plans(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        plans = self.user_client.pobierz_plany_treningowe()
        for plan in plans:
            btn = tk.Button(self.buttons_frame, text=plan.name,
                            command=lambda p=plan: self.show_plan(p))
            btn.pack(pady=5, fill="x", padx=20)

    def show_plan(self, plan: TreningPlan):
        self.buttons_frame.pack_forget()
        self.detail_view.set_plan(plan)
        self.detail_view.pack(fill="both", expand=True)

    def generate_plan(self):
        try:
            days = int(self.days_spin.get())
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowa liczba dni treningowych.")
            return

        # Wygeneruj plan AI
        try:
            new_plan = self.user_client.generowanie_planu_treningowego_AI(days)
            print("Nowy plan", new_plan)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wygenerować planu: {e}")
            return

        try:
            plan_id = self.user_client.dodaj_pan_treningowy(new_plan)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać planu: {e}")
            return

        messagebox.showinfo("Sukces", f"Nowy plan został zapisany (ID: {plan_id}).")

        self.refresh_plans()
        self.show_plan(new_plan)




    def set_plan(self, plan: TreningPlan):
        self.label.config(text=f"Plan: {plan.name}")
        lines = []
        for i, ex in enumerate(plan.cwiczenia):
            letter = chr(ord('a') + i)
            lines.append(f"{letter}) {ex.name} - {ex.liczba_serii}x{ex.liczba_powtorzen}")
        self.details.config(text="\n".join(lines))

    def _go_back(self):
        self.pack_forget()
        self.return_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()