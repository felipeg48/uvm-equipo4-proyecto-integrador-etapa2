"""Proyecto Integrador, Etapa 2: reproductor de música con tkinter y pygame.mixer.

Uso:
    python reproductor.py                 # abre el reproductor vacío (botón "Abrir carpeta…")
    python reproductor.py musica          # abre el reproductor con esa carpeta ya cargada
    python reproductor.py --prueba        # autoverificación de la lógica, sin ventana ni sonido
"""
# b) Bibliotecas que usa la aplicación
import os                                  # leer el contenido de la carpeta de música
import sys
import time
import tkinter as tk                       # ventana, botones, lista y deslizador
from tkinter import filedialog, ttk        # filedialog: cuadro para elegir la carpeta

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame                              # pygame.mixer carga y reproduce el audio

EXTENSIONES = (".mp3", ".wav", ".ogg")


def formato_tiempo(segundos):
    """Convierte segundos a mm:ss (por ejemplo 83.4 -> '01:23')."""
    s = int(segundos)
    return f"{s // 60:02d}:{s % 60:02d}"


class Reproductor:
    """Lógica del reproductor: lista de reproducción, estado y control de pygame.mixer.

    No sabe nada de la ventana; la interfaz solo llama a estos métodos y lee el estado.
    """

    def __init__(self):
        pygame.mixer.init()
        self.carpeta = ""
        self.canciones = []        # rutas completas de los archivos de audio
        self.indice = 0            # canción seleccionada
        self.estado = "detenido"   # "detenido", "reproduciendo" o "pausado"
        self.volumen = 0.7
        self._inicio = 0.0         # momento (time.monotonic) en que empezó el tramo actual
        self._acumulado = 0.0      # segundos reproducidos antes de la última pausa
        self._duraciones = {}      # caché: ruta -> duración en segundos
        pygame.mixer.music.set_volume(self.volumen)

    # e) Cargar la lista de canciones desde una carpeta
    def cargar_carpeta(self, carpeta):
        archivos = sorted(f for f in os.listdir(carpeta)
                          if f.lower().endswith(EXTENSIONES) and not f.startswith("."))
        self.detener()
        self.carpeta = carpeta
        self.canciones = [os.path.join(carpeta, f) for f in archivos]
        self.indice = 0
        return len(self.canciones)

    # d) Título (nombre del archivo sin extensión) de la canción seleccionada
    def titulo(self, i=None):
        if not self.canciones:
            return "Sin canciones"
        i = self.indice if i is None else i
        return os.path.splitext(os.path.basename(self.canciones[i]))[0]

    # c) Reproducir: empieza la canción seleccionada o continúa si estaba en pausa
    def reproducir(self, indice=None):
        if not self.canciones:
            return
        if indice is not None and indice != self.indice:
            self.indice = indice
            self.estado = "detenido"
        if self.estado == "pausado":
            pygame.mixer.music.unpause()
        elif self.estado == "detenido":
            pygame.mixer.music.load(self.canciones[self.indice])
            pygame.mixer.music.play()
            self._acumulado = 0.0
        else:
            return                 # ya está sonando
        self._inicio = time.monotonic()
        self.estado = "reproduciendo"

    # c) Pausa: congela la canción en el punto actual
    def pausar(self):
        if self.estado == "reproduciendo":
            pygame.mixer.music.pause()
            self._acumulado += time.monotonic() - self._inicio
            self.estado = "pausado"

    # c) Detener: para el audio y regresa al principio de la canción
    def detener(self):
        pygame.mixer.music.stop()
        self._acumulado = 0.0
        self.estado = "detenido"

    # c) Adelantar / avanzar: siguiente canción (al final regresa a la primera)
    def siguiente(self):
        if self.canciones:
            self.detener()
            self.reproducir((self.indice + 1) % len(self.canciones))

    # c) Retroceder / devolver: canción anterior (desde la primera va a la última)
    def anterior(self):
        if self.canciones:
            self.detener()
            self.reproducir((self.indice - 1) % len(self.canciones))

    # g) Volumen de 0 a 100
    def cambiar_volumen(self, porcentaje):
        self.volumen = max(0, min(100, float(porcentaje))) / 100
        pygame.mixer.music.set_volume(self.volumen)

    # h) Tiempo reproducido y duración total
    def transcurrido(self):
        if self.estado == "reproduciendo":
            return self._acumulado + time.monotonic() - self._inicio
        return self._acumulado

    def duracion(self, i=None):
        if not self.canciones:
            return 0.0
        ruta = self.canciones[self.indice if i is None else i]
        if ruta not in self._duraciones:
            self._duraciones[ruta] = pygame.mixer.Sound(ruta).get_length()
        return self._duraciones[ruta]

    def termino(self):
        """True cuando la canción llegó a su final sola (no por pausa ni por detener)."""
        return self.estado == "reproduciendo" and not pygame.mixer.music.get_busy()


