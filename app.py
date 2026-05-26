import os
import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
TIMEOUT = 10

# Validación de API key al iniciar
if not OPENWEATHER_API_KEY:
    raise ValueError('OPENWEATHER_API_KEY no está configurada en .env')


def make_weather_request(params):
    """
    Realiza una solicitud a OpenWeather API con manejo de errores.
    
    Args:
        params (dict): Parámetros para la solicitud
        
    Returns:
        tuple: (data, status_code, error_message)
    """
    try:
        response = requests.get(
            OPENWEATHER_BASE_URL,
            params={**params, 'appid': OPENWEATHER_API_KEY, 'units': 'metric'},
            timeout=TIMEOUT
        )
        
        # 401 - API key inválida
        if response.status_code == 401:
            return None, 401, 'API key inválida o expirada'
        
        # 404 - Ciudad no encontrada
        if response.status_code == 404:
            return None, 404, 'Ciudad no encontrada'
        
        # Otros errores HTTP
        if response.status_code >= 400:
            return None, response.status_code, f'Error en OpenWeather API: {response.status_code}'
        
        return response.json(), 200, None
        
    except requests.exceptions.Timeout:
        return None, 504, 'Timeout: La solicitud tardó demasiado'
    except requests.exceptions.ConnectionError:
        return None, 503, 'Error de conexión con OpenWeather API'
    except requests.exceptions.RequestException as e:
        return None, 500, f'Error en la solicitud: {str(e)}'


def format_weather_response(data):
    """
    Formatea la respuesta de OpenWeather API de forma limpia.
    
    Args:
        data (dict): Datos de la API de OpenWeather
        
    Returns:
        dict: Respuesta formateada
    """
    return {
        'city': data.get('name'),
        'country': data.get('sys', {}).get('country'),
        'coordinates': {
            'latitude': data.get('coord', {}).get('lat'),
            'longitude': data.get('coord', {}).get('lon')
        },
        'weather': {
            'main': data.get('weather', [{}])[0].get('main'),
            'description': data.get('weather', [{}])[0].get('description'),
            'icon': data.get('weather', [{}])[0].get('icon')
        },
        'temperature': {
            'current': data.get('main', {}).get('temp'),
            'feels_like': data.get('main', {}).get('feels_like'),
            'min': data.get('main', {}).get('temp_min'),
            'max': data.get('main', {}).get('temp_max')
        },
        'humidity': data.get('main', {}).get('humidity'),
        'pressure': data.get('main', {}).get('pressure'),
        'wind_speed': data.get('wind', {}).get('speed'),
        'clouds': data.get('clouds', {}).get('all'),
        'timestamp': datetime.fromtimestamp(data.get('dt', 0)).isoformat()
    }


