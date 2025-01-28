import os
import requests
import tkinter as tk
from tkinter import messagebox, filedialog
from ffmpy import FFmpeg

def download_ts_files(m3u8_url, output_folder):
    response = requests.get(m3u8_url)
    response.raise_for_status()

    lines = response.text.splitlines()
    ts_urls = [line for line in lines if line.endswith('.ts')]

    if not ts_urls:
        raise ValueError("No .ts files found in the m3u8 playlist.")

    ts_files = []
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

    return ts_files

def merge_audio(ts_files, output_mp3):
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

def start_download():
    m3u8_url = url_entry.get()
    output_folder = filedialog.askdirectory(title="Select Output Folder")

    if not m3u8_url or not output_folder:
        messagebox.showerror("Error", "Please provide a valid URL and output folder.")
        return

    try:
        ts_files = download_ts_files(m3u8_url, output_folder)
        output_mp3 = os.path.join(output_folder, "output.mp3")
        merge_audio(ts_files, output_mp3)

        # Cleanup downloaded .ts files
        for ts_file in ts_files:
            os.remove(ts_file)

        messagebox.showinfo("Success", f"Audio saved as {output_mp3}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def create_gui():
    root = tk.Tk()
    root.title("M3U8 Audio Downloader")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="M3U8 URL:").grid(row=0, column=0, sticky="w")
    global url_entry
    url_entry = tk.Entry(frame, width=50)
    url_entry.grid(row=0, column=1, padx=5, pady=5)

    download_button = tk.Button(frame, text="Download and Merge", command=start_download)
    download_button.grid(row=1, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
