import threading
import time
import numpy as np
import sqlite3

class SistemaMonitoreoCardiaco:
    def __init__(self, db_file="frecuencia_cardiaca.db"):
        self.frecuencia_cardiaca = 60  # Frecuencia cardíaca inicial
        self.detener_hilo = False
        self.db_file = db_file


        #-----------------------------------------------------------------------------------------        
        # 1/3 IMPLEMENTACIÓN SEMAFORO
        #-----------------------------------------------------------------------------------------
        self.semaforo = threading.Semaphore(1)  # Inicializar semáforo binario con 1


        #-----------------------------------------------------------------------------------------
        # 2/3 IMPLEMENTACIÓN BASE DE DATOS
        #-----------------------------------------------------------------------------------------        
        # Conexión a la base de datos SQLite3
        self.conn = sqlite3.connect(db_file, check_same_thread=False)  # Permitir acceso desde diferentes hilos
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS frecuencia_cardiaca
                          (timestamp REAL, frecuencia REAL)''')
        self.conn.commit()

    def simular_frecuencia_cardiaca(self):
        while not self.detener_hilo:
            # Simular cambios en la frecuencia cardíaca
            nueva_frecuencia = 60 + 10 * np.sin(time.time() / 10)  # Simulación de una frecuencia variable
            self.semaforo.acquire()
            self.frecuencia_cardiaca = nueva_frecuencia
            self.semaforo.release()
            # Guardar la frecuencia cardíaca en la base de datos
            conn = sqlite3.connect(self.db_file)  # Crear una nueva conexión para cada iteración
            c = conn.cursor()
            c.execute("INSERT INTO frecuencia_cardiaca (timestamp, frecuencia) VALUES (?, ?)",
                       (time.time(), nueva_frecuencia))
            conn.commit()
            conn.close()
            time.sleep(1)  # Actualizar cada segundo

    def visualizar_frecuencia_cardiaca(self):
        while not self.detener_hilo:
            # Imprimir la frecuencia cardíaca en tiempo real
            self.semaforo.acquire()
            print("Frecuencia cardíaca:", self.frecuencia_cardiaca)
            self.semaforo.release()
            time.sleep(1)  # Actualizar cada segundo

    def iniciar_monitoreo(self):
        # Crear hilos para simular y visualizar la frecuencia cardíaca
        hilo_simulacion = threading.Thread(target=self.simular_frecuencia_cardiaca)
        hilo_visualizacion = threading.Thread(target=self.visualizar_frecuencia_cardiaca)

        # Iniciar los hilos
        hilo_simulacion.start()
        hilo_visualizacion.start()

        # Esperar a que los hilos terminen (esto no sucederá en este ejemplo)
        hilo_simulacion.join()
        hilo_visualizacion.join()

    def detener_monitoreo(self):
        self.detener_hilo = True
        # Cerrar la conexión con la base de datos
        self.conn.close()

#----------------------------------------------------------------------------------------------
# 3/3 IMPLEMENTACIÓN EXCEPCIONES
#----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    sistema_monitoreo = SistemaMonitoreoCardiaco()

    try:
        # Iniciar el monitoreo
        sistema_monitoreo.iniciar_monitoreo()
    except KeyboardInterrupt:
        # Manejar la interrupción del teclado (Ctrl+C)
        sistema_monitoreo.detener_monitoreo()
        print("\nMonitoreo detenido por el usuario.")
