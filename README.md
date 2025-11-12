# Tito.ai

Tito.ai es una aplicación modular de asistente de voz que utiliza un servidor FastAPI para orquestar flujos de trabajo de bots y un cliente Next.js para las interacciones del usuario.

## Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Arquitectura](#arquitectura)
  - [Servidor](#servidor)
  - [Cliente](#cliente)
- [Configuración e Instalación](#configuración-e-instalación)
- [Ejecutando la Aplicación](#ejecutando-la-aplicación)
- [Pruebas](#pruebas)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Descripción del Proyecto

El proyecto califica a los leads guiando a los usuarios a través de una serie de pasos conversacionales. Se compone de dos componentes principales:

1.  **Servidor:** Construido con FastAPI, este componente gestiona los flujos de trabajo de los bots y maneja las integraciones (por ejemplo, salas de Daily, transcripción, TTS y servicios de OpenAI).
2.  **Cliente:** Desarrollado con Next.js y TypeScript, este componente sirve como el widget de cara al usuario.

## Arquitectura

### Servidor

#### Estructura de Directorios
```
server/
├── __init__.py            # Inicialización del paquete e información de la versión
├── main.py                # Punto de entrada del servidor FastAPI
├── runner.py              # CLI del corredor de bots y gestión del ciclo de vida
├── Dockerfile             # Configuración del contenedor
├── requirements.txt       # Dependencias de Python
├── bots/                  # Implementaciones de bots
│   ├── __init__.py
│   ├── base_bot.py        # Framework de bot compartido
│   ├── flow.py            # Implementación de bot basada en flujo
│   └── simple.py          # Implementación de bot simple
├── config/                # Gestión de la configuración
│   ├── __init__.py
│   ├── bot.py             # Configuraciones específicas del bot y manejo de variables de entorno
│   └── server.py          # Configuración de red y tiempo de ejecución del servidor
├── prompts/               # Prompts del sistema LLM
│   ├── __init__.py        # Inicialización del paquete; expone los módulos flow, simple, helpers y types
│   ├── flow.py            # Definiciones de prompts basadas en flujo para flujos de trabajo de conversación
│   ├── simple.py          # Definiciones de prompts simples y directas para interacciones únicas
│   ├── helpers.py         # Funciones de ayuda para la generación y manipulación de prompts
│   └── types.py           # Definiciones de tipos para estructuras de prompts
├── services/              # Integraciones de API externas
│   ├── __init__.py
│   └── calcom_api.py      # Cliente de la API de Cal.com
```

#### Componentes Clave

- **`main.py`**
  El punto de entrada del servidor FastAPI que maneja:
  - Creación y gestión de salas
  - Ciclo de vida del proceso del bot
  - Endpoints HTTP para acceso del navegador y RTVI
  - Gestión de credenciales de conexión

- **`runner.py`**
  El CLI del corredor de bots que maneja:
  - Configuración del bot a través de argumentos CLI
  - Sobrescritura de variables de entorno
  - Inicialización del proceso del bot
  - Argumentos CLI soportados:
    ```bash
    -u/--room-url      URL de la sala de Daily (requerido)
    -t/--token         Token de la sala de Daily (requerido)
    -b/--bot-type      Variante del bot [simple|flow]
    -p/--tts-provider  Servicio de TTS [deepgram|cartesia|elevenlabs|rime]
    -m/--openai-model  Nombre del modelo de OpenAI
    -T/--temperature   Temperatura del LLM (0.0-2.0)
    -n/--bot-name      Nombre personalizado del bot
    ```

- **`bots/`**
  Contiene implementaciones de bots con:
  - `base_bot.py`: Framework compartido e inicialización de servicios
  - `flow.py`: Lógica de conversación sofisticada basada en flujos
  - `simple.py`: Implementación básica de un solo prompt

- **`config/`**
  Gestiona la configuración de la aplicación:
  - Validación de variables de entorno
  - Clases de configuración con tipos seguros
  - Manejo de valores por defecto

- **`prompts/`**
  Contiene los prompts modulares del sistema LLM, incluyendo:
  - `flow.py`: Definiciones de prompts basadas en flujo para flujos de conversación
  - `simple.py`: Definiciones de prompts simples para el agente de un solo prompt
  - `helpers.py`: Funciones para ayudar en la generación y mantenimiento de prompts
  - `types.py`: Definiciones para la estructura y tipos de los prompts

- **`services/`**
  Integraciones de API externas:
  - API de Cal.com para la programación de citas
  - Se pueden añadir integraciones adicionales según sea necesario

- **`utils/`**
  Utilidades y funciones de ayuda comunes:
  - Gestión del ciclo de vida del bot
  - Funciones de ayuda compartidas

### Cliente

#### Estructura de Directorios
- **Directorio:** `client/`

#### Descripción General
- Desarrollado con Next.js usando TypeScript con comprobación de tipos estricta.
- Sigue las convenciones de Next.js: rutas en `/app` o `/pages`, componentes compartidos en `/components`, y estilos en `/styles` o mediante CSS Modules.
- Gestionado con pnpm para el manejo de dependencias.

## Configuración e Instalación

### Configuración del Entorno

Crea un archivo `.env` con las variables de entorno requeridas:
```bash
# Claves de API Requeridas
DAILY_API_KEY=tu_clave_de_api_de_daily
DEEPGRAM_API_KEY=tu_clave_de_api_de_deepgram

# Configuración de LLM (Google es el predeterminado)
GOOGLE_API_KEY=tu_clave_de_api_de_google        # Requerido para Google LLM
GOOGLE_MODEL=gemini-2.0-flash             # Modelo de Google por defecto
GOOGLE_TEMPERATURE=1.0                     # Temperatura de Google por defecto

# Configuración Opcional de OpenAI
OPENAI_API_KEY=tu_clave_de_api_de_openai        # Requerido si se usa OpenAI
OPENAI_MODEL=gpt-4o                       # Modelo de OpenAI por defecto
OPENAI_TEMPERATURE=0.2                    # Temperatura de OpenAI por defecto

# Configuración de TTS
TTS_PROVIDER=deepgram                     # Opciones: deepgram, cartesia, elevenlabs, rime
DEEPGRAM_VOICE=aura-athena-en            # Voz de Deepgram por defecto
CARTESIA_API_KEY=tu_clave_de_api_de_cartesia   # Requerido si se usa Cartesia TTS
CARTESIA_VOICE=tu_id_de_voz_de_cartesia    # Por defecto: 79a125e8-cd45-4c13-8a67-188112f4dd22
ELEVENLABS_API_KEY=tu_clave_de_elevenlabs   # Requerido si se usa ElevenLabs TTS
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb # Voz de ElevenLabs por defecto
RIME_API_KEY=tu_clave_de_api_de_rime           # Requerido si se usa Rime TTS
RIME_VOICE_ID=marissa                    # Voz de Rime por defecto

# Configuración del Bot
BOT_TYPE=flow                            # Opciones: flow, simple (por defecto: flow)
BOT_NAME="Tito.ai"                       # Nombre del bot por defecto
LLM_PROVIDER=google                      # Opciones: google, openai (por defecto: google)
ENABLE_STT_MUTE_FILTER=false             # Habilitar filtro de silencio STT (por defecto: false)

# Sobrescrituras Opcionales
DAILY_API_URL=https://api.daily.co/v1    # URL de la API de Daily por defecto
```

Asegúrate de que el archivo `.env` esté excluido del control de versiones:
```bash
grep -qxF ".env" .gitignore || echo ".env" >> .gitignore
```

### Opciones de Configuración Avanzadas

La aplicación admite una configuración extensa a través de variables de entorno y argumentos CLI. Aquí hay un desglose detallado:

#### Configuración de LLM
- **Selección del Proveedor de LLM**
  - El proveedor por defecto es Google (Gemini)
  - Se puede cambiar a OpenAI a través de `LLM_PROVIDER=openai`
  - Cada proveedor tiene su propio modelo y configuraciones de temperatura

- **Configuración de Google LLM**
  - Modelo: `GOOGLE_MODEL` (por defecto: gemini-2.0-flash)
  - Temperatura: `GOOGLE_TEMPERATURE` (por defecto: 1.0)

- **Configuración de OpenAI**
  - Modelo: `OPENAI_MODEL` (por defecto: gpt-4o)
  - Temperatura: `OPENAI_TEMPERATURE` (por defecto: 0.2)

#### Configuración de TTS
La aplicación admite múltiples proveedores de TTS:
- Deepgram (por defecto)
- Cartesia
- ElevenLabs
- Rime

Cada proveedor requiere su propia clave de API y tiene configuraciones de voz configurables.

#### Configuración del Bot
- Tipo de Bot: `flow` (por defecto) o `simple`
- Nombre de bot personalizado
- Interruptor de filtro de silencio STT

### Argumentos CLI

El corredor de bots (`runner.py`) admite los siguientes argumentos de línea de comandos:

```bash
Argumentos requeridos:
  -u, --room-url              URL de la sala de Daily
  -t, --token                 Token de autenticación

Configuración del bot:
  -b, --bot-type             Tipo de bot [simple|flow] (por defecto: flow)
  -n, --bot-name             Sobrescribe BOT_NAME

Configuración de LLM:
  -l, --llm-provider         Proveedor de servicios LLM [google|openai] (por defecto: google)
  
  # Opciones específicas de Google
  -m, --google-model         Sobrescribe GOOGLE_MODEL
  -T, --google-temperature   Sobrescribe GOOGLE_TEMPERATURE (por defecto: 1.0)
  
  # Opciones específicas de OpenAI
  --openai-model            Sobrescribe OPENAI_MODEL (por defecto: gpt-4o)
  --openai-temperature      Sobrescribe OPENAI_TEMPERATURE (por defecto: 0.2)

Configuración de TTS:
  -p, --tts-provider         Servicio de TTS [deepgram|cartesia|elevenlabs|rime] (por defecto: deepgram)
  --deepgram-voice           Sobrescribe DEEPGRAM_VOICE
  --cartesia-voice           Sobrescribe CARTESIA_VOICE
  --elevenlabs-voice-id      Sobrescribe ELEVENLABS_VOICE_ID
  --rime-voice-id            Sobrescribe RIME_VOICE_ID

Opciones adicionales:
  --enable-stt-mute-filter   Habilitar filtro de silencio STT [true|false] (por defecto: false)
```

### Configuración del Servidor

Navega al directorio `server`, configura un entorno virtual e instala las dependencias:
```bash
cd server
python -m venv venv
# Activa el entorno virtual:
# En Linux/macOS:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate
pip install -r requirements.txt
pip install -e "../external/pipecat[daily,google,anthropic,openai,deepgram,cartesia,silero]"
pip install -e "../external/pipecat-flows"
```

### Configuración del Cliente

Navega al directorio `client` e instala las dependencias usando pnpm:
```bash
cd ../client
pnpm install
```

## Ejecutando la Aplicación

### Servidor

#### Desarrollo Local
Ejecuta el servidor desde el directorio `server`:
```bash
python -m main --bot-type flow  # Usa "simple" en lugar de "flow" para la variante de bot simple
```

#### Contenedor Docker
Construye y ejecuta el servidor en un contenedor Docker:
```bash
docker build -t pipecat-server:latest -f server/Dockerfile .
docker run -p 7860:7860 pipecat-server:latest
```

### Cliente

#### Modo de Desarrollo
Ejecuta el cliente Next.js en modo de desarrollo:
```bash
pnpm dev
```

#### Build de Producción
Para construir e iniciar la versión de producción del cliente:
```bash
pnpm build
pnpm start
```

## Pruebas

- **Servidor:**
  Sigue las directrices de prueba proporcionadas en el código base. Las pruebas deben usar el patrón Arrange-Act-Assert para verificar los endpoints de la API y las funcionalidades del bot.

- **Cliente:**
  Ejecuta las pruebas de frontend usando tu corredor de pruebas preferido (por ejemplo, Jest).

## Licencia

[Licencia MIT](LICENSE.md)

## Contacto

Para cualquier pregunta o problema, por favor contacta a [support@tito.ai](mailto:support@tito.ai).
