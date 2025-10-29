import time
import pyfirmata  
import socket
import inspect
from datetime import datetime
#from servidor import conectar_servidor
#from servidor import enviar_datos

# --- Parche compatibilidad Python 3.11 ---
if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

# --- Conexión a Arduino ---
board = pyfirmata.Arduino('COM6')
print("Conectado a Arduino en COM6\n")

# --- Variables Globales ---
t1 = t2 = t3 = t4 = t5 = 0
promedio = 0
flag = 0
salir = False
n = 3.5
tendencia = 'NULA'
print("Ciclo de lectura inicial n = 3.5s\n")

# Capturas
capturasTemperatura = []
capturasTendencia = []
capturasFecha = []
print("Listas de capturas inicializadas.\n")

# --- Pines ---
sensor_temp  = board.get_pin('a:0:i')
led_verde    = board.get_pin('d:10:o')
led_amarillo = board.get_pin('d:9:o')
led_rojo     = board.get_pin('d:8:o')
pulsador     = board.get_pin('d:5:i')
print("Pines configurados.\n")

# --- Inicialización ---
it = pyfirmata.util.Iterator(board)
it.start()
sensor_temp.enable_reporting()
pulsador.enable_reporting()
print("Sensores habilitados.\n")

for _ in range(10):
    if sensor_temp.read() is not None:
        break
    time.sleep(0.1)

print("Programa iniciado muejejejeje. Ctrl+C para salir.\n")
# --------------------------------------------------------------------
# ------------------ CONFIGURACIÓN DEL SERVIDOR ----------------------
# --------------------------------------------------------------------
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = '10.245.52.39'  # Cambiar por la IP real del servidor
server_port = 12345
print(f"Conectando al servidor en {server_ip}:{server_port}...")
client_socket.connect((server_ip, server_port))
print("Servidor conectado correctamente.\n")
servidor_conectado = True
# --------------------------------------------------------------------
# ------------------------ BUCLE PRINCIPAL ---------------------------
# --------------------------------------------------------------------
presionado = False
inicio_pulso = 0
inicio = time.time()

try:
    while not salir:
        lectura = sensor_temp.read()
        estado = pulsador.read()
        ahora = time.time()

        # ===========================================================
        # ----------- CONTROL DEL BOTÓN DENTRO DEL BUCLE ------------
        # ===========================================================
        if estado is not None:
            estado = bool(estado) #caso base si no esta conectado boton

            # Cuando se presiona
            if estado and not presionado:
                presionado = True
                inicio_pulso = time.time() #empezar a contar tiempo
                led_verde.write(1)
                led_amarillo.write(1)
                led_rojo.write(1)
                n=0.05

            # Cuando se suelta
            elif not estado and presionado:
                presionado = False
                duracion = time.time() - inicio_pulso
                led_verde.write(0)
                led_amarillo.write(0)
                led_rojo.write(0)

                if duracion <= 0.2:
                    print(f"Botón mantenido {duracion:.2f}s → Finalizando programa...")
                    salir = True
                elif duracion < 2.5:
                    n = 2.5
                elif duracion > 10:
                    n = 10
                else:
                    n = duracion

                print(f"Duración del botón: {duracion:.2f}s → nuevo ciclo n = {n:.2f}s")

        # -------- LECTURA DE TEMPERATURA Y ENVÍO AL SERVIDOR -----------
        if lectura is not None and (ahora - inicio) >= n: #toma lecturas cada n segundos dados por el boton
            #temp_c = 5000 * (lectura / 1023)
            #temp_c = (lectura * lectura * 32)
            temp_c = (lectura * lectura * lectura) - (25 * lectura) + 30  # Curva calibrada
            # sino probar con esta otra curva
            #temp_c = (lectura * lectura) - (15 * lectura) + 40  # Curva calibrada 2
            #sino con esta otra
            #temp_c = (lectura * lectura * lectura * lectura) - (30 * lectura * lectura) + (200 * lectura) - 300  # Curva calibrada 3

            hora = datetime.now().strftime("%H:%M:%S")
            print(f"{hora} | Temperatura: {temp_c:.2f} °C")

            # Promedio móvil
            t5, t4, t3, t2, t1 = t4, t3, t2, t1, temp_c
            flag += 1
            if flag > 4:
                promedio = (t1 + t2 + t3 + t4 + t5) / 5
                print(f"Temperatura promedio: {promedio:.2f} °C")

                if temp_c < 0.965 * promedio:
                    led_verde.write(1); led_amarillo.write(0); led_rojo.write(0)
                    tendencia = 'BAJA'
                elif temp_c > 1.035 * promedio:
                    led_verde.write(0); led_amarillo.write(0); led_rojo.write(1)
                    tendencia = 'ALTA'
                else:
                    led_verde.write(0); led_amarillo.write(1); led_rojo.write(0)
                    tendencia = 'MEDIA'
            else:
                led_verde.write(1); led_amarillo.write(1); led_rojo.write(1)

            # Guardar captura
            capturasTemperatura.append(temp_c)
            capturasTendencia.append(tendencia)
            capturasFecha.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            
            # Enviar datos solo si hay conexión
            if servidor_conectado and client_socket:
                try:
                    mensaje = f"{hora} | Temp: {temp_c:.2f}°C | Prom: {promedio:.2f}°C"
                    client_socket.sendall(mensaje.encode())

                except Exception as e:
                    print(f"Error al enviar datos: {e}")
                    servidor_conectado = False
            else:
                print("Servidor no conectado, datos no enviados.\n")

            inicio = ahora

        time.sleep(0.05)


#--------------------------------- INICIO DE ESPACIO PUBLICITARIO  ------------------------------------


except KeyboardInterrupt:
    print("Programa terminado por el usuario.")
finally:
    print("\n=== Resumen de capturas ===")
    for i in range(len(capturasTemperatura)):
        print(f"Captura {i+1}: {capturasTemperatura[i]:.2f}°C, Tendencia: {capturasTendencia[i]}, Fecha: {capturasFecha[i]}")

    # Guardar capturas
    with open("capturas.txt", "w", encoding="utf-8") as archivo:
        for i in range(len(capturasTemperatura)):
            archivo.write(f"Captura {i+1}: {capturasTemperatura[i]:.2f}°C, Tendencia: {capturasTendencia[i]}, Fecha: {capturasFecha[i]}\n")

    print("\nDatos guardados en 'capturas.txt'.")

    # Cierre ordenado
    led_verde.write(0)
    led_amarillo.write(0)
    led_rojo.write(0)
    board.exit()

    client_socket.close()


#--------------------------------- FIN DE ESPACIO PUBLICITARIO  ------------------------------------


# made on earth by humans
