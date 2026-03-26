# flash_app.py — 未来塾 単語暗記アプリ（SM-2忘却曲線）改訂版
import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import date, timedelta

TRANSLATIONS = {
    "ja": {
        "app_title": "📖 単語暗記アプリ | 未来塾",
        "select_user": "ユーザーを選んでください",
        "start": "スタート！",
        "no_user": "ユーザーが登録されていません。管理者に連絡してください。",
        "select_prompt": "--- 選んでください ---",
        "select_error": "ユーザーを選んでください",
        "welcome": "さん！今日もいっしょに覚えよう！",
        "streak_msg": "日連続学習中！すごい！",
        "streak_zero": "📖 さあ、今日から始めよう！",
        "select_material": "📚 教材を選ぶ",
        "no_material": "教材がまだ登録されていません。管理者に連絡してください。",
        "material_label": "教材",
        "no_cards_set": "この教材にはまだ単語が登録されていません。",
        "page_range": "📖 ページ範囲:",
        "item_range": "🔢",
        "progress_caption": "枚クリア",
        "today_task": "📝 今日やること",
        "badge_new": "🆕 新しい単語",
        "badge_due": "🔁 復習が必要",
        "cards": "枚",
        "start_study": "✨ 今日の学習をはじめる！",
        "all_done": "🎉 今日の分は全部終わった！また明日！",
        "more_study": "🌟 もっとやりたい人はここから！",
        "current_title": "現在の称号",
        "total_xp_lbl": "累計",
        "weak_btn": "🔁 苦手だけ復習\n\n答えが出なかった\n単語をもう一度",
        "new_btn": "🚀 先取りチャレンジ\n\nまだ見ていない\n新しい単語へ",
        "all_btn": "🎯 全部通し復習\n\n教材の全単語を\nシャッフルで",
        "ta_btn": "⚡ タイムアタック！\n\n10秒で答えろ！\nランキングに挑戦",
        "logout": "🚪 ログアウト",
        "think_hint": "💭 意味を頭に思い浮かべてから押してね",
        "show_answer": "👀 答えを見る",
        "reading_label": "🔊 読み：",
        "reading_jp_lbl": "読み：",
        "phonetic_label": "🔤 発音：",
        "zh_meaning_label": "🇨🇳 中文：",
        "example_lbl": "📝 例文: ",
        "how_much": "どのくらい覚えていた？",
        "q0_btn": "❌\n全然ダメ\n\n答えが\n出てこなかった",
        "q3_btn": "🔶\nうっすら\n\n思い出すのに\n時間がかかった",
        "q4_btn": "🟢\nだいたい\n\nすぐ出たが\n少し不安だった",
        "q5_btn": "⭐\nバッチリ！\n\n一瞬で\n完全に自信あり",
        "next_day": "次回: 明日",
        "next_6d": "次回: 6日後",
        "next_weeks": "次回: 数週間後",
        "next_month": "次回: 1ヶ月以上",
        "legend_bad": "❌ 全然ダメ",
        "legend_good": "⭐ バッチリ！",
        "result_title": "🎉 今日の学習完了！",
        "perfect_lbl": "🎯 バッチリ",
        "good_lbl": "🟢 だいたい",
        "ok_lbl": "🔶 うっすら",
        "ng_lbl": "❌ 要復習",
        "lv_label": "🎮 累計",
        "next_lv": "次のレベルまで",
        "words_done": "✅ 覚えられた単語",
        "words_retry": "🔁 次回また挑戦",
        "ng_notice_tail": "は明日また出てきます。大丈夫、繰り返すことで必ず覚えられます！",
        "home_btn": "🏠 ホームへ戻る",
        "retry_btn": "🔁 もう一度チャレンジ",
        "graph_title": "📈 あなたの成長グラフ",
        "tab_xp": "⚡ XP推移",
        "tab_cards": "📚 学習枚数",
        "tab_acc": "🎯 正解率",
        "lang_switch": "🇨🇳 切换中文",
        "nickname_label": "🎮 ランキングネーム:",
        "nick_title": "### 🎮 ランキング用ネームを決めよう！",
        "nick_box1": "📺 なまえを いれてください",
        "nick_box2": "ランキングに表示される名前です。本名は使わないでね！",
        "nick_field": "ニックネーム（3〜8文字）",
        "nick_placeholder": "例: たんごマスター",
        "nick_submit": "⚡ これで決定！",
        "nick_err": "2文字以上で入力してください",
        "nick_ok": "🎉「{nick}」に決定！ランキングに参戦できます！",
        "nick_caption": "🎮 ランキングネーム: **{nick}**　[変更する場合はログアウト後に設定]",
        "weak_ok": "🎉 苦手な単語はありません！",
        "new_ok": "🏆 全単語制覇！すごい！",
        "daily_7": "🌟 7日連続達成！XP×2ボーナス獲得中！",
        "daily_3": "🔥 {s}日連続！あと{r}日で7日連続ボーナス！",
        "daily_0": "💡 毎日続けると7日連続ボーナスXP×2が解放されます！",
        "interrupt_btn": "⏸️ いったん中断してホームへ戻る",
        "progress_n": "{i} / {t} 枚目",
        "ta_question": "💭 正しい意味はどれ？",
        "ta_tap": "👇 正しい意味をタップ！",
        "ta_next": "➡️ 次の問題へ",
        "rank_title": "🏆 みんなのランキング（TOP10）",
        "rank_empty": "まだ記録がありません。あなたが1位になろう！",
        "ta_again": "🔁 もう一度タイムアタック",
        "score_save_err": "スコア保存エラー: ",
        "graph_need_days": "📊 グラフは2日以上学習すると表示されます！明日も来てね 🔥",
        "acc_no_data": "正解率データがありません",
        "study_days_caption": "🔥 過去30日で **{n}日** 学習しました！",
        "max_day_caption": "🏅 最多学習日: **{d}** ({n}枚)",
        "avg_acc_caption": "📊 過去30日の平均正解率: **{a:.1f}%**",
        "target_80": "目標 80%",
        "result_hero_100_title": "🏆 パーフェクト！！",
        "result_hero_100_sub": "全問正解！完璧な学習でした！",
        "result_hero_80_title": "🎉 素晴らしい！",
        "result_hero_80_sub": "正解率 {a:.0f}% — この調子で続けよう！",
        "result_hero_50_title": "💪 よく頑張った！",
        "result_hero_50_sub": "正解率 {a:.0f}% — 復習で差をつけよう！",
        "result_hero_low_title": "📖 今日はここから！",
        "result_hero_low_sub": "正解率 {a:.0f}% — 繰り返せば必ず覚えられる！",
        "xp_get": "⚡ +{xp} XP ゲット！",
        "summary_title": "### 📋 今日の単語まとめ",
        "no_words_yet": "まだありません",
        "none_perfect": "なし！完璧です 🎉",
        "chart_cum_xp_name": "累計XP",
        "chart_cum_xp_title": "累計XPの推移（過去30日）",
        "chart_date": "日付",
        "chart_daily_cards_name": "学習枚数",
        "chart_daily_cards_title": "日別 学習枚数（過去30日）",
        "chart_count_axis": "枚数",
        "chart_acc_name": "正解率",
        "chart_acc_title": "日別 正解率（過去30日）",
        "chart_acc_yaxis": "正解率 (%)",
        "ta_header": "⚡ タイムアタック {i}/{t}",
        "ta_reading": "読み: {r}",
        "ta_correct": "✅ 正解！",
        "ta_wrong": "❌ 不正解",
        "ta_seconds": "⏱ {s:.1f}秒",
        "ta_correct_meaning": "正解: <b>{m}</b>",
        "rank_ta_result": "⚡ タイムアタック結果",
        "rank_score_line": "{c}/{t}問正解",
        "rank_record_as": "🎮 {name} として記録",
        "rank_word_times": "### ⏱️ 単語別タイム",
        "rank_you": " 👈 あなた",
        "rank_q_suffix": "問",
        "word_list_title": "📋 今日の単語リスト",
        "word_list_sub": "まずこの単語を覚えてから、チェックに進もう！",
        "word_list_no": "No.",
        "word_list_word": "単語",
        "word_list_reading": "読み",
        "word_list_meaning": "意味",
        "word_list_start": "✅ 覚えた！単語チェックをはじめる",
        "word_list_back": "🏠 ホームに戻る",
        "word_list_note": "💡 ノートに書いて覚えるときはこのリストを見ながら練習しよう！",
    },
    "zh": {
        "app_title": "📖 单词记忆 | 未来塾",
        "select_user": "请选择用户",
        "start": "开始！",
        "no_user": "还没有注册用户，请联系管理员。",
        "select_prompt": "--- 请选择 ---",
        "select_error": "请选择用户",
        "welcome": "同学！我们一起来记单词吧！",
        "streak_msg": "天连续学习！太厉害了！",
        "streak_zero": "📖 今天开始学习吧！",
        "select_material": "📚 选择教材",
        "no_material": "还没有教材，请联系管理员。",
        "material_label": "教材",
        "no_cards_set": "本教材暂无单词。",
        "page_range": "📖 页码范围:",
        "item_range": "🔢",
        "progress_caption": "个已掌握",
        "today_task": "📝 今日任务",
        "badge_new": "🆕 新单词",
        "badge_due": "🔁 需要复习",
        "cards": "个",
        "start_study": "✨ 开始今天的学习！",
        "all_done": "🎉 今天的任务全部完成！明天见！",
        "more_study": "🌟 想继续学习的同学看这里！",
        "current_title": "当前称号",
        "total_xp_lbl": "累计",
        "weak_btn": "🔁 复习弱项\n\n再练一次\n没记住的单词",
        "new_btn": "🚀 提前挑战\n\n学习新的\n未见过的单词",
        "all_btn": "🎯 全部复习\n\n随机顺序\n复习所有单词",
        "ta_btn": "⚡ 限时挑战！\n\n10秒内作答！\n挑战排行榜",
        "logout": "🚪 退出登录",
        "think_hint": "💭 先在脑中想想意思，再按按钮",
        "show_answer": "👀 查看答案",
        "reading_label": "🔊 读音：",
        "reading_jp_lbl": "读音：",
        "phonetic_label": "🔤 发音：",
        "zh_meaning_label": "🇨🇳 中文：",
        "example_lbl": "📝 例句：",
        "how_much": "你记得多少？",
        "q0_btn": "❌\n完全不会\n\n完全\n想不起来",
        "q3_btn": "🔶\n有点印象\n\n想起来了\n但花了时间",
        "q4_btn": "🟢\n大体记得\n\n很快想起\n但不太确定",
        "q5_btn": "⭐\n完全记住！\n\n瞬间答出\n完全有把握",
        "next_day": "下次：明天",
        "next_6d": "下次：6天后",
        "next_weeks": "下次：数周后",
        "next_month": "下次：1个月以上",
        "legend_bad": "❌ 完全不会",
        "legend_good": "⭐ 完美！",
        "result_title": "🎉 今天的学习完成！",
        "perfect_lbl": "🎯 完美",
        "good_lbl": "🟢 大体记住",
        "ok_lbl": "🔶 有点印象",
        "ng_lbl": "❌ 需复习",
        "lv_label": "🎮 累计",
        "next_lv": "距离下一级",
        "words_done": "✅ 已记住的单词",
        "words_retry": "🔁 下次再挑战",
        "ng_notice_tail": "单词明天还会出现。反复练习一定能记住！",
        "home_btn": "🏠 返回首页",
        "retry_btn": "🔁 再挑战一次",
        "graph_title": "📈 你的成长图表",
        "tab_xp": "⚡ XP变化",
        "tab_cards": "📚 学习数量",
        "tab_acc": "🎯 正确率",
        "lang_switch": "🇯🇵 切换日本語",
        "nickname_label": "🎮 排行榜名称:",
        "nick_title": "### 🎮 设置排行榜昵称",
        "nick_box1": "📺 请输入昵称",
        "nick_box2": "将显示在排行榜上，请勿使用真实姓名！",
        "nick_field": "昵称（3〜8字）",
        "nick_placeholder": "例：单词达人",
        "nick_submit": "⚡ 确定！",
        "nick_err": "请输入至少2个字",
        "nick_ok": "🎉「{nick}」已确定！可以参加排行榜了！",
        "nick_caption": "🎮 排行榜名称: **{nick}**　[修改请退出后设置]",
        "weak_ok": "🎉 没有薄弱单词！",
        "new_ok": "🏆 全部单词已掌握！太棒了！",
        "daily_7": "🌟 连续7天达成！XP×2奖励中！",
        "daily_3": "🔥 已连续{s}天！再过{r}天解锁7天奖励！",
        "daily_0": "💡 每天坚持可解锁连续7天XP×2奖励！",
        "interrupt_btn": "⏸️ 暂停并返回首页",
        "progress_n": "{i} / {t} 题",
        "ta_question": "💭 正确的意思是哪个？",
        "ta_tap": "👇 点击正确的意思！",
        "ta_next": "➡️ 下一题",
        "rank_title": "🏆 排行榜（TOP10）",
        "rank_empty": "还没有记录，来当第一吧！",
        "ta_again": "🔁 再来一次限时",
        "score_save_err": "保存分数出错：",
        "graph_need_days": "📊 学习满2天即可显示图表！明天再来哦 🔥",
        "acc_no_data": "暂无正确率数据",
        "study_days_caption": "🔥 过去30天共学习 **{n}天**！",
        "max_day_caption": "🏅 学习最多的一天: **{d}** ({n}个)",
        "avg_acc_caption": "📊 过去30天平均正确率: **{a:.1f}%**",
        "target_80": "目标 80%",
        "result_hero_100_title": "🏆 全对！！",
        "result_hero_100_sub": "全部答对！太棒了！",
        "result_hero_80_title": "🎉 太棒了！",
        "result_hero_80_sub": "正确率 {a:.0f}% — 继续保持！",
        "result_hero_50_title": "💪 加油！",
        "result_hero_50_sub": "正确率 {a:.0f}% — 复习一下会更好！",
        "result_hero_low_title": "📖 从这里开始！",
        "result_hero_low_sub": "正确率 {a:.0f}% — 多练一定能记住！",
        "xp_get": "⚡ +{xp} XP 获得！",
        "summary_title": "### 📋 今日单词汇总",
        "no_words_yet": "还没有",
        "none_perfect": "没有！全对 🎉",
        "chart_cum_xp_name": "累计XP",
        "chart_cum_xp_title": "累计XP变化（过去30天）",
        "chart_date": "日期",
        "chart_daily_cards_name": "学习数量",
        "chart_daily_cards_title": "每日学习数量（过去30天）",
        "chart_count_axis": "数量",
        "chart_acc_name": "正确率",
        "chart_acc_title": "每日正确率（过去30天）",
        "chart_acc_yaxis": "正确率 (%)",
        "ta_header": "⚡ 限时挑战 {i}/{t}",
        "ta_reading": "读音: {r}",
        "ta_correct": "✅ 正确！",
        "ta_wrong": "❌ 错误",
        "ta_seconds": "⏱ {s:.1f}秒",
        "ta_correct_meaning": "正确答案: <b>{m}</b>",
        "rank_ta_result": "⚡ 限时挑战结果",
        "rank_score_line": "{c}/{t}题答对",
        "rank_record_as": "🎮 以 {name} 记录",
        "rank_word_times": "### ⏱️ 各题用时",
        "rank_you": " 👈 你",
        "rank_q_suffix": "题",
        "word_list_title": "📋 今日的单词列表",
        "word_list_sub": "先记住这些单词，再开始测验！",
        "word_list_no": "No.",
        "word_list_word": "单词",
        "word_list_reading": "读音",
        "word_list_meaning": "意思",
        "word_list_start": "✅ 记住了！开始单词测验",
        "word_list_back": "🏠 返回首页",
        "word_list_note": "💡 想用笔记本抄写的同学，可以对照这个列表练习！",
    },
}


