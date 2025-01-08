import threading
import streamlit as st
import requests
import time

# Variabel global
running_sessions = {}
session_logs = {}

# CSS untuk tampilan Streamlit
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
            font-size: 16px;
            background-color: #4CAF50;
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .stop-button {
            background-color: #FF5733;
        }
        .stop-button:hover {
            background-color: #E74C3C;
        }
        .slider-label {
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }
        .log-box {
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            background-color: #f9f9f9;
            font-family: monospace;
            white-space: pre-wrap;
            height: 300px;
            overflow-y: auto;
        }
        .status-running {
            color: green;
            font-weight: bold;
        }
        .status-stopped {
            color: red;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Sepampam / Didin Wahyudin MOD</h1>", unsafe_allow_html=True)

# Input data
st.markdown("<h3>Tambah Session</h3>", unsafe_allow_html=True)
if "sessions" not in st.session_state:
    st.session_state.sessions = []

if st.button("Tambah Session"):
    st.session_state.sessions.append({
        "session": "",
        "shopid": "",
        "userig": "",
        "uuid": "",
        "url_raw_github": "",
        "pesan": "",
        "like_cnt": 10,
        "delay_between_actions": 1.0,
        "send_like": False,
        "send_message": False,
        "send_follow": False,
        "send_buy": False,
        "status": "Stopped",
    })

# Fungsi untuk memuat cookies
def load_cookies_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()
    except Exception as e:
        return []

# Fungsi untuk mengirim like
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
        return f"Error: {e}"

# Fungsi untuk mengirim pesan
def send_message(session_id, cookies, uuid, userig, content):
    url = f"https://live.shopee.co.id/api/v1/session/{session_id}/message"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'af-ac-enc-dat': '001ed94da16d0da5',
        'client-info': 'platform=9;device_id=9WKYLbnCkcojeuzaOGw7bKz1BScokjgs',
        'content-type': 'application/json',
        'origin': 'https://live.shopee.co.id',
        'priority': 'u=1, i',
        'referer': f'https://live.shopee.co.id/pc/live?session={session_id}',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-sz-sdk-version': '1.10.7',
        "cookie": "; ".join(cookies)
    }
    data = {
        'uuid': uuid,
        'usersig': userig,
        'content': f'{{"type":100,"content":"{content}"}}',
        'pin': False
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return "Pesan berhasil dikirim!"
        else:
            return f"Gagal mengirim pesan. Kode Status: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# Fungsi untuk mengirim follow
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
        return f"Error: {e}"

# Fungsi untuk memproses setiap session
def process_session(session_data, session_idx):
    cookies_list = load_cookies_from_github(session_data["url_raw_github"])
    session_logs[session_idx] = []
    if not cookies_list:
        session_logs[session_idx].append(f"Session {session_idx + 1}: Gagal memuat cookies.")
        st.session_state.sessions[session_idx]["status"] = "Stopped"
        return

    st.session_state.sessions[session_idx]["status"] = "Running"
    while running_sessions.get(session_idx, False):
        for cookie in cookies_list:
            if session_data["send_like"]:
                log = send_like(session_data["session"], [cookie], session_data["like_cnt"])
                session_logs[session_idx].append(log)

            if session_data["send_message"]:
                log = send_message(session_data["session"], [cookie], session_data["uuid"], session_data["userig"], session_data["pesan"])
                session_logs[session_idx].append(log)

            if session_data["send_follow"]:
                log = send_follow(session_data["session"], session_data["shopid"], [cookie])
                session_logs[session_idx].append(log)

            time.sleep(session_data["delay_between_actions"])

    st.session_state.sessions[session_idx]["status"] = "Stopped"

# Menampilkan session yang sudah ditambahkan
for idx, session_data in enumerate(st.session_state.sessions):
    with st.expander(f"Session {idx + 1}"):
        session_data["session"] = st.text_input(f"Session ID ({idx + 1}):", value=session_data["session"], key=f"session-{idx}")
        session_data["shopid"] = st.text_input(f"Shop ID ({idx + 1}):", value=session_data["shopid"], key=f"shopid-{idx}")
        session_data["userig"] = st.text_input(f"User IG ({idx + 1}):", value=session_data["userig"], key=f"userig-{idx}")
        session_data["uuid"] = st.text_input(f"UUID ({idx + 1}):", value=session_data["uuid"], key=f"uuid-{idx}")
        session_data["url_raw_github"] = st.text_input(f"URL Raw GitHub ({idx + 1}):", value=session_data["url_raw_github"], key=f"url-{idx}")
        session_data["pesan"] = st.text_area(f"Pesan ({idx + 1}):", value=session_data["pesan"], key=f"pesan-{idx}")

        # Slider untuk jumlah like dan delay antar aksi
        session_data["like_cnt"] = st.slider(f"Jumlah Like ({idx + 1}):", min_value=1, max_value=50, value=session_data["like_cnt"], key=f"like-{idx}")
        session_data["delay_between_actions"] = st.slider(f"Delay antar aksi (detik) ({idx + 1}):", min_value=0.1, max_value=5.0, value=session_data["delay_between_actions"], key=f"delay-{idx}")

        # Checkbox untuk bot
        session_data["send_like"] = st.checkbox(f"Kirim Like ({idx + 1})", value=session_data["send_like"], key=f"send-like-{idx}")
        session_data["send_message"] = st.checkbox(f"Kirim Pesan ({idx + 1})", value=session_data["send_message"], key=f"send-message-{idx}")
        session_data["send_follow"] = st.checkbox(f"Kirim Follow ({idx + 1})", value=session_data["send_follow"], key=f"send-follow-{idx}")

        # Tombol Start/Stop dan Hapus
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Start", key=f"start-{idx}"):
                if not running_sessions.get(idx, False):
                    running_sessions[idx] = True
                    threading.Thread(target=process_session, args=(session_data, idx), daemon=True).start()
        with col2:
            if st.button("Stop", key=f"stop-{idx}"):
                running_sessions[idx] = False
        with col3:
            if st.button("Hapus", key=f"delete-{idx}"):
                del st.session_state.sessions[idx]
                st.experimental_rerun()

        # Menampilkan status
        status = session_data["status"]
        if status == "Running":
            st.markdown("<p class='status-running'>Status: Running</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='status-stopped'>Status: Stopped</p>", unsafe_allow_html=True)

# Menampilkan log dari setiap session
st.markdown("<h3>Log Data yang Berjalan</h3>", unsafe_allow_html=True)
for idx, logs in session_logs.items():
    st.markdown(f"<h4>Session {idx + 1}:</h4>", unsafe_allow_html=True)
    st.markdown(f"<div class='log-box'>{'<br>'.join(logs[-20:])}</div>", unsafe_allow_html=True)
