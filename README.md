# Weather REST API

API REST en Flask que consume OpenWeather API para obtener datos meteorológicos.

## Requisitos

- Python 3.8+
- Flask 3.0.0
- requests 2.31.0
- python-dotenv 1.0.0

## Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar API Key:**
   - Registrarse en [OpenWeather API](https://openweathermap.org/api)
   - Obtener tu API key (generalmente disponible en pocos minutos)
   - Editar el archivo `.env` y reemplazar `your_openweather_api_key_here` con tu clave real

   Archivo `.env`:
   ```
   OPENWEATHER_API_KEY=tu_api_key_real_aqui
   FLASK_ENV=development
   FLASK_DEBUG=True
   PORT=5000
   ```

## Ejecutar la aplicación

```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

## Endpoints

### 1. Health Check
**GET** `/health`

Verifica que la API está funcionando correctamente.

**Respuesta exitosa (200):**
```json
{
  "status": "OK",
  "service": "Weather API",
  "version": "1.0.0",
  "timestamp": "2026-05-26T10:30:45.123456"
}
```

### 2. Información de la API
**GET** `/`

Información general de la API y endpoints disponibles.

**Respuesta (200):**
```json
{
  "name": "Weather REST API",
  "version": "1.0.0",
  "description": "API para consultar datos meteorológicos usando OpenWeather",
  "endpoints": {
    "health": "GET /health",
    "weather_by_city": "GET /weather?city=<city_name>",
    "weather_by_coordinates": "GET /weather?lat=<latitude>&lon=<longitude>",
    "multiple_weather": "POST /weather/multiple"
  }
}
```

### 3. Clima por ciudad
**GET** `/weather?city=<nombre_ciudad>`

Obtiene el clima actual de una ciudad específica.

**Parámetros:**
- `city` (string, requerido): Nombre de la ciudad

**Ejemplo:**
```bash
curl "http://localhost:5000/weather?city=London"
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "city": "London",
    "country": "GB",
    "coordinates": {
      "latitude": 51.51,
      "longitude": -0.13
    },
    "weather": {
      "main": "Clouds",
      "description": "overcast clouds",
      "icon": "04d"
    },
    "temperature": {
      "current": 15.2,
      "feels_like": 14.8,
      "min": 13.5,
      "max": 17.1
    },
    "humidity": 65,
    "pressure": 1013,
    "wind_speed": 4.5,
    "clouds": 90,
    "timestamp": "2026-05-26T10:30:45"
  }
}
```

### 4. Clima por coordenadas
**GET** `/weather?lat=<latitud>&lon=<longitud>`

Obtiene el clima usando coordenadas geográficas.

**Parámetros:**
- `lat` (float, requerido): Latitud (-90 a 90)
- `lon` (float, requerido): Longitud (-180 a 180)

**Ejemplo:**
```bash
curl "http://localhost:5000/weather?lat=51.5&lon=-0.1"
```

**Respuesta:** (idéntica al endpoint anterior)

### 5. Clima múltiple
**POST** `/weather/multiple`

Obtiene el clima para múltiples ciudades o ubicaciones en una sola solicitud.

**Body JSON - Por ciudades:**
```json
{
  "cities": ["London", "Paris", "Madrid", "Barcelona"]
}
```

**Body JSON - Por coordenadas:**
```json
{
  "locations": [
    {"lat": 51.5, "lon": -0.1},
    {"lat": 48.8, "lon": 2.3},
    {"lat": 40.4, "lon": -3.7}
  ]
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/weather/multiple \
  -H "Content-Type: application/json" \
  -d '{
    "cities": ["London", "Paris", "Madrid"]
  }'
