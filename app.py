import os
import yt_dlp
from flask import Flask, request, send_from_directory, render_template, jsonify

app = Flask(__name__)

# Ensure downloads directory exists
DOWNLOADS_DIR = 'downloads'
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

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
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = os.path.basename(ydl.prepare_filename(info))

            return render_template('index.html', success=True, filename=filename)

        except yt_dlp.utils.DownloadError as e:
            return render_template('index.html', error=f"Download error: {e}")
        except Exception as e:
            return render_template('index.html', error=f"An unexpected error occurred: {e}")

    # Render form on GET request
    return render_template('index.html')


@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
