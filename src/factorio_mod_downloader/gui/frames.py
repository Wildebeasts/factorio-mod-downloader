"""
GUI Components and Frames for the Factorio Mod Downloader.
"""

import re
import webbrowser
from pathlib import Path
from tkinter import END
from tkinter import filedialog

import customtkinter
from CTkMessagebox import CTkMessagebox
from PIL import Image

from factorio_mod_downloader.gui.utils import resource_path


download_icon = customtkinter.CTkImage(Image.open(resource_path("icons/download.png")), size=(16, 16))
success_icon = customtkinter.CTkImage(Image.open(resource_path("icons/check.png")), size=(16, 16))
error_icon = customtkinter.CTkImage(Image.open(resource_path("icons/error.png")), size=(16, 16))
warning_icon = customtkinter.CTkImage(Image.open(resource_path("icons/warning.png")), size=(16, 16))


class DownloadEntry:
    """Represents a single download entry with status and progress."""

    def __init__(self, file_name, frame, icon_label, text_label, sub_label, progress_bar):
        self.file_name = file_name
        self.frame = frame
        self.icon_label = icon_label
        self.text_label = text_label
        self.sub_label = sub_label
        self.progress_bar = progress_bar

    def update_progress(self, percent: float, downloaded_mb: float, total_mb: float, speed: float):
        """Update progress visuals."""
        self.progress_bar.set(percent)
        self.sub_label.configure(
            text=f"{percent * 100:.1f}% — {downloaded_mb:.1f} MB / {total_mb:.1f} MB @ {speed:.1f} MB/s"
        )

    def mark_complete(self):
        """Mark the download as complete."""
        self.icon_label.configure(image=success_icon)
        self.sub_label.configure(text="Completed successfully.", text_color="#65A63F")
        self.progress_bar.set(1.0)
        self.progress_bar.configure(progress_color="#65A63F")  # factorio green

    def mark_failed(self, error_msg: str):
        """Mark the download as failed."""
        self.icon_label.configure(image=error_icon)
        self.sub_label.configure(text=f"Error: {error_msg}", text_color="#E32D2D")
        self.progress_bar.configure(progress_color="#E32D2D")  # factorio red

    def mark_warning(self, error_msg: str):
        self.icon_label.configure(image=warning_icon)

    def mark_retrying(self, attempt: int, max_attempts: int):
        """Mark the download as retrying."""
        self.icon_label.configure(image=warning_icon)  # orange warning icon
        self.sub_label.configure(text=f"Retrying... ({attempt}/{max_attempts})", text_color="#FF9F1C")
        self.progress_bar.configure(progress_color="#FF9F1C")


class DownloaderFrame(customtkinter.CTkScrollableFrame):
    """Scrollable frame displaying active downloads with progress bars."""

    def __init__(self, master, title):
        super().__init__(master, height=500, width=300, label_text=title, fg_color="#242322", label_fg_color="#3e3c38", label_text_color="#FF9F1C")
        self.grid_columnconfigure(0, weight=1)
        self.frames = []

        self.container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=5)

    def _setup_downloads_frame(self, label: str):
        """Setup the UI for one download entry, inside a bordered box."""
        downloads_frame = customtkinter.CTkFrame(master=self.container, fg_color="#1a1a1d", border_width=2, border_color="#3e3c38")
        downloads_frame.pack(fill="x", pady=5)  # more padding for separation

        label_container = customtkinter.CTkFrame(master=downloads_frame, fg_color="transparent")
        label_container.pack(side="top", fill="x", padx=12, pady=(6, 0))

        icon_label = customtkinter.CTkLabel(master=label_container, image=download_icon, text="")
        icon_label.pack(side="left")

        # File name label
        text_label = customtkinter.CTkLabel(
            master=label_container,
            text=f"{label}",
            font=customtkinter.CTkFont(family="Segoe UI Semibold", weight="bold"),
            text_color="#E6E1D6",
            anchor="w",
            justify="left",
        )
        text_label.pack(side="left", padx=(8, 0), fill="x", expand=True)

        # Subtext for progress details
        sub_label = customtkinter.CTkLabel(
            master=downloads_frame,
            text="Starting...",
            font=customtkinter.CTkFont(family="Segoe UI", size=11),
            text_color="gray70",
            anchor="w",
            justify="left",
        )
        sub_label.pack(side="top", fill="x", padx=12, pady=(0, 0))

        # Progress bar
        progress_bar = customtkinter.CTkProgressBar(
            downloads_frame,
            orientation="horizontal",
            width=260,
            mode="determinate",
            progress_color="#FF9F1C",
            fg_color="#242322",
            border_color="#3e3c38",
            border_width=1,
        )
        progress_bar.set(0)
        progress_bar.pack(side="top", fill="x", padx=12, pady=(4, 10))

        return downloads_frame, icon_label, text_label, sub_label, progress_bar

    def add_download(self, file_name: str):
        """Add a new download entry."""
        frame, icon_label, text_label, sub_label, progress_bar = self._setup_downloads_frame(file_name)
        entry = DownloadEntry(file_name, frame, icon_label, text_label, sub_label, progress_bar)
        self.frames.append(entry)
        self.update_idletasks()

        try:
            self._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

        return entry


