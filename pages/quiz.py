import random
import streamlit as st
from utils import init_sidebar, load_champions

st.set_page_config(page_title="Study Mode", page_icon="📚", layout="centered")

t, _ = init_sidebar()
champions, version = load_champions(st.session_state.lang)

st.title(t["study_title"])

if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "card_flipped" not in st.session_state:
    st.session_state.card_flipped = False

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

    splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ['id']}_0.jpg"
    
    st.markdown(f"**Картка {st.session_state.card_idx + 1} з {len(filtered_champs)}**")
    st.image(splash_url, use_container_width=True)

    if st.button(t["hide_card"] if st.session_state.card_flipped else t["show_card"], use_container_width=True):
        st.session_state.card_flipped = not st.session_state.card_flipped
        st.rerun()

    if st.session_state.card_flipped:
        st.info(f"### {champ['name']}\n*{champ['title'].capitalize()}*")
        st.write(f"**{t['primary_pos']}:** `{champ['primary_pos']}`")
        
        flex_text = ", ".join(champ["flex_pos"]) if champ["flex_pos"] else t["no_flex"]
        st.write(f"**{t['flex_pos']}:** {flex_text}")
        st.write(f"**{t['tags_label']}:** {', '.join(champ.get('tags', []))}")

    st.divider()

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