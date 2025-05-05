import tkinter as tk
import datetime
import ctypes
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def update_display():
    now = datetime.datetime.now()

    if current_mode[0] == 'clock':
        time_str = now.strftime('%H:%M:%S')
        canvas.itemconfig(time_text, text=time_str)
        canvas.itemconfig(date_text, text=now.strftime('%d %b %Y').upper())
    elif current_mode[0] == 'timer':
        elapsed = datetime.datetime.now() - timer_start[0]
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        canvas.itemconfig(time_text, text=timer_str)
        canvas.itemconfig(date_text, text="TIMER")
    elif current_mode[0] == 'date':
        canvas.itemconfig(time_text, text=now.strftime('%b %Y').upper())
        canvas.itemconfig(date_text, text="")
    elif current_mode[0] == 'countdown':
        remaining = countdown_target[0] - now
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            canvas.itemconfig(time_text, text=countdown_str)
            canvas.itemconfig(date_text, text="COUNTDOWN")
        else:
            canvas.itemconfig(time_text, text="00:00:00")
            canvas.itemconfig(date_text, text="TIME'S UP")
            if not is_expired[0]:
                canvas.itemconfig(rectangle_id, fill='red')
                is_expired[0] = True

    root.after(1000, update_display)

def set_mode(mode):
    current_mode[0] = mode
    canvas.itemconfig(rectangle_id, fill='black')
    is_expired[0] = False
    if mode == 'timer':
        timer_start[0] = datetime.datetime.now()
    elif mode == 'countdown':
        open_countdown_input()
    elif mode == 'wiki':
        open_wiki_search()

