import tkinter as tk
import ctypes
import subprocess
import json
import os
import time
from datetime import datetime

PALETTE = {
    'bg': '#0f1220',
    'card': '#171b2e',
    'chip': '#222741',
    'chip_hover': '#2c3254',
    'text': '#e8eaf6',
    'muted': '#7b82a8',
    'accent': '#6c8cff',
    'accent_hover': '#839fff',
    'danger': '#ff5c7a',
    'danger_hover': '#ff7b93',
}
FONT = 'Segoe UI'
PRESETS = (30, 60, 90, 120)
MAX_MINUTES = 1440
VERSION = '1.0'
AUTHOR = 'Kaeswar'
EMAIL = 'kaeswar@gmail.com'
UPI = 'kaeswar@oksbi'
COPY_GLYPH = '⧉'
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.png')


class ShutdownService:
    def schedule(self, seconds):
        self.cancel()
        return self._run(['shutdown', '/s', '/t', str(seconds)])

    def cancel(self):
        return self._run(['shutdown', '/a'])

    def _run(self, args):
        result = subprocess.run(args, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return result.returncode == 0


class TimerStore:
    def __init__(self):
        folder = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'ShutdownTimer')
        os.makedirs(folder, exist_ok=True)
        self.path = os.path.join(folder, 'timer.json')

    def save(self, total, end):
        with open(self.path, 'w') as f:
            json.dump({'total': total, 'end': end}, f)

    def load(self):
        try:
            with open(self.path) as f:
                data = json.load(f)
            if data['end'] > time.time():
                return data['total'], data['end']
        except (OSError, ValueError, KeyError):
            pass
        return None

    def clear(self):
        try:
            os.remove(self.path)
        except OSError:
            pass


class TimerState:
    def __init__(self):
        self.total = 0
        self.end = 0

    @property
    def active(self):
        return self.end > 0

    def start(self, total, end):
        self.total, self.end = total, end

    def stop(self):
        self.total, self.end = 0, 0

    def remaining(self):
        return max(0, self.end - time.time())

    def fraction(self):
        return self.remaining() / self.total if self.total else 0


class FlatButton(tk.Label):
    def __init__(self, parent, text, command, bg, hover, fg=PALETTE['text'], font_size=11, padx=18, pady=10):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=(FONT, font_size, 'bold'),
                         padx=padx, pady=pady, cursor='hand2')
        self.command = command
        self.normal_bg, self.hover_bg = bg, hover
        self.bind('<Enter>', lambda e: self.config(bg=self.hover_bg))
        self.bind('<Leave>', lambda e: self.config(bg=self.normal_bg))
        self.bind('<Button-1>', lambda e: self.command())


class CountdownRing(tk.Canvas):
    SIZE = 220
    PAD = 16
    WIDTH = 12

    def __init__(self, parent):
        super().__init__(parent, width=self.SIZE, height=self.SIZE, bg=PALETTE['bg'], highlightthickness=0)
        box = (self.PAD, self.PAD, self.SIZE - self.PAD, self.SIZE - self.PAD)
        self.create_oval(*box, outline=PALETTE['card'], width=self.WIDTH)
        self.arc = self.create_arc(*box, start=90, extent=0, style='arc',
                                   outline=PALETTE['accent'], width=self.WIDTH)
        mid = self.SIZE // 2
        self.time_text = self.create_text(mid, mid - 8, text='00:00:00', fill=PALETTE['muted'],
                                          font=(FONT, 30, 'bold'))
        self.caption = self.create_text(mid, mid + 28, text='NO TIMER', fill=PALETTE['muted'],
                                        font=(FONT, 9, 'bold'))

    def show(self, seconds, fraction, active):
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        color = PALETTE['text'] if active else PALETTE['muted']
        self.itemconfig(self.time_text, text=f'{h:02d}:{m:02d}:{s:02d}', fill=color)
        self.itemconfig(self.caption, text='UNTIL SHUTDOWN' if active else 'NO TIMER')
        self.itemconfig(self.arc, extent=-min(359.9, 360 * fraction))


