
import serial
import time

# Ersetze 'COM3' durch den tatsächlichen Port, an den das Arduino angeschlossen ist
# Auf Linux- und Mac-Systemen könnte es etwas wie '/dev/ttyUSB0' oder '/dev/ttyACM0' sein
arduino_port = 'COM9'
baud_rate = 9600

# Initialisiere die serielle Verbindung
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Warte kurz, bis die serielle Verbindung etabliert ist

try:
    while True:
        # Signal an das Arduino senden
        command = input("Geben Sie '1' ein, um Pin einzuschalten; '0', um auszuschalten: ")
        if command in ['0', '1']:
            ser.write(command.encode())
        else:
            print("Ungültige Eingabe. Bitte geben Sie '1' oder '0' ein.")
except KeyboardInterrupt:
    print("Programm beendet.")

# Schließe die serielle Verbindung
ser.close()
