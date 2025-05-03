import streamlit as st
import json
import os

# データファイルのパス
DATA_FILE = "data/groups.json"

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

# メインアプリ
def main():
    st.title("学生団体イベントアプリ3")

    # データをロード
    groups = load_data()

    # タブで機能を切り替え
    tab1, tab2, tab3, tab4 = st.tabs(["イベント一覧", "イベントを登録する", "イベントに参加する", "サークル代表者用"])

    # イベント一覧表示
    with tab1:
        st.header("イベント一覧")
        if groups:
            for group in groups:
                st.subheader(group["name"])
                if "events" in group and group["events"]:
                    for event in group["events"]:
                        st.write(f"**イベント名:** {event['title']}")
                        st.write(f"**場所:** {event.get('location', '未設定')}")
                        st.write(f"**日時:** {event.get('date', '未設定')}")
                        st.write(f"**イベント内容:** {event.get('description', '未設定')}")
                        st.write(f"**応募対象:** {event.get('target', '未設定')}")
                        st.write(f"**応募人数:** {event.get('capacity', '未設定')}")
                        
                        if st.button(f"参加する ({event['title']})", key=f"join_{group['name']}_{event['title']}"):
                            st.session_state["selected_event"] = {"group": group["name"], "event": event["title"]}
                            st.session_state["tab"] = "イベントに参加する"
                        st.write("---")
                else:
                    st.write("現在、この団体には登録されたイベントがありません。")
        else:
            st.write("現在、登録されている学生団体はありません。")

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
        with st.form("add_event_form"):
            group_name = st.selectbox("団体名", [group["name"] for group in groups] if groups else [])
            event_title = st.text_input("イベント名")
            event_description = st.text_area("イベントの説明")
            event_date = st.date_input("イベント日時")
            submitted = st.form_submit_button("登録")

            if submitted:
                if group_name and event_title and event_description and event_date:
                    # 該当する団体を検索してイベントを追加
                    for group in groups:
                        if group["name"] == group_name:
                            if "events" not in group:
                                group["events"] = []
                            group["events"].append({
                                "title": event_title,
                                "description": event_description,
                                "date": str(event_date)
                            })
                            save_data(groups)
                            st.success(f"イベント '{event_title}' を団体 '{group_name}' に登録しました！")
                            break
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