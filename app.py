from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for, after_this_request
import yt_dlp, os, traceback, sys

app = Flask(__name__)
app.secret_key = "premium2026mini"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

if sys.platform == 'win32':
    FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg.exe")
else:
    FFMPEG_PATH = "ffmpeg"
COOKIES_PATH = os.path.join(BASE_DIR, "cookies.txt")

@app.route("/", methods=["GET", "POST"])
def index():
    info = None
    url = request.form.get("url", "").strip() if request.method == "POST" else request.args.get("url", "")
    if request.method == "POST":
        use_cookies = request.form.get("use_cookies") == "1"
        cookies_text = request.form.get("cookies_text", "").strip()
        cookies_file = request.files.get("cookies_file")
        try:
            if use_cookies or cookies_text or (cookies_file and cookies_file.filename):
                if cookies_file and cookies_file.filename:
                    data = cookies_file.read()
                    try:
                        text = data.decode("utf-8", errors="ignore")
                    except:
                        text = data.decode("latin-1", errors="ignore")
                else:
                    text = cookies_text
                if text:
                    with open(COOKIES_PATH, "w", encoding="utf-8", errors="ignore") as f:
                        f.write(text)
                    flash("Cookies сохранены")
        except Exception as e:
            traceback.print_exc()
            flash(f"Ошибка сохранения cookies: {str(e)}")
    if request.method == "POST" and url:
        try:
            ydl_opts = {
                'quiet': True,
                'noplaylist': True,
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
                }
            }
            if os.path.exists(COOKIES_PATH):
                ydl_opts['cookiefile'] = COOKIES_PATH
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            traceback.print_exc()
            flash(f"Ошибка при поиске: {str(e)}")
    return render_template("index.html", info=info, url=url)

@app.route("/download", methods=["POST"])
def download():
    print("Download request received")
    url = request.form["url"]
    print(f"URL: {url}")
    audio_only = request.form.get("audio_only") == "1"
    height = request.form.get("height")
    print(f"Audio only: {audio_only}, Height: {height}")

    try:
        if audio_only:
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s [MUSIC].%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320'}],
                'ffmpeg_location': FFMPEG_PATH,
                'noplaylist': True,
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
                }
            }
        else:
            h = int(height)
            opts = {
                'format': f'best[height={h}][ext=mp4]/bestvideo[height={h}]+bestaudio/best',
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s [{h}p].%(ext)s',
                'merge_output_format': 'mp4',
                'ffmpeg_location': FFMPEG_PATH,
                'noplaylist': True,
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
                }
            }
        if os.path.exists(COOKIES_PATH):
            opts['cookiefile'] = COOKIES_PATH

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn = ydl.prepare_filename(info)
            if audio_only and not fn.endswith('.mp3'):
                fn = fn.rsplit('.', 1)[0] + '.mp3'
            
            print(f"File prepared: {fn}")
            if not os.path.exists(fn):
                print(f"File not found: {fn}")
                # Try to find file with different extension if mp3 conversion failed or didn't rename
                base_fn = fn.rsplit('.', 1)[0]
                for ext in ['.webm', '.m4a', '.mp4']:
                    if os.path.exists(base_fn + ext):
                        fn = base_fn + ext
                        print(f"Found alternative file: {fn}")
                        break
            
            sys.stdout.flush()

        flash(f"Файл успешно сохранен в папку Загрузки: {os.path.basename(fn)}")
        return redirect(url_for('index', url=url))
    except Exception as e:
        traceback.print_exc()
        flash(f"Ошибка скачивания: {str(e)}")
        return redirect(url_for('index', url=url))

if __name__ == "__main__":
    from waitress import serve
    print("PREMIUM YT DOWNLOADER 2026 — КОМПАКТНАЯ ВЕРСИЯ ЗАПУЩЕНА!")
    print("Видео 480-720p • Компактно • Всё работает")
    print("http://127.0.0.1:5000")
    serve(app, host="127.0.0.1", port=5000)