class Interfaz:
    """f) Ventana de tkinter: botones, lista de reproducción, volumen y tiempo."""

    def __init__(self, raiz, reproductor):
        self.raiz, self.r = raiz, reproductor
        raiz.title("Reproductor de música")
        raiz.geometry("620x520")
        raiz.minsize(520, 440)
        estilo = ttk.Style()
        estilo.configure("Titulo.TLabel", font=("Helvetica", 18, "bold"))
        estilo.configure("Tiempo.TLabel", font=("Menlo", 13))

        marco = ttk.Frame(raiz, padding=16)
        marco.pack(fill="both", expand=True)

        # d) Canción actual
        ttk.Label(marco, text="Ahora suena", foreground="#666").pack(anchor="w")
        self.lbl_titulo = ttk.Label(marco, text="Sin canciones", style="Titulo.TLabel")
        self.lbl_titulo.pack(anchor="w", pady=(0, 6))
        self.lbl_estado = ttk.Label(marco, text="Detenido", foreground="#666")
        self.lbl_estado.pack(anchor="w")

        # h) Tiempo reproducido / duración total y barra de avance
        fila_tiempo = ttk.Frame(marco)
        fila_tiempo.pack(fill="x", pady=(10, 4))
        self.lbl_tiempo = ttk.Label(fila_tiempo, text="00:00", style="Tiempo.TLabel")
        self.lbl_tiempo.pack(side="left")
        self.lbl_total = ttk.Label(fila_tiempo, text="00:00", style="Tiempo.TLabel")
        self.lbl_total.pack(side="right")
        self.barra = ttk.Progressbar(fila_tiempo, maximum=1.0)
        self.barra.pack(side="left", fill="x", expand=True, padx=10)

        # f) Botones de control
        botones = ttk.Frame(marco)
        botones.pack(pady=10)
        for texto, accion in [("⏮ Anterior", self.r.anterior), ("▶ Reproducir", self.reproducir),
                              ("⏸ Pausa", self.r.pausar), ("⏹ Detener", self.r.detener),
                              ("⏭ Siguiente", self.r.siguiente)]:
            ttk.Button(botones, text=texto, command=lambda a=accion: self.ejecutar(a)).pack(side="left", padx=3)

        # g) Control deslizante de volumen
        fila_vol = ttk.Frame(marco)
        fila_vol.pack(fill="x", pady=(0, 10))
        ttk.Label(fila_vol, text="Volumen").pack(side="left")
        self.vol = tk.Scale(fila_vol, from_=0, to=100, orient="horizontal", showvalue=True,
                            command=self.r.cambiar_volumen)
        self.vol.set(int(self.r.volumen * 100))
        self.vol.pack(side="left", fill="x", expand=True, padx=10)

        # e) Lista de reproducción y botón para elegir la carpeta
        fila_lista = ttk.Frame(marco)
        fila_lista.pack(fill="x")
        ttk.Label(fila_lista, text="Lista de reproducción").pack(side="left")
        ttk.Button(fila_lista, text="📂 Abrir carpeta…", command=self.abrir_carpeta).pack(side="right")
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True, pady=(4, 0))
        self.lista = tk.Listbox(contenedor, activestyle="none", font=("Helvetica", 13),
                                selectbackground="#3b5bdb", selectforeground="white")
        barra_lista = ttk.Scrollbar(contenedor, command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra_lista.set)
        self.lista.pack(side="left", fill="both", expand=True)
        barra_lista.pack(side="right", fill="y")
        self.lista.bind("<Double-Button-1>", lambda e: self.reproducir_seleccion())
        self.lista.bind("<Return>", lambda e: self.reproducir_seleccion())

        self.lbl_pie = ttk.Label(marco, text="Abre una carpeta con archivos .mp3, .wav u .ogg",
                                 foreground="#666")
        self.lbl_pie.pack(anchor="w", pady=(6, 0))
        self.actualizar()

    def abrir_carpeta(self):
        carpeta = filedialog.askdirectory(title="Elige la carpeta con tu música")
        if carpeta:
            self.cargar(carpeta)

    def cargar(self, carpeta):
        n = self.r.cargar_carpeta(carpeta)
        self.lista.delete(0, "end")
        for i in range(n):
            self.lista.insert("end", f"{i + 1:>2}.  {self.r.titulo(i)}   ({formato_tiempo(self.r.duracion(i))})")
        self.lbl_pie.config(text=f"{n} canciones en la carpeta «{os.path.basename(carpeta)}»")
        self.refrescar()

    def reproducir(self):
        sel = self.lista.curselection()
        self.r.reproducir(sel[0] if sel else None)

    def reproducir_seleccion(self):
        sel = self.lista.curselection()
        if sel:
            self.r.detener()
            self.r.reproducir(sel[0])
            self.refrescar()

    def ejecutar(self, accion):
        accion()
        self.refrescar()

    def refrescar(self):
        """Pinta en pantalla el estado del reproductor."""
        r = self.r
        self.lbl_titulo.config(text=r.titulo())
        self.lbl_estado.config(text={"reproduciendo": "▶ Reproduciendo", "pausado": "⏸ En pausa",
                                     "detenido": "⏹ Detenido"}[r.estado])
        total = r.duracion()
        actual = min(r.transcurrido(), total)
        self.lbl_tiempo.config(text=formato_tiempo(actual))
        self.lbl_total.config(text=formato_tiempo(total))
        self.barra["value"] = actual / total if total else 0
        if r.canciones:
            self.lista.selection_clear(0, "end")
            self.lista.selection_set(r.indice)
            self.lista.see(r.indice)

    def actualizar(self):
        """Se llama sola cada 250 ms: avanza el reloj y pasa a la siguiente al terminar."""
        if self.r.termino():
            self.r.siguiente()
        self.refrescar()
        self.raiz.after(250, self.actualizar)


