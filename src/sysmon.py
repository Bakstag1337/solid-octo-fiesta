#!/usr/bin/env python3
"""
Desktop System Monitor - Beautiful real-time system stats on your desktop
Sticks to wallpaper like Conky!
"""

import tkinter as tk
from tkinter import ttk
import psutil
import platform
from datetime import timedelta
import threading
import time
import subprocess
import os


class SystemMonitor(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window configuration - stick to desktop!
        self.title("System Monitor")
        self.overrideredirect(True)  # No window decorations
        self.attributes('-alpha', 0.85)  # Semi-transparent

        # Try to set window type to desktop (X11)
        try:
            self.attributes('-type', 'desktop')
        except:
            pass

        # Window size and position (bottom right corner by default)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        widget_width = 350
        widget_height = 480

        # Position in bottom-right corner with some padding
        x_pos = screen_width - widget_width - 20
        y_pos = 60  # Top position

        self.geometry(f"{widget_width}x{widget_height}+{x_pos}+{y_pos}")
        self.resizable(False, False)

        # Configure dark theme colors with more transparency
        self.bg_color = "#1a1a1a"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4ff"

        self.configure(bg=self.bg_color)

        # Variables for drag
        self._drag_data = {"x": 0, "y": 0}

        # Create UI
        self.create_widgets()

        # Set window to stay on desktop (below all windows)
        self.after(100, self.stick_to_desktop)

        # Start monitoring
        self.update_interval = 1000  # 1 second
        self.running = True
        self.update_stats()

        # Bind dragging events (right-click to drag)
        self.bind("<Button-3>", self.start_drag)
        self.bind("<ButtonRelease-3>", self.stop_drag)
        self.bind("<B3-Motion>", self.on_drag)

        # Double-click to close
        self.bind("<Double-Button-1>", lambda e: self.on_closing())

    def stick_to_desktop(self):
        """Make window stick to desktop background using wmctrl"""
        try:
            # Get window ID
            window_id = self.wm_frame()

            # Try wmctrl first
            subprocess.run([
                'wmctrl', '-i', '-r', str(window_id),
                '-b', 'add,below,sticky'
            ], check=False, capture_output=True)

            # Also try setting window type
            subprocess.run([
                'xprop', '-id', str(window_id),
                '-f', '_NET_WM_WINDOW_TYPE', '32a',
                '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DESKTOP'
            ], check=False, capture_output=True)

        except Exception as e:
            # Fallback: just put it below other windows
            try:
                self.attributes('-topmost', False)
                self.lower()
            except:
                pass

    def create_widgets(self):
        # Main container with border
        main_frame = tk.Frame(self, bg=self.bg_color, padx=15, pady=15,
                             highlightbackground=self.accent_color,
                             highlightthickness=1)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header with close button
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        # Title
        title = tk.Label(
            header_frame,
            text="⚡ System Monitor",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color,
            anchor="w"
        )
        title.pack(side=tk.LEFT)

        # Close button
        close_btn = tk.Label(
            header_frame,
            text="✕",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg="#ff5555",
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.on_closing())

        # Control hint
        hint_label = tk.Label(
            main_frame,
            text="Double-click ✕ to close | Right-click to drag",
            font=("Arial", 7),
            bg=self.bg_color,
            fg="#555555"
        )
        hint_label.pack(pady=(0, 10))

        # Hostname
        hostname = platform.node()
        host_label = tk.Label(
            main_frame,
            text=f"🖥️  {hostname}",
            font=("Arial", 10),
            bg=self.bg_color,
            fg="#888888"
        )
        host_label.pack(pady=(0, 15))

        # CPU Section
        self.create_section(main_frame, "💻 CPU", "cpu")

        # RAM Section
        self.create_section(main_frame, "🧠 RAM", "ram")

        # Disk Section
        self.create_section(main_frame, "💾 Disk", "disk")

        # Network Section
        self.create_section(main_frame, "🌐 Network", "net")

        # Temperature Section (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                self.create_section(main_frame, "🌡️  Temperature", "temp")
        except:
            pass

        # Uptime Section
        self.uptime_label = tk.Label(
            main_frame,
            text="⏱️  Uptime: Loading...",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="#888888",
            anchor="w"
        )
        self.uptime_label.pack(fill=tk.X, pady=(10, 0))

    def create_section(self, parent, title, section_id):
        # Section frame
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.X, pady=8)

        # Title
        title_label = tk.Label(
            frame,
            text=title,
            font=("Arial", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor="w"
        )
        title_label.pack(fill=tk.X)

        # Progress bar
        style_name = f"{section_id}.Horizontal.TProgressbar"
        style = ttk.Style()

        # Configure style based on section
        if section_id == "cpu":
            color = "#00ff88"
        elif section_id == "ram":
            color = "#ffaa00"
        elif section_id == "disk":
            color = "#ff5555"
        elif section_id == "net":
            color = "#5599ff"
        elif section_id == "temp":
            color = "#ff6b6b"
        else:
            color = "#888888"

        style.configure(
            style_name,
            troughcolor=self.bg_color,
            background=color,
            bordercolor=self.bg_color,
            lightcolor=color,
            darkcolor=color
        )

        progress = ttk.Progressbar(
            frame,
            style=style_name,
            length=300,
            mode='determinate'
        )
        progress.pack(fill=tk.X, pady=(5, 2))

        # Info label
        info_label = tk.Label(
            frame,
            text="Loading...",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="#aaaaaa",
            anchor="w"
        )
        info_label.pack(fill=tk.X)

        # Store references
        setattr(self, f"{section_id}_progress", progress)
        setattr(self, f"{section_id}_label", info_label)

    def update_stats(self):
        if not self.running:
            return

        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()

            self.cpu_progress['value'] = cpu_percent
            freq_ghz = cpu_freq.current / 1000 if cpu_freq else 0
            self.cpu_label.config(
                text=f"{cpu_percent:.1f}% | {cpu_count} cores | {freq_ghz:.2f} GHz",
                fg=self.get_color(cpu_percent)
            )

            # RAM
            ram = psutil.virtual_memory()
            ram_used_gb = ram.used / (1024**3)
            ram_total_gb = ram.total / (1024**3)

            self.ram_progress['value'] = ram.percent
            self.ram_label.config(
                text=f"{ram.percent:.1f}% | {ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB",
                fg=self.get_color(ram.percent)
            )

            # Disk
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)

            self.disk_progress['value'] = disk.percent
            self.disk_label.config(
                text=f"{disk.percent:.1f}% | {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB",
                fg=self.get_color(disk.percent)
            )

            # Network
            if not hasattr(self, '_last_net_io'):
                self._last_net_io = psutil.net_io_counters()
                self._last_net_time = time.time()
                net_text = "Measuring..."
            else:
                current_net = psutil.net_io_counters()
                current_time = time.time()
                time_delta = current_time - self._last_net_time

                bytes_sent = (current_net.bytes_sent - self._last_net_io.bytes_sent) / time_delta
                bytes_recv = (current_net.bytes_recv - self._last_net_io.bytes_recv) / time_delta

                # Convert to human readable
                sent_str = self.format_bytes(bytes_sent)
                recv_str = self.format_bytes(bytes_recv)

                net_text = f"↑ {sent_str}/s | ↓ {recv_str}/s"

                self._last_net_io = current_net
                self._last_net_time = current_time

                # Show activity (0-100 based on MB/s, max at 10 MB/s)
                total_mbps = (bytes_sent + bytes_recv) / (1024 * 1024)
                net_percent = min(total_mbps * 10, 100)
                self.net_progress['value'] = net_percent

            self.net_label.config(text=net_text, fg="#aaaaaa")

            # Temperature (if available)
            if hasattr(self, 'temp_progress'):
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Try to get CPU temp from common sources
                        temp_value = None
                        for name, entries in temps.items():
                            if 'coretemp' in name.lower() or 'cpu' in name.lower():
                                if entries:
                                    temp_value = entries[0].current
                                    break

                        if temp_value is None and temps:
                            # Fallback to first available
                            temp_value = list(temps.values())[0][0].current

                        if temp_value:
                            # Scale temperature to 0-100 (assuming 0-100°C range)
                            temp_percent = min(temp_value, 100)
                            self.temp_progress['value'] = temp_percent
                            self.temp_label.config(
                                text=f"{temp_value:.1f}°C",
                                fg=self.get_temp_color(temp_value)
                            )
                except:
                    pass

            # Uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            self.uptime_label.config(text=f"⏱️  Uptime: {uptime_str}")

        except Exception as e:
            print(f"Error updating stats: {e}")

        # Schedule next update
        self.after(self.update_interval, self.update_stats)

    def get_color(self, percent):
        """Get color based on percentage"""
        if percent < 50:
            return "#00ff88"  # Green
        elif percent < 80:
            return "#ffaa00"  # Orange
        else:
            return "#ff5555"  # Red

    def get_temp_color(self, temp):
        """Get color based on temperature"""
        if temp < 60:
            return "#00ff88"  # Green
        elif temp < 80:
            return "#ffaa00"  # Orange
        else:
            return "#ff5555"  # Red

    def format_bytes(self, bytes_val):
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB"

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def stop_drag(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def on_drag(self, event):
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        x = self.winfo_x() + delta_x
        y = self.winfo_y() + delta_y
        self.geometry(f"+{x}+{y}")

    def on_closing(self):
        self.running = False
        self.destroy()


def main():
    print("Starting Desktop System Monitor...")
    print("Close the window or press Ctrl+C to exit.")

    app = SystemMonitor()

    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
        app.running = False


if __name__ == "__main__":
    main()
