# flash_app.py 窶・譛ｪ譚･蝪ｾ 蜊倩ｪ樊囓險倥い繝励Μ・・M-2蠢伜唆譖ｲ邱夲ｼ画隼險ら沿
import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import date, timedelta

TRANSLATIONS = {
    "ja": {
        "app_title": "当 蜊倩ｪ樊囓險倥い繝励Μ | 譛ｪ譚･蝪ｾ",
        "select_user": "繝ｦ繝ｼ繧ｶ繝ｼ繧帝∈繧薙〒縺上□縺輔＞",
        "start": "繧ｹ繧ｿ繝ｼ繝茨ｼ・,
        "no_user": "繝ｦ繝ｼ繧ｶ繝ｼ縺檎匳骭ｲ縺輔ｌ縺ｦ縺・∪縺帙ｓ縲らｮ｡逅・・↓騾｣邨｡縺励※縺上□縺輔＞縲・,
        "select_prompt": "--- 驕ｸ繧薙〒縺上□縺輔＞ ---",
        "select_error": "繝ｦ繝ｼ繧ｶ繝ｼ繧帝∈繧薙〒縺上□縺輔＞",
        "welcome": "縺輔ｓ・∽ｻ頑律繧ゅ＞縺｣縺励ｇ縺ｫ隕壹∴繧医≧・・,
        "streak_msg": "譌･騾｣邯壼ｭｦ鄙剃ｸｭ・√☆縺斐＞・・,
        "streak_zero": "当 縺輔≠縲∽ｻ頑律縺九ｉ蟋九ａ繧医≧・・,
        "select_material": "答 謨呎攝繧帝∈縺ｶ",
        "no_material": "謨呎攝縺後∪縺逋ｻ骭ｲ縺輔ｌ縺ｦ縺・∪縺帙ｓ縲らｮ｡逅・・↓騾｣邨｡縺励※縺上□縺輔＞縲・,
        "material_label": "謨呎攝",
        "no_cards_set": "縺薙・謨呎攝縺ｫ縺ｯ縺ｾ縺蜊倩ｪ槭′逋ｻ骭ｲ縺輔ｌ縺ｦ縺・∪縺帙ｓ縲・,
        "page_range": "当 繝壹・繧ｸ遽・峇:",
        "item_range": "箸",
        "progress_caption": "譫壹け繝ｪ繧｢",
        "today_task": "統 莉頑律繧・ｋ縺薙→",
        "badge_new": "・ 譁ｰ縺励＞蜊倩ｪ・,
        "badge_due": "煤 蠕ｩ鄙偵′蠢・ｦ・,
        "cards": "譫・,
        "start_study": "笨ｨ 莉頑律縺ｮ蟄ｦ鄙偵ｒ縺ｯ縺倥ａ繧具ｼ・,
        "all_done": "脂 莉頑律縺ｮ蛻・・蜈ｨ驛ｨ邨ゅｏ縺｣縺滂ｼ√∪縺滓・譌･・・,
        "more_study": "検 繧ゅ▲縺ｨ繧・ｊ縺溘＞莠ｺ縺ｯ縺薙％縺九ｉ・・,
        "current_title": "迴ｾ蝨ｨ縺ｮ遘ｰ蜿ｷ",
        "total_xp_lbl": "邏ｯ險・,
        "weak_btn": "煤 闍ｦ謇九□縺大ｾｩ鄙箪n\n遲斐∴縺悟・縺ｪ縺九▲縺歃n蜊倩ｪ槭ｒ繧ゅ≧荳蠎ｦ",
        "new_btn": "噫 蜈亥叙繧翫メ繝｣繝ｬ繝ｳ繧ｸ\n\n縺ｾ縺隕九※縺・↑縺Ыn譁ｰ縺励＞蜊倩ｪ槭∈",
        "all_btn": "識 蜈ｨ驛ｨ騾壹＠蠕ｩ鄙箪n\n謨呎攝縺ｮ蜈ｨ蜊倩ｪ槭ｒ\n繧ｷ繝｣繝・ヵ繝ｫ縺ｧ",
        "ta_btn": "笞｡ 繧ｿ繧､繝繧｢繧ｿ繝・け・―n\n10遘偵〒遲斐∴繧搾ｼ―n繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ縺ｫ謖第姶",
        "logout": "坎 繝ｭ繧ｰ繧｢繧ｦ繝・,
        "think_hint": "眺 諢丞袖繧帝ｭ縺ｫ諤昴＞豬ｮ縺九∋縺ｦ縺九ｉ謚ｼ縺励※縺ｭ",
        "show_answer": "操 遲斐∴繧定ｦ九ｋ",
        "reading_label": "矧 隱ｭ縺ｿ・・,
        "reading_jp_lbl": "隱ｭ縺ｿ・・,
        "phonetic_label": "筈 逋ｺ髻ｳ・・,
        "zh_meaning_label": "・・ 荳ｭ譁・ｼ・,
        "example_lbl": "統 萓区枚: ",
        "how_much": "縺ｩ縺ｮ縺上ｉ縺・ｦ壹∴縺ｦ縺・◆・・,
        "q0_btn": "笶圭n蜈ｨ辟ｶ繝繝｡\n\n遲斐∴縺圭n蜃ｺ縺ｦ縺薙↑縺九▲縺・,
        "q3_btn": "噺\n縺・▲縺吶ｉ\n\n諤昴＞蜃ｺ縺吶・縺ｫ\n譎る俣縺後°縺九▲縺・,
        "q4_btn": "泙\n縺縺・◆縺Ыn\n縺吶＄蜃ｺ縺溘′\n蟆代＠荳榊ｮ峨□縺｣縺・,
        "q5_btn": "箝申n繝舌ャ繝√Μ・―n\n荳迸ｬ縺ｧ\n螳悟・縺ｫ閾ｪ菫｡縺ゅｊ",
        "next_day": "谺｡蝗・ 譏取律",
        "next_6d": "谺｡蝗・ 6譌･蠕・,
        "next_weeks": "谺｡蝗・ 謨ｰ騾ｱ髢灘ｾ・,
        "next_month": "谺｡蝗・ 1繝ｶ譛井ｻ･荳・,
        "legend_bad": "笶・蜈ｨ辟ｶ繝繝｡",
        "legend_good": "箝・繝舌ャ繝√Μ・・,
        "result_title": "脂 莉頑律縺ｮ蟄ｦ鄙貞ｮ御ｺ・ｼ・,
        "perfect_lbl": "識 繝舌ャ繝√Μ",
        "good_lbl": "泙 縺縺・◆縺・,
        "ok_lbl": "噺 縺・▲縺吶ｉ",
        "ng_lbl": "笶・隕∝ｾｩ鄙・,
        "lv_label": "式 邏ｯ險・,
        "next_lv": "谺｡縺ｮ繝ｬ繝吶Ν縺ｾ縺ｧ",
        "words_done": "笨・隕壹∴繧峨ｌ縺溷腰隱・,
        "words_retry": "煤 谺｡蝗槭∪縺滓倦謌ｦ",
        "ng_notice_tail": "縺ｯ譏取律縺ｾ縺溷・縺ｦ縺阪∪縺吶ょ､ｧ荳亥､ｫ縲∫ｹｰ繧願ｿ斐☆縺薙→縺ｧ蠢・★隕壹∴繧峨ｌ縺ｾ縺呻ｼ・,
        "home_btn": "匠 繝帙・繝縺ｸ謌ｻ繧・,
        "retry_btn": "煤 繧ゅ≧荳蠎ｦ繝√Ε繝ｬ繝ｳ繧ｸ",
        "graph_title": "嶋 縺ゅ↑縺溘・謌宣聞繧ｰ繝ｩ繝・,
        "tab_xp": "笞｡ XP謗ｨ遘ｻ",
        "tab_cards": "答 蟄ｦ鄙呈椢謨ｰ",
        "tab_acc": "識 豁｣隗｣邇・,
        "lang_switch": "・・ 蛻・困荳ｭ譁・,
        "nickname_label": "式 繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ繝阪・繝:",
        "nick_title": "### 式 繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ逕ｨ繝阪・繝繧呈ｱｺ繧√ｈ縺・ｼ・,
        "nick_box1": "銅 縺ｪ縺ｾ縺医ｒ 縺・ｌ縺ｦ縺上□縺輔＞",
        "nick_box2": "繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ縺ｫ陦ｨ遉ｺ縺輔ｌ繧句錐蜑阪〒縺吶よ悽蜷阪・菴ｿ繧上↑縺・〒縺ｭ・・,
        "nick_field": "繝九ャ繧ｯ繝阪・繝・・縲・譁・ｭ暦ｼ・,
        "nick_placeholder": "萓・ 縺溘ｓ縺斐・繧ｹ繧ｿ繝ｼ",
        "nick_submit": "笞｡ 縺薙ｌ縺ｧ豎ｺ螳夲ｼ・,
        "nick_err": "2譁・ｭ嶺ｻ･荳翫〒蜈･蜉帙＠縺ｦ縺上□縺輔＞",
        "nick_ok": "脂縲鶏nick}縲阪↓豎ｺ螳夲ｼ√Λ繝ｳ繧ｭ繝ｳ繧ｰ縺ｫ蜿よ姶縺ｧ縺阪∪縺呻ｼ・,
        "nick_caption": "式 繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ繝阪・繝: **{nick}**縲[螟画峩縺吶ｋ蝣ｴ蜷医・繝ｭ繧ｰ繧｢繧ｦ繝亥ｾ後↓險ｭ螳咯",
        "weak_ok": "脂 闍ｦ謇九↑蜊倩ｪ槭・縺ゅｊ縺ｾ縺帙ｓ・・,
        "new_ok": "醇 蜈ｨ蜊倩ｪ槫宛隕・ｼ√☆縺斐＞・・,
        "daily_7": "検 7譌･騾｣邯夐＃謌撰ｼ々Pﾃ・繝懊・繝翫せ迯ｲ蠕嶺ｸｭ・・,
        "daily_3": "櫨 {s}譌･騾｣邯夲ｼ√≠縺ｨ{r}譌･縺ｧ7譌･騾｣邯壹・繝ｼ繝翫せ・・,
        "daily_0": "庁 豈取律邯壹￠繧九→7譌･騾｣邯壹・繝ｼ繝翫せXPﾃ・縺瑚ｧ｣謾ｾ縺輔ｌ縺ｾ縺呻ｼ・,
        "interrupt_btn": "竢ｸ・・縺・▲縺溘ｓ荳ｭ譁ｭ縺励※繝帙・繝縺ｸ謌ｻ繧・,
        "progress_n": "{i} / {t} 譫夂岼",
        "ta_question": "眺 豁｣縺励＞諢丞袖縺ｯ縺ｩ繧鯉ｼ・,
        "ta_tap": "燥 豁｣縺励＞諢丞袖繧偵ち繝・・・・,
        "ta_next": "筐｡・・谺｡縺ｮ蝠城｡後∈",
        "rank_title": "醇 縺ｿ繧薙↑縺ｮ繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ・・OP10・・,
        "rank_empty": "縺ｾ縺險倬鹸縺後≠繧翫∪縺帙ｓ縲ゅ≠縺ｪ縺溘′1菴阪↓縺ｪ繧阪≧・・,
        "ta_again": "煤 繧ゅ≧荳蠎ｦ繧ｿ繧､繝繧｢繧ｿ繝・け",
        "score_save_err": "繧ｹ繧ｳ繧｢菫晏ｭ倥お繝ｩ繝ｼ: ",
        "graph_need_days": "投 繧ｰ繝ｩ繝輔・2譌･莉･荳雁ｭｦ鄙偵☆繧九→陦ｨ遉ｺ縺輔ｌ縺ｾ縺呻ｼ∵・譌･繧よ擂縺ｦ縺ｭ 櫨",
        "acc_no_data": "豁｣隗｣邇・ョ繝ｼ繧ｿ縺後≠繧翫∪縺帙ｓ",
        "study_days_caption": "櫨 驕主悉30譌･縺ｧ **{n}譌･** 蟄ｦ鄙偵＠縺ｾ縺励◆・・,
        "max_day_caption": "遵 譛螟壼ｭｦ鄙呈律: **{d}** ({n}譫・",
        "avg_acc_caption": "投 驕主悉30譌･縺ｮ蟷ｳ蝮・ｭ｣隗｣邇・ **{a:.1f}%**",
        "target_80": "逶ｮ讓・80%",
        "result_hero_100_title": "醇 繝代・繝輔ぉ繧ｯ繝茨ｼ・ｼ・,
        "result_hero_100_sub": "蜈ｨ蝠乗ｭ｣隗｣・∝ｮ檎挑縺ｪ蟄ｦ鄙偵〒縺励◆・・,
        "result_hero_80_title": "脂 邏譎ｴ繧峨＠縺・ｼ・,
        "result_hero_80_sub": "豁｣隗｣邇・{a:.0f}% 窶・縺薙・隱ｿ蟄舌〒邯壹￠繧医≧・・,
        "result_hero_50_title": "潮 繧医￥鬆大ｼｵ縺｣縺滂ｼ・,
        "result_hero_50_sub": "豁｣隗｣邇・{a:.0f}% 窶・蠕ｩ鄙偵〒蟾ｮ繧偵▽縺代ｈ縺・ｼ・,
        "result_hero_low_title": "当 莉頑律縺ｯ縺薙％縺九ｉ・・,
        "result_hero_low_sub": "豁｣隗｣邇・{a:.0f}% 窶・郢ｰ繧願ｿ斐○縺ｰ蠢・★隕壹∴繧峨ｌ繧具ｼ・,
        "xp_get": "笞｡ +{xp} XP 繧ｲ繝・ヨ・・,
        "summary_title": "### 搭 莉頑律縺ｮ蜊倩ｪ槭∪縺ｨ繧・,
        "no_words_yet": "縺ｾ縺縺ゅｊ縺ｾ縺帙ｓ",
        "none_perfect": "縺ｪ縺暦ｼ∝ｮ檎挑縺ｧ縺・脂",
        "chart_cum_xp_name": "邏ｯ險・P",
        "chart_cum_xp_title": "邏ｯ險・P縺ｮ謗ｨ遘ｻ・磯℃蜴ｻ30譌･・・,
        "chart_date": "譌･莉・,
        "chart_daily_cards_name": "蟄ｦ鄙呈椢謨ｰ",
        "chart_daily_cards_title": "譌･蛻･ 蟄ｦ鄙呈椢謨ｰ・磯℃蜴ｻ30譌･・・,
        "chart_count_axis": "譫壽焚",
        "chart_acc_name": "豁｣隗｣邇・,
        "chart_acc_title": "譌･蛻･ 豁｣隗｣邇・ｼ磯℃蜴ｻ30譌･・・,
        "chart_acc_yaxis": "豁｣隗｣邇・(%)",
        "ta_header": "笞｡ 繧ｿ繧､繝繧｢繧ｿ繝・け {i}/{t}",
        "ta_reading": "隱ｭ縺ｿ: {r}",
        "ta_correct": "笨・豁｣隗｣・・,
        "ta_wrong": "笶・荳肴ｭ｣隗｣",
        "ta_seconds": "竢ｱ {s:.1f}遘・,
        "ta_correct_meaning": "豁｣隗｣: <b>{m}</b>",
        "rank_ta_result": "笞｡ 繧ｿ繧､繝繧｢繧ｿ繝・け邨先棡",
        "rank_score_line": "{c}/{t}蝠乗ｭ｣隗｣",
        "rank_record_as": "式 {name} 縺ｨ縺励※險倬鹸",
        "rank_word_times": "### 竢ｱ・・蜊倩ｪ槫挨繧ｿ繧､繝",
        "rank_you": " 争 縺ゅ↑縺・,
        "rank_q_suffix": "蝠・,
        "word_list_title": "搭 莉頑律縺ｮ蜊倩ｪ槭Μ繧ｹ繝・,
        "word_list_sub": "縺ｾ縺壹％縺ｮ蜊倩ｪ槭ｒ隕壹∴縺ｦ縺九ｉ縲√メ繧ｧ繝・け縺ｫ騾ｲ繧ゅ≧・・,
        "word_list_no": "No.",
        "word_list_word": "蜊倩ｪ・,
        "word_list_reading": "隱ｭ縺ｿ",
        "word_list_meaning": "諢丞袖",
        "word_list_start": "笨・隕壹∴縺滂ｼ∝腰隱槭メ繧ｧ繝・け繧偵・縺倥ａ繧・,
        "word_list_back": "匠 繝帙・繝縺ｫ謌ｻ繧・,
        "word_list_note": "庁 繝弱・繝医↓譖ｸ縺・※隕壹∴繧九→縺阪・縺薙・繝ｪ繧ｹ繝医ｒ隕九↑縺後ｉ邱ｴ鄙偵＠繧医≧・・,
    },
    "zh": {
        "app_title": "当 蜊戊ｯ崎ｮｰ蠢・| 譛ｪ譚･蝪ｾ",
        "select_user": "隸ｷ騾画叫逕ｨ謌ｷ",
        "start": "蠑蟋具ｼ・,
        "no_user": "霑俶ｲ｡譛画ｳｨ蜀檎畑謌ｷ・瑚ｯｷ閨皮ｳｻ邂｡逅・遭縲・,
        "select_prompt": "--- 隸ｷ騾画叫 ---",
        "select_error": "隸ｷ騾画叫逕ｨ謌ｷ",
        "welcome": "蜷悟ｭｦ・∵・莉ｬ荳襍ｷ譚･隶ｰ蜊戊ｯ榊制・・,
        "streak_msg": "螟ｩ霑樒ｻｭ蟄ｦ荵・∝､ｪ蜴牙ｮｳ莠・ｼ・,
        "streak_zero": "当 莉雁､ｩ蠑蟋句ｭｦ荵蜷ｧ・・,
        "select_material": "答 騾画叫謨呎攝",
        "no_material": "霑俶ｲ｡譛画蕗譚撰ｼ瑚ｯｷ閨皮ｳｻ邂｡逅・遭縲・,
        "material_label": "謨呎攝",
        "no_cards_set": "譛ｬ謨呎攝證よ裏蜊戊ｯ阪・,
        "page_range": "当 鬘ｵ遐∬激蝗ｴ:",
        "item_range": "箸",
        "progress_caption": "荳ｪ蟾ｲ謗梧升",
        "today_task": "統 莉頑律莉ｻ蜉｡",
        "badge_new": "・ 譁ｰ蜊戊ｯ・,
        "badge_due": "煤 髴隕∝､堺ｹ",
        "cards": "荳ｪ",
        "start_study": "笨ｨ 蠑蟋倶ｻ雁､ｩ逧・ｭｦ荵・・,
        "all_done": "脂 莉雁､ｩ逧・ｻｻ蜉｡蜈ｨ驛ｨ螳梧・・∵・螟ｩ隗・ｼ・,
        "more_study": "検 諠ｳ扈ｧ扈ｭ蟄ｦ荵逧・酔蟄ｦ逵玖ｿ咎㈹・・,
        "current_title": "蠖灘燕遘ｰ蜿ｷ",
        "total_xp_lbl": "邏ｯ隶｡",
        "weak_btn": "煤 螟堺ｹ蠑ｱ鬘ｹ\n\n蜀咲ｻ・ｸ谺｡\n豐｡隶ｰ菴冗噪蜊戊ｯ・,
        "new_btn": "噫 謠仙燕謖第・\n\n蟄ｦ荵譁ｰ逧Ыn譛ｪ隗∬ｿ・噪蜊戊ｯ・,
        "all_btn": "識 蜈ｨ驛ｨ螟堺ｹ\n\n髫乗惻鬘ｺ蠎十n螟堺ｹ謇譛牙黒隸・,
        "ta_btn": "笞｡ 髯先慮謖第・・―n\n10遘貞・菴懃ｭ費ｼ―n謖第・謗定｡梧ｦ・,
        "logout": "坎 騾蜃ｺ逋ｻ蠖・,
        "think_hint": "眺 蜈亥惠閼台ｸｭ諠ｳ諠ｳ諢乗晢ｼ悟・謖画潔髓ｮ",
        "show_answer": "操 譟･逵狗ｭ疲｡・,
        "reading_label": "矧 隸ｻ髻ｳ・・,
        "reading_jp_lbl": "隸ｻ髻ｳ・・,
        "phonetic_label": "筈 蜿鷹浹・・,
        "zh_meaning_label": "・・ 荳ｭ譁・ｼ・,
        "example_lbl": "統 萓句唱・・,
        "how_much": "菴隶ｰ蠕怜､壼ｰ托ｼ・,
        "q0_btn": "笶圭n螳悟・荳堺ｼ喀n\n螳悟・\n諠ｳ荳崎ｵｷ譚･",
        "q3_btn": "噺\n譛臥せ蜊ｰ雎｡\n\n諠ｳ襍ｷ譚･莠・n菴・干莠・慮髣ｴ",
        "q4_btn": "泙\n螟ｧ菴楢ｮｰ蠕予n\n蠕亥ｿｫ諠ｳ襍ｷ\n菴・ｸ榊､ｪ遑ｮ螳・,
        "q5_btn": "箝申n螳悟・隶ｰ菴擾ｼ―n\n迸ｬ髣ｴ遲泌・\n螳悟・譛画滑謠｡",
        "next_day": "荳区ｬ｡・壽・螟ｩ",
        "next_6d": "荳区ｬ｡・・螟ｩ蜷・,
        "next_weeks": "荳区ｬ｡・壽焚蜻ｨ蜷・,
        "next_month": "荳区ｬ｡・・荳ｪ譛井ｻ･荳・,
        "legend_bad": "笶・螳悟・荳堺ｼ・,
        "legend_good": "箝・螳檎ｾ趣ｼ・,
        "result_title": "脂 莉雁､ｩ逧・ｭｦ荵螳梧・・・,
        "perfect_lbl": "識 螳檎ｾ・,
        "good_lbl": "泙 螟ｧ菴楢ｮｰ菴・,
        "ok_lbl": "噺 譛臥せ蜊ｰ雎｡",
        "ng_lbl": "笶・髴螟堺ｹ",
        "lv_label": "式 邏ｯ隶｡",
        "next_lv": "霍晉ｦｻ荳倶ｸ郤ｧ",
        "words_done": "笨・蟾ｲ隶ｰ菴冗噪蜊戊ｯ・,
        "words_retry": "煤 荳区ｬ｡蜀肴倦謌・,
        "ng_notice_tail": "蜊戊ｯ肴・螟ｩ霑倅ｼ壼・邇ｰ縲ょ渚螟咲ｻ・ｹ荳螳夊・隶ｰ菴擾ｼ・,
        "home_btn": "匠 霑泌屓鬥夜｡ｵ",
        "retry_btn": "煤 蜀肴倦謌倅ｸ谺｡",
        "graph_title": "嶋 菴逧・・髟ｿ蝗ｾ陦ｨ",
        "tab_xp": "笞｡ XP蜿伜喧",
        "tab_cards": "答 蟄ｦ荵謨ｰ驥・,
        "tab_acc": "識 豁｣遑ｮ邇・,
        "lang_switch": "・・ 蛻・困譌･譛ｬ隱・,
        "nickname_label": "式 謗定｡梧ｦ懷錐遘ｰ:",
        "nick_title": "### 式 隶ｾ鄂ｮ謗定｡梧ｦ懈亰遘ｰ",
        "nick_box1": "銅 隸ｷ霎灘・譏ｵ遘ｰ",
        "nick_box2": "蟆・仞遉ｺ蝨ｨ謗定｡梧ｦ應ｸ奇ｼ瑚ｯｷ蜍ｿ菴ｿ逕ｨ逵溷ｮ槫ｧ灘錐・・,
        "nick_field": "譏ｵ遘ｰ・・縲・蟄暦ｼ・,
        "nick_placeholder": "萓具ｼ壼黒隸崎ｾｾ莠ｺ",
        "nick_submit": "笞｡ 遑ｮ螳夲ｼ・,
        "nick_err": "隸ｷ霎灘・閾ｳ蟆・荳ｪ蟄・,
        "nick_ok": "脂縲鶏nick}縲榊ｷｲ遑ｮ螳夲ｼ∝庄莉･蜿ょ刈謗定｡梧ｦ應ｺ・ｼ・,
        "nick_caption": "式 謗定｡梧ｦ懷錐遘ｰ: **{nick}**縲[菫ｮ謾ｹ隸ｷ騾蜃ｺ蜷手ｮｾ鄂ｮ]",
        "weak_ok": "脂 豐｡譛芽埋蠑ｱ蜊戊ｯ搾ｼ・,
        "new_ok": "醇 蜈ｨ驛ｨ蜊戊ｯ榊ｷｲ謗梧升・∝､ｪ譽剃ｺ・ｼ・,
        "daily_7": "検 霑樒ｻｭ7螟ｩ霎ｾ謌撰ｼ々Pﾃ・螂門干荳ｭ・・,
        "daily_3": "櫨 蟾ｲ霑樒ｻｭ{s}螟ｩ・∝・霑・r}螟ｩ隗｣髞・螟ｩ螂門干・・,
        "daily_0": "庁 豈丞､ｩ蝮壽戟蜿ｯ隗｣髞∬ｿ樒ｻｭ7螟ｩXPﾃ・螂門干・・,
        "interrupt_btn": "竢ｸ・・證ょ●蟷ｶ霑泌屓鬥夜｡ｵ",
        "progress_n": "{i} / {t} 鬚・,
        "ta_question": "眺 豁｣遑ｮ逧・э諤晄弍蜩ｪ荳ｪ・・,
        "ta_tap": "燥 轤ｹ蜃ｻ豁｣遑ｮ逧・э諤晢ｼ・,
        "ta_next": "筐｡・・荳倶ｸ鬚・,
        "rank_title": "醇 謗定｡梧ｦ懶ｼ・OP10・・,
        "rank_empty": "霑俶ｲ｡譛芽ｮｰ蠖包ｼ梧擂蠖鍋ｬｬ荳蜷ｧ・・,
        "ta_again": "煤 蜀肴擂荳谺｡髯先慮",
        "score_save_err": "菫晏ｭ伜・謨ｰ蜃ｺ髞呻ｼ・,
        "graph_need_days": "投 蟄ｦ荵貊｡2螟ｩ蜊ｳ蜿ｯ譏ｾ遉ｺ蝗ｾ陦ｨ・∵・螟ｩ蜀肴擂蜩ｦ 櫨",
        "acc_no_data": "證よ裏豁｣遑ｮ邇・焚謐ｮ",
        "study_days_caption": "櫨 霑・悉30螟ｩ蜈ｱ蟄ｦ荵 **{n}螟ｩ**・・,
        "max_day_caption": "遵 蟄ｦ荵譛螟夂噪荳螟ｩ: **{d}** ({n}荳ｪ)",
        "avg_acc_caption": "投 霑・悉30螟ｩ蟷ｳ蝮・ｭ｣遑ｮ邇・ **{a:.1f}%**",
        "target_80": "逶ｮ譬・80%",
        "result_hero_100_title": "醇 蜈ｨ蟇ｹ・・ｼ・,
        "result_hero_100_sub": "蜈ｨ驛ｨ遲泌ｯｹ・∝､ｪ譽剃ｺ・ｼ・,
        "result_hero_80_title": "脂 螟ｪ譽剃ｺ・ｼ・,
        "result_hero_80_sub": "豁｣遑ｮ邇・{a:.0f}% 窶・扈ｧ扈ｭ菫晄戟・・,
        "result_hero_50_title": "潮 蜉豐ｹ・・,
        "result_hero_50_sub": "豁｣遑ｮ邇・{a:.0f}% 窶・螟堺ｹ荳荳倶ｼ壽峩螂ｽ・・,
        "result_hero_low_title": "当 莉手ｿ咎㈹蠑蟋具ｼ・,
        "result_hero_low_sub": "豁｣遑ｮ邇・{a:.0f}% 窶・螟夂ｻ・ｸ螳夊・隶ｰ菴擾ｼ・,
        "xp_get": "笞｡ +{xp} XP 闔ｷ蠕暦ｼ・,
        "summary_title": "### 搭 莉頑律蜊戊ｯ肴ｱ・ｻ",
        "no_words_yet": "霑俶ｲ｡譛・,
        "none_perfect": "豐｡譛会ｼ∝・蟇ｹ 脂",
        "chart_cum_xp_name": "邏ｯ隶｡XP",
        "chart_cum_xp_title": "邏ｯ隶｡XP蜿伜喧・郁ｿ・悉30螟ｩ・・,
        "chart_date": "譌･譛・,
        "chart_daily_cards_name": "蟄ｦ荵謨ｰ驥・,
        "chart_daily_cards_title": "豈乗律蟄ｦ荵謨ｰ驥擾ｼ郁ｿ・悉30螟ｩ・・,
        "chart_count_axis": "謨ｰ驥・,
        "chart_acc_name": "豁｣遑ｮ邇・,
        "chart_acc_title": "豈乗律豁｣遑ｮ邇・ｼ郁ｿ・悉30螟ｩ・・,
        "chart_acc_yaxis": "豁｣遑ｮ邇・(%)",
        "ta_header": "笞｡ 髯先慮謖第・ {i}/{t}",
        "ta_reading": "隸ｻ髻ｳ: {r}",
        "ta_correct": "笨・豁｣遑ｮ・・,
        "ta_wrong": "笶・髞呵ｯｯ",
        "ta_seconds": "竢ｱ {s:.1f}遘・,
        "ta_correct_meaning": "豁｣遑ｮ遲疲｡・ <b>{m}</b>",
        "rank_ta_result": "笞｡ 髯先慮謖第・扈捺棡",
        "rank_score_line": "{c}/{t}鬚倡ｭ泌ｯｹ",
        "rank_record_as": "式 莉･ {name} 隶ｰ蠖・,
        "rank_word_times": "### 竢ｱ・・蜷・｢倡畑譌ｶ",
        "rank_you": " 争 菴",
        "rank_q_suffix": "鬚・,
        "word_list_title": "搭 莉頑律逧・黒隸榊・陦ｨ",
        "word_list_sub": "蜈郁ｮｰ菴剰ｿ吩ｺ帛黒隸搾ｼ悟・蠑蟋区ｵ矩ｪ鯉ｼ・,
        "word_list_no": "No.",
        "word_list_word": "蜊戊ｯ・,
        "word_list_reading": "隸ｻ髻ｳ",
        "word_list_meaning": "諢乗・,
        "word_list_start": "笨・隶ｰ菴丈ｺ・ｼ∝ｼ蟋句黒隸肴ｵ矩ｪ・,
        "word_list_back": "匠 霑泌屓鬥夜｡ｵ",
        "word_list_note": "庁 諠ｳ逕ｨ隨碑ｮｰ譛ｬ謚・・逧・酔蟄ｦ・悟庄莉･蟇ｹ辣ｧ霑吩ｸｪ蛻苓｡ｨ扈・ｹ・・,
    },
}


