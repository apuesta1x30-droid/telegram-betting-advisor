import os
from groq import Groq

# Inicializar el cliente de Groq con la clave del entorno
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Eres un Profesor Experto en Apuestas Deportivas. Tu misión es EDUCAR, no dar pronósticos.

REGLAS DE ORO:
- Explica conceptos complejos de forma sencilla, con analogías de la vida real.
- Usa formato Markdown en Telegram: *negritas*, _cursivas_, listas con guiones.
- Usa emojis relevantes para hacer las respuestas visuales 📊🧠
- NUNCA uses fórmulas LaTeX (nada de \\[ \\] o \\( \\)). Escribe fórmulas en texto plano.
- NUNCA uses tablas complejas con | | |. Usa listas simples.
- Mantén las respuestas concisas (máximo 15-20 líneas).
- Termina siempre con una pregunta para verificar que el alumno entendió.

TONO: Pedagógico, paciente, profesional. Como un mentor que quiere que tu alumno sea independiente y rentable a largo plazo.

ENFOQUE: Matemáticas, estadística, gestión de bankroll, psicología, varianza, valor esperado (+EV), lectura de tendencias."""

def ask_ai(question: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            model="groq/compound",
            temperature=0.3,
            max_tokens=600  # Reducido para evitar rate limits
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        
        # Manejo específico de rate limits
        if "429" in error_msg or "rate limit" in error_msg.lower():
            return (
                " *Límite de peticiones alcanzado*\n\n"
                "Has hecho muchas preguntas en poco tiempo. Groq limita las peticiones en el plan gratuito.\n\n"
                "*Consejos:*\n"
                "- Espera 30-60 segundos antes de preguntar de nuevo\n"
                "- Las preguntas cortas consumen menos tokens\n"
                "- Si necesitas ayuda urgente, espera un minuto e inténtalo de nuevo\n\n"
                "_Esto es normal en el plan gratuito. La IA estará disponible en breve._"
            )
        
        return f"⚠️ Error al conectar con la IA. Verifica la configuración. Detalle: {error_msg}"

def analyze_match(match_data, ev_data):
    """Analiza un partido usando la IA con datos reales."""
    home = match_data.get("home_team")
    away = match_data.get("away_team")
    commence_time = match_data.get("commence_time", "Desconocido")
    
    prompt = f"""
    Actúa como un analista deportivo profesional.
    Partido: {home} vs {away}
    Fecha: {commence_time}
    
    Datos de mercado (Pinnacle):
    - Cuota Local: {ev_data.get('home_odd')} (Probabilidad implícita: {ev_data.get('home_imp')}%)
    - Cuota Empate: {ev_data.get('draw_odd')} (Probabilidad implícita: {ev_data.get('draw_imp')}%)
    - Cuota Visitante: {ev_data.get('away_odd')} (Probabilidad implícita: {ev_data.get('away_imp')}%)
    
    Mi cálculo de Valor Esperado para el favorito indica: {ev_data.get('verdict')} con un {ev_data.get('ev')}% de EV.
    
    Tarea:
    1. Explica brevemente qué significan estas cuotas en el mercado actual.
    2. Da un consejo de gestión de bankroll para este tipo de partido.
    3. Recuérdame que el +EV es matemático, pero el fútbol tiene varianza.
    Usa formato Markdown (*negritas*, listas, emojis). Sé conciso.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="groq/compound",
            temperature=0.3,
            max_tokens=400
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en el análisis IA: {str(e)}"
