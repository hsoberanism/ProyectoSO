import mysql.connector
import os
import redis
import time
import sys
import uuid
import random
import argparse
from datetime import datetime


# CONFIGURACION

parser = argparse.ArgumentParser()

parser.add_argument("nombre", help="Identificador del consumidor")

parser.add_argument(
    "--sin-mutex",
    action="store_true",
    help="Ejecutar sin semaforo para demostrar la condicion de carrera"
)

args = parser.parse_args()

NOMBRE = args.nombre
SIN_MUTEX = args.sin_mutex

CLAVE_MUTEX = "semaforo:transacciones"
TIEMPO_EXPIRACION = 10


# Conexión con Redis

r = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

#Conexión con Base de Datos
def conectar_mysql():
    return mysql.connector.connect(
        host="mysql",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


#Liberación del MUTEX

LIBERAR_MUTEX = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""


def liberar_mutex(token):

    resultado = r.eval(
        LIBERAR_MUTEX,
        1,
        CLAVE_MUTEX,
        token
    )

    if resultado == 1:
        print(
            f"[{NOMBRE}] Mutex liberado correctamente",
            flush=True
        )
    else:
        print(
            f"[{NOMBRE}] No se libero: ya no soy el propietario",
            flush=True
        )


#Selección de Modo

modo = "SIN MUTEX" if SIN_MUTEX else "CON MUTEX"

print(
    f"[{NOMBRE}] Iniciado - Modo: {modo}",
    flush=True
)


while True:

    token = str(uuid.uuid4())
    adquirido = False
    conexion = None
    cursor = None

    try:

        #Adquirir Mutex

        if not SIN_MUTEX:

            adquirido = r.set(
                CLAVE_MUTEX,
                token,
                nx=True,
                ex=TIEMPO_EXPIRACION
            )

            if not adquirido:

                print(
                    f"[{NOMBRE}] Esperando mutex...",
                    flush=True
                )

                time.sleep(0.5)
                continue

            print(
                f"[{NOMBRE}] Mutex adquirido",
                flush=True
            )

        else:

            print(
                f"[{NOMBRE}] Ejecutando SIN mutex",
                flush=True
            )


        #Consultar si existen transacciones pendientes

        conexion = conectar_mysql()
        cursor = conexion.cursor()

        if SIN_MUTEX:

            sql = """
                SELECT id, cuenta, tipo, monto, moneda
                FROM banco
                WHERE estado = 'PENDIENTE'
                ORDER BY creado_en ASC, id ASC
                LIMIT 1
            """

        else:

            sql = """
                SELECT id, cuenta, tipo, monto, moneda
                FROM banco
                WHERE estado = 'PENDIENTE'
                ORDER BY creado_en ASC, id ASC
                LIMIT 1
                FOR UPDATE
            """

        cursor.execute(sql)

        transaccion = cursor.fetchone()


        #Verificar si hay transacciones

        if transaccion is None:

            conexion.rollback()

            print(
                f"[{NOMBRE}] No hay transacciones pendientes",
                flush=True
            )

        else:

            id_transaccion = transaccion[0]

            cuenta = transaccion[1]

            tipo = transaccion[2]

            monto = transaccion[3]

            moneda = transaccion[4]

            print(
                f"[{NOMBRE}] Procesando transaccion "
                f"#{id_transaccion} | Cuenta: {cuenta} "
                f"| {tipo} | {monto} {moneda}",
                flush=True
            )


            # Precesamiento

            tiempo = random.uniform(1, 3)

            time.sleep(tiempo)


            # Actualizar transacción

            if not SIN_MUTEX:

                # Verificar que Redis sigue reconociendo
                # a este consumidor como propietario.

                propietario = r.get(CLAVE_MUTEX)

                if propietario != token:

                    conexion.rollback()

                    print(
                        f"[{NOMBRE}] Mutex perdido. "
                        f"No se actualizara la transaccion",
                        flush=True
                    )

                    continue

                sql_update = """
                    UPDATE banco
                    SET estado = 'PROCESADO',
                        procesado_en = NOW(),
                        procesado_por = %s
                    WHERE id = %s
                    AND estado = 'PENDIENTE'
                """

            else:

                # Modo de demostracion de condicion de carrera.
                # Los dos consumidores pueden actualizar la misma fila.

                sql_update = """
                    UPDATE banco
                    SET estado = 'PROCESADO',
                        procesado_en = NOW(),
                        procesado_por = %s
                    WHERE id = %s
                """

            cursor.execute(
                sql_update,
                (NOMBRE, id_transaccion)
            )

            conexion.commit()

            print(
                f"[{NOMBRE}] Transaccion #{id_transaccion} "
                f"actualizada a PROCESADO "
                f"| Procesado por: {NOMBRE}",
                flush=True
            )


    except Exception as e:

        if conexion:
            conexion.rollback()

        print(
            f"[{NOMBRE}] Error: {e}",
            flush=True
        )


    finally:

        #Cerrar conexión

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


        #Liberar Mutex

        if adquirido:

            try:
                liberar_mutex(token)

            except Exception as e:

                print(
                    f"[{NOMBRE}] Error liberando mutex: {e}",
                    flush=True
                )


        time.sleep(0.5) 