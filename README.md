# M3U8 Audio Downloader

## Setup Instructions

1. **Clone the repository or download the script:**

    ```sh
    git clone https://github.com/Brocowlee/UN_downloader
    cd UN_downloader
    ```

2. **Create a virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Run the script:**

    ```sh
    python m3u3_engine.py
    ```

## Dependencies

- [requests](http://_vscodecontentref_/0): For downloading .ts files.
- [tk](http://_vscodecontentref_/1): For creating the GUI.
- [ffmpy](http://_vscodecontentref_/2): For merging audio files using FFmpeg.

Make sure you have FFmpeg installed on your system. You can download it from [FFmpeg.org](https://ffmpeg.org/download.html).