class AboutWindow(tk.Toplevel):
    FEATURES = (
        'Schedule a Windows shutdown with one click (30m, 1h, 1.5h, 2h)',
        f'Custom timer from 1 to {MAX_MINUTES} minutes',
        'Live countdown ring with the exact shutdown time',
        'Instant cancel, no confirmation needed',
        'Timer survives closing the app, so Cancel still works after a restart',
    )

    def __init__(self, parent, icon):
        super().__init__(parent, bg=PALETTE['bg'])
        self.title('About Shutdown Timer')
        self.resizable(False, False)
        self.transient(parent)
        self.logo = icon.subsample(3)
        self.iconphoto(False, icon)

        tk.Label(self, image=self.logo, bg=PALETTE['bg']).pack(pady=(24, 6))
        tk.Label(self, text='Shutdown Timer', font=(FONT, 18, 'bold'),
                 bg=PALETTE['bg'], fg=PALETTE['text']).pack()
        tk.Label(self, text=f'Version {VERSION}', font=(FONT, 9),
                 bg=PALETTE['bg'], fg=PALETTE['muted']).pack(pady=(2, 14))

        card = tk.Frame(self, bg=PALETTE['card'], padx=18, pady=14)
        card.pack(fill='x', padx=24)
        tk.Label(card, text='WHAT IT CAN DO', font=(FONT, 9, 'bold'),
                 bg=PALETTE['card'], fg=PALETTE['accent']).pack(anchor='w', pady=(0, 8))
        for line in self.FEATURES:
            tk.Label(card, text=f'•  {line}', font=(FONT, 10), justify='left', wraplength=300,
                     bg=PALETTE['card'], fg=PALETTE['text']).pack(anchor='w', pady=2)

        tk.Label(self, text='THOUGHT PROVIDER', font=(FONT, 9, 'bold'),
                 bg=PALETTE['bg'], fg=PALETTE['muted']).pack(pady=(18, 2))
        tk.Label(self, text=AUTHOR, font=(FONT, 14, 'bold'),
                 bg=PALETTE['bg'], fg=PALETTE['text']).pack()
        tk.Label(self, text=EMAIL, font=(FONT, 10),
                 bg=PALETTE['bg'], fg=PALETTE['accent']).pack(pady=(4, 0))
        donate = tk.Frame(self, bg=PALETTE['bg'])
        donate.pack(pady=(10, 0))
        tk.Label(donate, text='If interested, Donate via UPI:', font=(FONT, 9),
                 bg=PALETTE['bg'], fg=PALETTE['muted']).pack(side='left')
        upi = tk.Entry(donate, font=(FONT, 9, 'bold'), width=len(UPI), relief='flat', bd=0,
                       highlightthickness=0, justify='left', cursor='xterm',
                       fg=PALETTE['text'], readonlybackground=PALETTE['bg'],
                       selectbackground=PALETTE['accent'], selectforeground='white')
        upi.insert(0, UPI)
        upi.config(state='readonly')
        upi.pack(side='left', padx=(4, 0))
        self.copy_icon = tk.Label(donate, text=COPY_GLYPH, font=('Segoe UI Symbol', 11), cursor='hand2',
                                  bg=PALETTE['bg'], fg=PALETTE['accent'])
        self.copy_icon.pack(side='left', padx=(8, 0))
        self.copy_icon.bind('<Button-1>', lambda e: self.copy_upi())
        self.copy_icon.bind('<Enter>', lambda e: self.copy_icon.config(fg=PALETTE['accent_hover']))
        self.copy_icon.bind('<Leave>', lambda e: self.copy_icon.config(fg=PALETTE['accent']))

        FlatButton(self, 'Close', self.destroy, PALETTE['accent'], PALETTE['accent_hover'],
                   fg='white', padx=40, pady=8).pack(side='bottom', pady=20)
        self.update_idletasks()
        self.geometry(f'380x{self.winfo_reqheight()}')


    def copy_upi(self):
        self.clipboard_clear()
        self.clipboard_append(UPI)
        self.copy_icon.config(text='✓ Copied', font=(FONT, 9, 'bold'))
        self.after(1500, self.reset_copy_icon)

    def reset_copy_icon(self):
        if self.copy_icon.winfo_exists():
            self.copy_icon.config(text=COPY_GLYPH, font=('Segoe UI Symbol', 11))