def prueba():
    """Revisa la lógica con el controlador de audio 'dummy' (sin bocinas ni ventana)."""
    import tempfile
    import generar_musica
    with tempfile.TemporaryDirectory() as tmp:
        for nombre, bpm, melodia in generar_musica.CANCIONES[:3]:
            generar_musica.sintetizar(os.path.join(tmp, nombre), bpm, melodia[:4])
        open(os.path.join(tmp, "notas.txt"), "w").close()       # no es audio: se ignora
        r = Reproductor()
        assert r.cargar_carpeta(tmp) == 3
        assert r.titulo() == "01 Amanecer en Do"
        r.reproducir()
        assert r.estado == "reproduciendo"
        time.sleep(0.2)
        r.pausar()
        t = r.transcurrido()
        assert r.estado == "pausado" and t >= 0.2
        time.sleep(0.2)
        assert r.transcurrido() == t, "en pausa el reloj no avanza"
        r.reproducir()
        assert r.estado == "reproduciendo"
        r.detener()
        assert r.estado == "detenido" and r.transcurrido() == 0
        r.siguiente()
        assert r.indice == 1 and r.estado == "reproduciendo"
        r.anterior(); r.anterior()
        assert r.indice == 2, "desde la primera, anterior va a la última"
        r.siguiente()
        assert r.indice == 0, "desde la última, siguiente va a la primera"
        r.cambiar_volumen(150)
        assert r.volumen == 1.0
        r.cambiar_volumen(35)
        assert abs(r.volumen - 0.35) < 1e-9
        assert abs(r.duracion(0) - 4 * 60 / 100) < 0.01
        assert formato_tiempo(83.4) == "01:23"
    print("prueba: todo correcto")


if __name__ == "__main__":
    if "--prueba" in sys.argv:
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        prueba()
    else:
        raiz = tk.Tk()
        app = Interfaz(raiz, Reproductor())
        if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
            app.cargar(sys.argv[1])
        raiz.mainloop()
