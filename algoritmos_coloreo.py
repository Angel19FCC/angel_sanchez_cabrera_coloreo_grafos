# ==========================================
# ARCHIVO: algoritmos_busqueda.py
# OBJETIVO: Motores matemáticos para colorear el grafo
# ==========================================
import networkx as nx
import pulp

import copy # Necesitamos esto para crear nuestros "universos paralelos"

def coloreo_greedy(grafo, orden_evaluacion): #recibir el grafo y el orden de evaluacion
    """
    Asigna el número mínimo de bloque de tiempo a cada materia,
    evaluando los nodos en el orden estricto proporcionado.
    """
    
    # Aquí guardaremos el resultado: { 'A': 1, 'B': 2, ... }
    bloques_asignados = {} # se almacenaran los ids de materia y el bloque de tiempo-color asignado
    
    # Le pedimos al grafo su mapa de conflictos
    mapa_conflictos = grafo.obtener_lista_adyacencia() #obtiene la lista completa de conflictos entre los nodos por id y sus conflictos para consultarlos de una forma mas rapida 

    print(f"🔄 Iniciando algoritmo Greedy con el orden: {orden_evaluacion}\n")

    # Evaluamos cada nodo uno por uno según el orden que se quiso agarramos su id 
    for id_materia in orden_evaluacion:
        
        # 1. ¿Qué bloques de tiempo ya tienen mis enemigos?
        bloques_enemigos = set() # Un 'set' es una lista que no admite duplicados:  guarda el bloque asignado para cada nodo-materia sinrepetir para saber que bloque van generanado y asignar el menor posible
        
        for enemigo in mapa_conflictos[id_materia]:  #agara la metria en el orden y revisa sus conlfictos 
            if enemigo in bloques_asignados: # si la materia ya se le asigno un bloque de timepo 
                # Si mi enemigo ya tiene horario, lo anoto para no usarlo
                bloques_enemigos.add(bloques_asignados[enemigo])
        
        #basicamente recorre en el orden selecionado agarrar el primeor y ve a todos sus conflictos y guarda si ya tiene algun bloque de tiempo asignaod un valor y los guarda 
        # el arreglo set solo agurada valores uq eno sea duplicados ys tofos son 2 solo guarda un 2, para saber cual no se debe asignar porque ya existen
        # 2. Buscar el bloque de tiempo (color) más bajo disponible
        bloque_actual = 1  # se trata de asignar siempre el valor mas pequeño posible por eso empeiza en 1
        while bloque_actual in bloques_enemigos: # si ya existen el 1 le suma 1 , si existen el 2 le suma otro asi hasy aque   o exista el valor sea 1 o n 
            # Si el bloque ya lo tiene un enemigo, probamos con el siguiente
            bloque_actual += 1
            
        # 3. ¡Asignamos el bloque!
        bloques_asignados[id_materia] = bloque_actual  #lo asigna con su id de al materia 
        print(f"✅ Materia {id_materia} asignada al Bloque de Tiempo {bloque_actual} (Enemigos en bloques: {list(bloques_enemigos)})")

    return bloques_asignados

def coloreo_dsatur(grafo):
    """
    Algoritmo DSatur: Selecciona dinámicamente el nodo con mayor saturación
    (más colores diferentes a su alrededor) para colorearlo primero.
    """
    bloques_asignados = {}
    mapa_conflictos = grafo.obtener_lista_adyacencia()
    
    # Creamos una lista con todos los IDs que faltan por colorear
    nodos_restantes = list(mapa_conflictos.keys())

    print("🧠 Iniciando algoritmo DSatur...\n")

    while nodos_restantes:
        max_saturacion = -1
        max_grado = -1
        nodo_elegido = None #haremos que el primer nodo sea el mas saturado creo

        # 1. BUSCAR EL NODO MÁS ACORRALADO
        for nodo in nodos_restantes: ## se evaluara toda la lista de nodos
            colores_vecinos = set()
            grado_no_coloreados = 0

            # Revisamos a los enemigos de este nodo
            for enemigo in mapa_conflictos[nodo]: # los comparara con sus enemigos especificos de ese nodo en esa iteracion 
                if enemigo in bloques_asignados: # preguntamos si ya tiene un bloque de color o tiempo asignados, si eese enmigo de esa nodo lista de espera general
                    colores_vecinos.add(bloques_asignados[enemigo]) #guardamos que color tiene 
                else:
                    grado_no_coloreados += 1 # este es un contador de enemigos que tiene

            # La saturación es cuántos colores DIFERENTES lo rodean
            saturacion = len(colores_vecinos) # decuelve la cantidad de objetos que ya tiene color

            # REGLAS DE TORNEO DSATUR:
            # Regla A: Gana el que tenga mayor saturación
            if saturacion > max_saturacion: #quien tenga el mayor numero de vecinos con colores o bloques de tiempo 
                max_saturacion = saturacion
                max_grado = grado_no_coloreados
                nodo_elegido = nodo
                
            # Regla B (Desempate): Si tienen la misma saturación, gana el que 
            # tenga más enemigos aún sin colorear (mayor grado incidente)
            elif saturacion == max_saturacion and grado_no_coloreados > max_grado: #checar si tienen el mismo numero de bloques y si tiene mas enemigos sin colorear
                max_grado = grado_no_coloreados
                nodo_elegido = nodo

        # 2. ASIGNARLE EL COLOR MÁS BAJO DISPONIBLE AL GANADOR
        colores_prohibidos = set()
        for enemigo in mapa_conflictos[nodo_elegido]:
            if enemigo in bloques_asignados:
                colores_prohibidos.add(bloques_asignados[enemigo])

        color_actual = 1
        while color_actual in colores_prohibidos:
            color_actual += 1

        # 3. GUARDAR RESULTADO Y QUITARLO DE LA LISTA
        bloques_asignados[nodo_elegido] = color_actual
        nodos_restantes.remove(nodo_elegido)
        
        print(f"✅ Se eligió la Materia {nodo_elegido} (Saturación: {max_saturacion}) -> Bloque asignado: {color_actual}")

    return bloques_asignados

