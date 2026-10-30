import os
import sys
from collections import deque

import customtkinter as ctk
import serial
import serial.tools.list_ports
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BAUD_RATE = 115200
BUFFER_LEN = 200      # number of samples shown on screen
UPDATE_MS = 30        # GUI refresh interval (~33 FPS)

# Put your IEEE logo image in the same folder as this script with this name.
# If the file isn't there, a text "IEEE" placeholder is shown instead.
LOGO_FILE = "ieee_logo.png"

ctk.set_appearance_mode("dark")

# The 6 values the Teensy sends, in order: ax,ay,az,gx,gy,gz
CHANNEL_NAMES = ["Acc X", "Acc Y", "Acc Z", "Gyro X", "Gyro Y", "Gyro Z"]

# Accent colours for the "Default" theme (picked from the Accent dropdown)
#ACCENTS = {
    #"IEEE Blue": "#00629B",
    #"Teal": "#12a58c",
    #"Green": "#2e9e5b",
    #"Orange": "#e67e22",
    #"Purple": "#8e44ad",
    #"Red": "#c0392b",
#}

# ---------------------------------------------------------------------------
# Themes. Each one sets: appearance mode, accent colour, sidebar colour,
# graph colours, and line/border thickness. (Colour palettes only - no artwork.)
# "sidebar": None means "use the normal CustomTkinter sidebar colour".
# ---------------------------------------------------------------------------
DEFAULT_THEMES = {
    "Dark": {
        "mode": "Dark", "accent": None, "sidebar": None,
        "plot": {"bg": "#1e1e1e", "fg": "#dddddd", "grid": "#444444", "spine": "#666666",
                 "legend_bg": "#2a2a2a", "legend_edge": "#555555"},
        "colors": ["#ff5c5c", "#5cff7a", "#5c9dff", "#4de8e8", "#ff66ff", "#ffe14d"],
        "linewidth": 1.4, "spine_width": 0.8,
    },
    "Light": {
        "mode": "Light", "accent": None, "sidebar": None,
        "plot": {"bg": "#ffffff", "fg": "#222222", "grid": "#cccccc", "spine": "#888888",
                 "legend_bg": "#f5f5f5", "legend_edge": "#bbbbbb"},
        "colors": ["#d62728", "#2ca02c", "#1f77b4", "#138d9e", "#b5179e", "#b38f00"],
        "linewidth": 1.4, "spine_width": 0.8,
    },
}

#THEMES = {
    #"Shrek Swamp": {
        #"mode": "Dark", "accent": "#5f8f12", "sidebar": "#2b3a1f",
        #"plot": {"bg": "#1f2a16", "fg": "#e6f0c8", "grid": "#3e5230", "spine": "#7aa63a",
                 #"legend_bg": "#2b3a1f", "legend_edge": "#7aa63a"},
        #"colors": ["#b5e61d", "#f2c14e", "#f4802f", "#d2b48c", "#3fc9a0", "#7fd1ff"],
        #"linewidth": 2.0, "spine_width": 1.2,
    #},
    #"Toon Night": {
        #"mode": "Dark", "accent": "#c2389b", "sidebar": "#1b1340",
        #"plot": {"bg": "#241a55", "fg": "#fff1a8", "grid": "#3d2f85", "spine": "#ffd93d",
                 #"legend_bg": "#1b1340", "legend_edge": "#ffd93d"},
        #"colors": ["#ffd93d", "#6bf5ff", "#ff6bcb", "#7dff6b", "#ff9a3d", "#b88cff"],
        #"linewidth": 2.6, "spine_width": 1.8,
    #},
#}

#PRESET_NAMES = ["Default"] + list(THEMES.keys())


def darken(hex_color, factor=0.8):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * factor), int(g * factor), int(b * factor))


class IMUDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MPU6500 Live Sensor Dashboard")
        self.geometry("1250x800")
        self.minsize(950, 600)

        self.ser = None
        self.paused = False
        self.new_data = False
        self.port_map = {}
        self.preset = "Default"
        #self.accent_name = "IEEE Blue"          # last accent chosen from the dropdown
        #self.accent = ACCENTS[self.accent_name]
        self.buffers = [deque([0.0] * BUFFER_LEN, maxlen=BUFFER_LEN) for _ in range(6)]
        self.x_data = list(range(BUFFER_LEN))

        # Widgets that get recoloured when the accent changes
        #self.accent_switches = []
        #self.accent_menus = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_plots()
        #self.apply_plot_theme()
        #self.apply_accent()
        self.refresh_ports()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(UPDATE_MS, self.poll)

    # ---------- UI ----------
    def build_logo(self, parent):
        self.logo_placeholder = None
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO_FILE)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                w = 190
                h = max(1, int(img.height * w / img.width))
                self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
                ctk.CTkLabel(parent, image=self.logo_img, text="").pack(pady=(12, 4))
                return
            except Exception as e:
                print(f"Could not load logo '{LOGO_FILE}': {e}")
        self.logo_placeholder = ctk.CTkLabel(parent, text="IEEE",
                                             font=ctk.CTkFont(size=38, weight="bold"),
                                             text_color="#00629B")
        self.logo_placeholder.pack(pady=(12, 4))

    def make_switch(self, parent, **kwargs):
        sw = ctk.CTkSwitch(parent, **kwargs)
        #self.accent_switches.append(sw)
        return sw

    def build_sidebar(self):
        sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar = sidebar
        self.default_sidebar_color = tuple(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

        self.build_logo(sidebar)
        ctk.CTkLabel(sidebar, text="IMU Dashboard",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 14), padx=10)

        # --- Connection ---
        ctk.CTkLabel(sidebar, text="Serial port").pack(padx=10, anchor="w")
        self.port_menu = ctk.CTkOptionMenu(sidebar, values=["No ports found"])
        self.port_menu.pack(padx=10, pady=(2, 8), fill="x")
        #self.accent_menus.append(self.port_menu)

        ctk.CTkButton(sidebar, text="Refresh ports", fg_color="gray40", hover_color="gray30",
                      command=self.refresh_ports).pack(padx=10, pady=(0, 10), fill="x")

        self.connect_btn = ctk.CTkButton(sidebar, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(padx=10, pady=(0, 6), fill="x")

        self.status_label = ctk.CTkLabel(sidebar, text="Disconnected", text_color="#ff6b6b")
        self.status_label.pack(padx=10, anchor="w")

        # --- Graph controls ---
        self.pause_switch = self.make_switch(sidebar, text="Pause graphs", command=self.toggle_pause)
        self.pause_switch.pack(padx=10, pady=(16, 8), anchor="w")

        #ctk.CTkButton(sidebar, text="Clear graphs", fg_color="gray40", hover_color="gray30",
                      #command=self.clear_graphs).pack(padx=10, pady=(0, 16), fill="x")

        # --- Live values (master switch + one switch per value) ---
        #self.master_switch = self.make_switch(sidebar, text="Show live values",
                                              #font=ctk.CTkFont(size=14, weight="bold"),
                                              #command=self.toggle_master)
        #self.master_switch.select()
        #self.master_switch.pack(padx=10, pady=(0, 2), anchor="w")

        self.values_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.values_frame.pack(fill="x")

        ctk.CTkLabel(self.values_frame, text="Each switch controls the number and its graph line",
                     text_color="gray60", font=ctk.CTkFont(size=11),
                     wraplength=220, justify="left").pack(padx=10, pady=(0, 4), anchor="w")

        self.value_switches = []
        self.value_labels = []
        for i, name in enumerate(CHANNEL_NAMES):
            row = ctk.CTkFrame(self.values_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            sw = self.make_switch(row, text=name, width=110,
                                  command=lambda idx=i: self.toggle_value(idx))
            sw.select()
            sw.pack(side="left")
            lbl = ctk.CTkLabel(row, text="0.000", anchor="e")
            lbl.pack(side="right")
            self.value_switches.append(sw)
            self.value_labels.append(lbl)

        ctk.CTkLabel(self.values_frame, text="Acc in g  |  Gyro in deg/s",
                     text_color="gray60", font=ctk.CTkFont(size=11)).pack(padx=10, pady=(8, 0), anchor="w")

        # --- Theme ---
        #ctk.CTkLabel(sidebar, text="Theme",
                     #font=ctk.CTkFont(size=14, weight="bold")).pack(padx=10, pady=(20, 4), anchor="w")

        #ctk.CTkLabel(sidebar, text="Theme preset").pack(padx=10, anchor="w")
        #self.preset_menu = ctk.CTkOptionMenu(sidebar, values=PRESET_NAMES, command=self.change_preset)
        #self.preset_menu.set("Default")
        #self.preset_menu.pack(padx=10, pady=(2, 8), fill="x")
        #self.accent_menus.append(self.preset_menu)

        #ctk.CTkLabel(sidebar, text="Appearance").pack(padx=10, anchor="w")
        #self.appearance_btn = ctk.CTkSegmentedButton(sidebar, values=["Dark", "Light", "System"],
                                                     #command=self.change_appearance)
        #self.appearance_btn.set("Dark")
        #self.appearance_btn.pack(padx=10, pady=(2, 8), fill="x")

        #ctk.CTkLabel(sidebar, text="Accent colour").pack(padx=10, anchor="w")
        #self.accent_menu = ctk.CTkOptionMenu(sidebar, values=list(ACCENTS.keys()),
                                             #command=self.change_accent)
        #self.accent_menu.set(self.accent_name)
        #self.accent_menu.pack(padx=10, pady=(2, 10), fill="x")
        #self.accent_menus.append(self.accent_menu)

    def build_plots(self):
        self.plot_frame = ctk.CTkFrame(self, corner_radius=0)
        self.plot_frame.grid(row=0, column=1, sticky="nsew")

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax_acc = self.fig.add_subplot(211)
        self.ax_gyr = self.fig.add_subplot(212)
        self.fig.subplots_adjust(left=0.07, right=0.98, top=0.94, bottom=0.07, hspace=0.3)

        self.lines = []  # index i matches channel i (0-2 accelerometer, 3-5 gyro)
        for ax, title, idx in ((self.ax_acc, "Accelerometer (g)", range(0, 3)),
                               (self.ax_gyr, "Gyroscope (deg/s)", range(3, 6))):
            ax.set_title(title, fontsize=11)
            ax.set_xlim(0, BUFFER_LEN - 1)
            for i in idx:
                (line,) = ax.plot(self.x_data, list(self.buffers[i]), label=CHANNEL_NAMES[i])
                self.lines.append(line)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------- Theming ----------
    #def current_theme(self):
        #if self.preset != "Default":
            #return THEMES[self.preset]
        #return DEFAULT_THEMES.get(ctk.get_appearance_mode(), DEFAULT_THEMES["Dark"])

    #def apply_plot_theme(self):
        #th = self.current_theme()
        #t = th["plot"]

        #self.sidebar.configure(fg_color=th["sidebar"] or self.default_sidebar_color)
        #self.plot_frame.configure(fg_color=t["bg"])

        #self.fig.set_facecolor(t["bg"])
        #for ax in (self.ax_acc, self.ax_gyr):
            #ax.set_facecolor(t["bg"])
            #ax.title.set_color(t["fg"])
            #ax.tick_params(colors=t["fg"], labelsize=9)
            #ax.grid(True, color=t["grid"], linewidth=0.6)
            #for spine in ax.spines.values():
                #spine.set_color(t["spine"])
                #spine.set_linewidth(th["spine_width"])

        #for line, color in zip(self.lines, th["colors"]):
            #line.set_color(color)
            #line.set_linewidth(th["linewidth"])

        #for sw, color in zip(self.value_switches, th["colors"]):
            #sw.configure(text_color=color)

        #self.rebuild_legends()
        #self.canvas.draw_idle()

    def rebuild_legends(self):
        """Legends only list the lines that are currently visible."""
        t = DEFAULT_THEMES.get(ctk.get_appearance_mode(), DEFAULT_THEMES["Dark"])["plot"]
        for ax, group in ((self.ax_acc, self.lines[0:3]), (self.ax_gyr, self.lines[3:6])):
            old = ax.get_legend()
            if old is not None:
                old.remove()
            visible = [ln for ln in group if ln.get_visible()]
            if not visible:
                continue
            legend = ax.legend(handles=visible, loc="upper right", fontsize=8, ncol=3,
                               facecolor=t["legend_bg"], edgecolor=t["legend_edge"])
            for text in legend.get_texts():
                text.set_color(t["fg"])

    #def apply_accent(self):
        #hover = darken(self.accent, 0.8)
        #for sw in self.accent_switches:
            #sw.configure(progress_color=self.accent)
        #for menu in self.accent_menus:
            #menu.configure(fg_color=self.accent, button_color=hover,
                           #button_hover_color=darken(self.accent, 0.65))
        #self.appearance_btn.configure(selected_color=self.accent, selected_hover_color=hover)
        #if self.ser is None:
            #self.connect_btn.configure(fg_color=self.accent, hover_color=hover)
        #if self.logo_placeholder is not None:
            #self.logo_placeholder.configure(text_color=self.accent)

    #def change_preset(self, choice):
        #self.preset = choice
        #if choice == "Default":
            #ctk.set_appearance_mode(self.appearance_btn.get())
            #elf.accent = ACCENTS[self.accent_name]
            #self.accent_menu.set(self.accent_name)
        #else:
            #th = THEMES[choice]
            #ctk.set_appearance_mode(th["mode"])
            #self.appearance_btn.set(th["mode"])
            #self.accent = th["accent"]
            #self.accent_menu.set("From theme")
        #self.apply_plot_theme()
        #self.apply_accent()

    #def change_appearance(self, choice):
        # Picking Dark/Light/System goes back to the Default theme in that mode
        #self.appearance_btn.set(choice)
        #self.preset_menu.set("Default")
        #self.change_preset("Default")

    #def change_accent(self, choice):
        #self.accent_name = choice
        #self.accent = ACCENTS[choice]
        #self.apply_accent()

    # ---------- Serial ----------
    def refresh_ports(self):
        self.port_map = {}
        for p in serial.tools.list_ports.comports():
            self.port_map[f"{p.device} - {p.description}"] = p.device
        names = list(self.port_map.keys()) or ["No ports found"]
        self.port_menu.configure(values=names)
        self.port_menu.set(names[0])

    def toggle_connection(self):
        if self.ser is None:
            self.connect()
        else:
            self.disconnect()

    def connect(self):
        port = self.port_map.get(self.port_menu.get())
        if port is None:
            self.set_status("No port selected", "#ff6b6b")
            return
        try:
            # Only one program can use a COM port at a time - close any serial monitor first
            self.ser = serial.Serial(port, BAUD_RATE, timeout=0.01)
            self.ser.reset_input_buffer()
        except Exception as e:
            self.ser = None
            self.set_status(f"Error: {e}", "#ff6b6b")
            return
        self.connect_btn.configure(text="Disconnect", fg_color="#c0392b", hover_color="#e74c3c")
        self.set_status(f"Connected: {port}", "#4cd964")

    def disconnect(self):
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None
        self.connect_btn.configure(text="Connect", fg_color="#00629B",
                                   hover_color=darken("#00629B", 0.8))
        self.set_status("Disconnected", "#ff6b6b")

    def set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

    # ---------- Controls ----------
    def toggle_pause(self):
        self.paused = bool(self.pause_switch.get())

    #def clear_graphs(self):
        #for buf in self.buffers:
            #for _ in range(BUFFER_LEN):
                #buf.append(0.0)
        #self.new_data = True

    #def toggle_master(self):
        #if self.master_switch.get():
            #self.values_frame.pack(fill="x", after=self.master_switch)
        #else:
            #self.values_frame.pack_forget()

    def toggle_value(self, idx):
        """One switch controls both the number readout and the graph line for that channel."""
        on = bool(self.value_switches[idx].get())
        self.lines[idx].set_visible(on)
        self.value_labels[idx].configure(text=f"{self.buffers[idx][-1]:8.3f}" if on else "")
        self.rebuild_legends()
        self.update_plots()

    # ---------- Main loop ----------
    def poll(self):
        if self.ser is not None:
            try:
                while self.ser.in_waiting:
                    line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                    if not line or self.paused:
                        continue  # while paused, read and discard so the buffer doesn't fill up
                    try:
                        vals = [float(v) for v in line.split(",")]
                    except ValueError:
                        print(f"Skipped non-data line: {line}")
                        continue
                    if len(vals) == 6:
                        for buf, v in zip(self.buffers, vals):
                            buf.append(v)
                        self.new_data = True
                    else:
                        print(f"Expected 6 values, got {len(vals)}: {line}")
            except (serial.SerialException, OSError) as e:
                print(f"Serial error (Teensy unplugged?): {e}")
                self.disconnect()
                self.set_status("Connection lost", "#ff6b6b")

        if self.new_data:
            self.update_plots()
            self.new_data = False

        self.after(UPDATE_MS, self.poll)

    def update_plots(self):
        for line, buf in zip(self.lines, self.buffers):
            line.set_data(self.x_data, list(buf))
        for ax in (self.ax_acc, self.ax_gyr):
            ax.relim(visible_only=True)   # scale the axis to the lines that are shown
            ax.autoscale_view(scalex=False, scaley=True)
        #if self.master_switch.get():
            #for sw, lbl, buf in zip(self.value_switches, self.value_labels, self.buffers):
                #if sw.get():
                    #lbl.configure(text=f"{buf[-1]:8.3f}")
        self.canvas.draw_idle()

    def on_close(self):
        self.disconnect()
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = IMUDashboard()
    app.mainloop()