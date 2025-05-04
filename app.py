import streamlit as st
import json
import os
import pandas as pd
from geopy.geocoders import Nominatim
from PIL import Image
import bcrypt
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語フォントを設定
rcParams['font.family'] = 'Yu Gothic'  # Windowsの場合、'Meiryo' も可

# 定数
DATA_FILE = "data/groups.json"
ICON_FOLDER = "data/icons"
DEFAULT_ICON_URL = "data\icons\default_icon.png"

# データ操作関連
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def save_icon(icon_file, group_name):
    if not os.path.exists(ICON_FOLDER):
        os.makedirs(ICON_FOLDER)
    icon_path = os.path.join(ICON_FOLDER, f"{group_name}.png")
    with open(icon_path, "wb") as f:
        f.write(icon_file.getbuffer())
    return icon_path

# パスワードハッシュ化関連
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# イベント一覧表示（応募機能付き）
def display_event_list(groups):
    st.header("イベント一覧")

    # 検索ボックスと並び替えオプション
    search_query = st.text_input("イベント名で検索", "")
    sort_option = st.selectbox("並び替え", ["開催日時（昇順）", "開催日時（降順）", "イベント名（昇順）", "イベント名（降順）"])

    # フィルタリングとソート
    filtered_groups = []
    for group in groups:
        if "events" in group and group["events"]:
            filtered_events = [
                event for event in group["events"]
                if search_query.lower() in event["title"].lower()
            ]
            if filtered_events:
                group_copy = group.copy()
                group_copy["events"] = filtered_events
                filtered_groups.append(group_copy)

    # 並び替え処理
    for group in filtered_groups:
        if sort_option == "開催日時（昇順）":
            group["events"].sort(key=lambda x: x.get("date", ""))
        elif sort_option == "開催日時（降順）":
            group["events"].sort(key=lambda x: x.get("date", ""), reverse=True)
        elif sort_option == "イベント名（昇順）":
            group["events"].sort(key=lambda x: x.get("title", "").lower())
        elif sort_option == "イベント名（降順）":
            group["events"].sort(key=lambda x: x.get("title", "").lower(), reverse=True)

    # イベント表示
    if filtered_groups:
        for group_index, group in enumerate(filtered_groups):  # グループのインデックスを取得
            col1, col2 = st.columns([1, 9])
            with col1:
                # 修正: icon_path が None の場合にデフォルトURLを使用
                icon_path = group.get("icon") or DEFAULT_ICON_URL
                st.image(icon_path, width=50)
            with col2:
                st.markdown(f"## {group['name']}")
            if "events" in group and group["events"]:
                for event_index, event in enumerate(group["events"]):  # イベントのインデックスを取得
                    st.markdown(
                        f"""
                        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #003366; color: white;">
                            <h4 style="color: #ffffff;">🎯 イベント名: {event['title']}</h4>
                            <p><strong>📍 場所:</strong> {event.get('location', '未設定')}</p>
                            <p><strong>📅 日時:</strong> {event.get('date', '未設定')}</p>
                            <p><strong>📝 イベント内容:</strong> {event.get('description', '未設定')}</p>
                            <p><strong>📊 募集人数:</strong> {event.get('capacity', '未設定')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    # 応募フォームを展開するボタン
                    with st.expander("応募する"):
                        form_key = f"apply_form_{group_index}_{event_index}"  # インデックスを含めたキー
                        with st.form(form_key):
                            name = st.text_input("名前を入力してください", key=f"name_{group_index}_{event_index}")
                            email = st.text_input("メールアドレスを入力してください", key=f"email_{group_index}_{event_index}")
                            submitted = st.form_submit_button("送信")
                            if submitted:
                                if name and email:
                                    if "applicants" not in event:
                                        event["applicants"] = []
                                    event["applicants"].append({"name": name, "email": email})
                                    save_data(groups)
                                    st.success(f"{name} さんがイベント '{event['title']}' に応募しました！")
                                else:
                                    st.error("名前とメールアドレスを入力してください。")
            else:
                st.markdown("<p style='color: gray;'>現在、この団体には登録されたイベントがありません。</p>", unsafe_allow_html=True)
            
            # 団体間に空白行を追加
            st.markdown("<hr style='border: none; height: 20px;'>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: gray;'>該当するイベントが見つかりません。</p>", unsafe_allow_html=True)

# サークル追加フォーム
def add_group_form(groups):
    st.subheader("サークルを追加する")
    with st.form("add_group_form"):
        new_group_name = st.text_input("新しいサークル名")
        icon_file = st.file_uploader("サークルアイコンをアップロード (PNG形式)", type=["png"])
        group_password = st.text_input("サークルのパスワード", type="password")
        group_submitted = st.form_submit_button("サークルを追加")

        if group_submitted:
            if new_group_name and group_password:
                if any(group["name"] == new_group_name for group in groups):
                    st.error(f"サークル '{new_group_name}' は既に存在します。")
                else:
                    icon_path = save_icon(icon_file, new_group_name) if icon_file else None
                    groups.append({
                        "name": new_group_name,
                        "password": hash_password(group_password),  # ハッシュ化
                        "events": [],
                        "icon": icon_path
                    })
                    save_data(groups)
                    st.success(f"サークル '{new_group_name}' を追加しました！")
            else:
                st.error("サークル名とパスワードを入力してください。")

# イベントマップ表示
def display_map(groups):
    st.header("イベントマップ")
    map_data = []
    for group in groups:
        if "events" in group and group["events"]:
            for event in group["events"]:
                if "latitude" in event and "longitude" in event:
                    map_data.append({
                        "lat": event["latitude"],
                        "lon": event["longitude"],
                        "event": event["title"],
                        "group": group["name"]
                    })
    if map_data:
        df = pd.DataFrame(map_data)
        st.map(df)
    else:
        st.write("現在、地図に表示できるイベントはありません。")

# 管理者画面
def admin_panel(groups):
    st.header("管理者画面")

    # セッションに初期値がなければ初期化
    if "authenticated_group" not in st.session_state:
        st.session_state["authenticated_group"] = None
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        selected_group = st.selectbox("管理するサークルを選択してください", [group["name"] for group in groups])
        password_input = st.text_input("パスワードを入力してください", type="password")

        if st.button("認証"):
            group = next((g for g in groups if g["name"] == selected_group), None)
            if group and check_password(password_input, group["password"]):  # ハッシュを比較
                st.session_state["authenticated_group"] = selected_group
                st.session_state["authenticated"] = True
                st.success(f"サークル '{selected_group}' の管理画面にアクセスしました！")
                st.rerun()
            else:
                st.error("パスワードが間違っています。")
    else:
        # ログイン済みのグループ名を取得
        selected_group = st.session_state["authenticated_group"]
        group = next((g for g in groups if g["name"] == selected_group), None)
        st.success(f"サークル '{selected_group}' の管理画面にアクセス中")
        st.subheader("登録済みのイベント")

        if group and "events" in group and group["events"]:
            for event_index, event in enumerate(group["events"]):
                st.markdown(f"### イベント名: {event['title']}")

                if "applicants" in event and event["applicants"]:
                    st.markdown("#### 応募者リスト:")
                    for applicant in event["applicants"]:
                        st.markdown(f"- 名前: {applicant['name']}, メール: {applicant['email']}")
                else:
                    st.markdown("- 応募者なし")

                delete_button_key = f"delete_{group['name']}_{event_index}"
                if st.button(f"イベントを削除 ({event['title']})", key=delete_button_key):
                    st.session_state["delete_event"] = {
                        "group_name": group["name"],
                        "event_index": event_index
                    }
                    st.rerun()

            # 削除処理（rerun後）
            if "delete_event" in st.session_state:
                to_delete = st.session_state.pop("delete_event")
                if to_delete["group_name"] == group["name"]:
                    if 0 <= to_delete["event_index"] < len(group["events"]):
                        deleted_event = group["events"].pop(to_delete["event_index"])
                        save_data(groups)
                        st.success(f"イベント '{deleted_event['title']}' を削除しました！")
                        st.rerun()
        else:
            st.markdown("- イベントなし")

        # イベント追加フォーム
        st.subheader("イベントを追加する")
        with st.form("add_event_form"):
            event_title = st.text_input("イベント名")
            event_date = st.date_input("開催日時")
            event_location_name = st.text_input("イベントの場所 (地名)", placeholder="例: 東京タワー")
            event_description = st.text_area("イベント内容")
            event_capacity = st.number_input("募集人数", min_value=1, step=1)
            submitted = st.form_submit_button("登録")

            if submitted:
                if event_title and event_description and event_date and event_location_name:
                    try:
                        geolocator = Nominatim(user_agent="student-groups-app")
                        location = geolocator.geocode(event_location_name)
                        if location:
                            lat, lon = location.latitude, location.longitude
                            group["events"].append({
                                "title": event_title,
                                "description": event_description,
                                "date": str(event_date),
                                "location": event_location_name,
                                "latitude": lat,
                                "longitude": lon,
                                "capacity": event_capacity
                            })
                            save_data(groups)
                            st.success(f"イベント '{event_title}' を団体 '{selected_group}' に登録しました！")
                        else:
                            st.error("指定された地名から緯度・経度を取得できませんでした。正しい地名を入力してください。")
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
                else:
                    st.error("すべての項目を入力してください。")

        # ログアウトボタン
        if st.button("ログアウト"):
            st.session_state["authenticated"] = False
            st.session_state["authenticated_group"] = None
            st.rerun()

def main():
    # タイトルの背景を設定
    title_bg_style = '''
    <style>
    .title-container {
        font-family: 'Noto Serif JP', sans-serif; /* フォントを設定 */
        background-color: #333333; /* 暗い背景色 */
        color: white; /* 文字色を白に設定 */
        padding: 10px; /* 内側の余白を設定 */
        border-radius: 5px; /* 角を丸くする */
        text-align: center; /* 中央揃え */
        width: 100%; /* 横幅を100%に設定 */
        margin-bottom: 30px; /* タイトル下に余白を追加 */
    }
    .spacer {
        height: 20px; /* 空白の高さを設定 */
    }
    </style>
    <div class="title-container">
        <h1>学生団体イベントアプリ</h1>
    </div>
    <div class="spacer"></div> <!-- タイトルとタブの間に空白を挿入 -->
    '''
    st.markdown(title_bg_style, unsafe_allow_html=True)

    # セッションに現在のタブを保存
    if "current_tab" not in st.session_state:
        st.session_state["current_tab"] = "イベント一覧"  # 初期タブを設定

    # タブの選択
    tabs = ["イベント一覧", "イベントマップ", "サークルを登録する", "サークル管理者画面"]
    selected_tab = st.selectbox("タブを選択してください", tabs, index=tabs.index(st.session_state["current_tab"]))

    # タブが変更された場合にリロード
    if selected_tab != st.session_state["current_tab"]:
        st.session_state["current_tab"] = selected_tab
        st.rerun()

    # タブごとの処理
    groups = load_data()
    if selected_tab == "イベント一覧":
        display_event_list(groups)
    elif selected_tab == "イベントマップ":
        display_map(groups)
    elif selected_tab == "サークルを登録する":
        add_group_form(groups)
    elif selected_tab == "サークル管理者画面":
        admin_panel(groups)

if __name__ == "__main__":
    main()