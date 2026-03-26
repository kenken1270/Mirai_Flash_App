# flash_app.py — 未来塾 単語暗記アプリ（SM-2忘却曲線）改訂版
import streamlit as st
import random
from supabase import create_client
from datetime import date, timedelta

st.set_page_config(page_title="📖 単語暗記 | 未来塾", layout="centered")

# ─────────────────────────────
# 接続
# ─────────────────────────────
@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# ─────────────────────────────
# SM-2 アルゴリズム（変更なし）
# ─────────────────────────────
def sm2_update(quality, ease_factor, interval, repetitions):
    if quality < 3:
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
# save_review（変更なし）
# ─────────────────────────────
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
# データ取得関数
# ─────────────────────────────
@st.cache_data(ttl=60)
def load_users():
    try:
        sb = get_supabase()
        res = sb.table("users").select("username").execute()
        return [row["username"] for row in res.data] if res.data else []
    except:
        return []

@st.cache_data(ttl=30)
def load_flashcard_sets():
    try:
        sb = get_supabase()
        res = sb.table("flashcard_sets").select("id,set_name,category,grade,description").execute()
        return res.data if res.data else []
    except:
        return []

@st.cache_data(ttl=30)
def load_flashcards_by_set(set_id):
    try:
        sb = get_supabase()
        res = sb.table("flashcards").select("*").eq("set_id", set_id).execute()
        return res.data if res.data else []
    except:
        return []

@st.cache_data(ttl=30)
def load_review_logs(username):
    try:
        sb = get_supabase()
        res = sb.table("review_logs").select("*").eq("username", username).execute()
        return res.data if res.data else []
    except:
        return []

def compute_learning_streak(username):
    logs = load_review_logs(username)
    if not logs:
        return 0
    reviewed_dates = set()
    for row in logs:
        try:
            d = row["reviewed_at"][:10]
            reviewed_dates.add(d)
        except:
            pass
    streak = 0
    check = date.today()
    while check.isoformat() in reviewed_dates:
        streak += 1
        check -= timedelta(days=1)
    return streak

def count_correct_once_in_set(username, set_id):
    cards = load_flashcards_by_set(set_id)
    if not cards:
        return 0
    card_ids = {c["id"] for c in cards}
    logs = load_review_logs(username)
    correct_ids = {
        row["flashcard_id"]
        for row in logs
        if row["flashcard_id"] in card_ids and row.get("quality", 0) >= 3
    }
    return len(correct_ids)

def count_new_and_due_for_set(username, set_id):
    cards = load_flashcards_by_set(set_id)
    if not cards:
        return 0, 0
    card_ids = [c["id"] for c in cards]
    logs = load_review_logs(username)

    # 各カードの最新ログを取得
    latest = {}
    for row in logs:
        cid = row["flashcard_id"]
        if cid not in latest:
            latest[cid] = row
        else:
            if row["reviewed_at"] > latest[cid]["reviewed_at"]:
                latest[cid] = row

    today_str = date.today().isoformat()
    new_count = sum(1 for cid in card_ids if cid not in latest)
    due_count = sum(
        1 for cid in card_ids
        if cid in latest and latest[cid].get("next_review_date", "9999") <= today_str
    )
    return new_count, due_count

def load_due_cards(username, set_id):
    cards = load_flashcards_by_set(set_id)
    if not cards:
        return []
    logs = load_review_logs(username)

    latest = {}
    for row in logs:
        cid = row["flashcard_id"]
        if cid not in latest or row["reviewed_at"] > latest[cid]["reviewed_at"]:
            latest[cid] = row

    today_str = date.today().isoformat()
    new_cards = [c for c in cards if c["id"] not in latest]
    random.shuffle(new_cards)
    new_cards = new_cards[:10]

    due_cards = [
        c for c in cards
        if c["id"] in latest and latest[c["id"]].get("next_review_date", "9999") <= today_str
    ]

    combined = new_cards + due_cards
    random.shuffle(combined)
    return combined

