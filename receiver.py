import pika
import requests
import logging
import time


# CONFIGURAÇÃO DE LOG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('receiver')

# ENDPOINT DO ODOO QUE RECEBERÁ A NOTIFICAÇÃO
ENDPOINT = 'notify'

# URL OU IP DO ODOO QUE RECEBERÁ A NOTIFICAÇÃO
odoo_url = "http://localhost:8069/"

# API DO ODOO QUE RECEBERÁ O JSON
headers = {"Content-type": "application/json"}

# ESTABELECENDO A CONEXÃO COM O RABBITMQ, SUBSTITUA LOCALHOST PELA URL OU IP DO RABBITMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
# BUSCAR A QUEUE QUE CONTÉM AS MENSAGENS RECEBIDAS DO POSTGRES
channel.queue_declare(queue='your_row')

# FUNÇÃO DE CALLBACK QUE REPASSARÁ AS INFORMAÇÕES AO ODOO E
# EVITARÁ QUE FALHAS DE CONEXÃO ACONTEÇAM
def callback(ch, method, properties, body):
    callback_end = True
    while callback_end:
        try:
            # ENVIAMOS O JSON AO ODOO.
            response = requests.post(url=odoo_url + ENDPOINT, headers=headers, data=body.decode())
            logger.info(response)
            # AVALIAMOS O RETORNO RECEBIDO. SE O CÓDIGO FOR 200, SINAL QUE A MENSAGEM FOI RECEBIDA COM SUCESSO PELO ODOO.
            if response.status_code == 200:
                # COM A CONFIRMAÇÃO RECEBIDA, DELETAMOS A MENSAGEM DO RABBITMQ
                # PARA EVITAR DUPLICIDADE DE INFORMAÇÕES.
                channel.basic_ack(multiple=True)
                callback_end = False
            else:
                # SE O CÓDIGO FOR DIFERENTE DE 200, ACONTECEU ALGUMA FALHA,
                # PORTANTO NÃO DELETAMOS A MENSAGEM DO RABBITMQ POR QUESTÕES DE SEGURANÇA.
                logger.info('TRY AGAIN')
                time.sleep(5)

        except:
            # SE A CONEXÃO COM O SERVIDOR FOR PERDIDA, A MENSAGEM ABAIXO É EXEBIDA.
            logger.info('SERVER NOT FOUND')
            time.sleep(5)
        logger.info(body.decode())

def run():
    # FUNÇÃO QUE IRÁ CONSUMIR AS MENSAGENS DO RABBITMQ.
    channel.basic_consume('hml',
                          callback)
    channel.start_consuming()

while True:
    try:
        run()
    except Exception as e:
        logger.exception(f'Erro ao executar tarefas: {e}')
