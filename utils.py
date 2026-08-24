import json
import os
import requests
import streamlit as st

LEADERBOARD_FILE = "leaderboard.json"

POSITION_OVERRIDES = {
    "LeeSin": {"primary": "Jungle", "flex": []},
    "MasterYi": {"primary": "Jungle", "flex": []},
    "Warwick": {"primary": "Jungle", "flex": ["Top"]},
    "Khazix": {"primary": "Jungle", "flex": []},
    "Graves": {"primary": "Jungle", "flex": ["Top"]},
    "Vi": {"primary": "Jungle", "flex": []},
    "JarvanIV": {"primary": "Jungle", "flex": []},
    "Shaco": {"primary": "Jungle", "flex": ["Support"]},
    "Hecarim": {"primary": "Jungle", "flex": []},
    "Evelynn": {"primary": "Jungle", "flex": []},
    "Kayn": {"primary": "Jungle", "flex": []},
    "Viego": {"primary": "Jungle", "flex": ["Mid"]},
    "Nidalee": {"primary": "Jungle", "flex": []},
    "Elise": {"primary": "Jungle", "flex": []},
    "Kindred": {"primary": "Jungle", "flex": []},
    "Fiddlesticks": {"primary": "Jungle", "flex": []},
    "Rengar": {"primary": "Jungle", "flex": ["Top"]},
    "Nocturne": {"primary": "Jungle", "flex": []},
    "Amumu": {"primary": "Jungle", "flex": ["Support"]},
    "Nunu": {"primary": "Jungle", "flex": []},
    "Zac": {"primary": "Jungle", "flex": ["Top", "Support"]},
    "Rammus": {"primary": "Jungle", "flex": []},
    "Volibear": {"primary": "Jungle", "flex": ["Top"]},
    "Udyr": {"primary": "Jungle", "flex": ["Top"]},
    "Belveth": {"primary": "Jungle", "flex": []},
    "Briar": {"primary": "Jungle", "flex": []},
    "Ivern": {"primary": "Jungle", "flex": []},
    "Swain": {"primary": "Support", "flex": ["Mid", "Bot (ADC)"]},
    "Lux": {"primary": "Support", "flex": ["Mid"]},
    "Morgana": {"primary": "Support", "flex": ["Mid", "Jungle"]},
    "Yasuo": {"primary": "Mid", "flex": ["Top", "Bot (ADC)"]},
    "Yone": {"primary": "Mid", "flex": ["Top"]},
    "Pantheon": {"primary": "Support", "flex": ["Top", "Mid"]},
    "Sett": {"primary": "Top", "flex": ["Support", "Mid"]},
    "Jayce": {"primary": "Top", "flex": ["Mid"]},
    "Gragas": {"primary": "Top", "flex": ["Jungle", "Mid"]},
    "TahmKench": {"primary": "Support", "flex": ["Top"]},
    "Malphite": {"primary": "Top", "flex": ["Mid", "Support"]},
    "Karma": {"primary": "Support", "flex": ["Mid", "Top"]},
    "Seraphine": {"primary": "Support", "flex": ["Bot (ADC)", "Mid"]},
    "Senna": {"primary": "Support", "flex": ["Bot (ADC)"]},
    "Tristana": {"primary": "Bot (ADC)", "flex": ["Mid"]},
    "Lucian": {"primary": "Bot (ADC)", "flex": ["Mid"]},
    "Vayne": {"primary": "Bot (ADC)", "flex": ["Top"]},
    "Varus": {"primary": "Bot (ADC)", "flex": ["Mid"]},
    "Kaisa": {"primary": "Bot (ADC)", "flex": ["Mid"]},
    "Brand": {"primary": "Support", "flex": ["Jungle", "Mid"]},
    "Zyra": {"primary": "Support", "flex": ["Jungle"]},
    "Velkoz": {"primary": "Support", "flex": ["Mid"]},
    "Xerath": {"primary": "Support", "flex": ["Mid"]},
    "Pyke": {"primary": "Support", "flex": ["Mid"]},
    "Nautilus": {"primary": "Support", "flex": []},
    "Thresh": {"primary": "Support", "flex": []},
    "Blitzcrank": {"primary": "Support", "flex": []},
    "Leona": {"primary": "Support", "flex": []},
    "Lulu": {"primary": "Support", "flex": []},
    "Nami": {"primary": "Support", "flex": []},
    "Janna": {"primary": "Support", "flex": []},
    "Yuumi": {"primary": "Support", "flex": []},
    "Sona": {"primary": "Support", "flex": []},
    "Soraka": {"primary": "Support", "flex": []},
    "Milio": {"primary": "Support", "flex": []},
    "Renata": {"primary": "Support", "flex": []},
    "Rakan": {"primary": "Support", "flex": []},
}

TEXTS = {
    "uk": {
        "title": "⚔️ League of Legends Quiz",
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
        "study_title": "📚 Навчання (Quizlet)",
        "filter_role": "Фільтр за роллю:",
        "all_roles": "Усі ролі",
        "show_card": "👁️ Перевернути картку",
        "hide_card": "🙈 Сховати деталі",
        "next_card": "Наступна картка ➡️",
        "prev_card": "⬅️ Попередня картка",
        "random_card": "🎲 Випадкова картка",
        "primary_pos": "Основна позиція",
        "flex_pos": "Flex / Інші варіанти",
        "no_flex": "Спеціалізований пик (немає)",
        "tags_label": "Класс",
    },
    "en": {
        "title": "⚔️ League of Legends Quiz",
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
        "study_title": "📚 Study Mode (Quizlet)",
        "filter_role": "Filter by role:",
        "all_roles": "All Roles",
        "show_card": "👁️ Flip Card",
        "hide_card": "🙈 Hide Details",
        "next_card": "Next Card ➡️",
        "prev_card": "⬅️ Previous Card",
        "random_card": "🎲 Random Card",
        "primary_pos": "Primary Position",
        "flex_pos": "Flex / Other Positions",
        "no_flex": "Specialized Pick (None)",
        "tags_label": "Class",
    },
}

def get_champion_positions(champ_id, tags):
    if champ_id in POSITION_OVERRIDES:
        return POSITION_OVERRIDES[champ_id]["primary"], POSITION_OVERRIDES[champ_id]["flex"]
    if "Marksman" in tags:
        return "Bot (ADC)", []
    elif "Support" in tags:
        return "Support", ["Mid"] if "Mage" in tags else []
    elif "Assassin" in tags:
        return "Mid", ["Jungle"]
    elif "Mage" in tags:
        return "Mid", ["Support"]
    elif "Fighter" in tags:
        return "Top", ["Jungle"]
    elif "Tank" in tags:
        return "Top", ["Support"]
    return "Mid", []

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
            tags = v.get("tags", [])
            primary_pos, flex_pos = get_champion_positions(k, tags)
            champions_list.append({
                "id": k,
                "name": v["name"],
                "title": v.get("title", ""),
                "tags": tags,
                "primary_pos": primary_pos,
                "flex_pos": flex_pos
            })
        return champions_list, latest_version
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return [], "14.1.1"

def init_sidebar():
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

    return t, player_name