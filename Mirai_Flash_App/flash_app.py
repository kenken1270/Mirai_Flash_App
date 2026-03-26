# flash_app.py — 未来塾 単語暗記アプリ（SM-2忘却曲線）
import random
from typing import List, Tuple

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


def load_flashcard_sets() -> List[dict]:
    try:
        sb = get_supabase()
        res = sb.table("flashcard_sets").select(
            "id,set_name,category,grade,description"
        ).execute()
        if res.data:
            return list(res.data)
        return []
    except Exception:
        return []


def load_flashcards_by_set(set_id) -> List[dict]:
    try:
        sb = get_supabase()
        res = sb.table("flashcards").select("*").eq("set_id", set_id).execute()
        if res.data:
            return list(res.data)
        return []
    except Exception:
        return []


@st.cache_data(ttl=30)
def load_review_status(username: str):
    """ユーザーの全復習記録（最新1件/カード）を取得"""
    sb = get_supabase()
    res = sb.table("review_logs").select("*").eq("username", username).execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    if df.empty:
        return df
    df["reviewed_at"] = pd.to_datetime(df["reviewed_at"])
    df = df.sort_values("reviewed_at").groupby("flashcard_id").last().reset_index()
    return df


def compute_learning_streak(username: str) -> int:
    try:
        sb = get_supabase()
        res = (
            sb.table("review_logs")
            .select("reviewed_at")
            .eq("username", username)
            .execute()
        )
    except Exception:
        return 0
    if not res.data:
        return 0
    dates_with_activity = {
        pd.to_datetime(r["reviewed_at"]).date() for r in res.data
    }
    d = date.today()
    streak = 0
    while d in dates_with_activity:
        streak += 1
        d -= timedelta(days=1)
    return streak


def count_correct_once_in_set(username: str, set_id) -> int:
    cards = load_flashcards_by_set(set_id)
    if not cards:
        return 0
    card_ids = [c["id"] for c in cards]
    try:
        sb = get_supabase()
        res = (
            sb.table("review_logs")
            .select("flashcard_id, quality")
            .eq("username", username)
            .in_("flashcard_id", card_ids)
            .execute()
        )
    except Exception:
        return 0
    if not res.data:
        return 0
    ok = set()
    for row in res.data:
        if row.get("quality", 0) >= 3:
            ok.add(row["flashcard_id"])
    return len(ok)


def count_new_and_due_for_set(username: str, set_id) -> Tuple[int, int]:
    cards = load_flashcards_by_set(set_id)
    if not cards:
        return 0, 0
    card_ids = [c["id"] for c in cards]
    card_id_set = set(card_ids)
    try:
        sb = get_supabase()
        res = (
            sb.table("review_logs")
            .select("*")
            .eq("username", username)
            .in_("flashcard_id", card_ids)
            .execute()
        )
    except Exception:
        return 0, 0

    if not res.data:
        return len(card_ids), 0

    df = pd.DataFrame(res.data)
    df["reviewed_at"] = pd.to_datetime(df["reviewed_at"])
    df = df.sort_values("reviewed_at").groupby("flashcard_id").last().reset_index()

    learned = set(df["flashcard_id"].tolist())
    new_count = len([cid for cid in card_ids if cid not in learned])

    today_str = date.today().isoformat()
    due_count = 0
    for _, row in df.iterrows():
        if row["flashcard_id"] not in card_id_set:
            continue
        nrd = str(row["next_review_date"])
        if nrd <= today_str:
            due_count += 1

    return new_count, due_count


