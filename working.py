import os
import random
import time
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import font
import cv2
import wave
import numpy as np
import pyaudio
import requests
import webbrowser


class Wristband:
    def __init__(self, root):
        self.textbelt_api_url = "https://textbelt.com/text"
        self.textbelt_api_key = "text belt"  # You should use your actual Textbelt API key here
        self.root = root
        self.online_mode = True  # Start in online mode by default
        self.recordings_folder = "recordings"
        os.makedirs(self.recordings_folder, exist_ok=True)
        self.status_var = tk.StringVar()

        # Update the status display
        self.update_status()

        # Window Appearance
        self.root.title("Wristband - Emergency & Defense Mode")
        self.root.geometry("650x500")
        self.root.config(bg="#2C3E50")  # Set background color

        # Frame for content
        self.content_frame = tk.Frame(self.root, bg="#34495E", bd=10)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title label with style
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.title_label = tk.Label(self.content_frame, text="Wristband - Emergency & Defense Mode",
                                    font=title_font, bg="#34495E", fg="#ECF0F1")
        self.title_label.pack(pady=10)

        # Panic Button
        self.panic_button = tk.Button(self.content_frame, text="Panic Button", command=self.panic_button,
                                      width=20, height=2, font=("Arial", 12), bg="#E74C3C", fg="white",
                                      relief="raised", bd=4)
        self.panic_button.pack(pady=15)

        # Defense Button
        self.defense_button = tk.Button(self.content_frame, text="Defense Button", command=self.defense_button,
                                        width=20, height=2, font=("Arial", 12), bg="#2980B9", fg="white",
                                        relief="raised", bd=4)
        self.defense_button.pack(pady=15)

        # Toggle Online/Offline Button
        self.toggle_button = tk.Button(self.content_frame, text="Toggle Online/Offline Mode",
                                       command=self.toggle_mode, width=25, height=2, font=("Arial", 12),
                                       bg="#2ECC71", fg="white", relief="raised", bd=4)
        self.toggle_button.pack(pady=15)

        # Status Label
        self.status_label_frame = tk.Frame(self.content_frame, bg="#16A085", bd=2)
        self.status_label_frame.pack(pady=20, fill="both", padx=20)

        self.status_label = tk.Label(self.status_label_frame, textvariable=self.status_var, font=("Arial", 14),
                                     bg="#16A085", fg="white")
        self.status_label.pack(pady=5)

    def update_status(self):
        """Update the status display on the GUI."""
        mode = "Online" if self.online_mode else "Offline"
        self.status_var.set(f"Current Mode: {mode}")

    def toggle_mode(self):
        """Toggle between online and offline modes."""
        self.online_mode = not self.online_mode
        self.update_status()

    def panic_button(self):
        """Activate the Panic Button sequence."""
        print("\n--- Panic Button Activated ---")
        messagebox.showinfo("Panic Mode", "Panic Mode Activated! Details sent to contacts.")

        # Create alert.txt to store panic alert message
        alert_file_path = os.path.abspath('alert.txt')
        alert_message = "Panic button pressed! Immediate attention required."
        with open(alert_file_path, 'w') as alert_file:
            alert_file.write(alert_message)
        print(f"Alert saved to: {alert_file_path}")  # Debugging print to confirm file path

        # Log emergency details to emergencylog.txt
        emergency_log_path = os.path.abspath('emergency_log.txt')
        emergency_message = f"Emergency at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Panic button pressed. Location: {self.get_location()}"
        with open(emergency_log_path, 'a') as emergency_log_file:
            emergency_log_file.write(emergency_message + "\n")
        print(f"Emergency log saved to: {emergency_log_path}")  # Debugging print to confirm file path

        # Fetch location
        location = self.get_location()
        if location[0] is not None and location[1] is not None:
            location_text = f"Location: Latitude {location[0]:.6f}, Longitude {location[1]:.6f}"
            location_link = f"https://www.google.com/maps?q={location[0]},{location[1]}"
            # Open location in a separate thread
            threading.Thread(target=lambda: webbrowser.open(location_link)).start()

            # Save location in location.txt
            self.save_location_data(location)
        else:
            location_text = "Unable to fetch location."
            location_link = "N/A"

        # Update the status label with location
        self.status_var.set(f"Panic Mode Active!\n{location_text}\nGoogle Maps Link: {location_link}")

        # Schedule video recording after location
        self.root.after(5000, self.record_video_and_audio, location)

    def record_video_and_audio(self, location):
        """Record video and then audio."""
        video_file = self.record_video()
        audio_file = self.record_audio()
        # Send SMS with all details
        self.send_sms(location, video_file, audio_file)

    def defense_button(self):
        """Sequential defense actions."""
        print("\n--- Defense Mode Activated ---")
        messagebox.showinfo("Defense Mode", "Defense Mode Activated!")
        self.simulate_blinding_light()
        self.simulate_sprayable_gel()

    def get_location(self):
        """Fetch location based on the mode (Online or Offline)."""
        return self.get_location_online() if self.online_mode else self.get_location_offline()

    def get_location_online(self):
        """Fetch real-time location using IP-based geolocation (Online Mode)."""
        try:
            response = requests.get("http://ip-api.com/json/")  # Fetch location based on IP
            data = response.json()
            if data['status'] == 'fail':
                print("Error fetching location")
                return None, None
            return data['lat'], data['lon']
        except requests.exceptions.RequestException:
            print("Failed to fetch real-time location.")
            return None, None

    def get_location_offline(self):
        """Simulate GPS coordinates (Offline Mode)."""
        return round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6)

    def save_location_data(self, location):
        """Save location data to location.txt"""
        with open('location.txt', 'w') as location_file:
            location_file.write(f"Latitude: {location[0]:.6f}, Longitude: {location[1]:.6f}")
        print(f"Location saved to: location.txt")

    def record_video(self):
        """Record video using the webcam."""
        print("Recording video...")
        video_file = os.path.join(self.recordings_folder, f"video_{time.strftime('%Y%m%d_%H%M%S')}.avi")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Webcam not accessible.")
            return "Error: No video recorded."

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_file, fourcc, 20.0, (640, 480))

        start_time = time.time()
        while time.time() - start_time < 5:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                cv2.imshow("Recording...", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        return video_file

    def record_audio(self):
        """Record audio using pyaudio."""
        print("Recording audio...")
        audio_file = os.path.join(self.recordings_folder, f"audio_{time.strftime('%Y%m%d_%H%M%S')}.wav")
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100
        record_seconds = 5

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        frames = [stream.read(chunk) for _ in range(int(rate / chunk * record_seconds))]
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        return audio_file

    def send_sms(self, location, video_file, audio_file):
        """Simulate sending SMS with emergency details."""
        location_link = f"https://www.google.com/maps?q={location[0]},{location[1]}"
        message = f"Emergency! Location: {location_link}. Video: {video_file}, Audio: {audio_file}."
        print(f"Sending SMS: {message}")

        # List of emergency contacts (Phone numbers)
        emergency_contacts = ["+917869603799"]  # Replace with actual phone numbers

        for contact in emergency_contacts:
            try:
                # Send SMS using Textbelt API
                response = requests.post(self.textbelt_api_url, {
                    'phone': contact,
                    'message': message,
                    'key': self.textbelt_api_key
                })
                response_data = response.json()
                if response_data['success']:
                    print(f"SMS sent to {contact}")
                else:
                    print(f"Failed to send SMS to {contact}: {response_data['error']}")
            except Exception as e:
                print(f"Error sending SMS to {contact}: {str(e)}")

    def simulate_blinding_light(self):
        """Simulate blinding light with OpenCV."""
        height, width = 500, 500
        for i in range(0, 255, 5):
            frame = np.ones((height, width, 3), dtype="uint8") * i
            cv2.imshow("Blinding Light", frame)
            cv2.waitKey(50)
        cv2.destroyAllWindows()

    def simulate_sprayable_gel(self):
        """Simulate sprayable gel with OpenCV."""
        height, width = 500, 500
        for _ in range(10):
            frame = np.zeros((height, width, 3), dtype="uint8")
            for _ in range(300):
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(0, width), random.randint(0, height)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.imshow("Sprayable Gel", frame)
            cv2.waitKey(100)
        cv2.destroyAllWindows()


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    wristband_app = Wristband(root)
    root.mainloop()
