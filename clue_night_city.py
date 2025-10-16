import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import random
import textwrap
import os

# ========================
# DATOS PRINCIPALES
# ========================

SUSPECTS = ["Hacker", "Jefe", "Ejecutiva", "Mercenario", "Investigadora"]
WEAPONS = ["Mantis", "Monowire", "Cuchillo", "Katana", "Pistola"]
AREAS = ["Laboratorio Biologico", "Sala Seguridad", "Penthouse", "Cafetería", "Taller de prototipos"]

# ========================
# FUNCIONES PARA GENERAR PISTAS
# ========================

def clue_physical(area, weapon, is_true):
    if is_true:
        return f"En {area} hay rastros compatibles con {weapon}."
    else:
        other = random.choice([w for w in WEAPONS if w != weapon])
        return f"Se encontraron marcas que podrían corresponder a {other}."

def clue_access(area, culprit, is_true):
    if is_true:
        return f"Registro de acceso reciente vinculado a alguien similar a {culprit}."
    else:
        other = random.choice([s for s in SUSPECTS if s != culprit])
        return f"Un acceso temporal muestra la tarjeta de {other}."

def clue_social(area, culprit, is_true):
    if is_true:
        return f"Un testigo dice haber visto a alguien con rasgos del {culprit} en {area}."
    else:
        other = random.choice([s for s in SUSPECTS if s != culprit])
        return f"Rumores dicen que {other} estuvo discutiendo en la torre."

def clue_item(area, weapon, is_true):
    if is_true:
        return f"Se halló un objeto manchado o asociado a {weapon}."
    else:
        other = random.choice([w for w in WEAPONS if w != weapon])
        return f"Se encontró un objeto relacionado con {other}."

def generate_clues(culprit, weapon, location, seed=None):
    if seed is not None:
        random.seed(seed)
    clues_by_area = {area: [] for area in AREAS}

    true_templates = [clue_physical, clue_access, clue_social, clue_item]
    for i in range(random.randint(3, 5)):
        tpl = random.choice(true_templates)
        area = location if i == 0 else random.choice(AREAS)
        if tpl in (clue_physical, clue_item):
            txt = tpl(area, weapon, True)
        else:
            txt = tpl(area, culprit, True)
        clues_by_area[area].append({"text": txt, "true": True})

    for i in range(random.randint(6, 9)):
        tpl = random.choice(true_templates)
        area = random.choice(AREAS)
        if tpl in (clue_physical, clue_item):
            txt = tpl(area, weapon, False)
        else:
            txt = tpl(area, culprit, False)
        clues_by_area[area].append({"text": txt, "true": False})

    for area in clues_by_area:
        random.shuffle(clues_by_area[area])
    return clues_by_area

# ========================
# CLASE PRINCIPAL DEL JUEGO
# ========================

class ClueGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clue: Night City Protocol")
        self.root.geometry("850x750")
        self.root.config(bg="#101010")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton",
                        font=("Consolas", 11, "bold"),
                        foreground="#00ffe7",
                        background="#222222",
                        borderwidth=2,
                        focusthickness=3,
                        focuscolor="#00ffe7",
                        padding=6)
        style.map("TButton",
                  background=[('active', '#00ffe7')],
                  foreground=[('active', '#101010')])

        self.initialize_game()

        # Logo
        logo_path = os.path.join("Images", "Logo Clue.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img.thumbnail((550, 300))
            logo_img = ImageTk.PhotoImage(img)
            self.logo = tk.Label(root, image=logo_img, bg="#101010")
            self.logo.image = logo_img
            self.logo.pack(pady=10)
        else:
            tk.Label(root, text="CLUE: Night City Protocol", font=("Consolas", 20, "bold"), fg="#00ffe7", bg="#101010").pack(pady=10)

        # Área de texto
        self.text_area = tk.Text(root, wrap="word", height=15, width=100, bg="#181c1f", fg="#00ffe7",
                                 insertbackground="#00ffe7", font=("Consolas", 11), bd=2, relief="groove",
                                 highlightbackground="#00ffe7", highlightcolor="#00ffe7")
        self.text_area.pack(pady=10)
        self.text_area.insert("end", self.get_intro_text())

        self.cont_button = ttk.Button(root, text="Continuar", width=20, command=self.show_main_options)
        self.cont_button.pack(pady=5)

        self.button_frame = tk.Frame(root, bg="#101010")

    def initialize_game(self):
        self.culprit = random.choice(SUSPECTS)
        self.weapon = random.choice(WEAPONS)
        self.location = random.choice(AREAS)
        self.clues = generate_clues(self.culprit, self.weapon, self.location)
        self.found_clues = []
        self.turns = 0
        self.max_turns = 10
        self.intro_shown = False

    def get_intro_text(self):
        return textwrap.dedent("""
        ==========================================
                CLUE: NIGHT CITY PROTOCOL
        ==========================================
        El Director de Investigación de Biotecnología ha sido asesinado
        en la torre Arasaka durante una noche lluviosa.

        Dentro de la torre se encuentran cinco individuos:

        - Hacker
        - Jefe
        - Ejecutiva
        - Mercenario
        - Investigadora

        Posibles armas utilizadas:
        - Mantis
        - Monowire
        - Cuchillo
        - Katana
        - Pistola

        Tu objetivo es descubrir quién lo asesinó, con qué arma y en qué lugar.
        Presiona "Continuar" para comenzar.
        """)

    # ==========================
    # OPCIONES PRINCIPALES
    # ==========================

    def show_main_options(self):
        if self.intro_shown:
            return
        self.intro_shown = True
        self.cont_button.destroy()

        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", "Investiga las áreas o sospechosos para recolectar pistas y resolver el misterio.\n")

        # Botones de áreas
        self.button_frame.pack(pady=10)
        tk.Label(self.button_frame, text="Áreas:", fg="#00ffe7", bg="#101010", font=("Consolas", 12, "bold")).pack(pady=5)
        for area in AREAS:
            btn = ttk.Button(self.button_frame, text=area, width=25, command=lambda a=area: self.enter_area(a))
            btn.pack(pady=2)

        # Separación para sospechosos
        tk.Label(self.button_frame, text="Sospechosos:", fg="#00ffe7", bg="#101010", font=("Consolas", 12, "bold")).pack(pady=5)
        for suspect in SUSPECTS:
            btn = ttk.Button(self.button_frame, text=f"Investigar a {suspect}", width=25, command=lambda s=suspect: self.enter_suspect(s))
            btn.pack(pady=2)

        # Acciones
        action_frame = tk.Frame(self.root, bg="#101010")
        action_frame.pack(pady=10)
        ttk.Button(action_frame, text="Ver Pistas", width=20, command=self.show_pistas).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Hacer Acusación", width=20, command=self.toggle_accusation).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Salir del Juego", width=20, command=self.root.quit).grid(row=0, column=2, padx=5)

    # ==========================
    # INVESTIGAR ÁREA O SOSPECHOSO
    # ==========================

    def enter_area(self, area):
        if self.turns >= self.max_turns:
            messagebox.showinfo("Fin de turnos", "Has agotado todos tus movimientos. Debes hacer tu acusación ahora.")
            self.disable_investigation()
            return

        self.turns += 1
        self.text_area.insert("end", f"\n\n--- {area} ---\n")
        available = self.clues.get(area, [])
        if not available:
            self.text_area.insert("end", "No hay pistas visibles aquí por ahora.\n")
        else:
            num = min(2, len(available))
            revealed = available[:num]
            self.clues[area] = available[num:]
            for c in revealed:
                self.text_area.insert("end", f"Pista encontrada: {c['text']}\n")
                self.found_clues.append(c["text"])
        self.text_area.see("end")

        if self.turns >= self.max_turns:
            self.disable_investigation()

    def enter_suspect(self, suspect):
        if self.turns >= self.max_turns:
            messagebox.showinfo("Fin de turnos", "Has agotado todos tus movimientos. Debes hacer tu acusación ahora.")
            self.disable_investigation()
            return

        self.turns += 1
        self.text_area.insert("end", f"\n\n--- Investigando a {suspect} ---\n")

        possible_clues = []
        for area in AREAS:
            for c in self.clues[area]:
                if suspect in c.get("text", ""):
                    possible_clues.append(c)

        if not possible_clues:
            txt = f"Al investigar a {suspect}, no se encontró nada concluyente, pero hay rumores extraños..."
            self.text_area.insert("end", f"{txt}\n")
        else:
            num = min(2, len(possible_clues))
            revealed = possible_clues[:num]
            for c in revealed:
                self.text_area.insert("end", f"Pista encontrada: {c['text']}\n")
                self.found_clues.append(c["text"])
        self.text_area.see("end")

        if self.turns >= self.max_turns:
            self.disable_investigation()

    # ==========================
    # MOSTRAR PISTAS
    # ==========================

    def show_pistas(self):
        if not self.found_clues:
            messagebox.showinfo("Pistas", "Aún no has encontrado ninguna pista.")
        else:
            # Separar pistas de lugares y sospechosos
            area_clues = [p for p in self.found_clues if any(area in p for area in AREAS)]
            suspect_clues = [p for p in self.found_clues if any(s in p for s in SUSPECTS)]
            msg = ""
            if area_clues:
                msg += "Pistas de Áreas:\n" + "\n".join(f"- {p}" for p in area_clues) + "\n\n"
            if suspect_clues:
                msg += "Pistas de Sospechosos:\n" + "\n".join(f"- {p}" for p in suspect_clues)
            messagebox.showinfo("Pistas Encontradas", msg)

    # ==========================
    # ACUSACIÓN PLEGABLE
    # ==========================

    def toggle_accusation(self):
        if hasattr(self, 'acc_frame') and self.acc_frame.winfo_exists():
            if self.acc_frame.winfo_ismapped():
                self.acc_frame.pack_forget()
            else:
                self.acc_frame.pack(pady=10, fill='both', expand=True)
        else:
            self.acc_frame = tk.Frame(self.root, bg="#101010")
            self.acc_frame.pack(pady=10, fill='both', expand=True)

            canvas = tk.Canvas(self.acc_frame, bg="#101010", highlightthickness=0)
            scrollbar = tk.Scrollbar(self.acc_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#101010")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            tk.Label(scrollable_frame, text="Selecciona al Sospechoso:", bg="#101010", fg="#00ffe7", font=("Consolas", 12, "bold")).pack(pady=5)
            self.suspect_var = tk.StringVar()
            for s in SUSPECTS:
                ttk.Radiobutton(scrollable_frame, text=s, value=s, variable=self.suspect_var).pack(anchor="w", padx=20)

            tk.Label(scrollable_frame, text="Selecciona el Arma:", bg="#101010", fg="#00ffe7", font=("Consolas", 12, "bold")).pack(pady=5)
            self.weapon_var = tk.StringVar()
            for w in WEAPONS:
                ttk.Radiobutton(scrollable_frame, text=w, value=w, variable=self.weapon_var).pack(anchor="w", padx=20)

            tk.Label(scrollable_frame, text="Selecciona el Lugar:", bg="#101010", fg="#00ffe7", font=("Consolas", 12, "bold")).pack(pady=5)
            self.location_var = tk.StringVar()
            for a in AREAS:
                ttk.Radiobutton(scrollable_frame, text=a, value=a, variable=self.location_var).pack(anchor="w", padx=20)

            def acusar():
                suspect = self.suspect_var.get()
                weapon = self.weapon_var.get()
                location = self.location_var.get()
                if not suspect or not weapon or not location:
                    messagebox.showwarning("Error", "Debes seleccionar una opción de cada categoría.")
                    return
                correct = (suspect == self.culprit and weapon == self.weapon and location == self.location)
                if correct:
                    messagebox.showinfo("Victoria!", f"¡Correcto! El culpable era {self.culprit}, con {self.weapon} en {self.location}.")
                else:
                    messagebox.showerror("Incorrecto", "Esa acusación no es correcta.")
                self.restart_game()

            ttk.Button(scrollable_frame, text="Acusar", command=acusar).pack(pady=10)

    # ==========================
    # DESACTIVAR BOTONES DE INVESTIGACIÓN
    # ==========================

    def disable_investigation(self):
        if hasattr(self, 'button_frame') and self.button_frame.winfo_exists():
            for child in self.button_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="disabled")
        self.toggle_accusation()

    # ==========================
    # REINICIAR JUEGO
    # ==========================

    def restart_game(self):
        self.initialize_game()
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", self.get_intro_text())
        if hasattr(self, 'acc_frame') and self.acc_frame.winfo_exists():
            self.acc_frame.destroy()
        if hasattr(self, 'button_frame') and self.button_frame.winfo_exists():
            for child in self.button_frame.winfo_children():
                child.destroy()
        self.cont_button = ttk.Button(self.root, text="Continuar", width=20, command=self.show_main_options)
        self.cont_button.pack(pady=5)

# ========================
# EJECUCIÓN DEL PROGRAMA
# ========================

if __name__ == "__main__":
    root = tk.Tk()
    app = ClueGameGUI(root)
    root.mainloop()
