import tkinter as tk
from tkinter import messagebox
import requests

# Open-Meteo API (100% Free, NO API Key needed)
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Beautiful Dark Mode Palette (Catppuccin Mocha inspired)
BG_COLOR = "#1e1e2e"
CARD_COLOR = "#313244"
TEXT_COLOR = "#cdd6f4"
SUBTEXT_COLOR = "#a6adc8"
ACCENT_COLOR = "#89b4fa"
INPUT_BG = "#181825"
ERROR_COLOR = "#f38ba8"

WMO_CODES = {
    0: "☀️ Clear sky", 
    1: "🌤️ Mainly clear", 2: "⛅ Partly cloudy", 3: "☁️ Overcast",
    45: "🌫️ Fog", 48: "🌫️ Depositing rime fog", 
    51: "🌧️ Light drizzle", 53: "🌧️ Moderate drizzle", 55: "🌧️ Dense drizzle", 
    61: "🌧️ Slight rain", 63: "🌧️ Moderate rain", 65: "🌧️ Heavy rain",
    71: "❄️ Slight snow", 73: "❄️ Moderate snow", 75: "❄️ Heavy snow", 77: "❄️ Snow grains",
    80: "🌦️ Slight rain showers", 81: "🌦️ Moderate rain showers", 82: "⛈️ Violent rain showers",
    85: "🌨️ Slight snow showers", 86: "🌨️ Heavy snow showers", 
    95: "🌩️ Thunderstorm", 96: "🌩️ Thunderstorm with slight hail", 99: "🌩️ Thunderstorm with heavy hail"
}

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium Weather Explorer")
        self.root.geometry("450x650")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.setup_ui()

    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(30, 10))
        
        title_label = tk.Label(header_frame, text="Current Weather", font=("Helvetica", 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        title_label.pack()

        subtitle_label = tk.Label(header_frame, text="Powered by Open-Meteo", font=("Helvetica", 10), bg=BG_COLOR, fg=SUBTEXT_COLOR)
        subtitle_label.pack()

        # Input Area
        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.pack(pady=20)

        # Custom Input Entry wrapped in Canvas for corner styling
        self.city_entry = tk.Entry(input_frame, font=("Helvetica", 14), width=18, 
                                   justify='center', bg=INPUT_BG, fg=TEXT_COLOR, 
                                   insertbackground=TEXT_COLOR, relief=tk.FLAT)
        self.city_entry.insert(0, "Enter City or Village...")
        self.city_entry.bind("<FocusIn>", self._clear_placeholder)
        self.city_entry.bind("<FocusOut>", self._add_placeholder)
        self.city_entry.bind('<Return>', lambda e: self.get_weather())
        self.city_entry.grid(row=0, column=0, ipady=10, padx=10, pady=5)

        # Custom Search Button
        search_btn = tk.Button(input_frame, text="🔍", command=self.get_weather, 
                               font=("Helvetica", 16), bg=ACCENT_COLOR, fg=BG_COLOR, 
                               relief=tk.FLAT, activebackground="#b4befe", activeforeground=BG_COLOR,
                               cursor="hand2", padx=15, pady=2)
        search_btn.grid(row=0, column=1)

        # Weather Card Canvas
        self.card_canvas = tk.Canvas(self.root, width=380, height=350, bg=BG_COLOR, highlightthickness=0)
        self.card_canvas.pack(pady=10)
        self.create_rounded_rect(self.card_canvas, 10, 10, 370, 340, radius=30, fill=CARD_COLOR)

        # Inside the Weather Card
        self.city_label = tk.Label(self.root, text="Search a Location", font=("Helvetica", 18, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
        self.card_canvas.create_window(190, 50, window=self.city_label)

        self.temp_label = tk.Label(self.root, text="--°", font=("Helvetica", 54, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
        self.card_canvas.create_window(190, 140, window=self.temp_label)

        self.desc_label = tk.Label(self.root, text="", font=("Helvetica", 16, "italic"), bg=CARD_COLOR, fg=ACCENT_COLOR)
        self.card_canvas.create_window(190, 220, window=self.desc_label)

        self.info_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg=CARD_COLOR, fg=SUBTEXT_COLOR)
        self.card_canvas.create_window(190, 280, window=self.info_label)

    def _clear_placeholder(self, event):
        if self.city_entry.get() == "Enter City or Village...":
            self.city_entry.delete(0, tk.END)

    def _add_placeholder(self, event):
        if not self.city_entry.get():
            self.city_entry.insert(0, "Enter City or Village...")

    def set_loading(self, loading=True):
        if loading:
            self.city_label.config(text="Searching...", fg=SUBTEXT_COLOR)
            self.temp_label.config(text="--°", fg=SUBTEXT_COLOR)
            self.desc_label.config(text="")
            self.info_label.config(text="")
            self.root.update()

    def get_weather(self):
        city = self.city_entry.get().strip()
        
        if not city or city == "Enter City or Village...":
            messagebox.showwarning("Input Error", "Please enter a location.")
            return

        self.set_loading(True)

        try:
            # 1. Geocoding
            geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
            geo_response = requests.get(GEO_URL, params=geo_params, timeout=5)
            geo_data = geo_response.json()

            if 'results' not in geo_data or not geo_data['results']:
                self.set_loading(False)
                messagebox.showerror("Not Found", f"Could not find coordinates for: {city}")
                self.city_label.config(text="Not Found", fg=ERROR_COLOR)
                return

            location = geo_data['results'][0]
            lat = location['latitude']
            lon = location['longitude']
            name = location['name']
            country = location.get('country', '')
            admin1 = location.get('admin1', '')
            
            display_name = f"{name}, {country}" if country else name
            if admin1 and country and admin1 != name:
                display_name = f"{name}, {admin1}"

            # 2. Weather Data
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            }
            weather_response = requests.get(WEATHER_URL, params=weather_params, timeout=5)
            weather_data = weather_response.json()

            current = weather_data['current']
            temp = current['temperature_2m']
            humidity = current['relative_humidity_2m']
            wind = current['wind_speed_10m']
            code = current['weather_code']

            desc = WMO_CODES.get(code, "Unknown status")

            self.city_label.config(text=display_name, fg=TEXT_COLOR)
            self.temp_label.config(text=f"{temp}°C", fg=TEXT_COLOR)
            self.desc_label.config(text=desc)
            self.info_label.config(text=f"💧 Humidity: {humidity}%    |    💨 Wind: {wind} km/h")

        except Exception as e:
            self.set_loading(False)
            messagebox.showerror("Network Error", f"Unable to fetch data:\n{str(e)}")
            self.city_label.config(text="Error", fg=ERROR_COLOR)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
