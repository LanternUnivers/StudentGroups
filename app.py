import streamlit as st
import json
import os
import pandas as pd  # 地図表示のために必要
from geopy.geocoders import Nominatim  # 地名から緯度・経度を取得するために必要
from PIL import Image  # 画像処理用

# データファイルのパス
DATA_FILE = "data/groups.json"
ICON_FOLDER = "data/icons"  # アイコン画像を保存するフォルダ

# JSONデータを読み込む関数
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# JSONデータを保存する関数
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# アイコン画像を保存する関数
def save_icon(icon_file, group_name):
    if not os.path.exists(ICON_FOLDER):
        os.makedirs(ICON_FOLDER)
    icon_path = os.path.join(ICON_FOLDER, f"{group_name}.png")
    with open(icon_path, "wb") as f:
        f.write(icon_file.getbuffer())
    return icon_path

# メインアプリ
def main():
    st.title("学生団体イベントアプリ3")
    # タイトルとアイコンを横並びに表示（HTMLとCSSを使用）
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px;">
            <h1 style="margin: 0; font-size: 2.5rem;">Co-Act</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # データをロード
    groups = load_data()

    # タブで機能を切り替え
    tab1, tab2, tab3, tab4, tab5, tab3, tab4 = st.tabs(["イベント一覧", "イベントを登録する", "イベントに参加する", "サークル代表者用", "イベントマップ", "イベントに参加する", "サークル代表者用"])

    # イベント一覧表示
    with tab1:
        st.header("イベント一覧")
        if groups:
            for group in groups:
                # サークルアイコンを表示
                col1, col2 = st.columns([1, 9])
                with col1:
                    if "icon" in group and os.path.exists(group["icon"]):
                        st.image(group["icon"], width=50)
                    else:
                        st.image("https://via.placeholder.com/50", width=50)  # デフォルト画像
                with col2:
                    st.markdown(f"## {group['name']}")
                if "events" in group and group["events"]:
                    for event in group["events"]:
                        st.markdown(
                            f"""
                            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #003366; color: white;">
                                <h4 style="color: #ffffff;">🎯 イベント名: {event['title']}</h4>
                                <p><strong>📍 場所:</strong> {event.get('location', '未設定')}</p>
                                <p><strong>📅 日時:</strong> {event.get('date', '未設定')}</p>
                                <p><strong>📝 イベント内容:</strong> {event.get('description', '未設定')}</p>
                                <p><strong>👥 応募対象:</strong> {event.get('target', '未設定')}</p>
                                <p><strong>📊 応募人数:</strong> {event.get('capacity', '未設定')}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<p style='color: gray;'>現在、この団体には登録されたイベントがありません。</p>",
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                "<p style='color: gray;'>現在、登録されている学生団体はありません。</p>",
                unsafe_allow_html=True
            )

    # イベント登録フォーム
    with tab2:
        st.header("イベントを登録する")

        # サークル追加フォーム
        st.subheader("サークルを追加する")
        with st.form("add_group_form"):
            new_group_name = st.text_input("新しいサークル名")
            group_submitted = st.form_submit_button("サークルを追加")

            if group_submitted:
                if new_group_name:
                    # サークルが既に存在するか確認
                    if any(group["name"] == new_group_name for group in groups):
                        st.error(f"サークル '{new_group_name}' は既に存在します。")
                    else:
                        groups.append({"name": new_group_name, "events": []})
                        save_data(groups)
                        st.success(f"サークル '{new_group_name}' を追加しました！")
                else:
                    st.error("サークル名を入力してください。")

        # イベント追加フォーム
        st.subheader("イベントを追加する")

        # サークル追加フォーム
        st.subheader("サークルを追加する")
        with st.form("add_group_form"):
            new_group_name = st.text_input("新しいサークル名")
            icon_file = st.file_uploader("サークルアイコンをアップロード (PNG形式)", type=["png"])
            group_submitted = st.form_submit_button("サークルを追加")

            if group_submitted:
                if new_group_name:
                    # サークルが既に存在するか確認
                    if any(group["name"] == new_group_name for group in groups):
                        st.error(f"サークル '{new_group_name}' は既に存在します。")
                    else:
                        icon_path = None
                        if icon_file:
                            icon_path = save_icon(icon_file, new_group_name)
                        groups.append({"name": new_group_name, "events": [], "icon": icon_path})
                        save_data(groups)
                        st.success(f"サークル '{new_group_name}' を追加しました！")
                else:
                    st.error("サークル名を入力してください。")

        # イベント追加フォーム
        st.subheader("イベントを追加する")
        with st.form("add_event_form"):
            group_name = st.selectbox("団体名", [group["name"] for group in groups] if groups else [])
            event_title = st.text_input("イベント名")
            event_date = st.date_input("開催日時")
            event_location_name = st.text_input("イベントの場所 (地名)", placeholder="例: 東京タワー")
            event_location = st.text_input("場所")
            event_target = st.text_input("募集対象")
            event_capacity = st.number_input("募集人数", min_value=1, step=1)
            submitted = st.form_submit_button("登録")

            if submitted:
                if group_name and event_title and event_description and event_date and event_location_name:
                    try:
                        # 地名から緯度・経度を取得
                        geolocator = Nominatim(user_agent="student-groups-app")
                        location = geolocator.geocode(event_location_name)

                        if location:
                            lat, lon = location.latitude, location.longitude
                            # 該当する団体を検索してイベントを追加
                            for group in groups:
                                if group["name"] == group_name:
                                    if "events" not in group:
                                        group["events"] = []
                                    group["events"].append({
                                        "title": event_title,
                                        "description": event_description,
                                        "date": str(event_date),
                                        "location": event_location_name,
                                        "latitude": lat,
                                        "longitude": lon
                                    })
                                    save_data(groups)
                                    st.success(f"イベント '{event_title}' を団体 '{group_name}' に登録しました！")
                                    break
                        else:
                            st.error("指定された地名から緯度・経度を取得できませんでした。正しい地名を入力してください。")
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
                else:
                    st.error("すべての項目を入力してください。")

    # イベント参加フォーム
    with tab3:
        st.header("イベントに参加する")
        if "selected_event" in st.session_state:
            selected_event = st.session_state["selected_event"]
            st.write(f"**団体名:** {selected_event['group']}")
            st.write(f"**イベント名:** {selected_event['event']}")
            with st.form("join_event_form"):
                participant_name = st.text_input("参加者名")
                participant_email = st.text_input("メールアドレス")
                submitted = st.form_submit_button("参加登録")

                if submitted:
                    if participant_name and participant_email:
                        # 該当する団体とイベントを検索して参加者を追加
                        for group in groups:
                            if group["name"] == selected_event["group"]:
                                for event in group.get("events", []):
                                    if event["title"] == selected_event["event"]:
                                        if "participants" not in event:
                                            event["participants"] = []
                                        event["participants"].append({
                                            "name": participant_name,
                                            "email": participant_email
                                        })
                                        save_data(groups)
                                        st.success(f"'{participant_name}' さんがイベント '{event['title']}' に参加登録しました！")
                                        # 状態をリセット
                                        del st.session_state["selected_event"]
                                        st.session_state["tab"] = "イベント一覧"
                                        break
                    else:
                        st.error("すべての項目を入力してください。")
        else:
            st.write("参加するイベントを選択してください。")

    # サークル代表者用タブ
    with tab4:
        st.header("サークル代表者用ページ")
        
        # サークル選択とパスワード入力
        selected_group = st.selectbox("サークルを選択してください", [group["name"] for group in groups])
        password = st.text_input("パスワードを入力してください", type="password")

        # 該当サークルを取得
        group_data = next((group for group in groups if group["name"] == selected_group), None)

        if group_data:
            # サークルごとのパスワードを確認
            correct_password = group_data.get("password", selected_group)

            if password == correct_password:
                st.success(f"認証に成功しました！ サークル: {selected_group}")
                if "events" in group_data and group_data["events"]:
                    for event in group_data["events"]:
                        st.write(f"**イベント名:** {event['title']}")
                        st.write(f"**場所:** {event.get('location', '未設定')}")
                        st.write(f"**日時:** {event.get('date', '未設定')}")
                        st.write(f"**イベント内容:** {event.get('description', '未設定')}")
                        st.write(f"**応募対象:** {event.get('target', '未設定')}")
                        st.write(f"**応募人数:** {event.get('capacity', '未設定')}")
                        
                        # イベント削除ボタン
                        if st.button(f"イベントを削除 ({event['title']})", key=f"delete_{group_data['name']}_{event['title']}"):
                            group_data["events"].remove(event)
                            save_data(groups)
                            st.success(f"イベント '{event['title']}' を削除しました！")
                            # 状態をリセットして再描画
                            st.query_params = {"refresh": "true"}
                        st.write("---")
                else:
                    st.write("現在、このサークルには登録されたイベントがありません。")
            elif password:
                st.error("パスワードが間違っています。")
        else:
            st.error("選択されたサークルが見つかりません。")

    # イベントマップ表示
    with tab5:
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
                            "group": group["name"],
                            "description": event.get("description", "説明なし"),
                            "date": event.get("date", "未設定"),
                            "location": event.get("location", "未設定")
                        })
        if map_data:
            df = pd.DataFrame(map_data)
            st.map(df)
            st.write("**イベント情報一覧:**")
            for data in map_data:
                st.write(f"- **イベント名:** {data['event']}, **団体名:** {data['group']}, **場所:** {data['location']}, **日時:** {data['date']}, **説明:** {data['description']}")
        else:
            st.write("現在、地図に表示できるイベントはありません。")

    # イベント参加フォーム
    with tab3:
        st.header("イベントに参加する")
        if "selected_event" in st.session_state:
            selected_event = st.session_state["selected_event"]
            st.write(f"**団体名:** {selected_event['group']}")
            st.write(f"**イベント名:** {selected_event['event']}")
            with st.form("join_event_form"):
                participant_name = st.text_input("参加者名")
                participant_email = st.text_input("メールアドレス")
                submitted = st.form_submit_button("参加登録")

                if submitted:
                    if participant_name and participant_email:
                        # 該当する団体とイベントを検索して参加者を追加
                        for group in groups:
                            if group["name"] == selected_event["group"]:
                                for event in group.get("events", []):
                                    if event["title"] == selected_event["event"]:
                                        if "participants" not in event:
                                            event["participants"] = []
                                        event["participants"].append({
                                            "name": participant_name,
                                            "email": participant_email
                                        })
                                        save_data(groups)
                                        st.success(f"'{participant_name}' さんがイベント '{event['title']}' に参加登録しました！")
                                        # 状態をリセット
                                        del st.session_state["selected_event"]
                                        st.session_state["tab"] = "イベント一覧"
                                        break
                    else:
                        st.error("すべての項目を入力してください。")
        else:
            st.write("参加するイベントを選択してください。")

    # サークル代表者用タブ
    with tab4:
        st.header("サークル代表者用ページ")
        
        # サークル選択とパスワード入力
        selected_group = st.selectbox("サークルを選択してください", [group["name"] for group in groups])
        password = st.text_input("パスワードを入力してください", type="password")

        # 該当サークルを取得
        group_data = next((group for group in groups if group["name"] == selected_group), None)

        if group_data:
            # サークルごとのパスワードを設定（ここでは仮にサークル名をパスワードにしています）
            correct_password = group_data.get("password", selected_group)  # デフォルトでサークル名をパスワードに

            if password == correct_password:
                st.success(f"認証に成功しました！ サークル: {selected_group}")
                if "events" in group_data and group_data["events"]:
                    for event in group_data["events"]:
                        st.write(f"**イベント名:** {event['title']}")
                        st.write(f"**場所:** {event.get('location', '未設定')}")
                        st.write(f"**日時:** {event.get('date', '未設定')}")
                        st.write(f"**イベント内容:** {event.get('description', '未設定')}")
                        st.write(f"**応募対象:** {event.get('target', '未設定')}")
                        st.write(f"**応募人数:** {event.get('capacity', '未設定')}")
                        
                        # 参加者一覧を表示
                        if "participants" in event and event["participants"]:
                            st.write("**参加者一覧:**")
                            for participant in event["participants"]:
                                st.write(f"- {participant['name']} ({participant['email']})")
                        else:
                            st.write("**参加者一覧:** 現在参加者はいません。")
                        st.write("---")
                else:
                    st.write("現在、このサークルには登録されたイベントがありません。")
            elif password:
                st.error("パスワードが間違っています。")
        else:
            st.error("選択されたサークルが見つかりません。")

if __name__ == "__main__":
    main()