# ─────────────────────────────
# セッション初期化
# ─────────────────────────────
for key, default in [
    ("flash_user", ""),
    ("flash_mode", "home"),
    ("flash_queue", []),
    ("flash_index", 0),
    ("flash_show_answer", False),
    ("flash_session_results", []),
    ("selected_set_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────
# ログイン画面
# ─────────────────────────────
if not st.session_state["flash_user"]:
    st.title("📖 単語暗記アプリ | 未来塾")
    user_list = load_users()
    if not user_list:
        st.warning("ユーザーが登録されていません。管理者に連絡してください。")
        st.stop()
    selected = st.selectbox("ユーザーを選んでください", ["--- 選んでください ---"] + user_list)
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
def show_home(username):
    st.markdown("""
    <style>
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; font-size: 1.2rem;
        border-radius: 12px; padding: 0.6rem 1rem; border: none;
    }
    .badge-red {
        background:#ff4b4b; color:white;
        border-radius:20px; padding:4px 14px;
        font-weight:bold; display:inline-block; margin:4px;
        font-size: 1rem;
    }
    .badge-yellow {
        background:#ffa500; color:white;
        border-radius:20px; padding:4px 14px;
        font-weight:bold; display:inline-block; margin:4px;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ゾーン①: ウェルカム
    st.success(f"🎉 こんにちは、{username}さん！今日もいっしょに覚えよう！")
    streak = compute_learning_streak(username)
    if streak >= 1:
        st.info(f"🔥 {streak}日連続学習中！すごい！")
    else:
        st.info("📖 さあ、今日から始めよう！")

    st.markdown("---")

    # ゾーン②: 教材選択
    st.markdown("### 📚 教材を選ぶ")
    sets = load_flashcard_sets()
    if not sets:
        st.warning("教材がまだ登録されていません。管理者に連絡してください。")
        if st.button("🚪 ログアウト"):
            st.session_state["flash_user"] = ""
            st.rerun()
        return

    set_id_list = [s["id"] for s in sets]
    set_name_map = {s["id"]: s["set_name"] for s in sets}
    set_info_map = {s["id"]: s for s in sets}

    # 前回選択を維持
    prev = st.session_state.get("selected_set_id")
    default_idx = set_id_list.index(prev) if prev in set_id_list else 0

    selected_set_id = st.selectbox(
        "教材",
        options=set_id_list,
        index=default_idx,
        format_func=lambda x: set_name_map[x]
    )
    st.session_state["selected_set_id"] = selected_set_id

    info = set_info_map[selected_set_id]
    st.caption(f"📂 {info.get('category','')}  ／  {info.get('grade','')}  ／  {info.get('description','')}")

    cards = load_flashcards_by_set(selected_set_id)
    total = len(cards)

    if total == 0:
        st.warning("この教材にはまだ単語が登録されていません。")
    else:
        # ページ範囲・item番号
        page_ranges = [c.get("page_range") for c in cards if c.get("page_range")]
        item_nos = [c.get("item_no") for c in cards if c.get("item_no") is not None]
        if page_ranges:
            st.markdown(f"📖 **ページ範囲:** {min(page_ranges)} 〜 {max(page_ranges)}")
        if item_nos:
            st.markdown(f"🔢 **No.{min(item_nos)} 〜 No.{max(item_nos)}**")

        # 進捗バー
        correct = count_correct_once_in_set(username, selected_set_id)
        progress_val = correct / total if total > 0 else 0
        st.progress(progress_val)
        st.caption(f"✅ {correct} / {total} 枚クリア（{int(progress_val*100)}%）")

    st.markdown("---")

    # ゾーン③: アクション
    st.markdown("### 📝 今日やること")
    new_count, due_count = count_new_and_due_for_set(username, selected_set_id)
    st.markdown(
        f'<span class="badge-red">🆕 新しい単語 {new_count}枚</span>'
        f'<span class="badge-yellow">🔁 復習が必要 {due_count}枚</span>',
        unsafe_allow_html=True
    )
    st.markdown("")

    total_today = new_count + due_count
    if total_today == 0:
        st.success("🎉 今日の分は全部終わった！また明日！")
    else:
        if st.button("✨ 今日の学習をはじめる！", type="primary", use_container_width=True):
            queue = load_due_cards(username, selected_set_id)
            st.session_state["flash_queue"] = queue
            st.session_state["flash_index"] = 0
            st.session_state["flash_show_answer"] = False
            st.session_state["flash_session_results"] = []
            st.session_state["flash_mode"] = "study"
            st.rerun()

    st.markdown("---")
    if st.button("🚪 ログアウト"):
        st.session_state["flash_user"] = ""
        st.rerun()

# ─────────────────────────────
# 学習画面（変更なし）
# ─────────────────────────────
def show_study(username):
    queue = st.session_state["flash_queue"]
    idx = st.session_state["flash_index"]

    if idx >= len(queue):
        st.session_state["flash_mode"] = "result"
        st.rerun()

    card = queue[idx]
    total = len(queue)

    st.progress(idx / total, text=f"{idx + 1} / {total} 枚目")
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
            logs = load_review_logs(username)
            cid = card["id"]
            latest = {}
            for row in logs:
                rid = row["flashcard_id"]
                if rid not in latest or row["reviewed_at"] > latest[rid]["reviewed_at"]:
                    latest[rid] = row
            if cid in latest:
                row = latest[cid]
                ef = float(row["ease_factor"])
                iv = int(row["interval_days"])
                rp = int(row["repetitions"])
            else:
                ef, iv, rp = 2.5, 1, 0
            new_ef, new_iv, new_rp, next_date = sm2_update(q, ef, iv, rp)
            save_review(username, cid, q, new_ef, new_iv, new_rp, next_date)
            st.session_state["flash_session_results"].append({
                "word": card["word"], "quality": q, "next_review": next_date
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
# 結果画面（変更なし）
# ─────────────────────────────
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
        st.session_state["flash_mode"] = "home"
        st.session_state["flash_session_results"] = []
        st.rerun()

# ─────────────────────────────
# 画面ルーティング
# ─────────────────────────────
mode = st.session_state["flash_mode"]
if mode == "home":
    show_home(username)
elif mode == "study":
    show_study(username)
elif mode == "result":
    show_result()
