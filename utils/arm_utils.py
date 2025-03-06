import serial

def check_serial_connection():
    print("[SERIAL] Checking...")
    try:
        ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
        ser.write(b'PING')  # Envoi du signal de test au Pico
        response = ser.readline().decode('utf-8').strip()
        ser.close()
        return response == "PONG"  # Vérifie si le Pico répond avec "PONG"
    except serial.SerialException:
        return False

def pick(line, col):
    # Code pour communiquer avec le Doosan ici. Utiliser le module ROS de python
    pass

def pick(namedPosition):
    # Code pour communiquer avec le Doosan ici. Utiliser le module ROS de python
    pass

def drop(line, col):
    # Code pour communiquer avec le Doosan ici. Utiliser le module ROS de python
    pass

def drop(namedPosition):
    # Code pour communiquer avec le Doosan ici. Utiliser le module ROS de python
    pass
