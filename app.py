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
    st.title("学生団体イベントアプリ")

    # データをロード
    groups = load_data()

    # タブで機能を切り替え
    tab1, tab2 = st.tabs(["イベント一覧", "イベントを登録する"])

    # イベント一覧表示
    with tab1:
        st.header("イベント一覧")
        if groups:
            for group in groups:
                st.subheader(group["name"])
                if "events" in group and group["events"]:
                    for event in group["events"]:
                        st.write(f"**イベント名:** {event['title']}")
                        st.write(f"**説明:** {event['description']}")
                        st.write(f"**日時:** {event['date']}")
                        st.write("---")
                else:
                    st.write("現在、この団体には登録されたイベントがありません。")
        else:
            st.write("現在、登録されている学生団体はありません。")

    # イベント登録フォーム
    with tab2:
        st.header("イベントを登録する")
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

if __name__ == "__main__":
    main()