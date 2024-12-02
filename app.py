import os
import yt_dlp
from flask import Flask, request, send_from_directory, render_template, jsonify
import subprocess

app = Flask(__name__)


DOWNLOADS_DIR = 'downloads'
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


COOKIES_FILE_PATH = 'www.youtube.com_cookies.txt' 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            url = request.form.get('url')

            if not url:
                return render_template('index.html', error="Please provide a valid YouTube URL.")

            
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
                'cookies': COOKIES_FILE_PATH,  
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = os.path.basename(ydl.prepare_filename(info))

            return render_template('index.html', success=True, filename=filename)

        except yt_dlp.utils.DownloadError as e:
            return render_template('index.html', error=f"Download error: {e}")
        except Exception as e:
            return render_template('index.html', error=f"An unexpected error occurred: {e}")

    return render_template('index.html')


@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)


@app.route('/stream', methods=['POST'])
def stream_video():
    try:
        url = request.form.get('url')
        if not url:
            return render_template('index.html', error="Please provide a valid YouTube URL.")

        command = [
            'yt-dlp', '-o', '-', url
        ]
        vlc_command = ['vlc', '-']

        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen(vlc_command, stdin=process.stdout)

        return render_template('index.html', success=True, message="Streaming to VLC...")

    except Exception as e:
        return render_template('index.html', error=f"An error occurred: {e}")


if __name__ == '__main__':
    app.run(debug=True)
