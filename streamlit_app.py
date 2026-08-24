import random
import streamlit as st
from utils import TEXTS, init_sidebar, load_champions, load_leaderboard, save_score

st.set_page_config(page_title="LoL Quiz", page_icon="⚔️", layout="centered")

t, player_name = init_sidebar()
champions, version = load_champions(st.session_state.lang)

if not champions:
    st.stop()

def generate_round_options(champions_pool):
    correct = random.choice(champions_pool)
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