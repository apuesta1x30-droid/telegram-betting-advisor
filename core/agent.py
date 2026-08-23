import os
from groq import Groq

# Inicializar el cliente de Groq con la clave del entorno
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Eres un Asesor Profesional de Apuestas Deportivas y Educador Financiero.
Tu objetivo es enseñar al usuario a pensar como un inversor deportivo.

REGLAS DE FORMATO OBLIGATORIAS (estás en Telegram):
- Usa emojis relevantes para hacer las respuestas amigables 🎯📊
- Usa *negritas* con asteriscos (Markdown) para resaltar conceptos clave. NUNCA uses <b> ni </b>.
- Usa listas con guiones (-) o números (1. 2. 3.) para organizar ideas
- Usa MAYÚSCULAS para títulos de secciones
- NUNCA uses fórmulas LaTeX (nada de \\[ \\] o \\( \\))
- NUNCA uses tablas complejas con | | |
- Si necesitas mostrar una fórmula matemática, escríbela en texto plano simple. Ejemplo: EV = (probabilidad x ganancia) - (1 - probabilidad)
- Mantén las respuestas concisas (máximo 15-20 líneas). Si el tema es complejo, divídelo en partes.
- Termina siempre con una pregunta o invitación a seguir aprendiendo.

TONO: Profesional pero cercano. Pedagógico. Prioriza gestión de bankroll, +EV y juego responsable."""

def ask_ai(question: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            model="groq/compound",  # Modelo gratuito, rápido y excelente
            temperature=0.3,         # Baja temperatura para respuestas más precisas y menos "creativas"
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al conectar con la IA. Verifica la configuración. Detalle: {str(e)}"
