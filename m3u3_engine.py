import os
import time
import requests
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from ffmpy import FFmpeg
import threading

def download_ts_files(m3u8_url, output_folder, progress_var, progress_bar):
    response = requests.get(m3u8_url)
    response.raise_for_status()

    lines = response.text.splitlines()
    ts_urls = [line for line in lines if line.endswith('.ts')]

    if not ts_urls:
        raise ValueError("No .ts files found in the m3u8 playlist.")

    ts_files = []
    total_files = len(ts_urls)
    for i, ts_url in enumerate(ts_urls):
        ts_filename = os.path.join(output_folder, f"segment_{i}.ts")
        ts_files.append(ts_filename)

        # Full URL for .ts file if relative
        if not ts_url.startswith("http"):
            ts_url = os.path.join(os.path.dirname(m3u8_url), ts_url)

        with requests.get(ts_url, stream=True) as ts_response:
            ts_response.raise_for_status()
            with open(ts_filename, 'wb') as ts_file:
                for chunk in ts_response.iter_content(chunk_size=8192):
                    ts_file.write(chunk)

        # Update progress bar
        progress_var.set((i + 1) / total_files * 100)
        progress_bar.update()

    return ts_files

def merge_audio(ts_files, output_mp3, progress_var, progress_bar, waiting_label):
    def rolling_waiting():
        while not merge_done:
            for char in "|/-\\":
                waiting_label.config(text=f"Concatenating... {char}")
                waiting_label.update()
                time.sleep(0.1)

    # Start the rolling waiting indicator in a separate thread
    merge_done = False
    threading.Thread(target=rolling_waiting).start()

    # Generate the file list for ffmpeg
    with open("file_list.txt", "w") as f:
        for ts_file in ts_files:
            f.write(f"file '{ts_file}'\n")
    
    ffmpeg = FFmpeg(
        inputs={"file_list.txt": "-f concat -safe 0"},
        outputs={output_mp3: "-y -f mp3 -acodec libmp3lame -ar 44100 -b:a 192k"}
    )
    ffmpeg.run()
    os.remove("file_list.txt")

    # Update progress bar to 100% after merging
    progress_var.set(100)
    progress_bar.update()

    # Stop the rolling waiting indicator
    merge_done = True
    waiting_label.config(text="Concatenation complete")

def start_download():
    m3u8_url = url_entry.get()
    output_folder = filedialog.askdirectory(title="Select Output Folder")

    if not m3u8_url or not output_folder:
        messagebox.showerror("Error", "Please provide a valid URL and output folder.")
        return

    # Create progress window
    progress_window = tk.Toplevel(root)
    progress_window.title("Progress")
    tk.Label(progress_window, text="Downloading...").pack(pady=10)
    progress_var.set(0)
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10, padx=10, fill="x")

    waiting_label = tk.Label(progress_window, text="")
    waiting_label.pack(pady=10)

    def download_and_merge():
        try:
            ts_files = download_ts_files(m3u8_url, output_folder, progress_var, progress_bar)
            output_mp3 = os.path.join(output_folder, "output.mp3")
            merge_audio(ts_files, output_mp3, progress_var, progress_bar, waiting_label)

            # Cleanup downloaded .ts files
            for ts_file in ts_files:
                os.remove(ts_file)

            messagebox.showinfo("Success", f"Audio saved as {output_mp3}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_window.destroy()

    threading.Thread(target=download_and_merge).start()

def create_gui():
    global root, url_entry, progress_var
    root = tk.Tk()
    root.title("M3U8 Audio Downloader")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="M3U8 URL:").grid(row=0, column=0, sticky="w")
    url_entry = tk.Entry(frame, width=50)
    url_entry.grid(row=0, column=1, padx=5, pady=5)

    download_button = tk.Button(frame, text="Download and Merge", command=start_download)
    download_button.grid(row=1, column=0, columnspan=2, pady=10)

    progress_var = tk.DoubleVar()

    root.mainloop()

if __name__ == "__main__":
    create_gui()