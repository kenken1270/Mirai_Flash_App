# flash_app.py — 未来塾 単語暗記アプリ（SM-2忘却曲線）
import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import date, timedelta

# ─────────────────────────────
# 設定・接続
# ─────────────────────────────
st.set_page_config(page_title="📖 単語暗記 | 未来塾", layout="centered")


@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


# ─────────────────────────────
# SM-2 アルゴリズム
# ─────────────────────────────
def sm2_update(quality: int, ease_factor: float, interval: int, repetitions: int):
    """
    quality: 0〜5（3以上で正解とみなす）
    返り値: (new_ef, new_interval, new_repetitions, next_review_date)
    """
    if quality < 3:
        # 不正解：最初からやり直し
        new_repetitions = 0
        new_interval = 1
    else:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)
        new_repetitions = repetitions + 1

    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + 0.02 * (5 - quality)))
    new_ef = max(1.3, new_ef)

    next_date = (date.today() + timedelta(days=new_interval)).isoformat()
    return new_ef, new_interval, new_repetitions, next_date


# ─────────────────────────────
# データ読み込み
# ─────────────────────────────
@st.cache_data(ttl=60)
def load_users():
    sb = get_supabase()
    res = sb.table("users").select("username").execute()
    if res.data:
        return [row["username"] for row in res.data]
    return []


@st.cache_data(ttl=30)
def load_flashcards(category=None, grade=None):
    sb = get_supabase()
    q = sb.table("flashcards").select("*")
    if category:
        q = q.eq("category", category)
    if grade:
        q = q.eq("grade", grade)
    res = q.execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()


@st.cache_data(ttl=30)
def load_review_status(username: str):
    """ユーザーの全復習記録（最新1件/カード）を取得"""
    sb = get_supabase()
    res = sb.table("review_logs").select("*").eq("username", username).execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    if df.empty:
        return df
    # flashcard_idごとに最新1件を残す
    df["reviewed_at"] = pd.to_datetime(df["reviewed_at"])
    df = df.sort_values("reviewed_at").groupby("flashcard_id").last().reset_index()
    return df


def save_review(username, flashcard_id, quality, ef, interval, reps, next_date):
    sb = get_supabase()
    sb.table("review_logs").insert({
        "username": username,
        "flashcard_id": flashcard_id,
        "quality": quality,
        "ease_factor": ef,
        "interval_days": interval,
        "repetitions": reps,
        "next_review_date": next_date,
    }).execute()
    st.cache_data.clear()


# ─────────────────────────────
# セッション初期化
# ─────────────────────────────
if "flash_user" not in st.session_state:
    st.session_state["flash_user"] = ""
if "flash_mode" not in st.session_state:
    st.session_state["flash_mode"] = "home"  # home / study / result
if "flash_queue" not in st.session_state:
    st.session_state["flash_queue"] = []
if "flash_index" not in st.session_state:
    st.session_state["flash_index"] = 0
if "flash_show_answer" not in st.session_state:
    st.session_state["flash_show_answer"] = False
if "flash_session_results" not in st.session_state:
    st.session_state["flash_session_results"] = []

# ─────────────────────────────
# ログイン画面
# ─────────────────────────────
if not st.session_state["flash_user"]:
    st.title("📖 単語暗記アプリ | 未来塾")

    user_list = load_users()

    if not user_list:
        st.warning("ユーザーが登録されていません。管理者に連絡してください。")
        st.stop()

    selected = st.selectbox(
        "ユーザーを選んでください",
        options=["--- 選んでください ---"] + user_list
    )

    if st.button("スタート！"):
        if selected == "--- 選んでください ---":
            st.error("ユーザーを選んでください")
        else:
            st.session_state["flash_user"] = selected
            st.rerun()

    st.stop()

username = st.session_state["flash_user"]

