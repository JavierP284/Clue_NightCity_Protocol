import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random
import textwrap
import os

# ========================
# DATOS PRINCIPALES DEL JUEGO
# ========================

SUSPECTS = ["Hacker", "Jefe seguridad", "Ejecutiva", "Mercenario", "Investigadora"]
WEAPONS = ["Mantis Blades", "Monowire", "Cuchillo", "Katana", "Pistola"]
AREAS = ["Laboratorio Biologico", "Sala Seguridad", "Penthouse", "Cafetería", "Taller de prototipos"]

# Plantilla para generar el resultado final del caso
NARRATIVE_TEMPLATE = (
    "El culpable, {culprit}, fue detectado en {location}. "
    "Usó su {weapon} para cometer el crimen. "
    "Algunos testigos reportaron movimientos sospechosos cerca de {secondary_area}. "
    "El hecho ocurrió durante {weather}."
)

# ========================
# FUNCIONES PARA GENERAR PISTAS DIGERIBLES
# ========================

def clue_physical(area, weapon, is_true):
    # Pista relacionada con rastros físicos del arma en un área.
    if is_true:
        return f"Se encontraron rastros en {area} que podrían indicar que se usó un {weapon}."
    else:
        other = random.choice([w for w in WEAPONS if w != weapon])
        return f"En {area} hay señales que parecen de un {other}, pero no es concluyente."

def clue_access(area, culprit, is_true):
    # Pista relacionada con la actividad o el acceso del sospechoso a un área.
    if is_true:
        return f"Se registró actividad reciente de alguien similar a {culprit} en {area}."
    else:
        other = random.choice([s for s in SUSPECTS if s != culprit])
        return f"Al parecer {other} estuvo en {area}, aunque no hay certeza."

def clue_social(area, culprit, is_true):
    # Pista basada en testimonios o rumores sociales.
    if is_true:
        return f"Un testigo vio a alguien con características de {culprit} cerca de {area}."
    else:
        other = random.choice([s for s in SUSPECTS if s != culprit])
        return f"Se rumorea que {other} estaba cerca de {area}, pero no es seguro."

def clue_item(area, weapon, is_true):
    # Pista relacionada con objetos o herramientas del arma.
    if is_true:
        return f"Se encontró un objeto relacionado con {weapon} dentro de {area}."
    else:
        other = random.choice([w for w in WEAPONS if w != weapon])
        return f"Hay un objeto que parece vinculado a un {other}, aunque no es definitivo."

def generate_clues(culprit, weapon, location, seed=None):
    # Genera el conjunto completo de pistas (verdaderas y falsas).
    if seed is not None:
        random.seed(seed)
    clues_by_area = {area: [] for area in AREAS}

    # Asegura que haya 4 pistas verdaderas clave
    clues_by_area[location].append({"text": clue_physical(location, weapon, True), "true": True})
    clues_by_area[location].append({"text": clue_item(location, weapon, True), "true": True})
    random_area = random.choice([a for a in AREAS if a != location])
    clues_by_area[random_area].append({"text": clue_access(random_area, culprit, True), "true": True})
    clues_by_area[random_area].append({"text": clue_social(random_area, culprit, True), "true": True})

    # Agrega 8 pistas falsas para la dificultad
    for _ in range(8):
        tpl = random.choice([clue_physical, clue_access, clue_social, clue_item])
        area = random.choice(AREAS)
        if tpl in (clue_physical, clue_item):
            txt = tpl(area, weapon, False)
        else:
            txt = tpl(area, culprit, False)
        clues_by_area[area].append({"text": txt, "true": False})

    # Mezclar y devolver las pistas
    for area in clues_by_area:
        random.shuffle(clues_by_area[area])
    return clues_by_area

# ========================
# CLASE PRINCIPAL DEL JUEGO: ClueGameGUI
# ========================

class ClueGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clue: Night City Protocol")
        self.root.geometry("850x700") # Tamaño inicial de la ventana
        self.root.config(bg="#101010")

        # Configuración de estilos Cyberpunk
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
        
        # ======== Barra de estado (Abajo, Izquierda) ========
        # Frame contenedor anclado al bottom del root para ocupar todo el ancho.
        status_frame = tk.Frame(root, bg="#101010", height=20)
        status_frame.pack(side="bottom", fill="x")
        
        self.status_var = tk.StringVar(value="Turno: 0 / 10")
        # La etiqueta se ancla a la IZQUIERDA del status_frame, solucionando el problema del centrado del contador.
        self.status_bar = tk.Label(status_frame, textvariable=self.status_var, bg="#101010", fg="#00ffe7",
                                   font=("Consolas", 11), anchor="w", padx=10) 
        self.status_bar.pack(side="left") 

        # ======== Scroll General (Canvas y Scrollbar) ========
        # El Canvas ocupa todo el espacio restante sobre la barra de estado.
        self.main_canvas = tk.Canvas(root, bg="#101010", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        
        # El frame que contiene todo el contenido real (es la ventana dentro del canvas).
        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#101010") 

        # Lógica para gestionar el Scroll y el Centrado Dinámico
        def on_frame_configure(event):
            # 1. Ajuste del Bounding Box para el Scroll y Centrado
            bbox = self.main_canvas.bbox("all")
            # Forzamos la anchura del frame a la anchura actual del canvas para evitar scroll horizontal.
            self.main_canvas.itemconfigure(self.frame_id, width=self.main_canvas.winfo_width())
            
            # Si el contenido es menor que el canvas, ajustamos el scrollregion a la altura del canvas.
            # Esto permite que el grid de centrado tenga el espacio completo para trabajar.
            if bbox[3] < self.main_canvas.winfo_height():
                 self.main_canvas.configure(scrollregion=(bbox[0], bbox[1], bbox[2], self.main_canvas.winfo_height()))
            # Si el contenido es más grande, se usa el tamaño real para permitir el scroll normal.
            else:
                 self.main_canvas.configure(scrollregion=bbox)

        # El binding en el frame detecta cambios en el tamaño del contenido.
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # Coloca el scrollable_frame dentro del canvas y guarda su ID.
        self.frame_id = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # El binding en el canvas detecta cuando la ventana principal se redimensiona
        # y llama a la función de configuración para reajustar el scroll y el centrado.
        def on_canvas_resize(event):
             on_frame_configure(event)
        self.main_canvas.bind('<Configure>', on_canvas_resize)

        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Empaquetado final del Canvas y la Scrollbar.
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Habilita el scroll con la rueda del ratón.
        self.main_canvas.bind_all("<MouseWheel>", lambda e: self.main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ======== Contenedor Principal (Marco de Centrado GRID) ========
        self.container = self.scrollable_frame
        
        # Marco que ocupa todo el espacio del scrollable_frame.
        self.main_content_frame = tk.Frame(self.container, bg="#101010")
        self.main_content_frame.pack(fill="both", expand=True)
        
        # Configuración de pesos: Clave para el centrado DINÁMICO.
        self.main_content_frame.grid_columnconfigure(0, weight=1) # Expande la columna horizontalmente
        self.main_content_frame.grid_rowconfigure(0, weight=1)    # Fila superior vacía (empuje vertical)
        self.main_content_frame.grid_rowconfigure(3, weight=1)    # Fila inferior vacía (empuje vertical)

        # ======== Logo (Se define como widget de GRID) ========
        logo_path = os.path.join("Images", "Logo Clue.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img.thumbnail((450, 200))
            logo_img = ImageTk.PhotoImage(img)
            self.logo = tk.Label(self.main_content_frame, image=logo_img, bg="#101010")
            self.logo.image = logo_img
        else:
            self.logo = tk.Label(self.main_content_frame, text="CLUE: Night City Protocol", font=("Consolas", 20, "bold"),
                     fg="#00ffe7", bg="#101010")


        # ======== Frame del Menú (Se define como widget de GRID) ========
        self.menu_frame = tk.Frame(self.main_content_frame, bg="#101010")
        
        # Contenido del menú (texto de introducción y botones)
        tk.Label(self.menu_frame, text=self.get_intro_text(), fg="#00ffe7", bg="#101010",
                 font=("Consolas", 12), justify="left").pack(pady=10)
        ttk.Button(self.menu_frame, text="Comenzar Investigación", command=lambda: self.show_frame("Investigation")).pack(pady=5)
        ttk.Button(self.menu_frame, text="Hacer Acusación", command=lambda: self.show_frame("Accusacion")).pack(pady=5)
        ttk.Button(self.menu_frame, text="Salir del Juego", command=self.root.quit).pack(pady=5)
        
        # ======== Creación de pantallas secundarias ========
        self.create_investigation_screen()
        self.create_acusacion_screen()
        
        # Muestra la pantalla de menú inicialmente.
        self.show_frame("Menu") 
    
    # ========================
    # INICIALIZAR JUEGO
    # ========================
    def initialize_game(self):
        # Establece la solución secreta del caso al inicio.
        self.culprit = random.choice(SUSPECTS)
        self.weapon = random.choice(WEAPONS)
        self.location = random.choice(AREAS)
        self.clues = generate_clues(self.culprit, self.weapon, self.location)
        self.found_clues = []
        self.turns = 0
        self.max_turns = 10

    # ========================
    # SECCIONES DE PANTALLA
    # ========================

    def create_investigation_screen(self):
        # Frame para la pantalla de investigación (usa pack como gestor)
        self.invest_frame = tk.Frame(self.container, bg="#101010") 

        # Área de texto para mostrar las pistas
        self.invest_text = tk.Text(self.invest_frame, wrap="word", height=20, width=100, bg="#181c1f",
                                   fg="#00ffe7", insertbackground="#00ffe7",
                                   font=("Consolas", 11), bd=2, relief="groove",
                                   highlightbackground="#00ffe7", highlightcolor="#00ffe7")
        self.invest_text.pack(pady=10)

        # Marco para botones de navegación
        btn_frame = tk.Frame(self.invest_frame, bg="#101010")
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Investigar Áreas", command=self.investigate_area_menu).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Investigar Sospechosos", command=self.investigate_suspect_menu).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Investigar Armas", command=self.investigate_weapon_menu).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Volver al Menú", command=lambda: self.show_frame("Menu")).grid(row=0, column=3, padx=5)

    def create_acusacion_screen(self):
        # Frame para la pantalla de acusación (usa pack como gestor)
        self.acusacion_frame = tk.Frame(self.container, bg="#0f0f1a")
        tk.Label(self.acusacion_frame, text="Hacer Acusación", fg="#00ffe7",
                 bg="#0f0f1a", font=("Consolas", 16, "bold")).pack(pady=10)

        form_frame = tk.Frame(self.acusacion_frame, bg="#0f0f1a")
        form_frame.pack(pady=10)

        # Comboboxes para la acusación formal
        tk.Label(form_frame, text="Selecciona Sospechoso:", bg="#0f0f1a", fg="#00ffe7", font=("Consolas", 12)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cb_suspect = ttk.Combobox(form_frame, values=SUSPECTS, font=("Consolas", 11), state="readonly")
        self.cb_suspect.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Selecciona Arma:", bg="#0f0f1a", fg="#00ffe7", font=("Consolas", 12)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.cb_weapon = ttk.Combobox(form_frame, values=WEAPONS, font=("Consolas", 11), state="readonly")
        self.cb_weapon.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Selecciona Lugar:", bg="#0f0f1a", fg="#00ffe7", font=("Consolas", 12)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.cb_location = ttk.Combobox(form_frame, values=AREAS, font=("Consolas", 11), state="readonly")
        self.cb_location.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.acusacion_frame, text="Pistas encontradas:", fg="#00ffe7", bg="#0f0f1a", font=("Consolas", 12, "bold")).pack(pady=(10,0))
        # Área de texto para revisar pistas encontradas
        self.acusacion_text = tk.Text(self.acusacion_frame, wrap="word", height=15, width=90, bg="#12131a", fg="#00ffe7", font=("Consolas", 11), bd=0)
        self.acusacion_text.pack(pady=5, padx=10, fill="both", expand=True)

        ttk.Button(self.acusacion_frame, text="Hacer Acusación", command=self.make_accusation).pack(pady=8)
        ttk.Button(self.acusacion_frame, text="⬅ Volver al Menú", command=lambda: self.show_frame("Menu")).pack(pady=10)

    # ========================
    # MOSTRAR SECCIÓN
    # Controla la visibilidad y el centrado de los frames.
    # ========================
    def show_frame(self, name):
        # 1. Oculta todos los frames que usan pack (investigación y acusación)
        for f in [self.invest_frame, self.acusacion_frame]:
            f.pack_forget()
            
        # 2. Oculta el marco de centrado (pack) y sus contenidos (grid)
        self.main_content_frame.pack_forget()
        self.logo.grid_forget()
        self.menu_frame.grid_forget()

        if name == "Menu":
            # Muestra el marco de centrado GRID (permite la dinámica).
            self.main_content_frame.pack(fill="both", expand=True)
            
            # Posiciona el logo y el menú en las filas centrales del grid.
            self.logo.grid(row=1, column=0, pady=(10, 5))
            self.menu_frame.grid(row=2, column=0, pady=10)
            
            self.main_canvas.yview_moveto(0) # Va al inicio del scroll.

        elif name == "Investigation":
            # Muestra la pantalla de investigación, ocupando todo el espacio.
            self.invest_frame.pack(fill="both", expand=True)
            
        elif name == "Accusacion":
            self.update_acusacion_pistas()
            # Muestra la pantalla de acusación, ocupando todo el espacio.
            self.acusacion_frame.pack(fill="both", expand=True)

    # ========================
    # FUNCIONES DE INVESTIGACION
    # ========================
    
    def clear_investigation_buttons(self):
        # Limpia los botones temporales de selección (áreas, sospechosos, armas)
        for widget in self.invest_frame.winfo_children():
            if isinstance(widget, ttk.Button) and widget.cget("text") in AREAS + SUSPECTS + WEAPONS:
                widget.destroy()

    def investigate_area_menu(self):
        # Prepara la pantalla para seleccionar un área a investigar.
        self.invest_text.delete("1.0", "end")
        self.invest_text.insert("end", "Selecciona un área para investigar:\n")

        self.clear_investigation_buttons()

        for area in AREAS:
            ttk.Button(self.invest_frame, text=area, command=lambda a=area: self.enter_area(a)).pack(pady=2)

    def investigate_suspect_menu(self):
        # Prepara la pantalla para seleccionar un sospechoso a investigar.
        self.invest_text.delete("1.0", "end")
        self.invest_text.insert("end", "Selecciona un sospechoso para investigar:\n")

        self.clear_investigation_buttons()

        for suspect in SUSPECTS:
            ttk.Button(self.invest_frame, text=suspect, command=lambda s=suspect: self.enter_suspect(s)).pack(pady=2)

    def investigate_weapon_menu(self):
        # Prepara la pantalla para seleccionar un arma a investigar.
        self.invest_text.delete("1.0", "end")
        self.invest_text.insert("end", "Selecciona un arma para investigar:\n")

        self.clear_investigation_buttons()

        for weapon in WEAPONS:
            ttk.Button(self.invest_frame, text=weapon, command=lambda w=weapon: self.enter_weapon(w)).pack(pady=2)

    def enter_area(self, area):
        # Lógica de investigar un área: consume un turno y revela pistas.
        if self.turns >= 10:
            messagebox.showinfo("Fin de Turnos", "Has agotado tus movimientos. ¡Hora de hacer una acusación!")
            return
        self.turns += 1
        self.status_var.set(f"Turno: {self.turns} / {self.max_turns}")
        self.invest_text.insert("end", f"\n--- {area} ---\n")
        available = self.clues.get(area, [])
        if not available:
            self.invest_text.insert("end", "No hay pistas visibles aquí.\n")
        else:
            num = min(2, len(available))
            revealed = available[:num]
            self.clues[area] = available[num:]
            for c in revealed:
                self.invest_text.insert("end", f"Pista encontrada: {c['text']}\n")
                self.found_clues.append(c["text"])
        self.invest_text.see("end") # Hace scroll al final del texto.

    def enter_suspect(self, suspect):
        # Lógica de investigar un sospechoso: consume un turno y busca pistas relacionadas.
        if self.turns >= 10:
            messagebox.showinfo("Fin de Turnos", "Has agotado tus movimientos. ¡Hora de hacer una acusación!")
            return
        self.turns += 1
        self.status_var.set(f"Turno: {self.turns} / {self.max_turns}")
        self.invest_text.insert("end", f"\n--- Investigando a {suspect} ---\n")
        
        possible_clues = []
        for area in AREAS:
            for i, c in enumerate(self.clues[area]):
                if suspect in c.get("text", ""):
                    possible_clues.append((area, i, c))
        
        if not possible_clues:
            self.invest_text.insert("end", f"No se encontró nada concluyente sobre {suspect}.\n")
        else:
            num = min(2, len(possible_clues))
            for _, _, c in possible_clues[:num]:
                self.invest_text.insert("end", f"Pista encontrada: {c['text']}\n")
                self.found_clues.append(c["text"])
                
        self.invest_text.see("end")

    def enter_weapon(self, weapon):
        # Lógica de investigar un arma: consume un turno y busca pistas relacionadas.
        if self.turns >= 10:
            messagebox.showinfo("Fin de Turnos", "Has agotado tus movimientos. ¡Hora de hacer una acusación!")
            return
        self.turns += 1
        self.status_var.set(f"Turno: {self.turns} / {self.max_turns}")
        self.invest_text.insert("end", f"\n--- Investigando el arma {weapon} ---\n")
        possible_clues = []
        for area in AREAS:
            for c in self.clues[area]:
                if weapon in c.get("text", ""):
                    possible_clues.append(c)
                    
        if not possible_clues:
            self.invest_text.insert("end", f"No se encontró información relevante sobre {weapon}.\n")
        else:
            num = min(2, len(possible_clues))
            revealed = possible_clues[:num]
            for c in revealed:
                self.invest_text.insert("end", f"Pista encontrada: {c['text']}\n")
                self.found_clues.append(c["text"])
                
        self.invest_text.see("end")

    # ========================
    # LÓGICA DE ACUSACIÓN Y REINICIO
    # ========================
    def update_acusacion_pistas(self):
        # Actualiza el área de texto de la pantalla de acusación con las pistas encontradas.
        self.acusacion_text.config(state="normal")
        self.acusacion_text.delete("1.0", "end")
        if not self.found_clues:
            self.acusacion_text.insert("end", "Aún no has encontrado pistas.\n")
        else:
            for p in self.found_clues:
                self.acusacion_text.insert("end", f"- {p}\n")
        self.acusacion_text.config(state="disabled")
    
    def make_accusation(self):
        # Procesa la acusación y muestra el resultado del caso.
        suspect = self.cb_suspect.get()
        weapon = self.cb_weapon.get()
        location = self.cb_location.get()
        if not suspect or not weapon or not location:
            messagebox.showwarning("Error", "Debes seleccionar una opción de cada categoría.")
            return

        correct = (suspect == self.culprit and weapon == self.weapon and location == self.location)

        # Genera la narrativa final del caso.
        narrative = NARRATIVE_TEMPLATE.format(
            culprit=self.culprit,
            weapon=self.weapon,
            location=self.location,
            secondary_area=random.choice([a for a in AREAS if a != self.location]),
            weather=random.choice(["una tormenta", "la noche silenciosa", "la tarde nublada"])
        )

        # Muestra la ventana de resultado (victoria/derrota).
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultado del Caso")
        result_window.geometry("600x400")
        result_window.config(bg="#101010")
        result_window.grab_set()
        
        # ... (configuración y contenido de la ventana de resultado)
        title_text = "¡Victoria Detective!" if correct else "Caso Fallido"
        title_color = "#00ff00" if correct else "#ff4040"

        tk.Label(result_window, text=title_text, font=("Consolas", 20, "bold"),
                fg=title_color, bg="#101010").pack(pady=20)

        narrative_label = tk.Text(result_window, wrap="word", height=10, width=60, bg="#181c1f",
                                fg="#00ffe7", font=("Consolas", 12), bd=2, relief="groove")
        narrative_label.pack(pady=10, padx=10)
        
        narrative_label.config(state="normal")
        if correct:
            narrative_label.insert("end", f"¡Correcto! Has resuelto el caso.\n\n{narrative}")
        else:
            narrative_label.insert("end", f"Esa acusación no es correcta.\nEl culpable era {self.culprit}, "
                                        f"con {self.weapon} en {self.location}.\n\n{narrative}")
        narrative_label.config(state="disabled")

        ttk.Button(result_window, text="Reiniciar Juego", command=lambda: [result_window.destroy(), self.restart_game()]).pack(pady=15)
        
    def restart_game(self):
        # Reinicia el estado del juego.
        self.initialize_game()
        self.status_var.set(f"Turno: {self.turns} / {self.max_turns}")
        self.show_frame("Menu")

    def get_intro_text(self):
        # Devuelve el texto descriptivo del juego.
        return textwrap.dedent("""\
            ==========================================
                    CLUE: NIGHT CITY PROTOCOL
            ==========================================
            El Director de Arasaka ha sido atacado.
            Tu objetivo es descubrir quién es el culpable, con qué arma y en qué lugar.
            Investiga áreas, sospechosos y armas para reunir pistas suficientes.
            Solo tienes 10 turnos antes de que el caso se enfríe.
            Dentro de la torre se encuentran cinco individuos:

            - Hacker
            - Jefe de seguridad
            - Ejecutiva
            - Mercenario
            - Investigadora

            Posibles armas utilizadas:
            - Mantis Blades
            - Monowire
            - Cuchillo
            - Katana
            - Pistola
                               
            Áreas dentro de la torre:
            - Laboratorio Biologico
            - Sala Seguridad
            - Penthouse
            - Cafetería
            - Taller de prototipos
                               
            Buena suerte, detective.
        """)
        

# ========================
# EJECUTAR EL JUEGO
# ========================
if __name__ == "__main__":
    root = tk.Tk()
    app = ClueGameGUI(root)
    root.mainloop()