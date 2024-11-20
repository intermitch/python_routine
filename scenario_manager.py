import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class JsonManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Manager")

        # Variables
        self.title_var = tk.StringVar()
        self.start_hour_var = tk.StringVar()
        self.end_hour_var = tk.StringVar()
        self.events = []

        # Layout
        tk.Label(root, text="Title:").grid(row=0, column=0, sticky="e")
        tk.Entry(root, textvariable=self.title_var).grid(row=0, column=1, columnspan=2, sticky="we")

        tk.Label(root, text="Start Hour:").grid(row=1, column=0, sticky="e")
        tk.Entry(root, textvariable=self.start_hour_var).grid(row=1, column=1, sticky="we")

        tk.Label(root, text="End Hour:").grid(row=1, column=2, sticky="e")
        tk.Entry(root, textvariable=self.end_hour_var).grid(row=1, column=3, sticky="we")

        # Events list
        self.events_frame = ttk.Frame(root)
        self.events_frame.grid(row=2, column=0, columnspan=4, sticky="we")
        self.events_listbox = tk.Listbox(self.events_frame, height=10)
        self.events_listbox.pack(side="left", fill="both", expand=True)
        self.events_listbox.bind("<<ListboxSelect>>", self.load_event_details)
        self.events_scrollbar = ttk.Scrollbar(self.events_frame, orient="vertical", command=self.events_listbox.yview)
        self.events_scrollbar.pack(side="right", fill="y")
        self.events_listbox.config(yscrollcommand=self.events_scrollbar.set)

        # Event details
        tk.Label(root, text="Event Time:").grid(row=3, column=0, sticky="e")
        self.event_time_var = tk.StringVar()
        tk.Entry(root, textvariable=self.event_time_var).grid(row=3, column=1, sticky="we")

        tk.Label(root, text="Event Icon:").grid(row=3, column=2, sticky="e")
        self.event_icon_var = tk.StringVar()
        tk.Entry(root, textvariable=self.event_icon_var).grid(row=3, column=3, sticky="we")

        # Buttons
        ttk.Button(root, text="Add Event", command=self.add_event).grid(row=4, column=0)
        ttk.Button(root, text="Update Event", command=self.update_event).grid(row=4, column=1)
        ttk.Button(root, text="Delete Event", command=self.delete_event).grid(row=4, column=2)

        # File operations
        ttk.Button(root, text="Load JSON", command=self.load_json).grid(row=5, column=0)
        ttk.Button(root, text="Save JSON", command=self.save_json).grid(row=5, column=1)
        ttk.Button(root, text="New JSON", command=self.new_json).grid(row=5, column=2)

    def new_json(self):
        self.title_var.set("")
        self.start_hour_var.set("")
        self.end_hour_var.set("")
        self.events = []
        self.refresh_events_list()

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.title_var.set(data.get("title", ""))
                    self.start_hour_var.set(data.get("start_hour", ""))
                    self.end_hour_var.set(data.get("end_hour", ""))
                    self.events = data.get("events", [])
                    self.refresh_events_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON file: {e}")

    def save_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            data = {
                "title": self.title_var.get(),
                "start_hour": self.start_hour_var.get(),
                "end_hour": self.end_hour_var.get(),
                "events": self.events
            }
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                    messagebox.showinfo("Success", "JSON file saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save JSON file: {e}")

    def add_event(self):
        event = {
            "time": self.event_time_var.get(),
            "icon": self.event_icon_var.get()
        }
        self.events.append(event)
        self.refresh_events_list()

    def update_event(self):
        selected_index = self.events_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.events[index] = {
                "time": self.event_time_var.get(),
                "icon": self.event_icon_var.get()
            }
            self.refresh_events_list()

    def delete_event(self):
        selected_index = self.events_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            del self.events[index]
            self.refresh_events_list()

    def load_event_details(self, event):
        selected_index = self.events_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            event = self.events[index]
            self.event_time_var.set(event["time"])
            self.event_icon_var.set(event["icon"])

    def refresh_events_list(self):
        self.events_listbox.delete(0, tk.END)
        for event in self.events:
            self.events_listbox.insert(tk.END, f"{event['time']} - {event['icon']}")

# Main
root = tk.Tk()
app = JsonManagerApp(root)
root.mainloop()
