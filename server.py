import os
import shutil
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import yt_dlp
import imageio_ffmpeg

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ['PATH'] += os.pathsep + os.path.dirname(ffmpeg_path)

app = Flask(__name__)
CORS(app, origins=['https://www.youtube.com'])

TEMP_DIR = './temp_download'
FINAL_DIR = './downloads'

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

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

def move_to_final_folder(filename):
    src = os.path.join(TEMP_DIR, filename)
    dst = os.path.join(FINAL_DIR, filename)
    shutil.move(src, dst)
    return dst

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
        info = download_video(url, format_opts, TEMP_DIR)
        filename = f"{info['title']}.mp4"
        final_path = move_to_final_folder(filename)

        response = make_response(send_file(final_path, as_attachment=True))
        response.headers["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        print(response.headers["Content-Disposition"])
        return response
    except Exception as e:
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
        info = download_video(url, format_opts, TEMP_DIR)
        filename = f"{info['title']}.mp3"
        final_path = move_to_final_folder(filename)

        response = make_response(send_file(final_path, as_attachment=True))
        response.headers["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        print(response.headers["Content-Disposition"])
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200

if __name__ == '__main__':
    app.run(port=5000)
