# ==========================================
# WEBSOCKET SERVER DARI KODE KAMU
# SCRAPING TETAP SAMA (ScrapeThisSite)
# ==========================================

from flask import Flask, render_template
from flask_socketio import SocketIO
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "rahasia_socket"
socketio = SocketIO(app)

# ==========================================
# HALAMAN UTAMA
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")

# ==========================================
# EVENT WEBSOCKET
# ==========================================
@socketio.on("mulai_scraping")
def mulai_scraping():

    url = "https://www.scrapethissite.com/pages/"

    socketio.emit("status", {
        "pesan": "🔄 Menghubungi website target..."
    })

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, "html.parser")
            pages = soup.find_all("div", class_="page")

            data = []

            socketio.emit("status", {
                "pesan": f"✅ Website berhasil diakses. Ditemukan {len(pages)} data."
            })

            for i, p in enumerate(pages):

                title = p.find("h3", class_="page-title").text.strip()
                lead = p.find("p", class_="lead session-desc").text.strip()

                item = {
                    "title": title,
                    "lead": lead
                }

                data.append(item)

                # kirim realtime ke browser
                socketio.emit("hasil_scraping", {
                    "no": i + 1,
                    "title": title,
                    "lead": lead
                })

                time.sleep(0.5)

            # ==========================
            # SIMPAN JSON
            # ==========================
            with open("countries.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            # ==========================
            # SIMPAN CSV
            # ==========================
            with open("countries.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "lead"])
                writer.writeheader()
                writer.writerows(data)

            socketio.emit("status", {
                "pesan": "✅ Scraping selesai. File JSON & CSV berhasil disimpan."
            })

        else:
            socketio.emit("status", {
                "pesan": "❌ Gagal mengakses halaman."
            })

    except Exception as e:
        socketio.emit("status", {
            "pesan": f"❌ Error: {str(e)}"
        })

# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    print("🚀 WebSocket Server berjalan di http://localhost:5000")
    socketio.run(app, debug=True, port=5000)