def T(key):
    """迴ｾ蝨ｨ縺ｮ險隱櫁ｨｭ螳壹〒繝・く繧ｹ繝医ｒ霑斐☆"""
    lang = st.session_state.get("user_lang", "ja")
    return TRANSLATIONS.get(lang, TRANSLATIONS["ja"]).get(
        key, TRANSLATIONS["ja"].get(key, key)
    )


st.set_page_config(page_title="当 蜊倩ｪ樊囓險・| 譛ｪ譚･蝪ｾ", layout="centered")

# 笏笏 繝輔か繝ｳ繝郁ｪｭ縺ｿ霎ｼ縺ｿ・・ink繧ｿ繧ｰ蜊倡峡・俄楳笏笏笏笏笏笏笏笏笏笏笏笏笏
st.markdown(
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP'
    ':wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700'
    '&family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# 笏笏 繝輔か繝ｳ繝磯←逕ｨCSS・・tyle繧ｿ繧ｰ蜊倡峡・俄楳笏笏笏笏笏笏笏笏笏笏笏笏笏
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

# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# 謗･邯・
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# SM-2 繧｢繝ｫ繧ｴ繝ｪ繧ｺ繝・亥､画峩縺ｪ縺暦ｼ・
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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

# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# save_review・・eview_logs 縺ｫ upsert・・
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def save_review(username, cid, q, new_ef, new_iv, new_rp, next_date):
    # cid縺君one縺ｾ縺溘・0縺ｮ蝣ｴ蜷医・螟夜Κ繧ｭ繝ｼ蛻ｶ邏・＆蜿阪↓縺ｪ繧九◆繧√せ繧ｭ繝・・
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

# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# 繝・・繧ｿ蜿門ｾ鈴未謨ｰ
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
@st.cache_data(ttl=60)
def load_users():
    try:
        sb = get_supabase()
        res = sb.table("users").select("username").execute()
        return [row["username"] for row in res.data] if res.data else []
    except:
        return []


# Supabase SQL Editor 縺ｧ users 縺ｫ nickname 蛻励ｒ霑ｽ蜉縺吶ｋ縺ｨ縺阪・萓具ｼ域焔蜍募ｮ溯｡鯉ｼ・
# ALTER TABLE users ADD COLUMN IF NOT EXISTS nickname TEXT DEFAULT '';
# ALTER TABLE users ADD COLUMN IF NOT EXISTS lang TEXT DEFAULT 'ja';


@st.cache_data(ttl=60)
def load_user_nickname(username):
    """繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ繝九ャ繧ｯ繝阪・繝繧貞叙蠕・""
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
    """繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ險隱櫁ｨｭ螳壹ｒ蜿門ｾ・""
    try:
        sb = get_supabase()
        res = sb.table("users").select("lang").eq("username", username).execute()
        if res.data and res.data[0].get("lang"):
            return res.data[0]["lang"]
        return "ja"
    except:
        return "ja"


def save_user_lang(username, lang):
    """險隱櫁ｨｭ螳壹ｒ菫晏ｭ・""
    try:
        sb = get_supabase()
        sb.table("users").update({"lang": lang}).eq("username", username).execute()
        st.cache_data.clear()
    except:
        pass


def save_user_nickname(username, nickname):
    """繝九ャ繧ｯ繝阪・繝繧剃ｿ晏ｭ・""
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
    蝓ｺ譛ｬ繝壹・繧ｹ(base_daily_limit)縺ｨ莉頑律縺ｮ隱ｿ謨ｴ蛟､繧貞叙蠕励☆繧九・
    today_limit_date 縺御ｻ頑律縺ｧ縺ｪ縺代ｌ縺ｰ today_limit 縺ｯ辟｡蜉ｹ縺ｨ縺ｿ縺ｪ縺吶・
    謌ｻ繧雁､: {"base": int, "today": int, "effective": int}
      effective = 莉頑律螳滄圀縺ｫ菴ｿ縺・椢謨ｰ
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
        # 莉頑律縺ｮ譌･莉倥→荳閾ｴ縺吶ｋ蝣ｴ蜷医・縺ｿ today_limit 繧呈怏蜉ｹ縺ｫ縺吶ｋ
        if today_limit is not None and str(today_date) == today_str:
            effective = int(today_limit)
        else:
            effective = base
        return {"base": base, "today": today_limit if str(today_date) == today_str else None, "effective": effective}
    except:
        return {"base": 10, "today": None, "effective": 10}


def save_base_limit(username: str, limit: int) -> bool:
    """蝓ｺ譛ｬ繝壹・繧ｹ・・ase_daily_limit・峨ｒ菫晏ｭ倥☆繧・""
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
    """莉頑律縺縺代・隱ｿ謨ｴ譫壽焚繧剃ｿ晏ｭ倥☆繧・""
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
def load_flashcards_for_step1(set_id: int):
    try:
        sb = get_supabase()
        res = (
            sb.table("flashcards_v2")
            .select(
                "id, lang1, lang1_sub, lang2, lang2_sub, "
                "lang3, lang3_sub, page_range, item_no, category"
            )
            .eq("set_id", set_id)
            .order("item_no")
            .execute()
        )
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

    # 蜷・き繝ｼ繝峨・譛譁ｰ繝ｭ繧ｰ繧貞叙蠕・
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

    if "縺ｿ繧薙↑縺ｮ譌･譛ｬ隱・ in category:
        meaning = card.get("meaning", "")
        st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#fff9f0,#fff3e0);
    border-radius:16px;
    padding:2.5rem 1.5rem;
    text-align:center;
    box-shadow:0 4px 16px rgba(0,0,0,0.08);
    margin:0.5rem 0;">
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">蝠城｡・/div>
  <div style="font-size:2.2rem;font-weight:700;color:#1a1a1a;line-height:1.4;">
    {meaning}
  </div>
  <div style="font-size:0.85rem;color:#bbb;margin-top:1rem;">譌･譛ｬ隱槭〒菴輔→險縺・∪縺吶°・・/div>
</div>
""", unsafe_allow_html=True)

    else:
        word    = card.get("lang1", card.get("word", ""))
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
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">蝠城｡・/div>
  <div style="font-size:2.4rem;font-weight:700;color:#1a1a1a;">
    {word}
  </div>
  {reading_html}
</div>
""", unsafe_allow_html=True)


