# RocketFinderBot

RocketFinderBot es un bot de Telegram que ayuda a encontrar el momento exacto en el que un cohete despega en un video. Funciona mostrando imágenes del video y pidiéndote que indiques si el cohete ya ha despegado o no. El bot utiliza un algoritmo de búsqueda por bisección para encontrar el frame exacto del despegue de forma eficiente.

---

## Requisitos

- Python 3.10 o superior
- Un bot de Telegram y su token
- Conexión a internet
- Acceso a la API de FrameX

---

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/rocketfinderbot.git
cd rocketfinderbot
```
2. Crea un entorno virtual e instala las dependencias del archivo **requirements.txt** :

```bash
python -m venv venv
source venv/bin/activate

# Si el comando de arriba no funciona, prueba este:
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```
3. Crea un archivo .env en la raíz del proyecto con las siguientes variables:
```env
TELEGRAM_TOKEN=tu_token_de_telegram
API_BASE=https://framex.with-madrid.dev/api/
VIDEO_NAME=Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c
```

# Uso
1. Activa tu entorno virtual:
```bash
source venv/bin/activate
venv\Scripts\activate
```
2. Tener una cuenta en Telegram, buscar al contacto BotFather y crear un bot:


3. Copiar el token que te ha dado y sustituir en el .env.


4. Ejecuta el bot:
```bash
python main.py
```

5. Ir a telegram, busca tu bot en chats y escribe /start para iniciar la conversación con el bot:


6. Para empezar una búsqueda de despegue, escribe /newtest.


7. Responder a las preguntas.


8. Para cancelar la búsqueda en cualquier momento, escribe /cancel.
