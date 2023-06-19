from db import Database
import datetime
import psutil
import matplotlib.pyplot as plt
import threading
import os


# Verbindung zur Datenbank herstellen
connection_string = os.environ.get("CONNECTION_STRING")
db = Database(connection_string)
# Eine Sammlung ("Collection") in der Datenbank abrufen
col = db.get_collection("Power", "check")

class Power:
    def __init__(self, cpu, ram_total, ram_used, timestamp=None):
        self.cpu = cpu
        self.ram_total = ram_total
        self.ram_used = ram_used
        if timestamp is None:
            self.timestamp = datetime.datetime.now()
        else:
            self.timestamp = timestamp

    def save_to_database(self):
        # Speichert die Power-Daten in der Datenbank.
        # Löscht älteste Datensätze, falls die Anzahl der Dokumente in der Datenbank größer als 10000 ist.
        col.insert_one(self.__dict__)
        if col.count_documents({}) > 10000:
            oldest_logs = col.find().sort('timestamp', 1).limit(col.count_documents({}) - 10000)
            col.delete_many({'_id': {'$in': [log['_id'] for log in oldest_logs]}})

    def plt(self):
        # Zeigt ein Diagramm mit den CPU- und RAM-Daten der letzten 10000 Datensätze an.
        logs = col.find().sort('timestamp', 1).limit(10000)
        cpu_values = []
        ram_values = []
        timestamps = []

        for log in logs:
            cpu_values.append(log['cpu'])
            ram_values.append(log['ram_used'])
            timestamps.append(log['timestamp'])

        plt.plot(timestamps, cpu_values, color='red', label='CPU Usage in %')
        plt.plot(timestamps, ram_values, color='blue', label='RAM Usage in MB')
        plt.xlabel('Time')
        plt.ylabel('Usage')
        plt.legend()
        threading.Timer(1.0, plt.close).start()
        plt.show()

def power_stats():
    # Ruft kontinuierlich die CPU- und RAM-Daten ab, speichert sie in der Datenbank und gibt sie aus.
    # Zeigt auch das Diagramm der Daten an.
    while True:
        # CPU- und RAM-Daten abrufen
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        ram_total = mem.total
        ram_used = mem.used

        # Power-Objekt erstellen und in der Datenbank speichern
        power = Power(cpu_percent, ram_total, ram_used)
        power.save_to_database()

        # Daten ausgeben
        print("CPU Usage: {}%".format(power.cpu))
        print("RAM Total: {} MB".format(power.ram_total))
        print("RAM Used: {} MB".format(power.ram_used))
        print("Timestamp: {}".format(power.timestamp))
        print("---------------------------------")

        # Daten mit der App ausgeben
        power = Power(None, None, None)
        power.plt()


power_stats()