def render_card_back(card: dict, lang: str = "ja"):
    category = str(card.get("category", ""))

    if "縺ｿ繧薙↑縺ｮ譌･譛ｬ隱・ in category:
        word    = card.get("lang1", card.get("word", ""))
        reading = card.get("reading", "")
        pos     = card.get("meaning_zh", "")   # 蜩∬ｩ槭亥錐縲峨亥虚I縲・
        accent  = card.get("phonetic", "")     # 繧｢繧ｯ繧ｻ繝ｳ繝育分蜿ｷ

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
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">遲斐∴</div>
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
        zh_html = f'<div style="font-size:1.1rem;color:#e05a00;margin-top:0.6rem;">・・ {meaning_zh}</div>' \
                  if meaning_zh else ""
        ex_html = f'<div style="font-size:0.9rem;color:#aaa;margin-top:0.6rem;font-style:italic;">{example}</div>' \
                  if example else ""
        rd_html = f'<div style="font-size:1rem;color:#555;margin-top:0.4rem;">隱ｭ縺ｿ・嘴reading}</div>' \
                  if reading else ""

        st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#f0f4ff,#e8f0fe);
    border-radius:16px;
    padding:2.5rem 1.5rem;
    text-align:center;
    box-shadow:0 4px 16px rgba(0,0,0,0.08);
    margin:0.5rem 0;">
  <div style="font-size:0.85rem;color:#aaa;margin-bottom:0.8rem;letter-spacing:2px;">遲斐∴</div>
  <div style="font-size:1.8rem;font-weight:700;color:#1a1a1a;">
    {meaning}
  </div>
  {rd_html}
  {ph_html}
  {zh_html}
  {ex_html}