def open_countdown_input():
    global input_win
    input_win = tk.Toplevel(root)
    input_win.overrideredirect(True)
    input_win.attributes('-topmost', True)
    input_win.configure(bg='pink')
    input_win.wm_attributes('-transparentcolor', 'pink')

    w, h = 300, 140
    x = root.winfo_x() + 50
    y = root.winfo_y() + 50
    input_win.geometry(f"{w}x{h}+{x}+{y}")

    input_canvas = tk.Canvas(input_win, width=w, height=h, bg='pink', highlightthickness=0)
    input_canvas.pack()

    def round_rect(x1, y1, x2, y2, radius=50, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return input_canvas.create_polygon(points, **kwargs, smooth=True)

    rect = round_rect(0, 0, w, h, radius=50, fill='black')

    input_canvas.create_text(50, 40, text="H:", fill="white", font=("Arial", 12))
    input_canvas.create_text(125, 40, text="M:", fill="white", font=("Arial", 12))
    input_canvas.create_text(200, 40, text="S:", fill="white", font=("Arial", 12))

    h_entry = tk.Entry(input_win, width=3, font=("Arial", 12), justify='center')
    m_entry = tk.Entry(input_win, width=3, font=("Arial", 12), justify='center')
    s_entry = tk.Entry(input_win, width=3, font=("Arial", 12), justify='center')

    input_canvas.create_window(70, 40, window=h_entry)
    input_canvas.create_window(145, 40, window=m_entry)
    input_canvas.create_window(220, 40, window=s_entry)

    def start_countdown():
        try:
            h = int(h_entry.get() or 0)
            m = int(m_entry.get() or 0)
            s = int(s_entry.get() or 0)
            total_sec = h*3600 + m*60 + s
            countdown_target[0] = datetime.datetime.now() + datetime.timedelta(seconds=total_sec)
            input_win.destroy()
        except:
            pass

    btn = tk.Button(input_win, text="Start", command=start_countdown, bg='black', fg='white',
                    highlightbackground='white', highlightcolor='white', relief='solid', bd=1)
    input_canvas.create_window(w//2, 100, window=btn)

    def start_move(event):
        input_win.x = event.x
        input_win.y = event.y

    def do_move(event):
        dx = event.x - input_win.x
        dy = event.y - input_win.y
        x = input_win.winfo_x() + dx
        y = input_win.winfo_y() + dy
        input_win.geometry(f"+{x}+{y}")

    input_canvas.bind("<Button-1>", start_move)
    input_canvas.bind("<B1-Motion>", do_move)

def open_menu(event):
    global menu_win
    if menu_win and menu_win.winfo_exists():
        menu_win.destroy()

    menu_win = tk.Toplevel(root)
    menu_win.overrideredirect(True)
    menu_win.attributes('-topmost', True)
    menu_win.configure(bg='pink')
    menu_win.wm_attributes('-transparentcolor', 'pink')

    w, h = 200, 220
    x = event.x_root
    y = event.y_root
    menu_win.geometry(f"{w}x{h}+{x}+{y}")

    menu_canvas = tk.Canvas(menu_win, width=w, height=h, bg='pink', highlightthickness=0)
    menu_canvas.pack()

    def round_rect(x1, y1, x2, y2, radius=30, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return menu_canvas.create_polygon(points, **kwargs, smooth=True)

    rect = round_rect(0, 0, w, h, radius=30, fill='black')

    def close_and_set(mode):
        set_mode(mode)
        menu_win.destroy()

    btn_clock = tk.Button(menu_win, text="Clock", command=lambda: close_and_set('clock'), bg='black', fg='white',
                          highlightbackground='white', highlightcolor='white', relief='solid', bd=1)
    btn_timer = tk.Button(menu_win, text="Timer", command=lambda: close_and_set('timer'), bg='black', fg='white',
                          highlightbackground='white', highlightcolor='white', relief='solid', bd=1)
    btn_date = tk.Button(menu_win, text="Date", command=lambda: close_and_set('date'), bg='black', fg='white',
                         highlightbackground='white', highlightcolor='white', relief='solid', bd=1)
    btn_countdown = tk.Button(menu_win, text="Countdown", command=lambda: close_and_set('countdown'), bg='black', fg='white',
                              highlightbackground='white', highlightcolor='white', relief='solid', bd=1)
    btn_wiki = tk.Button(menu_win, text="Wiki", command=lambda: close_and_set('wiki'), bg='black', fg='white',
                         highlightbackground='white', highlightcolor='white', relief='solid', bd=1)

    menu_canvas.create_window(w//2, 40, window=btn_clock)
    menu_canvas.create_window(w//2, 80, window=btn_timer)
    menu_canvas.create_window(w//2, 120, window=btn_date)
    menu_canvas.create_window(w//2, 160, window=btn_countdown)
    menu_canvas.create_window(w//2, 200, window=btn_wiki)

    menu_canvas.bind("<Button-1>", lambda e: None)
    menu_win.bind("<Button-1>", lambda e: None)

    def close_on_click_outside(event):
        if menu_win and not (menu_win == event.widget or menu_win in event.widget.winfo_toplevel().winfo_children()):
            menu_win.destroy()

    root.bind("<Button-1>", close_on_click_outside)

def open_wiki_search():
    global input_win, search_entry
    input_win = tk.Toplevel(root)
    input_win.overrideredirect(True)
    input_win.attributes('-topmost', True)
    input_win.configure(bg='pink')
    input_win.wm_attributes('-transparentcolor', 'pink')

    w, h = 300, 80
    x = root.winfo_x() + 50
    y = root.winfo_y() + 50
    input_win.geometry(f"{w}x{h}+{x}+{y}")

    input_canvas = tk.Canvas(input_win, width=w, height=h, bg='pink', highlightthickness=0)
    input_canvas.pack()

    def round_rect(x1, y1, x2, y2, radius=30, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return input_canvas.create_polygon(points, **kwargs, smooth=True)

    rect = round_rect(0, 0, w, h, radius=30, fill='black')

    search_entry = tk.Entry(input_win, font=("Arial", 12))
    input_canvas.create_window(w//2, h//2, window=search_entry)

    search_entry.bind("<Return>", fetch_wikipedia_summary)

def fetch_wikipedia_summary(event=None):
    query = search_entry.get()
    if query:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urlopen(req) as response:
                data = json.loads(response.read().decode())
                summary = data.get("extract", "No summary available.")
                show_wiki_result(query, summary)
        except HTTPError as e:
            show_wiki_result(query, f"HTTP Error: {e.code}")
        except URLError as e:
            show_wiki_result(query, f"URL Error: {e.reason}")
        except Exception as e:
            show_wiki_result(query, f"Error: {e}")
        input_win.destroy()

def show_wiki_result(title, summary):
    result_win = tk.Toplevel(root)
    result_win.title(title)
    result_win.geometry("400x300")
    result_win.attributes('-topmost', True)

    text_widget = tk.Text(result_win, wrap='word', bg='black', fg='white', font=("Arial", 12))
    text_widget.insert('1.0', summary)
    text_widget.config(state='disabled')
    text_widget.pack(expand=True, fill='both')

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
window_width = 300
window_height = 100
x_pos = (screen_width // 2) - (window_width // 2)
y_pos = 20

root = tk.Tk()
root.overrideredirect(True)
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
root.attributes('-topmost', True)
root.configure(bg='pink')
root.wm_attributes('-transparentcolor', 'pink')

canvas = tk.Canvas(root, width=window_width, height=window_height, bg='pink', highlightthickness=0)
canvas.pack()

def round_rect(x1, y1, x2, y2, radius=50, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

rectangle_id = round_rect(0, 0, window_width, window_height, radius=50, fill='black')
time_text = canvas.create_text(window_width//2, 38, text="", fill="white", font=("Arial", 28, "bold"))
date_text = canvas.create_text(window_width//2, 70, text="", fill="gray80", font=("Arial", 10))

def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    dx = event.x - root.x
    dy = event.y - root.y
    x = root.winfo_x() + dx
    y = root.winfo_y() + dy
    root.geometry(f"+{x}+{y}")

canvas.bind("<Button-1>", start_move)
canvas.bind("<B1-Motion>", do_move)

def reset_color(event):
    if is_expired[0]:
        canvas.itemconfig(rectangle_id, fill='black')
        is_expired[0] = False

canvas.bind("<ButtonRelease-1>", reset_color)
canvas.bind("<Button-3>", open_menu)

current_mode = ['clock']
timer_start = [datetime.datetime.now()]
countdown_target = [datetime.datetime.now()]
is_expired = [False]
menu_win = None
input_win = None

update_display()
root.mainloop()
