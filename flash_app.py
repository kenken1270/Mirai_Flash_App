# flash_app.py — 未来塾 単語暗記アプリ（SM-2忘却曲線）改訂版
import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

        # ── 追加学習メニュー ────────────────────
        st.markdown("#### 🌟 もっとやりたい人はここから！")

        # 称号表示
        total_xp = calc_total_xp(username)
        level = calc_level(total_xp)
        titles = {
            1: ("🌱", "たんご の たまご"),
            2: ("📖", "たんご の たまご+"),
            3: ("⚡", "たんご の せんし"),
            4: ("🔥", "たんご の たつじん"),
            5: ("💎", "たんご の えいゆう"),
            6: ("👑", "たんご の おう"),
            7: ("🌟", "たんご の でんせつ"),
        }
        icon, title = titles.get(min(level, 7), ("🌟", "たんご の でんせつ"))
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);
            border-radius:16px; padding:14px 20px; color:white;
            display:flex; align-items:center; gap:12px; margin-bottom:16px;">
            <span style="font-size:2rem;">{icon}</span>
            <div>
                <div style="font-size:0.8rem; opacity:0.85;">現在の称号</div>
                <div style="font-size:1.2rem; font-weight:bold;">
                    Lv.{level} {title}
                </div>
                <div style="font-size:0.78rem; opacity:0.75;">
                    累計 {total_xp} XP
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3つの追加学習ボタン
        ex1, ex2, ex3 = st.columns(3)

        with ex1:
            st.markdown("""
            <div style="background:#ff6b6b; border-radius:14px;
                padding:14px 8px; text-align:center; color:white;
                font-weight:bold; margin-bottom:6px;">
                <div style="font-size:1.4rem;">🔁</div>
                <div style="font-size:0.9rem;">苦手だけ</div>
                <div style="font-size:0.75rem; opacity:0.9;">
                    復習する
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("苦手を復習", key="extra_weak", use_container_width=True):
                cards = load_flashcards_by_set(selected_set_id)
                logs = load_review_logs(username)
                # quality < 4 のカードIDを抽出（最新ログ基準）
                latest = {}
                for row in logs:
                    cid = row["flashcard_id"]
                    if cid not in latest or row["reviewed_at"] > latest[cid]["reviewed_at"]:
                        latest[cid] = row
                weak_ids = {
                    cid for cid, row in latest.items()
                    if row.get("quality", 5) < 4
                }
                weak_cards = [c for c in cards if c["id"] in weak_ids]
                if weak_cards:
                    random.shuffle(weak_cards)
                    st.session_state["flash_queue"] = weak_cards
                    st.session_state["flash_index"] = 0
                    st.session_state["flash_show_answer"] = False
                    st.session_state["flash_session_results"] = []
                    st.session_state["flash_mode"] = "study"
                    st.rerun()
                else:
                    st.success("🎉 苦手な単語はありません！完璧です！")

        with ex2:
            st.markdown("""
            <div style="background:#667eea; border-radius:14px;
                padding:14px 8px; text-align:center; color:white;
                font-weight:bold; margin-bottom:6px;">
                <div style="font-size:1.4rem;">🚀</div>
                <div style="font-size:0.9rem;">先取り</div>
                <div style="font-size:0.75rem; opacity:0.9;">
                    新しい単語へ
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("先取りする", key="extra_new", use_container_width=True):
                cards = load_flashcards_by_set(selected_set_id)
                logs = load_review_logs(username)
                learned_ids = {row["flashcard_id"] for row in logs}
                new_cards = [c for c in cards if c["id"] not in learned_ids]
                if new_cards:
                    random.shuffle(new_cards)
                    st.session_state["flash_queue"] = new_cards[:10]
                    st.session_state["flash_index"] = 0
                    st.session_state["flash_show_answer"] = False
                    st.session_state["flash_session_results"] = []
                    st.session_state["flash_mode"] = "study"
                    st.rerun()
                else:
                    st.success("🏆 この教材は全単語制覇です！すごい！")

        with ex3:
            st.markdown("""
            <div style="background:#00b09b; border-radius:14px;
                padding:14px 8px; text-align:center; color:white;
                font-weight:bold; margin-bottom:6px;">
                <div style="font-size:1.4rem;">🎯</div>
                <div style="font-size:0.9rem;">全部復習</div>
                <div style="font-size:0.75rem; opacity:0.9;">
                    全単語を通す
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("全部やる", key="extra_all", use_container_width=True):
                cards = load_flashcards_by_set(selected_set_id)
                if cards:
                    random.shuffle(cards)
                    st.session_state["flash_queue"] = cards
                    st.session_state["flash_index"] = 0
                    st.session_state["flash_show_answer"] = False
                    st.session_state["flash_session_results"] = []
                    st.session_state["flash_mode"] = "study"
                    st.rerun()

        # デイリーミッション（簡易版）
        st.markdown("---")
        streak = compute_learning_streak(username)
        if streak >= 7:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#f7971e,#ffd200);
                border-radius:14px; padding:12px 16px; color:#333;
                font-weight:bold; text-align:center;">
                🌟 7日連続達成！XP×2ボーナス獲得中！
            </div>
            """, unsafe_allow_html=True)
        elif streak >= 3:
            st.info(f"🔥 {streak}日連続！あと{7-streak}日で7日連続ボーナス！")
        else:
            st.caption(f"💡 毎日続けると7日連続ボーナスXP×2が解放されます！")
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
# 学習画面
# ─────────────────────────────
def show_study(username):
    queue = st.session_state["flash_queue"]
    idx = st.session_state["flash_index"]

    if idx >= len(queue):
        st.session_state["flash_mode"] = "result"
        st.rerun()

    card = queue[idx]
    total = len(queue)

    st.markdown("""
<style>
.card-front {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 40px 24px;
    text-align: center;
    color: white;
    margin: 16px 0;
    box-shadow: 0 8px 24px rgba(102,126,234,0.4);
}
.card-word {
    font-size: 2.4rem;
    font-weight: bold;
    letter-spacing: 2px;
    margin-bottom: 8px;
}
.card-reading {
    font-size: 1.1rem;
    opacity: 0.85;
}
.card-back {
    background: white;
    border: 3px solid #667eea;
    border-radius: 20px;
    padding: 32px 24px;
    text-align: center;
    margin: 16px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.card-meaning {
    font-size: 1.8rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 12px;
}
.card-example {
    font-size: 1rem;
    color: #666;
    font-style: italic;
    border-top: 1px solid #eee;
    padding-top: 12px;
    margin-top: 12px;
}
.progress-bar-label {
    font-size: 0.9rem;
    color: #888;
    text-align: right;
    margin-bottom: 4px;
}
.rating-bar {
    display: flex;
    gap: 8px;
    margin: 16px 0;
}
.rating-btn-0 {
    flex: 1;
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
    color: white; border: none; border-radius: 16px;
    padding: 16px 8px; cursor: pointer;
    text-align: center; font-weight: bold;
    box-shadow: 0 4px 12px rgba(255,75,75,0.3);
}
.rating-btn-3 {
    flex: 1;
    background: linear-gradient(135deg, #ffa500, #ffbe00);
    color: white; border: none; border-radius: 16px;
    padding: 16px 8px; cursor: pointer;
    text-align: center; font-weight: bold;
    box-shadow: 0 4px 12px rgba(255,165,0,0.3);
}
.rating-btn-4 {
    flex: 1;
    background: linear-gradient(135deg, #00b09b, #00d4aa);
    color: white; border: none; border-radius: 16px;
    padding: 16px 8px; cursor: pointer;
    text-align: center; font-weight: bold;
    box-shadow: 0 4px 12px rgba(0,176,155,0.3);
}
.rating-btn-5 {
    flex: 1;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none; border-radius: 16px;
    padding: 16px 8px; cursor: pointer;
    text-align: center; font-weight: bold;
    box-shadow: 0 4px 12px rgba(102,126,234,0.4);
}
.rating-label {
    font-size: 0.78rem;
    margin-top: 6px;
    opacity: 0.92;
    line-height: 1.3;
}
.rating-icon {
    font-size: 1.8rem;
    margin-bottom: 4px;
}
.rate-card button {
    height: auto !important;
    min-height: 110px !important;
    border-radius: 20px !important;
    border: none !important;
    font-size: 1rem !important;
    font-weight: bold !important;
    white-space: pre-wrap !important;
    line-height: 1.5 !important;
    padding: 12px 6px !important;
    transition: transform 0.1s ease, box-shadow 0.1s ease !important;
}
.rate-card button:active {
    transform: scale(0.96) !important;
}
/* 各ボタンの色 */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important;
    box-shadow: 0 6px 16px rgba(255,75,75,0.35) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
    background: linear-gradient(135deg, #ffa500, #ffbe00) !important;
    color: white !important;
    box-shadow: 0 6px 16px rgba(255,165,0,0.35) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
    background: linear-gradient(135deg, #00b09b, #00d4aa) !important;
    color: white !important;
    box-shadow: 0 6px 16px rgba(0,176,155,0.35) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    box-shadow: 0 6px 16px rgba(102,126,234,0.4) !important;
}
</style>
""", unsafe_allow_html=True)

    col_prog, col_home = st.columns([4, 1])
    with col_prog:
        st.markdown(
            f'<div class="progress-bar-label">{idx + 1} / {total} 枚目</div>',
            unsafe_allow_html=True,
        )
        st.progress(idx / total)
    with col_home:
        if st.button("🏠", help="ホームへ戻る", use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.rerun()

    category = card.get("category", "")
    is_japanese = category in ["JLPT", "日本語", "国語"]

    if not st.session_state["flash_show_answer"]:
        if is_japanese:
            reading = card.get("reading", "")
            reading_html = (
                f'<div class="card-reading">読み：{reading}</div>'
                if reading
                else ""
            )
            st.markdown(
                f"""
<div class="card-front">
    <div class="card-word">{card['word']}</div>
    {reading_html}
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
<div class="card-front">
    <div class="card-word">{card['word']}</div>
</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='text-align:center; color:#888; "
            "font-size:0.9rem; margin:8px 0;'>"
            "💭 意味を頭に思い浮かべてから押してね</div>",
            unsafe_allow_html=True,
        )
        if st.button("👀 答えを見る", type="primary", use_container_width=True):
            st.session_state["flash_show_answer"] = True
            st.rerun()
    else:
        if is_japanese:
            example = card.get("example", "")
            example_html = (
                f'<div class="card-example">📝 例文: {example}</div>'
                if example
                else ""
            )
            st.markdown(
                f"""
<div class="card-back">
    <div class="card-meaning">💡 {card['meaning']}</div>
    {example_html}
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            reading = card.get("reading", "")
            reading_html = (
                f'<div style="font-size:1rem; color:#667eea; margin-top:8px;">'
                f"🔊 読み：{reading}</div>"
            ) if reading else ""

            example = card.get("example", "")
            example_html = (
                f'<div class="card-example">📝 例文: {example}</div>'
                if example
                else ""
            )

            st.markdown(
                f"""
<div class="card-back">
    <div class="card-meaning">💡 {card['meaning']}</div>
    {reading_html}
    {example_html}
</div>
""",
                unsafe_allow_html=True,
            )

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

        st.markdown("---")
        st.markdown("### どのくらい覚えていた？")

        # グラデーション凡例バー
        st.markdown("""
<div style="
    height: 12px; border-radius: 8px;
    background: linear-gradient(to right, #ff4b4b, #ffa500, #00b09b, #667eea);
    margin: 4px 0 2px 0;
"></div>
<div style="display:flex; justify-content:space-between;
            font-size:0.75rem; color:#888; margin-bottom:16px;">
    <span>❌ 全然ダメ</span><span>⭐ バッチリ！</span>
</div>
""", unsafe_allow_html=True)

        # ワンタップカードボタン（1列4つ）
        c0, c1, c2, c3 = st.columns(4)

        with c0:
            if st.button(
                "❌\n全然ダメ\n\n答えが\n出てこなかった",
                key="q0", use_container_width=True
            ):
                record_quality(0)

        with c1:
            if st.button(
                "🔶\nうっすら\n\n思い出すのに\n時間がかかった",
                key="q3", use_container_width=True
            ):
                record_quality(3)

        with c2:
            if st.button(
                "🟢\nだいたい\n\nすぐ出たが\n少し不安だった",
                key="q4", use_container_width=True
            ):
                record_quality(4)

        with c3:
            if st.button(
                "⭐\nバッチリ！\n\n一瞬で\n完全に自信あり",
                key="q5", use_container_width=True
            ):
                record_quality(5)

        # 次回復習の目安（ボタン下）
        st.markdown("""
<div style="display:flex; justify-content:space-between;
            font-size:0.70rem; color:#bbb; margin-top:6px;">
    <span style="flex:1;text-align:center;">次回: 明日</span>
    <span style="flex:1;text-align:center;">次回: 6日後</span>
    <span style="flex:1;text-align:center;">次回: 数週間後</span>
    <span style="flex:1;text-align:center;">次回: 1ヶ月以上</span>
</div>
""", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("⏸️ いったん中断してホームへ戻る", use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.rerun()

# ─────────────────────────────
# 結果画面（XP・レベル）
# ─────────────────────────────
def calc_session_xp(results):
    """セッションの獲得XPを計算"""
    xp = 0
    for r in results:
        q = r["quality"]
        if q >= 5:
            xp += 10
        elif q >= 4:
            xp += 6
        elif q >= 3:
            xp += 3
        else:
            xp += 1
    return xp


def calc_total_xp(username):
    """累計XPをreview_logsから計算"""
    logs = load_review_logs(username)
    xp = 0
    for row in logs:
        q = row.get("quality", 0)
        if q >= 5:
            xp += 10
        elif q >= 4:
            xp += 6
        elif q >= 3:
            xp += 3
        else:
            xp += 1
    return xp


def calc_level(total_xp):
    """XPからレベルを計算（RPG式成長曲線）"""
    import math

    return int(math.sqrt(total_xp / 10)) + 1


def calc_level_progress(total_xp):
    """現レベル内の進捗率(0.0〜1.0)を返す"""
    import math

    level = calc_level(total_xp)
    xp_current_level = ((level - 1) ** 2) * 10
    xp_next_level = (level ** 2) * 10
    if xp_next_level == xp_current_level:
        return 1.0
    return (total_xp - xp_current_level) / (xp_next_level - xp_current_level)


def load_daily_stats(username):
    """
    過去30日分の日別学習統計を返す
    戻り値: list[dict] = [
        {"date": "2026-03-01", "xp": 45, "cards": 10, "accuracy": 80.0},
        ...
    ]
    """
    logs = load_review_logs(username)
    if not logs:
        return []

    from collections import defaultdict
    daily = defaultdict(lambda: {"xp": 0, "total": 0, "correct": 0})

    for row in logs:
        d = row.get("reviewed_at", "")[:10]
        q = row.get("quality", 0)
        if q >= 5:
            xp = 10
        elif q >= 4:
            xp = 6
        elif q >= 3:
            xp = 3
        else:
            xp = 1
        daily[d]["xp"] += xp
        daily[d]["total"] += 1
        if q >= 3:
            daily[d]["correct"] += 1

    # 過去30日分に絞る & ソート
    from datetime import date, timedelta
    today = date.today()
    result = []
    for i in range(29, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        stats = daily.get(d, {"xp": 0, "total": 0, "correct": 0})
        accuracy = (
            stats["correct"] / stats["total"] * 100
            if stats["total"] > 0 else None
        )
        result.append({
            "date": d,
            "xp": stats["xp"],
            "cards": stats["total"],
            "accuracy": accuracy,
        })
    return result


def load_cumulative_xp(username):
    """
    過去30日分の累計XP推移を返す
    戻り値: list[dict] = [{"date": "...", "cumulative_xp": 120}, ...]
    """
    daily = load_daily_stats(username)
    # 全履歴の累計XPの開始値を計算
    all_logs = load_review_logs(username)
    from datetime import date, timedelta
    cutoff = (date.today() - timedelta(days=29)).isoformat()

    # cutoff以前のXP合計
    base_xp = 0
    for row in all_logs:
        d = row.get("reviewed_at", "")[:10]
        if d < cutoff:
            q = row.get("quality", 0)
            if q >= 5: base_xp += 10
            elif q >= 4: base_xp += 6
            elif q >= 3: base_xp += 3
            else: base_xp += 1

    cumulative = []
    running = base_xp
    for day in daily:
        running += day["xp"]
        cumulative.append({"date": day["date"], "cumulative_xp": running})
    return cumulative


def show_result():
    results = st.session_state["flash_session_results"]
    username = st.session_state["flash_user"]

    perfect = [r for r in results if r["quality"] >= 5]
    good = [r for r in results if r["quality"] == 4]
    ok = [r for r in results if r["quality"] == 3]
    ng = [r for r in results if r["quality"] < 3]

    session_xp = calc_session_xp(results)
    total_xp = calc_total_xp(username)
    level = calc_level(total_xp)
    lv_progress = calc_level_progress(total_xp)
    accuracy = (
        len([r for r in results if r["quality"] >= 3]) / len(results) * 100
        if results
        else 0
    )

    # ── CSS ──────────────────────────────────
    st.markdown(
        """
    <style>
    .result-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 24px; padding: 32px 24px;
        text-align: center; color: white; margin-bottom: 20px;
    }
    .result-title { font-size: 2rem; font-weight: bold; margin-bottom: 4px; }
    .result-sub   { font-size: 1rem; opacity: 0.85; }
    .xp-badge {
        display: inline-block;
        background: rgba(255,255,255,0.25);
        border-radius: 20px; padding: 6px 20px;
        font-size: 1.4rem; font-weight: bold;
        margin-top: 12px;
    }
    .stat-card {
        border-radius: 16px; padding: 16px 10px;
        text-align: center; color: white;
        font-weight: bold;
    }
    .word-pill {
        display: inline-block;
        border-radius: 20px; padding: 4px 14px;
        margin: 4px; font-size: 0.9rem; font-weight: bold;
        color: white;
    }
    .level-bar-wrap {
        background: #f0f0f0; border-radius: 10px;
        overflow: hidden; height: 14px; margin: 6px 0;
    }
    .level-bar-fill {
        height: 100%; border-radius: 10px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 1s ease;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # ── 花火演出 ─────────────────────────────
    if accuracy >= 80:
        st.balloons()

    # ── ヒーローバナー ────────────────────────
    if accuracy == 100:
        title_text = "🏆 パーフェクト！！"
        sub_text = "全問正解！完璧な学習でした！"
    elif accuracy >= 80:
        title_text = "🎉 素晴らしい！"
        sub_text = f"正解率 {accuracy:.0f}% — この調子で続けよう！"
    elif accuracy >= 50:
        title_text = "💪 よく頑張った！"
        sub_text = f"正解率 {accuracy:.0f}% — 復習で差をつけよう！"
    else:
        title_text = "📖 今日はここから！"
        sub_text = f"正解率 {accuracy:.0f}% — 繰り返せば必ず覚えられる！"

    st.markdown(
        f"""
    <div class="result-hero">
        <div class="result-title">{title_text}</div>
        <div class="result-sub">{sub_text}</div>
        <div class="xp-badge">⚡ +{session_xp} XP ゲット！</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── 4指標カード（1行）────────────────────
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "⭐ バッチリ", len(perfect), "#667eea"),
        (c2, "🟢 だいたい", len(good), "#00b09b"),
        (c3, "🔶 うっすら", len(ok), "#ffa500"),
        (c4, "❌ 要復習", len(ng), "#ff4b4b"),
    ]
    for col, label, count, color in stats:
        with col:
            st.markdown(
                f"""
            <div class="stat-card" style="background:{color};">
                <div style="font-size:1.5rem;">{count}枚</div>
                <div style="font-size:0.78rem; margin-top:4px;">{label}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── レベル・XPバー ───────────────────────
    st.markdown("---")
    st.markdown(f"### 🎮 Lv.{level} — 累計 {total_xp} XP")
    st.markdown(
        f"""
    <div class="level-bar-wrap">
        <div class="level-bar-fill" style="width:{int(lv_progress*100)}%;"></div>
    </div>
    <div style="font-size:0.78rem; color:#888; text-align:right;">
        次のレベルまで {int((1-lv_progress)*100)}%
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── 単語別結果（ピル表示）────────────────
    st.markdown("---")
    st.markdown("### 📋 今日の単語まとめ")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**✅ 覚えられた単語**")
        covered = perfect + good
        if covered:
            pills = " ".join(
                [
                    f'<span class="word-pill" style="background:#00b09b;">{r["word"]}</span>'
                    for r in covered
                ]
            )
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.caption("まだありません")

    with col_b:
        st.markdown("**🔁 次回また挑戦**")
        retry = ok + ng
        if retry:
            pills = " ".join(
                [
                    f'<span class="word-pill" style="background:#ffa500;">{r["word"]}</span>'
                    for r in ok
                ]
                + [
                    f'<span class="word-pill" style="background:#ff4b4b;">{r["word"]}</span>'
                    for r in ng
                ]
            )
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.caption("なし！完璧です 🎉")

    # ── 次回復習日の予告 ─────────────────────
    if ng:
        st.markdown("---")
        st.info(
            f"💡 **{len(ng)}枚**は明日また出てきます。大丈夫、繰り返すことで必ず覚えられます！"
        )

    # ── 成長グラフ ───────────────────────────
    st.markdown("---")
    st.markdown("### 📈 あなたの成長グラフ")

    daily_stats = load_daily_stats(username)
    cum_stats = load_cumulative_xp(username)

    # 学習があった日だけ抽出
    active_days = [d for d in daily_stats if d["cards"] > 0]

    if len(active_days) < 2:
        st.info("📊 グラフは2日以上学習すると表示されます！明日も来てね 🔥")
    else:
        tab1, tab2, tab3 = st.tabs(["⚡ XP推移", "📚 学習枚数", "🎯 正解率"])

        # ── Tab1: 累計XP折れ線グラフ ──────────
        with tab1:
            df_cum = pd.DataFrame(cum_stats)
            # 学習のある日だけマーカーを強調
            df_cum["has_activity"] = df_cum["date"].isin(
                [d["date"] for d in active_days]
            )
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df_cum["date"],
                y=df_cum["cumulative_xp"],
                mode="lines+markers",
                line=dict(color="#667eea", width=3),
                marker=dict(
                    size=[8 if h else 4 for h in df_cum["has_activity"]],
                    color=["#764ba2" if h else "#cccccc"
                           for h in df_cum["has_activity"]],
                ),
                fill="tozeroy",
                fillcolor="rgba(102,126,234,0.15)",
                name="累計XP",
                hovertemplate="%{x}<br>累計XP: %{y}<extra></extra>",
            ))
            fig1.update_layout(
                title="累計XPの推移（過去30日）",
                xaxis_title="日付",
                yaxis_title="累計XP",
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="sans-serif", size=12),
                margin=dict(l=40, r=20, t=40, b=40),
                hovermode="x unified",
            )
            st.plotly_chart(fig1, use_container_width=True)
            # 総合コメント
            total_active = len(active_days)
            st.caption(f"🔥 過去30日で **{total_active}日** 学習しました！")

        # ── Tab2: 日別学習枚数棒グラフ ────────
        with tab2:
            df_daily = pd.DataFrame(daily_stats)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_daily["date"],
                y=df_daily["cards"],
                marker_color=[
                    "#667eea" if c > 0 else "#eeeeee"
                    for c in df_daily["cards"]
                ],
                hovertemplate="%{x}<br>学習枚数: %{y}枚<extra></extra>",
                name="学習枚数",
            ))
            fig2.update_layout(
                title="日別 学習枚数（過去30日）",
                xaxis_title="日付",
                yaxis_title="枚数",
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="sans-serif", size=12),
                margin=dict(l=40, r=20, t=40, b=40),
            )
            st.plotly_chart(fig2, use_container_width=True)
            max_day = df_daily.loc[df_daily["cards"].idxmax()]
            if max_day["cards"] > 0:
                st.caption(
                    f"🏅 最多学習日: **{max_day['date']}** ({int(max_day['cards'])}枚)"
                )

        # ── Tab3: 日別正解率折れ線グラフ ──────
        with tab3:
            df_acc = pd.DataFrame([
                d for d in daily_stats
                if d["accuracy"] is not None
            ])
            if df_acc.empty:
                st.info("正解率データがありません")
            else:
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=df_acc["date"],
                    y=df_acc["accuracy"],
                    mode="lines+markers",
                    line=dict(color="#00b09b", width=3),
                    marker=dict(size=8, color="#00b09b"),
                    fill="tozeroy",
                    fillcolor="rgba(0,176,155,0.12)",
                    name="正解率",
                    hovertemplate="%{x}<br>正解率: %{y:.1f}%<extra></extra>",
                ))
                # 80%ラインを点線で追加
                fig3.add_hline(
                    y=80,
                    line_dash="dot",
                    line_color="#ffa500",
                    annotation_text="目標 80%",
                    annotation_position="bottom right",
                )
                fig3.update_layout(
                    title="日別 正解率（過去30日）",
                    xaxis_title="日付",
                    yaxis_title="正解率 (%)",
                    yaxis_range=[0, 105],
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="sans-serif", size=12),
                    margin=dict(l=40, r=20, t=40, b=40),
                )
                st.plotly_chart(fig3, use_container_width=True)
                avg_acc = df_acc["accuracy"].mean()
                st.caption(f"📊 過去30日の平均正解率: **{avg_acc:.1f}%**")

    # ── アクションボタン ─────────────────────
    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🏠 ホームへ戻る", type="primary", use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.session_state["flash_session_results"] = []
            st.rerun()
    with b2:
        if st.button("🔁 もう一度チャレンジ", use_container_width=True):
            ng_words = [r["word"] for r in ng + ok]
            selected_set_id = st.session_state.get("selected_set_id")
            if selected_set_id:
                all_cards = load_flashcards_by_set(selected_set_id)
                retry_queue = [c for c in all_cards if c["word"] in ng_words]
                if retry_queue:
                    random.shuffle(retry_queue)
                    st.session_state["flash_queue"] = retry_queue
                    st.session_state["flash_index"] = 0
                    st.session_state["flash_show_answer"] = False
                    st.session_state["flash_session_results"] = []
                    st.session_state["flash_mode"] = "study"
                    st.rerun()
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
