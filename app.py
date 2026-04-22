import streamlit as st
from openai import OpenAI
import os, json

# Инициализация OpenAI-клиента (ключ из окружения или файла secrets)



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Профориентация", layout="centered")
st.title("🧠 AI-Профориентация нового поколения")

# =========================
# Инициализация памяти сессии
# =========================
if "profile" not in st.session_state:
    st.session_state.profile = None  # сюда запишем текст профиля после анализа
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # история переписки

# =========================
# 1. Ввод данных: имя и фото
# =========================
name = st.text_input("Введите ваше имя")
photo = st.file_uploader("Загрузите ваше фото (по желанию)", type=["jpg", "png"])

st.write("---")
# =========================
# 2. Психологический тест (пример)
# =========================
st.subheader("🧠 Психологический тест (RIASEC + Big Five)")

# RIASEC-пример вопросов
q1 = st.radio("Любите ли вы работать с техникой и инструментами?", ["Да", "Нет", "Не знаю"])
q2 = st.radio("Нравится ли вам решать научно-аналитические задачи?", ["Да", "Нет", "Не знаю"])
q3 = st.radio("Предпочитаете ли вы творческие или художественные занятия?", ["Да", "Нет", "Не знаю"])
q4 = st.radio("Вы получаете удовольствие, помогая другим людям?", ["Да", "Нет", "Не знаю"])
q5 = st.radio("Считаете ли вы себя лидером (часто берёте на себя инициативу)?", ["Да", "Нет", "Не знаю"])
q6 = st.radio("Предпочитаете ли вы чёткие инструкции и правила в работе?", ["Да", "Нет", "Не знаю"])

st.write("*(Добавьте остальные вопросы RIASEC и Big Five по аналогии)*")

st.write("---")
# =========================
# 3. Логический тест
# =========================
st.subheader("🧩 Логическое мышление")

l1 = st.radio("1) Последовательность: 2, 4, 8, 16, ?", ["32", "24", "18"])
l2 = st.radio("2) Лишнее слово: Кошка, Собака, Стол.", ["Стол", "Кошка", "Собака"])
l3 = st.radio("3) Если A > B и B > C, то:", ["A > C", "C > A", "Нельзя определить"])
l4 = st.radio("4) Последовательность: 3, 6, 12, 24, ?", ["36", "48", "30"])
l5 = st.radio("5) Если сегодня среда, то через три дня будет:", ["Суббота", "Воскресенье", "Понедельник"])
l6 = st.radio("6) Если все A — B и все B — C, то:", ["Все A — C", "Все C — A", "Нельзя определить"])
# (Добавьте задачи до 10 по аналогии)

st.write("---")
# =========================
# 4. Кнопка запуска анализа
# =========================
if st.button("🔍 Получить анализ"):

    # Собираем ответы в текстовый блок для GPT
    answers = f"Имя: {name}\n" \
              f"RIASEC-вопросы:\n- {q1}\n- {q2}\n- {q3}\n- {q4}\n- {q5}\n- {q6}\n" \
              f"Логические задачи: {l1}, {l2}, {l3}, {l4}, {l5}, {l6}\n"

    # Готовим промпт для анализа профиля
    prompt = f"""
Ты — AI-консультант по профориентации.
Проанализируй пользователя по данным:
{answers}
Укажи:
1. Общий анализ личности (RIASEC, Big Five) и потенциал.
2. Сделай профессионально оформленный психологический разбор и анализ по физиогномике(с пометкой, что это гипотеза).
3. Сильные стороны.
4. Слабые стороны.
5. RIASEC-тип личности.
6. 3-5 подходящих профессий или направлений.
7. Рекомендуемые университеты и их контакты (Казахстан и по всему миру).
8. План развития.
Дай структурированный ответ с пунктами.
"""

    # Вызываем OpenAI ChatCompletion
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # можно заменить на gpt-3.5-turbo или другой
        messages=[{"role": "user", "content": prompt}]
    )
    result_text = response.choices[0].message.content

    # Сохраняем сгенерированный профиль в сессию
    st.session_state.profile = result_text

    st.subheader("📊 Результат анализа")
    st.write(result_text)

# =========================
# 5. Персональный чат с ботом
# =========================
if st.session_state.profile:
    st.subheader("💬 Персональный AI-чат (задать вопросы)")
    user_input = st.text_input("Введите вопрос или команду (например: 'Куда мне поступать?')")
    if st.button("Отправить"):
        # Формируем контекст для ChatGPT: профиль + история + новый вопрос
        messages = [
            {"role": "system", "content": f"""
Ты — карьерный AI-наставник. У тебя есть профиль пользователя:
{st.session_state.profile}
Отвечай только на основе этого профиля и знаний. Давай персональные советы.
""".strip()}
        ]
        # Добавляем предыдущую историю чата
        for msg in st.session_state.chat_history:
            messages.append(msg)
        # Добавляем вопрос пользователя
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        answer = response.choices[0].message.content

        # Сохраняем в историю
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Выводим историю диалога
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.write(f"👤 **Вы:** {msg['content']}")
        else:
            st.write(f"🤖 **AI:** {msg['content']}")
