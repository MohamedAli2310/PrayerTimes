import tkinter as tk
from tkinter import font as tkfont, colorchooser
from PIL import Image, ImageTk
import requests
from datetime import datetime, timedelta
from playsound import playsound
import threading
import schedule
import time
import os

is_adhan_playing = False
adhan_thread = None
exit_flag = threading.Event()


class ToggleButton(tk.Canvas):
    def __init__(self, parent, width=60, height=30, padding=3, command=None):
        super().__init__(parent, width=width, height=height, bg='black', highlightthickness=0)
        self.command = command
        self.toggle_state = False

        self.width = width
        self.height = height
        self.padding = padding

        self.switch_bg = self.create_rounded_rect(padding, padding, width - padding, height - padding,
                                                  radius=height // 2, fill='#4a4a4a', outline='')

        switch_size = height - 2 * padding
        self.switch = self.create_oval(padding, padding, padding + switch_size, height - padding, fill='white',
                                       outline='')

        self.bind("<Button-1>", self.toggle)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def toggle(self, event=None):
        self.toggle_state = not self.toggle_state
        if self.toggle_state:
            self.itemconfig(self.switch_bg, fill='#00aaff')
            self.coords(self.switch, self.width - self.height + self.padding, self.padding,
                        self.width - self.padding, self.height - self.padding)
        else:
            self.itemconfig(self.switch_bg, fill='#4a4a4a')
            self.coords(self.switch, self.padding, self.padding,
                        self.height - self.padding, self.height - self.padding)
        if self.command:
            self.command()


def get_location():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        latitude = data['latitude']
        longitude = data['longitude']
        city = data.get('city', 'Unknown')
        region = data.get('region', 'Unknown')
        country = data.get('country_name', 'Unknown')
        location_name = f"{city}, {region}, {country}"
        return latitude, longitude, location_name, False
    except:
        return 40.7440, -74.0324, "West New York, New Jersey, United States", True


def get_prayer_times(latitude, longitude):
    url = f"http://api.aladhan.com/v1/timings/{datetime.now().strftime('%d-%m-%Y')}?latitude={latitude}&longitude={longitude}&method=2"
    response = requests.get(url)
    data = response.json()
    timings = data['data']['timings']
    return {
        'Fajr': timings['Fajr'],
        'Shrooq': timings['Sunrise'],
        'Dhuhr': timings['Dhuhr'],
        'Asr': timings['Asr'],
        'Maghrib': timings['Maghrib'],
        'Isha': timings['Isha']
    }


def toggle_adhan(prayer):
    adhan_enabled[prayer] = not adhan_enabled[prayer]


def update_display():
    global current_time_label, date_label, prayer_labels, prayer_times, is_adhan_playing
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time_label.config(text=current_time)
    date_label.config(text=current_date)

    next_prayer = get_next_prayer()
    for prayer, (name_label, time_label, _) in prayer_labels.items():
        time_label.config(text=f"{prayer_times[prayer]}")
        if prayer == next_prayer:
            name_label.config(fg='#00FFFF')
            time_label.config(fg='#00FFFF')
        else:
            name_label.config(fg='white')
            time_label.config(fg='white')

    check_adhan()
    if not exit_flag.is_set():
        root.after(1000, update_display)


def update_prayer_times():
    global prayer_times, LATITUDE, LONGITUDE, LOCATION_NAME, location_label, using_default
    LATITUDE, LONGITUDE, LOCATION_NAME, using_default = get_location()
    prayer_times = get_prayer_times(LATITUDE, LONGITUDE)
    location_text = f"Location: {LOCATION_NAME}"
    if using_default:
        location_text += " (Default)"
    location_label.config(text=location_text)
    reset_dhuhr_time()


def run_schedule():
    while not exit_flag.is_set():
        schedule.run_pending()
        time.sleep(1)


def check_adhan():
    global is_adhan_playing, adhan_thread
    current_time = datetime.now()
    current_time_str = current_time.strftime("%H:%M")
    current_second = current_time.second
    for prayer, prayer_time in prayer_times.items():
        if current_time_str == prayer_time and \
                prayer in adhan_enabled and \
                adhan_enabled[prayer] and \
                current_second == 0:
            if not is_adhan_playing:
                is_adhan_playing = True
                adhan_thread = threading.Thread(target=play_adhan, daemon=True)
                adhan_thread.start()
                show_audio_icon(prayer)
            break
    else:
        if is_adhan_playing and (adhan_thread is None or not adhan_thread.is_alive()):
            is_adhan_playing = False
            hide_audio_icon()


def play_adhan():
    playsound("adhan.mp3")


def get_next_prayer():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    for prayer, prayer_time in prayer_times.items():
        if current_time < prayer_time:
            return prayer
    return list(prayer_times.keys())[0]


def edit_dhuhr_time():
    new_time = dhuhr_entry.get()
    if new_time and len(new_time) == 5 and ":" in new_time:
        prayer_times['Dhuhr'] = new_time
        update_display()


def reset_dhuhr_time():
    global prayer_times
    original_dhuhr = get_prayer_times(LATITUDE, LONGITUDE)['Dhuhr']
    prayer_times['Dhuhr'] = original_dhuhr
    dhuhr_entry.delete(0, tk.END)
    dhuhr_entry.insert(0, original_dhuhr)
    update_display()


def show_audio_icon(prayer):
    row = list(prayer_times.keys()).index(prayer) + 3
    audio_icon_button.grid(row=row, column=0, padx=(0, 10), pady=5, sticky='e')


def hide_audio_icon():
    audio_icon_button.grid_forget()


def stop_adhan():
    global is_adhan_playing, adhan_thread
    if is_adhan_playing:
        is_adhan_playing = False
        if adhan_thread:
            adhan_thread.join(timeout=1)
        hide_audio_icon()


def change_background_color():
    color = colorchooser.askcolor(title="Choose background color")
    if color[1]:
        root.configure(bg=color[1])
        main_frame.configure(bg=color[1])
        for widget in main_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=color[1])