@app.route('/health', methods=['GET'])
def health_check():
    """
    Verifica que la API está funcionando correctamente.
    """
    return jsonify({
        'status': 'ok',
        'service': 'Weather API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """
    Ruta raíz con información de la API.
    """
    return jsonify({
        'name': 'Weather REST API',
        'version': '1.0.0',
        'description': 'API para consultar datos meteorológicos usando OpenWeather',
        'endpoints': {
            'health': 'GET /health',
            'weather_by_city': 'GET /weather?city=<city_name>',
            'weather_by_coordinates': 'GET /weather?lat=<latitude>&lon=<longitude>',
            'multiple_weather': 'POST /weather/multiple'
        }
    }), 200


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Obtiene el clima actual por ciudad o coordenadas.
    
    Parámetros:
        - city (str): Nombre de la ciudad (ej: ?city=London)
        - lat (float): Latitud (ej: ?lat=51.5&lon=-0.1)
        - lon (float): Longitud
        
    Returns:
        JSON con datos del clima o error
    """
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    # Validación: debe proporcionar ciudad o coordenadas
    if not city and not (lat and lon):
        return jsonify({
            'error': 'Parámetros inválidos',
            'message': 'Debe proporcionar: city=<nombre> o lat=<latitud>&lon=<longitud>'
        }), 400
    
    # Validación: coordenadas válidas
    if lat or lon:
        if not lat or not lon:
            return jsonify({
                'error': 'Parámetros inválidos',
                'message': 'Ambas coordenadas (lat, lon) son requeridas'
            }), 400
        
        try:
            lat = float(lat)
            lon = float(lon)
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return jsonify({
                    'error': 'Coordenadas fuera de rango',
                    'message': 'Latitud debe estar entre -90 y 90, longitud entre -180 y 180'
                }), 400
            params = {'lat': lat, 'lon': lon}
        except ValueError:
            return jsonify({
                'error': 'Tipo de dato inválido',
                'message': 'Latitud y longitud deben ser números'
            }), 400
    else:
        # Validación: ciudad no vacía
        city = city.strip()
        if not city:
            return jsonify({
                'error': 'Ciudad vacía',
                'message': 'El parámetro city no puede estar vacío'
            }), 400
        params = {'q': city}
    
    # Realizar solicitud a OpenWeather
    data, status_code, error_msg = make_weather_request(params)
    
    if error_msg:
        return jsonify({
            'error': error_msg,
            'status_code': status_code
        }), status_code
    
    # Formatear y retornar respuesta
    formatted_data = format_weather_response(data)
    return jsonify({
        'success': True,
        'data': formatted_data
    }), 200


@app.route('/weather/multiple', methods=['POST'])
def get_multiple_weather():
    """
    Obtiene el clima para múltiples ciudades.
    
    Body JSON esperado:
    {
        "cities": ["London", "Paris", "Madrid"]
    }
    o
    {
        "locations": [
            {"lat": 51.5, "lon": -0.1},
            {"lat": 48.8, "lon": 2.3}
        ]
    }
    
    Returns:
        JSON con datos de múltiples ciudades o error
    """
    try:
        payload = request.get_json()
    except Exception:
        return jsonify({
            'error': 'JSON inválido',
            'message': 'El body debe ser un JSON válido'
        }), 400
    
    if not payload:
        return jsonify({
            'error': 'Body vacío',
            'message': 'El body no puede estar vacío'
        }), 400
    
    cities = payload.get('cities', [])
    locations = payload.get('locations', [])
    
    # Validación: debe proporcionar ciudades o coordenadas
    if not cities and not locations:
        return jsonify({
            'error': 'Parámetros inválidos',
            'message': 'Debe proporcionar: cities=[] o locations=[]'
        }), 400
    
    # Validación: listas no vacías
    if cities and not isinstance(cities, list):
        return jsonify({
            'error': 'Tipo inválido',
            'message': 'cities debe ser una lista'
        }), 400
    
    if locations and not isinstance(locations, list):
        return jsonify({
            'error': 'Tipo inválido',
            'message': 'locations debe ser una lista'
        }), 400
    
    # Validación: número máximo de solicitudes (para evitar abusos)
    total_requests = len(cities) + len(locations)
    if total_requests > 50:
        return jsonify({
            'error': 'Demasiadas solicitudes',
            'message': 'Máximo 50 ciudades/ubicaciones por solicitud'
        }), 429
    
    results = {
        'successful': [],
        'failed': []
    }
    
    # Procesar ciudades
    for city in cities:
        if not isinstance(city, str) or not city.strip():
            results['failed'].append({
                'query': city,
                'error': 'Ciudad inválida o vacía'
            })
            continue
        
        data, status_code, error_msg = make_weather_request({'q': city.strip()})
        
        if error_msg:
            results['failed'].append({
                'query': city,
                'error': error_msg,
                'status_code': status_code
            })
        else:
            results['successful'].append({
                'query': city,
                'data': format_weather_response(data)
            })
    
    # Procesar coordenadas
    for loc in locations:
        if not isinstance(loc, dict) or not ('lat' in loc and 'lon' in loc):
            results['failed'].append({
                'query': loc,
                'error': 'Ubicación debe tener lat y lon'
            })
            continue
        
        try:
            lat = float(loc['lat'])
            lon = float(loc['lon'])
            
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                results['failed'].append({
                    'query': f"{lat},{lon}",
                    'error': 'Coordenadas fuera de rango'
                })
                continue
            
            data, status_code, error_msg = make_weather_request({'lat': lat, 'lon': lon})
            
            if error_msg:
                results['failed'].append({
                    'query': f"{lat},{lon}",
                    'error': error_msg,
                    'status_code': status_code
                })
            else:
                results['successful'].append({
                    'query': f"{lat},{lon}",
                    'data': format_weather_response(data)
                })
        except (ValueError, TypeError):
            results['failed'].append({
                'query': loc,
                'error': 'Latitud y longitud deben ser números'
            })
    
    return jsonify({
        'success': len(results['successful']) > 0,
        'summary': {
            'total_requested': total_requests,
            'successful': len(results['successful']),
            'failed': len(results['failed'])
        },
        'results': results
    }), 200 if results['successful'] else 400


# Manejo de errores global
@app.errorhandler(404)
def not_found(error):
    """Maneja rutas no encontradas."""
    return jsonify({
        'error': 'Ruta no encontrada',
        'path': request.path,
        'method': request.method
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Maneja errores internos del servidor."""
    return jsonify({
        'error': 'Error interno del servidor',
        'message': str(error)
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