def load_due_cards(username: str, set_id) -> List[dict]:
    cards = load_flashcards_by_set(set_id)
    if not cards:
        return []
    id_to_row = {c["id"]: c for c in cards}
    card_ids = set(id_to_row.keys())

    try:
        sb = get_supabase()
        res = (
            sb.table("review_logs")
            .select("*")
            .eq("username", username)
            .in_("flashcard_id", list(card_ids))
            .execute()
        )
    except Exception:
        return []

    if not res.data:
        new_ids = list(card_ids)
        random.shuffle(new_ids)
        new_pick = new_ids[:10]
        combined = new_pick
        random.shuffle(combined)
        return [id_to_row[i] for i in combined if i in id_to_row]

    df = pd.DataFrame(res.data)
    df["reviewed_at"] = pd.to_datetime(df["reviewed_at"])
    df = df.sort_values("reviewed_at").groupby("flashcard_id").last().reset_index()

    reviewed_ids = set(df["flashcard_id"].tolist())
    new_ids = [cid for cid in card_ids if cid not in reviewed_ids]
    random.shuffle(new_ids)
    new_pick = new_ids[:10]

    today_str = date.today().isoformat()
    sub = df[df["flashcard_id"].isin(card_ids)]
    due_ids = sub[sub["next_review_date"].astype(str) <= today_str][
        "flashcard_id"
    ].tolist()

    combined = new_pick + due_ids
    random.shuffle(combined)
    return [id_to_row[i] for i in combined if i in id_to_row]


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
# 画面
# ─────────────────────────────
def show_home(username: str):
    st.markdown(
        """
<style>
.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; font-size: 1.2rem;
    border-radius: 12px; padding: 0.6rem 1rem; border: none;
}
.badge-red {
    background:#ff4b4b; color:white;
    border-radius:20px; padding:4px 12px;
    font-weight:bold; display:inline-block; margin:4px;
}
.badge-yellow {
    background:#ffa500; color:white;
    border-radius:20px; padding:4px 12px;
    font-weight:bold; display:inline-block; margin:4px;
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.success(
        f"🎉 こんにちは、{username}さん！今日もいっしょに覚えよう！"
    )
    streak = compute_learning_streak(username)
    if streak >= 1:
        st.info(f"🔥 {streak}日連続学習中！すごい！")
    else:
        st.info("📖 さあ、今日から始めよう！")

    st.markdown("---")

    sets_list = load_flashcard_sets()
    if not sets_list:
        st.warning("教材がまだ登録されていません")
        if st.button("🚪 ログアウト"):
            st.session_state["flash_user"] = ""
            st.rerun()
        return

    set_name_map = {row["id"]: str(row["set_name"]) for row in sets_list}
    set_ids = [row["id"] for row in sets_list]

    cur = st.session_state.get("selected_set_id")
    default_i = 0
    if cur in set_ids:
        default_i = set_ids.index(cur)

    sel_id = st.selectbox(
        "📚 教材を選ぶ",
        options=set_ids,
        index=default_i,
        format_func=lambda x: set_name_map[x],
    )
    st.session_state["selected_set_id"] = sel_id

    meta = next((r for r in sets_list if r["id"] == sel_id), None)
    if meta:
        if meta.get("description"):
            st.write(meta["description"])
        st.caption(
            f"カテゴリ: {meta.get('category', '')}　／　グレード: {meta.get('grade', '')}"
        )

    cards = load_flashcards_by_set(sel_id)
    if not cards:
        st.warning("この教材にはまだ単語が登録されていません。")
    else:
        pr_vals = []
        for c in cards:
            if c.get("page_range") is not None:
                try:
                    pr_vals.append(float(c["page_range"]))
                except (TypeError, ValueError):
                    pass
        if pr_vals:
            pmin, pmax = int(min(pr_vals)), int(max(pr_vals))
            st.markdown(f"📖 **p.{pmin} 〜 p.{pmax}**")
        else:
            st.caption("ページ範囲のデータがありません")

        in_vals = []
        for c in cards:
            if c.get("item_no") is not None:
                try:
                    in_vals.append(float(c["item_no"]))
                except (TypeError, ValueError):
                    pass
        if in_vals:
            imin, imax = int(min(in_vals)), int(max(in_vals))
            st.markdown(f"**No.{imin} 〜 No.{imax}**")
        else:
            st.caption("番号（item_no）のデータがありません")

        total = len(cards)
        correct = count_correct_once_in_set(username, sel_id)
        prog = (correct / total) if total else 0.0
        st.progress(prog)
        st.caption(f"✅ {correct} / {total} 枚クリア")

    st.markdown("---")

    new_count, due_count = count_new_and_due_for_set(username, sel_id)
    st.markdown(
        f'<span class="badge-red">🆕 新しい単語 {new_count}枚</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="badge-yellow">🔁 復習が必要 {due_count}枚</span>',
        unsafe_allow_html=True,
    )

    total_today = new_count + due_count
    if total_today == 0:
        st.success("🎉 今日の分は全部終わった！また明日！")
    else:
        if st.button(
            "✨ 今日の学習をはじめる！",
            type="primary",
            use_container_width=True,
        ):
            queue = load_due_cards(username, sel_id)
            if not queue:
                st.warning(
                    "学習カードを読み込めませんでした。しばらくしてからもう一度お試しください。"
                )
            else:
                st.session_state["flash_queue"] = queue
                st.session_state["flash_index"] = 0
                st.session_state["flash_show_answer"] = False
                st.session_state["flash_session_results"] = []
                st.session_state["mode"] = "study"
                st.rerun()

    if st.button("🚪 ログアウト"):
        st.session_state["flash_user"] = ""
        st.rerun()


def show_study(username: str):
    queue = st.session_state["flash_queue"]
    idx = st.session_state["flash_index"]

    if idx >= len(queue):
        st.session_state["mode"] = "result"
        st.rerun()

    card = queue[idx]
    total = len(queue)

    st.progress((idx) / total, text=f"{idx + 1} / {total} 枚目")
    st.markdown("---")

    st.markdown(f"## 🔤 {card['word']}")
    if card.get("reading"):
        st.caption(f"読み：{card['reading']}")

    if not st.session_state["flash_show_answer"]:
        if st.button("✅ 意味を見る", type="primary", use_container_width=True):
            st.session_state["flash_show_answer"] = True
            st.rerun()
    else:
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


def show_result():
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
        st.session_state["mode"] = "home"
        st.session_state["flash_session_results"] = []
        st.rerun()


# ─────────────────────────────
# セッション初期化
# ─────────────────────────────
if "flash_user" not in st.session_state:
    st.session_state["flash_user"] = ""
if "mode" not in st.session_state:
    st.session_state["mode"] = "home"
if "flash_queue" not in st.session_state:
    st.session_state["flash_queue"] = []
if "flash_index" not in st.session_state:
    st.session_state["flash_index"] = 0
if "flash_show_answer" not in st.session_state:
    st.session_state["flash_show_answer"] = False
if "flash_session_results" not in st.session_state:
    st.session_state["flash_session_results"] = []
if "selected_set_id" not in st.session_state:
    st.session_state["selected_set_id"] = None

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
# ルーティング
# ─────────────────────────────
if st.session_state["mode"] == "home":
    show_home(username)
elif st.session_state["mode"] == "study":
    show_study(username)
elif st.session_state["mode"] == "result":
    show_result()