def T(key):
    """現在の言語設定でテキストを返す"""
    lang = st.session_state.get("user_lang", "ja")
    return TRANSLATIONS.get(lang, TRANSLATIONS["ja"]).get(
        key, TRANSLATIONS["ja"].get(key, key)
    )


st.set_page_config(page_title="📖 単語暗記 | 未来塾", layout="centered")

# ── フォント読み込み（linkタグ単独）──────────────
st.markdown(
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP'
    ':wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700'
    '&family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# ── フォント適用CSS（styleタグ単独）──────────────
st.markdown("""
<style>
.main .block-container,
.main .block-container p,
.main .block-container span,
.main .block-container div,
.main .block-container label,
.main .block-container h1,
.main .block-container h2,
.main .block-container h3 {
    font-family: 'Noto Sans JP', 'Noto Sans SC', 'Noto Sans', sans-serif !important;
}
[data-testid="stMarkdownContainer"] *,
[data-testid="stText"],
[data-testid="stCaption"],
[data-testid="stAlert"] div,
[data-testid="stExpander"] summary span,
[data-testid="stSelectbox"] *,
[data-testid="stTextInput"] input,
[data-testid="stSlider"] *,
[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-secondary"] p {
    font-family: 'Noto Sans JP', 'Noto Sans SC', 'Noto Sans', sans-serif !important;
}
.card-front, .card-back,
.card-word, .card-reading,
.card-meaning, .card-example {
    font-family: 'Noto Sans JP', 'Noto Sans SC', 'Noto Sans', sans-serif !important;
}
.stMarkdown div[style],
.stMarkdown span[style] {
    font-family: 'Noto Sans JP', 'Noto Sans SC', 'Noto Sans', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

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
# save_review（review_logs に upsert）
# ─────────────────────────────
def save_review(username, cid, q, new_ef, new_iv, new_rp, next_date):
    # cidがNoneまたは0の場合は外部キー制約違反になるためスキップ
    if not cid:
        return

    supabase = get_supabase()
    safe_username = str(username) if username else "admin"
    safe_cid = int(cid)
    data = {
        "username":         safe_username,
        "flashcard_id":     safe_cid,
        "quality":          int(q) if q is not None else 0,
        "ease_factor":      float(new_ef) if new_ef is not None else 2.5,
        "interval_days":    int(new_iv) if new_iv is not None else 1,
        "repetitions":      int(new_rp) if new_rp is not None else 1,
        "next_review_date": str(next_date) if next_date else date.today().isoformat(),
    }
    existing = (
        supabase.table("review_logs")
        .select("id")
        .eq("username", safe_username)
        .eq("flashcard_id", safe_cid)
        .execute()
    )
    if existing.data:
        supabase.table("review_logs").update(data).eq("username", safe_username).eq(
            "flashcard_id", safe_cid
        ).execute()
    else:
        supabase.table("review_logs").insert(data).execute()
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


# Supabase SQL Editor で users に nickname 列を追加するときの例（手動実行）:
# ALTER TABLE users ADD COLUMN IF NOT EXISTS nickname TEXT DEFAULT '';
# ALTER TABLE users ADD COLUMN IF NOT EXISTS lang TEXT DEFAULT 'ja';


@st.cache_data(ttl=60)
def load_user_nickname(username):
    """ユーザーのニックネームを取得"""
    try:
        sb = get_supabase()
        res = sb.table("users").select("nickname").eq("username", username).execute()
        if res.data and res.data[0].get("nickname"):
            return res.data[0]["nickname"]
        return ""
    except:
        return ""


@st.cache_data(ttl=60)
def load_user_lang(username):
    """ユーザーの言語設定を取得"""
    try:
        sb = get_supabase()
        res = sb.table("users").select("lang").eq("username", username).execute()
        if res.data and res.data[0].get("lang"):
            return res.data[0]["lang"]
        return "ja"
    except:
        return "ja"


def save_user_lang(username, lang):
    """言語設定を保存"""
    try:
        sb = get_supabase()
        sb.table("users").update({"lang": lang}).eq("username", username).execute()
        st.cache_data.clear()
    except:
        pass


def save_user_nickname(username, nickname):
    """ニックネームを保存"""
    try:
        sb = get_supabase()
        sb.table("users").update({"nickname": nickname}).eq("username", username).execute()
        st.cache_data.clear()
        return True
    except:
        return False


@st.cache_data(ttl=60)
def load_study_plan(username: str) -> dict:
    """
    基本ペース(base_daily_limit)と今日の調整値を取得する。
    today_limit_date が今日でなければ today_limit は無効とみなす。
    戻り値: {"base": int, "today": int, "effective": int}
      effective = 今日実際に使う枚数
    """
    try:
        sb = get_supabase()
        res = sb.table("users").select(
            "base_daily_limit, today_limit, today_limit_date"
        ).eq("username", username).execute()
        if not res.data:
            return {"base": 10, "today": None, "effective": 10}
        row = res.data[0]
        base = int(row.get("base_daily_limit") or 10)
        today_str = date.today().isoformat()
        today_limit = row.get("today_limit")
        today_date = row.get("today_limit_date")
        # 今日の日付と一致する場合のみ today_limit を有効にする
        if today_limit is not None and str(today_date) == today_str:
            effective = int(today_limit)
        else:
            effective = base
        return {"base": base, "today": today_limit if str(today_date) == today_str else None, "effective": effective}
    except:
        return {"base": 10, "today": None, "effective": 10}


def save_base_limit(username: str, limit: int) -> bool:
    """基本ペース（base_daily_limit）を保存する"""
    try:
        sb = get_supabase()
        sb.table("users").update({
            "base_daily_limit": limit,
            "today_limit": None,
            "today_limit_date": None,
        }).eq("username", username).execute()
        st.cache_data.clear()
        return True
    except:
        return False


def save_today_limit(username: str, limit: int) -> bool:
    """今日だけの調整枚数を保存する"""
    try:
        sb = get_supabase()
        sb.table("users").update({
            "today_limit": limit,
            "today_limit_date": date.today().isoformat(),
        }).eq("username", username).execute()
        st.cache_data.clear()
        return True
    except:
        return False


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
        res = sb.table("flashcards").select(
            "id, word, reading, phonetic, meaning, meaning_zh, "
            "example, category, grade, set_id, item_no, page_range, username"
        ).eq("set_id", set_id).execute()
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

def load_due_cards(username: str, set_id: int) -> list:
    cards = load_flashcards_by_set(set_id)
    if not cards:
        return []
    logs = load_review_logs(username)
    plan = load_study_plan(username)
    daily_limit = plan["effective"]

    latest = {}
    for row in logs:
        cid = row["flashcard_id"]
        if cid not in latest or row["reviewed_at"] > latest[cid]["reviewed_at"]:
            latest[cid] = row

    today_str = date.today().isoformat()
    new_cards = [c for c in cards if c["id"] not in latest]
    random.shuffle(new_cards)
    new_cards = new_cards[:daily_limit]

    due_cards = [
        c for c in cards
        if c["id"] in latest
        and latest[c["id"]].get("next_review_date", "9999") <= today_str
    ]

    combined = new_cards + due_cards
    random.shuffle(combined)
    return combined


def render_card_front(card: dict, lang: str = "ja"):
    category = str(card.get("category", ""))

    if "みんなの日本語" in category:
        meaning = card.get("meaning", "")
        st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#fff9f0,#fff3e0);
    border-radius:16px;
    padding:2.5rem 1.5rem;
    text-align:center;
    box-shadow:0 4px 16px rgba(0,0,0,0.08);
    margin:0.5rem 0;">
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">問題</div>
  <div style="font-size:2.2rem;font-weight:700;color:#1a1a1a;line-height:1.4;">
    {meaning}
  </div>
  <div style="font-size:0.85rem;color:#bbb;margin-top:1rem;">日本語で何と言いますか？</div>
</div>
""", unsafe_allow_html=True)

    else:
        word    = card.get("word", "")
        reading = card.get("reading", "")
        reading_html = f'<div style="font-size:1rem;color:#888;margin-top:0.4rem;">{reading}</div>' \
                       if reading and reading != word else ""
        st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#f0f4ff,#e8f0fe);
    border-radius:16px;
    padding:2.5rem 1.5rem;
    text-align:center;
    box-shadow:0 4px 16px rgba(0,0,0,0.08);
    margin:0.5rem 0;">
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">問題</div>
  <div style="font-size:2.4rem;font-weight:700;color:#1a1a1a;">
    {word}
  </div>
  {reading_html}
</div>
""", unsafe_allow_html=True)


def render_card_back(card: dict, lang: str = "ja"):
    category = str(card.get("category", ""))

    if "みんなの日本語" in category:
        word    = card.get("word", "")
        reading = card.get("reading", "")
        pos     = card.get("meaning_zh", "")   # 品詞〈名〉〈動I〉
        accent  = card.get("phonetic", "")     # アクセント番号

        accent_html = f'<span style="font-size:0.95rem;color:#e05a00;margin-left:0.5rem;">{accent}</span>' \
                      if accent else ""
        pos_html    = f'<div style="font-size:0.9rem;color:#888;margin-top:0.5rem;">{pos}</div>' \
                      if pos else ""

        st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#f0fff4,#e6ffed);
    border-radius:16px;
    padding:2.5rem 1.5rem;
    text-align:center;
    box-shadow:0 4px 16px rgba(0,0,0,0.08);
    margin:0.5rem 0;">
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">答え</div>
  <div style="font-size:2.2rem;font-weight:700;color:#1a1a1a;line-height:1.4;">
    {word}
  </div>
  <div style="font-size:1.1rem;color:#555;margin-top:0.5rem;">
    {reading}{accent_html}
  </div>
  {pos_html}
</div>
""", unsafe_allow_html=True)

    else:
        meaning    = card.get("meaning", "")
        reading    = card.get("reading", "")
        phonetic   = card.get("phonetic", "")
        meaning_zh = card.get("meaning_zh", "")
        example    = card.get("example", "")

        ph_html = f'<div style="font-size:1rem;color:#777;margin-top:0.3rem;">{phonetic}</div>' \
                  if phonetic else ""
        zh_html = f'<div style="font-size:1.1rem;color:#e05a00;margin-top:0.6rem;">🇨🇳 {meaning_zh}</div>' \
                  if meaning_zh else ""
        ex_html = f'<div style="font-size:0.9rem;color:#aaa;margin-top:0.6rem;font-style:italic;">{example}</div>' \
                  if example else ""
        rd_html = f'<div style="font-size:1rem;color:#555;margin-top:0.4rem;">読み：{reading}</div>' \
                  if reading else ""

        st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#f0f4ff,#e8f0fe);
    border-radius:16px;
    padding:2.5rem 1.5rem;
    text-align:center;
    box-shadow:0 4px 16px rgba(0,0,0,0.08);
    margin:0.5rem 0;">
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">答え</div>
  <div style="font-size:1.8rem;font-weight:700;color:#1a1a1a;">
    {meaning}
  </div>
  {rd_html}
  {ph_html}
  {zh_html}
  {ex_html}
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────
# セッション初期化
# ─────────────────────────────
for key, default in [
    ("flash_user", ""),
    ("user_lang", "ja"),
    ("flash_mode", "home"),
    ("show_settings", False),
    ("flash_queue", []),
    ("word_list_queue", []),
    ("flash_index", 0),
    ("flash_show_answer", False),
    ("flash_session_results", []),
    ("selected_set_id", None),
    ("flash_timer_start", None),
    ("flash_time_scores", []),
    ("ta_choices", []),
    ("ta_answered", False),
    ("ta_correct", None),
    ("ta_selected_idx", -1),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────
# ログイン画面
# ─────────────────────────────
if not st.session_state["flash_user"]:
    st.title(T("app_title"))
    user_list = load_users()
    if not user_list:
        st.warning(T("no_user"))
        st.stop()
    prompt = T("select_prompt")
    selected = st.selectbox(T("select_user"), [prompt] + user_list)
    if st.button(T("start")):
        if selected == prompt:
            st.error(T("select_error"))
        else:
            st.session_state["flash_user"] = selected
            st.session_state["user_lang"] = load_user_lang(selected)
            st.rerun()
    st.stop()

username = st.session_state["flash_user"]

# ─────────────────────────────
# ホーム画面
# ─────────────────────────────
def show_home(username):
    # ── CSS ────────────────────────────────
    st.markdown("""
    <style>
    .badge-red {
        background:#ff4b4b; color:white;
        border-radius:20px; padding:4px 14px;
        font-weight:bold; display:inline-block; margin:4px;
        font-size:1rem;
    }
    .badge-yellow {
        background:#ffa500; color:white;
        border-radius:20px; padding:4px 14px;
        font-weight:bold; display:inline-block; margin:4px;
        font-size:1rem;
    }
    .mini-card {
        background:#f8f9ff; border:1px solid #e0e4ff;
        border-radius:12px; padding:10px 16px;
        margin-bottom:8px; font-size:0.9rem; color:#444;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── モード判定 ─────────────────────────
    show_settings = st.session_state.get("show_settings", False)

    # ── ヘッダー行（常に表示） ──────────────
    col_title, col_gear = st.columns([5, 1])
    with col_title:
        if st.session_state.get("user_lang") == "zh":
            st.markdown(f"### 你好，{username}！")
        else:
            st.markdown(f"### こんにちは、{username}さん！")
    with col_gear:
        gear_label = "✖ 閉じる" if show_settings else "⚙️ 設定"
        if st.button(gear_label, key="toggle_settings"):
            st.session_state["show_settings"] = not show_settings
            st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 設定ページ
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if show_settings:
        st.markdown("---")
        st.markdown("#### ⚙️ 設定")

        # 言語切替
        if st.button(T("lang_switch"), key="lang_toggle"):
            new_lang = "zh" if st.session_state["user_lang"] == "ja" else "ja"
            st.session_state["user_lang"] = new_lang
            save_user_lang(username, new_lang)
            st.rerun()

        st.markdown("---")

        # 教材選択
        st.markdown("##### 📚 教材を選ぶ")
        sets = load_flashcard_sets()
        if sets:
            set_id_list = [s["id"] for s in sets]
            set_name_map = {s["id"]: s["set_name"] for s in sets}
            set_info_map = {s["id"]: s for s in sets}
            prev = st.session_state.get("selected_set_id")
            default_idx = set_id_list.index(prev) if prev in set_id_list else 0
            selected_set_id = st.selectbox(
                "教材",
                options=set_id_list,
                index=default_idx,
                format_func=lambda x: set_name_map[x],
                key="settings_set_select",
            )
            st.session_state["selected_set_id"] = selected_set_id
            info = set_info_map[selected_set_id]
            st.caption(
                f"📂 {info.get('category','')} ／ {info.get('grade','')} ／ {info.get('description','')}"
            )
        else:
            st.warning(T("no_material"))

        st.markdown("---")

        # 学習ペース設定
        st.markdown("##### 📅 学習ペース設定")
        plan = load_study_plan(username)
        base = plan["base"]
        today = plan["today"]
        eff = plan["effective"]

        st.markdown(
            f"<div style='font-size:0.9rem;color:#555;margin-bottom:8px;'>"
            f"現在の設定: <b>{eff}枚/日</b>"
            + (f"　（基本: {base}枚 / 今日: {today}枚）" if today is not None and today != base else "")
            + "</div>",
            unsafe_allow_html=True,
        )
        pace_options = [3, 5, 10, 15, 20, 25, 30]
        pace_mode = st.radio(
            "設定モード",
            options=["📋 基本ペースを変更", "⚡ 今日だけ調整"],
            horizontal=True,
            key="pace_mode_radio",
            label_visibility="collapsed",
        )
        if pace_mode == "📋 基本ペースを変更":
            st.caption("先生と相談して決めた1日の目標枚数です。")
            new_base = st.radio(
                "基本枚数",
                options=pace_options,
                index=pace_options.index(base) if base in pace_options else 1,
                horizontal=True,
                key="base_radio",
                format_func=lambda x: f"{x}枚",
            )
            st.caption("目安: 3〜5枚=初めて / 10枚=標準 / 20枚以上=試験前")
            if st.button("✅ 基本ペースを保存", key="save_base"):
                if save_base_limit(username, new_base):
                    st.success(f"基本ペースを {new_base}枚 に設定しました！")
                    st.rerun()
        else:
            st.caption("今日だけ変更できます。翌日は基本ペースに自動で戻ります。")
            adj_default = today if (today is not None and today in pace_options) else eff
            if adj_default not in pace_options:
                adj_default = 10
            new_today = st.radio(
                "今日の枚数",
                options=pace_options,
                index=pace_options.index(adj_default),
                horizontal=True,
                key="today_radio",
                format_func=lambda x: f"{x}枚",
            )
            diff = new_today - base
            st.caption(
                f"基本より {abs(diff)}枚 {'少なめ' if diff < 0 else '多め！🔥' if diff > 0 else '→ 基本ペース通り 👍'}"
            )
            if st.button("⚡ 今日はこの枚数で！", key="save_today"):
                if save_today_limit(username, new_today):
                    st.success(f"今日は {new_today}枚 で学習します！")
                    st.rerun()

        st.markdown("---")

        # ニックネーム設定
        st.markdown("##### 🎮 ランキングネーム")
        current_nick = load_user_nickname(username)
        if current_nick:
            st.caption(f"現在: **{current_nick}**")
        nick_input = st.text_input(
            "新しいニックネーム（2〜8文字）",
            max_chars=8,
            placeholder="例: たんごマスター",
            key="settings_nick",
        )
        if st.button("💾 保存", key="save_nick"):
            if len(nick_input) < 2:
                st.error("2文字以上で入力してください")
            else:
                if save_user_nickname(username, nick_input):
                    st.success(f"「{nick_input}」に変更しました！")
                    st.balloons()
                    st.rerun()

        st.markdown("---")

        # ログアウト
        if st.button(T("logout"), key="settings_logout"):
            st.session_state["flash_user"] = ""
            st.session_state["show_settings"] = False
            st.rerun()

        return  # 設定ページ表示中はホームコンテンツを表示しない

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ホームページ（学習特化・シンプル）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # 連続日数
    streak = compute_learning_streak(username)
    if streak >= 1:
        st.info(f"🔥 {streak}{T('streak_msg')}")
    else:
        st.info(T("streak_zero"))

    # 教材が未選択の場合は設定へ誘導
    sets = load_flashcard_sets()
    if not sets:
        st.warning(T("no_material"))
        return

    set_id_list = [s["id"] for s in sets]
    set_info_map = {s["id"]: s for s in sets}
    prev = st.session_state.get("selected_set_id")
    if prev not in set_id_list:
        st.session_state["selected_set_id"] = set_id_list[0]
    selected_set_id = st.session_state["selected_set_id"]
    info = set_info_map[selected_set_id]
    cards = load_flashcards_by_set(selected_set_id)
    total = len(cards)

    # 教材情報（コンパクト1行）
    set_name_map = {s["id"]: s["set_name"] for s in sets}
    st.markdown(
        f"<div class='mini-card'>📚 <b>{set_name_map[selected_set_id]}</b>"
        f"　{info.get('category','')} / {info.get('grade','')}</div>",
        unsafe_allow_html=True,
    )

    # 進捗バー
    if total > 0:
        correct = count_correct_once_in_set(username, selected_set_id)
        progress_val = correct / total
        st.progress(progress_val)
        st.caption(f"✅ {correct} / {total} {T('progress_caption')}（{int(progress_val*100)}%）")

    st.markdown("---")

    # ── 今日やること（メイン） ──────────────────
    st.markdown(f"### {T('today_task')}")
    new_count, due_count = count_new_and_due_for_set(username, selected_set_id)
    plan = load_study_plan(username)
    st.markdown(
        f'<span class="badge-red">{T("badge_new")} {new_count}{T("cards")}</span>'
        f'<span class="badge-yellow">{T("badge_due")} {due_count}{T("cards")}</span>',
        unsafe_allow_html=True,
    )
    st.caption(f"📅 1日のペース: {plan['effective']}枚")
    st.markdown("")

    total_today = new_count + due_count
    if total_today > 0:
        if st.button(T("start_study"), type="primary", use_container_width=True):
            queue = load_due_cards(username, selected_set_id)
            if queue:
                st.session_state["flash_queue"] = queue
                st.session_state["word_list_queue"] = queue
                st.session_state["flash_index"] = 0
                st.session_state["flash_show_answer"] = False
                st.session_state["flash_session_results"] = []
                st.session_state["flash_mode"] = "word_list"
                st.rerun()
            else:
                st.warning("カードが見つかりませんでした。")
    else:
        # 今日の分が終わった場合
        st.success(T("all_done"))
        st.markdown(f"#### {T('more_study')}")

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
        st.markdown(
            f"<div style='background:linear-gradient(135deg,#667eea,#764ba2);"
            f"border-radius:16px;padding:14px 20px;color:white;"
            f"display:flex;align-items:center;gap:12px;margin-bottom:16px;'>"
            f"<span style='font-size:2rem;'>{icon}</span>"
            f"<div><div style='font-size:0.8rem;opacity:0.85;'>{T('current_title')}</div>"
            f"<div style='font-size:1.2rem;font-weight:bold;'>Lv.{level} {title}</div>"
            f"<div style='font-size:0.78rem;opacity:0.75;'>{T('total_xp_lbl')} {total_xp} XP</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            if st.button(T("weak_btn"), key="extra_weak", use_container_width=True):
                cards_all = load_flashcards_by_set(selected_set_id)
                logs = load_review_logs(username)
                latest = {}
                for row in logs:
                    cid = row["flashcard_id"]
                    if cid not in latest or row["reviewed_at"] > latest[cid]["reviewed_at"]:
                        latest[cid] = row
                weak_ids = {cid for cid, row in latest.items() if row.get("quality", 5) < 4}
                weak_cards = [c for c in cards_all if c["id"] in weak_ids]
                if weak_cards:
                    random.shuffle(weak_cards)
                    st.session_state["flash_queue"] = weak_cards
                    st.session_state["flash_index"] = 0
                    st.session_state["flash_show_answer"] = False
                    st.session_state["flash_session_results"] = []
                    st.session_state["flash_mode"] = "study"
                    st.rerun()
                else:
                    st.success(T("weak_ok"))
        with ex2:
            if st.button(T("new_btn"), key="extra_new", use_container_width=True):
                cards_all = load_flashcards_by_set(selected_set_id)
                logs = load_review_logs(username)
                learned_ids = {row["flashcard_id"] for row in logs}
                new_cards = [c for c in cards_all if c["id"] not in learned_ids]
                if new_cards:
                    random.shuffle(new_cards)
                    st.session_state["flash_queue"] = new_cards[:10]
                    st.session_state["flash_index"] = 0
                    st.session_state["flash_show_answer"] = False
                    st.session_state["flash_session_results"] = []
                    st.session_state["flash_mode"] = "study"
                    st.rerun()
                else:
                    st.success(T("new_ok"))
        with ex3:
            if st.button(T("all_btn"), key="extra_all", use_container_width=True):
                cards_all = load_flashcards_by_set(selected_set_id)
                if cards_all:
                    random.shuffle(cards_all)
                    st.session_state["flash_queue"] = cards_all
                    st.session_state["flash_index"] = 0
                    st.session_state["flash_show_answer"] = False
                    st.session_state["flash_session_results"] = []
                    st.session_state["flash_mode"] = "study"
                    st.rerun()

        # タイムアタックボタン
        if st.button(T("ta_btn"), key="extra_ta", use_container_width=True):
            cards_all = load_flashcards_by_set(selected_set_id)
            if cards_all:
                random.shuffle(cards_all)
                st.session_state["flash_queue"] = cards_all[:10]
                st.session_state["flash_index"] = 0
                st.session_state["flash_time_scores"] = []
                st.session_state["ta_choices"] = []
                st.session_state["ta_answered"] = False
                st.session_state["ta_correct"] = None
                st.session_state["ta_selected_idx"] = -1
                st.session_state["flash_mode"] = "time_attack"
                st.rerun()

        # ストリーク情報
        streak = compute_learning_streak(username)
        if streak >= 7:
            st.success(T("daily_7"))
        elif streak >= 3:
            st.info(T("daily_3").format(s=streak, r=7 - streak))
        else:
            st.info(T("daily_0"))


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
            f'<div class="progress-bar-label">'
            f'{T("progress_n").format(i=idx + 1, t=total)}</div>',
            unsafe_allow_html=True,
        )
        st.progress(idx / total)
    with col_home:
        if st.button("🏠", help=T("home_btn"), use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.rerun()

    if not st.session_state["flash_show_answer"]:
        render_card_front(card)

        st.markdown(
            "<div style='text-align:center; color:#888; "
            "font-size:0.9rem; margin:8px 0;'>"
            f"{T('think_hint')}</div>",
            unsafe_allow_html=True,
        )
        if st.button(T("show_answer"), type="primary", use_container_width=True):
            st.session_state["flash_show_answer"] = True
            st.rerun()
    else:
        render_card_back(card)

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
        st.markdown(f"### {T('how_much')}")

        # グラデーション凡例バー
        st.markdown(
            f"""
<div style="
    height: 12px; border-radius: 8px;
    background: linear-gradient(to right, #ff4b4b, #ffa500, #00b09b, #667eea);
    margin: 4px 0 2px 0;
"></div>
<div style="display:flex; justify-content:space-between;
            font-size:0.75rem; color:#888; margin-bottom:16px;">
    <span>{T("legend_bad")}</span><span>{T("legend_good")}</span>
</div>
""",
            unsafe_allow_html=True,
        )

        # ワンタップカードボタン（1列4つ）
        c0, c1, c2, c3 = st.columns(4)

        with c0:
            if st.button(
                T("q0_btn"),
                key="q0", use_container_width=True
            ):
                record_quality(0)

        with c1:
            if st.button(
                T("q3_btn"),
                key="q3", use_container_width=True
            ):
                record_quality(3)

        with c2:
            if st.button(
                T("q4_btn"),
                key="q4", use_container_width=True
            ):
                record_quality(4)

        with c3:
            if st.button(
                T("q5_btn"),
                key="q5", use_container_width=True
            ):
                record_quality(5)

        # 次回復習の目安（ボタン下）
        st.markdown(
            f"""
<div style="display:flex; justify-content:space-between;
            font-size:0.70rem; color:#bbb; margin-top:6px;">
    <span style="flex:1;text-align:center;">{T("next_day")}</span>
    <span style="flex:1;text-align:center;">{T("next_6d")}</span>
    <span style="flex:1;text-align:center;">{T("next_weeks")}</span>
    <span style="flex:1;text-align:center;">{T("next_month")}</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        if st.button(T("interrupt_btn"), use_container_width=True):
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


# Supabase SQL Editor で ta_scores テーブルを作成するときの例（手動実行）:
# CREATE TABLE IF NOT EXISTS ta_scores (
#   id SERIAL PRIMARY KEY,
#   username TEXT NOT NULL,
#   nickname TEXT NOT NULL DEFAULT 'なし',
#   set_id INTEGER NOT NULL,
#   total_score INTEGER NOT NULL,
#   correct_count INTEGER NOT NULL,
#   total_cards INTEGER NOT NULL,
#   played_at TIMESTAMP DEFAULT NOW()
# );


def generate_choices(correct_card, all_cards, n=4):
    import random
    category = str(correct_card.get("category", ""))
    if "みんなの日本語" in category:
        # 問題は中国語(meaning)、正解は日本語(word)
        correct_answer = correct_card["word"]
        others = [
            c["word"] for c in all_cards
            if c["id"] != correct_card["id"]
            and c["word"] != correct_answer
        ]
    else:
        # 問題は英語(word)、正解は日本語訳(meaning)
        correct_answer = correct_card["meaning"]
        others = [
            c["meaning"] for c in all_cards
            if c["id"] != correct_card["id"]
            and c["meaning"] != correct_answer
        ]
    fallback = ["わからない", "べつのことば", "ちがうもの",
                "またべつのもの", "なにかのこと"]
    while len(others) < 3:
        fb = fallback.pop(0)
        if fb not in others:
            others.append(fb)
    dummy = random.sample(others, 3)
    choices = dummy + [correct_answer]
    random.shuffle(choices)
    return choices


def _record_ta_quality(username, card, quality):
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
    new_ef, new_iv, new_rp, next_date = sm2_update(quality, ef, iv, rp)
    save_review(username, cid, quality, new_ef, new_iv, new_rp, next_date)


def save_ta_score(username, nickname, set_id, total_score,
                  correct_count, total_cards):
    try:
        sb = get_supabase()
        sb.table("ta_scores").insert({
            "username": username,
            "nickname": nickname if nickname else username,
            "set_id": set_id,
            "total_score": total_score,
            "correct_count": correct_count,
            "total_cards": total_cards,
        }).execute()
        st.cache_data.clear()
    except Exception as e:
        st.warning(f"スコア保存エラー: {e}")


@st.cache_data(ttl=30)
def load_ta_ranking(set_id, limit=10):
    try:
        sb = get_supabase()
        res = (
            sb.table("ta_scores")
            .select("nickname,total_score,correct_count,total_cards,played_at")
            .eq("set_id", set_id)
            .order("total_score", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data if res.data else []
    except:
        return []


def show_time_attack(username):
    import time

    queue = st.session_state["flash_queue"]
    idx = st.session_state["flash_index"]

    if idx >= len(queue):
        st.session_state["flash_mode"] = "ranking"
        st.rerun()

    card = queue[idx]
    total = len(queue)

    # ── CSS ──────────────────────────────────
    st.markdown("""
    <style>
    .ta-card-dark {
        background: linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius: 20px; padding: 36px 24px;
        text-align: center; color: white; margin: 12px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .ta-word {
        font-size: 2.8rem; font-weight: bold;
        letter-spacing: 3px; margin-bottom: 8px;
    }
    .ta-timer {
        font-size: 2.8rem; font-weight: bold;
        text-align: center; font-family: monospace;
    }
    /* 4択ボタン 未回答時 */
    div[data-testid="stHorizontalBlock"]
        button[kind="secondary"] {
        background: white !important;
        color: #333 !important;
        border: 2px solid #ddd !important;
        border-radius: 16px !important;
        min-height: 80px !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        white-space: pre-wrap !important;
        transition: all 0.15s !important;
        box-shadow: 0 4px 0 #ccc !important;
    }
    div[data-testid="stHorizontalBlock"]
        button[kind="secondary"]:hover {
        border-color: #667eea !important;
        box-shadow: 0 4px 0 #667eea !important;
        transform: translateY(-2px) !important;
    }
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
    </style>
    """, unsafe_allow_html=True)

    # ── ヘッダー ──────────────────────────────
    col_p, col_h = st.columns([4, 1])
    with col_p:
        st.markdown(
            f'<div style="font-size:0.9rem;color:#888;">'
            f'{T("ta_header").format(i=idx + 1, t=total)}</div>',
            unsafe_allow_html=True
        )
        st.progress(idx / total)
    with col_h:
        if st.button("🏠", key="ta_home", help=T("home_btn")):
            st.session_state["flash_mode"] = "home"
            st.session_state["ta_choices"] = []
            st.session_state["ta_answered"] = False
            st.session_state["ta_correct"] = None
            st.session_state["ta_selected_idx"] = -1
            st.session_state["flash_timer_start"] = None
            st.rerun()

    # ── タイマー管理 ─────────────────────────
    if st.session_state["flash_timer_start"] is None:
        st.session_state["flash_timer_start"] = time.time()

    elapsed = time.time() - st.session_state["flash_timer_start"]
    limit = 10  # 秒
    remaining = max(0.0, limit - elapsed)

    # タイマーの色を残り時間で変える
    if remaining > 6:
        timer_color = "#00b09b"   # 緑
    elif remaining > 3:
        timer_color = "#ffa500"   # オレンジ
    else:
        timer_color = "#ff4b4b"   # 赤

    # ── カード表示 ───────────────────────────
    if not st.session_state["ta_answered"]:
        st.markdown(
            f'<div style="font-size:0.85rem; opacity:0.6; margin-bottom:6px; '
            f'text-align:center; color:#aaa;">{T("ta_question")}</div>',
            unsafe_allow_html=True,
        )
        render_card_front(card)
    else:
        render_card_back(card)

    # ── タイマー表示 ─────────────────────────
    if not st.session_state["ta_answered"]:
        st.markdown(
            f'<div class="ta-timer" style="color:{timer_color};">'
            f'{T("ta_seconds").format(s=remaining)}</div>',
            unsafe_allow_html=True
        )
    else:
        # 回答済みは結果カラーで固定表示
        result_color = "#00b09b" if st.session_state["ta_correct"] else "#ff4b4b"
        result_text = (
            T("ta_correct") if st.session_state["ta_correct"] else T("ta_wrong")
        )
        st.markdown(
            f'<div class="ta-timer" style="color:{result_color};">'
            f'{result_text}</div>',
            unsafe_allow_html=True
        )

    # ── 4択ボタン生成 ────────────────────────
    # 選択肢がない or 新しいカードの場合のみ生成
    if not st.session_state["ta_choices"]:
        all_cards = load_flashcards_by_set(
            st.session_state.get("selected_set_id")
        )
        st.session_state["ta_choices"] = generate_choices(card, all_cards)

    choices = st.session_state["ta_choices"]
    category = str(card.get("category", ""))
    if "みんなの日本語" in category:
        correct_meaning = card["word"]   # 日本語が正解
    else:
        correct_meaning = card["meaning"]  # 日本語訳が正解

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; font-size:0.9rem;"
        "color:#888; margin-bottom:8px;'>"
        f"{T('ta_tap')}</div>",
        unsafe_allow_html=True
    )

    # 2×2 グリッドで4択表示
    row1 = st.columns(2)
    row2 = st.columns(2)
    grid = [row1[0], row1[1], row2[0], row2[1]]

    answered = st.session_state["ta_answered"]

    for i, (col, choice) in enumerate(zip(grid, choices)):
        with col:
            # 回答後の色分け
            if answered:
                if choice == correct_meaning:
                    # 正解選択肢 → 緑ハイライト
                    st.markdown(f"""
                    <div style="background:#00b09b; color:white;
                        border-radius:16px; padding:18px 8px;
                        text-align:center; font-weight:bold;
                        font-size:1rem; min-height:80px;
                        display:flex; align-items:center;
                        justify-content:center;">
                        ✅ {choice}
                    </div>
                    """, unsafe_allow_html=True)
                elif (not st.session_state["ta_correct"]
                      and i == st.session_state.get("ta_selected_idx")):
                    # 自分が選んだ不正解 → 赤ハイライト
                    st.markdown(f"""
                    <div style="background:#ff4b4b; color:white;
                        border-radius:16px; padding:18px 8px;
                        text-align:center; font-weight:bold;
                        font-size:1rem; min-height:80px;
                        display:flex; align-items:center;
                        justify-content:center;">
                        ❌ {choice}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # その他 → グレー
                    st.markdown(f"""
                    <div style="background:#f0f0f0; color:#aaa;
                        border-radius:16px; padding:18px 8px;
                        text-align:center; font-size:1rem;
                        min-height:80px; display:flex;
                        align-items:center; justify-content:center;">
                        {choice}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # 未回答 → 押せるボタン
                if st.button(choice, key=f"ta_choice_{i}",
                             use_container_width=True, type="secondary"):
                    is_correct = (choice == correct_meaning)
                    st.session_state["ta_answered"] = True
                    st.session_state["ta_correct"] = is_correct
                    st.session_state["ta_selected_idx"] = i
                    score = max(0, int(remaining * 10)) if is_correct else 0
                    st.session_state["flash_time_scores"].append({
                        "word": card["word"],
                        "meaning": correct_meaning,
                        "chosen": choice,
                        "time": round(elapsed, 1),
                        "score": score,
                        "result": "correct" if is_correct else "wrong",
                    })
                    quality = 5 if is_correct else 0
                    _record_ta_quality(username, card, quality)
                    st.rerun()

    # ── タイムオーバー処理 ───────────────────
    if remaining <= 0 and not answered:
        st.session_state["ta_answered"] = True
        st.session_state["ta_correct"] = False
        st.session_state["ta_selected_idx"] = -1
        st.session_state["flash_time_scores"].append({
            "word": card["word"],
            "meaning": correct_meaning,
            "chosen": "（時間切れ）",
            "time": 10.0,
            "score": 0,
            "result": "timeout",
        })
        _record_ta_quality(username, card, 0)
        st.rerun()

    # ── 回答済み → 次へボタン ────────────────
    if answered:
        st.markdown(
            f"<div style='text-align:center; font-size:0.9rem;"
            f"color:#666; margin:8px 0;'>"
            f"{T('ta_correct_meaning').format(m=correct_meaning)}</div>",
            unsafe_allow_html=True
        )
        if st.button(T("ta_next"), type="primary",
                     use_container_width=True, key="ta_next"):
            st.session_state["flash_index"] += 1
            st.session_state["flash_show_answer"] = False
            st.session_state["flash_timer_start"] = None
            st.session_state["ta_choices"] = []
            st.session_state["ta_answered"] = False
            st.session_state["ta_correct"] = None
            st.session_state["ta_selected_idx"] = -1
            st.rerun()
    else:
        # 未回答中は自動更新
        time.sleep(0.5)
        st.rerun()


def show_ranking():
    username = st.session_state["flash_user"]
    set_id = st.session_state.get("selected_set_id")
    scores = st.session_state.get("flash_time_scores", [])
    nickname = load_user_nickname(username)

    # スコア集計
    total_score = sum(s["score"] for s in scores)
    correct_count = sum(1 for s in scores if s["result"] == "correct")
    total_cards = len(scores)

    # Supabaseに保存
    if scores and set_id:
        save_ta_score(username, nickname, set_id,
                      total_score, correct_count, total_cards)

    st.markdown("""
    <style>
    .rank-hero {
        background: linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius: 24px; padding: 28px 20px;
        text-align: center; color: white; margin-bottom: 20px;
    }
    .rank-score {
        font-size: 3rem; font-weight: bold;
        background: linear-gradient(135deg,#ffd200,#ff6b6b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .rank-row {
        display: flex; align-items: center;
        padding: 10px 16px; border-radius: 12px;
        margin: 6px 0; font-weight: bold;
    }
    .rank-1 { background: linear-gradient(135deg,#ffd200,#ffbe00); color:#333; }
    .rank-2 { background: #c0c0c0; color: #333; }
    .rank-3 { background: #cd7f32; color: white; }
    .rank-other { background: #f5f5f5; color: #333; }
    </style>
    """, unsafe_allow_html=True)

    # スコア表示
    accuracy = correct_count / total_cards * 100 if total_cards > 0 else 0
    rec_name = nickname if nickname else username
    st.markdown(
        f"""
    <div class="rank-hero">
        <div style="font-size:1rem; opacity:0.7; margin-bottom:4px;">
            {T("rank_ta_result")}
        </div>
        <div class="rank-score">{total_score} pts</div>
        <div style="font-size:1rem; margin-top:8px;">
            {T("rank_score_line").format(c=correct_count, t=total_cards)}
            （{accuracy:.0f}%）
        </div>
        <div style="font-size:0.85rem; opacity:0.7; margin-top:4px;">
            {T("rank_record_as").format(name=rec_name)}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 単語別タイム一覧
    st.markdown(T("rank_word_times"))
    for s in scores:
        icon = "✅" if s["result"] == "correct" else (
                "⏰" if s["result"] == "timeout" else "❌")
        color = "#00b09b" if s["result"] == "correct" else "#ff4b4b"
        st.markdown(
            f'<div style="display:flex; justify-content:space-between;'
            f'padding:8px 12px; background:{color}22; border-radius:10px;'
            f'margin:4px 0; font-size:0.9rem;">'
            f'<span>{icon} <b>{s["word"]}</b> — {s["meaning"]}</span>'
            f'<span style="color:{color}; font-weight:bold;">'
            f'{s["score"]}pts ({s["time"]}秒)</span></div>',
            unsafe_allow_html=True
        )

    # ランキング表示
    st.markdown("---")
    st.markdown(f"### {T('rank_title')}")
    ranking = load_ta_ranking(set_id) if set_id else []
    if not ranking:
        st.info(T("rank_empty"))
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, row in enumerate(ranking):
            medal = medals[i] if i < 3 else f"{i+1}."
            cls = ["rank-1", "rank-2", "rank-3"]
            bg = cls[i] if i < 3 else "rank-other"
            is_me = row["nickname"] == nickname
            me_mark = T("rank_you") if is_me else ""
            st.markdown(
                f'<div class="rank-row {bg}">'
                f'<span style="font-size:1.3rem; margin-right:12px;">{medal}</span>'
                f'<span style="flex:1;">{row["nickname"]}</span>'
                f'<span style="font-size:1.1rem;">{row["total_score"]} pts</span>'
                f'<span style="font-size:0.8rem; margin-left:8px; opacity:0.7;">'
                f'{row["correct_count"]}/{row["total_cards"]}'
                f'{T("rank_q_suffix")}{me_mark}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    # ボタン
    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button(T("ta_again"),
                     use_container_width=True):
            cards = load_flashcards_by_set(set_id)
            if cards:
                random.shuffle(cards)
                st.session_state["flash_queue"] = cards[:10]
                st.session_state["flash_index"] = 0
                st.session_state["flash_show_answer"] = False
                st.session_state["flash_time_scores"] = []
                st.session_state["flash_timer_start"] = None
                st.session_state["flash_mode"] = "time_attack"
                st.rerun()
    with b2:
        if st.button(T("home_btn"),
                     type="primary", use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.session_state["flash_time_scores"] = []
            st.session_state["flash_timer_start"] = None
            st.rerun()


def show_word_list():
    """今日の単語一覧ページ"""
    queue = st.session_state.get("word_list_queue", [])
    username = st.session_state["flash_user"]

    st.markdown(f"## {T('word_list_title')}")
    st.caption(T("word_list_sub"))
    st.markdown(T("word_list_note"))
    st.markdown("---")

    # カテゴリ判定（最初のカードで代表判定）
    category = str(queue[0].get("category", "")) if queue else ""
    is_mnn = "みんなの日本語" in category

    # テーブルヘッダー
    if is_mnn:
        # みんなの日本語：中国語→日本語
        header_cols = st.columns([1, 3, 3, 3])
        header_cols[0].markdown(f"**{T('word_list_no')}**")
        header_cols[1].markdown("**中国語（問題）**")
        header_cols[2].markdown(f"**{T('word_list_word')}（答え）**")
        header_cols[3].markdown(f"**{T('word_list_reading')}**")
    else:
        # 英検：英語→日本語
        header_cols = st.columns([1, 3, 3, 3])
        header_cols[0].markdown(f"**{T('word_list_no')}**")
        header_cols[1].markdown(f"**{T('word_list_word')}**")
        header_cols[2].markdown(f"**{T('word_list_meaning')}**")
        header_cols[3].markdown("**発音 / 読み**")

    st.markdown("<hr style='margin:4px 0 8px 0;'>", unsafe_allow_html=True)

    # 単語行
    for i, card in enumerate(queue):
        row_bg = "#f8f9ff" if i % 2 == 0 else "#ffffff"
        cols = st.columns([1, 3, 3, 3])

        if is_mnn:
            meaning_zh = card.get("meaning", "")    # 中国語（問題）
            word       = card.get("word", "")        # 日本語（答え）
            reading    = card.get("reading", "")
            accent     = card.get("phonetic", "")
            reading_str = f"{reading}　{accent}" if accent else reading

            cols[0].markdown(
                f"<div style='background:{row_bg};padding:6px 4px;"
                f"border-radius:8px;text-align:center;color:#888;"
                f"font-size:0.85rem;'>{i+1}</div>",
                unsafe_allow_html=True
            )
            cols[1].markdown(
                f"<div style='background:{row_bg};padding:6px 8px;"
                f"border-radius:8px;font-weight:bold;color:#e05a00;"
                f"font-size:1rem;'>{meaning_zh}</div>",
                unsafe_allow_html=True
            )
            cols[2].markdown(
                f"<div style='background:{row_bg};padding:6px 8px;"
                f"border-radius:8px;font-weight:bold;color:#1a1a1a;"
                f"font-size:1rem;'>{word}</div>",
                unsafe_allow_html=True
            )
            cols[3].markdown(
                f"<div style='background:{row_bg};padding:6px 8px;"
                f"border-radius:8px;color:#555;font-size:0.9rem;'>"
                f"{reading_str}</div>",
                unsafe_allow_html=True
            )
        else:
            word     = card.get("word", "")
            meaning  = card.get("meaning", "")
            phonetic = card.get("phonetic", "")
            reading  = card.get("reading", "")
            sub_str  = phonetic if phonetic else reading

            cols[0].markdown(
                f"<div style='background:{row_bg};padding:6px 4px;"
                f"border-radius:8px;text-align:center;color:#888;"
                f"font-size:0.85rem;'>{i+1}</div>",
                unsafe_allow_html=True
            )
            cols[1].markdown(
                f"<div style='background:{row_bg};padding:6px 8px;"
                f"border-radius:8px;font-weight:bold;color:#1a1a1a;"
                f"font-size:1.05rem;'>{word}</div>",
                unsafe_allow_html=True
            )
            cols[2].markdown(
                f"<div style='background:{row_bg};padding:6px 8px;"
                f"border-radius:8px;font-weight:bold;color:#333;"
                f"font-size:1rem;'>{meaning}</div>",
                unsafe_allow_html=True
            )
            cols[3].markdown(
                f"<div style='background:{row_bg};padding:6px 8px;"
                f"border-radius:8px;color:#777;font-size:0.85rem;'>"
                f"{sub_str}</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ボタン
    col_back, col_start = st.columns([1, 2])
    with col_back:
        if st.button(T("word_list_back"), use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.rerun()
    with col_start:
        if st.button(T("word_list_start"), type="primary",
                     use_container_width=True):
            st.session_state["flash_mode"] = "study"
            st.rerun()


def show_result():
    results = st.session_state["flash_session_results"]
    username = st.session_state["flash_user"]

    st.title(T("result_title"))

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
        title_text = T("result_hero_100_title")
        sub_text = T("result_hero_100_sub")
    elif accuracy >= 80:
        title_text = T("result_hero_80_title")
        sub_text = T("result_hero_80_sub").format(a=accuracy)
    elif accuracy >= 50:
        title_text = T("result_hero_50_title")
        sub_text = T("result_hero_50_sub").format(a=accuracy)
    else:
        title_text = T("result_hero_low_title")
        sub_text = T("result_hero_low_sub").format(a=accuracy)

    st.markdown(
        f"""
    <div class="result-hero">
        <div class="result-title">{title_text}</div>
        <div class="result-sub">{sub_text}</div>
        <div class="xp-badge">{T("xp_get").format(xp=session_xp)}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── 4指標カード（1行）────────────────────
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, T("perfect_lbl"), len(perfect), "#667eea"),
        (c2, T("good_lbl"), len(good), "#00b09b"),
        (c3, T("ok_lbl"), len(ok), "#ffa500"),
        (c4, T("ng_lbl"), len(ng), "#ff4b4b"),
    ]
    for col, label, count, color in stats:
        with col:
            st.markdown(
                f"""
            <div class="stat-card" style="background:{color};">
                <div style="font-size:1.5rem;">{count}{T("cards")}</div>
                <div style="font-size:0.78rem; margin-top:4px;">{label}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── レベル・XPバー ───────────────────────
    st.markdown("---")
    st.markdown(f"### 🎮 Lv.{level} — {T('total_xp_lbl')} {total_xp} XP")
    st.markdown(
        f"""
    <div class="level-bar-wrap">
        <div class="level-bar-fill" style="width:{int(lv_progress*100)}%;"></div>
    </div>
    <div style="font-size:0.78rem; color:#888; text-align:right;">
        {T("next_lv")} {int((1-lv_progress)*100)}%
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── 単語別結果（ピル表示）────────────────
    st.markdown("---")
    st.markdown(T("summary_title"))

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**{T('words_done')}**")
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
            st.caption(T("no_words_yet"))

    with col_b:
        st.markdown(f"**{T('words_retry')}**")
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
            st.caption(T("none_perfect"))

    # ── 次回復習日の予告 ─────────────────────
    if ng:
        st.markdown("---")
        st.info(
            f"💡 **{len(ng)}{T('cards')}**{T('ng_notice_tail')}"
        )

    # ── 成長グラフ ───────────────────────────
    st.markdown("---")
    st.markdown(f"### {T('graph_title')}")

    daily_stats = load_daily_stats(username)
    cum_stats = load_cumulative_xp(username)

    # 学習があった日だけ抽出
    active_days = [d for d in daily_stats if d["cards"] > 0]

    if len(active_days) < 2:
        st.info(T("graph_need_days"))
    else:
        tab1, tab2, tab3 = st.tabs([T("tab_xp"), T("tab_cards"), T("tab_acc")])

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
                name=T("chart_cum_xp_name"),
                hovertemplate="%{x}<br>"
                + T("chart_cum_xp_name")
                + ": %{y}<extra></extra>",
            ))
            fig1.update_layout(
                title=T("chart_cum_xp_title"),
                xaxis_title=T("chart_date"),
                yaxis_title=T("chart_cum_xp_name"),
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="sans-serif", size=12),
                margin=dict(l=40, r=20, t=40, b=40),
                hovermode="x unified",
            )
            st.plotly_chart(fig1, use_container_width=True)
            # 総合コメント
            total_active = len(active_days)
            st.caption(T("study_days_caption").format(n=total_active))

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
                hovertemplate="%{x}<br>"
                + T("chart_daily_cards_name")
                + ": %{y}<extra></extra>",
                name=T("chart_daily_cards_name"),
            ))
            fig2.update_layout(
                title=T("chart_daily_cards_title"),
                xaxis_title=T("chart_date"),
                yaxis_title=T("chart_count_axis"),
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(family="sans-serif", size=12),
                margin=dict(l=40, r=20, t=40, b=40),
            )
            st.plotly_chart(fig2, use_container_width=True)
            max_day = df_daily.loc[df_daily["cards"].idxmax()]
            if max_day["cards"] > 0:
                st.caption(
                    T("max_day_caption").format(
                        d=max_day["date"], n=int(max_day["cards"])
                    )
                )

        # ── Tab3: 日別正解率折れ線グラフ ──────
        with tab3:
            df_acc = pd.DataFrame([
                d for d in daily_stats
                if d["accuracy"] is not None
            ])
            if df_acc.empty:
                st.info(T("acc_no_data"))
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
                    name=T("chart_acc_name"),
                    hovertemplate="%{x}<br>"
                    + T("chart_acc_name")
                    + ": %{y:.1f}%<extra></extra>",
                ))
                # 80%ラインを点線で追加
                fig3.add_hline(
                    y=80,
                    line_dash="dot",
                    line_color="#ffa500",
                    annotation_text=T("target_80"),
                    annotation_position="bottom right",
                )
                fig3.update_layout(
                    title=T("chart_acc_title"),
                    xaxis_title=T("chart_date"),
                    yaxis_title=T("chart_acc_yaxis"),
                    yaxis_range=[0, 105],
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="sans-serif", size=12),
                    margin=dict(l=40, r=20, t=40, b=40),
                )
                st.plotly_chart(fig3, use_container_width=True)
                avg_acc = df_acc["accuracy"].mean()
                st.caption(T("avg_acc_caption").format(a=avg_acc))

    # ── アクションボタン ─────────────────────
    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button(T("home_btn"), type="primary", use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.session_state["flash_session_results"] = []
            st.rerun()
    with b2:
        if st.button(T("retry_btn"), use_container_width=True):
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
elif mode == "word_list":
    show_word_list()
elif mode == "study":
    show_study(username)
elif mode == "time_attack":
    show_time_attack(username)
elif mode == "ranking":
    show_ranking()
elif mode == "result":
    show_result()
