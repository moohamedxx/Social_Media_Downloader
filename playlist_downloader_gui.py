import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import yt_dlp
import shutil


class PlaylistDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")

        # Colors
        self.bg_color = "#f0f0f0"
        self.primary_color = "#FF0000"  # YouTube red
        self.secondary_color = "#282828"

        self.root.configure(bg=self.bg_color)

        # Variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to download 🚀")
        self.download_type = tk.StringVar(value="v")
        self.quality = tk.StringVar(value="720")

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Navbar
        navbar = ttk.Frame(main_container, style="Navbar.TFrame")
        navbar.pack(fill="x", pady=(0, 20))

        # YouTube icon and title
        icon_canvas = tk.Canvas(
            navbar, width=50, height=50, bg=self.secondary_color, highlightthickness=0
        )
        icon_canvas.pack(side="left", padx=(10, 5))
        icon_canvas.create_oval(5, 5, 45, 45, fill=self.primary_color, outline="")
        icon_canvas.create_polygon(20, 15, 20, 35, 35, 25, fill="white")

        title_label = tk.Label(
            navbar,
            text="YouTube Playlist Downloader",
            font=("Arial", 18, "bold"),
            fg="white",
            bg=self.secondary_color,
        )
        title_label.pack(side="left", padx=10)

        # Input frame
        input_frame = ttk.LabelFrame(
            main_container, text="🔗 Playlist Details", padding=15
        )
        input_frame.pack(fill="x", pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)

        # URL Entry
        ttk.Label(input_frame, text="Playlist URL:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.url_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Folder Entry
        ttk.Label(input_frame, text="Folder name:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.folder_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.folder_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Range Entry
        ttk.Label(input_frame, text="Video range (1-3,5):").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.range_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.range_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Options frame
        options_frame = ttk.Frame(main_container)
        options_frame.pack(fill="x", pady=(0, 15))
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)

        # Download type
        type_frame = ttk.LabelFrame(options_frame, text="Download Type", padding=10)
        type_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        type_frame.columnconfigure(0, weight=1)

        ttk.Radiobutton(
            type_frame,
            text="🎬 Video",
            variable=self.download_type,
            value="v",
            command=self.toggle_quality,
        ).pack(side="left", padx=10)
        ttk.Radiobutton(
            type_frame,
            text="🎵 Audio",
            variable=self.download_type,
            value="a",
            command=self.toggle_quality,
        ).pack(side="left", padx=10)

        # Quality selection
        self.quality_frame = ttk.LabelFrame(
            options_frame, text="Video Quality", padding=10
        )
        self.quality_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.quality_frame.columnconfigure(0, weight=1)

        qualities = ["1080", "720", "480", "360"]
        for q in qualities:
            ttk.Radiobutton(
                self.quality_frame, text=f"{q}p", variable=self.quality, value=q
            ).pack(side="left", padx=10)

        # Download button
        self.download_btn = tk.Button(
            main_container,
            text="⬇️ Download Now!",
            command=self.start_download,
            font=("Arial", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
        )
        self.download_btn.pack(pady=10)

        # Progress Section
        progress_frame = ttk.LabelFrame(
            main_container, text="📊 Download Progress", padding=15
        )
        progress_frame.pack(fill="x", pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)

        # Status label
        self.status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg=self.bg_color,
            fg="#333333",
        )
        self.status_label.pack(anchor="w", pady=(0, 5))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))

        # Download info
        self.info_frame = ttk.Frame(progress_frame)
        self.info_frame.pack(fill="x")

        self.speed_label = tk.Label(
            self.info_frame,
            text="Speed: -- KB/s",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="#666666",
        )
        self.speed_label.pack(side="left")

        self.filename_label = tk.Label(
            self.info_frame,
            text="File: --",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="#666666",
        )
        self.filename_label.pack(side="right")

        # Log Section
        log_frame = ttk.LabelFrame(main_container, text="📝 Download Log", padding=15)
        log_frame.pack(fill="both", expand=True, pady=(0, 15))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD,
            relief="solid",
            borderwidth=1,
        )
        self.log_text.pack(fill="both", expand=True)

        # Clear log button
        clear_btn = tk.Button(
            log_frame,
            text="🗑️ Clear Log",
            command=self.clear_log,
            font=("Arial", 9),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            padx=10,
            pady=5,
        )
        clear_btn.pack(pady=(10, 0))

        # Configure grid weights for resizing
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)

    def toggle_quality(self):
        """Toggle quality options visibility"""
        if self.download_type.get() == "a":
            self.quality_frame.grid_remove()
        else:
            self.quality_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def parse_ranges(self, range_str):
        """Parse input like '1-3,5,7-9' and return a list of indices (0-based)."""
        result = set()
        for part in range_str.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                result.update(range(start, end + 1))
            else:
                result.add(int(part))
        return sorted([i - 1 for i in result])  # 0-based indexing

    def hook(self, d):
        """Progress hook for yt-dlp"""
        if d["status"] == "downloading":
            # Update progress
            percent = d.get("_percent_str", "0%").strip("%")
            try:
                self.progress_var.set(float(percent))
            except ValueError:
                pass

            # Update status
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")
            filename = d.get("filename", "N/A").split("/")[-1]

            self.status_var.set(f"Downloading {filename}... {percent}%")
            self.speed_label.config(text=f"Speed: {speed}")
            self.filename_label.config(text=f"File: {filename}")

            self.log_message(
                f"Downloading: {filename} | {percent}% | Speed: {speed} | ETA: {eta}"
            )

        elif d["status"] == "finished":
            filename = d.get("filename", "N/A").split("/")[-1]
            self.status_var.set(f"Finished: {filename}")
            self.progress_var.set(100)
            self.log_message(f"✅ Download complete: {filename}")

    def start_download(self):
        """Start the download process"""
        # Disable button during download
        self.download_btn.config(state="disabled", text="⏳ Downloading...")

        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting download...")
        self.clear_log()

        # Start download in thread
        thread = threading.Thread(target=self.download_playlist)
        thread.daemon = True
        thread.start()

    def download_playlist(self):
        """Download the playlist videos"""
        try:
            playlist_url = self.url_entry.get().strip()
            folder_name = self.folder_entry.get().strip()
            range_str = self.range_entry.get().strip()
            download_type = self.download_type.get()
            quality = self.quality.get() if download_type == "v" else None

            if not all([playlist_url, folder_name, range_str]):
                messagebox.showerror("Error", "Please fill in all fields")
                return

            # Create folder first
            try:
                os.makedirs(folder_name, exist_ok=True)
                self.log_message(f"Created folder: {folder_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {str(e)}")
                return

            selected_indices = self.parse_ranges(range_str)

            ffmpeg_path = shutil.which("ffmpeg")

            # First, get playlist info
            with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
                try:
                    info = ydl.extract_info(playlist_url, download=False)
                    if not info:
                        raise ValueError("Could not extract playlist information")

                    # Handle both playlist and single video cases
                    if "entries" in info:
                        entries = info["entries"]
                    else:
                        entries = [info]

                    if not entries:
                        raise ValueError("No videos found in the playlist")

                    self.log_message(
                        f"Playlist: {info.get('title', 'Untitled Playlist')}"
                    )
                    self.log_message(f"Total videos: {len(entries)}")

                    # Create a list of URLs to download
                    urls_to_download = []
                    for i in selected_indices:
                        if i < 0 or i >= len(entries):
                            self.log_message(f"⚠️ Skipping invalid video index: {i+1}")
                            continue

                        entry = entries[i]
                        if not entry:
                            self.log_message(f"⚠️ Skipping unavailable video: {i+1}")
                            continue

                        video_url = entry.get("url") or entry.get("webpage_url")
                        if not video_url:
                            self.log_message(f"⚠️ Could not get URL for video: {i+1}")
                            continue

                        urls_to_download.append(video_url)

                    if not urls_to_download:
                        raise ValueError("No valid videos to download")

                    # Now download each video individually
                    for url in urls_to_download:
                        try:
                            # Configure download options for this video
                            video_opts = {
                                "outtmpl": os.path.join(
                                    folder_name, "%(title)s.%(ext)s"
                                ),
                                "quiet": True,
                                "progress_hooks": [self.hook],
                            }

                            if ffmpeg_path:
                                video_opts["ffmpeg_location"] = ffmpeg_path

                            if download_type == "a":
                                video_opts["format"] = "bestaudio/best"
                                if ffmpeg_path:
                                    video_opts["postprocessors"] = [
                                        {
                                            "key": "FFmpegExtractAudio",
                                            "preferredcodec": "mp3",
                                            "preferredquality": "192",
                                        }
                                    ]
                            else:
                                if ffmpeg_path:
                                    video_opts["format"] = (
                                        f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
                                    )
                                else:
                                    video_opts["format"] = (
                                        f"best[height<={quality}][ext=mp4]/best"
                                    )

                            # Get video info first
                            with yt_dlp.YoutubeDL({"quiet": True}) as info_ydl:
                                video_info = info_ydl.extract_info(url, download=False)
                                if video_info:
                                    video_title = video_info.get(
                                        "title", "Unknown Title"
                                    )
                                    self.status_var.set(f"⬇️ Downloading: {video_title}")
                                    self.log_message(
                                        f"Starting download: {video_title}"
                                    )

                                    # Download the video
                                    with yt_dlp.YoutubeDL(video_opts) as download_ydl:
                                        download_ydl.download([url])
                                        self.log_message(
                                            f"✅ Downloaded: {video_title}"
                                        )

                        except Exception as e:
                            self.log_message(f"⚠️ Failed to download video: {str(e)}")
                            continue

                    self.status_var.set("✅ All downloads completed!")
                    self.log_message("🎉 All downloads completed successfully!")
                    messagebox.showinfo(
                        "Success",
                        f"All downloads completed!\nFiles saved in: {os.path.abspath(folder_name)}",
                    )

                except Exception as e:
                    raise Exception(f"Error processing playlist: {str(e)}")

        except Exception as e:
            self.status_var.set("Download failed! ❌")
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.download_btn.config(state="normal", text="⬇️ Download Now!")
