import tkinter as tk
from tkinter import messagebox, simpledialog, ttk  # <-- Agrega ttk
from PIL import Image, ImageTk
import random
import textwrap
import os

# ========================
# DATOS PRINCIPALES
# ========================

SUSPECTS = ["Hacker", "Jefe de Seguridad", "Ejecutiva", "Mercenario", "Investigadora"]
WEAPONS = ["Mantis Blades", "Monowire", "Cuchillo", "Katana", "Pistola"]
AREAS = [
    "Laboratorio de Biotecnología",
    "Centro de Seguridad / Sala de Monitoreo",
    "Penthouse Ejecutivo / Oficina del Director",
    "Cafetería Corporativa",
    "Taller de Prototipos / Armería"
]

# ========================
# FUNCIONES PARA GENERAR PISTAS
# ========================

def clue_physical(area, weapon, is_true):
    if is_true:
        return f"En el área hay rastros compatibles con la {weapon}."
    else:
        other = random.choice([w for w in WEAPONS if w != weapon])
        return f"Se encontraron marcas que podrían corresponder a la {other}."

def clue_access(area, culprit, is_true):
    if is_true:
        return f"Registro de acceso reciente vinculado a alguien con perfil similar al {culprit}."
    else:
        other = random.choice([s for s in SUSPECTS if s != culprit])
        return f"Un acceso temporal muestra la tarjeta de un empleado similar a {other}."

def clue_social(area, culprit, is_true):
    if is_true:
        return f"Un testigo dice haber visto a alguien con rasgos del {culprit} cerca de aquí."
    else:
        other = random.choice([s for s in SUSPECTS if s != culprit])
        return f"Rumores dicen que {other} estuvo discutiendo en la torre hace poco."

def clue_item(area, weapon, is_true):
    if is_true:
        return f"Se halló un objeto manchado o asociado a la {weapon}."
    else:
        other = random.choice([w for w in WEAPONS if w != weapon])
        return f"Se encontró un objeto que pertenece a un equipo relacionado con la {other}."

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
        self.root.geometry("800x650")
        self.root.config(bg="#101010")

        # ====== NUEVO: Estilos ttk ======
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

        # Datos del juego
        self.culprit = random.choice(SUSPECTS)
        self.weapon = random.choice(WEAPONS)
        self.location = random.choice(AREAS)
        self.clues = generate_clues(self.culprit, self.weapon, self.location)
        self.found_clues = []
        self.turns = 0
        self.max_turns = 5
        self.intro_shown = False

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

        # Área de texto (mejorada)
        self.text_area = tk.Text(root, wrap="word", height=15, width=90, bg="#181c1f", fg="#00ffe7", insertbackground="#00ffe7", font=("Consolas", 11), bd=2, relief="groove", highlightbackground="#00ffe7", highlightcolor="#00ffe7")
        self.text_area.pack(pady=10)
        self.text_area.insert("end", self.get_intro_text())

        # Botón para continuar (ahora ttk)
        self.cont_button = ttk.Button(root, text="Continuar", width=20, command=self.show_main_options)
        self.cont_button.pack(pady=5)

        # Frame de botones (oculto hasta mostrar opciones)
        self.button_frame = tk.Frame(root, bg="#101010")

    def get_intro_text(self):
        return textwrap.dedent("""
        ==========================================
                CLUE: NIGHT CITY PROTOCOL
        ==========================================
        El Director de Investigación de Biotecnología ha sido asesinado
        en la torre Arasaka durante una noche lluviosa. El edificio está
        en cuarentena, y nadie puede salir hasta resolver el crimen.

        Dentro de la torre se encuentran cinco individuos con acceso y
        motivos suficientes para cometer el asesinato:

        - Hacker: experto en infiltración de sistemas.
        - Jefe de Seguridad: controla cámaras y accesos.
        - Ejecutiva: maneja contratos y decisiones estratégicas.
        - Mercenario: contratado por Arasaka para misiones secretas y
          transporte de prototipos experimentales.
        - Investigadora: trabaja con biotecnología y AI junto al Director.

        Posibles armas utilizadas:
        - Mantis Blades
        - Monowire
        - Cuchillo
        - Katana
        - Pistola

        Tu objetivo es descubrir quién lo asesinó, con qué arma y en qué lugar.
        Cuando estés listo, presiona "Continuar" para comenzar la investigación.
        """)

    def show_main_options(self):
        if self.intro_shown:
            return
        self.intro_shown = True
        self.cont_button.destroy()

        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", "Investiga las áreas para recolectar pistas y resolver el misterio.\n")

        self.button_frame.pack(pady=10)
        for area in AREAS:
            btn = ttk.Button(self.button_frame, text=area, width=35, command=lambda a=area: self.enter_area(a))
            btn.pack(pady=3)

        action_frame = tk.Frame(self.root, bg="#101010")
        action_frame.pack(pady=10)
        ttk.Button(action_frame, text="Ver Pistas", width=20, command=self.show_pistas).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Hacer Acusación", width=20, command=self.make_accusation).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Salir del Juego", width=20, command=self.root.quit).grid(row=0, column=2, padx=5)

    def enter_area(self, area):
        self.turns += 1
        if self.turns > self.max_turns:
            messagebox.showinfo("Fin del juego", "Has agotado tus movimientos. El caso quedó sin resolver.")
            self.root.quit()
            return

        self.text_area.insert("end", f"\n\n--- {area} ---\n")
        available = self.clues.get(area, [])
        if not available:
            self.text_area.insert("end", "No hay pistas visibles aquí por ahora.\n")
            return

        num = min(2, len(available))
        revealed = available[:num]
        self.clues[area] = available[num:]
        for c in revealed:
            self.text_area.insert("end", f"Pista encontrada: {c['text']}\n")
            self.found_clues.append(c["text"])
        self.text_area.see("end")

    def show_pistas(self):
        if not self.found_clues:
            messagebox.showinfo("Pistas", "Aún no has encontrado ninguna pista.")
        else:
            pistas = "\n".join(f"- {p}" for p in self.found_clues)
            messagebox.showinfo("Pistas Encontradas", pistas)

    def make_accusation(self):
        suspect = simpledialog.askstring("Acusación", f"Sospechosos:\n{', '.join(SUSPECTS)}\n\n¿Quién crees que es el culpable?")
        if not suspect or suspect not in SUSPECTS:
            messagebox.showwarning("Error", "Sospechoso no válido.")
            return
        weapon = simpledialog.askstring("Arma", f"Armas:\n{', '.join(WEAPONS)}\n\n¿Qué arma se usó?")
        if not weapon or weapon not in WEAPONS:
            messagebox.showwarning("Error", "Arma no válida.")
            return
        location = simpledialog.askstring("Lugar", f"Áreas:\n{', '.join(AREAS)}\n\n¿Dónde ocurrió el crimen?")
        if not location or location not in AREAS:
            messagebox.showwarning("Error", "Lugar no válido.")
            return

        correct = (suspect == self.culprit and weapon == self.weapon and location == self.location)
        if correct:
            messagebox.showinfo("Victoria!", f"¡Correcto! El culpable era {self.culprit}, con la {self.weapon} en {self.location}.")
            self.root.quit()
        else:
            messagebox.showerror("Incorrecto", "Esa acusación no es correcta. Sigue investigando.")
            self.turns += 1


# ========================
# EJECUCIÓN DEL PROGRAMA
# ========================

if __name__ == "__main__":
    root = tk.Tk()
    app = ClueGameGUI(root)
    root.mainloop()
