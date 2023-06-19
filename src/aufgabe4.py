from db import Database
import datetime
import psutil
import matplotlib.pyplot as plt
import threading

connectionString = "mongodb+srv://lucibluc:luci69@cluster0.rtex13l.mongodb.net/?retryWrites=true&w=majority"
db = Database(connectionString)
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
        col.insert_one(self.__dict__)
        if col.count_documents({}) > 10000:
            oldest_logs = col.find().sort('timestamp', 1).limit(col.count_documents({}) - 10000)
            col.delete_many({'_id': {'$in': [log['_id'] for log in oldest_logs]}})

    def plt(self):
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
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        ram_total = mem.total
        ram_used = mem.used

        power = Power(cpu_percent, ram_total, ram_used)
        power.save_to_database()

        print("CPU Usage: {}%".format(power.cpu))
        print("RAM Total: {} MB".format(power.ram_total))
        print("RAM Used: {} MB".format(power.ram_used))
        print("Timestamp: {}".format(power.timestamp))
        print("---------------------------------")

        power = Power(None, None, None)
        power.plt()


power_stats()
