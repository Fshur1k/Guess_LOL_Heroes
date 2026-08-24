import random
import streamlit as st
from utils import init_sidebar, load_champions

st.set_page_config(page_title="Study Mode", page_icon="📚", layout="centered")

t, _ = init_sidebar()
champions, version = load_champions(st.session_state.lang)

# Додаткові тексти для Quizlet-режиму (адаптивні під мову)
is_uk = st.session_state.lang == "uk"
t_batch_size = "Розмір порції (карток):" if is_uk else "Batch size (cards):"
t_start = "🚀 Почати навчання" if is_uk else "🚀 Start Learning"
t_know = "✅ Знаю" if is_uk else "✅ Know it"
t_learn = "🔄 Ще вчу" if is_uk else "🔄 Still learning"
t_batch_done = "🎉 Порцію вивчено!" if is_uk else "🎉 Batch complete!"
t_next_batch = "Наступна порція ➡️" if is_uk else "Next Batch ➡️"
t_all_done = "🏆 Ви вивчили всіх чемпіонів у цій категорії!" if is_uk else "🏆 You learned all champions in this category!"
t_restart = "Почати заново 🔄" if is_uk else "Restart 🔄"
t_left_in_batch = "Залишилось у поточній порції:" if is_uk else "Left in current batch:"
t_total_progress = "Загальний прогрес:" if is_uk else "Total progress:"
t_stop = "🛑 Зупинити навчання" if is_uk else "🛑 Stop Learning"

st.title(t["study_title"])

# Ініціалізація нових станів для Quizlet-логіки
if "quizlet_active" not in st.session_state:
    st.session_state.quizlet_active = False
if "card_flipped" not in st.session_state:
    st.session_state.card_flipped = False

def reset_learning():
    """Скидає прогрес навчання та повертає до вибору категорії"""
    st.session_state.quizlet_active = False
    st.session_state.unseen = []
    st.session_state.queue = []
    st.session_state.learned_count = 0
    st.session_state.card_flipped = False

def load_next_batch():
    """Бере наступну порцію невідкритих карток і додає їх у чергу"""
    batch_size = st.session_state.batch_size
    new_batch = st.session_state.unseen[:batch_size]
    st.session_state.unseen = st.session_state.unseen[batch_size:]
    st.session_state.queue = new_batch
    st.session_state.card_flipped = False

# ==========================================
# 1. ЕКРАН НАЛАШТУВАНЬ (ДО ПОЧАТКУ)
# ==========================================
if not st.session_state.quizlet_active:
    all_tags = sorted(list({tag for c in champions for tag in c.get("tags", [])}))
    selected_role = st.selectbox(t["filter_role"], [t["all_roles"]] + all_tags)

    filtered_champs = champions
    if selected_role != t["all_roles"]:
        filtered_champs = [c for c in champions if selected_role in c.get("tags", [])]

    # Вибір розміру порції
    st.session_state.batch_size = st.slider(t_batch_size, min_value=5, max_value=20, value=10, step=5)

    if not filtered_champs:
        st.warning("Чемпіонів не знайдено." if is_uk else "No champions found.")
    else:
        st.write(f"Усього карток у категорії: **{len(filtered_champs)}**")
        
        if st.button(t_start, type="primary", use_container_width=True):
            # Запускаємо систему навчання
            random.shuffle(filtered_champs) # Перемішуємо, щоб не вчити за алфавітом
            st.session_state.unseen = filtered_champs
            st.session_state.total_in_category = len(filtered_champs)
            st.session_state.learned_count = 0
            
            load_next_batch()
            st.session_state.quizlet_active = True
            st.rerun()

# ==========================================
# 2. РЕЖИМ НАВЧАННЯ (КАРТКИ)
# ==========================================
else:
    # Верхня панель: Прогрес бар та кнопка зупинки
    c1, c2 = st.columns([3, 1])
    with c1:
        progress_val = st.session_state.learned_count / st.session_state.total_in_category
        st.progress(progress_val, text=f"{t_total_progress} {st.session_state.learned_count} / {st.session_state.total_in_category}")
    with c2:
        if st.button(t_stop, use_container_width=True):
            reset_learning()
            st.rerun()
            
    st.divider()

    # Сценарій А: Черга порожня
    if len(st.session_state.queue) == 0:
        if len(st.session_state.unseen) == 0:
            # Вивчили взагалі все
            st.success(t_all_done)
            st.balloons()
            if st.button(t_restart, type="primary", use_container_width=True):
                reset_learning()
                st.rerun()
        else:
            # Вивчили порцію, є ще слова
            st.success(t_batch_done)
            if st.button(t_next_batch, type="primary", use_container_width=True):
                load_next_batch()
                st.rerun()
                
    # Сценарій Б: У черзі ще є картки
    else:
        champ = st.session_state.queue[0] # Завжди беремо першу картку з черги
        
        st.caption(f"{t_left_in_batch} {len(st.session_state.queue)}")
        splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ['id']}_0.jpg"
        st.image(splash_url, use_container_width=True)

        if not st.session_state.card_flipped:
            # Лицьова сторона
            if st.button(t["show_card"], type="primary", use_container_width=True):
                st.session_state.card_flipped = True
                st.rerun()
        else:
            # Зворотня сторона (Інформація)
            st.info(f"### {champ['name']}\n*{champ['title'].capitalize()}*")
            st.write(f"**{t['primary_pos']}:** `{champ['primary_pos']}`")
            flex_text = ", ".join(champ["flex_pos"]) if champ["flex_pos"] else t["no_flex"]
            st.write(f"**{t['flex_pos']}:** {flex_text}")
            st.write(f"**{t['tags_label']}:** {', '.join(champ.get('tags', []))}")

            st.write("")
            bc1, bc2 = st.columns(2)
            with bc1:
                # Кнопка "Ще вчу"
                if st.button(t_learn, use_container_width=True):
                    # Видаляємо з початку і ставимо в кінець черги (крутимо по колу)
                    st.session_state.queue.append(st.session_state.queue.pop(0))
                    st.session_state.card_flipped = False
                    st.rerun()
            with bc2:
                # Кнопка "Знаю"
                if st.button(t_know, type="primary", use_container_width=True):
                    # Видаляємо з черги назавжди
                    st.session_state.queue.pop(0)
                    st.session_state.learned_count += 1
                    st.session_state.card_flipped = False
                    st.rerun()