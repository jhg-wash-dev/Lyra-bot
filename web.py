import streamlit as st
import google.generativeai as genai

# 1. Configuración visual
st.set_page_config(page_title="JHG Bin Wash", page_icon="💧")

# Esconder el menú, el pie de página y el gatito de GitHub
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("💧 JHG Bin Wash - Asistente")
st.write("Pregúntame sobre precios, horarios o servicios.")

# 2. TU LLAVE (Desde la caja fuerte)
api_key = st.secrets["GOOGLE_API_KEY"]

# 3. Conexión ESTABLE (Sin antena, pero rápida y segura)
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash') 
    chat = model.start_chat(history=[])
except Exception as e:
    st.error(f"Error de configuración: {e}")

# 4. Memoria visual
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje de bienvenida con AVATAR
    with st.chat_message("assistant", avatar="IMG_2666.JPG"):
        st.write("¡Hola! Soy Lyra. ¿En qué puedo ayudarte hoy?")

# 5. Mostrar historial con AVATAR
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="IMG_2666.JPG"):
            st.write(message["content"])
    else:
        with st.chat_message("user"):
            st.write(message["content"])

# 6. El Chat
prompt = st.chat_input("Escribe tu pregunta aquí...")

if prompt:
    # Mostrar tu mensaje
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # EL ALMA DE LYRA (Instrucciones)
    # 1. Aquí va TODO lo que copiaste de AI Studio (Las 7 partes juntas)
    # IMPORTANTE: PEGA AQUÍ ADENTRO TU TEXTO LARGO DE LA EMPRESA
    info_empresa = """
    --- LISTA OFICIAL DE PRECIOS Y SERVICIOS (INVIERNO) ---

    NUESTRA PROMESA:
    No solo lavamos, transformamos tus botes. Usamos agua a alta presión, desinfección profunda y desodorización con productos ecológicos.

    PLANES DISPONIBLES (Solo vende estos):

    1. LAVADO DE 1 BOTE ($17 USD):
       La opción perfecta para probar nuestra calidad por primera vez sin compromiso.

    2. PAQUETE DE 2 BOTES ($30 USD):
       Ideal para la mayoría de las casas. Ahorras dinero y dejas todo limpio en una sola visita.

    3. PAQUETE DE 3 BOTES ($45 USD):
       ¿Tienes mucha basura acumulada? Este paquete es la solución completa para familias grandes.

    4. MEMBRESÍA MENSUAL ($40 USD/mes):
       ¡Nuestra opción VIP! Por solo $40 al mes (precio promocional), venimos cada 15 días. Olvídate de los malos olores para siempre.
    """

    # 2. CEREBRO SUTIL Y CONVERSACIONAL (Instrucciones Finales)
    instrucciones = f"""
    Eres Lyra, la asistente inteligente de JHG Bin Wash.
    
    TU CONOCIMIENTO INTERNO:
    {info_empresa}

    ---------------------------------------------------
    PREGUNTA DEL CLIENTE: {prompt}
    
    IDIOMA / LANGUAGE:
    - Detecta el idioma y responde en el mismo (Español/Inglés).
    
    TUS REGLAS DE ORO (COMPORTAMIENTO HUMANO):
    
    1. MODO ASISTENTE GENERAL: Si preguntan clima, noticias o deportes, responde brevemente solo eso (si tienes el dato).
    
    2. MODO VENTAS (SUTIL): 
       - ¡NO VOMITES INFORMACIÓN! Si el cliente dice "quiero lavar mi bote", NO le des la lista de precios completa de golpe.
       - ACTÚA CON CALMA: Primero pregunta: "¡Claro que sí! ¿Cuántos botes te gustaría que laváramos?" o "¿En qué ciudad te encuentras?".
       - SÉ ESPECÍFICA: 
         * Si responden "1 bote", dales SOLO el precio de 1 ($17) y ofrece agendar.
         * Si responden "2 botes", dales SOLO el precio de 2 ($30).
       - SOLO da la lista completa si preguntan explícitamente "¿Cuáles son tus precios?".

    3. SUTILEZA: Sé breve. Respuestas cortas (máximo 2-3 frases). Conversa, no des discursos.
    
    Si el cliente YA decidió y quiere agendar:
    👉 [📲 Agendar Cita por WhatsApp](https://wa.me/18012287260?text=Hola,%20vengo%20de%20hablar%20con%20Lyra%20y%20quiero%20agendar%20un%20servicio)
    """

    try:
        response = chat.send_message(instrucciones)
        
        # Respuesta de Lyra con AVATAR
        with st.chat_message("assistant", avatar="IMG_2666.JPG"):
            st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"Error: {e}")
