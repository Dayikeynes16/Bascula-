import serial
import time

def leer_bascula():
    puerto = '/dev/ttyUSB0'  # Asegúrate de cambiar esto por el puerto correcto
    baudios = 9600  # Ajusta la tasa de baudios según sea necesario

    try:
        with serial.Serial(puerto, baudios, timeout=1) as ser:
            print("Conexión establecida con la báscula.")
            ser.write(b'P')  # Envía un comando a la báscula, ajusta según sea necesario
            time.sleep(1)  # Espera a que la báscula responda

            if ser.in_waiting:
                data = ser.readline().decode('utf-8').rstrip()
                return data
            else:
                return "No se recibió respuesta de la báscula."
    except serial.SerialException as e:
        return f"Error al abrir el puerto serial: {e}"

# Llamar a la función y mostrar el resultado
peso = leer_bascula()
print(f"Peso leído: {peso}")

