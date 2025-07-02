import os
import shutil
from flask import Flask, request, jsonify, send_file, make_response, after_this_request
from flask_cors import CORS
import yt_dlp
import imageio_ffmpeg
import threading

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ['PATH'] += os.pathsep + os.path.dirname(ffmpeg_path)

app = Flask(__name__)
CORS(app, origins=['https://www.youtube.com'])

TEMP_DIR = './temp_download'
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Active process counter + lock ---
active_processes = 0
process_lock = threading.Lock()

def cleanup_temp_dir():
    try:
        shutil.rmtree(TEMP_DIR)
    except FileNotFoundError:
        pass
    os.makedirs(TEMP_DIR, exist_ok=True)

def before_download_cleanup():
    global active_processes
    with process_lock:
        if active_processes == 0:
            cleanup_temp_dir()
        active_processes += 1

def after_download_cleanup():
    global active_processes
    with process_lock:
        active_processes -= 1

def download_video(url, format_opts, temp_folder):
    ydl_opts = {
        **format_opts,
        'outtmpl': os.path.join(temp_folder, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_path,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return info

def get_temp_path(filename):
    return os.path.join(TEMP_DIR, filename)

def send_and_cleanup(filepath, filename):
    @after_this_request
    def remove_file(response):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f'Cleanup failed: {e}')
        after_download_cleanup()
        return response

    response = make_response(send_file(filepath, as_attachment=True))
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return response

@app.route('/download/mp4', methods=['POST'])
def download_mp4_route():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    format_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    try:
        before_download_cleanup()
        info = download_video(url, format_opts, TEMP_DIR)
        filename = f"{info['title']}.mp4"
        return send_and_cleanup(get_temp_path(filename), filename)
    except Exception as e:
        after_download_cleanup()
        return jsonify({'error': str(e)}), 500

@app.route('/download/mp3', methods=['POST'])
def download_mp3_route():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    format_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        before_download_cleanup()
        info = download_video(url, format_opts, TEMP_DIR)
        filename = f"{info['title']}.mp3"
        return send_and_cleanup(get_temp_path(filename), filename)
    except Exception as e:
        after_download_cleanup()
        return jsonify({'error': str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200

if __name__ == '__main__':
    app.run(port=6969, debug=True, threaded=True)
