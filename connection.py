import psycopg2.extensions
import psycopg2.pool
import psycopg2.extras
import time
import logging

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('listen')

# Passe os parâmetros da conexão ao banco de dados pretendido
db_config = {
    'dbname': 'your_database',
    'user': 'your_user',
    'password': 'your_pass',
    'host': 'localhost', # Substituir pela URL ou IP
    'port': 'your_port',
    'connect_timeout': 30
}

# Configurações de pool de conexão
pool_config = {
    'minconn': 1,
    'maxconn': 10,
    'connection_factory': psycopg2.extras.RealDictConnection,
    'dsn': f"dbname={db_config['dbname']} user={db_config['user']} password={db_config['password']} host={db_config['host']} port={db_config['port']}"
}

# Criação do pool de conexão
connection_pool = psycopg2.pool.SimpleConnectionPool(**pool_config)

# Função que obtém uma conexão do pool de conexão
def get_connection():
    return connection_pool.getconn()

# Função que retorna a conexão para o pool de conexão
def return_connection(conn):
    try:
        connection_pool.putconn(conn)
    except psycopg2.OperationalError as e:
        logger.warning(f'Erro ao retornar a conexão para o pool: {e}')

logger.warning('Aguardando conexão com o servidor...')
while True:
    try:
        conn = get_connection()
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        break

    except psycopg2.OperationalError as e:
        # Se ocorrer um erro de conexão, imprime uma mensagem e aguarda o intervalo de tempo antes de tentar novamente
        logger.warning(f"Erro de conexão: \n{e}")
        time.sleep(5)

    finally:
        # Retorna a conexão para o pool de conexão
        return_connection(conn)