</div>
""", unsafe_allow_html=True)


# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# 繧ｻ繝・す繝ｧ繝ｳ蛻晄悄蛹・
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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

if "word_list_queue" not in st.session_state:
    st.session_state.word_list_queue = []
if "selected_set_id" not in st.session_state:
    st.session_state.selected_set_id = None
if "flash_step" not in st.session_state:
    st.session_state.flash_step = "home"

# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# 繝ｭ繧ｰ繧､繝ｳ逕ｻ髱｢
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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

# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# 繝帙・繝逕ｻ髱｢
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def show_home(username):
    # 笏笏 CSS 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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

    # 笏笏 繝｢繝ｼ繝牙愛螳・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    show_settings = st.session_state.get("show_settings", False)

    # 笏笏 繝倥ャ繝繝ｼ陦鯉ｼ亥ｸｸ縺ｫ陦ｨ遉ｺ・・笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    col_title, col_gear = st.columns([5, 1])
    with col_title:
        if st.session_state.get("user_lang") == "zh":
            st.markdown(f"### 菴螂ｽ・鶏username}・・)
        else:
            st.markdown(f"### 縺薙ｓ縺ｫ縺｡縺ｯ縲＋username}縺輔ｓ・・)
    with col_gear:
        gear_label = "笨・髢峨§繧・ if show_settings else "笞呻ｸ・險ｭ螳・
        if st.button(gear_label, key="toggle_settings"):
            st.session_state["show_settings"] = not show_settings
            st.rerun()

    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏・
    # 險ｭ螳壹・繝ｼ繧ｸ
    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏・
    if show_settings:
        st.markdown("---")
        st.markdown("#### 笞呻ｸ・險ｭ螳・)

        # 險隱槫・譖ｿ
        if st.button(T("lang_switch"), key="lang_toggle"):
            new_lang = "zh" if st.session_state["user_lang"] == "ja" else "ja"
            st.session_state["user_lang"] = new_lang
            save_user_lang(username, new_lang)
            st.rerun()

        st.markdown("---")

        # 謨呎攝驕ｸ謚・
        st.markdown("##### 答 謨呎攝繧帝∈縺ｶ")
        sets = load_flashcard_sets()
        if sets:
            set_id_list = [s["id"] for s in sets]
            set_name_map = {s["id"]: s["set_name"] for s in sets}
            set_info_map = {s["id"]: s for s in sets}
            prev = st.session_state.get("selected_set_id")
            default_idx = set_id_list.index(prev) if prev in set_id_list else 0
            selected_set_id = st.selectbox(
                "謨呎攝",
                options=set_id_list,
                index=default_idx,
                format_func=lambda x: set_name_map[x],
                key="settings_set_select",
            )
            st.session_state["selected_set_id"] = selected_set_id
            info = set_info_map[selected_set_id]
            st.caption(
                f"唐 {info.get('category','')} ・・{info.get('grade','')} ・・{info.get('description','')}"
            )
        else:
            st.warning(T("no_material"))

        st.markdown("---")

        # 蟄ｦ鄙偵・繝ｼ繧ｹ險ｭ螳・
        st.markdown("##### 套 蟄ｦ鄙偵・繝ｼ繧ｹ險ｭ螳・)
        plan = load_study_plan(username)
        base = plan["base"]
        today = plan["today"]
        eff = plan["effective"]

        st.markdown(
            f"<div style='font-size:0.9rem;color:#555;margin-bottom:8px;'>"
            f"迴ｾ蝨ｨ縺ｮ險ｭ螳・ <b>{eff}譫・譌･</b>"
            + (f"縲・亥渕譛ｬ: {base}譫・/ 莉頑律: {today}譫夲ｼ・ if today is not None and today != base else "")
            + "</div>",
            unsafe_allow_html=True,
        )
        pace_options = [3, 5, 10, 15, 20, 25, 30]
        pace_mode = st.radio(
            "險ｭ螳壹Δ繝ｼ繝・,
            options=["搭 蝓ｺ譛ｬ繝壹・繧ｹ繧貞､画峩", "笞｡ 莉頑律縺縺題ｪｿ謨ｴ"],
            horizontal=True,
            key="pace_mode_radio",
            label_visibility="collapsed",
        )
        if pace_mode == "搭 蝓ｺ譛ｬ繝壹・繧ｹ繧貞､画峩":
            st.caption("蜈育函縺ｨ逶ｸ隲・＠縺ｦ豎ｺ繧√◆1譌･縺ｮ逶ｮ讓呎椢謨ｰ縺ｧ縺吶・)
            new_base = st.radio(
                "蝓ｺ譛ｬ譫壽焚",
                options=pace_options,
                index=pace_options.index(base) if base in pace_options else 1,
                horizontal=True,
                key="base_radio",
                format_func=lambda x: f"{x}譫・,
            )
            st.caption("逶ｮ螳・ 3縲・譫・蛻昴ａ縺ｦ / 10譫・讓呎ｺ・/ 20譫壻ｻ･荳・隧ｦ鬨灘燕")
            if st.button("笨・蝓ｺ譛ｬ繝壹・繧ｹ繧剃ｿ晏ｭ・, key="save_base"):
                if save_base_limit(username, new_base):
                    st.success(f"蝓ｺ譛ｬ繝壹・繧ｹ繧・{new_base}譫・縺ｫ險ｭ螳壹＠縺ｾ縺励◆・・)
                    st.rerun()
        else:
            st.caption("莉頑律縺縺大､画峩縺ｧ縺阪∪縺吶らｿ梧律縺ｯ蝓ｺ譛ｬ繝壹・繧ｹ縺ｫ閾ｪ蜍輔〒謌ｻ繧翫∪縺吶・)
            adj_default = today if (today is not None and today in pace_options) else eff
            if adj_default not in pace_options:
                adj_default = 10
            new_today = st.radio(
                "莉頑律縺ｮ譫壽焚",
                options=pace_options,
                index=pace_options.index(adj_default),
                horizontal=True,
                key="today_radio",
                format_func=lambda x: f"{x}譫・,
            )
            diff = new_today - base
            st.caption(
                f"蝓ｺ譛ｬ繧医ｊ {abs(diff)}譫・{'蟆代↑繧・ if diff < 0 else '螟壹ａ・Å沐･' if diff > 0 else '竊・蝓ｺ譛ｬ繝壹・繧ｹ騾壹ｊ 総'}"
            )
            if st.button("笞｡ 莉頑律縺ｯ縺薙・譫壽焚縺ｧ・・, key="save_today"):
                if save_today_limit(username, new_today):
                    st.success(f"莉頑律縺ｯ {new_today}譫・縺ｧ蟄ｦ鄙偵＠縺ｾ縺呻ｼ・)
                    st.rerun()

        st.markdown("---")

        # 繝九ャ繧ｯ繝阪・繝險ｭ螳・
        st.markdown("##### 式 繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ繝阪・繝")
        current_nick = load_user_nickname(username)
        if current_nick:
            st.caption(f"迴ｾ蝨ｨ: **{current_nick}**")
        nick_input = st.text_input(
            "譁ｰ縺励＞繝九ャ繧ｯ繝阪・繝・・縲・譁・ｭ暦ｼ・,
            max_chars=8,
            placeholder="萓・ 縺溘ｓ縺斐・繧ｹ繧ｿ繝ｼ",
            key="settings_nick",
        )
        if st.button("沈 菫晏ｭ・, key="save_nick"):
            if len(nick_input) < 2:
                st.error("2譁・ｭ嶺ｻ･荳翫〒蜈･蜉帙＠縺ｦ縺上□縺輔＞")
            else:
                if save_user_nickname(username, nick_input):
                    st.success(f"縲鶏nick_input}縲阪↓螟画峩縺励∪縺励◆・・)
                    st.balloons()
                    st.rerun()

        st.markdown("---")

        # 繝ｭ繧ｰ繧｢繧ｦ繝・
        if st.button(T("logout"), key="settings_logout"):
            st.session_state["flash_user"] = ""
            st.session_state["show_settings"] = False
            st.rerun()

        return  # 險ｭ螳壹・繝ｼ繧ｸ陦ｨ遉ｺ荳ｭ縺ｯ繝帙・繝繧ｳ繝ｳ繝・Φ繝・ｒ陦ｨ遉ｺ縺励↑縺・

    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏・
    # 繝帙・繝繝壹・繧ｸ・亥ｭｦ鄙堤音蛹悶・繧ｷ繝ｳ繝励Ν・・
    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏・

    # 騾｣邯壽律謨ｰ
    streak = compute_learning_streak(username)
    if streak >= 1:
        st.info(f"櫨 {streak}{T('streak_msg')}")
    else:
        st.info(T("streak_zero"))

    # 謨呎攝縺梧悴驕ｸ謚槭・蝣ｴ蜷医・險ｭ螳壹∈隱伜ｰ・
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

    # 謨呎攝諠・ｱ・医さ繝ｳ繝代け繝・陦鯉ｼ・
    set_name_map = {s["id"]: s["set_name"] for s in sets}
    st.markdown(
        f"<div class='mini-card'>答 <b>{set_name_map[selected_set_id]}</b>"
        f"縲{info.get('category','')} / {info.get('grade','')}</div>",
        unsafe_allow_html=True,
    )

    # 騾ｲ謐励ヰ繝ｼ
    if total > 0:
        correct = count_correct_once_in_set(username, selected_set_id)
        progress_val = correct / total
        st.progress(progress_val)
        st.caption(f"笨・{correct} / {total} {T('progress_caption')}・・int(progress_val*100)}%・・)

    st.markdown("---")

    # 笏笏 莉頑律繧・ｋ縺薙→・医Γ繧､繝ｳ・・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    st.markdown(f"### {T('today_task')}")
    new_count, due_count = count_new_and_due_for_set(username, selected_set_id)
    plan = load_study_plan(username)
    st.markdown(
        f'<span class="badge-red">{T("badge_new")} {new_count}{T("cards")}</span>'
        f'<span class="badge-yellow">{T("badge_due")} {due_count}{T("cards")}</span>',
        unsafe_allow_html=True,
    )
    st.caption(f"套 1譌･縺ｮ繝壹・繧ｹ: {plan['effective']}譫・)
    st.markdown("")

    total_today = new_count + due_count
    if total_today > 0:
        if st.button(
            "噫 莉頑律縺ｮ蟄ｦ鄙偵ｒ縺ｯ縺倥ａ繧具ｼ・,
            use_container_width=True,
            type="primary",
            key="btn_start_learning",
        ):
            st.session_state.flash_step = "select"
            st.rerun()
    else:
        # 莉頑律縺ｮ蛻・′邨ゅｏ縺｣縺溷ｴ蜷・
        st.success(T("all_done"))
        st.markdown(f"#### {T('more_study')}")

        # 遘ｰ蜿ｷ陦ｨ遉ｺ
        total_xp = calc_total_xp(username)
        level = calc_level(total_xp)
        titles = {
            1: ("験", "縺溘ｓ縺・縺ｮ 縺溘∪縺・),
            2: ("当", "縺溘ｓ縺・縺ｮ 縺溘∪縺・"),
            3: ("笞｡", "縺溘ｓ縺・縺ｮ 縺帙ｓ縺・),
            4: ("櫨", "縺溘ｓ縺・縺ｮ 縺溘▽縺倥ｓ"),
            5: ("虫", "縺溘ｓ縺・縺ｮ 縺医＞繧・≧"),
            6: ("荘", "縺溘ｓ縺・縺ｮ 縺翫≧"),
            7: ("検", "縺溘ｓ縺・縺ｮ 縺ｧ繧薙○縺､"),
        }
        icon, title = titles.get(min(level, 7), ("検", "縺溘ｓ縺・縺ｮ 縺ｧ繧薙○縺､"))
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

        # 繧ｿ繧､繝繧｢繧ｿ繝・け繝懊ち繝ｳ
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

        # 繧ｹ繝医Μ繝ｼ繧ｯ諠・ｱ
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
/* 蜷・・繧ｿ繝ｳ縺ｮ濶ｲ */
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
        if st.button("匠", help=T("home_btn"), use_container_width=True):
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
                "word": card.get("lang1", card.get("word", "")), "quality": q, "next_review": next_date
            })
            st.session_state["flash_index"] += 1
            st.session_state["flash_show_answer"] = False
            st.rerun()

        st.markdown("---")
        st.markdown(f"### {T('how_much')}")

        # 繧ｰ繝ｩ繝・・繧ｷ繝ｧ繝ｳ蜃｡萓九ヰ繝ｼ
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

        # 繝ｯ繝ｳ繧ｿ繝・・繧ｫ繝ｼ繝峨・繧ｿ繝ｳ・・蛻・縺､・・
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

        # 谺｡蝗槫ｾｩ鄙偵・逶ｮ螳会ｼ医・繧ｿ繝ｳ荳具ｼ・
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

# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# 邨先棡逕ｻ髱｢・・P繝ｻ繝ｬ繝吶Ν・・
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
def calc_session_xp(results):
    """繧ｻ繝・す繝ｧ繝ｳ縺ｮ迯ｲ蠕郵P繧定ｨ育ｮ・""
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
    """邏ｯ險・P繧池eview_logs縺九ｉ險育ｮ・""
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
    """XP縺九ｉ繝ｬ繝吶Ν繧定ｨ育ｮ暦ｼ・PG蠑乗・髟ｷ譖ｲ邱夲ｼ・""
    import math

    return int(math.sqrt(total_xp / 10)) + 1


