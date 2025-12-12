import time
import streamlit as st
import google.generativeai as genai

# =========================
# 0) PAGE CONFIG (DEBE SER LO PRIMERO)
# =========================
st.set_page_config(
    page_title="JHG Bin Wash – Asistente",
    page_icon="🧼",
)

# =========================
# 1) ESTILO (OCULTAR MENÚ/FOOTER)
# =========================
HIDE_STYLE = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(HIDE_STYLE, unsafe_allow_html=True)

# =========================
# 2) UI
# =========================
st.title("🧼 JHG Bin Wash – Asistente")
st.write("Pregúntame sobre horarios, cobertura o servicios.")

# =========================
# 3) SECRETS
# =========================
api_key = st.secrets["GOOGLE_API_KEY"]

# =========================
# 4) “BIBLIA” (LIVIANA Y CONTROLADA)
#    - NO se manda completa siempre (ahorra tokens)
# =========================
LYRA_SYSTEM = """
You are Lyra, the virtual assistant of JHG Bin Wash (Santaquin, Utah).
Your job is to help the community with info about services, coverage areas, and general questions.

Rules:
- Be friendly, clear, and concise (2–4 short sentences max).
- If the user writes in Spanish, respond in Spanish. If in English, respond in English.
- Do NOT mention prices unless the user explicitly asks for pricing.
- If the user asks to book/schedule, you cannot book directly: guide them to contact via WhatsApp or email.
- If you don’t know something, say so and offer the best next step.
"""

JHG_FACTS = """
Business: JHG Bin Wash (Santaquin, Utah).
Service: trash bin cleaning / deodorizing / community-focused help.
Contact:
- WhatsApp: +1 (801) 228-7260
- Email: contact@jhgbinwash.com
"""

# =========================
# 5) INIT CHAT ONCE (NO LOOPS)
# =========================
if "chat" not in st.session_state:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    st.session_state.chat = model.start_chat(history=[])

    st.session_state.messages = []
    st.session_state.last_call = 0.0
    st.session_state.turns = 0

    # Bienvenida (NO usa IA)
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hola 👋 Soy **Lyra**, la asistente virtual de **JHG Bin Wash**. ¿En qué puedo ayudarte?"
    })

# =========================
# 6) RENDER HISTORIAL
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# =========================
# 7) INPUT
# =========================
prompt = st.chat_input("Escribe tu pregunta aquí…")

if prompt:
    # Mostrar user msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # -------------------------
    # PREFILTRO (SIN IA)
    # -------------------------
    t = prompt.lower().strip()

    # Saludos / mensajes cortos (no llamar IA)
    if any(w in t for w in ["hola", "buenas", "hey", "hi", "gracias", "thank you"]):
        respuesta = "¡Hola! 😊 Dime qué necesitas saber sobre JHG Bin Wash (zona, servicios, cómo funciona, etc.)."
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        with st.chat_message("assistant"):
            st.write(respuesta)
        st.stop()

    # -------------------------
    # COOLDOWN (ANTI 429)
    # -------------------------
    if time.time() - st.session_state.last_call < 8:
        with st.chat_message("assistant"):
            st.write("⏳ Dame unos segundos antes de la siguiente pregunta para evitar límites del sistema.")
        st.stop()

    st.session_state.last_call = time.time()
    st.session_state.turns += 1

    # -------------------------
    # CONTEXTO CONTROLADO (AHORRO DE TOKENS)
    # - Enviamos LYRA_SYSTEM + FACTS solo en el primer turno o cada 6 turnos
    # - Enviamos solo últimos 6 mensajes del chat como contexto
    # -------------------------
    contexto = ""
    if st.session_state.turns == 1 or (st.session_state.turns % 6 == 0):
        contexto = LYRA_SYSTEM + "\n" + JHG_FACTS + "\n"

    # Últimos mensajes (memoria corta)
    recent = st.session_state.messages[-6:]
    history_text = ""
    for m in recent:
        role = "User" if m["role"] == "user" else "Assistant"
        history_text += f"{role}: {m['content']}\n"

    # -------------------------
    # LLAMADA ÚNICA A GEMINI
    # -------------------------
    try:
        response = st.session_state.chat.send_message(
            f"{contexto}\nConversation:\n{history_text}\nUser: {prompt}\n\nAnswer:"
        )
        answer = response.text.strip() if response and getattr(response, "text", None) else ""

        if not answer:
            answer = "⚠️ No pude generar una respuesta en este momento. Intenta de nuevo en unos segundos."

    except Exception:
        answer = "⚠️ Hubo un problema temporal con el servicio. Intenta de nuevo en unos segundos."

    # -------------------------
    # POST-FILTRO SUAVE (CTA)
    # - Si preguntan por cita / agendar, guía a WhatsApp/email
    # -------------------------
    ask_booking = any(w in t for w in ["cita", "agendar", "schedule", "appointment", "book", "reservar"])
    if ask_booking and ("801" not in answer and "contact@jhgbinwash.com" not in answer):
        answer += "\n\n📲 Para agendar, escríbenos por WhatsApp al **(801) 228-7260** o al correo **contact@jhgbinwash.com**."

    # Mostrar respuesta
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
