"""
main_app.py - Girls Safety & Health Assistant
Main Tkinter application with all screens and navigation.

Run:  python main_app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from datetime import datetime, date

# ── Local modules ─────────────────────────────────────────────────────────
import database as db
import safety_logic as safety
import health_logic as health

# ── Initialize DB on startup ─────────────────────────────────────────────
db.initialize_database()

# ══════════════════════════════════════════════════════════════════════════
#  THEME CONSTANTS
# ══════════════════════════════════════════════════════════════════════════

# Warm rose-toned dark theme
C = {
    "bg":         "#1A0A12",   # Deep wine background
    "surface":    "#2D1520",   # Card / panel surface
    "surface2":   "#3D1F2C",   # Slightly lighter surface
    "primary":    "#E85D8A",   # Rose / hot pink
    "primary_dk": "#C04070",   # Darker accent
    "secondary":  "#FF9EC0",   # Soft pink
    "accent":     "#FF6B9D",   # Bright accent
    "success":    "#6EE7A0",   # Mint green
    "warning":    "#FFD166",   # Warm amber
    "danger":     "#FF4757",   # Alert red
    "text":       "#FFE8F0",   # Near white with pink tint
    "text_muted": "#C4879A",   # Muted pink-grey
    "border":     "#5C2E40",   # Subtle border
}

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_H2     = ("Georgia", 14, "bold")
FONT_H3     = ("Georgia", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_BIG    = ("Georgia", 32, "bold")


# ══════════════════════════════════════════════════════════════════════════
#  HELPER WIDGETS
# ══════════════════════════════════════════════════════════════════════════

def styled_button(parent, text, command, bg=None, fg=None, width=18, pady=8, font=None):
    bg = bg or C["primary"]
    fg = fg or C["text"]
    font = font or FONT_BUTTON
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=C["primary_dk"], activeforeground=C["text"],
        relief="flat", bd=0, font=font, cursor="hand2",
        padx=14, pady=pady, width=width
    )
    return btn


def card_frame(parent, **kwargs):
    """A surface-coloured rounded-look frame."""
    defaults = {"bg": C["surface"], "relief": "flat", "bd": 0}
    defaults.update(kwargs)
    f = tk.Frame(parent, **defaults)
    return f


def section_label(parent, text):
    return tk.Label(parent, text=text, bg=C["surface"], fg=C["secondary"],
                    font=FONT_H2, anchor="w")


def entry_widget(parent, show=None):
    kw = dict(bg=C["surface2"], fg=C["text"], insertbackground=C["text"],
               relief="flat", bd=0, font=FONT_BODY,
               highlightthickness=1, highlightbackground=C["border"],
               highlightcolor=C["primary"])
    if show:
        kw["show"] = show
    return tk.Entry(parent, **kw)


def scrollable_text(parent, height=8, width=60):
    frame = tk.Frame(parent, bg=C["surface"], relief="flat")
    txt = tk.Text(frame, height=height, width=width,
                  bg=C["surface2"], fg=C["text"], insertbackground=C["text"],
                  font=FONT_BODY, relief="flat", bd=0, wrap="word",
                  highlightthickness=1, highlightbackground=C["border"])
    sb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=sb.set)
    txt.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return frame, txt


# ══════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION CLASS
# ══════════════════════════════════════════════════════════════════════════

class GirlsSafetyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Girls Safety & Health Assistant 💗")
        self.geometry("920x680")
        self.configure(bg=C["bg"])
        self.resizable(True, True)

        # State
        self.current_user = None   # dict from DB after login
        self._sos_active = False
        self._fake_call_active = False

        # Container for all pages
        self.container = tk.Frame(self, bg=C["bg"])
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (LoginPage, RegisterPage, DashboardPage):
            frame = PageClass(self.container, self)
            self.frames[PageClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_page("LoginPage")

        # Periodic reminder checker (every 60 seconds)
        self._start_reminder_checker()

    # ── Navigation ────────────────────────────────────────────────────────

    def show_page(self, name):
        frame = self.frames[name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def logout(self):
        self.current_user = None
        self.show_page("LoginPage")

    # ── Reminder background checker ───────────────────────────────────────

    def _start_reminder_checker(self):
        def check():
            while True:
                time.sleep(60)
                if self.current_user:
                    self._check_reminders()
        t = threading.Thread(target=check, daemon=True)
        t.start()

    def _check_reminders(self):
        reminders = db.get_reminders(self.current_user["id"])
        today = date.today().isoformat()
        for r in reminders:
            if r["remind_date"] <= today:
                self.after(0, lambda r=r: messagebox.showinfo(
                    "⏰ Reminder",
                    f"{r['reminder_type'].upper()}\n\n{r['message']}"
                ))
                db.mark_reminder_done(r["id"])


# ══════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════

class LoginPage(tk.Frame):
    def __init__(self, parent, app: GirlsSafetyApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        # ── Decorative header ─────────────────────────────────────────────
        header = tk.Frame(self, bg=C["primary"], height=6)
        header.pack(fill="x")

        center = tk.Frame(self, bg=C["bg"])
        center.pack(expand=True)

        tk.Label(center, text="💗", font=("Segoe UI Emoji", 48), bg=C["bg"],
                 fg=C["primary"]).pack(pady=(40, 5))
        tk.Label(center, text="Girls Safety &", font=FONT_TITLE,
                 bg=C["bg"], fg=C["secondary"]).pack()
        tk.Label(center, text="Health Assistant", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack()
        tk.Label(center, text="Your safe space, always with you.",
                 font=FONT_SMALL, bg=C["bg"], fg=C["text_muted"]).pack(pady=(4, 30))

        # ── Login card ────────────────────────────────────────────────────
        card = card_frame(center)
        card.pack(padx=40, pady=10, ipadx=30, ipady=20)

        tk.Label(card, text="Sign In", font=FONT_H2,
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=10, pady=(10, 15))

        tk.Label(card, text="Email", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=10)
        self.email_entry = entry_widget(card)
        self.email_entry.pack(fill="x", padx=10, pady=(0, 12), ipady=6)

        tk.Label(card, text="Password", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=10)
        self.pass_entry = entry_widget(card, show="•")
        self.pass_entry.pack(fill="x", padx=10, pady=(0, 20), ipady=6)

        styled_button(card, "Sign In ➜", self._login, width=28).pack(padx=10, pady=4)

        sep = tk.Frame(card, bg=C["border"], height=1)
        sep.pack(fill="x", padx=10, pady=12)

        tk.Label(card, text="Don't have an account?",
                 bg=C["surface"], fg=C["text_muted"], font=FONT_SMALL).pack()
        styled_button(card, "Create Account", self._go_register,
                      bg=C["surface2"], width=28, pady=6).pack(padx=10, pady=(4, 10))

    def _login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        user = db.login_user(email, password)
        if user:
            self.app.current_user = user
            self.app.show_page("DashboardPage")
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    def _go_register(self):
        self.app.show_page("RegisterPage")


# ══════════════════════════════════════════════════════════════════════════
#  REGISTER PAGE
# ══════════════════════════════════════════════════════════════════════════

class RegisterPage(tk.Frame):
    def __init__(self, parent, app: GirlsSafetyApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        tk.Frame(self, bg=C["primary"], height=6).pack(fill="x")

        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=C["bg"])
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            window_id, width=e.width))

        tk.Label(inner, text="Create Your Account", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack(pady=(30, 20))

        card = card_frame(inner)
        card.pack(padx=60, pady=10, ipadx=20, ipady=20, fill="x")

        fields = [
            ("Full Name *", "name"),
            ("Age", "age"),
            ("Email Address *", "email"),
            ("Password *", "password"),
            ("Blood Group (e.g. A+)", "blood"),
        ]
        self.entries = {}
        for label, key in fields:
            tk.Label(card, text=label, font=FONT_SMALL,
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=10)
            e = entry_widget(card, show="•" if key == "password" else None)
            e.pack(fill="x", padx=10, pady=(0, 10), ipady=6)
            self.entries[key] = e

        styled_button(card, "Register ✓", self._register, width=28).pack(padx=10, pady=10)
        styled_button(card, "← Back to Login", self._back,
                      bg=C["surface2"], width=28, pady=6).pack(padx=10, pady=(0, 10))

    def _register(self):
        name = self.entries["name"].get().strip()
        age  = self.entries["age"].get().strip()
        email = self.entries["email"].get().strip()
        password = self.entries["password"].get().strip()
        blood = self.entries["blood"].get().strip()

        if not name or not email or not password:
            messagebox.showerror("Error", "Name, Email and Password are required.")
            return
        try:
            age_int = int(age) if age else 0
        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")
            return

        success, result = db.register_user(name, age_int, email, password, blood)
        if success:
            messagebox.showinfo("Welcome! 💗", f"Account created for {name}!\nPlease sign in.")
            self.app.show_page("LoginPage")
        else:
            messagebox.showerror("Registration Failed", result)

    def _back(self):
        self.app.show_page("LoginPage")


# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD  (tabbed main screen)
# ══════════════════════════════════════════════════════════════════════════

class DashboardPage(tk.Frame):
    def __init__(self, parent, app: GirlsSafetyApp):
        super().__init__(parent, bg=C["bg"])
        self.app = app

        # Top navigation bar
        self.nav = tk.Frame(self, bg=C["surface"], height=56)
        self.nav.pack(fill="x")
        self.nav.pack_propagate(False)

        tk.Label(self.nav, text="💗 SafeHer", font=FONT_H2,
                 bg=C["surface"], fg=C["primary"]).pack(side="left", padx=20)
        self.welcome_lbl = tk.Label(self.nav, text="", font=FONT_SMALL,
                                    bg=C["surface"], fg=C["text_muted"])
        self.welcome_lbl.pack(side="left", padx=10)

        styled_button(self.nav, "Logout", self.app.logout,
                      bg=C["danger"], width=8, pady=4).pack(side="right", padx=16, pady=10)

        # Tab selector
        self.tab_bar = tk.Frame(self, bg=C["surface2"])
        self.tab_bar.pack(fill="x")

        self.content = tk.Frame(self, bg=C["bg"])
        self.content.pack(fill="both", expand=True)

        # Build all tab panels (lazy – created once)
        self._panels = {}
        self._tab_btns = {}

        tabs = [
            ("🏠 Home",       "home"),
            ("🚨 Safety",     "safety"),
            ("🩺 Health",     "health"),
            ("📍 Location",   "location"),
            ("⏰ Reminders",  "reminders"),
            ("🛡️ Tips",       "tips"),
            ("👤 Profile",    "profile"),
        ]
        for label, key in tabs:
            btn = tk.Button(
                self.tab_bar, text=label, font=FONT_SMALL,
                bg=C["surface2"], fg=C["text_muted"],
                activebackground=C["primary"], activeforeground=C["text"],
                relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                command=lambda k=key: self._switch_tab(k)
            )
            btn.pack(side="left")
            self._tab_btns[key] = btn

        self._active_tab = None

    def on_show(self):
        u = self.app.current_user
        self.welcome_lbl.config(text=f"Hi, {u['name']} 👋")
        # Rebuild panels for fresh data
        for panel in self._panels.values():
            panel.destroy()
        self._panels.clear()
        self._switch_tab("home")

    def _switch_tab(self, key):
        # Highlight active tab
        for k, btn in self._tab_btns.items():
            btn.config(bg=C["primary"] if k == key else C["surface2"],
                       fg=C["text"] if k == key else C["text_muted"])

        if key not in self._panels:
            builders = {
                "home":      self._build_home,
                "safety":    self._build_safety,
                "health":    self._build_health,
                "location":  self._build_location,
                "reminders": self._build_reminders,
                "tips":      self._build_tips,
                "profile":   self._build_profile,
            }
            panel = tk.Frame(self.content, bg=C["bg"])
            builders[key](panel)
            self._panels[key] = panel

        # Hide all, show selected
        for p in self._panels.values():
            p.pack_forget()
        self._panels[key].pack(fill="both", expand=True)
        self._active_tab = key

    # ══════════════════════════
    #  TAB: HOME
    # ══════════════════════════

    def _build_home(self, panel):
        u = self.app.current_user
        uid = u["id"]

        # Scrollable canvas
        canvas = tk.Canvas(panel, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["bg"])
        wid = canvas.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))

        # ── Greeting ──────────────────────────────────────────────────────
        tk.Label(inner, text=f"Good {_greeting()}, {u['name']}! 💗",
                 font=FONT_TITLE, bg=C["bg"], fg=C["secondary"]).pack(anchor="w", padx=30, pady=(20, 4))
        tk.Label(inner, text=datetime.now().strftime("%A, %B %d %Y"),
                 font=FONT_SMALL, bg=C["bg"], fg=C["text_muted"]).pack(anchor="w", padx=32)

        # ── Quick SOS row ─────────────────────────────────────────────────
        sos_card = card_frame(inner, bg=C["danger"])
        sos_card.pack(fill="x", padx=30, pady=(18, 6))
        tk.Label(sos_card, text="🚨  Emergency SOS", font=FONT_H2,
                 bg=C["danger"], fg="white").pack(side="left", padx=20, pady=14)
        styled_button(sos_card, "SEND SOS NOW", lambda: self._trigger_sos(),
                      bg="#CC0000", fg="white", width=16, pady=10,
                      font=("Segoe UI", 11, "bold")).pack(side="right", padx=20, pady=10)

        # ── Cycle status card ─────────────────────────────────────────────
        phase_info = health.get_cycle_phase(uid)
        cycle_card = card_frame(inner)
        cycle_card.pack(fill="x", padx=30, pady=6)
        phase_colors = {"Menstrual": "#FF6B9D", "Follicular": "#6EE7A0",
                        "Ovulation": "#FFD166", "Luteal": "#B980F0", "Unknown": C["text_muted"]}
        pc = phase_colors.get(phase_info["phase"], C["text_muted"])
        tk.Label(cycle_card, text="🩸 Cycle Phase", font=FONT_H3,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16, pady=(12, 0))
        tk.Label(cycle_card, text=f"{phase_info['phase']}  (Day {phase_info['day']})",
                 font=FONT_H2, bg=C["surface"], fg=pc).pack(anchor="w", padx=16)
        tk.Label(cycle_card, text=phase_info["description"], font=FONT_BODY,
                 bg=C["surface"], fg=C["text"], wraplength=600, justify="left"
                 ).pack(anchor="w", padx=16, pady=(2, 12))

        # ── Next period prediction ────────────────────────────────────────
        next_date, note = db.predict_next_cycle(uid)
        pred_card = card_frame(inner)
        pred_card.pack(fill="x", padx=30, pady=6)
        tk.Label(pred_card, text="📅 Next Period Prediction", font=FONT_H3,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16, pady=(12, 0))
        next_text = next_date if next_date else "Log your period to get a prediction"
        tk.Label(pred_card, text=next_text, font=FONT_H2,
                 bg=C["surface"], fg=C["secondary"]).pack(anchor="w", padx=16)
        tk.Label(pred_card, text=note, font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16, pady=(0, 12))

        # ── Daily health tip ──────────────────────────────────────────────
        tip_card = card_frame(inner)
        tip_card.pack(fill="x", padx=30, pady=(6, 20))
        tk.Label(tip_card, text="💡 Today's Health Tip", font=FONT_H3,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16, pady=(12, 0))
        tk.Label(tip_card, text=health.get_daily_tip(), font=FONT_BODY,
                 bg=C["surface"], fg=C["text"], wraplength=600, justify="left"
                 ).pack(anchor="w", padx=16, pady=(2, 12))

    # ══════════════════════════
    #  TAB: SAFETY
    # ══════════════════════════

    def _build_safety(self, panel):
        canvas = _make_scrollable(panel)
        inner = canvas["inner"]
        uid = self.app.current_user["id"]

        tk.Label(inner, text="🚨 Safety Features", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack(anchor="w", padx=30, pady=(20, 4))

        # ── SOS ───────────────────────────────────────────────────────────
        sos_f = card_frame(inner, bg="#3D0A0A")
        sos_f.pack(fill="x", padx=30, pady=8)
        tk.Label(sos_f, text="🚨 Emergency SOS", font=FONT_H2,
                 bg="#3D0A0A", fg="#FF6666").pack(anchor="w", padx=16, pady=(12, 4))
        tk.Label(sos_f, text="Tap the button below to instantly alert all your emergency contacts\n"
                 "with your current location.",
                 font=FONT_BODY, bg="#3D0A0A", fg=C["text"], wraplength=550).pack(anchor="w", padx=16)

        btn_row = tk.Frame(sos_f, bg="#3D0A0A")
        btn_row.pack(padx=16, pady=12)
        styled_button(btn_row, "🚨 SEND SOS ALERT", lambda: self._trigger_sos(),
                      bg=C["danger"], fg="white", width=22,
                      pady=12, font=("Segoe UI", 12, "bold")).pack(side="left", padx=4)
        styled_button(btn_row, "📞 Call Contacts", lambda: self._call_contacts_dialog(),
                      bg="#883300", width=16, pady=12).pack(side="left", padx=4)

        # ── Fake Call ─────────────────────────────────────────────────────
        fake_f = card_frame(inner)
        fake_f.pack(fill="x", padx=30, pady=8)
        tk.Label(fake_f, text="📱 Fake Call", font=FONT_H2,
                 bg=C["surface"], fg=C["secondary"]).pack(anchor="w", padx=16, pady=(12, 4))
        tk.Label(fake_f, text="Simulate an incoming call to exit an uncomfortable situation.",
                 font=FONT_BODY, bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=16)
        styled_button(fake_f, "📲 Trigger Fake Call", self._fake_call,
                      bg=C["surface2"], width=22, pady=8).pack(anchor="w", padx=16, pady=(8, 12))

        # ── Manage Emergency Contacts ─────────────────────────────────────
        cont_f = card_frame(inner)
        cont_f.pack(fill="x", padx=30, pady=8)
        header_row = tk.Frame(cont_f, bg=C["surface"])
        header_row.pack(fill="x", padx=16, pady=(12, 4))
        section_label(header_row, "👥 Emergency Contacts").pack(side="left")
        styled_button(header_row, "+ Add", lambda: self._add_contact_dialog(uid, cont_f),
                      bg=C["primary"], width=8, pady=4).pack(side="right")

        self._contacts_list = tk.Frame(cont_f, bg=C["surface"])
        self._contacts_list.pack(fill="x", padx=16, pady=(0, 12))
        self._refresh_contacts(uid, self._contacts_list)

    def _refresh_contacts(self, uid, frame):
        for w in frame.winfo_children():
            w.destroy()
        contacts = db.get_contacts(uid)
        if not contacts:
            tk.Label(frame, text="No contacts added yet.", font=FONT_SMALL,
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w")
            return
        for c in contacts:
            row = tk.Frame(frame, bg=C["surface2"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"  {c['name']}  |  {c['phone']}  |  {c['relation']}",
                     font=FONT_BODY, bg=C["surface2"], fg=C["text"]).pack(side="left", padx=8, pady=6)
            styled_button(row, "✕", lambda cid=c["id"]: self._delete_contact(uid, cid),
                          bg=C["danger"], width=2, pady=2, font=FONT_SMALL).pack(side="right", padx=6, pady=4)

    def _add_contact_dialog(self, uid, parent_frame):
        win = _dialog_window(self, "Add Emergency Contact")
        fields = {}
        for label, key in [("Name", "name"), ("Phone Number", "phone"), ("Relation (e.g. Mum)", "rel")]:
            tk.Label(win, text=label, font=FONT_SMALL, bg=C["surface"],
                     fg=C["text_muted"]).pack(anchor="w", padx=20, pady=(8, 0))
            e = entry_widget(win)
            e.pack(fill="x", padx=20, pady=(0, 4), ipady=6)
            fields[key] = e

        def save():
            name = fields["name"].get().strip()
            phone = fields["phone"].get().strip()
            rel = fields["rel"].get().strip()
            if not name or not phone:
                messagebox.showerror("Error", "Name and Phone required.", parent=win)
                return
            db.add_contact(uid, name, phone, rel)
            win.destroy()
            self._refresh_contacts(uid, self._contacts_list)

        styled_button(win, "Save Contact", save, width=22).pack(pady=14)

    def _delete_contact(self, uid, contact_id):
        if messagebox.askyesno("Confirm", "Delete this contact?"):
            db.delete_contact(contact_id)
            self._refresh_contacts(uid, self._contacts_list)

    def _trigger_sos(self):
        uid = self.app.current_user["id"]
        name = self.app.current_user["name"]
        loc = safety.get_current_location()
        msg = safety.compose_sos_message(name, loc)
        db.log_sos(uid, loc["latitude"], loc["longitude"], loc["address"])
        contacts = db.get_contacts(uid)

        win = _dialog_window(self, "🚨 SOS ALERT SENT", w=520, h=480)
        win.configure(bg="#1A0000")

        tk.Label(win, text="🚨 SOS ALERT SENT!", font=("Georgia", 18, "bold"),
                 bg="#1A0000", fg=C["danger"]).pack(pady=(20, 8))
        if contacts:
            tk.Label(win, text=f"Alerted {len(contacts)} contact(s):",
                     font=FONT_BODY, bg="#1A0000", fg=C["text"]).pack()
            for c in contacts:
                tk.Label(win, text=f"  📞 {c['name']} ({c['phone']})",
                         font=FONT_SMALL, bg="#1A0000", fg=C["warning"]).pack()
        else:
            tk.Label(win, text="⚠ No contacts added yet!",
                     font=FONT_BODY, bg="#1A0000", fg=C["warning"]).pack()

        tk.Label(win, text="\nMessage that would be sent:",
                 font=FONT_SMALL, bg="#1A0000", fg=C["text_muted"]).pack()
        _, txt = scrollable_text(win, height=10, width=54)
        txt.pack_forget()
        msg_frame, txt2 = scrollable_text(win, height=10)
        msg_frame.pack(padx=20, pady=6, fill="x")
        txt2.insert("1.0", msg)
        txt2.config(state="disabled", bg="#2A0000", fg=C["text"])

        styled_button(win, "Close", win.destroy, bg=C["danger"], width=16).pack(pady=12)

    def _call_contacts_dialog(self):
        uid = self.app.current_user["id"]
        contacts = db.get_contacts(uid)
        if not contacts:
            messagebox.showinfo("No Contacts", "Add emergency contacts first.")
            return
        win = _dialog_window(self, "📞 Call Emergency Contact", w=400, h=320)
        tk.Label(win, text="Select a contact to call:", font=FONT_H3,
                 bg=C["surface"], fg=C["text"]).pack(pady=(16, 8))
        for c in contacts:
            styled_button(win, f"📞 {c['name']}  ({c['phone']})",
                          lambda ph=c["phone"]: messagebox.showinfo(
                              "Calling...",
                              f"Dialing {ph}...\n(In a real device, this would open the phone dialer.)",
                              parent=win),
                          width=28, bg=C["surface2"]).pack(pady=4)

    def _fake_call(self):
        """Simulate a fake incoming call overlay."""
        caller = simpledialog.askstring(
            "Fake Call", "Caller name to display:", initialvalue="Mum", parent=self)
        if not caller:
            return
        win = tk.Toplevel(self)
        win.title("Incoming Call")
        win.geometry("320x400")
        win.configure(bg="#0D1117")
        win.attributes("-topmost", True)
        win.resizable(False, False)

        tk.Label(win, text="📲 Incoming Call", font=FONT_SMALL,
                 bg="#0D1117", fg="#888").pack(pady=(30, 4))
        tk.Label(win, text="📞", font=("Segoe UI Emoji", 60),
                 bg="#0D1117", fg=C["success"]).pack()
        tk.Label(win, text=caller, font=("Georgia", 26, "bold"),
                 bg="#0D1117", fg="white").pack(pady=4)
        tk.Label(win, text="Mobile", font=FONT_SMALL, bg="#0D1117", fg="#888").pack()

        btn_row = tk.Frame(win, bg="#0D1117")
        btn_row.pack(pady=30)
        styled_button(btn_row, "✅ Answer", win.destroy,
                      bg="#22AA55", width=10, pady=12).pack(side="left", padx=16)
        styled_button(btn_row, "❌ Decline", win.destroy,
                      bg=C["danger"], width=10, pady=12).pack(side="left", padx=16)

        # Auto-dismiss after 30 seconds
        win.after(30000, win.destroy)

    # ══════════════════════════
    #  TAB: HEALTH
    # ══════════════════════════

    def _build_health(self, panel):
        canvas = _make_scrollable(panel)
        inner = canvas["inner"]
        uid = self.app.current_user["id"]

        tk.Label(inner, text="🩺 Health Tracking", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack(anchor="w", padx=30, pady=(20, 4))

        # ── Log Period ────────────────────────────────────────────────────
        period_f = card_frame(inner)
        period_f.pack(fill="x", padx=30, pady=8)
        section_label(period_f, "🩸 Log Period").pack(anchor="w", padx=16, pady=(12, 4))

        row1 = tk.Frame(period_f, bg=C["surface"])
        row1.pack(fill="x", padx=16, pady=4)
        tk.Label(row1, text="Start Date (YYYY-MM-DD):", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        start_e = entry_widget(row1)
        start_e.insert(0, date.today().isoformat())
        start_e.pack(side="left", padx=8, ipady=5)

        row2 = tk.Frame(period_f, bg=C["surface"])
        row2.pack(fill="x", padx=16, pady=4)
        tk.Label(row2, text="End Date (optional):      ", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        end_e = entry_widget(row2)
        end_e.pack(side="left", padx=8, ipady=5)

        row3 = tk.Frame(period_f, bg=C["surface"])
        row3.pack(fill="x", padx=16, pady=4)
        tk.Label(row3, text="Cycle Length (days):      ", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        len_e = entry_widget(row3)
        len_e.insert(0, "28")
        len_e.pack(side="left", padx=8, ipady=5)

        def save_period():
            sd = start_e.get().strip()
            ed = end_e.get().strip() or None
            try:
                cl = int(len_e.get().strip())
                datetime.strptime(sd, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return
            db.add_cycle(uid, sd, ed, cl)
            messagebox.showinfo("Saved ✓", "Period logged successfully!")
            # Refresh home if built
            if "home" in self._panels:
                self._panels["home"].destroy()
                del self._panels["home"]

        styled_button(period_f, "Save Period Log", save_period, width=20).pack(anchor="w", padx=16, pady=10)

        # ── Log Symptoms ──────────────────────────────────────────────────
        sym_f = card_frame(inner)
        sym_f.pack(fill="x", padx=30, pady=8)
        section_label(sym_f, "📋 Log Today's Symptoms").pack(anchor="w", padx=16, pady=(12, 4))

        checks = {}
        for sym in ["Headache", "Cramps", "Fatigue", "Bloating"]:
            var = tk.IntVar()
            cb = tk.Checkbutton(sym_f, text=sym, variable=var, font=FONT_BODY,
                                bg=C["surface"], fg=C["text"], selectcolor=C["primary"],
                                activebackground=C["surface"])
            cb.pack(anchor="w", padx=16)
            checks[sym.lower()] = var

        tk.Label(sym_f, text="Mood:", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16, pady=(8, 0))
        mood_var = tk.StringVar(value=health.MOOD_OPTIONS[0])
        mood_menu = tk.OptionMenu(sym_f, mood_var, *health.MOOD_OPTIONS)
        mood_menu.config(bg=C["surface2"], fg=C["text"], activebackground=C["primary"],
                         font=FONT_BODY, relief="flat", bd=0)
        mood_menu.pack(anchor="w", padx=16, pady=4)

        tk.Label(sym_f, text="Notes:", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16)
        sym_notes = tk.Text(sym_f, height=3, bg=C["surface2"], fg=C["text"],
                            font=FONT_BODY, relief="flat", bd=0,
                            highlightthickness=1, highlightbackground=C["border"])
        sym_notes.pack(fill="x", padx=16, pady=4)

        def save_symptoms():
            db.add_symptom_log(
                uid, date.today().isoformat(),
                headache=checks["headache"].get(),
                cramps=checks["cramps"].get(),
                fatigue=checks["fatigue"].get(),
                bloating=checks["bloating"].get(),
                mood=mood_var.get(),
                notes=sym_notes.get("1.0", "end").strip()
            )
            messagebox.showinfo("Saved ✓", "Symptoms logged!")

        styled_button(sym_f, "Save Symptoms", save_symptoms, width=20).pack(anchor="w", padx=16, pady=10)

        # ── Symptom analysis ──────────────────────────────────────────────
        analysis_f = card_frame(inner)
        analysis_f.pack(fill="x", padx=30, pady=8)
        section_label(analysis_f, "📊 Symptom Analysis").pack(anchor="w", padx=16, pady=(12, 4))
        analysis_txt = tk.Label(analysis_f, text=health.analyze_symptoms(uid),
                                font=FONT_BODY, bg=C["surface"], fg=C["text"],
                                justify="left", wraplength=600)
        analysis_txt.pack(anchor="w", padx=16, pady=(0, 12))

        # ── Medical Notes ─────────────────────────────────────────────────
        notes_f = card_frame(inner)
        notes_f.pack(fill="x", padx=30, pady=(8, 20))
        header_row = tk.Frame(notes_f, bg=C["surface"])
        header_row.pack(fill="x", padx=16, pady=(12, 4))
        section_label(header_row, "📝 Medical History Notes").pack(side="left")
        styled_button(header_row, "+ Add Note",
                      lambda: self._add_note_dialog(uid, self._notes_list),
                      bg=C["primary"], width=10, pady=4).pack(side="right")

        self._notes_list = tk.Frame(notes_f, bg=C["surface"])
        self._notes_list.pack(fill="x", padx=16, pady=(0, 12))
        self._refresh_notes(uid, self._notes_list)

    def _refresh_notes(self, uid, frame):
        for w in frame.winfo_children():
            w.destroy()
        notes = db.get_medical_notes(uid)
        if not notes:
            tk.Label(frame, text="No medical notes yet.", font=FONT_SMALL,
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w")
            return
        for n in notes:
            nf = tk.Frame(frame, bg=C["surface2"])
            nf.pack(fill="x", pady=3)
            tk.Label(nf, text=f"  📌 {n['title']}  —  {n['created_at'][:10]}",
                     font=FONT_BODY, bg=C["surface2"], fg=C["secondary"]).pack(side="left", padx=8, pady=4)
            styled_button(nf, "View", lambda c=n["content"], t=n["title"]: messagebox.showinfo(t, c),
                          bg=C["surface"], width=5, pady=2).pack(side="right", padx=2)
            styled_button(nf, "✕", lambda nid=n["id"]: (
                db.delete_medical_note(nid), self._refresh_notes(uid, frame)),
                bg=C["danger"], width=2, pady=2).pack(side="right", padx=2)

    def _add_note_dialog(self, uid, frame):
        win = _dialog_window(self, "Add Medical Note", w=440, h=340)
        tk.Label(win, text="Title:", font=FONT_SMALL, bg=C["surface"],
                 fg=C["text_muted"]).pack(anchor="w", padx=20, pady=(12, 0))
        title_e = entry_widget(win)
        title_e.pack(fill="x", padx=20, ipady=6)
        tk.Label(win, text="Content:", font=FONT_SMALL, bg=C["surface"],
                 fg=C["text_muted"]).pack(anchor="w", padx=20, pady=(10, 0))
        content_t = tk.Text(win, height=7, bg=C["surface2"], fg=C["text"],
                            font=FONT_BODY, relief="flat")
        content_t.pack(fill="x", padx=20, pady=4)

        def save():
            t = title_e.get().strip()
            c = content_t.get("1.0", "end").strip()
            if not t:
                messagebox.showerror("Error", "Title required.", parent=win)
                return
            db.add_medical_note(uid, t, c)
            win.destroy()
            self._refresh_notes(uid, frame)

        styled_button(win, "Save Note", save, width=20).pack(pady=10)

    # ══════════════════════════
    #  TAB: LOCATION
    # ══════════════════════════

    def _build_location(self, panel):
        uid = self.app.current_user["id"]
        name = self.app.current_user["name"]

        inner = tk.Frame(panel, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(inner, text="📍 Location Tracking", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack(anchor="w", pady=(0, 16))

        loc_card = card_frame(inner)
        loc_card.pack(fill="x", pady=8)

        tk.Label(loc_card, text="Current Location", font=FONT_H2,
                 bg=C["surface"], fg=C["secondary"]).pack(anchor="w", padx=16, pady=(12, 4))
        self._loc_label = tk.Label(loc_card, text="Tap 'Get Location' to fetch your position.",
                                   font=FONT_BODY, bg=C["surface"], fg=C["text"],
                                   wraplength=600, justify="left")
        self._loc_label.pack(anchor="w", padx=16, pady=(0, 12))

        btn_row = tk.Frame(loc_card, bg=C["surface"])
        btn_row.pack(padx=16, pady=(0, 12))
        styled_button(btn_row, "📍 Get My Location", self._fetch_location,
                      width=20).pack(side="left", padx=4)
        styled_button(btn_row, "📤 Share with Contacts",
                      lambda: self._share_location(uid, name),
                      bg=C["surface2"], width=22).pack(side="left", padx=4)

        # ── Location History ──────────────────────────────────────────────
        hist_card = card_frame(inner)
        hist_card.pack(fill="x", pady=8)
        tk.Label(hist_card, text="ℹ️  About Location Tracking", font=FONT_H3,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16, pady=(12, 4))
        tk.Label(hist_card, text=(
            "• Location is simulated in this desktop app.\n"
            "• On a real device/mobile, this would use GPS or IP-based geolocation.\n"
            "• You can integrate 'geopy' or 'gpsd' library for real GPS coordinates.\n"
            "• Sharing sends the message to your emergency contacts via SMS or WhatsApp."
        ), font=FONT_BODY, bg=C["surface"], fg=C["text"], justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 12))

    def _fetch_location(self):
        loc = safety.get_current_location()
        self._loc_label.config(
            text=f"📍 {loc['address']}\n"
                 f"🌐 Coordinates: {loc['latitude']}, {loc['longitude']}\n"
                 f"🔗 Maps: {loc['maps_link']}\n"
                 f"⏰ Updated: {loc['timestamp']}"
        )

    def _share_location(self, uid, name):
        loc = safety.get_current_location()
        msg = safety.compose_share_location_message(name, loc)
        contacts = db.get_contacts(uid)
        if not contacts:
            messagebox.showinfo("No Contacts", "Please add emergency contacts first.")
            return
        names = ", ".join(c["name"] for c in contacts)
        messagebox.showinfo(
            "Location Shared",
            f"Location sent to: {names}\n\nMessage:\n{msg}"
        )

    # ══════════════════════════
    #  TAB: REMINDERS
    # ══════════════════════════

    def _build_reminders(self, panel):
        uid = self.app.current_user["id"]

        canvas = _make_scrollable(panel)
        inner = canvas["inner"]

        tk.Label(inner, text="⏰ Reminders", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack(anchor="w", padx=30, pady=(20, 4))

        # ── Add Reminder ──────────────────────────────────────────────────
        add_f = card_frame(inner)
        add_f.pack(fill="x", padx=30, pady=8)
        section_label(add_f, "➕ Set New Reminder").pack(anchor="w", padx=16, pady=(12, 4))

        row1 = tk.Frame(add_f, bg=C["surface"])
        row1.pack(fill="x", padx=16, pady=4)
        tk.Label(row1, text="Type:", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        rtype = tk.StringVar(value="Period")
        type_menu = tk.OptionMenu(row1, rtype,
                                  "Period", "Medication", "Health Checkup",
                                  "Vitamins", "Exercise", "Other")
        type_menu.config(bg=C["surface2"], fg=C["text"], font=FONT_BODY, relief="flat")
        type_menu.pack(side="left", padx=8)

        row2 = tk.Frame(add_f, bg=C["surface"])
        row2.pack(fill="x", padx=16, pady=4)
        tk.Label(row2, text="Date (YYYY-MM-DD):", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        date_e = entry_widget(row2)
        date_e.insert(0, date.today().isoformat())
        date_e.pack(side="left", padx=8, ipady=5)

        tk.Label(add_f, text="Message:", font=FONT_SMALL,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16)
        msg_e = entry_widget(add_f)
        msg_e.pack(fill="x", padx=16, pady=4, ipady=6)

        def save_reminder():
            try:
                datetime.strptime(date_e.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date. Use YYYY-MM-DD.")
                return
            db.add_reminder(uid, rtype.get(), msg_e.get().strip(), date_e.get().strip())
            messagebox.showinfo("Saved ✓", "Reminder set!")
            # Refresh list
            self._refresh_reminders(uid, self._rem_list)

        styled_button(add_f, "Set Reminder ✓", save_reminder, width=20).pack(anchor="w", padx=16, pady=10)

        # ── Upcoming Reminders ────────────────────────────────────────────
        list_f = card_frame(inner)
        list_f.pack(fill="x", padx=30, pady=(8, 20))
        section_label(list_f, "📋 Upcoming Reminders").pack(anchor="w", padx=16, pady=(12, 4))
        self._rem_list = tk.Frame(list_f, bg=C["surface"])
        self._rem_list.pack(fill="x", padx=16, pady=(0, 12))
        self._refresh_reminders(uid, self._rem_list)

    def _refresh_reminders(self, uid, frame):
        for w in frame.winfo_children():
            w.destroy()
        reminders = db.get_reminders(uid)
        if not reminders:
            tk.Label(frame, text="No upcoming reminders.", font=FONT_SMALL,
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w")
            return
        for r in reminders:
            rf = tk.Frame(frame, bg=C["surface2"])
            rf.pack(fill="x", pady=3)
            tk.Label(rf, text=f"  {r['reminder_type']}  |  {r['remind_date']}  |  {r['message']}",
                     font=FONT_BODY, bg=C["surface2"], fg=C["text"]).pack(side="left", padx=8, pady=6)
            styled_button(rf, "✓ Done",
                          lambda rid=r["id"]: (db.mark_reminder_done(rid),
                                               self._refresh_reminders(uid, frame)),
                          bg=C["success"], width=7, pady=2).pack(side="right", padx=6)

    # ══════════════════════════
    #  TAB: TIPS
    # ══════════════════════════

    def _build_tips(self, panel):
        canvas = _make_scrollable(panel)
        inner = canvas["inner"]

        tk.Label(inner, text="🛡️ Safety Tips & Helplines", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack(anchor="w", padx=30, pady=(20, 4))

        # ── Self-defense tips ─────────────────────────────────────────────
        for tip in safety.SELF_DEFENSE_TIPS:
            tf = card_frame(inner)
            tf.pack(fill="x", padx=30, pady=5)
            tk.Label(tf, text=f"{tip['icon']}  {tip['title']}", font=FONT_H3,
                     bg=C["surface"], fg=C["secondary"]).pack(anchor="w", padx=16, pady=(10, 2))
            tk.Label(tf, text=tip["tip"], font=FONT_BODY, bg=C["surface"], fg=C["text"],
                     wraplength=600, justify="left").pack(anchor="w", padx=16, pady=(0, 10))

        # ── Safety guidelines ─────────────────────────────────────────────
        sg_f = card_frame(inner)
        sg_f.pack(fill="x", padx=30, pady=8)
        section_label(sg_f, "📜 Quick Safety Rules").pack(anchor="w", padx=16, pady=(12, 4))
        for g in safety.SAFETY_GUIDELINES:
            tk.Label(sg_f, text=g, font=FONT_BODY, bg=C["surface"], fg=C["text"],
                     anchor="w").pack(anchor="w", padx=16, pady=1)
        tk.Label(sg_f, text="").pack()

        # ── Helplines ─────────────────────────────────────────────────────
        hl_f = card_frame(inner)
        hl_f.pack(fill="x", padx=30, pady=(8, 20))
        section_label(hl_f, "📞 Emergency Helplines").pack(anchor="w", padx=16, pady=(12, 4))
        for h_line in safety.HELPLINES:
            row = tk.Frame(hl_f, bg=C["surface"])
            row.pack(fill="x", padx=16, pady=2)
            tk.Label(row, text=f"  📞 {h_line['name']}", font=FONT_BODY,
                     bg=C["surface"], fg=C["text"]).pack(side="left")
            tk.Label(row, text=h_line["number"], font=FONT_H3,
                     bg=C["surface"], fg=C["warning"]).pack(side="right")
        tk.Label(hl_f, text="").pack()

    # ══════════════════════════
    #  TAB: PROFILE
    # ══════════════════════════

    def _build_profile(self, panel):
        u = self.app.current_user
        uid = u["id"]

        inner = tk.Frame(panel, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(inner, text="👤 My Profile", font=FONT_TITLE,
                 bg=C["bg"], fg=C["primary"]).pack(anchor="w", pady=(0, 16))

        card = card_frame(inner)
        card.pack(fill="x", pady=8)

        tk.Label(card, text=f"👤  {u['name']}", font=FONT_H2,
                 bg=C["surface"], fg=C["secondary"]).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(card, text=f"✉️  {u['email']}", font=FONT_BODY,
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=16)
        tk.Label(card, text=f"🎂  Age: {u.get('age', '—')}  |  🩸 Blood Group: {u.get('blood_group','—')}",
                 font=FONT_BODY, bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=16, pady=(2, 12))

        # ── Edit profile ──────────────────────────────────────────────────
        edit_f = card_frame(inner)
        edit_f.pack(fill="x", pady=8)
        section_label(edit_f, "✏️ Edit Profile").pack(anchor="w", padx=16, pady=(12, 8))

        fields_cfg = [("Full Name", "name"), ("Age", "age"), ("Blood Group", "blood_group")]
        edit_entries = {}
        for label, key in fields_cfg:
            tk.Label(edit_f, text=label, font=FONT_SMALL,
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16)
            e = entry_widget(edit_f)
            e.insert(0, str(u.get(key, "")))
            e.pack(fill="x", padx=16, pady=(0, 8), ipady=6)
            edit_entries[key] = e

        def save_profile():
            name = edit_entries["name"].get().strip()
            try:
                age = int(edit_entries["age"].get().strip() or 0)
            except ValueError:
                messagebox.showerror("Error", "Age must be a number.")
                return
            blood = edit_entries["blood_group"].get().strip()
            db.update_user(uid, name, age, blood)
            self.app.current_user = db.get_user(uid)
            messagebox.showinfo("Saved ✓", "Profile updated successfully!")
            self.welcome_lbl.config(text=f"Hi, {name} 👋")

        styled_button(edit_f, "Save Changes ✓", save_profile, width=20).pack(anchor="w", padx=16, pady=(4, 14))

        # ── App info ──────────────────────────────────────────────────────
        info_f = card_frame(inner)
        info_f.pack(fill="x", pady=(8, 0))
        tk.Label(info_f, text="ℹ️  App Info", font=FONT_H3,
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=16, pady=(12, 4))
        tk.Label(info_f, text=(
            "Girls Safety & Health Assistant  v1.0\n"
            "Built with Python + Tkinter + SQLite\n"
            "Your data is stored locally on your device.\n"
            "No data is sent to any server."
        ), font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"], justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 12))


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════

def _greeting():
    h = datetime.now().hour
    if h < 12:
        return "morning"
    elif h < 17:
        return "afternoon"
    return "evening"


def _make_scrollable(parent):
    canvas = tk.Canvas(parent, bg=C["bg"], highlightthickness=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)
    inner = tk.Frame(canvas, bg=C["bg"])
    wid = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
    # Mouse wheel scrolling
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    return {"canvas": canvas, "inner": inner}


def _dialog_window(parent, title, w=460, h=400):
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry(f"{w}x{h}")
    win.configure(bg=C["surface"])
    win.resizable(False, False)
    win.grab_set()
    tk.Label(win, text=title, font=FONT_H2, bg=C["surface"],
             fg=C["primary"]).pack(pady=(14, 4))
    tk.Frame(win, bg=C["border"], height=1).pack(fill="x", padx=16)
    return win


# ══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = GirlsSafetyApp()
    app.mainloop()