def calc_level_progress(total_xp):
    """迴ｾ繝ｬ繝吶Ν蜀・・騾ｲ謐礼紫(0.0縲・.0)繧定ｿ斐☆"""
    import math

    level = calc_level(total_xp)
    xp_current_level = ((level - 1) ** 2) * 10
    xp_next_level = (level ** 2) * 10
    if xp_next_level == xp_current_level:
        return 1.0
    return (total_xp - xp_current_level) / (xp_next_level - xp_current_level)


def load_daily_stats(username):
    """
    驕主悉30譌･蛻・・譌･蛻･蟄ｦ鄙堤ｵｱ險医ｒ霑斐☆
    謌ｻ繧雁､: list[dict] = [
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

    # 驕主悉30譌･蛻・↓邨槭ｋ & 繧ｽ繝ｼ繝・
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
    驕主悉30譌･蛻・・邏ｯ險・P謗ｨ遘ｻ繧定ｿ斐☆
    謌ｻ繧雁､: list[dict] = [{"date": "...", "cumulative_xp": 120}, ...]
    """
    daily = load_daily_stats(username)
    # 蜈ｨ螻･豁ｴ縺ｮ邏ｯ險・P縺ｮ髢句ｧ句､繧定ｨ育ｮ・
    all_logs = load_review_logs(username)
    from datetime import date, timedelta
    cutoff = (date.today() - timedelta(days=29)).isoformat()

    # cutoff莉･蜑阪・XP蜷郁ｨ・
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


# Supabase SQL Editor 縺ｧ ta_scores 繝・・繝悶Ν繧剃ｽ懈・縺吶ｋ縺ｨ縺阪・萓具ｼ域焔蜍募ｮ溯｡鯉ｼ・
# CREATE TABLE IF NOT EXISTS ta_scores (
#   id SERIAL PRIMARY KEY,
#   username TEXT NOT NULL,
#   nickname TEXT NOT NULL DEFAULT '縺ｪ縺・,
#   set_id INTEGER NOT NULL,
#   total_score INTEGER NOT NULL,
#   correct_count INTEGER NOT NULL,
#   total_cards INTEGER NOT NULL,
#   played_at TIMESTAMP DEFAULT NOW()
# );


