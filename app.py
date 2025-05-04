import streamlit as st
import json
import os
import pandas as pd
from geopy.geocoders import Nominatim
from PIL import Image
import bcrypt

# 定数
DATA_FILE = "data/groups.json"
ICON_FOLDER = "data/icons"
DEFAULT_ICON_URL = "data/icons/default_icon.png"

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

    # 検索ボックスとカテゴリー選択
    col1, col2 = st.columns([8, 2])
    with col1:
        search_query = st.text_input("イベント名で検索", "")
    with col2:
        category_filter = st.multiselect("ジャンルごとに検索", ["新歓", "勉強会", "交流会", "スポーツ", "ボランティア", "ものづくり系", "旅行", "インターン", "追いコン"], key="category_filter")

    # フィルタリングとソート
    filtered_groups = []
    for group in groups:
        if "events" in group and group["events"]:
            filtered_events = [
                event for event in group["events"]
                if (search_query.lower() in event["title"].lower()) and
                   (not category_filter or event.get("category") in category_filter)  # カテゴリーフィルタ適用
            ]
            if filtered_events:
                group_copy = group.copy()
                group_copy["events"] = filtered_events
                filtered_groups.append(group_copy)

    # イベント表示
    if filtered_groups:
        for group_index, group in enumerate(filtered_groups):
            col1, col2 = st.columns([1, 9])
            with col1:
                icon_path = group.get("icon") or "data/icons/default_icon.png"
                st.image(icon_path, width=40)
            with col2:
                st.markdown(
                    f"<h3 style='font-size: 30px;'>{group['name']}</h3>", 
                    unsafe_allow_html=True
                )

            if "events" in group and group["events"]:
                for event_index, event in enumerate(group["events"]):
                    # セッション状態の初期化
                    map_key = f"show_map_{group_index}_{event_index}"
                    if map_key not in st.session_state:
                        st.session_state[map_key] = False

                    # イベント情報の表示
                    st.markdown(
                        f"""
                        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #f0f8ff; color: #333;">
                            <h4 style="color: #333;">🎯 イベント名: {event['title']}</h4>
                            <p><strong>📍 場所:</strong> <a href="#" id="location_{group_index}_{event_index}" style="color: #007acc; text-decoration: underline;" onclick="window.showMap('{map_key}')">{event.get('location', '未設定')}</a></p>
                            <p><strong>📅 日時:</strong> {event.get('date', '未設定')}</p>
                            <p><strong>📝 イベント内容:</strong> {event.get('description', '未設定')}</p>
                            <p><strong>📊 募集人数:</strong> {event.get('capacity', '未設定')}</p>
                            <p><strong>🏷️ カテゴリー:</strong> {event.get('category', '未設定')}</p>
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

                    # 地図の表示
                    show_map = st.checkbox("地図を見る", key=f"map_checkbox_{group_index}_{event_index}", value=st.session_state.get(map_key, False))
                    st.session_state[map_key] = show_map

                    if st.session_state[map_key]:
                        st.map(pd.DataFrame([{
                            "lat": event["latitude"],
                            "lon": event["longitude"]
                        }]))

                    # レビュー表示
                    if "reviews" in event:
                        st.markdown(
                            "<h4 style='font-size: 18px;'>✒️レビュー</h4>",
                            unsafe_allow_html=True
                            )
                        for review in event["reviews"]:
                            st.markdown(
                                f"""
                                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #ffffe0;">
                                    <strong>【満足度】</strong> ⭐{review['satisfaction']} / ⭐5 <br>
                                    <strong>【感想】</strong> {review['feedback']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        # レビューの後に空白を挿入
                        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

            # 団体間に空白行を追加
            st.markdown("<hr style='border: none; height: 5px;'>", unsafe_allow_html=True)
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

# イベント追加フォーム
def add_event_form(groups):
    st.subheader("イベントを追加する")
    with st.form("add_event_form"):
        group_name = st.selectbox("団体名", [group["name"] for group in groups] if groups else [])
        event_title = st.text_input("イベント名")
        event_date = st.date_input("開催日時")
        event_location_name = st.text_input("イベントの場所 (地名)", placeholder="例: 東京タワー")
        event_description = st.text_area("イベント内容")
        event_capacity = st.number_input("募集人数", min_value=1, step=1)
        submitted = st.form_submit_button("登録")

        if submitted:
            if group_name and event_title and event_description and event_date and event_location_name:
                try:
                    geolocator = Nominatim(user_agent="student-groups-app")
                    location = geolocator.geocode(event_location_name)
                    if location:
                        lat, lon = location.latitude, location.longitude
                        for group in groups:
                            if group["name"] == group_name:
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
                                st.success(f"イベント '{event_title}' を団体 '{group_name}' に登録しました！")
                                break
                    else:
                        st.error("指定された地名から緯度・経度を取得できませんでした。正しい地名を入力してください。")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
            else:
                st.error("すべての項目を入力してください。")

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

        # イベント一覧セクション
        st.subheader("登録済みのイベント")
        if group and "events" in group and group["events"]:
            for event_index, event in enumerate(group["events"]):
                with st.container():
                    st.markdown(f"### 🎯 イベント名: {event['title']}")
                    st.markdown(f"- 📅 開催日時: {event.get('date', '未設定')}")
                    st.markdown(f"- 📍 場所: {event.get('location', '未設定')}")
                    st.markdown(f"- 📝 内容: {event.get('description', '未設定')}")
                    st.markdown(f"- 📊 募集人数: {event.get('capacity', '未設定')}")
                    st.markdown(f"- 🏷️ カテゴリー: {event.get('category', '未設定')}")

                    # 応募者リスト
                    if "applicants" in event and event["applicants"]:
                        st.markdown("#### 応募者リスト:")
                        for applicant in event["applicants"]:
                            st.markdown(f"- 名前: {applicant['name']}, メール: {applicant['email']}")
                    else:
                        st.markdown("- 応募者なし")

                    # 操作ボタンを縦に配置
                    if st.button(f"イベントを削除 ({event['title']})", key=f"delete_{group['name']}_{event_index}"):
                        st.session_state["delete_event"] = {
                            "group_name": group["name"],
                            "event_index": event_index
                        }
                        st.rerun()

                    # 編集フォームを展開するための expander
                    with st.expander(f"編集 ({event['title']})"):
                        with st.form(f"edit_event_form_{event_index}"):
                            new_title = st.text_input("イベント名", value=event["title"])
                            new_date = st.date_input("開催日時", value=pd.to_datetime(event["date"]))
                            new_location = st.text_input("イベントの場所", value=event.get("location", ""))
                            new_description = st.text_area("イベント内容", value=event.get("description", ""))
                            new_capacity = st.number_input("募集人数", min_value=1, step=1, value=event.get("capacity", 1))
                            submitted = st.form_submit_button("保存")

                            if submitted:
                                try:
                                    # 新しい場所の座標を取得
                                    geolocator = Nominatim(user_agent="student-groups-app")
                                    location = geolocator.geocode(new_location)
                                    if location:
                                        lat, lon = location.latitude, location.longitude
                                        # イベント情報を更新
                                        event["title"] = new_title
                                        event["date"] = str(new_date)
                                        event["location"] = new_location
                                        event["description"] = new_description
                                        event["capacity"] = new_capacity
                                        event["latitude"] = lat
                                        event["longitude"] = lon
                                        save_data(groups)
                                        st.success(f"イベント '{new_title}' を更新しました！")
                                        st.rerun()
                                    else:
                                        st.error("指定された地名から緯度・経度を取得できませんでした。正しい地名を入力してください。")
                                except Exception as e:
                                    st.error(f"エラーが発生しました: {e}")

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

        # イベント追加セクション
        st.subheader("イベントを追加する")
        with st.form("add_event_form"):
            event_title = st.text_input("イベント名")
            event_date = st.date_input("開催日時")
            event_location_name = st.text_input("イベントの場所 (地名)", placeholder="例: 東京タワー")
            event_description = st.text_area("イベント内容")
            event_capacity = st.number_input("募集人数", min_value=1, step=1)
            event_category = st.selectbox("カテゴリー", ["新歓", "勉強会", "交流会", "スポーツ", "ボランティア", "ものづくり系", "旅行", "インターン", "追いコン"])  # カテゴリー選択
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
                                "capacity": event_capacity,
                                "category": event_category  # ← カテゴリーを保存
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

# ジャンル選択ページ(クリックして検索までは実装できなかった)
def genre_selection_page():
    st.header("ジャンルを選択してください")

    # ジャンルリスト
    genres = [
        {"name": "新歓", "image": "data/images/shinkan.jpg"},
        {"name": "勉強会", "image": "data/images/study.jpeg"},
        {"name": "交流会", "image": "data/images/networking.jpg"},
        {"name": "スポーツ", "image": "data/images/sports.jpg"},
        {"name": "ボランティア", "image": "data/images/volunteer.jpg"},
        {"name": "ものづくり系", "image": "data/images/creation.jpeg"},
        {"name": "旅行", "image": "data/images/travel.jpg"},
        {"name": "インターン", "image": "data/images/internship.jpg"},
        {"name": "追いコン", "image": "data/images/farewell.jpg"},
    ]

    # グリッド形式でジャンルを表示
    cols = st.columns(3)  # 3列のグリッドを作成
    for index, genre in enumerate(genres):
        with cols[index % 3]:  # 各列に順番に配置
            image_path = genre["image"]
            if os.path.exists(image_path):  # ファイルが存在するか確認
                st.image(image_path, caption=genre["name"])
            else:
                st.error(f"画像が見つかりません: {image_path}")


# レビュー投稿ページ
def review_page(groups):
    st.header("レビューを書く")

    # イベント選択
    event_options = [
        (group["name"], event["title"])
        for group in groups if "events" in group and group["events"]
        for event in group["events"]
    ]
    if not event_options:
        st.info("現在、レビュー可能なイベントはありません。")
        return

    selected_event = st.selectbox(
        "レビューするイベントを選択してください",
        options=event_options,
        format_func=lambda x: f"{x[0]} - {x[1]}"
    )

    # ユーザー入力
    st.subheader("ユーザー認証")
    user_name = st.text_input("名前を入力してください")
    user_email = st.text_input("メールアドレスを入力してください")

    # 認証処理（最初に一回だけ）
    if "auth_success" not in st.session_state:
        st.session_state.auth_success = False

    if st.button("認証"):
        group_name, event_title = selected_event
        group_index = next((i for i, g in enumerate(groups) if g["name"] == group_name), None)

        if group_index is not None:
            event_index = next((j for j, e in enumerate(groups[group_index]["events"]) if e["title"] == event_title), None)

            if event_index is not None:
                event = groups[group_index]["events"][event_index]
                if "applicants" in event and any(app["email"] == user_email and app["name"] == user_name for app in event["applicants"]):
                    st.session_state.auth_success = True
                    st.session_state.group_index = group_index
                    st.session_state.event_index = event_index
                    st.session_state.user_name = user_name
                    st.session_state.user_email = user_email
                    st.success("認証に成功しました！")
                else:
                    st.error("応募者リストに存在しません。正しい名前とメールアドレスを入力してください。")
            else:
                st.error("イベントが見つかりません。")
        else:
            st.error("グループが見つかりません。")

    # 認証後のレビュー投稿画面
    if st.session_state.get("auth_success"):
        group_index = st.session_state.group_index
        event_index = st.session_state.event_index
        event = groups[group_index]["events"][event_index]
        user_email = st.session_state.user_email
        user_name = st.session_state.user_name

        if "reviews" in event and any(review["email"] == user_email for review in event["reviews"]):
            st.info("このイベントにはすでにレビューを投稿済みです。")
        else:
            st.subheader("レビューを書く")
            with st.form(f"review_form_{group_index}_{event_index}"):
                satisfaction = st.slider("満足度 (⭐1-⭐5)", 1, 5)
                feedback = st.text_area("感想")
                review_submitted = st.form_submit_button("レビューを送信")
                if review_submitted:
                    if "reviews" not in groups[group_index]["events"][event_index]:
                        groups[group_index]["events"][event_index]["reviews"] = []

                    groups[group_index]["events"][event_index]["reviews"].append({
                        "name": user_name,
                        "email": user_email,
                        "satisfaction": satisfaction,
                        "feedback": feedback
                    })
                    save_data(groups)
                    st.success("レビューを送信しました！")
                    st.session_state.auth_success = False  # 認証セッションを終了

# メイン関数
def main():
    # タイトルの背景を設定
    title_bg_style = '''
    <style>
    .title-container {
        font-family: 'Arial', sans-serif; /* フォントを設定 */
        background-color: #008080; /* 暗い背景色 */
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
        <h1 style="color: #ffffff;">Rally</h1>
        <p style="color: #ffffff;">ー サークル・学生団体と学生を繋ぐ ー</p>
    </div>
    <div class="spacer"></div> <!-- タイトルとタブの間に空白を挿入 -->
    '''
    st.markdown(title_bg_style, unsafe_allow_html=True)

    # セッションに現在のタブを保存
    if "current_tab" not in st.session_state:
        st.session_state["current_tab"] = "イベント一覧"  # 初期タブを設定

    # タブの選択
    tabs = ["イベント一覧", "ジャンルを選択する", "イベントマップ", "レビューを書く", "サークルを登録する", "サークル管理者画面"]
    selected_tab = st.selectbox("タブを選択してください", tabs, index=tabs.index(st.session_state["current_tab"]))

    # タブが変更された場合にリロード
    if selected_tab != st.session_state["current_tab"]:
        st.session_state["current_tab"] = selected_tab
        st.rerun()

    # タブごとの処理
    groups = load_data()
    if selected_tab == "イベント一覧":
        display_event_list(groups)
    elif selected_tab == "ジャンルを選択する":
        genre_selection_page()
    elif selected_tab == "イベントマップ":
        display_map(groups)
    elif selected_tab == "レビューを書く":
        review_page(groups)
    elif selected_tab == "サークルを登録する":
        add_group_form(groups)
    elif selected_tab == "サークル管理者画面":
        admin_panel(groups)

if __name__ == "__main__":
    main()