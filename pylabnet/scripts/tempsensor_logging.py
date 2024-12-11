import serial
import json
import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time as time

# Pfad für den Ordner und die JSON-Datei
order_path = r"C://GithubSync"
json_file_path = os.path.join(order_path, 'sensordata.json')

# Überprüfen und erstellen des Ordners, falls nicht vorhanden
if not os.path.exists(order_path):
    os.makedirs(order_path)
    print(f"Der Ordner {order_path} wurde erstellt.")

# Überprüfen und erstellen der JSON-Datei, falls nicht vorhanden
if not os.path.isfile(json_file_path):
    with open(json_file_path, 'w') as json_file:
        json.dump([], json_file)  # Initialisieren mit einem leeren JSON-Array
    print(f"Die JSON-Datei {json_file_path} wurde erstellt.")
else:
    print(f"Die JSON-Datei {json_file_path} existiert bereits.")

ser = serial.Serial('COM7', 9600)  # Passen Sie 'COM7' bei Bedarf an


def calculate_resistance(analog_value):
    V = 3.3 * analog_value / 4096
    R = V * 10000 / (3.3 - V)
    return R


def read_and_save_data(ser):
    data_list = []
    while True:
        print("Warte auf Daten...")
        try:
            time.sleep(0.1)
            line = ser.readline().decode('utf-8').strip()
            print(line)
            if line:
                values = line.split(';')
                if len(values) == 4:
                    A0 = float(values[0])
                    A1 = float(values[1])
                    A2 = float(values[2])
                    A11 = float(values[3])

                    # Berechnung der Widerstände
                    R0 = calculate_resistance(A0)
                    R1 = calculate_resistance(A1)
                    R2 = calculate_resistance(A2)
                    R11 = calculate_resistance(A11)

                    data = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'A0': A0,
                        'A1': A1,
                        'A2': A2,
                        'A11': A11,
                        'R0': R0,
                        'R1': R1,
                        'R2': R2,
                        'R11': R11
                    }

                    # Speichern der Daten in JSON
                    with open(json_file_path, 'a') as json_file:  # 'a' für Anhängen
                        json.dump(data, json_file)
                        json_file.write('\n')

                    # Daten zu data_list hinzufügen
                    data_list.append(data)
                    yield data  # Für Animation-Update zurückgeben
        except KeyboardInterrupt:
            print("Programm beendet")
            break
        except Exception as e:
            print(f"Fehler: {e}")
            continue


# Setup für live Plotting
fig, ax = plt.subplots(2, 2, figsize=(10, 8))
plots = {
    'R0': [],
    'R1': [],
    'R2': [],
    'R11': [],
    'time': []
}


def update(data):
    timestamp = data['timestamp']
    plots['R0'].append(data['R0'])
    plots['R1'].append(data['R1'])
    plots['R2'].append(data['R2'])
    plots['R11'].append(data['R11'])
    plots['time'].append(datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f'))

    ax[0, 0].clear()
    ax[0, 0].plot(plots['time'][1:-1], plots['R0'][1:-1])
    ax[0, 0].set_title('R0')

    ax[0, 1].clear()
    ax[0, 1].plot(plots['time'][1:-1], plots['R1'][1:-1])
    ax[0, 1].set_title('R1')

    ax[1, 0].clear()
    ax[1, 0].plot(plots['time'][1:-1], plots['R2'][1:-1])
    ax[1, 0].set_title('R2')

    ax[1, 1].clear()
    ax[1, 1].plot(plots['time'][1:-1], plots['R11'][1:-1])
    ax[1, 1].set_title('R11')

    # Für better formatting (gilt für alle Plots)
    for axis in ax.flatten():
        axis.set_xlabel('Zeit')
        axis.set_ylabel('Widerstand (Ohm)')
        axis.tick_params(axis='x', rotation=45)
        axis.grid()


if __name__ == '__main__':
    print("Programm gestartet")

    # Start der seriellen Lesefunktion und Live-Update
    ani = animation.FuncAnimation(fig, update, read_and_save_data(ser), blit=False, interval=600)
    plt.tight_layout()
    plt.show()
