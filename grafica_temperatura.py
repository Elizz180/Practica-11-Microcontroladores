"""
Grafica de Temperatura en Tiempo Real - PC
Lee datos del Raspberry Pi Pico via USB Serial
"""

import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import tkinter as tk
from tkinter import messagebox
import threading
import time
import re

# ── CONFIGURACION ──────────────────────────────
PUERTO = 'COM10'
BAUDRATE = 115200
MAX_PUNTOS = 100
UMBRAL_VENTILADOR = 70

# ── DATOS ──────────────────────────────────────
tiempos = deque(maxlen=MAX_PUNTOS)
temperaturas = deque(maxlen=MAX_PUNTOS)
muestras_guardadas = []
tiempo_inicio = time.time()
serial_conn = None
leyendo = False


def leer_serial():
    global serial_conn, leyendo
    while leyendo:
        try:
            if serial_conn and serial_conn.in_waiting:
                linea = serial_conn.readline().decode('utf-8').strip()
                match = re.search(r"Temperatura:\s*([\d.]+)", linea)
                if match:
                    temp = float(match.group(1))
                    t = time.time() - tiempo_inicio
                    tiempos.append(t)
                    temperaturas.append(temp)
                    muestras_guardadas.append((t, temp))
        except Exception:
            pass
        time.sleep(0.05)


def guardar_datos():
    if not muestras_guardadas:
        messagebox.showinfo("Sin datos", "No hay datos para guardar.")
        return
    with open("temperaturas.csv", "w") as f:
        f.write("Tiempo(s),Temperatura(C)\n")
        for t, temp in muestras_guardadas:
            f.write(f"{t:.2f},{temp:.1f}\n")
    messagebox.showinfo("Guardado", f"Se guardaron {len(muestras_guardadas)} muestras en 'temperaturas.csv'")


def conectar():
    global serial_conn, leyendo, tiempo_inicio
    puerto = entry_puerto.get().strip()
    try:
        serial_conn = serial.Serial(puerto, BAUDRATE, timeout=1)
        tiempo_inicio = time.time()
        leyendo = True
        hilo = threading.Thread(target=leer_serial, daemon=True)
        hilo.start()
        btn_conectar.config(state=tk.DISABLED)
        btn_desconectar.config(state=tk.NORMAL)
        lbl_estado.config(text=f"Conectado en {puerto}", fg="#a6e3a1")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar:\n{e}")


def desconectar():
    global leyendo, serial_conn
    leyendo = False
    if serial_conn:
        serial_conn.close()
        serial_conn = None
    btn_conectar.config(state=tk.NORMAL)
    btn_desconectar.config(state=tk.DISABLED)
    lbl_estado.config(text="Desconectado", fg="#f38ba8")


# ── VENTANA TKINTER ────────────────────────────
root = tk.Tk()
root.title("Monitor de Temperatura LM35 - Raspberry Pi Pico")
root.configure(bg="#b6b6fa")
root.geometry("900x600")

frame_top = tk.Frame(root, bg="#1e1e2e", pady=8)
frame_top.pack(fill=tk.X)

tk.Label(frame_top, text="Monitor de Temperatura LM35",
         font=("Segoe UI", 16, "bold"), fg="#cdd6f4", bg="#1e1e2e").pack(side=tk.LEFT, padx=15)

lbl_temp_actual = tk.Label(frame_top, text="-- C",
                            font=("Segoe UI", 22, "bold"), fg="#a6e3a1", bg="#1e1e2e")
lbl_temp_actual.pack(side=tk.RIGHT, padx=20)

lbl_fan = tk.Label(frame_top, text="Ventilador: OFF",
                   font=("Segoe UI", 11), fg="#89dceb", bg="#1e1e2e")
lbl_fan.pack(side=tk.RIGHT, padx=10)

frame_ctrl = tk.Frame(root, bg="#313244", pady=6)
frame_ctrl.pack(fill=tk.X)

tk.Label(frame_ctrl, text="Puerto:", fg="#cdd6f4", bg="#313244",
         font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(15, 4))

entry_puerto = tk.Entry(frame_ctrl, width=10, font=("Segoe UI", 10),
                        bg="#45475a", fg="#cdd6f4", insertbackground="white")
entry_puerto.insert(0, PUERTO)
entry_puerto.pack(side=tk.LEFT, padx=4)

btn_conectar = tk.Button(frame_ctrl, text="Conectar", command=conectar,
                         bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                         relief=tk.FLAT, padx=10)
btn_conectar.pack(side=tk.LEFT, padx=6)

btn_desconectar = tk.Button(frame_ctrl, text="Desconectar", command=desconectar,
                             bg="#f38ba8", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                             relief=tk.FLAT, padx=10, state=tk.DISABLED)
btn_desconectar.pack(side=tk.LEFT, padx=4)

tk.Button(frame_ctrl, text="Guardar CSV", command=guardar_datos,
          bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
          relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=6)

lbl_estado = tk.Label(frame_ctrl, text="Desconectado", fg="#f38ba8",
                      bg="#313244", font=("Segoe UI", 10))
lbl_estado.pack(side=tk.RIGHT, padx=15)

# ── GRAFICA MATPLOTLIB ─────────────────────────
fig, ax = plt.subplots(figsize=(9, 4))
fig.patch.set_facecolor("#1e1e2e")
ax.set_facecolor("#181825")
ax.tick_params(colors="#cdd6f4")
ax.spines[:].set_color("#45475a")
ax.set_xlabel("Tiempo (s)", color="#cdd6f4", fontsize=10)
ax.set_ylabel("Temperatura (C)", color="#cdd6f4", fontsize=10)
ax.set_title("Temperatura en Tiempo Real", color="#cdd6f4", fontsize=12, fontweight="bold")
ax.grid(True, color="#313244", linestyle="--", alpha=0.7)

linea, = ax.plot([], [], color="#1991e7", linewidth=2, label="Temperatura")
ax.axhline(y=UMBRAL_VENTILADOR, color="#f38ba8", linewidth=1.2,
           linestyle="--", label=f"Umbral ventilador ({UMBRAL_VENTILADOR}C)")
ax.legend(loc="upper left", facecolor="#500066", labelcolor="#cdd6f4")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=6)


def actualizar_grafica(frame):
    if len(tiempos) > 1:
        linea.set_data(list(tiempos), list(temperaturas))
        ax.set_xlim(max(0, tiempos[-1] - MAX_PUNTOS), tiempos[-1] + 2)
        temp_min = min(temperaturas) - 5
        temp_max = max(temperaturas) + 5
        ax.set_ylim(temp_min, max(temp_max, UMBRAL_VENTILADOR + 10))

        ultima_temp = temperaturas[-1]
        lbl_temp_actual.config(text=f"{ultima_temp:.1f} C")

        if ultima_temp > UMBRAL_VENTILADOR:
            lbl_temp_actual.config(fg="#f38ba8")
            lbl_fan.config(text="Ventilador: ON", fg="#f38ba8")
        elif ultima_temp > 50:
            lbl_temp_actual.config(fg="#fab387")
            lbl_fan.config(text="Ventilador: OFF", fg="#fab387")
        else:
            lbl_temp_actual.config(fg="#a6e3a1")
            lbl_fan.config(text="Ventilador: OFF", fg="#89dceb")

    canvas.draw()


ani = animation.FuncAnimation(fig, actualizar_grafica, interval=500, cache_frame_data=False)

root.mainloop()
