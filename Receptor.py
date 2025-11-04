import socket
import matplotlib.pyplot as plt
import time
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '192.168.56.1'  # IP del servidor
server_port = 31415
client_socket.connect((server_ip, server_port))
print("Conectado al servidor\n")

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-', label="Temperatura (°C)")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Temperatura (°C)")
ax.set_title("Lecturas del sensor en tiempo real")
ax.legend()
ax.grid(True)

tiempos = []
temperaturas = []
t0 = time.time()

try:
    while True:
        data = client_socket.recv(1024).decode().strip()
        if not data:
            break

        try:
            datos = json.loads(data)
            temp = float(datos["Temperatura"])
            tendencia = datos["Tendencia"]   # texto
            hora = datos["Hora"]              # string
        except (json.JSONDecodeError, KeyError, ValueError):
            continue

        temperaturas.append(temp)
        tiempos.append(time.time() - t0)

        print(f"Temp: {temp:.2f}°C | Tendencia: {tendencia} | Hora: {hora}")

        # Actualizar gráfico
        line.set_xdata(tiempos)
        line.set_ydata(temperaturas)
        ax.set_xlim(0, max(tiempos)+1)
        ax.relim()
        ax.autoscale_view()
        plt.pause(0.1)
        plt.draw()

except KeyboardInterrupt:
    print("\nCliente detenido manualmente.")

finally:
    client_socket.close()
    print("Conexión cerrada.")
