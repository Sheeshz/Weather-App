# 🌤️ PyWeather

A minimal, modern desktop weather app built with Python and CustomTkinter — featuring real-time conditions, hourly timelines, and a 5-day forecast.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-5865F2)
![OpenWeatherMap](https://img.shields.io/badge/API-OpenWeatherMap-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Current weather** — temperature, description, feels-like, humidity, wind speed & direction, pressure
- **Hourly forecast** — horizontally scrollable 24-hour timeline (3-hour intervals)
- **5-day forecast** — daily high/low with weather icon and condition description
- **Local time display** — uses the city's timezone offset from the API, not your system clock
- **Emoji weather icons** — mapped from OpenWeatherMap condition descriptions
- **Non-blocking UI** — API calls run in a background thread; the window never freezes
- **Error handling** — clear messages for invalid cities and network failures
- **Responsive & scrollable** — adapts to any window size

---

## 📸 Preview

```
┌─────────────────────────────────────┐
│  🔍 Search city…          [Search]  │
├─────────────────────────────────────┤
│         New Delhi, IN               │
│    Monday, 12 May 2025 • 14:30      │
│              ☀️                      │
│             34°C                    │
│         Clear Sky                   │
│  ┌──────┬────────┬───────┬────────┐ │
│  │ 32°C │  18%   │1.2m/s │1012hPa│ │
│  │Feels │Humidity│ Wind  │Pressure│ │
│  └──────┴────────┴───────┴────────┘ │
├─────────────────────────────────────┤
│  Hourly Forecast                    │
│  [14:00] [17:00] [20:00] [23:00]…   │
│   ☀️34°   🌤️31°   🌙28°   🌙27°     │
├─────────────────────────────────────┤
│  5-Day Forecast                     │
│  Mon    ☀️ Clear Sky      35° / 27° │
│  Tue   🌤️ Few Clouds     33° / 26° │
│  Wed   🌧️ Light Rain     29° / 23° │
│  Thu    ⛅ Scattered      31° / 25° │
│  Fri    ☀️ Clear Sky      36° / 28° │
└─────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A free [OpenWeatherMap API key](https://openweathermap.org/api)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/pyweather.git
   cd pyweather
   ```

2. **Install dependencies**
   ```bash
   pip install customtkinter requests
   ```

3. **Add your API key**

   Open `weather_app.py` and replace the placeholder on line 6:
   ```python
   API_KEY = "your_openweathermap_api_key_here"
   ```

4. **Run the app**
   ```bash
   python weather_app.py
   ```

---

## 🔑 Getting an API Key

1. Sign up for free at [openweathermap.org](https://home.openweathermap.org/users/sign_up)
2. Go to **API keys** in your account dashboard
3. Copy your default key (or generate a new one)
4. Keys activate within **10–15 minutes** of account creation

> The free tier includes the **Current Weather** and **5 Day / 3 Hour Forecast** APIs — everything this app uses.

---

## 📁 Project Structure

```
pyweather/
│
├── weather_app.py       # Main application (UI + logic)
└── README.md
```

---

## 🛠️ Built With

| Library | Purpose |
|---|---|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Modern dark-themed UI widgets |
| [Requests](https://docs.python-requests.org/) | HTTP calls to OpenWeatherMap |
| [threading](https://docs.python.org/3/library/threading.html) | Non-blocking API fetches (stdlib) |
| [datetime](https://docs.python.org/3/library/datetime.html) | Timezone-aware time display (stdlib) |

---

## 🌐 API Reference

This app uses two OpenWeatherMap endpoints:

| Endpoint | Usage |
|---|---|
| `/data/2.5/weather` | Current weather for the searched city |
| `/data/2.5/forecast` | 5-day forecast in 3-hour intervals |

Both are available on the **free tier** (60 calls/min, 1M calls/month).

---

## ⚙️ Configuration

You can tweak the following constants at the top of `weather_app.py`:

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | `""` | Your OpenWeatherMap API key |
| `BASE` | OWM API URL | Base URL for API requests |
| Window size | `480×820` | `self.geometry()` in `__init__` |
| Hourly slots | `8` (24 hrs) | Slice `fore["list"][:8]` |
| Forecast days | `5` | `rows = list(daily.items())[:5]` |

---

## 🐛 Known Limitations

- Temperature is displayed in **Celsius only**; Fahrenheit toggle is not yet implemented
- Hourly scroll bar is visible but subtle — scroll with mouse wheel or drag
- API key is hardcoded; not read from environment variables or a config file yet

---

## 🗺️ Roadmap

- [ ] °C / °F toggle button
- [ ] Store API key in `.env` or `config.ini`
- [ ] UV index and sunrise/sunset times
- [ ] Animated weather backgrounds
- [ ] System tray support

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Weather data provided by [OpenWeatherMap](https://openweathermap.org/)
- UI framework by [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
