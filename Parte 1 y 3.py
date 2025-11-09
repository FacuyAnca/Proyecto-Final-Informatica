import time
# Modulo estándar de manejo de tiempo, usa "time.sleep(sec)" o "time.time()" para marca de tiempo Unix
# Maneja tiempos y pausas, mide el tiempo en que algo succeda
import pyfirmata  
# Es una libreria de terceros para controlar arduino con el protoco firmata, estando este cargado en la arduino
# Nos permite llevar cosas mas complejas de programar a python
import socket
# Sirve para usar sockets, comunicaciones de red para enviar y recibir datos usando python
# Un ejemplo es crear un servidor que escucha conexiones enviadas por un cliente conectado a este
import inspect
# Permite mirar y analizar funciones mientras el programa esta corriendo, ver de donde viene una función, las lista
# de parametro que recibe o su codigo fuente. 
from datetime import datetime
# Nos permite saber fecha y hora actual y formatearla como texto

# --- Parche compatibilidad Python 3.11 ---
if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

# --- Conexión a Arduino ---
board = pyfirmata.Arduino('COM4')
print("Conectado a Arduino en COM6\n")

# --- Variables Globales ---
# Variables que se llenan paulatinamente para posteriormente calcular el promedio
t1 = t2 = t3 = t4 = t5 = 0
# Promedio de las anteriores variables
promedio = 0
# Variable de control: "a saber"
flag = 0
# Controla la finalización del programa
salir = False
# Intervalo de lectura inicial en segundos
n = 3.5
# Tendencia de como varía la temperatura, inicialmente nula al no tener información suficiente
tendencia = 'NULA'
print("Ciclo de lectura inicial n = 3.5s\n")

# Capturas
# Los vectores guardan los respectivos datos de cada captura en orden para su posterior uso
capturasTemperatura = []
capturasTendencia = []
capturasFecha = []
print("Listas de capturas inicializadas.\n")

# --- Pines ---
# Se asigna el valor de cada pin de la electronica
sensor_temp  = board.get_pin('a:0:i')
led_verde    = board.get_pin('d:10:o')
led_amarillo = board.get_pin('d:9:o')
led_rojo     = board.get_pin('d:8:o')
pulsador     = board.get_pin('d:5:i')
# Se indica en orden, el pin analogico, el numero de pin y si es entrada o salida
print("Pines configurados.\n")
# Los pines analógicos no se actualizan solos, requieren reporting

# --- Inicialización ---
# Creamos un hilo para que reciba y actualice continuamente los datos enviados por el Arduino
it = pyfirmata.util.Iterator(board)
it.start()
# Habilitamos el reporte continuo de los valores leídos
sensor_temp.enable_reporting() # El pin analogico necesita reporting para no devolver None
pulsador.enable_reporting() # El pulsador es digital pero enable_reporting mejora la actualización en tiempo real
print("Sensores habilitados.\n")

# La arduino todavía no envía el primer valor, el for intenta leer alguno para que no sea None
# Es un delay en todo caso de que no varía la entrada
for _ in range(10):
    if sensor_temp.read() is not None:
        break
    time.sleep(0.1)

print("Programa iniciado. Ctrl+C para salir.\n")

# --------------------------------------------------------------------
# ------------------------ BUCLE PRINCIPAL ---------------------------
# --------------------------------------------------------------------

# Se establece el estado inicial del boton como false
presionado = False
# Guardamos el momento en el que se comenzó a presionar el boton
inicio_pulso = 0
# Momento inicial en que arranca el programa
inicio = time.time()