def coloreo_ilp(grafo):
    """
    Algoritmo ILP (Programación Lineal Entera) usando PuLP.
    Garantiza el número mínimo absoluto de bloques de tiempo (Número Cromático).
    """
    mapa_conflictos = grafo.obtener_lista_adyacencia()
    nodos = list(mapa_conflictos.keys()) #genra una lista de todos los nodos
    
    # El máximo de colores posibles (en el peor caso, cada materia tiene su propio bloque)
    max_colores = len(nodos)
    colores_posibles = range(1, max_colores + 1)

    print("⚙️ Construyendo modelo matemático ILP...")

    # 1. CREAR EL MODELO
    # Le decimos a PuLP que nuestro objetivo es MINIMIZAR el número de colores
    modelo = pulp.LpProblem("Problema_Coloreo_Horarios", pulp.LpMinimize)

    # 2. DEFINIR LAS VARIABLES MATEMÁTICAS (Nuestras incógnitas)
    
    # Variable 'Y': ¿Se usó el bloque de tiempo 'c'? (1 si se usa, 0 si no)
    y = pulp.LpVariable.dicts("UsoBloque", colores_posibles, cat=pulp.LpBinary)
    
    # Variable 'X': ¿La materia 'n' está asignada al bloque 'c'? (1 si sí, 0 si no)
    x = pulp.LpVariable.dicts("Asignacion", 
    [(n, c) for n in nodos for c in colores_posibles], 
    cat=pulp.LpBinary)

    # 3. FUNCIÓN OBJETIVO
    # Queremos que la suma de los bloques usados ('Y') sea lo más pequeña posible
    modelo += pulp.lpSum([y[c] for c in colores_posibles])

    # 4. LAS REGLAS ESTRICTAS (Restricciones)

    # Regla A: Cada materia debe tener EXACTAMENTE UN bloque de tiempo
    for n in nodos:
        modelo += pulp.lpSum([x[(n, c)] for c in colores_posibles]) == 1

    # Regla B: Si dos materias chocan, NO pueden tener el mismo bloque 'c'
    # Además, vinculamos 'X' con 'Y' (Si alguien usa el bloque 'c', entonces Y[c] debe ser 1)
    for n1 in nodos:
        for n2 in mapa_conflictos[n1]:
            # Para evitar duplicar ecuaciones, solo lo hacemos en una dirección (ej. A < B)
            if n1 < n2: 
                for c in colores_posibles:
                    # La suma de las asignaciones de n1 y n2 en el color 'c' no puede ser mayor que Y[c]
                    modelo += x[(n1, c)] + x[(n2, c)] <= y[c]

    # 5. ¡RESOLVER EL SISTEMA DE ECUACIONES!
    print("🚀 Resolviendo ecuaciones...")
    modelo.solve(pulp.PULP_CBC_CMD(msg=False)) # 'msg=False' es para que no imprima basura técnica

    # 6. TRADUCIR LA RESPUESTA MATEMÁTICA (Colores Crudos)
    bloques_brutos = {}
    
    # Revisamos cuáles variables 'X' terminaron valiendo 1 (es decir, Verdadero)
    for n in nodos:
        for c in colores_posibles:
            if pulp.value(x[(n, c)]) == 1:
                bloques_brutos[n] = c
                print(f"✅ Matemáticamente comprobado: Materia {n} -> Bloque {c}")
                break

    # 7. COMPRIMIR Y RE-ORDENAR LOS COLORES (Para que empiecen en 1)
    print("🧹 Comprimiendo bloques de tiempo...")
    
    # a) Sacamos una lista de los colores únicos que realmente se usaron y los ordenamos.
    # Si la compu usó [4, 7, 5, 4], esto lo convierte en una lista limpia: [4, 5, 7]
    colores_unicos = sorted(list(set(bloques_brutos.values()))) 
    
    # b) Creamos un "Diccionario Traductor" usando enumerate (que empieza a contar desde 1)
    # Esto creará algo como: {4: 1, 5: 2, 7: 3}
    traductor_colores = {color_viejo: nuevo_id for nuevo_id, color_viejo in enumerate(colores_unicos, 1)}
    
    bloques_asignados = {}
    
    # c) Aplicamos la traducción a todas las materias
    for n, color_viejo in bloques_brutos.items():
        color_nuevo = traductor_colores[color_viejo]
        bloques_asignados[n] = color_nuevo
        print(f"✅ Materia {n} -> Bloque {color_nuevo} (Era el {color_viejo})")
    return bloques_asignados

