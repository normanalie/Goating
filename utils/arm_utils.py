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
    pass

def pick(namedPosition):
    pass

def drop(line, col):
    pass

def drop(namedPosition):
    pass
