import json
import os
import random
import requests
import streamlit as st

st.set_page_config(page_title="LoL Champion Quiz & Study", page_icon="⚔️", layout="centered")

LEADERBOARD_FILE = "leaderboard.json"

# --- ТЕКСТИ ІНТЕРФЕЙСУ ---
TEXTS = {
    "uk": {
        "title": "⚔️ League of Legends Quiz & Learn",
        "tab_game": "🎮 Квіз",
        "tab_study": "📚 Навчання (Quizlet)",
        "round": "Раунд",
        "score": "Бали",
        "mistakes": "Помилки",
        "streak": "Серія",
        "who_is_this": "Хто це на малюнку?",
        "find_photo": "Знайдіть фото для чемпіона",
        "choose": "Обрати",
        "correct": "Правильно!",
        "wrong": "Невірно. Правильна відповідь:",
        "next": "Наступний раунд ➡️",
        "game_over": "🎮 Гра завершена!",
        "restart": "Зіграти знову 🔄",
        "leaderboard": "🏆 Таблиця рекордів",
        "enter_name": "Ваше ім'я",
        "lang_label": "Мова / Language",
        "max_rounds": "Досягнуто ліміт 20 раундів!",
        "max_mistakes": "Ви припустилися 3 помилок!",
        "final_score": "Ваш підсумковий результат:",
        "filter_role": "Фільтр за роллю:",
        "all_roles": "Усі ролі",
        "show_card": "👁️ Перевернути картку",
        "hide_card": "🙈 Сховати деталі",
        "next_card": "Наступна картка ➡️",
        "prev_card": "⬅️ Попередня картка",
        "random_card": "🎲 Випадкова картка",
        "title_label": "Титул",
        "tags_label": "Роль",
    },
    "en": {
        "title": "⚔️ League of Legends Quiz & Learn",
        "tab_game": "🎮 Quiz",
        "tab_study": "📚 Study (Quizlet)",
        "round": "Round",
        "score": "Score",
        "mistakes": "Mistakes",
        "streak": "Streak",
        "who_is_this": "Who is this champion?",
        "find_photo": "Find the photo for champion",
        "choose": "Select",
        "correct": "Correct!",
        "wrong": "Wrong. Correct answer:",
        "next": "Next Round ➡️",
        "game_over": "🎮 Game Over!",
        "restart": "Play Again 🔄",
        "leaderboard": "🏆 Leaderboard",
        "enter_name": "Your Name",
        "lang_label": "Language / Мова",
        "max_rounds": "Maximum 20 rounds reached!",
        "max_mistakes": "You made 3 mistakes!",
        "final_score": "Your final score:",
        "filter_role": "Filter by role:",
        "all_roles": "All Roles",
        "show_card": "👁️ Flip Card",
        "hide_card": "🙈 Hide Details",
        "next_card": "Next Card ➡️",
        "prev_card": "⬅️ Previous Card",
        "random_card": "🎲 Random Card",
        "title_label": "Title",
        "tags_label": "Role",
    },
}

# --- ЗБЕРЕЖЕННЯ РЕКОРДІВ ---
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_score(name, score):
    board = load_leaderboard()
    player_name = name.strip()[:15] if name.strip() else "Гравець"
    board.append({"name": player_name, "score": score})
    board = sorted(board, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)

# --- ЗАВАНТАЖЕННЯ ДАНИХ RITO DRAGON ---
@st.cache_data
def load_champions(lang):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        versions = requests.get(version_url, headers=headers).json()
        latest_version = versions[0]

        locale = "uk_UA" if lang == "uk" else "en_US"
        url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/{locale}/champion.json"
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
            res = requests.get(url, headers=headers)

        data = res.json()["data"]
        champions_list = []
        for k, v in data.items():
            champions_list.append({
                "id": k,
                "name": v["name"],
                "title": v.get("title", ""),
                "tags": v.get("tags", []),
                "blurb": v.get("blurb", "")
            })
        return champions_list, latest_version
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return [], "14.1.1"

# --- АЛГОРИТМ РОЗУМНОГО ПІДБОРУ ВАРІАНТІВ ---
def generate_round_options(champions_pool):
    correct = random.choice(champions_pool)
    # Шукаємо чемпіонів зі схожою роллю (Mage, Fighter, Tank тощо)
    same_tag_champs = [
        c for c in champions_pool 
        if c["id"] != correct["id"] and any(t in correct.get("tags", []) for t in c.get("tags", []))
    ]
    
    if len(same_tag_champs) >= 3:
        distractors = random.sample(same_tag_champs, 3)
    else:
        other_champs = [c for c in champions_pool if c["id"] != correct["id"]]
        distractors = random.sample(other_champs, 3)

    options = distractors + [correct]
    random.shuffle(options)
    return options, correct

