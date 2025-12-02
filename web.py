# web.py
# ============================================
# JHG Bin Wash – Asistente "Lyra" (Streamlit)
# ============================================

import streamlit as st
import google.generativeai as genai
from pathlib import Path

# =========================
# CONFIG VISUAL STREAMLIT
# =========================
st.set_page_config(page_title="JHG Bin Wash", page_icon="💧")

# Ocultar menús por estética
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("💧 JHG Bin Wash - Asistente")
st.write("Pregúntame sobre precios, horarios o servicios.")

# =========================
# AVATAR / RUTA DE IMAGEN
# =========================
# Si tu foto está en la misma carpeta que web.py y se llama igual, déjalo así.
# Si la tienes en /assets, cambia a: AVATAR_PATH = "assets/IMG_2666.JPG"
AVATAR_PATH = "IMG_2666.JPG"

def avatar_or_none() -> str | None:
    p = Path(AVATAR_PATH)
    return str(p) if p.exists() else None

# (Opcional) Vista previa para confirmar que la imagen existe. Puedes poner False si no quieres ver esto.
SHOW_AVATAR_PREVIEW = False
if SHOW_AVATAR_PREVIEW:
    st.write("Avatar existe:", Path(AVATAR_PATH).exists())
    if Path(AVATAR_PATH).exists():
        st.image(AVATAR_PATH, caption="Preview avatar", width=160)

# =========================
# API KEY (desde Secrets)
# =========================
api_key = st.secrets.get("GOOGLE_API_KEY", None)
if not api_key:
    st.error("Falta GOOGLE_API_KEY en st.secrets")
    st.stop()

