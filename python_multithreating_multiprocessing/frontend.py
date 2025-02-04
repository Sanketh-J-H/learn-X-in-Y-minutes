import tkinter as tk
from tkinter import ttk
from multiprocessing import Process, Queue
import time
from user_interface_for_Rectifier import start_client

class PowerModuleDisplay:
    def __init__(self, queue):
        self.queue = queue  # Queue to receive live data
        self.soc_value = None
        self.soh_value = None
        self.temp_values = [None] * 6
        self.current_values = [None] * 6
        self.voltage_values = [None] * 6

        # Create main application window
        self.root = tk.Tk()
        self.root.title("Power Module Display")
        self.root.geometry("800x400")

        # Configure grid layout for the main window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create the main layout
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Create SOC and SOH section
        self.create_info_frame()

        # Create Power Modules section
        self.power_modules = []  # To store label references
        self.create_modules_frame()

        # Schedule periodic updates to fetch data from the queue
        self.root.after(500, self.update_data_from_queue)  # 500ms interval

    def create_info_frame(self):
        self.info_frame = ttk.Frame(self.main_frame, padding=10)
        self.info_frame.grid(row=0, column=0, sticky="ew")
        self.info_frame.columnconfigure(0, weight=1)

        self.soc_label = ttk.Label(self.info_frame, text="SOC: NA%", 
                                   font=("Arial", 12, "bold"), anchor="w")
        self.soc_label.pack(side="left", padx=10)

        self.soh_label = ttk.Label(self.info_frame, text="SOH: NA", 
                                   font=("Arial", 12, "bold"), anchor="w")
        self.soh_label.pack(side="left", padx=10)

    def create_modules_frame(self):
        self.modules_frame = ttk.Frame(self.main_frame, padding=10)
        self.modules_frame.grid(row=1, column=0, sticky="nsew")
        self.modules_frame.columnconfigure((0, 1, 2), weight=1)
        self.modules_frame.rowconfigure((0, 1), weight=1)

        for i in range(1, 7):
            self.power_modules.append(self.create_power_module(self.modules_frame, i))

    def create_power_module(self, parent, module_number):
        frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=10)
        frame.grid(row=(module_number - 1) // 3, column=(module_number - 1) % 3, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame, text=f"Power Module {module_number}", font=("Arial", 10, "bold"), anchor="center").pack(pady=5)

        temp_label = self.create_label(frame, "Temp: NA °C")
        current_label = self.create_label(frame, "Current: NA A")
        voltage_label = self.create_label(frame, "Voltage: NA V")

        return temp_label, current_label, voltage_label

    @staticmethod
    def create_label(frame, text):
        label = ttk.Label(frame, text=text, anchor="w")
        label.pack(fill="x", padx=5, pady=2)
        return label

    def update_data_from_queue(self):
        try:
            # Check if there's data in the queue
            while not self.queue.empty():
                data = self.queue.get_nowait()

                # Update SOC and SOH
                self.soc_value, self.soh_value = data["soc"], data["soh"]
                formatted_soc = f"SOC: {self.soc_value:.2f} %" if self.soc_value is not None else 'NA'
                self.soc_label.config(text=formatted_soc)
                self.soh_label.config(text=f"SOH: {self.soh_value if self.soh_value is not None else 'NA'}")

                # Update Power Module data
                self.temp_values = data["temp"]
                self.current_values = data["current"]
                self.voltage_values = data["voltage"]

                for i, (temp, current, voltage) in enumerate(zip(self.temp_values, self.current_values, self.voltage_values)):
                    formatted_temp = f"Temp: {temp:.2f} °C" if temp is not None else "Temp: NA"
                    self.power_modules[i][0].config(text=formatted_temp)
                    formatted_current = f"Current: {current:.2f} A" if current is not None else "Current: NA"
                    self.power_modules[i][1].config(text=formatted_current)
                    formatted_voltage = f"Voltage: {voltage:.2f} V" if voltage is not None else "Voltage: NA"
                    self.power_modules[i][2].config(text=formatted_voltage)
        except Exception as e:
            print(f"Error updating data: {e}")

        # Schedule the next update
        self.root.after(100, self.update_data_from_queue)

    def run(self):
        # Start the Tkinter event loop
        self.root.mainloop()


# Simulate live data updates from another process
def data_provider(queue):
    temp_values = [30, 32, None, 28, 31, 29]
    current_values = [5.1, 4.8, None, 5.5, 4.9, 5.0]
    voltage_values = [3.7, 3.8, None, 3.9, 3.6, 3.7]
    soc = 99

    while True:
        # Simulate new data being sent to the queue
        new_data = {
            "soc": soc,
            "soh": "Good",
            "temp": temp_values,
            "current": current_values,
            "voltage": voltage_values
        }
        queue.put(new_data)

        # Update data randomly for simulation
        time.sleep(0.5)
        temp_values = [t + 0.1 if t else None for t in temp_values]
        current_values = [c + 0.1 if c else None for c in current_values]
        voltage_values = [v + 0.1 if v else None for v in voltage_values]
        if soc < 100:
            soc += 0.1
        else:
            soc = 0


# Main execution
if __name__ == "__main__":
    queue = Queue()

    # Start the data provider process
    data_process = Process(target=data_provider, args=(queue,))
    # data_process = Process(target=start_client, args=(queue,))
    data_process.start()

    # Start the GUI application
    app = PowerModuleDisplay(queue)
    app.run()

    # Terminate the data provider process when the GUI exits
    data_process.terminate()
