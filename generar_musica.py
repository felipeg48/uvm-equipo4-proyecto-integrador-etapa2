"""Genera canciones de prueba (WAV) en la carpeta musica/, sin derechos de autor.

Cada canción es una melodía sintetizada con ondas senoidales, para poder probar el
reproductor sin depender de archivos con copyright. Solo usa la biblioteca estándar.

Uso:
    python generar_musica.py [carpeta]      # por defecto: musica/
"""
import math
import os
import struct
import sys
import wave

TASA = 22050  # muestras por segundo
NOTAS = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.00,
         "A": 440.00, "B": 493.88, "c": 523.25, "d": 587.33, "e": 659.25, "-": 0}

# (nombre del archivo, tempo en BPM, melodía; cada letra es una nota de un tiempo)
CANCIONES = [
    ("01 Amanecer en Do.wav", 100, "CEGcGECEGcGEFAcAFDFAdAFDEGcGECEGcGEc"),
    ("02 Camino al mar.wav", 120, "EDCDEEE-DDD-EGG-EDCDEEEEDDEDC---"),
    ("03 Lluvia de octubre.wav", 80, "AGFE-FGA-cBA-GFE-DEFGA---"),
    ("04 Ciudad de noche.wav", 140, "CCGGAAG-FFEEDDC-GGFFEED-GGFFEED-CCGGAAG-FFEEDDC-"),
    ("05 Viento del norte.wav", 90, "EFGcBAGFE-DEFGAGFED-CDEFGFEDC---"),
    ("06 Último tren.wav", 110, "cBAGFEDCDEFGABc-cGEC-DFAc-BGDB-c---"),
]


def sintetizar(ruta, bpm, melodia):
    dur = 60 / bpm
    muestras = bytearray()
    for i, nota in enumerate(melodia):
        f = NOTAS[nota]
        n = int(TASA * dur)
        for k in range(n):
            t = k / TASA
            env = min(1, k / 300) * math.exp(-3 * t / dur)          # ataque corto y caída suave
            bajo = 0.25 * math.sin(2 * math.pi * NOTAS["CEGF"[i // 8 % 4]] / 2 * t)
            v = (0.55 * math.sin(2 * math.pi * f * t) * env if f else 0) + bajo
            muestras += struct.pack("<h", int(max(-1, min(1, v)) * 12000))
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TASA)
        w.writeframes(bytes(muestras))


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "musica"
    os.makedirs(carpeta, exist_ok=True)
    for nombre, bpm, melodia in CANCIONES:
        ruta = os.path.join(carpeta, nombre)
        sintetizar(ruta, bpm, melodia)
        print(f"ok: {ruta}  ({len(melodia) * 60 / bpm:.0f} s)")