def exit_program():
    exit_flag.set()
    root.quit()
    root.destroy()
    os._exit(0)


root = tk.Tk()
root.title("Prayer Times")
root.attributes("-fullscreen", True)
root.configure(bg='black')

time_font = tkfont.Font(family="Helvetica", size=72, weight="bold")
date_font = tkfont.Font(family="Helvetica", size=36)
location_font = tkfont.Font(family="Helvetica", size=24)
prayer_font = tkfont.Font(family="Helvetica", size=28)

main_frame = tk.Frame(root, bg='black')
main_frame.place(relx=0.5, rely=0.5, anchor='center')

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_columnconfigure(2, weight=1)
main_frame.grid_columnconfigure(3, weight=1)

current_time_label = tk.Label(main_frame, font=time_font, bg='black', fg='white')
current_time_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))

date_label = tk.Label(main_frame, font=date_font, bg='black', fg='white')
date_label.grid(row=1, column=0, columnspan=4, pady=(0, 20))

location_label = tk.Label(main_frame, font=location_font, bg='black', fg='white')
location_label.grid(row=2, column=0, columnspan=4, pady=(0, 40))

LATITUDE, LONGITUDE, LOCATION_NAME, using_default = get_location()
prayer_times = get_prayer_times(LATITUDE, LONGITUDE)

adhan_prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

prayer_labels = {}
adhan_enabled = {}
for i, prayer in enumerate(prayer_times):
    name_label = tk.Label(main_frame, text=f"{prayer}:", font=prayer_font, bg='black', fg='white', anchor='e')
    name_label.grid(row=i + 3, column=1, pady=10, padx=(0, 20), sticky='e')

    time_label = tk.Label(main_frame, font=prayer_font, bg='black', fg='white', anchor='w')
    time_label.grid(row=i + 3, column=2, pady=10, sticky='w')

    if prayer in adhan_prayers:
        toggle = ToggleButton(main_frame, width=60, height=30, command=lambda p=prayer: toggle_adhan(p))
        toggle.grid(row=i + 3, column=3, pady=10, padx=(20, 0), sticky='w')
        adhan_enabled[prayer] = False
    else:
        toggle = None

    prayer_labels[prayer] = (name_label, time_label, toggle)

dhuhr_entry = tk.Entry(main_frame, font=prayer_font, width=5)
dhuhr_entry.grid(row=5, column=4, pady=10, padx=(20, 0), sticky='w')
dhuhr_entry.insert(0, prayer_times['Dhuhr'])

edit_button = tk.Button(main_frame, text="Edit", command=edit_dhuhr_time)
edit_button.grid(row=5, column=5, pady=10, padx=(5, 0), sticky='w')

reset_button = tk.Button(main_frame, text="Reset", command=reset_dhuhr_time)
reset_button.grid(row=5, column=6, pady=10, padx=(5, 0), sticky='w')

audio_icon = Image.open("audio_icon.png").resize((30, 30))
audio_icon = ImageTk.PhotoImage(audio_icon)
audio_icon_button = tk.Button(main_frame, image=audio_icon, bg='black', command=stop_adhan, borderwidth=0,
                              highlightthickness=0)
audio_icon_button.config(bd=5, relief=tk.RAISED)

gear_icon = Image.open("gear_icon.png").resize((30, 30))
gear_icon = ImageTk.PhotoImage(gear_icon)
gear_button = tk.Button(main_frame, image=gear_icon, bg='black', command=change_background_color)
gear_button.grid(row=0, column=5, sticky='ne', padx=(0, 10), pady=(10, 0))

exit_button = tk.Button(root, text="Exit", command=exit_program, font=("Helvetica", 14))
exit_button.place(relx=0.98, rely=0.98, anchor='se')

tk.Label(main_frame, bg='black').grid(row=len(prayer_times) + 3, column=0, columnspan=4, pady=20)

schedule.every().day.at("00:01").do(update_prayer_times)

schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

update_prayer_times()

is_adhan_playing = False
update_display()

root.mainloop()
