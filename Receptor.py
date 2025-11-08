import socket
import matplotlib.pyplot as plt

# Crear socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '192.168.204.39'  # IP del servidor
server_port = 12345
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print(f"Servidor escuchando en {server_ip}:{server_port}")
conn, addr = server_socket.accept()
print(f"Conexión establecida con {addr}")

tiempos = []
temperaturas = []
promedios = []

plt.ion()  # Modo interactivo para actualizar el gráfico en tiempo real

try:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        mensaje = data.decode()
        print(f"Recibido: {mensaje}")

        # Parsear
        partes = mensaje.split('|')
        hora = partes[0].strip()
        temp = float(partes[1].split(':')[1].replace('°C','').strip())
        prom = float(partes[2].split(':')[1].replace('°C','').strip())

        # Guardar
        tiempos.append(hora)
        temperaturas.append(temp)
        promedios.append(prom)

        # Actualizar gráfico
        plt.cla()
        plt.plot(tiempos, temperaturas, label='Temp')
        plt.plot(tiempos, promedios, label='Promedio', linestyle='--')
        plt.xlabel('Tiempo')
        plt.ylabel('°C')
        plt.title('Temperatura en tiempo real')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.pause(0.01)

finally:
    conn.close()
    server_socket.close()
    print("Caso cerrado.")