```

**Respuesta (200):**
```json
{
  "success": true,
  "summary": {
    "total_requested": 3,
    "successful": 3,
    "failed": 0
  },
  "results": {
    "successful": [
      {
        "query": "London",
        "data": { ... }
      },
      {
        "query": "Paris",
        "data": { ... }
      },
      {
        "query": "Madrid",
        "data": { ... }
      }
    ],
    "failed": []
  }
}
```

## Códigos de error

### 400 - Solicitud inválida
- Parámetros faltantes o inválidos
- Coordenadas fuera de rango
- Tipos de datos incorrectos

**Ejemplo:**
```json
{
  "error": "Parámetros inválidos",
  "message": "Debe proporcionar: city=<nombre> o lat=<latitud>&lon=<longitud>"
}
```

### 401 - No autorizado
- API key inválida o expirada

**Respuesta:**
```json
{
  "error": "API key inválida o expirada",
  "status_code": 401
}
```

### 404 - No encontrado
- Ciudad o ubicación no existe
- Ruta no encontrada

**Respuesta:**
```json
{
  "error": "Ciudad no encontrada",
  "status_code": 404
}
```

### 429 - Demasiadas solicitudes
- Más de 50 ciudades/ubicaciones en una sola solicitud

**Respuesta:**
```json
{
  "error": "Demasiadas solicitudes",
  "message": "Máximo 50 ciudades/ubicaciones por solicitud"
}
```

### 503 - Servicio no disponible
- Error de conexión con OpenWeather API

**Respuesta:**
```json
{
  "error": "Error de conexión con OpenWeather API"
}
```

### 504 - Gateway Timeout
- La solicitud tardó demasiado

**Respuesta:**
```json
{
  "error": "Timeout: La solicitud tardó demasiado"
}
```

## Validaciones incluidas

✅ **API Key requerida** - Se valida al iniciar la aplicación  
✅ **Parámetros requeridos** - Debe proporcionar ciudad o coordenadas  
✅ **Formato de coordenadas** - Validación de rango (lat -90 a 90, lon -180 a 180)  
✅ **Tipos de datos** - Validación de strings, floats, listas  
✅ **Límite de solicitudes** - Máximo 50 ubicaciones por solicitud  
✅ **JSON válido** - Validación del body en POST  
✅ **Timeouts** - Límite de 10 segundos por solicitud  

## Manejo de errores

La API maneja automáticamente:

- ❌ **Timeouts** (504) - Cuando OpenWeather tarda más de 10 segundos
- ❌ **Errores de conexión** (503) - Cuando no se puede conectar a OpenWeather
- ❌ **API key inválida** (401) - Cuando la clave es incorrecta o expirada
- ❌ **Ciudad no encontrada** (404) - Cuando la ubicación no existe
- ❌ **Solicitudes inválidas** (400) - Cuando los parámetros son incorrectos
- ❌ **Errores internos** (500) - Errores no esperados del servidor

## Respuestas JSON limpias

Todas las respuestas siguen este formato:

**Exitosa:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Con error:**
```json
{
  "error": "Descripción del error",
  "message": "Detalles adicionales (opcional)",
  "status_code": 400
}
```

## Ejemplos completos con Python

```python
import requests

# Clima de una ciudad
response = requests.get('http://localhost:5000/weather?city=London')
print(response.json())

# Clima por coordenadas
response = requests.get('http://localhost:5000/weather?lat=51.5&lon=-0.1')
print(response.json())

# Múltiples ciudades
data = {'cities': ['London', 'Paris', 'Madrid']}
response = requests.post('http://localhost:5000/weather/multiple', json=data)
print(response.json())

# Health check
response = requests.get('http://localhost:5000/health')
print(response.json())
```

## Estructura del proyecto

```
weather-api/
├── app.py              # Aplicación principal Flask
├── requirements.txt    # Dependencias Python
├── .env               # Variables de entorno (no versionar)
├── Dockerfile         # Para containerización
├── docker-compose.yml  # Configuración Docker Compose
├── test_api.py         # Suite de pruebas de la API
├── examples.sh         # Ejemplos con curl
└── README.md          # Este archivo
```

## Ejecución con Docker Compose

```bash
docker compose up --build
```

El servicio quedará disponible en `http://localhost:5000`.

## Variables de entorno

| Variable | Descripción | Requerida | Valor por defecto |
|----------|-------------|-----------|-------------------|
| `OPENWEATHER_API_KEY` | Clave de OpenWeather API | Sí | - |
| `FLASK_ENV` | Ambiente (development/production) | No | development |
| `FLASK_DEBUG` | Activar modo debug | No | True |
| `PORT` | Puerto de la aplicación | No | 5000 |

## Notas importantes

- ⚠️ **NO incluir el archivo `.env` en el repositorio** - Contiene credenciales sensibles
- ⚠️ **API Key gratuita** tiene límite de 1000 llamadas/día
- ⚠️ **Timeout de 10 segundos** - Aumentar si es necesario en redes lentas
- ⚠️ **Máximo 50 solicitudes** por POST `/weather/multiple` - Para evitar abusos

## Troubleshooting

**Error: "OPENWEATHER_API_KEY no está configurada"**
- Crear archivo `.env` en la raíz del proyecto
- Agregar: `OPENWEATHER_API_KEY=tu_clave_real`

**Error: "404 - Ciudad no encontrada"**
- Verificar que el nombre de la ciudad sea correcto
- Algunos nombres requieren país (ej: "London, GB")

**Error: "401 - API key inválida"**
- Verificar que la API key sea correcta
- Esperar unos minutos después de crear la cuenta en OpenWeather

**Timeout en conexión**
- Verificar conexión a internet
- Aumentar el timeout en `app.py` (línea: `TIMEOUT = 10`)

## Licencia

MIT

## Autor

Desarrollado como API REST para consumir OpenWeather API
