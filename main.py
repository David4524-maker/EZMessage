# -*- coding: utf-8 -*-
"""
============================================================
  EZMessage · Mensajería local con Cuenta David + EZPack AI
============================================================
  Cómo usar:
    1. Abre este archivo en IDLE (Python 3.14) y pulsa F5.
    2. Inicia sesión con tu Cuenta David o crea una nueva.
    3. Chatea con las demás Cuentas David del mismo equipo.
    4. Pulsa "🤖 Asistente AI" para abrir EZPack AI en el
       navegador con el proveedor (ChatGPT/Gemini/Claude/...)
       que hayas elegido en Ajustes.

  Requiere en la misma carpeta:
    · ezpack.html         (el asistente de IA que corre en navegador)

  Archivos que se crean solos:
    · david_accounts.json     -> cuentas David
    · ezmessage_chats.json    -> historial de mensajes
    · ezmessage_config.json   -> ajustes (proveedor IA elegido)
============================================================
"""

import datetime
import hashlib
import json
import os
import uuid
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

# ------------------------------------------------------------
#  Rutas
# ------------------------------------------------------------
APP_DIR       = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(APP_DIR, "david_accounts.json")
CHATS_FILE    = os.path.join(APP_DIR, "ezmessage_chats.json")
CONFIG_FILE   = os.path.join(APP_DIR, "ezmessage_config.json")
EZPACK_HTML   = os.path.join(APP_DIR, "ezpack.html")

# ------------------------------------------------------------
#  Proveedores de IA
# ------------------------------------------------------------
AI_PROVIDERS = ["EZPack Local", "ChatGPT", "Gemini", "Claude", "DeepSeek", "Grok"]

AI_PROVIDER_URLS = {
    "ChatGPT":  "https://chatgpt.com/",
    "Gemini":   "https://gemini.google.com/app",
    "Claude":   "https://claude.ai/new",
    "DeepSeek": "https://chat.deepseek.com/",
    "Grok":     "https://grok.com/",
}

# ------------------------------------------------------------
#  Paleta y fuentes
# ------------------------------------------------------------
BG        = "#0b1220"
PANEL     = "#101a2b"
CARD      = "#16233a"
CARD_H    = "#1e2d49"
BORDER    = "#243553"
ACCENT    = "#2563eb"
ACCENT_H  = "#1d4ed8"
TEXT      = "#e9effb"
MUTED     = "#8ea3c4"
DANGER    = "#ef4444"
DANGER_H  = "#dc2626"
PURPLE    = "#8b5cf6"
PURPLE_H  = "#7c3aed"
SUCCESS   = "#10b981"
AI_COL    = "#14b8a6"
AI_COL_H  = "#0d9488"
BUBBLE_ME = "#2563eb"
BUBBLE_OT = "#1e2d49"

F_TITLE = ("Segoe UI", 20, "bold")
F_H1    = ("Segoe UI", 15, "bold")
F_H2    = ("Segoe UI", 11, "bold")
F_BODY  = ("Segoe UI", 10)
F_BOLD  = ("Segoe UI", 10, "bold")
F_SMALL = ("Segoe UI", 9)
F_TINY  = ("Segoe UI", 8)
F_INPUT = ("Segoe UI", 11)

AVATAR_COLORS = ["#2563eb", "#8b5cf6", "#ec4899", "#f59e0b",
                 "#10b981", "#06b6d4", "#ef4444", "#6366f1"]

# ------------------------------------------------------------
#  Utilidades
# ------------------------------------------------------------
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except OSError as e:
        messagebox.showerror("EZMessage", f"No se pudo guardar:\n{e}")
        return False


def sha256(txt):
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def fmt_time(iso):
    try:
        dt = datetime.datetime.fromisoformat(iso)
    except Exception:
        return ""
    today = datetime.date.today()
    if dt.date() == today:
        return dt.strftime("%H:%M")
    if dt.date() == today - datetime.timedelta(days=1):
        return "Ayer " + dt.strftime("%H:%M")
    return dt.strftime("%d/%m %H:%M")


def initials(name):
    parts = [p for p in str(name).replace("_", " ").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def color_for(name):
    h = sum(ord(c) for c in str(name).lower())
    return AVATAR_COLORS[h % len(AVATAR_COLORS)]


def make_avatar(parent, name, size=42, bg=CARD):
    c = tk.Canvas(parent, width=size, height=size, bg=bg,
                  highlightthickness=0, bd=0)
    c.create_oval(0, 0, size - 1, size - 1, fill=color_for(name), outline="")
    c.create_text(size / 2, size / 2 + 1, text=initials(name),
                  fill="white", font=("Segoe UI", max(8, int(size * 0.36)), "bold"))
    return c


def set_bg_recursive(widget, color):
    try:
        widget.configure(bg=color)
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        set_bg_recursive(child, color)


def make_entry(parent, show=None):
    return tk.Entry(parent, bg=CARD, fg=TEXT, insertbackground=TEXT,
                    relief="flat", bd=0, font=F_INPUT,
                    highlightthickness=1, highlightbackground=BORDER,
                    highlightcolor=ACCENT, show=show)


def field(parent, label, bg=PANEL, show=None):
    tk.Label(parent, text=label, bg=bg, fg=MUTED, font=F_SMALL,
             anchor="w").pack(fill="x", pady=(10, 3))
    e = make_entry(parent, show=show)
    e.pack(fill="x", ipady=7)
    return e


# ------------------------------------------------------------
#  Widgets reutilizables
# ------------------------------------------------------------
class HoverButton(tk.Button):
    def __init__(self, parent, *, normal_bg, hover_bg, fg=TEXT, hover_fg=None, **kw):
        kw.setdefault("relief", "flat")
        kw.setdefault("bd", 0)
        kw.setdefault("cursor", "hand2")
        kw.setdefault("font", F_BOLD)
        kw.setdefault("activeforeground", fg)
        super().__init__(parent, bg=normal_bg, fg=fg,
                         activebackground=hover_bg, **kw)
        self._n, self._h = normal_bg, hover_bg
        self._fg, self._hfg = fg, hover_fg or fg
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)

    def _enter(self, _=None):
        if str(self["state"]) != "disabled":
            self.configure(bg=self._h, fg=self._hfg)

    def _leave(self, _=None):
        if str(self["state"]) != "disabled":
            self.configure(bg=self._n, fg=self._fg)


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)

    def _on_inner(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas(self, e):
        self.canvas.itemconfigure(self._win, width=e.width)

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()

    def to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)