# Inicio del bucle principal: abrimos un bloque que si hay mas adelante un error, el programa no queda colgado
try:
    # El bucle corre hasta que cambie el booleano salir
    while not salir:
        # Tomamos la ultima muestra analogica del sensor
        lectura = sensor_temp.read()
        # Leemos el ultimo valor de pulsador
        estado = pulsador.read()
        # Asignamos una variable que captura el timestamp actual en segundos
        ahora = time.time()

        # ===========================================================
        # ----------- CONTROL DEL BOTÓN DENTRO DEL BUCLE ------------
        # ===========================================================

        if estado is not None:
            estado = bool(estado)

            if estado and not presionado:
                presionado = True
                inicio_pulso = time.time()
                led_verde.write(1)
                led_amarillo.write(1)
                led_rojo.write(1)
                n = 0.05

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

        if lectura is not None and (ahora - inicio) >= n:

            temp_c = (lectura * lectura * lectura) - (25 * lectura) + 30  

            hora = datetime.now().strftime("%H:%M:%S")
            print(f"{hora} | Temperatura: {temp_c:.2f} °C")

            t5, t4, t3, t2, t1 = t4, t3, t2, t1, temp_c
            flag += 1

            if flag > 4 and not presionado:
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


        # ===========================================================
        # ------------------- TESTING (BOTÓN) -----------------------
        # ===========================================================

        if presionado:
            # Corre solo cuando se cumple el tiempo n
            if (ahora - inicio) >= n:
                inicio = ahora

                if flag > 4:
                    promedio = (t1 + t2 + t3 + t4 + t5) / 5
                    print(f"Temperatura promedio: {promedio:.2f} °C")

                    if temp_c < 0.965 * promedio:
                        tendencia = 'BAJA'
                        led_verde.write(1); led_amarillo.write(0); led_rojo.write(0)
                    elif temp_c > 1.035 * promedio:
                        tendencia = 'ALTA'
                        led_verde.write(0); led_amarillo.write(0); led_rojo.write(1)
                    else:
                        tendencia = 'MEDIA'
                        led_verde.write(0); led_amarillo.write(1); led_rojo.write(0)
                else:
                    tendencia = 'NULA'
                    led_verde.write(1); led_amarillo.write(1); led_rojo.write(1)

                # --- Parpadeo de 50 ms SOLO EN LA CAPTURA ---
                led_verde.write(1); led_amarillo.write(1); led_rojo.write(1)
                time.sleep(0.05)

                # Restaurar LED según tendencia
                if tendencia == 'BAJA':
                    led_verde.write(1); led_amarillo.write(0); led_rojo.write(0)
                elif tendencia == 'ALTA':
                    led_verde.write(0); led_amarillo.write(0); led_rojo.write(1)
                elif tendencia == 'MEDIA':
                    led_verde.write(0); led_amarillo.write(1); led_rojo.write(0)
                else:
                    led_verde.write(1); led_amarillo.write(1); led_rojo.write(1)

        if lectura is not None and (ahora - inicio) >= n:
            capturasTemperatura.append(temp_c)
            capturasTendencia.append(tendencia)
            capturasFecha.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            
            # Resteamos el temporizador del periodo de muestreo
            inicio = ahora
        time.sleep(0.05)

# Si se interrumpe por teclado entonces se sale del programa
except KeyboardInterrupt:
    print("Programa terminado por el usuario.")
# Finalmente imprimimos todos los datos en orden
finally:
    # Imprimimos primero las capturas
    print("\n=== Resumen de capturas ===")
    for i in range(len(capturasTemperatura)):
        print(f"Captura {i+1}: {capturasTemperatura[i]:.2f}°C, Tendencia: {capturasTendencia[i]}, Fecha: {capturasFecha[i]}")

    # Guardar capturas en un archivo para usar despues la parte 2
    with open("capturas.txt", "w", encoding="utf-8") as archivo:
        for i in range(len(capturasTemperatura)):
            archivo.write(f"Captura {i+1}: {capturasTemperatura[i]:.2f}°C, Tendencia: {capturasTendencia[i]}, Fecha: {capturasFecha[i]}\n")

    print("\nDatos guardados en 'capturas.txt'.")

    # Apagamos los leds
    led_verde.write(0)
    led_amarillo.write(0)
    led_rojo.write(0)
    board.exit()



