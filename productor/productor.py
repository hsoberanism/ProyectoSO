import mysql.connector
import random
import time
import os
from datetime import datetime

#Conexión a la base de datos buscando usuario y contraseña en el archivo .env
def conectar():
    return mysql.connector.connect(
        host="mysql",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

#Impresión de inicio del contenedor
print("[PRODUCTOR] Iniciado", flush=True)

#Ciclo de escritura en la base de datos, hasta que se detenga el contenedor
while True:
    #Intento de conexión y escritura en base de datos
    try:
        #Conexión a la base de datos
        conexion = conectar()
        cursor = conexion.cursor()

        #Generación de Datos aleatorios
        cuenta = str(random.randint(10000000, 99999999))

        tipo = random.choice(["MONETARIA", "AHORRO"])

        monto = round(random.uniform(10, 5000), 2)

        moneda = random.choice(["GTQ", "USD"])

        #Inserción de los datos generados
        sql = """
            INSERT INTO banco
            (cuenta, tipo, monto, moneda, estado)
            VALUES (%s, %s, %s, %s, 'PENDIENTE')
        """

        cursor.execute(
            sql,
            (cuenta, tipo, monto, moneda)
        )

        conexion.commit()

        id_transaccion = cursor.lastrowid

        hora = datetime.now().strftime("%H:%M:%S")

        #Impresión en pantalla de los datos insertados
        print(
            f"[{hora}] [PRODUCTOR] "
            f"Transacción #{id_transaccion} "
            f"| Cuenta: {cuenta} "
            f"| Tipo: {tipo} "
            f"| Monto: {monto} {moneda} "
            f"| PENDIENTE",
            flush=True
        )

        #Cierre de la conexión
        cursor.close()
        conexion.close()

        #Espera aleatoria entre 1 y 2 segundos para el siguiente registro
        tiempo = random.uniform(
            float(os.getenv("INTERVALO_PRODUCTOR_MIN", 1)),
            float(os.getenv("INTERVALO_PRODUCTOR_MAX", 2))
        )

        time.sleep(tiempo)

    #En caso de fallar la conexión muestra el error y espera 3 segundos para volder a intentar
    except Exception as e:
        print(f"[PRODUCTOR] Error: {e}", flush=True)
        time.sleep(3)