# ============================================================
#  Aplicación principal
# ============================================================
class EZMessage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EZMessage · Cuenta David · EZPack AI")
        self.geometry("1000x660")
        self.minsize(880, 580)
        self.configure(bg=BG)

        self.accounts = load_json(ACCOUNTS_FILE, {})
        self.chats    = load_json(CHATS_FILE, {"messages": []})
        self.config   = load_json(CONFIG_FILE, {"ai_provider": "EZPack Local"})
        self.current_user = None

        self._setup_style()

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for Cls in (LoginFrame, RegisterFrame, ChatFrame):
            f = Cls(self.container, self)
            f.grid(row=0, column=0, sticky="nsew")
            self.frames[Cls.__name__] = f

        self.bind_all("<MouseWheel>", self._on_wheel)
        self.bind_all("<Button-4>", lambda e: self._on_wheel(e, linux=-1))
        self.bind_all("<Button-5>", lambda e: self._on_wheel(e, linux=1))

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show("LoginFrame")

    # --------------------------------------------------------
    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Dark.TCombobox",
                        fieldbackground=CARD, background=CARD, foreground=TEXT,
                        arrowcolor=TEXT, bordercolor=BORDER,
                        lightcolor=CARD, darkcolor=CARD, relief="flat")
        style.map("Dark.TCombobox",
                  fieldbackground=[("readonly", CARD)],
                  foreground=[("readonly", TEXT)],
                  selectbackground=[("readonly", CARD)],
                  selectforeground=[("readonly", TEXT)])
        self.option_add("*TCombobox*Listbox.background", CARD)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", "white")

    def _on_wheel(self, event, linux=None):
        w = event.widget
        while w is not None:
            if isinstance(w, ScrollFrame):
                if linux is not None:
                    w.canvas.yview_scroll(linux, "units")
                else:
                    w.canvas.yview_scroll(int(-event.delta / 120), "units")
                return
            w = getattr(w, "master", None)

    def show(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    # --------------------------------------------------------
    def reload_accounts(self):
        self.accounts = load_json(ACCOUNTS_FILE, {})
        return self.accounts

    def save_accounts(self):
        return save_json(ACCOUNTS_FILE, self.accounts)

    def reload_chats(self):
        self.chats = load_json(CHATS_FILE, {"messages": []})
        return self.chats

    def save_config(self):
        return save_json(CONFIG_FILE, self.config)

    # --------------------------------------------------------
    def login(self, username):
        self.current_user = username.lower()
        self.show("ChatFrame")

    def logout(self):
        self.current_user = None
        self.show("LoginFrame")

    def delete_my_account(self):
        if not self.current_user:
            return
        name = self.display_name(self.current_user)
        if not messagebox.askyesno(
                "Eliminar cuenta",
                f"¿Seguro que quieres eliminar la Cuenta David «{name}»?\n\n"
                "También se borrarán todos tus mensajes."):
            return

        self.reload_accounts()
        self.accounts.pop(self.current_user, None)
        self.save_accounts()

        self.reload_chats()
        me = self.current_user
        self.chats["messages"] = [
            m for m in self.chats.get("messages", [])
            if m.get("from", "").lower() != me and m.get("to", "").lower() != me
        ]
        save_json(CHATS_FILE, self.chats)

        self.current_user = None
        self.show("LoginFrame")

    # --------------------------------------------------------
    def display_name(self, key):
        acc = self.accounts.get(key.lower())
        if acc:
            return acc.get("username", key)
        return key[:1].upper() + key[1:]

    def account_type(self, key):
        acc = self.accounts.get(key.lower())
        return acc.get("type", "externo") if acc else "externo"

    # --------------------------------------------------------
    #  🧠 EZPack AI · Integración con el navegador
    # --------------------------------------------------------
    def ai_provider(self):
        return self.config.get("ai_provider", "EZPack Local")

    def open_ai_assistant(self):
        """Abre el EZPack AI (HTML) en el navegador con el proveedor elegido."""
        if not os.path.isfile(EZPACK_HTML):
            messagebox.showwarning(
                "EZMessage · EZPack AI",
                "No encuentro el archivo ezpack.html en la carpeta de la app.\n\n"
                f"Guárdalo en:\n{EZPACK_HTML}\n\n"
                "Después vuelve a intentarlo.")
            return
        provider = self.ai_provider()
        url = "file:///" + EZPACK_HTML.replace("\\", "/")
        # Pasa el proveedor seleccionado al HTML (lo leerá vía URLSearchParams)
        from urllib.parse import quote
        url += "?ai=" + quote(provider)
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("EZMessage", f"No se pudo abrir el navegador:\n{e}")

    def open_ai_provider_web(self):
        """Abre directamente la web del proveedor de IA elegido."""
        provider = self.ai_provider()
        url = AI_PROVIDER_URLS.get(provider)
        if not url:
            messagebox.showinfo(
                "EZMessage · EZPack AI",
                "«EZPack Local» funciona sin conexión dentro del propio asistente.\n\n"
                "Pulsa «🤖 Asistente AI» para abrirlo en el navegador.")
            return
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("EZMessage", f"No se pudo abrir el navegador:\n{e}")

    def open_ai_settings(self):
        """Ventana de configuración de proveedor de IA."""
        dlg = tk.Toplevel(self)
        dlg.title("Configurar IA · EZMessage")
        dlg.configure(bg=PANEL)
        dlg.geometry("420x340")
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        dlg.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 420) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 340) // 2
        dlg.geometry(f"+{max(0, x)}+{max(0, y)}")

        tk.Label(dlg, text="🤖 Configurar Asistente IA", bg=PANEL, fg=TEXT,
                 font=F_H1).pack(anchor="w", padx=22, pady=(20, 2))
        tk.Label(dlg, text="Elige qué IA usarás desde EZMessage.\n"
                            "EZPack AI la abrirá en tu navegador.",
                 bg=PANEL, fg=MUTED, font=F_SMALL, justify="left"
                 ).pack(anchor="w", padx=22, pady=(0, 14))

        tk.Label(dlg, text="Proveedor de IA", bg=PANEL, fg=MUTED,
                 font=F_SMALL, anchor="w").pack(fill="x", padx=22, pady=(4, 3))

        var = tk.StringVar(value=self.ai_provider())
        cb = ttk.Combobox(dlg, textvariable=var, values=AI_PROVIDERS,
                          state="readonly", style="Dark.TCombobox",
                          font=F_INPUT)
        cb.pack(fill="x", padx=22, ipady=5)

        info_lbl = tk.Label(dlg, text="", bg=PANEL, fg=MUTED, font=F_TINY,
                             wraplength=360, justify="left")
        info_lbl.pack(fill="x", padx=22, pady=(10, 0))

        def actualizar_info(*_):
            p = var.get()
            url = AI_PROVIDER_URLS.get(p)
            if url:
                info_lbl.configure(text=f"🌐 Web: {url}")
            else:
                info_lbl.configure(text="🏠 Corre 100% offline en tu navegador. Sin servidores.")
        var.trace_add("write", actualizar_info)
        actualizar_info()

        def guardar():
            self.config["ai_provider"] = var.get()
            self.save_config()
            dlg.destroy()
            messagebox.showinfo("EZMessage",
                                f"Proveedor IA guardado: {var.get()}\n\n"
                                "Pulsa «🤖 Asistente AI» para usarlo.")

        HoverButton(dlg, text="Guardar",
                    normal_bg=ACCENT, hover_bg=ACCENT_H,
                    command=guardar, pady=9).pack(fill="x", padx=22, pady=(20, 6))

        HoverButton(dlg, text="Cancelar",
                    normal_bg=PANEL, hover_bg=CARD, fg=TEXT,
                    command=dlg.destroy, pady=8).pack(fill="x", padx=22)
        dlg.winfo_children()[-1].configure(highlightthickness=1,
                                             highlightbackground=BORDER,
                                             highlightcolor=BORDER)

    def _on_close(self):
        try:
            self.destroy()
        except tk.TclError:
            pass


