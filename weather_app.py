import tkinter as tk
from tkinter import messagebox
import requests

# To get your own API Key: 
# 1. Sign up at https://openweathermap.org/
# 2. Go to the "API keys" tab in your profile.
# 3. Copy your key and replace "YOUR_API_KEY_HERE" below.
API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Weather App")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.setup_ui()

    def setup_ui(self):
        # Header
        title_label = tk.Label(self.root, text="Weather App", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=20)

        # Input field
        self.city_entry = tk.Entry(self.root, font=("Arial", 14), width=25, justify='center')
        self.city_entry.insert(0, "Enter City Name")
        self.city_entry.bind("<FocusIn>", lambda e: self.city_entry.delete(0, tk.END) if self.city_entry.get() == "Enter City Name" else None)
        self.city_entry.pack(pady=10)
        self.city_entry.bind('<Return>', lambda e: self.get_weather())

        # Search Button
        search_btn = tk.Button(self.root, text="Get Weather", command=self.get_weather, 
                               font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
        search_btn.pack(pady=10)

        # Result Labels
        self.city_label = tk.Label(self.root, text="", font=("Arial", 18, "bold"), bg="#f0f0f0")
        self.city_label.pack(pady=5)

        self.temp_label = tk.Label(self.root, text="", font=("Arial", 32), bg="#f0f0f0")
        self.temp_label.pack(pady=5)

        self.desc_label = tk.Label(self.root, text="", font=("Arial", 14, "italic"), bg="#f0f0f0")
        self.desc_label.pack(pady=5)

        self.info_label = tk.Label(self.root, text="", font=("Arial", 10), bg="#f0f0f0", fg="#666")
        self.info_label.pack(pady=10)

    def get_weather(self):
        city = self.city_entry.get().strip()
        
        if not city or city == "Enter City Name":
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        if API_KEY == "YOUR_API_KEY_HERE":
            messagebox.showerror("Configuration Error", "Please set your OpenWeatherMap API key in the script.")
            return

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        try:
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if response.status_code == 200:
                name = data['name']
                country = data['sys']['country']
                temp = data['main']['temp']
                desc = data['weather'][0]['description'].capitalize()
                humidity = data['main']['humidity']
                wind = data['wind']['speed']

                self.city_label.config(text=f"{name}, {country}")
                self.temp_label.config(text=f"{temp}\u00b0C")
                self.desc_label.config(text=desc)
                self.info_label.config(text=f"Humidity: {humidity}% | Wind: {wind} m/s")
            else:
                messagebox.showerror("Error", f"City not found: {city}")
        except Exception as e:
            messagebox.showerror("Network Error", f"Unable to fetch data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
