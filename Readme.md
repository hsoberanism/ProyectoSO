\#Para validar la correcta instalación de Docker
docker ps

\#Construcción de los contenedores
docker compose up -d --build

\#Para ingresar a la Base de Datos
docker compose exec mysql mysql -u banco\_user -p banco\_db

\#Ingresar a la base de datos creada

SELECT DATABASE db\_banco;

\#Revisar las tablas creadas
SHOW TABLES;

\#Revisar Registros de la Tabla
SELECT \* FROM banco

\#Consultar el proceso del Productor
docker compose logs -f productor

\#El productor se ejecuta automáticamente si no es detenido, para detenerlo
docker compose stop productor

\#Iniciar contenedor del Productor
docker compose start productor

\#Consultar el proceso de los Consumidores
docker compose logs -f consumidor1 consumidor2

\#Detener los consumidores en caso de que no existan transacciones pendientes
docker compose stop consumidor1 consumidor2

\#Prueba de Condición de Carrera Iniciando los dos contenedores sin el semáforo
docker compose run --rm --no-deps consumidor1 python -u consumidor.py C1 --sin-mutex
docker compose run --rm --no-deps consumidor2 python -u consumidor.py C2 --sin-mutex