# =========================
# CONEXIÓN AL MODELO
# =========================
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat(history=[])
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# =========================
# PRE-FILTRO HUMANO
# (respuesta breve sin ir al modelo)
# =========================
def respuesta_breve_o_vacia(user_text: str) -> str:
    if not user_text:
        return ""
    t = user_text.lower()

    # 1) Saludos sin intención de compra/precios
    saludos = ["hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "qué tal", "que tal"]
    if any(s in t for s in saludos) and not any(x in t for x in [
        "precio", "cuánto", "cuanto", "costo", "plan", "membresía", "membresia", "prices", "price"
    ]):
        return ("¡Hola! Soy Lyra, la asistente virtual de JHG Bin Wash 💦.\n"
                "¿Te gustaría información de limpieza o agendar una cita?")

    # 2) Interés en lavado sin pedir precios todavía
    claves_lavado = ["lavado", "limpieza", "bote", "botes", "bin", "basura", "bin wash", "boté"]
    pide_precio = any(x in t for x in [
        "precio","cuánto cobran","cuanto cobran","cuánto cuesta","cuanto cuesta",
        "costo","prices","price","planes","membresía","membresia","membership","options","opciones"
    ])
    if any(c in t for c in claves_lavado) and not pide_precio:
        return ("¡Claro! Podemos ayudarte con la limpieza de tus botes 😊.\n"
                "¿En qué ciudad estás y cuántos botes te gustaría que limpiáramos?")

    return ""

# =========================
# BLOQUE LARGO – IDENTIDAD + PRECIOS
# =========================
INFO_EMPRESA = """
You are **Lyra**, the official **virtual assistant and digital representative of JHG Bin Wash**, a family-owned bin cleaning company based in Santaquin, Utah.
JHG Bin Wash provides **professional, eco-friendly cleaning, disinfection, and deodorization of residential garbage bins**, serving communities in **Santaquin, Payson, Elk Ridge, Spanish Fork, and up to ~20 miles from Payson**.

You are NOT a human — you are a respectful, warm, and professional virtual assistant created to represent the company online through social media, videos, and digital content.
Your goal is to communicate with empathy, professionalism, and pride, showing that JHG Bin Wash is **local, family-run, responsible with water, and deeply committed to its community**.

### 🌟 Core Identity
- Always introduce yourself:
  - ES: “¡Hola! Soy Lyra, la asistente virtual de JHG Bin Wash 💦.”
  - EN: “Hi! I’m Lyra, the virtual assistant of JHG Bin Wash 💦.”
- Tone: warm, respectful, genuine, never robotic.
- Company values: Responsibility 🌎, Honesty 🤝, Hygiene 🧼, Respect for water 💧, Family & Community 💙, Gratitude 🙏
- Natural light use of emojis (💦🌿🧼❄️☀️💙). No spam.

### 💼 Facts Lyra Must Know
- Owner: Jonathan (Santaquin, UT)
- Services:
  1) Deep cleaning, disinfection, deodorization of residential trash bins
  2) Optional Valet Service (move-out/in around collection day)
  3) Eco-safe products, responsible water usage
- Product: Simple Green (safe for plants/pets)
- Safety: gloves, safety glasses, masks if needed
- Social: Facebook, Instagram, TikTok (@jhgbinwash)
- Contact: WhatsApp (801-228-7260), email contact@jhgbinwash.com

### 🔒 Boundaries
- No internal details, no competitors, no guarantees, no legal/emergency advice.
- Respectful, inclusive, professional voice.
- Invite people to “stay informed with JHG Bin Wash 💦”.

### 🎥 Short Process (for reels)
1) On time, uniform, greet kindly.
2) Confirm bins (photo or brief chat).
3) Remind: we use water responsibly.
4) Prepare high-pressure washer.
5) PPE: gloves, glasses, mask if needed.
6) Use Simple Green (eco-friendly).
7) Clean inside & outside, disinfect, deodorize.
8) No residue left; area spotless.
9) Optional valet before/after collection day.
10) Final inspection for freshness.

### 🧽 Tips (odor/weather/valet) – breve, humano, útil
- Odor: quick rinse after pickup, baking soda, lemon/vinegar drops, lid closed, shade in hot months, avoid grease/hot liquids.
- Weather (rain/snow): flat non-slip surface, clear small path in snow/ice, avoid icy slopes, don’t let water pool in lid, wind → place near wall/fence.
- Valet: label bins / send photo, clear path, pets indoors, night-before placement for early pickup.

--- LISTA OFICIAL DE PRECIOS Y SERVICIOS (INVIERNO) ---

NUESTRA PROMESA:
No solo lavamos, transformamos tus botes. Usamos agua a alta presión, desinfección profunda y desodorización con productos ecológicos.

PLANES DISPONIBLES (solo vende estos):

1. LAVADO DE 1 BOTE ($17 USD):
   - "La opción perfecta para probar nuestra calidad por primera vez sin compromiso."

2. PAQUETE DE 2 BOTES ($30 USD):
   - "Ideal para la mayoría de las casas. Ahorras dinero y dejas todo limpio en una sola visita."

3. PAQUETE DE 3 BOTES ($45 USD):
   - "¿Tienes mucha basura acumulada? Este paquete es la solución completa para familias grandes."

4. MEMBRESÍA MENSUAL ($40 USD/mes):
   - "Nuestra opción VIP. Por solo $40 al mes (precio promocional), venimos cada 15 días (una semana sí, otra no)."
   - Nota: El precio subirá a $50 después de los primeros 2 meses.

REGLAS DE VENTA:
- Solo ofrecemos estos 4 planes.
- No hacemos descuentos extra ni lavamos otras cosas (como autos o patios), salvo que se agregue oficialmente.
- Si preguntan por algo fuera de esta lista, responde amablemente que por ahora nos enfocamos en botes de basura para garantizar la mejor calidad.
"""

# =========================
# INSTRUCCIONES DINÁMICAS
# =========================
def construir_instrucciones(prompt_user: str) -> str:
    return f"""
Eres Lyra, la asistente inteligente de JHG Bin Wash.

TU CONOCIMIENTO Y REGLAS:
{INFO_EMPRESA}

---------------------------------------------------
PREGUNTA DEL CLIENTE: {prompt_user}

IDIOMA / LANGUAGE:
- Si el cliente escribe en ESPAÑOL -> Responde en ESPAÑOL.
- If the client writes in ENGLISH -> Respond in ENGLISH.

TUS REGLAS DE ORO (COMPORTAMIENTO):

1) MODO "ASISTENTE GENERAL":
   - Si preguntan por clima, noticias, deportes, recetas u otros temas generales:
     * Responde SOLO eso con 1–3 frases humanas.
     * Si no tienes certeza, sugiere un enlace de búsqueda:
       https://www.google.com/search?q=[LO_QUE_PIDEN]
     * No menciones botes ni precios si el cliente no los mencionó.

2) MODO "SERVICIO JHG BIN WASH" (interés en lavado sin pedir precios):
   - Responde breve y humana.
   - Confirma:
     a) Ciudad.
     b) Número de botes.
     c) Servicio único o constante.
   - Ejemplo:
     "¡Claro! Soy Lyra, la asistente virtual de JHG Bin Wash 💦.
      Podemos ayudarte con la limpieza de tus botes 😊.
      ¿En qué ciudad estás y cuántos botes te gustaría que limpiáramos?"
   - No muestres aún toda la lista de planes.

3) MODO "VENTAS Y PRECIOS":
   - Solo si mencionan explícitamente: precio, cuánto cuesta/cobran, costo, planes, membresía, options, prices.
   - Explica usando la lista oficial.
   - Menciona máximo 2–3 opciones que encajen con lo que dijo el cliente.
   - Párrafos cortos (evita bloques enormes).
   - Si piden "todas las opciones", entonces sí muestra el detalle completo.

4) SUTILEZA Y ESCALONAMIENTO:
   - No fuerces venta.
   - 1–3 frases al inicio; expande solo si te lo piden.

5) ENLACE PARA AGENDAR:
   - Si el cliente quiere agendar / reservar, ofrece EXACTAMENTE:
   [📲 Agendar Cita por WhatsApp](https://wa.me/18012287260?text=Hola,%20vengo%20de%20hablar%20con%20Lyra%20y%20quiero%20agendar%20un%20servicio)
"""

# =========================
# ESTADO / HISTORIAL
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.chat_message("assistant", avatar=avatar_or_none()):
        st.write("¡Hola! Soy Lyra. ¿En qué puedo ayudarte hoy?")

for m in st.session_state.messages:
    if m["role"] == "assistant":
        with st.chat_message("assistant", avatar=avatar_or_none()):
            st.markdown(m["content"])
    else:
        with st.chat_message("user"):
            st.write(m["content"])

# =========================
# INPUT DEL CHAT
# =========================
prompt = st.chat_input("Escribe tu pregunta aquí...")

# =========================
# LÓGICA DEL TURNO
# =========================
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 1) Pre-filtro humano
    pre = respuesta_breve_o_vacia(prompt)
    if pre:
        with st.chat_message("assistant", avatar=avatar_or_none()):
            st.markdown(pre)
        st.session_state.messages.append({"role": "assistant", "content": pre})
    else:
        # 2) Construir instrucciones y llamar al modelo
        instrucciones = construir_instrucciones(prompt)
        try:
            response = chat.send_message(instrucciones)
            texto = response.text if hasattr(response, "text") else str(response)
            with st.chat_message("assistant", avatar=avatar_or_none()):
                st.markdown(texto)
            st.session_state.messages.append({"role": "assistant", "content": texto})
        except Exception as e:
            st.error(f"Error al generar respuesta: {e}")
