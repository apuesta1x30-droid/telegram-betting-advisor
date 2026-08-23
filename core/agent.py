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
            model="groq/compound",  # Modelo gratuito, rápido y excelente
            temperature=0.3,         # Baja temperatura para respuestas más precisas y menos "creativas"
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al conectar con la IA. Verifica la configuración. Detalle: {str(e)}"
