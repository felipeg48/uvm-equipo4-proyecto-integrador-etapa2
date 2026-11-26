"""Toma las capturas de la ventana del reproductor para el reporte (solo macOS).

Abre la aplicación real, presiona los botones en orden y guarda una imagen de la ventana
después de cada paso con `screencapture`.

Uso:
    python capturas_gui.py ../capturas
"""
import os
import subprocess
import sys
import tkinter as tk

from reproductor import Interfaz, Reproductor

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "capturas"
MUSICA = os.path.abspath("musica")


def capturar(raiz, nombre):
    raiz.update()
    barra = raiz.winfo_rooty() - raiz.winfo_y()          # alto de la barra de título
    x, y = raiz.winfo_x(), raiz.winfo_y()
    w, h = raiz.winfo_width(), raiz.winfo_height() + barra
    ruta = os.path.join(SALIDA, nombre)
    subprocess.run(["screencapture", "-x", "-o", f"-R{x},{y},{w},{h}", ruta], check=True)
    print("ok:", ruta)


def boton(app, texto):
    """Busca el botón por su texto y lo presiona, como lo haría el usuario."""
    def buscar(w):
        for hijo in w.winfo_children():
            if hijo.winfo_class() == "TButton" and texto in hijo.cget("text"):
                return hijo
            encontrado = buscar(hijo)
            if encontrado:
                return encontrado
    buscar(app.raiz).invoke()


def main():
    os.makedirs(SALIDA, exist_ok=True)
    raiz = tk.Tk()
    raiz.geometry("+120+120")
    app = Interfaz(raiz, Reproductor())
    raiz.lift()
    raiz.attributes("-topmost", True)

    pasos = [
        (800, lambda: None, "g01_inicio.png"),
        (300, lambda: app.cargar(MUSICA), "g03_lista_cargada.png"),
        (300, lambda: boton(app, "Reproducir"), None),
        (4200, lambda: None, "g04_reproduciendo.png"),
        (100, lambda: boton(app, "Pausa"), None),
        (1500, lambda: None, "g05_pausa.png"),
        (100, lambda: boton(app, "Reproducir"), None),
        (2000, lambda: None, "g06_continua.png"),
        (100, lambda: boton(app, "Siguiente"), None),
        (3200, lambda: None, "g07_siguiente.png"),
        (100, lambda: boton(app, "Anterior"), None),
        (2200, lambda: None, "g08_anterior.png"),
        (100, lambda: boton(app, "Detener"), None),
        (500, lambda: None, "g09_detenido.png"),
        (100, lambda: (app.lista.selection_clear(0, "end"), app.lista.selection_set(3),
                       app.reproducir_seleccion()), None),
        (100, lambda: app.vol.set(25), None),
        (2600, lambda: None, "g10_volumen_y_doble_clic.png"),
        (100, lambda: (app.r.detener(), app.r.reproducir(1)), None),     # canción 02 dura 29 s
        (26500, lambda: None, "g11_casi_termina.png"),
        (3500, lambda: None, "g12_avance_automatico.png"),
        (100, lambda: app.r.detener(), None),
    ]

    def correr(i=0):
        if i == len(pasos):
            raiz.destroy()
            return
        espera, accion, nombre = pasos[i]
        accion()
        app.refrescar()

        def despues():
            if nombre:
                capturar(raiz, nombre)
            correr(i + 1)
        raiz.after(espera, despues)

    raiz.after(500, correr)
    raiz.mainloop()


if __name__ == "__main__":
    main()