# ============================================================
#  VISTA 1 · INICIAR SESIÓN
# ============================================================
class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(wrap, bg=PANEL, padx=34, pady=28,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack()

        brand = tk.Frame(card, bg=PANEL)
        brand.pack(fill="x", pady=(0, 4))
        logo = tk.Canvas(brand, width=44, height=44, bg=PANEL,
                         highlightthickness=0, bd=0)
        logo.pack(side="left")
        logo.create_oval(0, 0, 43, 43, fill=ACCENT, outline="")
        logo.create_text(22, 22, text="EZ", fill="white",
                         font=("Segoe UI", 14, "bold"))

        tbox = tk.Frame(brand, bg=PANEL)
        tbox.pack(side="left", padx=12)
        tk.Label(tbox, text="EZMessage", bg=PANEL, fg=TEXT,
                 font=F_TITLE, anchor="w").pack(fill="x")
        tk.Label(tbox, text="Mensajería con Cuenta David + EZPack AI", bg=PANEL,
                 fg=MUTED, font=F_TINY, anchor="w").pack(fill="x")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=(18, 14))

        self.acc_header = tk.Label(card, text="CUENTAS GUARDADAS", bg=PANEL,
                                   fg=MUTED, font=("Segoe UI", 8, "bold"),
                                   anchor="w")
        self.acc_header.pack(fill="x")

        self.acc_list = tk.Frame(card, bg=PANEL)
        self.acc_list.pack(fill="x", pady=(8, 4))

        self.user_entry = field(card, "Usuario")
        self.pass_entry = field(card, "Contraseña", show="•")

        self.pass_entry.bind("<Return>", lambda e: self._do_login())
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus_set())

        self.btn_login = HoverButton(
            card, text="Entrar", normal_bg=ACCENT, hover_bg=ACCENT_H,
            command=self._do_login, pady=10)
        self.btn_login.pack(fill="x", pady=(18, 0))

        self.btn_create = HoverButton(
            card, text="Crear Cuenta David",
            normal_bg=PANEL, hover_bg=CARD, fg=TEXT,
            command=lambda: self.app.show("RegisterFrame"), pady=9)
        self.btn_create.pack(fill="x", pady=(8, 0))
        self.btn_create.configure(highlightthickness=1,
                                  highlightbackground=BORDER,
                                  highlightcolor=BORDER)

        tk.Label(card, text="Los datos se guardan localmente en david_accounts.json",
                 bg=PANEL, fg="#5b7295", font=F_TINY,
                 wraplength=330, justify="center").pack(pady=(16, 0))

    def on_show(self):
        self.app.reload_accounts()
        self.pass_entry.delete(0, "end")
        self._render_accounts()

    def _render_accounts(self):
        for w in self.acc_list.winfo_children():
            w.destroy()

        accounts = self.app.accounts
        if not accounts:
            tk.Label(self.acc_list,
                     text="No hay cuentas guardadas aún. Crea una 👇",
                     bg=PANEL, fg=MUTED, font=F_SMALL).pack(pady=6)
            return

        for key, acc in sorted(accounts.items()):
            is_kid = acc.get("type") == "kid"
            row = tk.Frame(self.acc_list, bg=CARD, cursor="hand2",
                           highlightthickness=1, highlightbackground=BORDER)
            row.pack(fill="x", pady=3)

            av = make_avatar(row, acc.get("username", key), 32, CARD)
            av.pack(side="left", padx=(10, 8), pady=8)

            info = tk.Frame(row, bg=CARD)
            info.pack(side="left", fill="x", expand=True, pady=6)
            tk.Label(info, text=acc.get("username", key), bg=CARD, fg=TEXT,
                     font=F_BOLD, anchor="w").pack(fill="x")
            sub = "Cuenta Infantil" if is_kid else acc.get("email", "Cuenta normal")
            tk.Label(info, text=sub, bg=CARD, fg=MUTED, font=F_TINY,
                     anchor="w").pack(fill="x")

            tag_color = "#fce7f3" if is_kid else "#1e3a8a"
            tag_fg = "#9d174d" if is_kid else "#93c5fd"
            tk.Label(row, text="Niño/a" if is_kid else "Normal",
                     bg=tag_color, fg=tag_fg, font=("Segoe UI", 8, "bold"),
                     padx=7, pady=2).pack(side="right", padx=(0, 10))

            def pick(_e, k=key):
                self.user_entry.delete(0, "end")
                self.user_entry.insert(0, self.app.accounts[k].get("username", k))
                self.pass_entry.focus_set()

            def hover_in(_e, r=row):
                set_bg_recursive(r, CARD_H)

            def hover_out(_e, r=row):
                set_bg_recursive(r, CARD)

            def bind_all_widgets(w, h_in, h_out, click):
                w.bind("<Enter>", h_in)
                w.bind("<Leave>", h_out)
                w.bind("<Button-1>", click)
                for c in w.winfo_children():
                    bind_all_widgets(c, h_in, h_out, click)

            bind_all_widgets(row, hover_in, hover_out, pick)

    def _do_login(self):
        user = self.user_entry.get().strip()
        pwd  = self.pass_entry.get()

        if not user or not pwd:
            messagebox.showwarning("EZMessage", "Rellena usuario y contraseña.")
            return

        self.app.reload_accounts()
        acc = self.app.accounts.get(user.lower())
        if acc and acc.get("password") == sha256(pwd):
            self.app.login(acc["username"])
        else:
            messagebox.showerror("EZMessage", "Usuario o contraseña incorrectos.")
            self.pass_entry.delete(0, "end")


