# RabbitMQ Communication Project

O objetivo deste projeto, é realizar a comunicação de um banco de dados qualquer com o framework Odoo, de forma organizada, através de uma fila.

Dê preferência em executar o script listen.py na mesma máquina do banco de dados, para evitar alguma possível perca de comunicação, já que o sistema de notificação do banco de dados - neste exemplo, um PostgreSQL - apenas dispara, sem um sistema de ack, ou seja, confirmação do recebimento da notificação. Já o receiver.py pode ser executado tanto na máquina do RabbitMQ quanto na do Odoo, já no Odoo sim, temos um sistema de resposta. Lembrando que o connection.py é importado no listen.py, então precisam ficar juntos.

Para esse ambiente funcionar, é necessário instalar as seguintes bibliotecas: pika e psycopg2

```pip install lib_name```

## RabbitMQ

Em um sistema Linux, você pode executar o RabbitMQ através de um único comando. Não esqueça de definir a porta de sua preferência em que o serviço irá rodar:

```docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management```

Ele poderá ser acesso atraés de localhost:numero_da_sua_porta

Usuário e senha padrão: guest / guest

## Listen

Depois de colocar o RabbitMQ para rodar, é hora de executar o listen.py. Depois de definir a máquina que ele irá ser executado, basta colocar o script para rodar.
Também lembre que, precisa definir as variáveis do seu banco de dados para que o listen possa acessar como database, usuário, senha e host.
Para que ele funcione corretamente, é necessário criar triggers no banco de dados com a função listen - disponivel no PostgreSQL - sendo possível formatar os dados em um JSON para serem enviados ao RabbitMQ.

Dica: Execute de forma que ele salve o log em um arquivo separado, caso você precise saber o motivo de eventuais erros.

## Receiver

O receiver.py tem a responsabilidade de ler as mensagens na fila e entregar ao Odoo. Como isso é feito através de uma API (request), podemos garantir que a mensagem foi entregue antes de deletar da fila. Se a resposta for 200, significa que a mensagem foi recebida e processada, qualquer coisa diferente disso, a mensagem é mantida no RabbitMQ.

O script tem um sistema que, caso ele não encontre a conexão com o Odoo, ele fica em looping tentando reestabelecer a cada 5 segundos.