# --- СТАН ДАНИХ ---
if "lang" not in st.session_state:
    st.session_state.lang = "uk"

t = TEXTS[st.session_state.lang]

with st.sidebar:
    selected_lang = st.radio(
        t["lang_label"],
        options=["uk", "en"],
        format_func=lambda x: "Українська 🇺🇦" if x == "uk" else "English 🇬🇧",
        index=0 if st.session_state.lang == "uk" else 1,
    )
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

    player_name = st.text_input(t["enter_name"], value="Гравець", max_chars=15)

champions, version = load_champions(st.session_state.lang)
if not champions:
    st.stop()

def reset_game():
    opts, corr = generate_round_options(champions)
    st.session_state.score = 0
    st.session_state.round = 1
    st.session_state.mistakes = 0
    st.session_state.streak = 0
    st.session_state.game_over = False
    st.session_state.score_saved = False
    st.session_state.answered = False
    st.session_state.selected_id = None
    st.session_state.options = opts
    st.session_state.correct = corr

if "round" not in st.session_state:
    reset_game()

def get_multiplier(streak):
    if streak >= 5: return 3.0
    if streak >= 3: return 2.0
    if streak >= 2: return 1.5
    return 1.0

def make_choice(opt_id):
    st.session_state.answered = True
    st.session_state.selected_id = opt_id
    if opt_id == st.session_state.correct["id"]:
        st.session_state.streak += 1
        mult = get_multiplier(st.session_state.streak)
        st.session_state.score += int(100 * mult)
    else:
        st.session_state.mistakes += 1
        st.session_state.streak = 0

def next_round():
    if st.session_state.round >= 20 or st.session_state.mistakes >= 3:
        st.session_state.game_over = True
    else:
        opts, corr = generate_round_options(champions)
        st.session_state.options = opts
        st.session_state.correct = corr
        st.session_state.round += 1
        st.session_state.answered = False
        st.session_state.selected_id = None

# --- ВКЛАДКИ РЕЖИМІВ (ГРА / НАВЧАННЯ) ---
tab_game, tab_study = st.tabs([t["tab_game"], t["tab_study"]])

# ==================== ВКЛАДКА 1: КВІЗ ====================
with tab_game:
    st.title(t["title"])

    if st.session_state.game_over or st.session_state.mistakes >= 3:
        if not st.session_state.get("score_saved", False):
            save_score(player_name, st.session_state.score)
            st.session_state.score_saved = True

        reason = t["max_mistakes"] if st.session_state.mistakes >= 3 else t["max_rounds"]
        st.error(f"{t['game_over']} ({reason})")
        st.subheader(f"{t['final_score']} **{st.session_state.score}**")

        st.divider()
        st.subheader(t["leaderboard"])
        board = load_leaderboard()
        if board:
            for idx, entry in enumerate(board, start=1):
                st.write(f"**{idx}. {entry['name']}** — {entry['score']} pts")

        if st.button(t["restart"], type="primary", use_container_width=True):
            reset_game()
            st.rerun()

    else:
        current_mult = get_multiplier(st.session_state.streak)
        lives_icons = "❤️" * (3 - st.session_state.mistakes) + "🖤" * st.session_state.mistakes

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t["round"], f"{st.session_state.round} / 20")
        col2.metric(t["score"], st.session_state.score)
        col3.metric(t["streak"], f"🔥 {st.session_state.streak}", f"x{current_mult}" if st.session_state.streak > 1 else None)
        col4.metric(t["mistakes"], lives_icons)

        st.divider()

        correct = st.session_state.correct
        options = st.session_state.options
        answered = st.session_state.answered
        selected_id = st.session_state.selected_id
        is_photo_to_name = st.session_state.round % 2 != 0

        if is_photo_to_name:
            st.subheader(t["who_is_this"])
            img_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{correct['id']}.png"

            c1, c2, c3 = st.columns([1, 1, 1])
            with c2:
                st.image(img_url, width=150)

            cols = st.columns(2)
            for idx, opt in enumerate(options):
                with cols[idx % 2]:
                    if not answered:
                        if st.button(opt["name"], key=f"btn_{opt['id']}", use_container_width=True):
                            make_choice(opt["id"])
                            st.rerun()
                    else:
                        if opt["id"] == correct["id"]:
                            st.markdown(f"<div style='background-color:#1e4620; color:#4caf50; border:2px solid #4caf50; padding:10px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:10px;'>✓ {opt['name']}</div>", unsafe_allow_html=True)
                        elif opt["id"] == selected_id:
                            st.markdown(f"<div style='background-color:#4a1c1d; color:#f44336; border:2px solid #f44336; padding:10px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:10px;'>✗ {opt['name']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='background-color:#212121; color:#757575; border:1px solid #333; padding:10px; border-radius:8px; text-align:center; margin-bottom:10px;'>{opt['name']}</div>", unsafe_allow_html=True)
        else:
            st.subheader(f"{t['find_photo']}: **{correct['name']}**")
            cols = st.columns(4)
            for idx, opt in enumerate(options):
                img_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{opt['id']}.png"
                with cols[idx]:
                    if not answered:
                        st.image(img_url, use_container_width=True)
                        if st.button(t["choose"], key=f"img_btn_{opt['id']}", use_container_width=True):
                            make_choice(opt["id"])
                            st.rerun()
                    else:
                        if opt["id"] == correct["id"]:
                            border_style = "border: 4px solid #4caf50; box-shadow: 0 0 12px #4caf50; border-radius: 10px;"
                        elif opt["id"] == selected_id:
                            border_style = "border: 4px solid #f44336; box-shadow: 0 0 12px #f44336; border-radius: 10px;"
                        else:
                            border_style = "opacity: 0.3;"

                        st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><img src='{img_url}' style='width:100%; {border_style}'></div>", unsafe_allow_html=True)

        if answered:
            st.write("")
            if selected_id == correct["id"]:
                st.success(f"{t['correct']} (+{int(100 * get_multiplier(st.session_state.streak))} pts)")
            else:
                st.error(f"{t['wrong']} {correct['name']}")

            if st.button(t["next"], type="primary", use_container_width=True):
                next_round()
                st.rerun()

