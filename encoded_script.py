import threading
import streamlit as st
import requests
import time

running = False
# Judul Aplikasi dengan CSS yang lebih menarik
st.markdown("""
    <style>
        h1 {
            text-align: center;
            color: #333;
            font-size: 40px;
        }
        .stButton > button {
            width: 100%;
            padding: 12px;
            font-size: 20px;
            background-color: #4CAF50;
            border: none;
            border-radius: 10px;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .slider-label {
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Sepampam / Didin Wahyudin</h1>", unsafe_allow_html=True)

# Mengatur layout dengan dua kolom
col1, col2 = st.columns(2)

with col1:
    session = st.text_input("Masukkan Session:")
    shopid = st.text_input("Masukkan Shop ID:")
with col2:
    url_raw_github = st.text_input("Masukkan URL Raw GitHub untuk Cookies:")

# Garis pembatas untuk estetika
st.markdown("<hr style='border:1px solid #eee;'>", unsafe_allow_html=True)

# Slider untuk Like dan Delay dengan Label yang Diperjelas
st.markdown('<p class="slider-label">Masukkan Jumlah Like:</p>', unsafe_allow_html=True)
like_cnt = st.slider("", min_value=1, max_value=50, value=1)

st.markdown('<p class="slider-label">Delay antar Aksi (detik):</p>', unsafe_allow_html=True)
delay_between_actions = st.slider("", min_value=0.1, max_value=5.0, value=1.0)

# Fungsi untuk memuat cookies dari URL GitHub
def load_cookies_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        cookies_list = response.text.splitlines()
        return [cookie.strip() for cookie in cookies_list]
    except Exception as e:
        st.error(f"Gagal mengunduh file cookies: {e}")
        return []

# Fungsi untuk mengirim like dengan header spesifik
def send_like(session_id, cookies, like_count):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/like"
    headers = {
        "cookie": "; ".join(cookies),
        "content-type": "application/json",
        "user-agent": "ShopeeApp/3.0 (Android; Mobile; AppVer=3.0)",
        "accept": "*/*"
    }
    data = {"like_cnt": like_count}
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Fungsi untuk mengirim follow dengan header spesifik
def send_follow(session_id, shop_id, cookies):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/follow/{shop_id}"
    headers = {
        "cookie": "; ".join(cookies),
        "user-agent": "ShopeeApp/3.0 (iOS; Mobile; AppVer=3.0)",
        "accept": "*/*",
        "content-type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json={})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Fungsi untuk mengirim buy dengan header spesifik
def send_buy(session_id, cookies):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/msg/buy"
    headers = {
        "cookie": "; ".join(cookies),
        "user-agent": "ShopeeApp/3.0 (Windows; Desktop; AppVer=3.0)",
        "content-type": "application/json",
        "accept": "*/*"
    }
    try:
        response = requests.post(url, headers=headers, json={})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Fungsi untuk menjalankan looping selamanya di background
def start_loop():
    global running
    running = True
    cookies_list = load_cookies_from_github(url_raw_github)

    if cookies_list:
        while running:
            for index, cookie in enumerate(cookies_list):
                cookie_list = [cookie]

                send_like(session, cookie_list, like_cnt)
                send_follow(session, shopid, cookie_list)
                send_buy(session, cookie_list)
                time.sleep(delay_between_actions)
    else:
        st.error("Gagal memuat cookies, pastikan URL Raw GitHub benar.")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start"):
        if not running:
            threading.Thread(target=start_loop, daemon=True).start()
            st.success("Looping di background dimulai! Aplikasi akan tetap berjalan.")
