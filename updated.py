import os
import sys
import ttkbootstrap as ttk
from PIL._tkinter_finder import tk
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QLabel, QPushButton, QApplication
from ttkbootstrap.constants import *
from tkinter import messagebox, Listbox
from datetime import datetime
import time
import psutil
from geopy.geocoders import Nominatim  # Import geopy for location tracking


class WristbandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wristband Application")
        self.root.geometry("800x500")  # Initial window size
        self.root.state("zoomed")  # Full-screen

        self.recordings_folder = "recordings"
        self.emergency_logs = os.path.join(self.recordings_folder, "emergency_log.txt")

        os.makedirs(self.recordings_folder, exist_ok=True)

        self.current_user = None
        self.users_data = {}  # Store user data for easy access

        self.flash_screen()

    def flash_screen(self):
        flash_frame = ttk.Frame(self.root, padding=20, bootstyle="dark")
        flash_frame.pack(fill="both", expand=True)

        # Display welcome message
        ttk.Label(flash_frame, text="Welcome to Wristband App", font=("Helvetica", 24, "bold"), bootstyle="inverse") \
            .pack(pady=20)

        self.root.update()
        time.sleep(2)

        flash_frame.destroy()
        self.show_auth_interface()

    def show_auth_interface(self):
        # Clear any existing content
        for widget in self.root.winfo_children():
            widget.destroy()

        # Add a rectangular frame in the center
        self.auth_frame = ttk.Frame(self.root, padding=40, bootstyle="info")  # Outer frame
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=500)  # Central rectangle

        # Add title
        ttk.Label(self.auth_frame, text="Wristband App", font=("Helvetica", 32, "bold")) \
            .pack(pady=40)

        # Add buttons
        ttk.Button(self.auth_frame, text="Sign Up", bootstyle="success", command=self.show_signup_frame).pack(pady=30)
        ttk.Button(self.auth_frame, text="Login", bootstyle="primary", command=self.show_login_frame).pack(pady=30)

    def show_signup_frame(self):
        # Destroy auth_frame and show signup frame
        self.auth_frame.destroy()
        self.signup_frame = self.create_signup_frame()
        self.signup_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        # Destroy auth_frame and show login frame
        self.auth_frame.destroy()
        self.login_frame = self.create_login_frame()
        self.login_frame.pack(fill="both", expand=True)

    def create_signup_frame(self):
        outer_frame = ttk.Frame(self.root, padding=20, bootstyle="info")
        outer_frame.place(relx=0.5, rely=0.5, anchor="center")

        inner_frame = ttk.Frame(outer_frame, padding=20, bootstyle="secondary")
        inner_frame.pack()

        ttk.Label(inner_frame, text="Sign Up", font=("Helvetica", 18, "bold")) \
            .pack(pady=20)

        ttk.Label(inner_frame, text="Name:").pack(anchor="w", padx=20, pady=5)
        self.signup_name_entry = ttk.Entry(inner_frame, width=30)
        self.signup_name_entry.pack(padx=20, pady=5)

        ttk.Label(inner_frame, text="Gender:").pack(anchor="w", padx=20, pady=5)
        self.signup_gender_var = ttk.StringVar(value="Select")
        ttk.Combobox(inner_frame, textvariable=self.signup_gender_var, values=["Male", "Female", "Other"], width=28,
                     bootstyle="primary") \
            .pack(padx=20, pady=5)

        ttk.Label(inner_frame, text="Date of Birth (YYYY-MM-DD):").pack(anchor="w", padx=20, pady=5)
        self.signup_dob_entry = ttk.Entry(inner_frame, width=30)
        self.signup_dob_entry.pack(padx=20, pady=5)

        ttk.Label(inner_frame, text="Password:").pack(anchor="w", padx=20, pady=5)
        self.signup_password_entry = ttk.Entry(inner_frame, width=30, show="*")
        self.signup_password_entry.pack(padx=20, pady=5)

        ttk.Button(inner_frame, text="Sign Up", bootstyle="success", command=self.submit_signup).pack(pady=20)
        ttk.Button(inner_frame, text="Back", bootstyle="secondary", command=self.back_to_auth).pack(pady=5)

        return outer_frame

    def create_login_frame(self):
        outer_frame = ttk.Frame(self.root, padding=20, bootstyle="info")
        outer_frame.place(relx=0.5, rely=0.5, anchor="center")

        inner_frame = ttk.Frame(outer_frame, padding=20, bootstyle="secondary")
        inner_frame.pack()

        ttk.Label(inner_frame, text="Login", font=("Helvetica", 18, "bold")) \
            .pack(pady=20)

        ttk.Label(inner_frame, text="Name:").pack(anchor="w", padx=20, pady=5)
        self.login_name_entry = ttk.Entry(inner_frame, width=30)
        self.login_name_entry.pack(padx=20, pady=5)

        ttk.Label(inner_frame, text="Password:").pack(anchor="w", padx=20, pady=5)
        self.login_password_entry = ttk.Entry(inner_frame, width=30, show="*")
        self.login_password_entry.pack(padx=20, pady=5)

        ttk.Button(inner_frame, text="Login", bootstyle="success", command=self.submit_login).pack(pady=20)
        ttk.Button(inner_frame, text="Back", bootstyle="secondary", command=self.back_to_auth).pack(pady=5)

        return outer_frame

    def back_to_auth(self):
        if hasattr(self, 'signup_frame'):
            self.signup_frame.destroy()
        if hasattr(self, 'login_frame'):
            self.login_frame.destroy()

        self.show_auth_interface()

    def submit_signup(self):
        name = self.signup_name_entry.get().strip()
        gender = self.signup_gender_var.get()
        dob = self.signup_dob_entry.get().strip()
        password = self.signup_password_entry.get().strip()

        if not name or gender == "Select" or not dob or not password:
            messagebox.showerror("Error", "Please fill out all fields correctly.")
            return

        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date of Birth must be in YYYY-MM-DD format.")
            return

        # Store user details in a dictionary
        self.users_data[name] = {"dob": dob, "gender": gender, "password": password}

        messagebox.showinfo("Success", "Sign up completed successfully! Please log in.")
        self.signup_frame.destroy()
        self.show_auth_interface()

    def submit_login(self):
        name = self.login_name_entry.get().strip()
        password = self.login_password_entry.get().strip()

        # Validate credentials
        if name in self.users_data and self.users_data[name]["password"] == password:
            self.current_user = name
            messagebox.showinfo("Success", "Login successful!")
            self.login_frame.destroy()
            self.show_features_frame()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    def show_features_frame(self):
        self.features_frame = ttk.Frame(self.root, padding=20, bootstyle="dark")
        self.features_frame.pack(fill="both", expand=True)

        # Sidebar menu
        sidebar = ttk.Frame(self.features_frame, width=200, padding=10, bootstyle="secondary")
        sidebar.pack(side="left", fill="y")

        ttk.Label(sidebar, text=f"Welcome, {self.current_user}", font=("Helvetica", 14, "bold"), anchor="center") \
            .pack(pady=10)

        ttk.Button(sidebar, text="My Profile", command=self.show_profile, bootstyle="light").pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Add Device", command=self.show_add_device, bootstyle="light").pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Features", command=self.show_main_features, bootstyle="light").pack(fill="x", pady=5)

        # Main features frame
        self.main_features_frame = self.create_main_features_frame()
        self.main_features_frame.pack(fill="both", expand=True)

    def show_profile(self):
        user_data = self.users_data.get(self.current_user)
        if user_data:
            self.features_frame.pack_forget()  # Hide main features frame
            profile_frame = ttk.Frame(self.root, padding=20, bootstyle="dark")
            profile_frame.pack(fill="both", expand=True)

            ttk.Label(profile_frame, text="My Profile", font=("Helvetica", 24, "bold"), bootstyle="inverse") \
                .pack(pady=20)

            ttk.Label(profile_frame, text=f"Name: {self.current_user}", font=("Helvetica", 18)) \
                .pack(pady=10)
            ttk.Label(profile_frame, text=f"Gender: {user_data['gender']}", font=("Helvetica", 18)) \
                .pack(pady=10)
            ttk.Label(profile_frame, text=f"Date of Birth: {user_data['dob']}", font=("Helvetica", 18)) \
                .pack(pady=10)

            ttk.Button(profile_frame, text="Back", bootstyle="secondary", command=self.show_features_frame).pack(
                pady=20)

    def show_add_device(self):
        options = ["Enable Wi-Fi", "Enable Bluetooth", "Offline Mode"]
        self.add_device_window = ttk.Toplevel(self.root)
        self.add_device_window.title("Add Device")
        self.add_device_window.geometry("300x200")

        ttk.Label(self.add_device_window, text="Select Device Mode").pack(pady=10)

        self.device_mode_var = ttk.StringVar(value="Enable Wi-Fi")

        device_mode_combobox = ttk.Combobox(self.add_device_window, textvariable=self.device_mode_var,
                                            values=options, width=28)
        device_mode_combobox.pack(padx=20, pady=20)

        ttk.Button(self.add_device_window, text="Save", bootstyle="success", command=self.save_device_mode).pack(
            pady=10)

    def save_device_mode(self):
        selected_mode = self.device_mode_var.get()
        messagebox.showinfo("Device Mode", f"Selected Mode: {selected_mode}")
        self.add_device_window.destroy()

    def show_main_features(self):
        if hasattr(self, 'main_features_frame'):
            self.main_features_frame.pack_forget()
        self.main_features_frame = self.create_main_features_frame()
        self.main_features_frame.pack(fill="both", expand=True)

    def create_main_features_frame(self):
        frame = ttk.Frame(self.features_frame, padding=20, bootstyle="dark")

        ttk.Label(frame, text="Wristband Features", font=("Helvetica", 18, "bold"), bootstyle="inverse") \
            .pack(pady=20)

        button_frame = ttk.Frame(frame, padding=10, bootstyle="dark")
        button_frame.pack(fill="both", expand=True)

        features = [
            ("View Recordings", self.view_recordings, "📁"),
            ("Alerts", self.view_logs, "⚠️"),
            ("Customer Service", self.customer_service, "📞"),
            ("Emergency Logs", self.alerts, "📜"),
            ("Battery Status", self.check_battery, "🔋"),
            ("Location Records", self.location_records, "📍"),
        ]

        rows = 2
        columns = 3
        for i, (feature, command, icon) in enumerate(features):
            row = i // columns
            col = i % columns
            button = ttk.Button(
                button_frame,
                text=f"{icon}\n{feature}",
                bootstyle="info-outline",
                command=command,
                width=15,
                padding=10
            )
            button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        for i in range(rows):
            button_frame.rowconfigure(i, weight=1)
        for j in range(columns):
            button_frame.columnconfigure(j, weight=1)

        return frame

    def view_recordings(self):
        if os.path.exists(self.recordings_folder):
            os.startfile(self.recordings_folder)
        else:
            messagebox.showinfo("Recordings", "No recordings found.")

    def view_logs(self):
        location_file = "emergency_log.txt"  # Path to the location file
        if os.path.exists(self.emergency_logs):
            with open(self.emergency_logs, "r") as log_file:
                logs = log_file.read().strip()
            if logs:
                messagebox.showinfo("Emergency Logs", logs)
            else:
                messagebox.showinfo("Emergency Logs", "The file exists but contains no logs.")

    def customer_service(self):
        messagebox.showinfo("Customer Service", "Contact: support@wristbandapp.com")

    def alerts(self):
        emergency_contacts = {
            "Police": "+1-123-456-7890",
            "Fire Department": "+1-987-654-3210",
            "Ambulance": "+1-555-666-7777",
            "Support Line": "+1-800-123-4567",
        }

        contact_info = "\n".join(f"{name}: {number}" for name, number in emergency_contacts.items())
        messagebox.showinfo("Emergency Logs", f"No alerts at the moment.\n\nEmergency Contacts:\n{contact_info}")

    def check_battery(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "Charging" if battery.power_plugged else "Discharging"
                messagebox.showinfo(
                    "Battery Status",
                    f"Battery remaining: {battery.percent}%\nStatus: {status}"
                )
            else:
                messagebox.showerror("Battery Status", "Battery status is not available.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def location_records(self):
        location_file = "location.txt"  # Path to the location file
        if os.path.exists(location_file):  # Check if the file exists
            with open(location_file, "r") as file:  # Open the file in read mode
                location_data = file.read()  # Read the content of the file
            if location_data:
                messagebox.showinfo("Location Records", location_data)  # Show the contents in a messagebox
            else:
                messagebox.showinfo("Location Records", "No location data available.")
        else:
            messagebox.showinfo("Location Records", "Location file not found.")

    def update_location(self):
        # Fetch the current location (this can be fetched via GPS or some API, for now, it's a placeholder)
        # For now, using a placeholder value, replace with actual location-fetching logic
        current_location = "Latitude: 40.7128, Longitude: -74.0060"  # Example: New York City coordinates

        # Get the current time to associate with the location record
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format the entry to be written in location.txt
        location_entry = f"{current_time} - {current_location}\n"

        # Write or append the location data to the location.txt file
        with open("location.txt", "a") as location_file:
            location_file.write(location_entry)

        messagebox.showinfo("Location Update", f"Location updated: {current_location}")


if __name__ == "__main__":
    app = ttk.Window(themename="superhero")  # Choose a colorful theme
    WristbandApp(app)
    app.mainloop()