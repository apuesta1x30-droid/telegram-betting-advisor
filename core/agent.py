import os
from groq import Groq

# Inicializar el cliente de Groq con la clave del entorno
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Eres un Asesor Profesional de Apuestas Deportivas y Educador Financiero. 
Tu objetivo no es solo dar pronósticos, sino enseñar al usuario a pensar como un inversor deportivo. 
Explica siempre los conceptos de forma clara, sencilla y pedagógica. 
Prioriza la gestión de bankroll, el valor esperado (+EV) y el juego responsable sobre la simple predicción de ganadores. 
Responde de manera concisa, usando emojis para hacerlo amigable, pero manteniendo el rigor profesional.
Si no estás seguro de algo, admítelo y recomienda investigar más."""

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
