#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Grok Register - Versi GUI TTK
Integrasi DrissionPage_example.py, openai_register.py, batch_open_nsfw.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import datetime
import time
import os
import sys
import gc
import queue
import secrets
import struct
import random
import re
import string
import json

os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")

import grok_core
from grok_core import *

def setup_light_theme(root):
    try:
        root.option_add("*Background", UI_BG)
        root.option_add("*Foreground", UI_FG)
        root.option_add("*selectBackground", UI_ACTIVE_BG)
        root.option_add("*selectForeground", UI_FG)
        root.option_add("*insertBackground", UI_FG)
        root.option_add("*Entry.Background", UI_ENTRY_BG)
        root.option_add("*Text.Background", UI_ENTRY_BG)
        root.option_add("*Menu.Background", UI_ENTRY_BG)
        root.option_add("*Menu.Foreground", UI_FG)
        style = ttk.Style(root)
        available = set(style.theme_names())
        if "clam" in available:
            style.theme_use("clam")
        elif "default" in available:
            style.theme_use("default")
        root.configure(bg=UI_BG)
        style.configure(".", background=UI_BG, foreground=UI_FG, fieldbackground=UI_ENTRY_BG)
        style.configure("TFrame", background=UI_BG)
        style.configure("TLabelframe", background=UI_BG, foreground=UI_FG)
        style.configure("TLabelframe.Label", background=UI_BG, foreground=UI_FG)
        style.configure("TLabel", background=UI_BG, foreground=UI_FG)
        style.configure("TCheckbutton", background=UI_BG, foreground=UI_FG)
        style.configure("TButton", background=UI_BUTTON_BG, foreground=UI_FG)
        style.configure("TEntry", fieldbackground=UI_ENTRY_BG, foreground=UI_FG)
        style.configure("TCombobox", fieldbackground=UI_ENTRY_BG, foreground=UI_FG)
        style.configure("TSpinbox", fieldbackground=UI_ENTRY_BG, foreground=UI_FG)
    except Exception:
        pass


def tk_label(parent, text="", **kwargs):
    font_val = kwargs.pop("font", ("Segoe UI", 10))
    return tk.Label(parent, text=text, bg=kwargs.pop("bg", UI_BG), fg=kwargs.pop("fg", UI_FG), font=font_val, **kwargs)


def tk_entry(parent, textvariable=None, width=30, **kwargs):
    return tk.Entry(
        parent,
        textvariable=textvariable,
        width=width,
        bg=UI_ENTRY_BG,
        fg=UI_FG,
        insertbackground=UI_FG,
        disabledbackground="#f8fafc",
        disabledforeground=UI_MUTED_FG,
        highlightthickness=1,
        highlightbackground="#cbd5e1",
        highlightcolor=UI_BUTTON_BG,
        relief=tk.FLAT,
        bd=0,
        font=("Segoe UI", 10),
        **kwargs,
    )


def tk_button(parent, text="", command=None, state=tk.NORMAL, **kwargs):
    bg_color = kwargs.pop("bg", UI_BUTTON_BG)
    fg_color = kwargs.pop("fg", "#ffffff")
    active_bg = kwargs.pop("activebackground", UI_ACTIVE_BG)
    active_fg = kwargs.pop("activeforeground", "#ffffff")
    font_val = kwargs.pop("font", ("Segoe UI Semibold", 10))
    
    return tk.Button(
        parent,
        text=text,
        command=command,
        state=state,
        bg=bg_color,
        fg=fg_color,
        activebackground=active_bg,
        activeforeground=active_fg,
        disabledforeground="#cbd5e1",
        relief=tk.FLAT,
        borderwidth=0,
        padx=14,
        pady=5,
        font=font_val,
        **kwargs,
    )


def tk_checkbutton(parent, text="", variable=None, **kwargs):
    bg_color = kwargs.pop("bg", UI_BG)
    return tk.Checkbutton(
        parent,
        text=text,
        variable=variable,
        bg=bg_color,
        fg=UI_FG,
        activebackground=bg_color,
        activeforeground=UI_FG,
        selectcolor="#ffffff",
        font=("Segoe UI", 10),
        **kwargs,
    )


def tk_option_menu(parent, variable, values, width=12):
    menu = tk.OptionMenu(parent, variable, *values)
    menu.configure(
        width=width,
        bg=UI_ENTRY_BG,
        fg=UI_FG,
        activebackground=UI_ACTIVE_BG,
        activeforeground="#ffffff",
        highlightthickness=1,
        highlightbackground="#cbd5e1",
        highlightcolor=UI_BUTTON_BG,
        relief=tk.FLAT,
        bd=0,
        font=("Segoe UI", 10),
    )
    menu["menu"].configure(
        bg=UI_ENTRY_BG,
        fg=UI_FG,
        activebackground=UI_ACTIVE_BG,
        activeforeground="#ffffff",
        font=("Segoe UI", 10),
    )
    return menu


class GrokRegisterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Grok Register - by @dailysweet.fa")
        
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
                self._icon_img = img
        except Exception:
            pass

        self.is_running = False
        self.batch_count = 0
        self.success_count = 0
        self.fail_count = 0
        self.success_count_var = tk.StringVar(value="0")
        self.fail_count_var = tk.StringVar(value="0")
        self.results = []
        self.stop_requested = False
        self.ui_queue = queue.Queue()
        self.accounts_output_file = ""
        
        # Check license on start
        ok, info = check_activated_license()
        if ok:
            self.root.geometry("1120x900")
            self.root.minsize(960, 700)
            self.setup_ui()
        else:
            self.root.geometry("520x300")
            self.root.resizable(False, False)
            self.setup_activation_ui()

    def setup_activation_ui(self):
        self.root.configure(bg="#f1f5f9")
        
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        title_font = ("Segoe UI Semibold", 12)
        label_font = ("Segoe UI", 10)
        
        tk.Label(
            self.root,
            text="Aktivasi Lisensi Grok Register",
            font=title_font,
            bg="#f1f5f9",
            fg="#0f172a"
        ).pack(pady=(20, 10))
        
        hwid = get_hwid()
        tk.Label(
            self.root,
            text=f"Silakan hubungi @dailysweet.fa untuk lisensi Anda.\nHardware ID Perangkat Anda: {hwid}",
            font=label_font,
            bg="#f1f5f9",
            fg="#64748b",
            justify=tk.CENTER
        ).pack(pady=(0, 15))
        
        entry_frame = tk.Frame(self.root, bg="#f1f5f9")
        entry_frame.pack(fill=tk.X, padx=40, pady=5)
        
        tk.Label(entry_frame, text="Kunci Lisensi:", font=label_font, bg="#f1f5f9", fg="#334155").pack(anchor=tk.W)
        self.key_var = tk.StringVar()
        entry = tk_entry(entry_frame, textvariable=self.key_var, width=44)
        entry.pack(fill=tk.X, pady=(4, 10))
        entry.focus_set()
        
        self.msg_label = tk.Label(self.root, text="", font=("Segoe UI", 9), bg="#f1f5f9", fg="#ef4444")
        self.msg_label.pack()
        
        def do_activate():
            key = self.key_var.get().strip()
            if not key:
                self.msg_label.config(text="Silakan masukkan kunci lisensi!", fg="#ef4444")
                return
            
            success, msg = verify_and_activate_license(key)
            if success:
                messagebox.showinfo("Aktivasi Sukses", "Lisensi berhasil diaktivasi!")
                # Reset to normal UI
                for widget in self.root.winfo_children():
                    widget.destroy()
                self.root.geometry("1120x900")
                self.root.resizable(True, True)
                self.root.minsize(960, 700)
                self.setup_ui()
            else:
                self.msg_label.config(text=f"Gagal: {msg}", fg="#ef4444")
                
        btn_frame = tk.Frame(self.root, bg="#f1f5f9")
        btn_frame.pack(pady=(10, 20))
        
        tk_button(btn_frame, text="Aktivasi", command=do_activate, bg="#2563eb", activebackground="#1d4ed8").pack(side=tk.LEFT, padx=5)
        tk_button(btn_frame, text="Keluar", command=self.root.destroy, bg="#e2e8f0", fg="#0f172a", activebackground="#cbd5e1", activeforeground="#0f172a").pack(side=tk.RIGHT, padx=5)

    def setup_ui(self):
        load_config()
        self.root.configure(bg="#f1f5f9")

        # 1. Left Sidebar
        sidebar = tk.Frame(self.root, bg="#0f172a", width=250, padx=16, pady=20)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Sidebar Header
        logo_label = tk.Label(
            sidebar,
            text="GROK REGISTER",
            font=("Segoe UI Semibold", 13),
            fg="#ffffff",
            bg="#0f172a",
        )
        logo_label.pack(anchor=tk.W, pady=(0, 2))
        
        watermark_label = tk.Label(
            sidebar,
            text="by @dailysweet.fa",
            font=("Segoe UI Italic", 9),
            fg="#64748b",
            bg="#0f172a",
        )
        watermark_label.pack(anchor=tk.W, pady=(0, 24))

        # Control Panel Buttons
        control_header = tk.Label(
            sidebar,
            text="KONTROL PANEL",
            font=("Segoe UI Semibold", 9),
            fg="#475569",
            bg="#0f172a",
        )
        control_header.pack(anchor=tk.W, pady=(0, 8))

        self.start_btn = tk_button(
            sidebar,
            text="Mulai Registrasi",
            command=self.start_registration,
            bg="#2563eb",
            activebackground="#1d4ed8"
        )
        self.start_btn.pack(fill=tk.X, pady=4)

        self.stop_btn = tk_button(
            sidebar,
            text="Berhenti",
            command=self.stop_registration,
            state=tk.DISABLED,
            bg="#ef4444",
            activebackground="#b91c1c"
        )
        self.stop_btn.pack(fill=tk.X, pady=4)

        self.clear_btn = tk_button(
            sidebar,
            text="Bersihkan Log",
            command=self.clear_log,
            bg="#334155",
            fg="#e2e8f0",
            activebackground="#475569",
            activeforeground="#e2e8f0"
        )
        self.clear_btn.pack(fill=tk.X, pady=(4, 28))

        # Statistics & Status Section
        stats_header = tk.Label(
            sidebar,
            text="STATISTIK SESI",
            font=("Segoe UI Semibold", 9),
            fg="#475569",
            bg="#0f172a",
        )
        stats_header.pack(anchor=tk.W, pady=(0, 8))

        # Status Card
        status_card = tk.Frame(
            sidebar,
            bg="#1e293b",
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground="#334155",
            bd=0,
        )
        status_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            status_card,
            text="STATUS SISTEM",
            font=("Segoe UI Semibold", 8),
            fg="#64748b",
            bg="#1e293b",
        ).pack(anchor=tk.W)
        self.status_var = tk.StringVar(value="SIAP")
        self.status_label = tk.Label(
            status_card,
            textvariable=self.status_var,
            font=("Segoe UI Semibold", 13),
            fg="#22c55e",
            bg="#1e293b",
        )
        self.status_label.pack(anchor=tk.W, pady=(2, 0))

        # Success Card
        success_card = tk.Frame(
            sidebar,
            bg="#1e293b",
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground="#334155",
            bd=0,
        )
        success_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            success_card,
            text="REGISTRASI SUKSES",
            font=("Segoe UI Semibold", 8),
            fg="#64748b",
            bg="#1e293b",
        ).pack(anchor=tk.W)
        self.success_label = tk.Label(
            success_card,
            textvariable=self.success_count_var,
            font=("Segoe UI Semibold", 16),
            fg="#22c55e",
            bg="#1e293b",
        )
        self.success_label.pack(anchor=tk.W, pady=(2, 0))

        # Fail Card
        fail_card = tk.Frame(
            sidebar,
            bg="#1e293b",
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground="#334155",
            bd=0,
        )
        fail_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            fail_card,
            text="REGISTRASI GAGAL",
            font=("Segoe UI Semibold", 8),
            fg="#64748b",
            bg="#1e293b",
        ).pack(anchor=tk.W)
        self.fail_label = tk.Label(
            fail_card,
            textvariable=self.fail_count_var,
            font=("Segoe UI Semibold", 16),
            fg="#ef4444",
            bg="#1e293b",
        )
        self.fail_label.pack(anchor=tk.W, pady=(2, 0))


        # 2. Main Content Area
        main_area = tk.Frame(self.root, bg="#f1f5f9", padx=16, pady=16)
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Row of Two Configuration Cards
        cards_frame = tk.Frame(main_area, bg="#f1f5f9")
        cards_frame.pack(fill=tk.X, pady=(0, 12))

        # CARD 1: Email & Jaringan
        card1 = tk.Frame(
            cards_frame,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#e2e8f0",
            bd=0,
            padx=16,
            pady=16,
        )
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        card1.grid_columnconfigure(1, weight=1)

        tk.Label(
            card1,
            text="Konfigurasi Email & Jaringan",
            font=("Segoe UI Semibold", 11),
            bg="#ffffff",
            fg="#0f172a",
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 12))

        def add_c1_label(row, text):
            tk_label(card1, text=text, bg="#ffffff", fg="#64748b").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 10), pady=4
            )

        def add_c1_field(widget, row):
            widget.grid(row=row, column=1, sticky=tk.EW, pady=4)

        # C1 Fields
        add_c1_label(1, "Penyedia Email:")
        self.email_provider_var = tk.StringVar(value=config.get("email_provider", "mailtm"))
        self.email_provider_combo = tk_option_menu(card1, self.email_provider_var, ["duckmail", "yyds", "cloudflare", "mailtm"], width=12)
        add_c1_field(self.email_provider_combo, 1)

        add_c1_label(2, "Jumlah Registrasi:")
        self.count_var = tk.StringVar(value=str(config.get("register_count", 1)))
        self.count_spinbox = tk.Spinbox(
            card1,
            from_=1,
            to=2500,
            width=8,
            textvariable=self.count_var,
            bg=UI_ENTRY_BG,
            fg=UI_FG,
            insertbackground=UI_FG,
            buttonbackground="#f1f5f9",
            disabledbackground="#f8fafc",
            disabledforeground=UI_MUTED_FG,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground="#cbd5e1",
            highlightcolor=UI_BUTTON_BG,
            font=("Segoe UI", 10),
        )
        add_c1_field(self.count_spinbox, 2)

        add_c1_label(3, "Proxy (Opsional):")
        self.proxy_var = tk.StringVar(value=config.get("proxy", ""))
        self.proxy_entry = tk_entry(card1, textvariable=self.proxy_var, width=24)
        add_c1_field(self.proxy_entry, 3)

        add_c1_label(4, "DuckMail API Key:")
        self.api_key_var = tk.StringVar(value=config.get("duckmail_api_key", ""))
        self.api_key_entry = tk_entry(card1, textvariable=self.api_key_var, width=24)
        add_c1_field(self.api_key_entry, 4)

        add_c1_label(5, "Mode Autentikasi CF:")
        self.cloudflare_auth_mode_var = tk.StringVar(value=config.get("cloudflare_auth_mode", "none"))
        self.cloudflare_auth_mode_combo = tk_option_menu(
            card1, self.cloudflare_auth_mode_var, ["query-key", "bearer", "x-api-key", "x-admin-auth", "none"], width=12
        )
        add_c1_field(self.cloudflare_auth_mode_combo, 5)

        add_c1_label(6, "Cloudflare API Base:")
        self.cloudflare_api_base_var = tk.StringVar(value=config.get("cloudflare_api_base", ""))
        self.cloudflare_api_base_entry = tk_entry(card1, textvariable=self.cloudflare_api_base_var, width=24)
        add_c1_field(self.cloudflare_api_base_entry, 6)

        add_c1_label(7, "Cloudflare API Key:")
        self.cloudflare_api_key_var = tk.StringVar(value=config.get("cloudflare_api_key", ""))
        self.cloudflare_api_key_entry = tk_entry(card1, textvariable=self.cloudflare_api_key_var, width=24)
        add_c1_field(self.cloudflare_api_key_entry, 7)

        add_c1_label(8, "Jalur CF:")
        self.cloudflare_paths_var = tk.StringVar(
            value=",".join(
                [
                    config.get("cloudflare_path_domains", "/api/domains"),
                    config.get("cloudflare_path_accounts", "/api/new_address"),
                    config.get("cloudflare_path_token", "/api/token"),
                    config.get("cloudflare_path_messages", "/api/mails"),
                ]
            )
        )
        self.cloudflare_paths_entry = tk_entry(card1, textvariable=self.cloudflare_paths_var, width=24)
        add_c1_field(self.cloudflare_paths_entry, 8)


        # CARD 2: grok2api & Pool
        card2 = tk.Frame(
            cards_frame,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#e2e8f0",
            bd=0,
            padx=16,
            pady=16,
        )
        card2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))
        card2.grid_columnconfigure(1, weight=1)

        tk.Label(
            card2,
            text="Integrasi API & Pool grok2api",
            font=("Segoe UI Semibold", 11),
            bg="#ffffff",
            fg="#0f172a",
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 12))

        def add_c2_label(row, text):
            tk_label(card2, text=text, bg="#ffffff", fg="#64748b").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 10), pady=4
            )

        def add_c2_field(widget, row):
            widget.grid(row=row, column=1, sticky=tk.EW, pady=4)

        # C2 Fields
        add_c2_label(1, "grok2api Pool Lokal:")
        self.grok2api_local_auto_var = tk.BooleanVar(value=bool(config.get("grok2api_auto_add_local", True)))
        self.grok2api_local_auto_check = tk_checkbutton(card2, variable=self.grok2api_local_auto_var, bg="#ffffff")
        add_c2_field(self.grok2api_local_auto_check, 1)

        add_c2_label(2, "Nama Pool grok2api:")
        self.grok2api_pool_name_var = tk.StringVar(value=str(config.get("grok2api_pool_name", "ssoBasic")))
        self.grok2api_pool_name_combo = tk_option_menu(
            card2, self.grok2api_pool_name_var, ["ssoBasic", "ssoSuper"], width=12
        )
        add_c2_field(self.grok2api_pool_name_combo, 2)

        add_c2_label(3, "Token Lokal (token.json):")
        self.grok2api_local_file_var = tk.StringVar(value=str(config.get("grok2api_local_token_file", "")))
        self.grok2api_local_file_entry = tk_entry(card2, textvariable=self.grok2api_local_file_var, width=24)
        add_c2_field(self.grok2api_local_file_entry, 3)

        add_c2_label(4, "grok2api Pool Remote:")
        self.grok2api_remote_auto_var = tk.BooleanVar(value=bool(config.get("grok2api_auto_add_remote", False)))
        self.grok2api_remote_auto_check = tk_checkbutton(card2, variable=self.grok2api_remote_auto_var, bg="#ffffff")
        add_c2_field(self.grok2api_remote_auto_check, 4)

        add_c2_label(5, "Base Remote grok2api:")
        self.grok2api_remote_base_var = tk.StringVar(value=str(config.get("grok2api_remote_base", "")))
        self.grok2api_remote_base_entry = tk_entry(card2, textvariable=self.grok2api_remote_base_var, width=24)
        add_c2_field(self.grok2api_remote_base_entry, 5)

        add_c2_label(6, "app_key Remote:")
        self.grok2api_remote_key_var = tk.StringVar(value=str(config.get("grok2api_remote_app_key", "")))
        self.grok2api_remote_key_entry = tk_entry(card2, textvariable=self.grok2api_remote_key_var, width=24)
        add_c2_field(self.grok2api_remote_key_entry, 6)

        add_c2_label(7, "Opsi Pendaftaran:")
        self.nsfw_var = tk.BooleanVar(value=config.get("enable_nsfw", True))
        self.nsfw_check = tk_checkbutton(card2, text="Aktifkan NSFW setelah pendaftaran", variable=self.nsfw_var, bg="#ffffff")
        add_c2_field(self.nsfw_check, 7)

        # Empty row to balance C2 height with C1
        tk.Label(card2, text="", bg="#ffffff").grid(row=8, column=0, pady=10)


        # CARD 3: Log Aktivitas Sesi (Bottom)
        log_card = tk.Frame(
            main_area,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#e2e8f0",
            bd=0,
            padx=16,
            pady=16,
        )
        log_card.pack(fill=tk.BOTH, expand=True)
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        tk.Label(
            log_card,
            text="Log Aktivitas Sesi",
            font=("Segoe UI Semibold", 11),
            bg="#ffffff",
            fg="#0f172a",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(
            log_card,
            bg="#ffffff",
            fg="#0f172a",
            insertbackground="#0f172a",
            selectbackground=UI_BUTTON_BG,
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#e2e8f0",
            highlightcolor=UI_BUTTON_BG,
            font=("Consolas", 10),
        )
        self.log_text.grid(row=1, column=0, sticky=tk.NSEW)

        # Stats Variable binding (not used visually since we have cards, but kept for compatibility)
        self.stats_var = tk.StringVar(value="Sukses: 0 | Gagal: 0")

        self.log("[*] GUI Siap, Grok Register by @dailysweet.fa")
        self.log(f"[*] Penyedia email saat ini: {self.email_provider_var.get()} | Jumlah registrasi: {self.count_var.get()}")

    def log(self, message):
        if not should_emit_log(message):
            return
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line, flush=True)
        try:
            self.log_text.insert(tk.END, f"{line}\n")
            # Mencegah area log tumbuh tanpa batas dan menyebabkan kelambatan saat berjalan lama
            try:
                line_count = int(float(str(self.log_text.index("end-1c").split(".")[0])))
                if line_count > 5000:
                    self.log_text.delete("1.0", f"{line_count - 4000}.0")
            except Exception:
                pass
            self.log_text.see(tk.END)
        except Exception:
            pass

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def update_stats(self):
        self.stats_var.set(f"Sukses: {self.success_count} | Gagal: {self.fail_count}")
        self.success_count_var.set(str(self.success_count))
        self.fail_count_var.set(str(self.fail_count))

    def _set_running_ui(self, running):
        self.is_running = running
        self.start_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL if running else tk.DISABLED)
        self.status_var.set("BERJALAN" if running else "SIAP")
        self.status_label.config(foreground="#3b82f6" if running else "#22c55e")

    def should_stop(self):
        return self.stop_requested or not self.is_running

    def start_registration(self):
        if self.is_running:
            self.log("[!] Ada tugas lain yang sedang berjalan")
            return

        config["email_provider"] = self.email_provider_var.get().strip() or "duckmail"
        config["enable_nsfw"] = bool(self.nsfw_var.get())
        config["proxy"] = self.proxy_var.get().strip()
        config["duckmail_api_key"] = self.api_key_var.get().strip()
        config["cloudflare_api_base"] = self.cloudflare_api_base_var.get().strip()
        config["cloudflare_api_key"] = self.cloudflare_api_key_var.get().strip()
        config["cloudflare_auth_mode"] = self.cloudflare_auth_mode_var.get().strip() or "none"
        config["grok2api_auto_add_local"] = bool(self.grok2api_local_auto_var.get())
        config["grok2api_local_token_file"] = self.grok2api_local_file_var.get().strip()
        config["grok2api_pool_name"] = self.grok2api_pool_name_var.get().strip() or "ssoBasic"
        config["grok2api_auto_add_remote"] = bool(self.grok2api_remote_auto_var.get())
        config["grok2api_remote_base"] = self.grok2api_remote_base_var.get().strip()
        config["grok2api_remote_app_key"] = self.grok2api_remote_key_var.get().strip()
        raw_paths = [x.strip() for x in self.cloudflare_paths_var.get().split(",") if x.strip()]
        if len(raw_paths) >= 4:
            config["cloudflare_path_domains"] = raw_paths[0] if raw_paths[0].startswith("/") else ("/" + raw_paths[0])
            config["cloudflare_path_accounts"] = raw_paths[1] if raw_paths[1].startswith("/") else ("/" + raw_paths[1])
            config["cloudflare_path_token"] = raw_paths[2] if raw_paths[2].startswith("/") else ("/" + raw_paths[2])
            config["cloudflare_path_messages"] = raw_paths[3] if raw_paths[3].startswith("/") else ("/" + raw_paths[3])
        save_config()
        if config["email_provider"] == "cloudflare" and not config["cloudflare_api_base"]:
            self.log("[!] Mode Cloudflare memerlukan pengisian Cloudflare API Base terlebih dahulu")
            return
        try:
            count = int(self.count_var.get())
        except Exception:
            self.log("[!] Jumlah registrasi tidak valid")
            return
        config["register_count"] = count
        save_config()
        self.stop_requested = False
        self.success_count = 0
        self.fail_count = 0
        self.results = []
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.accounts_output_file = os.path.join(
            os.path.dirname(__file__), f"accounts_{now}.txt"
        )
        self.update_stats()
        self._set_running_ui(True)
        self.log(f"[*] Konfigurasi disimpan, mulai eksekusi. Target jumlah: {count}")
        self.log(f"[*] Akun sukses akan disimpan langsung ke: {self.accounts_output_file}")
        threading.Thread(
            target=self.run_registration,
            args=(count,),
            daemon=True,
        ).start()

    def stop_registration(self):
        self.stop_requested = True
        self.log("[!] Registrasi dihentikan oleh pengguna")

    def run_registration(self, count):
        stop_speed = threading.Event()
        interval = float(config.get("speed_log_interval_sec", 60) or 60)
        def _gui_counts():
            with _stats_lock:
                return self.success_count, self.fail_count

        speed_thread, _meter = start_speed_logger(
            get_counts=_gui_counts,
            log_callback=self.log,
            stop_event=stop_speed,
            interval_sec=interval,
        )
        try:
            concurrent = max(1, int(config.get("concurrent_count", 1) or 1))
            self.log(f"[*] Level log: {get_log_level()} | Interval statistik kecepatan: {int(interval)}s")
            if concurrent <= 1:
                self._run_single_worker(count, worker_id=0)
            else:
                self._run_concurrent_workers(count, concurrent)
        except Exception as exc:
            self.log(f"[!] Pengecualian tugas: {exc}")
        finally:
            stop_speed.set()
            try:
                speed_thread.join(timeout=2)
            except Exception:
                pass
            _wait_cpa_async_threads(
                timeout=5 if self.should_stop() else 300,
                log_callback=self.log,
                skip_if_stopping=self.should_stop,
            )
            self._set_running_ui(False)
            self.log(
                f"[*] Tugas selesai。Sukses {self.success_count} | Gagal {self.fail_count}"
            )

    def _run_concurrent_workers(self, total_count, worker_count):
        import queue
        task_queue = queue.Queue()
        for idx in range(total_count):
            task_queue.put(idx)
        threads = []
        for wid in range(worker_count):
            if self.should_stop():
                break
            t = threading.Thread(
                target=self._worker_loop,
                args=(wid, task_queue, total_count),
                daemon=True,
            )
            t.start()
            threads.append(t)
            sleep_with_cancel(2, self.should_stop)
        _join_threads_interruptible(
            threads,
            should_stop=self.should_stop,
            timeout=None,
            poll=0.5,
        )
        if self.should_stop():
            _join_threads_interruptible(threads, should_stop=None, timeout=5, poll=0.5)

    def _worker_loop(self, worker_id, task_queue, total_count):
        _set_worker_id(worker_id)
        prefix = f"[W{worker_id}]"
        log_fn = lambda msg: self.log(f"{prefix} {msg}")
        try:
            start_browser(log_callback=log_fn)
            log_fn(f"[*] Worker-{worker_id} Browser telah dimulai")
        except Exception as e:
            log_fn(f"[!] Worker-{worker_id} Gagal meluncurkan browser: {e}")
            return
        restart_every = int(config.get("browser_restart_every", 10) or 0)
        local_success = 0
        local_attempts = 0
        max_slot_retry = 3
        try:
            while not self.should_stop():
                try:
                    task_queue.get_nowait()
                except Exception:
                    break
                slot_done = False
                retry_count_for_slot = 0
                while not slot_done and not self.should_stop():
                    try:
                        self._register_one_account(log_fn, worker_id, local_success)
                        local_success += 1
                        slot_done = True
                    except RegistrationCancelled:
                        return
                    except AccountRetryNeeded as exc:
                        retry_count_for_slot += 1
                        if retry_count_for_slot <= max_slot_retry:
                            log_fn(
                                f"[!] Alur akun macet, mencoba kembali ke-{retry_count_for_slot}/{max_slot_retry}: {exc}"
                            )
                            restart_browser(log_callback=log_fn)
                            continue
                        with _stats_lock:
                            self.fail_count += 1
                        log_fn(f"[-] Akun saat ini telah mencapai batas maksimal percobaan, lewati: {exc}")
                        slot_done = True
                    except Exception as exc:
                        with _stats_lock:
                            self.fail_count += 1
                        log_fn(f"[-] Pendaftaran Gagal: {exc}")
                        slot_done = True
                    finally:
                        local_attempts += 1
                        self.update_stats()
                        if self.should_stop():
                            break
                        # Konsisten dengan versi stabil/single worker: restart penuh setiap akun, menghindari sisa sesi SSO/TOS masuk ke tos-gate
                        if _get_browser() is None:
                            start_browser(log_callback=log_fn)
                        else:
                            if restart_every > 0 and local_attempts % restart_every == 0:
                                log_fn(
                                    f"[*] Worker-{worker_id} Telah memproses {local_attempts} akun, merestart browser secara berkala"
                                )
                            restart_browser(log_callback=log_fn)
                        sleep_with_cancel(1, self.should_stop)
        finally:
            stop_browser()

    def _register_one_account(self, log_fn, worker_id=0, local_success=0):
        email = ""
        dev_token = ""
        code = ""
        mail_ok = False
        max_mail_retry = 3
        for mail_try in range(1, max_mail_retry + 1):
            log_fn(f"[*] 1. Membuka halaman pendaftaran (Percobaan {mail_try}/{max_mail_retry})")
            open_signup_page(log_callback=log_fn, cancel_callback=self.should_stop)
            log_fn("[*] 2. Membuat email dan mengirim")
            email, dev_token = fill_email_and_submit(
                log_callback=log_fn, cancel_callback=self.should_stop
            )
            log_fn(f"[*] Email: {email}")
            try:
                with _io_lock:
                    with open(
                        os.path.join(os.path.dirname(__file__), "mail_credentials.txt"),
                        "a", encoding="utf-8",
                    ) as f:
                        f.write(f"{email}\t{dev_token}\n")
            except Exception:
                pass
            log_fn("[*] 3. Menarik kode verifikasi")
            try:
                code = fill_code_and_submit(
                    email, dev_token,
                    log_callback=log_fn, cancel_callback=self.should_stop,
                )
                mail_ok = True
                break
            except Exception as mail_exc:
                msg = str(mail_exc)
                if ("tidak menerima kode verifikasi" in msg.lower() or "kode verifikasi" in msg.lower()) and mail_try < max_mail_retry:
                    log_fn(f"[!] Email ini tidak menerima kode verifikasi, otomatis mengganti email baru dan mencoba kembali: {msg}")
                    restart_browser(log_callback=log_fn)
                    sleep_with_cancel(1, self.should_stop)
                    continue
                raise
        if not mail_ok:
            raise Exception("Tahap verifikasi Gagal, telah mencapai batas maksimal percobaan")
        log_fn(f"[*] Kode verifikasi: {code}")
        log_fn("[*] 4. Mengisi data")
        profile = fill_profile_and_submit(
            log_callback=log_fn, cancel_callback=self.should_stop
        )
        log_fn(f"[*] Data telah diisi: {profile.get('given_name')} {profile.get('family_name')}")
        log_fn("[*] 5. Menunggu sso cookie")
        sso = wait_for_sso_cookie(
            log_callback=log_fn, cancel_callback=self.should_stop
        )
        _cpa_page = _get_page()
        if config.get("cpa_export_enabled", True):
            cpa_async = bool(config.get("cpa_mint_async", True))
            if cpa_async:
                log_fn("[*] 6. Ekspor CPA xAI (Asinkron)")
                _cpa_bg_page = None
                def _cpa_mint_bg():
                    time.sleep(5)
                    try:
                        r = export_cpa_xai_for_account(
                            email, profile.get("password", ""), sso=sso,
                            log_callback=log_fn, page=_cpa_bg_page,
                        )
                        if r.get("ok"):
                            log_fn(f"[+] Ekspor CPA xAI Sukses: {r.get('path', '')}")
                        elif not r.get("skipped"):
                            log_fn(f"[!] Ekspor CPA xAI Gagal: {r.get('error', 'Kesalahan tidak diketahui')}")
                    except Exception as e:
                        log_fn(f"[!] Pengecualian ekspor CPA xAI: {e}")
                _t = threading.Thread(target=_cpa_mint_bg, daemon=True)
                _t.start()
                _track_cpa_async_thread(_t)
            else:
                log_fn("[*] 6. Ekspor CPA xAI (Sinkron)")
                cpa_result = export_cpa_xai_for_account(
                    email, profile.get("password", ""), sso=sso,
                    log_callback=log_fn, page=_cpa_page,
                )
                if cpa_result.get("ok"):
                    log_fn(f"[+] Ekspor CPA xAI Sukses: {cpa_result.get('path', '')}")
                elif not cpa_result.get("skipped"):
                    log_fn(f"[!] Ekspor CPA xAI Gagal: {cpa_result.get('error', 'Kesalahan tidak diketahui')}")
        if config.get("enable_nsfw", True):
            log_fn("[*] 6. Mengaktifkan NSFW")
            nsfw_ok, nsfw_msg = enable_nsfw_for_token(sso, log_callback=log_fn)
            if nsfw_ok:
                log_fn(f"[+] NSFW berhasil diaktifkan: {nsfw_msg}")
            else:
                log_fn(f"[!] NSFW tidak diaktifkan, melanjutkan penyimpanan akun: {nsfw_msg}")
        with _stats_lock:
            self.results.append({"email": email, "sso": sso, "profile": profile})
        try:
            line = f"{email}----{profile.get('password','')}----{sso}\n"
            with _io_lock:
                with open(self.accounts_output_file, "a", encoding="utf-8") as f:
                    f.write(line)
        except Exception as file_exc:
            log_fn(f"[Debug] Gagal menyimpan file akun: {file_exc}")
        add_token_to_grok2api_pools(sso, email=email, log_callback=log_fn)
        add_token_to_token_only_file(sso, log_callback=log_fn)
        with _stats_lock:
            self.success_count += 1
        log_fn(f"[+] Pendaftaran Sukses: {email}")

    def _run_single_worker(self, count, worker_id=0):
        _set_worker_id(worker_id)
        start_browser(log_callback=self.log)
        self.log("[*] Browser telah dimulai")
        restart_every = int(config.get("browser_restart_every", 10) or 0)
        i = 0
        retry_count_for_slot = 0
        max_slot_retry = 3
        while i < count:
            if self.should_stop():
                break
            self.log(f"--- Memulai akun ke-{i + 1}/{count} ---")
            try:
                self._register_one_account(self.log, worker_id, i)
                retry_count_for_slot = 0
                i += 1
                if restart_every > 0 and i > 0 and i % restart_every == 0:
                    self.log(f"[*] Telah mendaftar {i}  akun，restart browser")
                    restart_browser(log_callback=self.log)
                if (
                    self.success_count > 0
                    and self.success_count % MEMORY_CLEANUP_INTERVAL == 0
                    and i < count
                ):
                    cleanup_runtime_memory(
                        log_callback=self.log,
                        reason=f"Telah sukses {self.success_count} akun, menjalankan pembersihan berkala",
                    )
            except RegistrationCancelled:
                self.log("[!] Pendaftaran dihentikan oleh pengguna")
                break
            except AccountRetryNeeded as exc:
                retry_count_for_slot += 1
                if retry_count_for_slot <= max_slot_retry:
                    self.log(f"[!] Alur akun saat ini macet, mencoba kembali ke-{retry_count_for_slot}/{max_slot_retry}: {exc}")
                else:
                    with _stats_lock:
                        self.fail_count += 1
                    self.log(f"[-] Akun saat ini telah mencapai batas maksimal percobaan, lewati: {exc}")
                    retry_count_for_slot = 0
                    i += 1
            except Exception as exc:
                with _stats_lock:
                    self.fail_count += 1
                retry_count_for_slot = 0
                i += 1
                self.log(f"[-] Pendaftaran Gagal: {exc}")
            finally:
                self.update_stats()
                if self.should_stop():
                    break
                if _get_browser() is None:
                    start_browser(log_callback=self.log)
                else:
                    restart_browser(log_callback=self.log)
                sleep_with_cancel(1, self.should_stop)
        stop_browser()


def main():
    try:
        reset_9router_connections_status(print)
    except Exception:
        pass
        
    if len(sys.argv) > 1 and sys.argv[1].strip().lower() in ("start", "cli", "--cli"):
        if not check_license_cli():
            print("[!] Lisensi tidak valid, program CLI dihentikan.")
            sys.exit(1)
        main_cli()
        return
        
    root = tk.Tk()
    setup_light_theme(root)
    app = GrokRegisterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
