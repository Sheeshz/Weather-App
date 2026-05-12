import customtkinter as ctk
import requests
from datetime import datetime, timezone
import threading

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY = "ad63426974f86bfb69405c624ffa3783"
BASE    = "https://api.openweathermap.org/data/2.5"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Weather emoji map ─────────────────────────────────────────────────────────
ICONS = {
    "clear sky": "☀️", "few clouds": "🌤️", "scattered clouds": "⛅",
    "broken clouds": "🌥️", "overcast clouds": "☁️",
    "shower rain": "🌦️", "light rain": "🌧️", "moderate rain": "🌧️",
    "heavy intensity rain": "⛈️", "thunderstorm": "⛈️",
    "snow": "❄️", "light snow": "🌨️", "mist": "🌫️",
    "fog": "🌫️", "haze": "🌫️", "smoke": "🌫️",
    "drizzle": "🌦️", "freezing rain": "🌨️",
}

def get_icon(desc: str) -> str:
    desc = desc.lower()
    for key, icon in ICONS.items():
        if key in desc:
            return icon
    return "🌡️"

def kelvin_to_c(k): return k - 273.15
def wind_dir(deg):
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[round(deg / 45) % 8]


# ── Main App ──────────────────────────────────────────────────────────────────
class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Weather")
        self.geometry("480x820")
        self.minsize(420, 700)
        self.resizable(True, True)
        self.configure(fg_color="#0f0f14")

        self._build_ui()

    # ── UI skeleton ───────────────────────────────────────────────────────────
    def _build_ui(self):
        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(24, 0))

        self.city_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search city…",
            height=44,
            corner_radius=14,
            border_color="#2a2a3a",
            fg_color="#1a1a26",
            text_color="#e8e8f0",
            font=ctk.CTkFont(family="Helvetica", size=15),
        )
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.city_entry.bind("<Return>", lambda e: self._fetch())

        self.search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            width=80,
            height=44,
            corner_radius=14,
            fg_color="#4f6ef7",
            hover_color="#3a56e0",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            command=self._fetch,
        )
        self.search_btn.pack(side="left")

        # Status / error label
        self.status_lbl = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color="#ff6b6b"
        )
        self.status_lbl.pack(pady=(6, 0))

        # Scrollable content area
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", scrollbar_button_color="#2a2a3a"
        )
        self.scroll.pack(fill="both", expand=True, padx=12, pady=8)

        # ── Current weather card ──────────────────────────────────────────
        self.current_card = ctk.CTkFrame(
            self.scroll, fg_color="#1a1a26", corner_radius=20
        )
        self.current_card.pack(fill="x", pady=(4, 10))

        self.city_lbl   = ctk.CTkLabel(self.current_card, text="—",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color="#e8e8f0")
        self.city_lbl.pack(pady=(18, 0))

        self.date_lbl   = ctk.CTkLabel(self.current_card, text="",
            font=ctk.CTkFont(size=12), text_color="#6b6b8a")
        self.date_lbl.pack()

        self.icon_lbl   = ctk.CTkLabel(self.current_card, text="",
            font=ctk.CTkFont(size=64))
        self.icon_lbl.pack(pady=(8, 0))

        self.temp_lbl   = ctk.CTkLabel(self.current_card, text="—",
            font=ctk.CTkFont(family="Helvetica", size=62, weight="bold"),
            text_color="#ffffff")
        self.temp_lbl.pack(pady=(0, 0))

        self.desc_lbl   = ctk.CTkLabel(self.current_card, text="",
            font=ctk.CTkFont(size=15), text_color="#9898b8")
        self.desc_lbl.pack()

        # Stats row
        stats_frame = ctk.CTkFrame(self.current_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(14, 18))
        stats_frame.columnconfigure((0,1,2,3), weight=1)

        self._stat_labels = {}
        for col, (key, label) in enumerate([
            ("feels", "Feels like"),
            ("humidity", "Humidity"),
            ("wind", "Wind"),
            ("pressure", "Pressure"),
        ]):
            f = ctk.CTkFrame(stats_frame, fg_color="#13131e", corner_radius=12)
            f.grid(row=0, column=col, padx=4, pady=0, sticky="nsew")
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=10),
                         text_color="#55556a").pack(pady=(8, 2))
            v = ctk.CTkLabel(f, text="—", font=ctk.CTkFont(size=13, weight="bold"),
                             text_color="#c8c8e0")
            v.pack(pady=(0, 8))
            self._stat_labels[key] = v

        # ── Hourly section ────────────────────────────────────────────────
        ctk.CTkLabel(self.scroll, text="Hourly Forecast",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color="#9898b8", anchor="w").pack(fill="x", padx=8, pady=(4, 4))

        self.hourly_frame = ctk.CTkScrollableFrame(
            self.scroll, height=110, fg_color="#1a1a26",
            corner_radius=18, orientation="horizontal",
            scrollbar_button_color="#2a2a3a",
        )
        self.hourly_frame.pack(fill="x", pady=(0, 10))

        # ── 5-day section ─────────────────────────────────────────────────
        ctk.CTkLabel(self.scroll, text="5-Day Forecast",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color="#9898b8", anchor="w").pack(fill="x", padx=8, pady=(4, 4))

        self.daily_frame = ctk.CTkFrame(
            self.scroll, fg_color="#1a1a26", corner_radius=18
        )
        self.daily_frame.pack(fill="x", pady=(0, 14))

    # ── Data fetch (in thread) ────────────────────────────────────────────────
    def _fetch(self):
        city = self.city_entry.get().strip()
        if not city:
            return
        self.status_lbl.configure(text="Fetching…", text_color="#9898b8")
        self.search_btn.configure(state="disabled")
        threading.Thread(target=self._fetch_thread, args=(city,), daemon=True).start()

    def _fetch_thread(self, city):
        try:
            cur_r   = requests.get(f"{BASE}/weather?q={city}&appid={API_KEY}", timeout=8)
            fore_r  = requests.get(f"{BASE}/forecast?q={city}&appid={API_KEY}", timeout=8)

            if cur_r.status_code != 200:
                msg = cur_r.json().get("message", "City not found")
                self.after(0, self._show_error, msg.capitalize())
                return

            self.after(0, self._update_ui, cur_r.json(), fore_r.json())
        except Exception as e:
            self.after(0, self._show_error, "Network error — check connection")

    # ── UI update ─────────────────────────────────────────────────────────────
    def _update_ui(self, cur, fore):
        self.status_lbl.configure(text="")
        self.search_btn.configure(state="normal")

        # ── Current ───────────────────────────────────────────────────────
        desc  = cur["weather"][0]["description"]
        temp  = kelvin_to_c(cur["main"]["temp"])
        feels = kelvin_to_c(cur["main"]["feels_like"])
        hum   = cur["main"]["humidity"]
        wind  = cur["wind"]["speed"]
        wdir  = wind_dir(cur["wind"].get("deg", 0))
        pres  = cur["main"]["pressure"]
        city  = cur["name"] + ", " + cur["sys"]["country"]

        # local time via timezone offset in seconds
        offset = cur.get("timezone", 0)
        local_dt = datetime.fromtimestamp(cur["dt"] + offset, tz=timezone.utc)

        self.city_lbl.configure(text=city)
        self.date_lbl.configure(text=local_dt.strftime("%A, %d %B %Y  •  %H:%M"))
        self.icon_lbl.configure(text=get_icon(desc))
        self.temp_lbl.configure(text=f"{temp:.0f}°C")
        self.desc_lbl.configure(text=desc.title())
        self._stat_labels["feels"].configure(text=f"{feels:.0f}°C")
        self._stat_labels["humidity"].configure(text=f"{hum}%")
        self._stat_labels["wind"].configure(text=f"{wind:.1f} m/s {wdir}")
        self._stat_labels["pressure"].configure(text=f"{pres} hPa")

        # ── Hourly (next 24 h = 8 slots × 3 h) ───────────────────────────
        for w in self.hourly_frame.winfo_children():
            w.destroy()

        slots = fore["list"][:8]
        for slot in slots:
            offset_s = fore.get("city", {}).get("timezone", offset)
            dt = datetime.fromtimestamp(slot["dt"] + offset_s, tz=timezone.utc)
            t  = kelvin_to_c(slot["main"]["temp"])
            ic = get_icon(slot["weather"][0]["description"])

            f = ctk.CTkFrame(self.hourly_frame, fg_color="#13131e", corner_radius=14, width=72)
            f.pack(side="left", padx=5, pady=8)
            f.pack_propagate(False)
            ctk.CTkLabel(f, text=dt.strftime("%H:%M"),
                font=ctk.CTkFont(size=11), text_color="#6b6b8a").pack(pady=(10,2))
            ctk.CTkLabel(f, text=ic,
                font=ctk.CTkFont(size=22)).pack()
            ctk.CTkLabel(f, text=f"{t:.0f}°",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#e8e8f0").pack(pady=(2,10))

        # ── 5-day daily summary ───────────────────────────────────────────
        for w in self.daily_frame.winfo_children():
            w.destroy()

        # Group forecast by date, pick noon or closest
        daily: dict[str, list] = {}
        offset_s = fore.get("city", {}).get("timezone", offset)
        for slot in fore["list"]:
            dt = datetime.fromtimestamp(slot["dt"] + offset_s, tz=timezone.utc)
            day_key = dt.strftime("%Y-%m-%d")
            daily.setdefault(day_key, []).append(slot)

        rows = list(daily.items())[:5]
        for i, (day_key, slots) in enumerate(rows):
            # Pick the midday slot or median
            mid = sorted(slots, key=lambda s: abs(
                datetime.fromtimestamp(s["dt"] + offset_s, tz=timezone.utc).hour - 13
            ))[0]
            temps = [kelvin_to_c(s["main"]["temp"]) for s in slots]
            lo, hi = min(temps), max(temps)
            ic   = get_icon(mid["weather"][0]["description"])
            desc_d = mid["weather"][0]["description"].title()
            dt   = datetime.fromtimestamp(mid["dt"] + offset_s, tz=timezone.utc)

            row = ctk.CTkFrame(self.daily_frame, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=(4 if i else 12, 4 if i < len(rows)-1 else 12))
            row.columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=dt.strftime("%a"),
                width=42, anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#e8e8f0").grid(row=0, column=0, padx=(0,8))

            ctk.CTkLabel(row, text=f"{ic}  {desc_d}",
                anchor="w",
                font=ctk.CTkFont(size=13), text_color="#9898b8").grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(row,
                text=f"{hi:.0f}° / {lo:.0f}°",
                anchor="e",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#c8c8e0").grid(row=0, column=2, sticky="e")

            if i < len(rows) - 1:
                sep = ctk.CTkFrame(self.daily_frame, height=1, fg_color="#22223a")
                sep.pack(fill="x", padx=14)

    def _show_error(self, msg):
        self.status_lbl.configure(text=f"⚠  {msg}", text_color="#ff6b6b")
        self.search_btn.configure(state="normal")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()