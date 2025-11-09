import socket                 # Para manejar conexiones de red (TCP en este caso)
import matplotlib.pyplot as plt  # Para graficar datos en tiempo real

# ============================================================
# CONFIGURACIÓN DEL SERVIDOR TCP
# ============================================================
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
# Crea un socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)

server_ip = '192.168.204.39'  # Dirección IP donde va a escuchar el servidor
server_port = 12345           # Puerto de escucha (debe ser el mismo del cliente)

server_socket.bind((server_ip, server_port))  # Asocia el socket a la IP y el puerto
server_socket.listen(1)       # Comienza a escuchar conexiones (1 = solo una conexión permitida)

print(f"Servidor escuchando en {server_ip}:{server_port}")
conn, addr = server_socket.accept()  # Espera a que un cliente se conecte (bloqueante)
print(f"Conexión establecida con {addr}")

# ============================================================
# LISTAS PARA GUARDAR DATOS Y GRAFICAR
# ============================================================
tiempos = []        # Guarda los tiempos de cada recepción
temperaturas = []   # Guarda temperatura actual
promedios = []      # Guarda el promedio móvil enviado por el cliente

plt.ion()  # Activa el modo interactivo para actualizar el gráfico en vivo

# ============================================================
# BUCLE PRINCIPAL DE RECEPCIÓN Y GRAFICADO
# ============================================================
try:
    while True:
        data = conn.recv(1024)   # Recibe hasta 1024 bytes del cliente
        if not data:             # Si no llega nada, se terminó la conexión
            break

        mensaje = data.decode()  # Decodifica los bytes a texto
        print(f"Recibido: {mensaje}")

        # -------------------------
        # PARSEAR DATOS DEL MENSAJE
        # -------------------------
        partes = mensaje.split('|')  # Divide el mensaje en sus partes: hora | temp | prom

        hora = partes[0].strip()     # Extrae la hora
        temp = float(partes[1].split(':')[1].replace('°C', '').strip())   # Extrae temperatura como número
        prom = float(partes[2].split(':')[1].replace('°C', '').strip())   # Extrae promedio como número

        # -------------------------
        # GUARDAR DATOS EN LISTAS
        # -------------------------
        tiempos.append(hora)
        temperaturas.append(temp)
        promedios.append(prom)

        # -------------------------
        # ACTUALIZAR GRAFICO EN TIEMPO REAL
        # -------------------------
        plt.cla()  # Limpia la gráfica anterior para dibujar sobre la misma ventana
        plt.plot(tiempos, temperaturas, label='Temp')
        plt.plot(tiempos, promedios, label='Promedio', linestyle='--')

        plt.xlabel('Tiempo')
        plt.ylabel('°C')
        plt.title('Temperatura en tiempo real')
        plt.legend()
        plt.xticks(rotation=45)  # Rota las etiquetas para que no se encimen
        plt.tight_layout()
        plt.pause(0.01)         # Pequeña pausa para actualizar la imagen

# ============================================================
# FINALIZAR CONEXIÓN
# ============================================================
finally:
    conn.close()           # Cierra conexión con el cliente
    server_socket.close()  # Cierra el servidor
    print("Caso cerrado.")
