from tkinter import *
from tkinter import messagebox, filedialog
from pytube import YouTube
from threading import Thread
from tkinter import ttk

class VideoDownloaderApp(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.videos = None
        self.download_path = StringVar()
        self.init_ui()

    def init_ui(self):
        self.pack(fill=BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        self.create_header()
        self.create_url_entry()
        self.create_buttons()
        self.create_video_list()

    def create_header(self):
        frame_header = Frame(self)
        frame_header.pack()
        Label(frame_header, text="YouTube", font="ComicSans 20", fg="red").pack()

    def create_url_entry(self):
        frame_url = Frame(self)
        frame_url.pack(fill=X, padx=10, pady=10)
        Label(frame_url, text="Url: ", font="ComicSans 12").grid(row=0, column=0, padx=(0, 10))
        self.link = Entry(frame_url, width=50)
        self.link.grid(row=0, column=1)

    def create_buttons(self):
        frame_buttons = Frame(self)
        frame_buttons.pack()
        Button(frame_buttons, text="Fetch", font="ComicSans 12", command=self.fetch).pack(side=LEFT, padx=10)
        Button(frame_buttons, text="Choose Path", font="ComicSans 12", command=self.choose_path).pack(side=LEFT)
        self.select_button = Button(frame_buttons, text="Select", font="ComicSans 12", command=self.download_selected)
        self.select_button.pack(side=LEFT)

    def create_video_list(self):
        frame_list = Frame(self)
        frame_list.pack()
        self.display = Listbox(frame_list, selectbackground="green", activestyle="none", height=10, width=30)
        self.display.pack()

    def fetch(self):
        url = self.link.get()
        yt = YouTube(url)
        self.videos = yt.streams

        self.display.grid(row=0, column=0, pady=(30, 0))
        self.select_button.grid(row=1, column=0, pady=10)
        self.parent.geometry("400x400+450+50")

        self.display.delete(0, END)
        for index, video in enumerate(self.videos):
            self.display.insert("end", f"{index + 1}: {video.mime_type}, {video.resolution}")

    def choose_path(self):
        chosen_path = filedialog.askdirectory()
        if chosen_path:
            self.download_path.set(chosen_path)

    def download_selected(self):
        selected_index = int(self.display.get(ACTIVE).split(":")[0]) - 1
        selected_video = self.videos[selected_index]

        if not self.download_path.get() or not os.path.exists(self.download_path.get()):
            messagebox.showerror("Error", "Please choose a valid download path.")
            return

        # Create a progress bar frame
        frame_progress = Frame(self)
        frame_progress.pack()
        progress_bar = ttk.Progressbar(frame_progress, orient=HORIZONTAL, length=100, mode='determinate')
        progress_bar.grid(row=0, column=0, pady=10)

        # Start the download in a separate thread
        download_thread = Thread(target=self.download, args=(selected_video, progress_bar))
        download_thread.start()

    def download(self, video, progress_bar):
        download_path = self.download_path.get()
        messagebox.showinfo("Downloading", "The video is downloading.")

        def update_progress(stream, chunk, remaining):
            file_size = video.filesize
            downloaded_size = file_size - remaining
            percent = (downloaded_size / file_size) * 100
            progress_bar['value'] = percent
            self.parent.update_idletasks()

        video.register_on_progress_callback(update_progress)

        try:
            video.download(download_path)
            messagebox.showinfo("Download Complete", "The video has been successfully downloaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Error during download: {str(e)}")

        # Destroy the progress bar frame after download completion
        progress_bar.master.destroy()

if __name__ == '__main__':
    root = Tk()
    app = VideoDownloaderApp(root)
    root.title("Video Downloader")
    root.geometry("400x200+450+50")
    root.mainloop()