# ─────────────────────────────
# ホーム画面
# ─────────────────────────────
if st.session_state["flash_mode"] == "home":
    st.title(f"📖 こんにちは、{username}さん！")

    # カテゴリ・グレード選択
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("カテゴリ", ["英検", "JLPT", "理科", "社会", "その他"])
    with col2:
        grade = st.text_input("グレード（例：5級、N4）", "")

    df_cards = load_flashcards(category, grade if grade else None)

    if df_cards.empty:
        st.info("このカテゴリの単語はまだ登録されていません。")
    else:
        # 今日復習すべきカードを抽出
        df_review = load_review_status(username)
        today_str = date.today().isoformat()

        if df_review.empty:
            due_ids = df_cards["id"].tolist()
        else:
            reviewed_ids = df_review["flashcard_id"].tolist()
            due_df = df_review[df_review["next_review_date"] <= today_str]
            due_ids = due_df["flashcard_id"].tolist()
            # まだ一度もやっていないカードも追加
            new_ids = [i for i in df_cards["id"].tolist() if i not in reviewed_ids]
            due_ids = due_ids + new_ids

        due_cards = df_cards[df_cards["id"].isin(due_ids)]

        st.metric("今日の復習カード数", f"{len(due_cards)} 枚")
        st.metric("全カード数", f"{len(df_cards)} 枚")

        if len(due_cards) > 0:
            if st.button("🚀 今日の復習をはじめる！", type="primary"):
                st.session_state["flash_queue"] = due_cards.to_dict("records")
                st.session_state["flash_index"] = 0
                st.session_state["flash_show_answer"] = False
                st.session_state["flash_session_results"] = []
                st.session_state["flash_mode"] = "study"
                st.rerun()
        else:
            st.success("🎉 今日の復習は完了しています！")

    if st.button("🚪 ログアウト"):
        st.session_state["flash_user"] = ""
        st.rerun()

# ─────────────────────────────
# 学習画面
# ─────────────────────────────
elif st.session_state["flash_mode"] == "study":
    queue = st.session_state["flash_queue"]
    idx = st.session_state["flash_index"]

    if idx >= len(queue):
        st.session_state["flash_mode"] = "result"
        st.rerun()

    card = queue[idx]
    total = len(queue)

    st.progress((idx) / total, text=f"{idx + 1} / {total} 枚目")
    st.markdown("---")

    # カード表面
    st.markdown(f"## 🔤 {card['word']}")
    if card.get("reading"):
        st.caption(f"読み：{card['reading']}")

    if not st.session_state["flash_show_answer"]:
        if st.button("✅ 意味を見る", type="primary", use_container_width=True):
            st.session_state["flash_show_answer"] = True
            st.rerun()
    else:
        # カード裏面
        st.markdown(f"### 💡 {card['meaning']}")
        if card.get("example"):
            st.info(f"例文: {card['example']}")

        st.markdown("**どのくらい覚えていましたか？**")
        col1, col2, col3, col4 = st.columns(4)

        def record_quality(q):
            df_rev = load_review_status(username)
            cid = card["id"]
            if not df_rev.empty and cid in df_rev["flashcard_id"].values:
                row = df_rev[df_rev["flashcard_id"] == cid].iloc[0]
                ef = float(row["ease_factor"])
                iv = int(row["interval_days"])
                rp = int(row["repetitions"])
            else:
                ef, iv, rp = 2.5, 1, 0
            new_ef, new_iv, new_rp, next_date = sm2_update(q, ef, iv, rp)
            save_review(username, cid, q, new_ef, new_iv, new_rp, next_date)
            st.session_state["flash_session_results"].append({
                "word": card["word"],
                "quality": q,
                "next_review": next_date,
            })
            st.session_state["flash_index"] += 1
            st.session_state["flash_show_answer"] = False
            st.rerun()

        with col1:
            if st.button("😰\n全然\nわからない", use_container_width=True):
                record_quality(0)
        with col2:
            if st.button("🤔\nなんとなく\nわかった", use_container_width=True):
                record_quality(3)
        with col3:
            if st.button("😊\nだいたい\nわかった", use_container_width=True):
                record_quality(4)
        with col4:
            if st.button("🎯\nバッチリ\nわかった！", use_container_width=True):
                record_quality(5)

# ─────────────────────────────
# 結果画面
# ─────────────────────────────
elif st.session_state["flash_mode"] == "result":
    results = st.session_state["flash_session_results"]
    st.title("🎉 今日の学習完了！")

    perfect = [r for r in results if r["quality"] >= 4]
    ok = [r for r in results if r["quality"] == 3]
    ng = [r for r in results if r["quality"] < 3]

    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 バッチリ", f"{len(perfect)} 枚")
    col2.metric("🤔 まあまあ", f"{len(ok)} 枚")
    col3.metric("😰 要復習", f"{len(ng)} 枚")

    if ng:
        st.warning("次回すぐに復習するカード:")
        for r in ng:
            st.write(f"- {r['word']}")

    if st.button("🏠 ホームへ戻る", type="primary"):
        st.session_state["flash_mode"] = "home"
        st.session_state["flash_session_results"] = []
        st.rerun()
