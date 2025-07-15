import tkinter as tk
from .social_media_downloader import SocialMediaDownloader


def main():
    root = tk.Tk()
    app = SocialMediaDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
