# ==========================================
# ARCHIVO: estructura_nodo_grafo.py
# OBJETIVO: Definir la estructura de datos del nodo y del grafo
# ==========================================

class NodoMateria:
    """Representa un nodo individual en el grafo."""
    def __init__(self, id_materia, materia, grupo, docente): 
            self.id_materia = id_materia
            self.materia = materia
            self.grupo = grupo
            self.docente = docente
    """ Define la funcion, define el constructor y guarda los sus datos provenientes de los parametros   """

    def __str__(self):
        """Generamos una funcion para imprimir los datos."""
        return f"[{self.id_materia}] {self.materia} (G:{self.grupo}, D:{self.docente})"
    
class GrafoDeConflictos:
    """Gestiona los nodos y genera las aristas automáticamente."""
    def __init__(self): # definir la funcion y el contructor del grafo
        self.nodos = {}       # lista total de nodos
        self.adyacencia_conflicto = {}  # Lista de IDs conflictivos por nodo

    def agregar_nodo(self, nueva_materia):
        """Añade un nodo y calcula sus conflictos en tiempo real."""

        # --- VALIDACIÓN DE SEGURIDAD ---
        if nueva_materia.id_materia in self.nodos:
            print(f"⚠️ ALERTA: La materia con ID '{nueva_materia.id_materia}' ya existe. No se admiten duplicados.")
            return 
        # -------------------------------

        # 1. Guardamos el nuevo nodo y generamos una lista vacia para identificar los nodos con conflicto
        self.nodos[nueva_materia.id_materia] = nueva_materia
        self.adyacencia_conflicto[nueva_materia.id_materia] = []

        # 2. Comparamos contra los nodos existentes
        for id_existente, materia_existente in self.nodos.items():
            if nueva_materia.id_materia != id_existente: #evitar que se compara con sigo misma
                # REGLA DE CONFLICTO: Comparten Grupo O Docente
                if (nueva_materia.grupo == materia_existente.grupo) or (nueva_materia.docente == materia_existente.docente):
                    # Agregamos la conexión en ambas direcciones (Grafo no dirigido) agregando a su lista de conflictos
                    self.adyacencia_conflicto[nueva_materia.id_materia].append(id_existente)
                    self.adyacencia_conflicto[id_existente].append(nueva_materia.id_materia)

    def obtener_lista_adyacencia(self):
        """Devuelve el diccionario de conflictos."""
        return self.adyacencia_conflicto
    
    def limpiar_grafo(self):
        """Elimina todos los nodos y conflictos, dejando el grafo en blanco."""
        self.nodos = {}
        self.adyacencia_conflicto = {}
        print("🧹 El grafo ha sido limpiado por completo.")

    def eliminar_nodo(self, id_materia):
        """Elimina un nodo y limpia todas las conexiones que los demás tenían con él."""

        # 1. Verificamos si existe
        if id_materia not in self.nodos:
            print(f"⚠️ Error: No se puede eliminar. La materia '{id_materia}' no existe.")
            return
        
        # 2. Borrar las conexiones "fantasma"
        # Obtenemos la lista de los nodos con los que choca
        enemigos = self.adyacencia_conflicto[id_materia]

        # Le decimos a cada enemigo: "Busca a esta materia en tu lista y bórrala"
        for id_enemigo in enemigos:
            self.adyacencia_conflicto[id_enemigo].remove(id_materia)

        # 3. Eliminar el nodo de los registros principales
        del self.nodos[id_materia]
        del self.adyacencia_conflicto[id_materia]

        print(f"🗑️ La materia '{id_materia}' y todos sus conflictos fueron eliminados correctamente.")
    
# --- BLOQUE DE PRUEBA ---
# Esto solo se ejecuta si corremos este archivo directamente
"""if __name__ == "__main__":
    # 1. Iniciamos el grafo
    mi_grafo = GrafoDeConflictos()

    # 2. Agregamos las clases de tu Tabla 1 
    mi_grafo.agregar_nodo(NodoMateria('A', 'Mate I', 'G1', 'T1'))
    mi_grafo.agregar_nodo(NodoMateria('B', 'Mate II', 'G1', 'T2'))
    mi_grafo.agregar_nodo(NodoMateria('C', 'Mate III', 'G1', 'T3'))
    mi_grafo.agregar_nodo(NodoMateria('D', 'Fisica I', 'G2', 'T1'))
    mi_grafo.agregar_nodo(NodoMateria('E', 'Fisica II', 'G2', 'T2'))
    mi_grafo.agregar_nodo(NodoMateria('F', 'Fisica III', 'G2', 'T3'))
    mi_grafo.agregar_nodo(NodoMateria('G', 'Porg I', 'G3', 'T1'))
    mi_grafo.agregar_nodo(NodoMateria('H', 'Porg II', 'G3', 'T2'))
    mi_grafo.agregar_nodo(NodoMateria('I', 'Porg III', 'G3', 'T3'))

    # 3. Imprimimos el resultado final
    print("\n--- MAPA DE CONFLICTOS GENERADO ---")
    mapa = mi_grafo.obtener_lista_adyacencia()
    for id_materia, lista_enemigos in mapa.items():
        print(f"La Materia {id_materia} choca con: {lista_enemigos}")
    
    mi_grafo.eliminar_nodo('B')
    mapa = mi_grafo.obtener_lista_adyacencia()
    for id_materia, lista_enemigos in mapa.items():
        print(f"La Materia {id_materia} choca con: {lista_enemigos}")

    mi_grafo.limpiar_grafo()
    mapa = mi_grafo.obtener_lista_adyacencia()
    for id_materia, lista_enemigos in mapa.items():
        print(f"La Materia {id_materia} choca con: {lista_enemigos}")"""