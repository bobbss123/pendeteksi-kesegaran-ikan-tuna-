import streamlit as st
import requests
from PIL import Image
import io
import csv
import os
from datetime import datetime

ROBOFLOW_API_KEY = "WwHvvZp1bpdvIZWZN63u"
ROBOFLOW_PROJECT = "ikan-segar-detector-l3abz"
ROBOFLOW_VERSION = 1
ROBOFLOW_API_URL = f"https://infer.roboflow.com/{ROBOFLOW_PROJECT}/{ROBOFLOW_VERSION}?api_key={ROBOFLOW_API_KEY}"

RIWAYAT_FILE = "riwayat.csv"

def login_admin():
    st.title("Login Admin")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["admin_logged_in"] = True
            st.success("Login berhasil!")
        else:
            st.error("Username atau password salah.")

def show_riwayat():
    st.title("Riwayat Deteksi")
    if os.path.exists(RIWAYAT_FILE):
        with open(RIWAYAT_FILE, "r") as file:
            reader = csv.reader(file)
            data = list(reader)
            if data:
                st.table(data)
            else:
                st.info("Belum ada riwayat deteksi.")
    else:
        st.info("Belum ada riwayat deteksi.")

def landing_page():
    st.image("assets/landing.png", use_container_width=True)
    st.title("Sistem Deteksi Kesegaran Ikan Tuna")
    uploaded_file = st.file_uploader("Unggah gambar ikan tuna", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Gambar yang diunggah", use_column_width=True)
        if st.button("🔍 Deteksi Sekarang"):
            detect_image(image, uploaded_file.name)

def detect_image(image, filename):
    buf = io.BytesIO()
    image.save(buf, format='JPEG')
    byte_im = buf.getvalue()
    response = requests.post(ROBOFLOW_API_URL, files={"file": byte_im}, data={"confidence": "50", "overlap": "50"})
    if response.status_code == 200:
        result = response.json()
        if "predictions" in result and result["predictions"]:
            for pred in result["predictions"]:
                label = pred['class']
                confidence = round(pred['confidence'] * 100, 2)
                st.success(f"Deteksi: **{label}** dengan keyakinan {confidence}%")
                simpan_riwayat(filename, label, confidence)
        else:
            st.warning("Tidak ada objek yang terdeteksi.")
    else:
        st.error("Gagal menghubungi Roboflow API.")

def simpan_riwayat(filename, label, confidence):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [waktu, filename, label, f"{confidence}%"]
    with open(RIWAYAT_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)

menu = st.sidebar.radio("Navigasi", ["🏠 Beranda", "🧑‍💻 Login Admin", "📊 Riwayat Deteksi", "ℹ️ Tentang"])

if menu == "🏠 Beranda":
    landing_page()
elif menu == "🧑‍💻 Login Admin":
    login_admin()
elif menu == "📊 Riwayat Deteksi":
    if st.session_state.get("admin_logged_in"):
        show_riwayat()
    else:
        st.warning("Silakan login sebagai admin untuk melihat riwayat.")
elif menu == "ℹ️ Tentang":
    st.title("Tentang Aplikasi")
    st.markdown("""
Aplikasi ini mendeteksi kesegaran ikan tuna berdasarkan gambar menggunakan teknologi YOLOv8 dan Roboflow API.

👤 Admin Login: `admin` | Password: `admin123`
""")