from flask import Flask
import redis
import time
import os
from splitio import get_factory
from splitio.exceptions import TimeoutException
from dotenv import load_dotenv


# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Lee la clave de la variable de entorno
splitio_key = os.getenv('SPLITIO_API_KEY')

if not splitio_key:
    raise Exception("SPLITIO_API_KEY no se encontró en las variables de entorno.")

factory = get_factory(splitio_key)

try:
    factory.block_until_ready(5) ## wait up to 5 seconds
    print("✅ Cliente de Split.io está listo")
except TimeoutException:
    print("⚠️ Advertencia: El cliente de Split.io no está listo después de 5 segundos.")
    ## Now the user can choose whether to abort the whole execution, or just keep going
    ## without a ready client, which if configured properly, should become ready at some point.
    pass
split = factory.client()


app = Flask(__name__)

def wait_for_redis():
    """Esperar a que Redis esté disponible"""
    max_retries = 10
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            redis_client.ping()
            print("✅ Redis conectado exitosamente")
            return redis_client
        except redis.ConnectionError:
            print(f"⏳ Esperando por Redis... ({i+1}/{max_retries})")
            time.sleep(retry_delay)
    
    raise Exception("❌ No se pudo conectar a Redis")

@app.route('/')
def contador_visitas():
    try:
        redis_client = wait_for_redis()
        visitas = redis_client.incr('visitas')
        return f'''
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>📊 Contador de Visitas</h1>
                <p style="font-size: 24px;">¡Número de visitas: <strong>{visitas}</strong>! 🎉</p>
                <p>✅ Redis funcionando correctamente</p>
                <a href="/reiniciar">🔄 Reiniciar contador</a> | 
                <a href="/health">❤️ Health check</a>
            </body>
        </html>
        '''
    except Exception as e:
        return f'❌ Error: {str(e)}'

@app.route('/reiniciar')
def reiniciar_contador():
    try:
        redis_client = wait_for_redis()
        redis_client.set('visitas', 0)
        return '✅ ¡Contador reiniciado! <a href="/">Volver</a>'
    except Exception as e:
        return f'❌ Error: {str(e)}'

@app.route('/health')
def health_check():
    try:
        redis_client = wait_for_redis()
        redis_client.ping()
        return '✅ Health check: Todo funciona correctamente (Flask + Redis)'
    except Exception as e:
        return f'❌ Health check failed: {str(e)}'

if __name__ == '__main__':
    print("🚀 Iniciando aplicación Flask + Redis...")
    app.run(host='0.0.0.0', port=5000)