class BodyFrame(customtkinter.CTkFrame):
    """Main content frame with input controls and download status."""

    def __init__(self, master, downloader_frame):
        """
        Initialize the body frame.

        Args:
            master: Parent widget (the main App)
            downloader_frame: Reference to the DownloaderFrame
        """
        super().__init__(master, fg_color="#1a1a1d")
        self.app = master
        self.frame_0 = customtkinter.CTkFrame(master=self, fg_color="#2d2b29", border_width=2, border_color="#3e3c38")
        self.frame_0.pack(expand=True, pady=10, padx=10, fill="both")
        self.frame_0.grid_rowconfigure(0, weight=0)  # title
        self.frame_0.grid_rowconfigure(1, weight=0)  # inputs
        self.frame_0.grid_rowconfigure(2, weight=0)  # progress bar
        self.frame_0.grid_rowconfigure(3, weight=1)  # log textbox — takes all remaining height
        self.frame_0.grid_columnconfigure(0, weight=1)

        self.downloader_frame = downloader_frame
        self._setup_ui()

    def _setup_ui(self):
        """Initialize all UI components."""
        self._setup_title_frame()
        self._setup_body_frame()
        self._setup_downloads_frame()
        self._setup_textbox()

    def _setup_title_frame(self):
        """Setup title section with application info."""
        self.title_frame = customtkinter.CTkFrame(master=self.frame_0, fg_color="#3e3c38", corner_radius=0)
        self.title_frame.grid(row=0, column=0, sticky="new")
        self.title_frame.grid_rowconfigure(0, weight=1)
        self.title_frame.grid_rowconfigure(3, weight=1)

        self.title_label = customtkinter.CTkLabel(
            master=self.title_frame,
            text="Factorio Mod Downloader",
            text_color="#FF9F1C",
            font=customtkinter.CTkFont(family="Segoe UI Semibold", size=20, weight="bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, padx=10, pady=(10, 0), sticky="nsew")

        self.title_sub_label = customtkinter.CTkLabel(
            master=self.title_frame,
            text="One Downloader for all your factorio mods.",
            font=customtkinter.CTkFont(family="Segoe UI"),
            text_color="#E6E1D6",
        )
        self.title_sub_label.grid(row=1, padx=12, sticky="nsw")

        github_repo = "https://github.com/vaibhavvikas/factorio-mod-downloader"
        github_url = f"Made with ♥ by Vaibhav Vikas, {github_repo}"

        self.developer_label = customtkinter.CTkLabel(
            master=self.title_frame,
            text=github_url,
            font=customtkinter.CTkFont(family="Segoe UI Emoji"),
            text_color="#A19D94",
            cursor="hand2",
        )
        self.developer_label.grid(row=2, padx=12, pady=(0, 10), sticky="nsw")
        self.developer_label.bind(
            "<Button-1>",
            lambda e: self._callback(github_repo),
        )

    def _setup_body_frame(self):
        """Setup input controls section."""
        self.body_frame = customtkinter.CTkFrame(master=self.frame_0, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self.body_frame.grid_columnconfigure(0, weight=1)
        self.body_frame.grid_columnconfigure(3, weight=0)

        self.mod_url_label = customtkinter.CTkLabel(
            master=self.body_frame, text="Mod URL", text_color="#ff9f1c",
            font=customtkinter.CTkFont(family="Segoe UI Semibold", weight="bold"), anchor="w"
        )
        self.mod_url_label.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 2), sticky="nsw")

        self.mod_url = customtkinter.CTkEntry(
            self.body_frame, placeholder_text="Enter mod url here...", width=500,
            fg_color="#1a1a1d", border_color="#3e3c38", text_color="#e6e1d6"
        )
        self.mod_url.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")

        self.fetch_deps_button = customtkinter.CTkButton(
            master=self.body_frame, border_width=2,
            border_color="#3e3c38", fg_color="#2d2b29", hover_color="#4a4743",
            text_color="#ff9f1c", text="Check Deps", command=self._fetch_deps_action,
        )
        self.fetch_deps_button.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="nsew")

        self.download_path_label = customtkinter.CTkLabel(
            master=self.body_frame, text="Download Path", text_color="#ff9f1c",
            font=customtkinter.CTkFont(family="Segoe UI Semibold", weight="bold"), anchor="w"
        )
        self.download_path_label.grid(row=2, column=0, columnspan=4, padx=10, pady=(5, 2), sticky="nsw")

        self.download_path = customtkinter.CTkEntry(
            self.body_frame, placeholder_text="Enter output path here...", width=500,
            fg_color="#1a1a1d", border_color="#3e3c38", text_color="#e6e1d6"
        )
        self.download_path.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")

        self.path_button = customtkinter.CTkButton(
            master=self.body_frame, border_width=2,
            border_color="#3e3c38", fg_color="#2d2b29", hover_color="#4a4743",
            text_color="#ff9f1c", text="Browse", command=self._select_path,
        )
        self.path_button.grid(row=3, column=3, padx=10, pady=(0, 10), sticky="nsew")

        self.deps_container = customtkinter.CTkScrollableFrame(
            master=self.body_frame, fg_color="#1a1a1d", border_color="#3e3c38", border_width=2, height=100
        )
        self.deps_container.grid(row=4, column=0, columnspan=4, padx=10, pady=(10, 10), sticky="nsew")
        
        self.optional_deps_vars = {}

        deps_prompt = customtkinter.CTkLabel(
            self.deps_container, text="Click 'Check Deps' to load dependencies.", text_color="#A19D94"
        )
        deps_prompt.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.download_button = customtkinter.CTkButton(
            master=self.body_frame, text="START DOWNLOAD", command=self._download_button_action,
            font=customtkinter.CTkFont(family="Segoe UI Semibold", size=16, weight="bold"),
            fg_color="#ff9f1c", hover_color="#d97706", border_color="#92400e", border_width=2,
            text_color="#1a1a1d", text_color_disabled="gray30", height=40,
        )
        self.download_button.grid(row=5, column=0, columnspan=4, padx=10, pady=(10, 10), sticky="nsew")

    def _setup_downloads_frame(self):
        """Setup progress tracking section."""
        self.downloads_frame = customtkinter.CTkFrame(master=self.frame_0, fg_color="transparent")
        self.downloads_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.progress_file = customtkinter.CTkLabel(
            master=self.downloads_frame,
            text="Start download to see progress.",
            font=customtkinter.CTkFont(family="Segoe UI"),
            text_color="#e6e1d6",
        )
        self.progress_file.grid(row=0, padx=12, sticky="nsw")

        self.progressbar = customtkinter.CTkProgressBar(
            self.downloads_frame,
            orientation="horizontal",
            width=660,
            mode="indeterminate",
            indeterminate_speed=1,
            progress_color="#FF9F1C",
            fg_color="#1a1a1d",
            border_color="#3e3c38",
            border_width=1,
        )
        self.progressbar.grid(row=1, column=0, padx=(10, 10), pady=(5, 10), sticky="ns")
        self.progressbar.start()

    def _setup_textbox(self):
        """Setup logs section."""
        self.textbox = customtkinter.CTkTextbox(
            master=self.frame_0,
            border_width=2,
            border_color="#3e3c38",
            fg_color="#1a1a1d",
            text_color="#65a63f",
            width=680,
            font=customtkinter.CTkFont(family="Cascadia Mono"),
        )
        self.textbox.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.textbox.insert("0.0", "Factorio Mod Downloader v0.3.0:\n")
        self.textbox.yview(END)
        self.textbox.configure(state="disabled")

    def _select_path(self):
        """Handle path selection."""
        output_path = filedialog.askdirectory()
        if output_path and output_path != "":
            self.download_path.delete(0, END)
            self.download_path.insert(0, output_path)

    def _callback(self, url):
        """Open URL in browser."""
        webbrowser.open_new(url)

    def _validate_inputs(self) -> bool:
        """
        Validate user inputs.

        Returns:
            True if inputs are valid, False otherwise
        """
        mod_url = self.mod_url.get().strip()
        download_path = self.download_path.get().strip()

        if not mod_url or not re.match(r"^https://mods\.factorio\.com/mod/.*", mod_url):
            CTkMessagebox(
                title="Error",
                width=500,
                wraplength=500,
                message="Please provide a valid mod_url!!!",
                icon="cancel",
            )
            return False

        if not download_path:
            CTkMessagebox(
                title="Error",
                width=500,
                message="Please provide a valid download_path!!!",
                icon="cancel",
            )
            return False

        output = Path(download_path).expanduser().resolve()

        if output.exists() and not output.is_dir():
            CTkMessagebox(
                title="Error",
                width=500,
                wraplength=500,
                message=f"{output} already exists and is not a directory.\nEnter a valid output directory.",
                icon="cancel",
            )
            return False

        if output.exists() and output.is_dir() and tuple(output.glob("*")):
            response = CTkMessagebox(
                title="Continue?",
                width=500,
                wraplength=500,
                message=f"Directory {output} is not empty.\nDo you want to continue and overwrite?",
                icon="warning",
                option_1="Cancel",
                option_2="Yes",
            )

            if not response or response.get() != "Yes":
                return False

        return True

    def _download_button_action(self):
        """Handle download button click."""
        if not self._validate_inputs():
            return

        self.download_button.configure(state="disabled", text="Download Started")
        self.path_button.configure(state="disabled")
        download_path = self.download_path.get().strip()
        mod_url = self.mod_url.get().strip()

        import os

        os.makedirs(download_path, exist_ok=True)

        try:
            selected_optional = {mod for mod, var in self.optional_deps_vars.items() if var.get()}
            from factorio_mod_downloader.downloader.mod_downloader import ModDownloader

            mod_downloader = ModDownloader(mod_url, download_path, self.app, selected_optional_deps=selected_optional)
            mod_downloader.start()

        except Exception as e:
            CTkMessagebox(
                title="Error",
                width=500,
                wraplength=500,
                message=f"Unknown error occurred.\n{str(e).split(chr(10))[0]}",
                icon="cancel",
            )
            self.download_button.configure(state="normal", text="Start Download")
            self.path_button.configure(state="normal")

    def _fetch_deps_action(self):
        mod_url = self.mod_url.get().strip()
        if not mod_url or not re.match(r"^https://mods\.factorio\.com/mod/.*", mod_url):
            CTkMessagebox(
                title="Error", width=500, message="Please provide a valid mod_url to check dependencies!", icon="cancel"
            )
            return

        self.fetch_deps_button.configure(state="disabled", text="Fetching...")
        
        # Clear existing checkboxes
        for widget in self.deps_container.winfo_children():
            widget.destroy()
            
        lbl = customtkinter.CTkLabel(self.deps_container, text="Fetching dependencies...", text_color="#A19D94")
        lbl.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        from factorio_mod_downloader.downloader.mod_downloader import DependencyFetcher
        fetcher = DependencyFetcher(mod_url, self.app)
        fetcher.start()

    def on_deps_fetched(self, required_mods, optional_mods):
        self.fetch_deps_button.configure(state="normal", text="Check Deps")
        
        for widget in self.deps_container.winfo_children():
            widget.destroy()
            
        self.optional_deps_vars.clear()
        
        row_idx = 0
        
        if not required_mods and not optional_mods:
            lbl = customtkinter.CTkLabel(
                self.deps_container, text="No dependencies found.", text_color="#e6e1d6"
            )
            lbl.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            return

        for mod in required_mods:
            var = customtkinter.BooleanVar(value=True)
            cb = customtkinter.CTkCheckBox(
                master=self.deps_container, text=f"[Required] {mod}", variable=var, state="disabled",
                fg_color="#3e3c38", border_color="#ff9f1c", checkmark_color="#1a1a1d"
            )
            cb.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            row_idx += 1
            
        for mod in optional_mods:
            var = customtkinter.BooleanVar(value=False)
            self.optional_deps_vars[mod] = var
            cb = customtkinter.CTkCheckBox(
                master=self.deps_container, text=f"[Optional] {mod}", variable=var,
                fg_color="#3e3c38", border_color="#ff9f1c", checkmark_color="#1a1a1d", hover_color="#4a4743", text_color="#e6e1d6"
            )
            cb.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            row_idx += 1

    def on_deps_failed(self, error):
        self.fetch_deps_button.configure(state="normal", text="Check Deps")
        CTkMessagebox(
            title="Error", width=500, message=f"Failed to fetch dependencies:\n{error}", icon="cancel"
        )
