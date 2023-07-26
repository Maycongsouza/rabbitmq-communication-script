#!/usr/bin/env python3
import logging
import time

import pika
from connection import conn
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

# SQL de Keep Alive disparado em caso de não haver novas notificações
SQL = 'SELECT 1'

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('listen')

# Configuração do RabbitMQ
def connection_rabbit(notify):
    # Troque localhost pelo sua URL ou IP do RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # Cria um canal de conexão com o rabbitmq, a queue declarada é criada automaticamente
    channel = connection.channel()
    channel.queue_declare(queue='your_row')
    channel.basic_publish(exchange='',
                          routing_key='your_row',
                          body=notify)
    connection.close()

# Função para escutar notificações do banco de dados
def listen_notifications(conn, curs):
    logger.info('Iniciando escuta de notificações')

    # Trigger que você criou no seu banco
    curs.execute('LISTEN trigger_name')

    # Trigger que você criou no seu banco
    curs.execute('LISTEN trigger_name_2')

    # Apenas lembrando que você pode criar quantas quiser, basta ir adicionando elas conforme exemplo acima


    logger.info('Conexão estabelecida')
    logger.info(datetime.now())
    ultimo_sql = datetime.now()

    # looping que recebe as notificações e repassa ao rabbitmq
    while True:
        conn.poll()
        time.sleep(5)
        while conn.notifies:
            notify = conn.notifies.pop()
            logger.info(f'Recebida notificação: {notify.payload}')
            connection_rabbit(notify.payload)
            ultimo_sql = datetime.now()
        # Esse controle de tempo, serve para dispararmos um aviso ao banco de dados para que ele não encerre a conexão por inatividade
        data_atual = datetime.now()
        ultima_att_data = ultimo_sql + timedelta(minutes=5)
        if data_atual > ultima_att_data:
            curs.execute(SQL)
            logger.info('Keep Alive')
            ultimo_sql = datetime.now()

# Função para executar as tarefas em paralelo
def run():
    curs = conn.cursor()
    listen_task = ThreadPoolExecutor(max_workers=1).submit(listen_notifications, conn, curs)
    listen_task.result()  # Aguarda a conclusão da tarefa de escuta

# Executa as tarefas em um loop infinito
while True:
    try:
        run()
    except Exception as e:
        logger.info('Conexão perdida')
        logger.info(datetime.now())
        logger.exception(f'Erro ao executar: {e}')
        time.sleep(60)
        run()