class ShutdownTimerApp:
    def __init__(self, root):
        self.root = root
        self.service = ShutdownService()
        self.store = TimerStore()
        self.state = TimerState()
        self.about = None

        root.title('Shutdown Timer')
        root.geometry('380x500')
        root.resizable(False, False)
        root.configure(bg=PALETTE['bg'])
        self.icon = tk.PhotoImage(file=ICON_PATH)
        root.iconphoto(True, self.icon)

        tk.Label(root, text='Shutdown Timer', font=(FONT, 18, 'bold'),
                 bg=PALETTE['bg'], fg=PALETTE['text']).pack(pady=(24, 4))
        self.status = tk.Label(root, text='No timer active', font=(FONT, 10),
                               bg=PALETTE['bg'], fg=PALETTE['muted'])
        self.status.pack()

        self.ring = CountdownRing(root)
        self.ring.pack(pady=8)

        self.idle_panel = self.build_idle_panel()
        self.active_panel = self.build_active_panel()

        self.message = tk.Label(root, text='', font=(FONT, 9), bg=PALETTE['bg'], fg=PALETTE['danger'])
        self.message.pack(side='bottom', pady=12)

        about = tk.Label(root, text='About', font=(FONT, 9, 'underline'), cursor='hand2',
                         bg=PALETTE['bg'], fg=PALETTE['muted'])
        about.place(relx=1.0, x=-14, y=10, anchor='ne')
        about.bind('<Button-1>', lambda e: self.show_about())

        self.adopt_saved_timer()
        self.refresh_panels()
        self.tick()

    def build_idle_panel(self):
        panel = tk.Frame(self.root, bg=PALETTE['bg'])

        chips = tk.Frame(panel, bg=PALETTE['bg'])
        chips.pack()
        for minutes in PRESETS:
            label = f'{minutes // 60}h' if minutes % 60 == 0 else f'{minutes}m'
            FlatButton(chips, label, lambda m=minutes: self.start(m), PALETTE['chip'],
                       PALETTE['chip_hover'], padx=16, pady=9).pack(side='left', padx=4)

        row = tk.Frame(panel, bg=PALETTE['bg'])
        row.pack(pady=(16, 0))
        self.entry = tk.Entry(row, font=(FONT, 12), width=8, justify='center', relief='flat',
                              bg=PALETTE['chip'], fg=PALETTE['text'], insertbackground=PALETTE['text'],
                              highlightthickness=1, highlightbackground=PALETTE['chip'],
                              highlightcolor=PALETTE['accent'])
        self.entry.pack(side='left', ipady=8, padx=(0, 6))
        self.entry.bind('<Return>', lambda e: self.start_custom())
        tk.Label(row, text='min', font=(FONT, 10), bg=PALETTE['bg'], fg=PALETTE['muted']).pack(side='left', padx=(0, 10))
        FlatButton(row, 'Start', self.start_custom, PALETTE['accent'], PALETTE['accent_hover'],
                   fg='white', pady=8).pack(side='left')
        return panel

    def build_active_panel(self):
        panel = tk.Frame(self.root, bg=PALETTE['bg'])
        FlatButton(panel, 'Cancel Shutdown', self.cancel, PALETTE['danger'], PALETTE['danger_hover'],
                   fg='white', font_size=12, padx=50, pady=12).pack()
        return panel

    def adopt_saved_timer(self):
        saved = self.store.load()
        if saved:
            self.state.start(*saved)
        else:
            self.store.clear()

    def start_custom(self):
        try:
            minutes = int(self.entry.get())
        except ValueError:
            return self.flash('Enter a whole number of minutes')
        if not 1 <= minutes <= MAX_MINUTES:
            return self.flash(f'Choose between 1 and {MAX_MINUTES} minutes')
        self.start(minutes)

    def start(self, minutes):
        seconds = minutes * 60
        if not self.service.schedule(seconds):
            return self.flash('Could not schedule shutdown')
        end = time.time() + seconds
        self.state.start(seconds, end)
        self.store.save(seconds, end)
        self.entry.delete(0, 'end')
        self.flash('')
        self.refresh_panels()

    def cancel(self):
        self.service.cancel()
        self.state.stop()
        self.store.clear()
        self.flash('')
        self.refresh_panels()

    def show_about(self):
        if self.about and self.about.winfo_exists():
            return self.about.focus()
        self.about = AboutWindow(self.root, self.icon)

    def flash(self, text):
        self.message.config(text=text)

    def refresh_panels(self):
        if self.state.active:
            self.idle_panel.pack_forget()
            self.active_panel.pack(pady=10)
            at = datetime.fromtimestamp(self.state.end).strftime('%I:%M %p').lstrip('0')
            self.status.config(text=f'Shuts down at {at}', fg=PALETTE['accent'])
        else:
            self.active_panel.pack_forget()
            self.idle_panel.pack(pady=10)
            self.status.config(text='No timer active', fg=PALETTE['muted'])

    def tick(self):
        if self.state.active and self.state.remaining() <= 0:
            self.state.stop()
            self.store.clear()
            self.refresh_panels()
        self.ring.show(self.state.remaining(), self.state.fraction(), self.state.active)
        self.root.after(250, self.tick)


if __name__ == '__main__':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Kaeswar.ShutdownTimer')
    root = tk.Tk()
    ShutdownTimerApp(root)
    root.mainloop()