# ============================================================
#  VISTA 2 · CREAR CUENTA DAVID
# ============================================================
class RegisterFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.kind = "normal"

        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(wrap, bg=PANEL, padx=32, pady=24,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack()

        tk.Label(card, text="Crear Cuenta David", bg=PANEL, fg=TEXT,
                 font=F_TITLE, anchor="w").pack(fill="x")
        tk.Label(card, text="Elige el tipo de cuenta y completa los datos",
                 bg=PANEL, fg=MUTED, font=F_SMALL, anchor="w").pack(fill="x",
                                                                    pady=(2, 14))

        seg = tk.Frame(card, bg=CARD, highlightthickness=1,
                       highlightbackground=BORDER)
        seg.pack(fill="x")
        self.btn_normal = HoverButton(seg, text="Uso normal",
                                      normal_bg=ACCENT, hover_bg=ACCENT_H,
                                      command=lambda: self._set_kind("normal"),
                                      pady=9)
        self.btn_normal.pack(side="left", fill="x", expand=True, padx=3, pady=3)
        self.btn_kid = HoverButton(seg, text="Para mi niño/a",
                                   normal_bg=CARD, hover_bg=CARD_H, fg=MUTED,
                                   command=lambda: self._set_kind("kid"),
                                   pady=9)
        self.btn_kid.pack(side="left", fill="x", expand=True, padx=3, pady=3)

        self.e_user = field(card, "Nombre de usuario")
        self.e_email = field(card, "Correo electrónico")
        self.email_label = card.winfo_children()[-2]

        row1 = tk.Frame(card, bg=PANEL)
        row1.pack(fill="x")
        c1 = tk.Frame(row1, bg=PANEL)
        c1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        c2 = tk.Frame(row1, bg=PANEL)
        c2.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.e_dob = field(c1, "Nacimiento (AAAA-MM-DD)")
        self.e_age = field(c2, "Edad")

        tk.Label(card, text="Género", bg=PANEL, fg=MUTED,
                 font=F_SMALL, anchor="w").pack(fill="x", pady=(10, 3))
        self.e_gender = ttk.Combobox(card, state="readonly",
                                     style="Dark.TCombobox",
                                     values=["Masculino", "Femenino", "Otro"],
                                     font=F_INPUT)
        self.e_gender.pack(fill="x", ipady=5)

        row2 = tk.Frame(card, bg=PANEL)
        row2.pack(fill="x")
        c3 = tk.Frame(row2, bg=PANEL)
        c3.pack(side="left", fill="x", expand=True, padx=(0, 6))
        c4 = tk.Frame(row2, bg=PANEL)
        c4.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.e_pass = field(c3, "Contraseña", show="•")
        self.e_conf = field(c4, "Confirmar", show="•")

        self.btn_submit = HoverButton(card, text="Registrar Cuenta",
                                      normal_bg=ACCENT, hover_bg=ACCENT_H,
                                      command=self._submit, pady=10)
        self.btn_submit.pack(fill="x", pady=(20, 0))

        self.btn_back = HoverButton(card, text="Volver",
                                    normal_bg=PANEL, hover_bg=CARD, fg=TEXT,
                                    command=lambda: self.app.show("LoginFrame"),
                                    pady=9)
        self.btn_back.pack(fill="x", pady=(8, 0))
        self.btn_back.configure(highlightthickness=1,
                                highlightbackground=BORDER,
                                highlightcolor=BORDER)

        self.e_dob.bind("<FocusOut>", self._autofill_age)
        self.e_dob.bind("<Return>", self._autofill_age)

    def on_show(self):
        self._reset()

    def _reset(self):
        for e in (self.e_user, self.e_email, self.e_dob, self.e_age,
                  self.e_pass, self.e_conf):
            e.delete(0, "end")
        self.e_gender.set("")
        self._set_kind("normal")

    def _set_kind(self, kind):
        self.kind = kind
        if kind == "normal":
            self.btn_normal.configure(bg=ACCENT, fg="white")
            self.btn_normal._n, self.btn_normal._h = ACCENT, ACCENT_H
            self.btn_kid.configure(bg=CARD, fg=MUTED)
            self.btn_kid._n, self.btn_kid._h = CARD, CARD_H
            self.email_label.pack(fill="x", pady=(10, 3))
            self.e_email.pack(fill="x", ipady=7)
            self.e_gender.configure(values=["Masculino", "Femenino", "Otro"])
        else:
            self.btn_kid.configure(bg=PURPLE, fg="white")
            self.btn_kid._n, self.btn_kid._h = PURPLE, PURPLE_H
            self.btn_normal.configure(bg=CARD, fg=MUTED)
            self.btn_normal._n, self.btn_normal._h = CARD, CARD_H
            self.email_label.pack_forget()
            self.e_email.pack_forget()
            self.e_email.delete(0, "end")
            self.e_gender.configure(values=["Niño", "Niña", "Otro"])

    def _autofill_age(self, _=None):
        txt = self.e_dob.get().strip()
        try:
            d = datetime.datetime.strptime(txt, "%Y-%m-%d").date()
        except ValueError:
            return
        today = datetime.date.today()
        age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
        self.e_age.delete(0, "end")
        self.e_age.insert(0, str(max(0, age)))

    def _submit(self):
        user = self.e_user.get().strip()
        pwd  = self.e_pass.get()
        conf = self.e_conf.get()
        email = self.e_email.get().strip()

        if len(user) < 3:
            return self._err("El nombre de usuario debe tener al menos 3 caracteres.")
        if " " in user:
            return self._err("El nombre de usuario no puede tener espacios.")

        self.app.reload_accounts()
        if user.lower() in self.app.accounts:
            return self._err("Ese nombre de usuario ya está registrado.")

        if self.kind == "normal":
            if "@" not in email or "." not in email:
                return self._err("Introduce un correo electrónico válido.")
        else:
            email = ""

        dob = self.e_dob.get().strip()
        try:
            datetime.datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            return self._err("La fecha de nacimiento debe ser AAAA-MM-DD.")

        try:
            age = int(self.e_age.get())
        except ValueError:
            return self._err("La edad debe ser un número.")

        if self.kind == "kid" and not (1 <= age <= 17):
            return self._err("Una cuenta infantil debe tener entre 1 y 17 años.")
        if self.kind == "normal" and not (1 <= age <= 120):
            return self._err("Edad fuera de rango.")

        gender = self.e_gender.get()
        if not gender:
            return self._err("Selecciona un género.")

        if len(pwd) < 4:
            return self._err("La contraseña debe tener al menos 4 caracteres.")
        if pwd != conf:
            return self._err("Las contraseñas no coinciden.")

        self.app.accounts[user.lower()] = {
            "username": user,
            "type": self.kind,
            "email": email,
            "dob": dob,
            "age": age,
            "gender": gender,
            "password": sha256(pwd),
            "created": now_iso(),
        }
        self.app.save_accounts()

        messagebox.showinfo("EZMessage", f"¡Cuenta David «{user}» creada!\nYa tienes la sesión iniciada.")
        self.app.login(user)

    def _err(self, msg):
        messagebox.showwarning("EZMessage", msg)


# ============================================================
#  VISTA 3 · EZMessage (chat) + EZPack AI
# ============================================================
class ChatFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.active = None
        self._sig = None
        self._build()

    def _build(self):
        # ---------- SIDEBAR ----------
        side = tk.Frame(self, bg=PANEL, width=300)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        me_box = tk.Frame(side, bg=PANEL)
        me_box.pack(fill="x", padx=14, pady=(16, 10))

        self.me_avatar_slot = tk.Frame(me_box, bg=PANEL)
        self.me_avatar_slot.pack(side="left")

        info = tk.Frame(me_box, bg=PANEL)
        info.pack(side="left", fill="x", expand=True, padx=10)
        self.me_name = tk.Label(info, text="", bg=PANEL, fg=TEXT,
                                font=F_BOLD, anchor="w")
        self.me_name.pack(fill="x")
        self.me_sub = tk.Label(info, text="", bg=PANEL, fg=MUTED,
                               font=F_TINY, anchor="w")
        self.me_sub.pack(fill="x")

        self.menu_btn = HoverButton(me_box, text="⋯", normal_bg=PANEL,
                                    hover_bg=CARD, fg=MUTED,
                                    font=("Segoe UI", 15, "bold"),
                                    padx=9, pady=0,
                                    command=self._open_menu)
        self.menu_btn.pack(side="right")

        # ----- Botones principales de la sidebar -----
        HoverButton(side, text="＋  Nueva conversación",
                    normal_bg=CARD, hover_bg=CARD_H, fg=TEXT,
                    command=self.new_chat_dialog,
                    pady=9).pack(fill="x", padx=14, pady=(0, 6))

        # 🤖 EZPack AI
        HoverButton(side, text="🤖  Asistente AI",
                    normal_bg=AI_COL, hover_bg=AI_COL_H, fg="white",
                    command=self.app.open_ai_assistant,
                    pady=9).pack(fill="x", padx=14, pady=(0, 4))

        self.ai_hint = tk.Label(side, text=f"Proveedor: {self.app.ai_provider()}",
                                bg=PANEL, fg=MUTED, font=F_TINY, anchor="w")
        self.ai_hint.pack(fill="x", padx=18, pady=(0, 10))

        tk.Label(side, text="CONVERSACIONES", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold"), anchor="w"
                 ).pack(fill="x", padx=18, pady=(4, 6))

        self.conv_scroll = ScrollFrame(side, bg=PANEL)
        self.conv_scroll.pack(fill="both", expand=True, padx=(8, 4), pady=(0, 12))
        self.conv_scroll.canvas.configure(bg=PANEL)
        self.conv_scroll.inner.configure(bg=PANEL)
        self.conv_scroll.vsb.configure(bg=PANEL)

        # ---------- ÁREA DE CHAT ----------
        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        head = tk.Frame(right, bg=PANEL, height=64)
        head.pack(fill="x")
        head.pack_propagate(False)

        self.head_avatar_slot = tk.Frame(head, bg=PANEL)
        self.head_avatar_slot.pack(side="left", padx=(18, 10), pady=12)

        hinfo = tk.Frame(head, bg=PANEL)
        hinfo.pack(side="left", fill="y", pady=14)
        self.head_name = tk.Label(hinfo, text="", bg=PANEL, fg=TEXT,
                                  font=F_H2, anchor="w")
        self.head_name.pack(fill="x")
        self.head_sub = tk.Label(hinfo, text="", bg=PANEL, fg=MUTED,
                                 font=F_TINY, anchor="w")
        self.head_sub.pack(fill="x")

        self.msgs_scroll = ScrollFrame(right, bg=BG)
        self.msgs_scroll.pack(fill="both", expand=True)

        bar = tk.Frame(right, bg=PANEL)
        bar.pack(fill="x", side="bottom")

        inner_bar = tk.Frame(bar, bg=PANEL)
        inner_bar.pack(fill="x", padx=16, pady=12)

        self.msg_entry = tk.Entry(inner_bar, bg=CARD, fg=TEXT,
                                  insertbackground=TEXT, relief="flat", bd=0,
                                  font=F_INPUT, highlightthickness=1,
                                  highlightbackground=BORDER,
                                  highlightcolor=ACCENT)
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        self.btn_send = HoverButton(inner_bar, text="Enviar",
                                    normal_bg=ACCENT, hover_bg=ACCENT_H,
                                    command=self.send_message,
                                    padx=22, pady=9)
        self.btn_send.pack(side="right")

        self.msg_entry.bind("<KeyRelease>", self._update_send_state)
        self._update_send_state()

        self._show_empty_state()

    # --------------------------------------------------------
    def _show_empty_state(self):
        self.msgs_scroll.clear()
        holder = tk.Frame(self.msgs_scroll.inner, bg=BG)
        holder.pack(expand=True, fill="both", pady=140)
        tk.Label(holder, text="💬", bg=BG, fg=CARD_H,
                 font=("Segoe UI", 52)).pack()
        tk.Label(holder, text="Selecciona una conversación",
                 bg=BG, fg=TEXT, font=F_H1).pack(pady=(6, 2))
        tk.Label(holder, text="o pulsa «Nueva conversación» para empezar",
                 bg=BG, fg=MUTED, font=F_SMALL).pack()

    def _update_send_state(self, _=None):
        has_chat = self.active is not None
        has_text = bool(self.msg_entry.get().strip())
        state = "normal" if (has_chat and has_text) else "disabled"
        self.btn_send.configure(state=state)
        if state == "disabled":
            self.btn_send.configure(bg=CARD, fg=MUTED)
        else:
            self.btn_send.configure(bg=ACCENT, fg="white")

    def on_show(self):
        self.app.reload_accounts()
        self.app.reload_chats()
        self._render_me()
        self.active = None
        self._sig = None
        self.refresh_conversations()
        self._show_empty_state()
        self._update_send_state()
        self.ai_hint.configure(text=f"Proveedor: {self.app.ai_provider()}")
        self._schedule_poll()

    def _render_me(self):
        for w in self.me_avatar_slot.winfo_children():
            w.destroy()
        me = self.app.current_user
        if not me:
            return
        make_avatar(self.me_avatar_slot, self.app.display_name(me), 42, PANEL).pack()
        self.me_name.configure(text=self.app.display_name(me))
        t = self.app.account_type(me)
        self.me_sub.configure(
            text="Cuenta Infantil" if t == "kid" else "Cuenta normal")

    # --------------------------------------------------------
    def _open_menu(self):
        m = tk.Menu(self, tearoff=0, bg=CARD, fg=TEXT,
                    activebackground=ACCENT, activeforeground="white",
                    bd=0, font=F_BODY)
        m.add_command(label="  🤖 Abrir EZPack AI",
                      command=self.app.open_ai_assistant)
        prov = self.app.ai_provider()
        m.add_command(label=f"  🌐 Abrir {prov} en el navegador",
                      command=self.app.open_ai_provider_web)
        m.add_command(label="  ⚙️ Configurar IA…",
                      command=self.app.open_ai_settings)
        m.add_separator()
        m.add_command(label="  💬 Nueva conversación", command=self.new_chat_dialog)
        m.add_separator()
        m.add_command(label="  🚪 Cerrar sesión", command=self.app.logout)
        m.add_command(label="  🗑️ Eliminar mi cuenta",
                      command=self.app.delete_my_account)
        try:
            x = self.menu_btn.winfo_rootx() - 160
            y = self.menu_btn.winfo_rooty() + self.menu_btn.winfo_height() + 4
            m.tk_popup(x, y)
        finally:
            m.grab_release()

    # --------------------------------------------------------
    def _conversations(self):
        me = self.app.current_user
        convs = {}
        for m in self.app.chats.get("messages", []):
            f = str(m.get("from", "")).lower()
            t = str(m.get("to", "")).lower()
            if f == me:
                other = t
            elif t == me:
                other = f
            else:
                continue
            c = convs.setdefault(other, {"last": None, "unread": 0})
            if c["last"] is None or m.get("ts", "") > c["last"].get("ts", ""):
                c["last"] = m
            if t == me and not m.get("read", False):
                c["unread"] += 1

        for key in self.app.accounts:
            if key != me:
                convs.setdefault(key, {"last": None, "unread": 0})
        return convs

    def refresh_conversations(self):
        convs = self._conversations()
        ordered = sorted(
            convs.items(),
            key=lambda kv: (kv[1]["last"]["ts"] if kv[1]["last"] else ""),
            reverse=True)

        self.conv_scroll.clear()

        if not ordered:
            tk.Label(self.conv_scroll.inner,
                     text="Aún no hay otros usuarios.\nCrea otra Cuenta David\ny vuelve a iniciar sesión.",
                     bg=PANEL, fg=MUTED, font=F_SMALL,
                     justify="center").pack(pady=20)
            return

        for key, data in ordered:
            self._conv_row(key, data)

    def _conv_row(self, key, data):
        last = data["last"]
        unread = data["unread"]
        selected = (self.active == key)

        bg = CARD if selected else PANEL
        row = tk.Frame(self.conv_scroll.inner, bg=bg, cursor="hand2")
        row.pack(fill="x", pady=1)

        av = make_avatar(row, self.app.display_name(key), 40, bg)
        av.pack(side="left", padx=(10, 10), pady=8)

        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="both", expand=True, pady=8)

        top = tk.Frame(info, bg=bg)
        top.pack(fill="x")
        tk.Label(top, text=self.app.display_name(key), bg=bg, fg=TEXT,
                 font=F_BOLD, anchor="w").pack(side="left")
        if last:
            tk.Label(top, text=fmt_time(last.get("ts", "")), bg=bg,
                     fg=MUTED, font=F_TINY).pack(side="right")

        preview = "Sin mensajes"
        if last:
            txt = last.get("text", "")
            preview = ("Tú: " if str(last.get("from", "")).lower() == self.app.current_user
                       else "") + (txt[:34] + "…" if len(txt) > 34 else txt)

        bot = tk.Frame(info, bg=bg)
        bot.pack(fill="x")
        tk.Label(bot, text=preview, bg=bg,
                 fg=TEXT if unread else MUTED, font=F_TINY,
                 anchor="w").pack(side="left", fill="x", expand=True)

        if unread:
            tk.Label(bot, text=str(unread), bg=ACCENT, fg="white",
                     font=("Segoe UI", 8, "bold"), padx=6, pady=0
                     ).pack(side="right")

        def hover_in(_e, r=row):
            set_bg_recursive(r, CARD_H)

        def hover_out(_e, r=row, base=bg):
            set_bg_recursive(r, base)

        def click(_e, k=key):
            self.open_chat(k)

        def bind_all_widgets(w, hi, ho, cl):
            w.bind("<Enter>", hi)
            w.bind("<Leave>", ho)
            w.bind("<Button-1>", cl)
            for c in w.winfo_children():
                bind_all_widgets(c, hi, ho, cl)

        bind_all_widgets(row, hover_in, hover_out, click)

    # --------------------------------------------------------
    def open_chat(self, key):
        self.active = key.lower()
        self._mark_read(self.active)
        self.refresh_conversations()
        self._render_header()
        self._render_messages(scroll=True)
        self._update_send_state()
        self.msg_entry.focus_set()

    def _render_header(self):
        for w in self.head_avatar_slot.winfo_children():
            w.destroy()
        if not self.active:
            self.head_name.configure(text="")
            self.head_sub.configure(text="")
            return
        name = self.app.display_name(self.active)
        make_avatar(self.head_avatar_slot, name, 40, PANEL).pack()
        self.head_name.configure(text=name)
        t = self.app.account_type(self.active)
        if t == "kid":
            self.head_sub.configure(text="Cuenta Infantil de David")
        elif t == "normal":
            acc = self.app.accounts.get(self.active, {})
            self.head_sub.configure(text=acc.get("email", "Cuenta David"))
        else:
            self.head_sub.configure(text="Contacto externo")

    def _mark_read(self, other):
        me = self.app.current_user
        changed = False
        for m in self.app.chats.get("messages", []):
            if (str(m.get("from", "")).lower() == other
                    and str(m.get("to", "")).lower() == me
                    and not m.get("read", False)):
                m["read"] = True
                changed = True
        if changed:
            save_json(CHATS_FILE, self.app.chats)

    def _messages_with(self, other):
        me = self.app.current_user
        out = []
        for m in self.app.chats.get("messages", []):
            f = str(m.get("from", "")).lower()
            t = str(m.get("to", "")).lower()
            if (f == me and t == other) or (f == other and t == me):
                out.append(m)
        out.sort(key=lambda m: m.get("ts", ""))
        return out

    def _render_messages(self, scroll=False):
        if not self.active:
            return
        self.msgs_scroll.clear()

        msgs = self._messages_with(self.active)
        if not msgs:
            holder = tk.Frame(self.msgs_scroll.inner, bg=BG)
            holder.pack(fill="x", pady=60)
            tk.Label(holder,
                     text=f"Esta es tu conversación con {self.app.display_name(self.active)}.\n"
                          "Escribe el primer mensaje 👇",
                     bg=BG, fg=MUTED, font=F_SMALL, justify="center").pack()
            return

        tk.Frame(self.msgs_scroll.inner, bg=BG, height=10).pack(fill="x")

        last_date = None
        for m in msgs:
            try:
                d = datetime.datetime.fromisoformat(m.get("ts", "")).date()
            except Exception:
                d = None
            if d and d != last_date:
                last_date = d
                self._date_separator(d)
            self._bubble(m)

        tk.Frame(self.msgs_scroll.inner, bg=BG, height=12).pack(fill="x")
        if scroll:
            self.after(40, self.msgs_scroll.to_bottom)

    def _date_separator(self, d):
        today = datetime.date.today()
        if d == today:
            label = "Hoy"
        elif d == today - datetime.timedelta(days=1):
            label = "Ayer"
        else:
            label = d.strftime("%d/%m/%Y")
        holder = tk.Frame(self.msgs_scroll.inner, bg=BG)
        holder.pack(fill="x", pady=10)
        tk.Label(holder, text=label, bg=CARD, fg=MUTED, font=F_TINY,
                 padx=10, pady=3).pack()

    def _bubble(self, msg):
        mine = str(msg.get("from", "")).lower() == self.app.current_user

        row = tk.Frame(self.msgs_scroll.inner, bg=BG)
        row.pack(fill="x", padx=16, pady=3)

        bubble = tk.Frame(row, bg=BUBBLE_ME if mine else BUBBLE_OT,
                          padx=12, pady=8)
        bubble.pack(side="right" if mine else "left",
                    anchor="e" if mine else "w")

        tk.Label(bubble, text=msg.get("text", ""),
                 bg=BUBBLE_ME if mine else BUBBLE_OT,
                 fg="white" if mine else TEXT,
                 font=F_BODY, wraplength=430, justify="left",
                 anchor="w").pack(fill="x")

        meta = fmt_time(msg.get("ts", ""))
        if mine:
            meta += "  ✓✓" if msg.get("read") else "  ✓"
        tk.Label(bubble, text=meta,
                 bg=BUBBLE_ME if mine else BUBBLE_OT,
                 fg="#bfd4ff" if mine else MUTED,
                 font=F_TINY, anchor="e").pack(fill="x", pady=(3, 0))

    def send_message(self):
        if not self.active:
            return
        text = self.msg_entry.get().strip()
        if not text:
            return

        me = self.app.current_user
        self.app.reload_chats()
        self.app.chats.setdefault("messages", []).append({
            "id": str(uuid.uuid4()),
            "from": me,
            "to": self.active,
            "text": text,
            "ts": now_iso(),
            "read": False,
        })
        save_json(CHATS_FILE, self.app.chats)

        self.msg_entry.delete(0, "end")
        self._update_send_state()
        self._sig = None
        self.refresh_conversations()
        self._render_messages(scroll=True)

    # --------------------------------------------------------
    def new_chat_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Nueva conversación")
        dlg.configure(bg=PANEL)
        dlg.geometry("380x470")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        dlg.update_idletasks()
        x = self.winfo_toplevel().winfo_rootx() + (self.winfo_toplevel().winfo_width() - 380) // 2
        y = self.winfo_toplevel().winfo_rooty() + (self.winfo_toplevel().winfo_height() - 470) // 2
        dlg.geometry(f"+{max(0, x)}+{max(0, y)}")

        tk.Label(dlg, text="Nueva conversación", bg=PANEL, fg=TEXT,
                 font=F_H1).pack(anchor="w", padx=20, pady=(18, 2))
        tk.Label(dlg, text="Elige una Cuenta David o escribe un nombre",
                 bg=PANEL, fg=MUTED, font=F_SMALL).pack(anchor="w", padx=20)

        tk.Label(dlg, text="Nombre del contacto", bg=PANEL, fg=MUTED,
                 font=F_SMALL, anchor="w").pack(fill="x", padx=20, pady=(16, 3))
        name_e = make_entry(dlg)
        name_e.pack(fill="x", padx=20, ipady=7)

        def open_typed():
            n = name_e.get().strip()
            if not n:
                return
            dlg.destroy()
            self.open_chat(n)

        HoverButton(dlg, text="Abrir chat con este nombre",
                    normal_bg=ACCENT, hover_bg=ACCENT_H,
                    command=open_typed, pady=8).pack(fill="x", padx=20, pady=(8, 14))
        name_e.bind("<Return>", lambda e: open_typed())

        tk.Label(dlg, text="CUENTAS DAVID DISPONIBLES", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold"), anchor="w"
                 ).pack(fill="x", padx=22)

        sc = ScrollFrame(dlg, bg=PANEL)
        sc.pack(fill="both", expand=True, padx=(12, 6), pady=(6, 16))
        sc.canvas.configure(bg=PANEL)
        sc.inner.configure(bg=PANEL)

        me = self.app.current_user
        others = [(k, v) for k, v in sorted(self.app.accounts.items()) if k != me]

        if not others:
            tk.Label(sc.inner, text="No hay otras Cuentas David en este equipo.\n"
                                    "Crea otra cuenta para chatear.",
                     bg=PANEL, fg=MUTED, font=F_SMALL,
                     justify="center").pack(pady=24)
        else:
            for key, acc in others:
                row = tk.Frame(sc.inner, bg=PANEL, cursor="hand2")
                row.pack(fill="x", pady=1)
                make_avatar(row, acc.get("username", key), 34, PANEL
                            ).pack(side="left", padx=(10, 10), pady=6)
                info = tk.Frame(row, bg=PANEL)
                info.pack(side="left", fill="x", expand=True, pady=6)
                tk.Label(info, text=acc.get("username", key), bg=PANEL,
                         fg=TEXT, font=F_BOLD, anchor="w").pack(fill="x")
                tk.Label(info,
                         text="Cuenta Infantil" if acc.get("type") == "kid"
                         else acc.get("email", "Cuenta normal"),
                         bg=PANEL, fg=MUTED, font=F_TINY,
                         anchor="w").pack(fill="x")

                def click(_e, k=key):
                    dlg.destroy()
                    self.open_chat(k)

                def hi(_e, r=row):
                    set_bg_recursive(r, CARD)

                def ho(_e, r=row):
                    set_bg_recursive(r, PANEL)

                def bind_all_widgets(w, a, b, c):
                    w.bind("<Enter>", a)
                    w.bind("<Leave>", b)
                    w.bind("<Button-1>", c)
                    for ch in w.winfo_children():
                        bind_all_widgets(ch, a, b, c)

                bind_all_widgets(row, hi, ho, click)

    # --------------------------------------------------------
    def _schedule_poll(self):
        self.after(1500, self._poll)

    def _poll(self):
        if not self.winfo_exists():
            return
        try:
            new_chats = load_json(CHATS_FILE, {"messages": []})
            sig = json.dumps(new_chats.get("messages", []), sort_keys=True,
                             ensure_ascii=False)
            if sig != self._sig:
                self._sig = sig
                self.app.chats = new_chats
                self.app.reload_accounts()
                self.refresh_conversations()
                if self.active:
                    self._mark_read(self.active)
                    self._render_messages(scroll=True)
        except Exception:
            pass
        self._schedule_poll()


# ============================================================
#  Punto de entrada
# ============================================================
def main():
    app = EZMessage()
    app.mainloop()


if __name__ == "__main__":
    main()
