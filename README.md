# Reproductor de música en Python

**Proyecto Integrador, Etapa 2: Algoritmos en Inteligencia Artificial**
Universidad del Valle de México · Algoritmos y Complejidad Computacional · Equipo 4

Integrantes:

- Ariadna Jaeline García Juarez
- Rommel David García Montoya
- Enrique Gome López
- Felipe Gutiérrez Cruz

Profesor: Ph.D Ernesto Bautista Thompson

---

## ¿Qué es?

Este proyecto es un reproductor de música de escritorio, con interfaz gráfica, hecho en Python con tres bibliotecas:

| Biblioteca | Para qué se usa |
|---|---|
| `tkinter` y `tkinter.filedialog` | La ventana, los botones, la lista y el control de volumen; `filedialog` abre el cuadro para elegir la carpeta de música. |
| `pygame.mixer` | Carga y reproduce el audio, y controla la pausa, el paro y el volumen. |
| `os` | Lee la carpeta y arma la lista de reproducción con los archivos de audio. |

### Funciones

- **Abrir carpeta…**: carga los archivos `.mp3`, `.wav` y `.ogg` de una carpeta y los muestra en la lista de reproducción, cada uno con su duración.
- **▶ Reproducir**: empieza la canción seleccionada o la continúa si estaba en pausa.
- **⏸ Pausa**: congela la canción, y también el reloj, en el punto actual.
- **⏹ Detener**: para la música y regresa al principio de la canción.
- **⏭ Siguiente / ⏮ Anterior**: cambian de canción. La lista es circular: después de la última va la primera.
- **Volumen**: un control deslizante de 0 a 100.
- **Ahora suena**: muestra el título de la canción, su estado, el tiempo reproducido, la duración total y una barra de avance.
- **Doble clic** o **Enter** sobre una canción de la lista la reproduce.
- Cuando una canción termina, el reproductor pasa solo a la siguiente.

---

## Requisitos

- **Python 3.10 o más reciente**, con soporte para Tk.
- **pygame 2.5 o más reciente**, que se instala en el paso 3.

Revisa si tu Python ya trae Tk:

```bash
python3 -c "import tkinter; print('Tk', tkinter.TkVersion)"
```

Si este comando marca `ModuleNotFoundError: No module named '_tkinter'`, instala Tk así:

| Sistema | Cómo instalar Tk |
|---|---|
| Windows | El instalador de [python.org](https://www.python.org/downloads/) ya lo incluye. Deja marcada la opción *tcl/tk and IDLE*. |
| macOS con el instalador de python.org | Ya viene incluido. |
| macOS con Homebrew | `brew install python-tk@3.13` (cambia `3.13` por tu versión de Python). |
| Ubuntu / Debian | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |

---

## Instalación

### 1. Descarga el código

```bash
git clone https://github.com/felipeg48/uvm-equipo4-proyecto-integrador-etapa2.git
cd uvm-equipo4-proyecto-integrador-etapa2
```

También puedes usar **Code → Download ZIP** en GitHub y descomprimir el archivo.

### 2. Crea un entorno virtual

El entorno virtual mantiene pygame separado del resto de tu sistema.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Si PowerShell no deja activar el entorno, ejecuta primero
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

Con el entorno activo, la terminal muestra `(.venv)` al inicio de la línea.

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Comprueba la instalación

```bash
python reproductor.py --prueba
```

Debe imprimir:

```text
prueba: todo correcto
```

Esta prueba revisa la lógica del reproductor sin abrir la ventana y sin usar las bocinas: carga de la carpeta, pausa, detener, lista circular, volumen y duración.

---

## Cómo correrlo

### Con la música de prueba

El repositorio ya trae seis piezas cortas en `musica/`. Son grabaciones de música clásica de **dominio público o CC0**,
del proyecto Musopen, publicadas en Wikimedia Commons (ver [Créditos de la música](#créditos-de-la-música)).

```bash
python reproductor.py musica
```

Se abre la ventana con las seis canciones en la lista. Presiona **▶ Reproducir**.

### Con tu propia música

```bash
python reproductor.py
```

Presiona **📂 Abrir carpeta…** y elige cualquier carpeta que tenga archivos `.mp3`, `.wav` u `.ogg`.
También puedes pasar la carpeta al iniciar:

```bash
python reproductor.py "/ruta/a/mi/musica"
```

### Resumen de comandos

| Comando | Qué hace |
|---|---|
| `python reproductor.py` | Abre el reproductor vacío. |
| `python reproductor.py <carpeta>` | Abre el reproductor con esa carpeta cargada. |
| `python reproductor.py --prueba` | Autoverificación de la lógica. |
| `python capturas_gui.py <carpeta>` | Toma capturas de la ventana en cada estado (solo macOS; suena música). |

---

## Estructura del proyecto

```text
.
├── reproductor.py       # aplicación: clases Reproductor (lógica + pygame.mixer) e Interfaz (tkinter)
├── capturas_gui.py      # capturas automáticas de la ventana para el reporte (macOS)
├── musica/              # 6 piezas .ogg de dominio público (4.2 MB) + CREDITOS.md y fuentes.tsv
├── requirements.txt     # pygame
└── README.md
```

### Cómo está organizado el código

- **`Reproductor`** guarda la lista de canciones, la canción actual y el estado (`detenido`, `reproduciendo` o `pausado`). Es la única clase que llama a `pygame.mixer`. Mide el tiempo reproducido con `time.monotonic()`, así el reloj se congela en pausa y vuelve a cero al detener.
- **`Interfaz`** construye la ventana. Cada botón llama a un método de `Reproductor` y luego vuelve a dibujar la pantalla. Con `raiz.after(250, …)` la pantalla se actualiza cuatro veces por segundo sin bloquear la ventana, y en esa misma revisión se detecta cuándo termina una canción.
- **Siguiente y anterior** calculan el nuevo índice con `(indice ± 1) % len(canciones)`. Es una operación O(1) y hace que la lista sea circular.

---

## Créditos de la música

Las seis piezas de `musica/` son grabaciones de [Musopen](https://musopen.org) publicadas en
[Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Musopen), con licencia de dominio público o CC0.
Se pueden usar sin pedir permiso. Elegimos piezas cortas (29 a 64 s) y archivos chicos (menos de 1 MB cada uno).

| Archivo | Obra (compositor) | Licencia |
|---|---|---|
| `01 Clementi - Sonatina en Do, Vivace.ogg` | Sonatina Op. 36 n.º 1, III. Vivace (Muzio Clementi); intérprete: Alessio Cesaroni | CC0 |
| `02 Milhaud - Tambourin.ogg` | Suite d'après Corrette, II. Tambourin (Darius Milhaud) | Dominio público |
| `03 Mussorgsky - Promenade.ogg` | Cuadros de una exposición, Promenade (Modest Músorgski) | Dominio público |
| `04 Schumann - La gallina ciega.ogg` | Escenas infantiles, Op. 15, III (Robert Schumann) | Dominio público |
| `05 Schumann - Caballero del caballito.ogg` | Escenas infantiles, Op. 15, IX (Robert Schumann) | Dominio público |
| `06 Strauss - Bosques de Viena (cítara).ogg` | Cuentos de los bosques de Viena, Op. 325, solo de cítara (Johann Strauss II) | CC0 |

Los enlaces a cada archivo en Commons están en [`musica/CREDITOS.md`](musica/CREDITOS.md).

---

## Problemas comunes

| Síntoma | Solución |
|---|---|
| `No module named '_tkinter'` | A tu Python le falta Tk; consulta la sección [Requisitos](#requisitos). |
| `No module named 'pygame'` | Activa el entorno virtual (paso 2) y vuelve a correr `pip install -r requirements.txt`. |
| `pygame.error: No available audio device` | El equipo no tiene salida de audio; conecta unas bocinas o unos audífonos. La prueba `--prueba` funciona aunque no haya audio. |
| Un `.mp3` no se reproduce | Conviértelo a `.ogg` o `.wav`; algunos MP3 con codificación poco común no los soporta SDL. |