def coloreo_zykov(grafo):
    """
    Algoritmo exacto de Zykov mediante recursividad.
    Encuentra el número cromático perfecto creando ramas de contracción y adición.
    """
    print("🌳 Iniciando algoritmo de Zykov (explorando universos paralelos)...")
    mapa_original = grafo.obtener_lista_adyacencia()

    # --- FUNCIÓN RECURSIVA INTERNA ---
    def zykov_recursivo(mapa):
        nodos = list(mapa.keys())
        u, v = None, None
        
        # 1. BUSCAR DOS MATERIAS QUE NO CHOQUEN
        for i in range(len(nodos)):
            for j in range(i+1, len(nodos)):
                if nodos[j] not in mapa[nodos[i]]:
                    u, v = nodos[i], nodos[j]
                    break
            if u: break # Si ya encontramos un par, dejamos de buscar
            
        # 2. CASO BASE: EL CLIQUE PERFECTO
        if not u:
            # Si NO encontramos ninguna pareja sin chocar, significa que TODOS chocan.
            # La única solución es darle un bloque de tiempo distinto a cada uno.
            colores = {}
            for indice, nodo in enumerate(nodos):
                colores[nodo] = indice + 1
            return colores
            
        # 3. UNIVERSO A: OBLIGARLOS A TENER HORARIOS DIFERENTES (Adición)
        mapa_adicion = copy.deepcopy(mapa) # Clonamos el mapa
        mapa_adicion[u].append(v)          # Inventamos un choque falso entre ellos
        mapa_adicion[v].append(u)
        colores_adicion = zykov_recursivo(mapa_adicion) # Viajamos al futuro de este universo
        
        # 4. UNIVERSO B: OBLIGARLOS A COMPARTIR EL MISMO HORARIO (Contracción)
        mapa_contraccion = copy.deepcopy(mapa)
        enemigos_de_v = mapa_contraccion.pop(v) # Eliminamos a 'v' y nos quedamos con sus enemigos
        
        for enemigo in enemigos_de_v:
            if enemigo != u:
                mapa_contraccion[enemigo].remove(v) # Le quitamos 'v' a la lista del enemigo
                if u not in mapa_contraccion[enemigo]:
                    # Fusionamos a 'v' dentro de 'u'
                    mapa_contraccion[enemigo].append(u) 
                    mapa_contraccion[u].append(enemigo)
                    
        colores_contraccion_futuro = zykov_recursivo(mapa_contraccion)
        
        # Regresando del futuro del Universo B, le asignamos a 'v' el mismo color que a 'u'
        colores_contraccion = colores_contraccion_futuro.copy()
        colores_contraccion[v] = colores_contraccion[u]
        
        # 5. EL COMBATE FINAL: ¿QUÉ UNIVERSO FUE MÁS EFICIENTE?
        max_colores_a = max(colores_adicion.values())
        max_colores_b = max(colores_contraccion.values())
        
        if max_colores_b <= max_colores_a:
            return colores_contraccion
        else:
            return colores_adicion

    # --- EJECUCIÓN DEL ALGORITMO ---
    resultado_final = zykov_recursivo(mapa_original)
    print(f"✅ Zykov finalizado. Bloques máximos usados: {max(resultado_final.values())}")
    return resultado_final

