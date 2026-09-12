# Alerta de "0-0 al minuto 70" por Telegram

Este paquete revisa cada 10 minutos los partidos en vivo de Premier League, La Liga, Serie A, Bundesliga y Ligue 1, y te manda un mensaje de Telegram la primera vez que un partido llega al minuto 70 sin goles.

## Por qué funciona así (y no directo desde Claude)

Dos límites técnicos hacen que esto no se pueda correr directamente como una tarea programada de Claude: las tareas programadas de Claude no pueden repetirse más seguido que una vez por hora, y el entorno en la nube de Claude no tiene salida de red hacia Telegram ni hacia APIs de resultados en vivo. Por eso la solución corre sola en GitHub Actions (gratis), que sí permite revisar cada 5-10 minutos y sí tiene acceso a esos servicios.

Elegí Telegram en vez de WhatsApp porque un bot de Telegram es gratis y se crea en 2 minutos; enviar mensajes de WhatsApp automáticos normalmente requiere una cuenta de negocio de WhatsApp (vía Twilio u otro proveedor) con costo y aprobación previa. Si más adelante quieres cambiarlo a WhatsApp puedo ayudarte, pero implica ese paso adicional.

## Lo que necesitas crear (todo gratis)

### 1. Cuenta y API key en API-Football

1. Entra a https://dashboard.api-football.com/register y crea una cuenta gratis.
2. En el dashboard, copia tu **API Key** (plan Free: 100 solicitudes/día — de sobra para revisar cada 10 minutos).

### 2. Bot de Telegram

1. En Telegram, busca **@BotFather** y envíale `/newbot`.
2. Sigue las instrucciones (nombre y username del bot). Al final te da un **token** con este formato: `123456789:ABCdefGhIJKlmnoPQRstuVWXyz`.
3. Busca tu bot por su username y presiona **Start** (o envíale cualquier mensaje) para poder recibir avisos de él.
4. Para obtener tu **chat_id**: abre en el navegador
   `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   (reemplaza `<TU_TOKEN>` por el token real) y busca `"chat":{"id":` — ese número es tu `chat_id`.

### 3. Repositorio en GitHub

1. Si no tienes cuenta, crea una gratis en https://github.com.
2. Crea un repositorio nuevo (puede ser público — así las ejecuciones de Actions son ilimitadas y gratis; si lo haces privado tienes 2000 minutos gratis al mes, que también alcanzan).
3. Sube los archivos incluidos en este paquete manteniendo la misma estructura de carpetas:
   - `alerta_futbol.py`
   - `notified.json`
   - `.github/workflows/check_scores.yml`
4. Ve a **Settings → Secrets and variables → Actions → New repository secret** y crea estos tres secretos:
   - `API_FOOTBALL_KEY` → tu API key de API-Football
   - `TELEGRAM_BOT_TOKEN` → el token de tu bot
   - `TELEGRAM_CHAT_ID` → tu chat_id

### 4. Probarlo

1. Ve a la pestaña **Actions** de tu repositorio.
2. Selecciona el workflow **"Alerta 0-0 minuto 70"** y presiona **Run workflow** para probarlo manualmente.
3. Si no hay errores rojos, ya quedó activo: correrá solo cada 10 minutos entre las 09:00 y 23:00 UTC (aprox. 4am–6pm hora de Dallas) todos los días, cubriendo los horarios habituales de esas 5 ligas.

## Ajustes que puedes pedirme después

- Cambiar el minuto objetivo (por defecto 70) o la ventana de tolerancia.
- Agregar o quitar ligas (Champions League, Liga MX, etc.).
- Cambiar el rango de horas o la frecuencia de revisión.
- Agregar el marcador exacto o el nombre del árbitro/estadio al mensaje.

## Nota sobre mantenimiento

GitHub desactiva automáticamente los workflows programados si el repositorio no tiene actividad por 60 días. Si un día ves que dejó de avisarte, entra a la pestaña Actions y presiona "Run workflow" o "Enable workflow" para reactivarlo.
