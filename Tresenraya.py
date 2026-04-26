import time
import math
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

# Estilos necesarios
display(HTML("""
<style>
  .titulo { font-family: monospace; font-size: 22px; font-weight: bold; margin-bottom: 8px; }
  .tiempo { font-family: monospace; font-size: 13px; color: #888; margin-top: 8px; line-height: 1.8; }
  .resultado { font-size: 18px; font-weight: bold; margin-top: 10px; }
  .widget-button { font-size: 40px !important; font-weight: bold !important; }
</style>
"""))

# Combinaciones para ganar
COMBINACIONES = [
    [0,1,2], [3,4,5], [6,7,8],
    [0,3,6], [1,4,7], [2,5,8],
    [0,4,8], [2,4,6]
]

TIEMPO_IA = 1  # Se le agrego delay a la ia para darle posibilidades de ganar al jugador
tablero = [" "] * 9
tiempos_x = []
tiempos_ia = []
turno_inicio = [time.time()]
juego_activo = [True]
salida = widgets.Output()
botones = []

# Logica del juego
def verificar_ganador(t):
    for a, b, c in COMBINACIONES:
        if t[a] != " " and t[a] == t[b] == t[c]:
            return t[a]
    if " " not in t:
        return "empate"
    return None
def minimax(t, es_maximizador):
    resultado = verificar_ganador(t)
    if resultado:
        return {"O": 1, "X": -1, "empate": 0}[resultado]
    simbolo = "O" if es_maximizador else "X"
    valores = []
    for i in range(9):
        if t[i] == " ":
            t[i] = simbolo
            valor = minimax(t, not es_maximizador)
            valores.append(valor)
            t[i] = " "
    return max(valores) if es_maximizador else min(valores)
def mejor_jugada(t):
    mejor_valor = -math.inf
    mejor_movimiento = -1
    for i in range(9):
        if t[i] == " ":
            t[i] = "O"
            valor = minimax(t, False)
            t[i] = " "

            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = i
    return mejor_movimiento
def ganador_por_tiempo():
    if not tiempos_x or not tiempos_ia:
        return None, None, None
    promedio_x = sum(tiempos_x) / len(tiempos_x)
    promedio_ia = sum(tiempos_ia) / len(tiempos_ia)
    if promedio_x < promedio_ia:
        ganador = "Jugador (X)"
    elif promedio_ia < promedio_x:
        ganador = "IA (O)"
    else:
        ganador = "Empate de tiempos"
    return promedio_x, promedio_ia, ganador

# Render visual
def render():
    with salida:
        clear_output(wait=True)
        historial = ""
        total = max(len(tiempos_x), len(tiempos_ia))
        for i in range(total):
            if i < len(tiempos_x):
                historial += f'Jugada {i*2+1} (X): {tiempos_x[i]:.3f}s<br>'
            if i < len(tiempos_ia):
                historial += f'Jugada {i*2+2} (IA): {tiempos_ia[i]:.3f}s<br>'
        display(HTML(f"""
            <div class="titulo">Tres en Raya — Minimax</div>
            <div class="tiempo">{historial}</div>
        """))
        if not juego_activo[0]:
            px, pi, ganador = ganador_por_tiempo()
            if px:
                display(HTML(f"""
                    <div class="resultado">
                        Promedio X: {px:.3f}s | Promedio IA: {pi:.3f}s<br>
                        Ganador por tiempo: {ganador}
                    </div>
                """))
        display(widgets.GridBox(
            botones,
            layout=widgets.Layout(
                grid_template_columns="repeat(3, 90px)",
                grid_gap="6px"
            )
        ))
def terminar_juego(resultado):
    juego_activo[0] = False
    for b in botones:
        b.disabled = True
    render()
    mensajes = {
        "X": "Ganaste",
        "O": "Ganó la IA",
        "empate": "Empate"
    }
    with salida:
        display(HTML(f'<div class="resultado">{mensajes[resultado]}</div>'))

# Turnos
def jugar(pos):
    if not juego_activo[0] or tablero[pos] != " ":
        return

    # Turno del jugador
    tiempo = time.time() - turno_inicio[0]
    tiempos_x.append(round(tiempo, 3))
    tablero[pos] = "X"
    botones[pos].description = "✕"
    botones[pos].disabled = True
    ganador = verificar_ganador(tablero)
    if ganador:
        terminar_juego(ganador)
        return

    # Bloquear mientras juega IA
    for b in botones:
        b.disabled = True
    render()

    # Turno de la IA
    movimiento = mejor_jugada(tablero)
    tablero[movimiento] = "O"
    tiempos_ia.append(TIEMPO_IA)
    botones[movimiento].description = "◯"
    botones[movimiento].disabled = True
    ganador = verificar_ganador(tablero)
    if ganador:
        terminar_juego(ganador)
        return
    if " " not in tablero:
        terminar_juego("empate")
        return

    # Desbloqueo de botones
    for i, b in enumerate(botones):
        if tablero[i] == " ":
            b.disabled = False
    turno_inicio[0] = time.time()
    render()

# Crear el tablero
for i in range(9):
    boton = widgets.Button(
        description=" ",
        layout=widgets.Layout(width="85px", height="85px")
    )
    boton.on_click(lambda _, idx=i: jugar(idx))
    botones.append(boton)
display(salida)
turno_inicio[0] = time.time()
render()