# ==================== ВКЛАДКА 2: НАВЧАННЯ (QUIZLET) ====================
with tab_study:
    st.title(t["tab_study"])
    
    if "card_idx" not in st.session_state:
        st.session_state.card_idx = 0
    if "card_flipped" not in st.session_state:
        st.session_state.card_flipped = False

    # Фільтрація за ролями
    all_tags = sorted(list({tag for c in champions for tag in c.get("tags", [])}))
    selected_role = st.selectbox(t["filter_role"], [t["all_roles"]] + all_tags)

    filtered_champs = champions
    if selected_role != t["all_roles"]:
        filtered_champs = [c for c in champions if selected_role in c.get("tags", [])]

    if not filtered_champs:
        st.warning("Чемпіонів не знайдено.")
    else:
        st.session_state.card_idx %= len(filtered_champs)
        champ = filtered_champs[st.session_state.card_idx]

        # Великий сплеш-арт для картки Quizlet
        splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ['id']}_0.jpg"
        
        st.markdown(f"**Картка {st.session_state.card_idx + 1} з {len(filtered_champs)}**")
        
        # Відображення картинки картки
        st.image(splash_url, use_container_width=True)

        # Перевертання картки
        if st.button(t["hide_card"] if st.session_state.card_flipped else t["show_card"], use_container_width=True):
            st.session_state.card_flipped = not st.session_state.card_flipped
            st.rerun()

        if st.session_state.card_flipped:
            st.info(f"### {champ['name']}\n*{champ['title'].capitalize()}*")
            st.write(f"**{t['tags_label']}:** {', '.join(champ.get('tags', []))}")
            st.caption(champ.get("blurb", ""))

        st.divider()

        # Навігація карток
        n_col1, n_col2, n_col3 = st.columns(3)
        with n_col1:
            if st.button(t["prev_card"], use_container_width=True):
                st.session_state.card_idx = (st.session_state.card_idx - 1) % len(filtered_champs)
                st.session_state.card_flipped = False
                st.rerun()
        with n_col2:
            if st.button(t["random_card"], use_container_width=True):
                st.session_state.card_idx = random.randint(0, len(filtered_champs) - 1)
                st.session_state.card_flipped = False
                st.rerun()
        with n_col3:
            if st.button(t["next_card"], use_container_width=True):
                st.session_state.card_idx = (st.session_state.card_idx + 1) % len(filtered_champs)
                st.session_state.card_flipped = False
                st.rerun()