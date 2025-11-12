# Tito.AI Backend

Sistema de asistente de voz con IA para calificación de clientes potenciales y consultoría técnica.

## Características

- Asistente de voz conversacional en español
- Calificación automática de clientes potenciales
- Integración con Daily.co para videollamadas
- Soporte para múltiples proveedores de LLM (OpenAI, Google)
- Múltiples opciones de TTS (Deepgram, Cartesia, ElevenLabs, Rime)

## Configuración

1. Copiar `.env.example` a `.env`
2. Configurar las claves de API necesarias
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar: `python main.py`

## Uso

- Acceso directo: `GET /`
- Conexión API: `POST /connect`
- Estado del bot: `GET /status/{pid}`

## Tipos de Bot

- `simple`: Bot básico de calificación
- `flow`: Bot avanzado con flujo conversacional

## Variables de Entorno

Ver `.env.example` para la configuración completa.
