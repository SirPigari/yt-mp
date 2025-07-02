# YT-MB

A downloader for YouTube videos.
**No license — public code.**

## Requirements

- Python 3.10 or newer  
- Git  
- Chrome browser

## Installation

1. Clone the repository:

    ```bash
    git clone <repo_url>
    ```

2. Install the required Python packages:

    ```bash
    pip install flask flask_cors yt_dlp imageio_ffmpeg
    ```

3. Run the server:

    ```python
    python ./server.py
    ```

4. Set up the Chrome extension:

   - Open Chrome and go to `chrome://extensions`  
   - Enable **Developer mode**  
   - Click **Load unpacked**  
   - Select the cloned directory

5. Done!