def generate_choices(correct_card, all_cards, n=4):
    import random
    category = str(correct_card.get("category", ""))
    if "縺ｿ繧薙↑縺ｮ譌･譛ｬ隱・ in category:
        # 蝠城｡後・荳ｭ蝗ｽ隱・meaning)縲∵ｭ｣隗｣縺ｯ譌･譛ｬ隱・word)
        correct_answer = correct_card.get("lang1", correct_card.get("word", ""))
        others = [
            c.get("lang1", c.get("word", "")) for c in all_cards
            if c["id"] != correct_card["id"]
            and c.get("lang1", c.get("word", "")) != correct_answer
        ]
    else:
        # 蝠城｡後・闍ｱ隱・word)縲∵ｭ｣隗｣縺ｯ譌･譛ｬ隱櫁ｨｳ(meaning)
        correct_answer = correct_card["meaning"]
        others = [
            c["meaning"] for c in all_cards
            if c["id"] != correct_card["id"]
            and c["meaning"] != correct_answer
        ]
    fallback = ["繧上°繧峨↑縺・, "縺ｹ縺､縺ｮ縺薙→縺ｰ", "縺｡縺後≧繧ゅ・",
                "縺ｾ縺溘∋縺､縺ｮ繧ゅ・", "縺ｪ縺ｫ縺九・縺薙→"]
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
        st.warning(f"繧ｹ繧ｳ繧｢菫晏ｭ倥お繝ｩ繝ｼ: {e}")


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

    # 笏笏 CSS 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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
    /* 4謚槭・繧ｿ繝ｳ 譛ｪ蝗樒ｭ疲凾 */
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

    # 笏笏 繝倥ャ繝繝ｼ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    col_p, col_h = st.columns([4, 1])
    with col_p:
        st.markdown(
            f'<div style="font-size:0.9rem;color:#888;">'
            f'{T("ta_header").format(i=idx + 1, t=total)}</div>',
            unsafe_allow_html=True
        )
        st.progress(idx / total)
    with col_h:
        if st.button("匠", key="ta_home", help=T("home_btn")):
            st.session_state["flash_mode"] = "home"
            st.session_state["ta_choices"] = []
            st.session_state["ta_answered"] = False
            st.session_state["ta_correct"] = None
            st.session_state["ta_selected_idx"] = -1
            st.session_state["flash_timer_start"] = None
            st.rerun()

    # 笏笏 繧ｿ繧､繝槭・邂｡逅・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if st.session_state["flash_timer_start"] is None:
        st.session_state["flash_timer_start"] = time.time()

    elapsed = time.time() - st.session_state["flash_timer_start"]
    limit = 10  # 遘・
    remaining = max(0.0, limit - elapsed)

    # 繧ｿ繧､繝槭・縺ｮ濶ｲ繧呈ｮ九ｊ譎る俣縺ｧ螟峨∴繧・
    if remaining > 6:
        timer_color = "#00b09b"   # 邱・
    elif remaining > 3:
        timer_color = "#ffa500"   # 繧ｪ繝ｬ繝ｳ繧ｸ
    else:
        timer_color = "#ff4b4b"   # 襍､

    # 笏笏 繧ｫ繝ｼ繝芽｡ｨ遉ｺ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if not st.session_state["ta_answered"]:
        st.markdown(
            f'<div style="font-size:0.85rem; opacity:0.6; margin-bottom:6px; '
            f'text-align:center; color:#aaa;">{T("ta_question")}</div>',
            unsafe_allow_html=True,
        )
        render_card_front(card)
    else:
        render_card_back(card)

    # 笏笏 繧ｿ繧､繝槭・陦ｨ遉ｺ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if not st.session_state["ta_answered"]:
        st.markdown(
            f'<div class="ta-timer" style="color:{timer_color};">'
            f'{T("ta_seconds").format(s=remaining)}</div>',
            unsafe_allow_html=True
        )
    else:
        # 蝗樒ｭ疲ｸ医∩縺ｯ邨先棡繧ｫ繝ｩ繝ｼ縺ｧ蝗ｺ螳夊｡ｨ遉ｺ
        result_color = "#00b09b" if st.session_state["ta_correct"] else "#ff4b4b"
        result_text = (
            T("ta_correct") if st.session_state["ta_correct"] else T("ta_wrong")
        )
        st.markdown(
            f'<div class="ta-timer" style="color:{result_color};">'
            f'{result_text}</div>',
            unsafe_allow_html=True
        )

    # 笏笏 4謚槭・繧ｿ繝ｳ逕滓・ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    # 驕ｸ謚櫁い縺後↑縺・or 譁ｰ縺励＞繧ｫ繝ｼ繝峨・蝣ｴ蜷医・縺ｿ逕滓・
    if not st.session_state["ta_choices"]:
        all_cards = load_flashcards_by_set(
            st.session_state.get("selected_set_id")
        )
        st.session_state["ta_choices"] = generate_choices(card, all_cards)

    choices = st.session_state["ta_choices"]
    category = str(card.get("category", ""))
    if "縺ｿ繧薙↑縺ｮ譌･譛ｬ隱・ in category:
        correct_meaning = card["word"]   # 譌･譛ｬ隱槭′豁｣隗｣
    else:
        correct_meaning = card["meaning"]  # 譌･譛ｬ隱櫁ｨｳ縺梧ｭ｣隗｣

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; font-size:0.9rem;"
        "color:#888; margin-bottom:8px;'>"
        f"{T('ta_tap')}</div>",
        unsafe_allow_html=True
    )

    # 2ﾃ・ 繧ｰ繝ｪ繝・ラ縺ｧ4謚櫁｡ｨ遉ｺ
    row1 = st.columns(2)
    row2 = st.columns(2)
    grid = [row1[0], row1[1], row2[0], row2[1]]

    answered = st.session_state["ta_answered"]

    for i, (col, choice) in enumerate(zip(grid, choices)):
        with col:
            # 蝗樒ｭ泌ｾ後・濶ｲ蛻・￠
            if answered:
                if choice == correct_meaning:
                    # 豁｣隗｣驕ｸ謚櫁い 竊・邱代ワ繧､繝ｩ繧､繝・
                    st.markdown(f"""
                    <div style="background:#00b09b; color:white;
                        border-radius:16px; padding:18px 8px;
                        text-align:center; font-weight:bold;
                        font-size:1rem; min-height:80px;
                        display:flex; align-items:center;
                        justify-content:center;">
                        笨・{choice}
                    </div>
                    """, unsafe_allow_html=True)
                elif (not st.session_state["ta_correct"]
                      and i == st.session_state.get("ta_selected_idx")):
                    # 閾ｪ蛻・′驕ｸ繧薙□荳肴ｭ｣隗｣ 竊・襍､繝上う繝ｩ繧､繝・
                    st.markdown(f"""
                    <div style="background:#ff4b4b; color:white;
                        border-radius:16px; padding:18px 8px;
                        text-align:center; font-weight:bold;
                        font-size:1rem; min-height:80px;
                        display:flex; align-items:center;
                        justify-content:center;">
                        笶・{choice}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 縺昴・莉・竊・繧ｰ繝ｬ繝ｼ
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
                # 譛ｪ蝗樒ｭ・竊・謚ｼ縺帙ｋ繝懊ち繝ｳ
                if st.button(choice, key=f"ta_choice_{i}",
                             use_container_width=True, type="secondary"):
                    is_correct = (choice == correct_meaning)
                    st.session_state["ta_answered"] = True
                    st.session_state["ta_correct"] = is_correct
                    st.session_state["ta_selected_idx"] = i
                    score = max(0, int(remaining * 10)) if is_correct else 0
                    st.session_state["flash_time_scores"].append({
                        "word": card.get("lang1", card.get("word", "")),
                        "meaning": correct_meaning,
                        "chosen": choice,
                        "time": round(elapsed, 1),
                        "score": score,
                        "result": "correct" if is_correct else "wrong",
                    })
                    quality = 5 if is_correct else 0
                    _record_ta_quality(username, card, quality)
                    st.rerun()

    # 笏笏 繧ｿ繧､繝繧ｪ繝ｼ繝舌・蜃ｦ逅・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if remaining <= 0 and not answered:
        st.session_state["ta_answered"] = True
        st.session_state["ta_correct"] = False
        st.session_state["ta_selected_idx"] = -1
        st.session_state["flash_time_scores"].append({
            "word": card.get("lang1", card.get("word", "")),
            "meaning": correct_meaning,
            "chosen": "・域凾髢灘・繧鯉ｼ・,
            "time": 10.0,
            "score": 0,
            "result": "timeout",
        })
        _record_ta_quality(username, card, 0)
        st.rerun()

    # 笏笏 蝗樒ｭ疲ｸ医∩ 竊・谺｡縺ｸ繝懊ち繝ｳ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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
        # 譛ｪ蝗樒ｭ比ｸｭ縺ｯ閾ｪ蜍墓峩譁ｰ
        time.sleep(0.5)
        st.rerun()


def show_ranking():
    username = st.session_state["flash_user"]
    set_id = st.session_state.get("selected_set_id")
    scores = st.session_state.get("flash_time_scores", [])
    nickname = load_user_nickname(username)

    # 繧ｹ繧ｳ繧｢髮・ｨ・
    total_score = sum(s["score"] for s in scores)
    correct_count = sum(1 for s in scores if s["result"] == "correct")
    total_cards = len(scores)

    # Supabase縺ｫ菫晏ｭ・
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

    # 繧ｹ繧ｳ繧｢陦ｨ遉ｺ
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
            ・・accuracy:.0f}%・・
        </div>
        <div style="font-size:0.85rem; opacity:0.7; margin-top:4px;">
            {T("rank_record_as").format(name=rec_name)}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 蜊倩ｪ槫挨繧ｿ繧､繝荳隕ｧ
    st.markdown(T("rank_word_times"))
    for s in scores:
        icon = "笨・ if s["result"] == "correct" else (
                "竢ｰ" if s["result"] == "timeout" else "笶・)
        color = "#00b09b" if s["result"] == "correct" else "#ff4b4b"
        st.markdown(
            f'<div style="display:flex; justify-content:space-between;'
            f'padding:8px 12px; background:{color}22; border-radius:10px;'
            f'margin:4px 0; font-size:0.9rem;">'
            f'<span>{icon} <b>{s["word"]}</b> 窶・{s["meaning"]}</span>'
            f'<span style="color:{color}; font-weight:bold;">'
            f'{s["score"]}pts ({s["time"]}遘・</span></div>',
            unsafe_allow_html=True
        )

    # 繝ｩ繝ｳ繧ｭ繝ｳ繧ｰ陦ｨ遉ｺ
    st.markdown("---")
    st.markdown(f"### {T('rank_title')}")
    ranking = load_ta_ranking(set_id) if set_id else []
    if not ranking:
        st.info(T("rank_empty"))
    else:
        medals = ["･・, "･・, "･・]
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

    # 繝懊ち繝ｳ
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
    """莉頑律縺ｮ蜊倩ｪ樔ｸ隕ｧ繝壹・繧ｸ"""
    queue = st.session_state.get("word_list_queue", [])
    username = st.session_state["flash_user"]

    st.markdown(f"## {T('word_list_title')}")
    st.caption(T("word_list_sub"))
    st.markdown(T("word_list_note"))
    st.markdown("---")

    # 繧ｫ繝・ざ繝ｪ蛻､螳夲ｼ域怙蛻昴・繧ｫ繝ｼ繝峨〒莉｣陦ｨ蛻､螳夲ｼ・
    category = str(queue[0].get("category", "")) if queue else ""
    is_mnn = "縺ｿ繧薙↑縺ｮ譌･譛ｬ隱・ in category

    # 繝・・繝悶Ν繝倥ャ繝繝ｼ
    if is_mnn:
        # 縺ｿ繧薙↑縺ｮ譌･譛ｬ隱橸ｼ壻ｸｭ蝗ｽ隱樞・譌･譛ｬ隱・
        header_cols = st.columns([1, 3, 3, 3])
        header_cols[0].markdown(f"**{T('word_list_no')}**")
        header_cols[1].markdown("**荳ｭ蝗ｽ隱橸ｼ亥撫鬘鯉ｼ・*")
        header_cols[2].markdown(f"**{T('word_list_word')}・育ｭ斐∴・・*")
        header_cols[3].markdown(f"**{T('word_list_reading')}**")
    else:
        # 闍ｱ讀懶ｼ夊恭隱樞・譌･譛ｬ隱・
        header_cols = st.columns([1, 3, 3, 3])
        header_cols[0].markdown(f"**{T('word_list_no')}**")
        header_cols[1].markdown(f"**{T('word_list_word')}**")
        header_cols[2].markdown(f"**{T('word_list_meaning')}**")
        header_cols[3].markdown("**逋ｺ髻ｳ / 隱ｭ縺ｿ**")

    st.markdown("<hr style='margin:4px 0 8px 0;'>", unsafe_allow_html=True)

    # 蜊倩ｪ櫁｡・
    for i, card in enumerate(queue):
        row_bg = "#f8f9ff" if i % 2 == 0 else "#ffffff"
        cols = st.columns([1, 3, 3, 3])

        if is_mnn:
            meaning_zh = card.get("meaning", "")    # 荳ｭ蝗ｽ隱橸ｼ亥撫鬘鯉ｼ・
            word       = card.get("word", "")        # 譌･譛ｬ隱橸ｼ育ｭ斐∴・・
            reading    = card.get("reading", "")
            accent     = card.get("phonetic", "")
            reading_str = f"{reading}縲{accent}" if accent else reading

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
            word     = card.get("lang1", card.get("word", ""))
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

    # 繝懊ち繝ｳ
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

    # 笏笏 CSS 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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

    # 笏笏 闃ｱ轣ｫ貍泌・ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if accuracy >= 80:
        st.balloons()

    # 笏笏 繝偵・繝ｭ繝ｼ繝舌リ繝ｼ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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

    # 笏笏 4謖・ｨ吶き繝ｼ繝会ｼ・陦鯉ｼ俄楳笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
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

    # 笏笏 繝ｬ繝吶Ν繝ｻXP繝舌・ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    st.markdown("---")
    st.markdown(f"### 式 Lv.{level} 窶・{T('total_xp_lbl')} {total_xp} XP")
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

    # 笏笏 蜊倩ｪ槫挨邨先棡・医ヴ繝ｫ陦ｨ遉ｺ・俄楳笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    st.markdown("---")
    st.markdown(T("summary_title"))

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**{T('words_done')}**")
        covered = perfect + good
        if covered:
            pills = " ".join(
                [
                    f'<span class="word-pill" style="background:#00b09b;">{r.get("lang1", r.get("word", ""))}</span>'
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
                    f'<span class="word-pill" style="background:#ffa500;">{r.get("lang1", r.get("word", ""))}</span>'
                    for r in ok
                ]
                + [
                    f'<span class="word-pill" style="background:#ff4b4b;">{r.get("lang1", r.get("word", ""))}</span>'
                    for r in ng
                ]
            )
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.caption(T("none_perfect"))

    # 笏笏 谺｡蝗槫ｾｩ鄙呈律縺ｮ莠亥相 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if ng:
        st.markdown("---")
        st.info(
            f"庁 **{len(ng)}{T('cards')}**{T('ng_notice_tail')}"
        )

    # 笏笏 謌宣聞繧ｰ繝ｩ繝・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    st.markdown("---")
    st.markdown(f"### {T('graph_title')}")

    daily_stats = load_daily_stats(username)
    cum_stats = load_cumulative_xp(username)

    # 蟄ｦ鄙偵′縺ゅ▲縺滓律縺縺第歓蜃ｺ
    active_days = [d for d in daily_stats if d["cards"] > 0]

    if len(active_days) < 2:
        st.info(T("graph_need_days"))
    else:
        tab1, tab2, tab3 = st.tabs([T("tab_xp"), T("tab_cards"), T("tab_acc")])

        # 笏笏 Tab1: 邏ｯ險・P謚倥ｌ邱壹げ繝ｩ繝・笏笏笏笏笏笏笏笏笏笏
        with tab1:
            df_cum = pd.DataFrame(cum_stats)
            # 蟄ｦ鄙偵・縺ゅｋ譌･縺縺代・繝ｼ繧ｫ繝ｼ繧貞ｼｷ隱ｿ
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
            # 邱丞粋繧ｳ繝｡繝ｳ繝・
            total_active = len(active_days)
            st.caption(T("study_days_caption").format(n=total_active))

        # 笏笏 Tab2: 譌･蛻･蟄ｦ鄙呈椢謨ｰ譽偵げ繝ｩ繝・笏笏笏笏笏笏笏笏
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

        # 笏笏 Tab3: 譌･蛻･豁｣隗｣邇・釜繧檎ｷ壹げ繝ｩ繝・笏笏笏笏笏笏
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
                # 80%繝ｩ繧､繝ｳ繧堤せ邱壹〒霑ｽ蜉
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

    # 笏笏 繧｢繧ｯ繧ｷ繝ｧ繝ｳ繝懊ち繝ｳ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button(T("home_btn"), type="primary", use_container_width=True):
            st.session_state["flash_mode"] = "home"
            st.session_state["flash_session_results"] = []
            st.rerun()
    with b2:
        if st.button(T("retry_btn"), use_container_width=True):
            ng_words = [r.get("lang1", r.get("word", "")) for r in ng + ok]
            selected_set_id = st.session_state.get("selected_set_id")
            if selected_set_id:
                all_cards = load_flashcards_by_set(selected_set_id)
                retry_queue = [c for c in all_cards if c.get("lang1", c.get("word", "")) in ng_words]
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


# ==========================================================
# 笨・STEP1: 繧ｻ繝・ヨ驕ｸ謚・& 遽・峇謖・ｮ壹・繝ｼ繧ｸ・医す繝ｳ繝励Ν遽・峇謖・ｮ夂沿・・
# ==========================================================
def show_step1_select():
    st.markdown("## 笨・STEP 1繝ｻ莉頑律隕壹∴繧句腰隱槭ｒ驕ｸ縺ｼ縺・)
    st.caption("繧ｻ繝・ヨ繧帝∈繧薙〒縲∬ｦ壹∴縺溘＞遽・峇繧呈欠螳壹＠縺ｦ縺上□縺輔＞縲・)

    sets = load_flashcard_sets()
    if not sets:
        st.warning("繧ｻ繝・ヨ縺檎匳骭ｲ縺輔ｌ縺ｦ縺・∪縺帙ｓ縲・)
        if st.button("竊・繝帙・繝縺ｫ謌ｻ繧・):
            st.session_state.flash_step = "home"
            st.rerun()
        return

    set_labels = [
        f"{s['set_name']}・・s.get('category', '')}"
        f"{' ' + s.get('grade', '') if s.get('grade') else ''}・・
        for s in sets
    ]
    selected_idx = st.selectbox(
        "繧ｻ繝・ヨ繧帝∈繧薙〒縺上□縺輔＞",
        range(len(sets)),
        format_func=lambda i: set_labels[i],
        key="step1_set_select",
    )
    chosen_set = sets[selected_idx]
    chosen_set_id = chosen_set["id"]

    words = load_flashcards_for_step1(chosen_set_id)
    if not words:
        st.info("縺薙・繧ｻ繝・ヨ縺ｫ縺ｯ蜊倩ｪ槭′逋ｻ骭ｲ縺輔ｌ縺ｦ縺・∪縺帙ｓ縲・)
        if st.button("竊・謌ｻ繧・, key="step1_back_empty"):
            st.session_state.flash_step = "home"
            st.rerun()
        return

    # item_no 縺ｧ繧ｽ繝ｼ繝医・min/max 繧貞叙蠕・
    item_nos = [w["item_no"] for w in words if w.get("item_no") is not None]
    if not item_nos:
        st.warning("蝠城｡檎分蜿ｷ縺檎匳骭ｲ縺輔ｌ縺ｦ縺・∪縺帙ｓ縲・)
        return

    min_no = min(item_nos)
    max_no = max(item_nos)

    st.markdown("---")
    st.markdown(
        f'<div style="background:#f0f4ff;border-left:4px solid #4C6EF5;'
        f'padding:10px 16px;border-radius:0 8px 8px 0;margin-bottom:16px;">'
        f'<span style="font-weight:bold;color:#4C6EF5;">答 {chosen_set["set_name"]}</span>'
        f'<span style="color:#888;font-size:0.85rem;margin-left:8px;">'
        f'蜈ｨ {len(words)} 蜊倩ｪ橸ｼ・o.{min_no} 縲・No.{max_no}・・/span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("**菴慕分縺九ｉ菴慕分繧定ｦ壹∴縺ｾ縺吶°・・*")

    col_start, col_end = st.columns(2)
    with col_start:
        start_no = st.number_input(
            "髢句ｧ狗分蜿ｷ",
            min_value=min_no,
            max_value=max_no,
            value=min_no,
            step=1,
            key="step1_start_no",
        )
    with col_end:
        end_no = st.number_input(
            "邨ゆｺ・分蜿ｷ",
            min_value=min_no,
            max_value=max_no,
            value=max_no,
            step=1,
            key="step1_end_no",
        )

    # 遽・峇蜀・・蜊倩ｪ槭ｒ謚ｽ蜃ｺ
    if start_no > end_no:
        st.warning("笞・・髢句ｧ狗分蜿ｷ縺ｯ邨ゆｺ・分蜿ｷ莉･荳九↓縺励※縺上□縺輔＞縲・)
        selected_words = []
    else:
        selected_words = [
            w
            for w in words
            if w.get("item_no") is not None
            and start_no <= w["item_no"] <= end_no
        ]

    # 繝励Ξ繝薙Η繝ｼ陦ｨ遉ｺ
    st.markdown("---")
    if selected_words:
        st.markdown(
            f'<div style="background:#fff9f0;border:1px solid #F0C040;'
            f'border-radius:8px;padding:12px 16px;text-align:center;">'
            f'<span style="font-size:1.1rem;font-weight:bold;color:#e67e00;">'
            f"No.{start_no} 縲・No.{end_no}</span>"
            f'<span style="color:#888;margin-left:8px;font-size:0.9rem;">'
            f"・・len(selected_words)} 蜊倩ｪ橸ｼ・/span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # 驕ｸ謚槭＆繧後◆蜊倩ｪ槭ｒ蜈ｨ陦ｨ遉ｺ
        st.markdown("**搭 驕ｸ謚槭＆繧後◆蜊倩ｪ橸ｼ・*")

        def safe(v):
            return str(v) if v and str(v) not in ("None", "nan", "") else ""

        for w in selected_words:
            no = w.get("item_no", "-")
            lang1 = safe(w.get("lang1", ""))
            lang1_sub = safe(w.get("lang1_sub", ""))
            lang2 = safe(w.get("lang2", ""))
            lang2_sub = safe(w.get("lang2_sub", ""))
            lang3 = safe(w.get("lang3", ""))
            lang3_sub = safe(w.get("lang3_sub", ""))

            sub_parts = [s for s in [lang2_sub, lang3, lang3_sub] if s]
            sub_html = "".join(
                f'<span style="font-size:0.78rem;color:#888;margin-left:6px;">{s}</span>'
                for s in sub_parts
            )

            st.markdown(
                f'<div style="border-left:3px solid #dfe6e9;'
                f'padding:6px 12px;margin-bottom:4px;">'
                f'<span style="font-size:0.72rem;color:#aaa;">No.{no}</span>縲'
                f'<span style="font-weight:bold;font-size:0.92rem;">{lang1}</span>'
                + (
                    f'<span style="font-size:0.78rem;color:#888;margin-left:4px;">{lang1_sub}</span>'
                    if lang1_sub
                    else ""
                )
                + '<span style="color:#bbb;margin:0 8px;">竊・/span>'
                + f'<span style="font-size:0.92rem;color:#2d3436;">{lang2}</span>'
                + sub_html
                + "</div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("縺薙・遽・峇縺ｫ蜊倩ｪ槭′縺ゅｊ縺ｾ縺帙ｓ縲・)

    # 螳御ｺ・・繧ｿ繝ｳ
    st.markdown("---")
    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("竊・繝帙・繝", key="step1_back", use_container_width=True):
            st.session_state.flash_step = "home"
            st.rerun()
    with col_next:
        if st.button(
            f"当 縺薙・ {len(selected_words)} 蜊倩ｪ槭〒蟄ｦ鄙偵ｒ縺ｯ縺倥ａ繧・竊・,
            type="primary",
            use_container_width=True,
            key="step1_next",
            disabled=(len(selected_words) == 0),
        ):
            st.session_state.word_list_queue = selected_words
            st.session_state.selected_set_id = chosen_set_id
            st.session_state.flash_step = "list"
            st.rerun()


# ==========================================================
# 搭 STEP2: 蜊倩ｪ樔ｸ隕ｧ繝壹・繧ｸ・亥ｷｦ・壼撫鬘・/ 蜿ｳ・壼句挨繝医げ繝ｫ縺ｧ遲斐∴陦ｨ遉ｺ・・
# ==========================================================
def show_step2_list():
    words = st.session_state.get("word_list_queue", [])
    if not words:
        st.session_state.flash_step = "select"
        st.rerun()
        return

    def safe(v):
        return str(v) if v and str(v) not in ("None", "nan", "") else ""

    # 笏笏 繧ｻ繝・す繝ｧ繝ｳ蛻晄悄蛹・笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if st.session_state.get("fc_words_snapshot") != [w["id"] for w in words]:
        st.session_state["fc_index"] = 0
        st.session_state["fc_show_ans"] = False
        st.session_state["fc_known"] = []  # 遏･縺｣縺ｦ縺溘き繝ｼ繝迂D
        st.session_state["fc_unknown"] = []  # 遏･繧峨↑縺九▲縺溘き繝ｼ繝迂D
        st.session_state["fc_start_time"] = None
        st.session_state["fc_phase"] = "study"  # study / result / retry
        st.session_state["fc_retry_words"] = []
        st.session_state["fc_words_snapshot"] = [w["id"] for w in words]

    phase = st.session_state.get("fc_phase", "study")

    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤
    # PHASE: result・亥・繧ｫ繝ｼ繝牙ｮ御ｺ・ｾ後・邨先棡逕ｻ髱｢・・
    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤
    if phase == "result":
        known_ids = st.session_state.get("fc_known", [])
        unknown_ids = st.session_state.get("fc_unknown", [])
        total = len(known_ids) + len(unknown_ids)

        st.markdown("## 脂 邨先棡逋ｺ陦ｨ・・)
        st.markdown("---")

        col_k, col_u = st.columns(2)
        with col_k:
            st.markdown(
                f'<div style="background:#f0fff4;border-radius:12px;padding:20px;text-align:center;">'
                f'<div style="font-size:2rem;font-weight:bold;color:#00b894;">{len(known_ids)}</div>'
                f'<div style="font-size:0.9rem;color:#636e72;">笨・遏･縺｣縺ｦ縺・/div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with col_u:
            st.markdown(
                f'<div style="background:#fff5f5;border-radius:12px;padding:20px;text-align:center;">'
                f'<div style="font-size:2rem;font-weight:bold;color:#e17055;">{len(unknown_ids)}</div>'
                f'<div style="font-size:0.9rem;color:#636e72;">笶・遏･繧峨↑縺九▲縺・/div>'
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")

        if total > 0:
            pct = int(len(known_ids) / total * 100)
            st.progress(pct / 100)
            st.caption(f"豁｣遲皮紫・嘴pct}%縲・・len(known_ids)} / {total} 隱橸ｼ・)

        st.markdown("---")

        # 繝懊ち繝ｳ鄒､
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("竊・蜊倩ｪ槭ｒ驕ｸ縺ｳ逶ｴ縺・, use_container_width=True, key="res_back"):
                st.session_state.flash_step = "select"
                st.rerun()
        with col_b2:
            if unknown_ids:
                if st.button(
                    "煤 遏･繧峨↑縺九▲縺溷腰隱槭ｒ蜀肴倦謌ｦ",
                    use_container_width=True,
                    type="primary",
                    key="res_retry",
                ):
                    retry_words = [w for w in words if w["id"] in unknown_ids]
                    st.session_state["fc_retry_words"] = retry_words
                    st.session_state["fc_index"] = 0
                    st.session_state["fc_show_ans"] = False
                    st.session_state["fc_known"] = []
                    st.session_state["fc_unknown"] = []
                    st.session_state["fc_start_time"] = None
                    st.session_state["fc_phase"] = "retry"
                    st.session_state["fc_words_snapshot"] = None
                    st.rerun()
            else:
                st.success("蜈ｨ驛ｨ遏･縺｣縺ｦ縺滂ｼ∝ｮ檎挑縺ｧ縺咀沁・)
        with col_b3:
            if st.button("笨・蜊倩ｪ槭メ繧ｧ繝・け縺ｸ騾ｲ繧 竊・, use_container_width=True, key="res_next"):
                st.session_state["flash_queue"] = list(words)
                st.session_state["flash_index"] = 0
                st.session_state["flash_session_results"] = []
                st.session_state["flash_show_answer"] = False
                st.session_state["flash_mode"] = "study"
                st.session_state.flash_step = "study"
                st.rerun()
        return

    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤
    # PHASE: retry・育衍繧峨↑縺九▲縺溷腰隱槭・蜀肴倦謌ｦ・・
    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤
    if phase == "retry":
        words = st.session_state.get("fc_retry_words", [])
        if not words:
            st.session_state["fc_phase"] = "result"
            st.rerun()
            return

    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤
    # PHASE: study / retry 蜈ｱ騾夲ｼ医き繝ｼ繝芽｡ｨ遉ｺ・・
    # 笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤笏≫煤
    idx = st.session_state.get("fc_index", 0)
    show_ans = st.session_state.get("fc_show_ans", False)

    if idx >= len(words):
        st.session_state["fc_phase"] = "result"
        st.rerun()
        return

    w = words[idx]
    lang1 = safe(w.get("lang1", ""))
    lang1_sub = safe(w.get("lang1_sub", ""))
    lang2 = safe(w.get("lang2", ""))
    lang2_sub = safe(w.get("lang2_sub", ""))
    lang3 = safe(w.get("lang3", ""))
    lang3_sub = safe(w.get("lang3_sub", ""))
    item_no = w.get("item_no")
    page_val = safe(w.get("page_range", ""))

    # 繧ｿ繧､繝槭・髢句ｧ具ｼ医き繝ｼ繝芽｡ｨ遉ｺ譎ゑｼ・
    import time

    if st.session_state.get("fc_start_time") is None:
        st.session_state["fc_start_time"] = time.time()

    # 笏笏 繝倥ャ繝繝ｼ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    phase_label = "煤 蜀肴倦謌ｦ繝｢繝ｼ繝・ if phase == "retry" else "当 STEP 2繝ｻ繝輔Λ繝・す繝･繧ｫ繝ｼ繝・
    st.markdown(f"## {phase_label}")

    prog_col, count_col = st.columns([4, 1])
    with prog_col:
        st.progress((idx) / len(words))
    with count_col:
        st.markdown(
            f'<p style="text-align:right;font-size:0.9rem;color:#636e72;margin:0;">'
            f"{idx + 1} / {len(words)}</p>",
            unsafe_allow_html=True,
        )

    # 繝舌ャ繧ｸ
    badge_parts = []
    if page_val:
        badge_parts.append(f"塘 {page_val}")
    if item_no is not None:
        badge_parts.append(f"No.{item_no}")
    badge_str = "縲".join(badge_parts)

    st.markdown("---")

    # 笏笏 繧ｫ繝ｼ繝芽｡ｨ遉ｺ 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
    if not show_ans:
        # 陦ｨ髱｢・亥撫鬘鯉ｼ・
        st.markdown(
            f'<div style="background:#f0f4ff;border-radius:16px;padding:40px 32px;'
            f'text-align:center;min-height:200px;box-shadow:0 2px 8px rgba(76,110,245,0.10);">'
            f'<div style="font-size:0.75rem;color:#aaa;margin-bottom:12px;">{badge_str}</div>'
            f'<div style="font-size:2rem;font-weight:bold;color:#2d3436;letter-spacing:0.04em;">'
            f"{lang1}</div>"
            + (
                f'<div style="font-size:1rem;color:#888;margin-top:10px;">{lang1_sub}</div>'
                if lang1_sub
                else ""
            )
            + f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("")

        if st.button("早 遲斐∴繧定ｦ九ｋ", type="primary", use_container_width=True, key="fc_show"):
            st.session_state["fc_show_ans"] = True
            st.rerun()

    else:
        # 陬城擇・育ｭ斐∴・・
        elapsed = time.time() - st.session_state.get("fc_start_time", time.time())
        elapsed_str = f"{elapsed:.1f}遘・

        a_subs = [s for s in [lang2_sub, lang3, lang3_sub] if s]
        a_sub_html = "".join(
            f'<div style="font-size:0.85rem;color:#636e72;margin-top:6px;">{s}</div>'
            for s in a_subs
        )

        st.markdown(
            f'<div style="background:#f0fff4;border-radius:16px;padding:40px 32px;'
            f'text-align:center;min-height:200px;box-shadow:0 2px 8px rgba(0,184,148,0.10);">'
            f'<div style="font-size:0.75rem;color:#aaa;margin-bottom:12px;">{badge_str}</div>'
            f'<div style="font-size:1rem;color:#888;margin-bottom:8px;">{lang1}'
            + (f'縲<span style="font-size:0.85rem;">{lang1_sub}</span>' if lang1_sub else "")
            + f"</div>"
            f'<div style="font-size:2rem;font-weight:bold;color:#00b894;">{lang2}</div>'
            f"{a_sub_html}"
            f'<div style="font-size:0.75rem;color:#b2bec3;margin-top:16px;">竢ｱ {elapsed_str}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("")

        col_known, col_unknown = st.columns(2)
        with col_known:
            if st.button(
                "笨・遏･縺｣縺ｦ縺滂ｼ・,
                type="primary",
                use_container_width=True,
                key="fc_btn_known",
            ):
                st.session_state["fc_known"].append(w["id"])
                st.session_state["fc_index"] += 1
                st.session_state["fc_show_ans"] = False
                st.session_state["fc_start_time"] = None
                st.rerun()
        with col_unknown:
            if st.button("笶・遏･繧峨↑縺九▲縺・, use_container_width=True, key="fc_btn_unknown"):
                st.session_state["fc_unknown"].append(w["id"])
                st.session_state["fc_index"] += 1
                st.session_state["fc_show_ans"] = False
                st.session_state["fc_start_time"] = None
                st.rerun()

    st.markdown("---")
    if st.button("竊・蜊倩ｪ槭ｒ驕ｸ縺ｳ逶ｴ縺・, key="fc_back", use_container_width=False):
        st.session_state.flash_step = "select"
        st.rerun()


# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
# 逕ｻ髱｢繝ｫ繝ｼ繝・ぅ繝ｳ繧ｰ
# 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏
flash_step = st.session_state.get("flash_step", "home")

if flash_step == "select":
    show_step1_select()
elif flash_step == "list":
    show_step2_list()
elif st.session_state.get("flash_mode") == "time_attack":
    show_time_attack(username)
elif st.session_state.get("flash_mode") == "result":
    show_result()
elif st.session_state.get("flash_mode") == "ranking":
    show_ranking()
elif (
    flash_step == "study"
    or st.session_state.get("flash_mode") == "study"
) and st.session_state.get("flash_mode") != "home":
    show_study(username)
else:
    show_home(username)













