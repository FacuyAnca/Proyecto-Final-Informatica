import socket
import matplotlib.pyplot as plt
# Crear socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '10.16.115.80'  # IP del servidor
server_port = 12345
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print(f"Servidor escuchando en {server_ip}:{server_port}")
conn, addr = server_socket.accept()
print(f"Conexión establecida con {addr}")

tiempos = []
temperaturas = []
promedios = []

plt.ion()
plt.figure()
plt.show()



try:
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
        except TimeoutError:
            continue  # si no hay datos, seguir sin cortar el bucle

        mensajes = data.decode().split('\n')  # separa los mensajes por salto de línea
        for mensaje in mensajes:
            mensaje = mensaje.strip()
            if not mensaje:
                continue

            partes = mensaje.split('|')
            if len(partes) < 3:  
                continue
            print(f"Recibido: {mensaje}")

            partes = mensaje.split('|')

            hora = partes[0].strip()
            temp = float(partes[1].split(':')[1].replace('°C', '').strip())
            prom = float(partes[2].split(':')[1].replace('°C', '').strip())

            tiempos.append(hora)
            temperaturas.append(temp)
            promedios.append(prom)

            # actualizar gráfico
            plt.cla()
            plt.plot(tiempos, temperaturas, label='Temp')
            plt.plot(tiempos, promedios, label='Promedio', linestyle='--')
            plt.xlabel('Tiempo')
            plt.ylabel('°C')
            plt.title('Temperatura en tiempo real')
            plt.legend()
            plt.xticks(rotation=90)
            plt.tight_layout()
            plt.pause(0.01)

finally:
    conn.close()           # Cierra conexión con el cliente
    server_socket.close()  # Cierra el servidor
    print("Caso cerrado.")


