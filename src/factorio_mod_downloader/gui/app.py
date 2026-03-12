"""
Main Application Window for the Factorio Mod Downloader.
"""

import ctypes
import ctypes.wintypes
import customtkinter

from factorio_mod_downloader.gui.frames import BodyFrame
from factorio_mod_downloader.gui.frames import DownloaderFrame
from factorio_mod_downloader.gui.utils import resource_path


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize the main application window."""
        super().__init__(fg_color="#1a1a1d")
        self.resizable(True, True)
        self.title("Factorio Mod Downloader v0.3.0")
        self.geometry(f"{1100}x{860}")

        try:
            self.iconbitmap(resource_path("factorio_downloader.ico"))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        # Apply dark native title bar using DWM after the window is rendered
        self.after(50, self._apply_dark_titlebar)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create the downloader frame (right side - progress tracking)
        self.DownloaderFrame = DownloaderFrame(self, "Downloads")
        self.DownloaderFrame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        # Create the body frame (left side - input controls)
        self.BodyFrame = BodyFrame(self, self.DownloaderFrame)
        self.BodyFrame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Make references accessible for the downloader thread
        self.downloader_frame = self.DownloaderFrame
        self.progress_file = self.BodyFrame.progress_file
        self.progressbar = self.BodyFrame.progressbar
        self.download_button = self.BodyFrame.download_button
        self.textbox = self.BodyFrame.textbox

    def _apply_dark_titlebar(self):
        """
        Use the Windows DWM API to set the title bar and caption color
        so the native controls look at home with the dark Factorio theme.
        Works on Windows 10 (dark mode) and Windows 11 (caption color).
        """
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

            # Enable dark mode immersive title bar (Windows 10 20H1+ / Windows 11)
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )

            # Windows 11: set exact caption (title bar) background color
            # DWMWA_CAPTION_COLOR = 35  (available since Windows 11 Build 22000)
            # Color format: 0x00BBGGRR
            DWMWA_CAPTION_COLOR = 35
            # #3e3c38 → R=0x3e, G=0x3c, B=0x38 → 0x00383c3e
            caption_color = ctypes.c_int(0x00383C3E)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                ctypes.byref(caption_color),
                ctypes.sizeof(caption_color),
            )

            # Windows 11: set title text color
            # DWMWA_TEXT_COLOR = 36
            DWMWA_TEXT_COLOR = 36
            # #E6E1D6 → R=0xE6, G=0xE1, B=0xD6 → 0x00D6E1E6
            text_color = ctypes.c_int(0x00D6E1E6)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_TEXT_COLOR,
                ctypes.byref(text_color),
                ctypes.sizeof(text_color),
            )

        except Exception as e:
            print(f"DWM styling failed (may not be supported on this OS version): {e}")