def coloreo_welsh_powell(grafo):
    """
    Algoritmo Welsh-Powell:
    1. Ordena los nodos de mayor a menor grado (más conflictos primero).
    2. Toma el Bloque 1 y asigna todas las materias posibles que no choquen entre sí.
    3. Pasa al Bloque 2 y repite con los restantes.
    """
    mapa_conflictos = grafo.obtener_lista_adyacencia()
    bloques_asignados = {}

    print("📊 Iniciando algoritmo Welsh-Powell...")

    # 1. ORDENAMIENTO INTELIGENTE
    # Calculamos cuántos enemigos tiene cada nodo (len(mapa_conflictos[x]))
    # y ordenamos la lista de MAYOR a MENOR (reverse=True)
    nodos_ordenados = sorted(list(mapa_conflictos.keys()), 
                            key=lambda x: len(mapa_conflictos[x]), 
                            reverse=True)

    print(f"📋 Fila ordenada (Mayor a Menor grado): {nodos_ordenados}\n")

    bloque_actual = 1

    # 2. EL BUCLE PRINCIPAL (Mientras haya materias sin horario)
    while len(bloques_asignados) < len(nodos_ordenados):
        print(f"--- Abriendo Bloque de Tiempo {bloque_actual} ---")

        # 3. RECORREMOS LA FILA BUSCANDO QUIÉN CABE EN ESTE BLOQUE
        for nodo in nodos_ordenados:
            
            # Si el nodo ya tiene horario asignado, lo ignoramos
            if nodo in bloques_asignados:
                continue

            # Revisamos si este nodo choca con ALGUIEN que YA ESTÉ en el bloque_actual
            puede_entrar = True
            for enemigo in mapa_conflictos[nodo]:
                # Si el enemigo ya tiene horario Y además está en este mismo bloque
                if enemigo in bloques_asignados and bloques_asignados[enemigo] == bloque_actual:
                    puede_entrar = False
                    break # ¡Choca! Detenemos la revisión y rechazamos a esta materia

            # Si pasó la prueba (no choca con nadie de este bloque), la agendamos
            if puede_entrar:
                bloques_asignados[nodo] = bloque_actual
                print(f"✅ Materia {nodo} asignada al Bloque {bloque_actual} (Tenía {len(mapa_conflictos[nodo])} conflictos)")

        # Una vez que ya nadie más cupo en este bloque, abrimos el siguiente
        bloque_actual += 1

    print(f"\n🏆 Welsh-Powell finalizado. Bloques máximos usados: {bloque_actual - 1}")
    return bloques_asignados

def validar_coloreo_propio(grafo_conflictos, resultados):
    """
    Valida si la coloración es propia (ningún par de nodos adyacentes comparten el mismo bloque/color).
    'grafo_conflictos' es el objeto de tu clase GrafoDeConflictos.
    'resultados' es el diccionario con los bloques asignados {nodo: bloque}.
    """
    # 1. Construimos la red con NetworkX a partir del backend para extraer las aristas
    G = nx.Graph()
    mapa_ady = grafo_conflictos.obtener_lista_adyacencia()
    for nodo, enemigos in mapa_ady.items():
        G.add_node(nodo)
        for e in enemigos:
            G.add_edge(nodo, e)
            
    # 2. Validamos que ningún nodo adyacente comparta el mismo color
    for u, v in G.edges():
        bloque_u = resultados.get(u)
        bloque_v = resultados.get(v)
        
        # Si la arista existe y los colores son iguales, hay un conflicto
        if bloque_u == bloque_v:
            return False
            
    return True

# --- BLOQUE DE PRUEBA ---
"""if __name__ == "__main__":
    # Importamos la clase que creaste en el otro archivo
    from estructura_nodo_grafo import GrafoDeConflictos, NodoMateria

    # 1. Creamos el grafo y lo llenamos (Usaremos toda la Tabla 1 para la prueba real)
    mi_grafo = GrafoDeConflictos()
    mi_grafo.agregar_nodo(NodoMateria('A', 'Mate I', 'G1', 'T1'))
    mi_grafo.agregar_nodo(NodoMateria('B', 'Mate II', 'G1', 'T2'))
    mi_grafo.agregar_nodo(NodoMateria('C', 'Mate III', 'G1', 'T3'))
    mi_grafo.agregar_nodo(NodoMateria('D', 'Física I', 'G2', 'T1'))
    mi_grafo.agregar_nodo(NodoMateria('E', 'Física II', 'G2', 'T2'))
    mi_grafo.agregar_nodo(NodoMateria('F', 'Física III', 'G2', 'T3'))
    mi_grafo.agregar_nodo(NodoMateria('G', 'Prog I', 'G3', 'T1'))
    mi_grafo.agregar_nodo(NodoMateria('H', 'Prog II', 'G3', 'T2'))
    mi_grafo.agregar_nodo(NodoMateria('I', 'Prog III', 'G3', 'T3'))

    # 2. El orden exacto que te pidió el profesor en la Tarea 3
    orden_profesor = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

    # 3. ¡Ejecutamos el motor matemático!
    print("\n--- RESULTADO DEL COLOREO ---")
    resultado = coloreo_greedy(mi_grafo, orden_profesor)

    #resultado = coloreo_welsh_powell(mi_grafo) """