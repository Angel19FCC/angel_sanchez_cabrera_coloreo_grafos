# ==========================================
# ARCHIVO: app.py
# OBJETIVO: Interfaz Gráfica Profesional e Interactiva
# ==========================================

import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import time

# Importamos tu Cerebro y tus Motores
from estructura_nodo_grafo import GrafoDeConflictos, NodoMateria
import algoritmos_coloreo 

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera línea)
st.set_page_config(page_title="Optimizador de Horarios", layout="wide", page_icon="🎓")

# Paleta de colores profesionales para los Bloques
PALETA = ['#CCCCCC', '#b0c2f2', '#d2bead', '#ffda9e', '#d3bcf6', '#a0d995', '#b2e2f2', '#fdcae1', '#ebf3a0', '#ff9688', '#c0a0c3', '#ffe5f0', '#c5d084']

# 2. INICIALIZAR LA MEMORIA (Session State) 
if 'grafo' not in st.session_state:
    st.session_state.grafo = GrafoDeConflictos()
    st.session_state.materias = {} # Para guardar la info de los nodos
    st.session_state.resultados = {}
    st.session_state.orden_coloreo = []

# --- FUNCIONES DE CONTROL ---
def precargar_tabla_1():
    st.session_state.grafo = GrafoDeConflictos()
    st.session_state.materias = {}
    datos = [
        ('A', 'Mate I', 'G1', 'T1'), ('B', 'Mate II', 'G1', 'T2'), ('C', 'Mate III', 'G1', 'T3'),
        ('D', 'Física I', 'G2', 'T1'), ('E', 'Física II', 'G2', 'T2'), ('F', 'Física III', 'G2', 'T3'),
        ('G', 'Prog I', 'G3', 'T1'), ('H', 'Prog II', 'G3', 'T2'), ('I', 'Prog III', 'G3', 'T3')
    ]
    for id_mat, nom, grp, prof in datos:
        nodo = NodoMateria(id_mat, nom, grp, prof)
        st.session_state.grafo.agregar_nodo(nodo)
        st.session_state.materias[id_mat] = nodo
    st.session_state.resultados = {}

def limpiar_interfaz():
    # 1. Usamos TU función interna para vaciar el backend matemático
    st.session_state.grafo.limpiar_grafo() 
    
    # 2. Vaciamos la memoria visual de Streamlit (Frontend)
    st.session_state.materias.clear()
    st.session_state.resultados.clear()
    st.session_state.orden_coloreo.clear()

# --- FÁBRICA DE GRÁFICOS ---
def dibujar_grafo_estatico(diccionario_resultados):
    """Genera una imagen Plotly del grafo basándose en un diccionario de colores."""
    G = nx.Graph()
    mapa_ady = st.session_state.grafo.obtener_lista_adyacencia()
    for nodo, enemigos in mapa_ady.items():
        G.add_node(nodo)
        for e in enemigos:
            G.add_edge(nodo, e)
            
    if 'pos' not in st.session_state or len(st.session_state.pos) != len(G.nodes):
        st.session_state.pos = nx.spring_layout(G, seed=42)
    pos = st.session_state.pos

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines')

    node_x, node_y, node_color, node_text = [], [], [], []
    for nodo in G.nodes():
        x, y = pos[nodo]
        node_x.append(x)
        node_y.append(y)
        
        # Colorear según el diccionario que le pasemos
        if diccionario_resultados and nodo in diccionario_resultados:
            bloque = diccionario_resultados[nodo]
            color = PALETA[bloque % len(PALETA)]
            info = f"<br><b>Bloque: {bloque}</b>"
        else:
            color = PALETA[0]
            info = "<br><i>Sin asignar</i>"
            
        node_color.append(color)
        mat_info = st.session_state.materias[nodo]
        node_text.append(f"<b>Materia {nodo}: {mat_info.materia}</b>{info}")

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', hoverinfo='text', 
                            text=[str(n) for n in G.nodes()], textposition="middle center", hovertext=node_text,
                            marker=dict(showscale=False, color=node_color, size=45, line_width=2, line_color='white'))

    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), plot_bgcolor='rgba(0,0,0,0)'))
    return fig
# ---------------------------

# 3. BARRA LATERAL (Panel de Control)
with st.sidebar:
    st.image("https://secreacademica.cs.buap.mx/images/logo_FCC.png", width=200) #https://cdn-icons-png.flaticon.com/512/2232/2232688.png   80
    st.title("Panel de Control")
    
    st.header("1. Gestión de Datos")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Cargar Tabla 1", use_container_width=True): precargar_tabla_1()
    with col2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True): limpiar_interfaz()

    st.markdown("---")
    st.header("2. Agregar Materia")
    with st.form("form_agregar", clear_on_submit=True):
        n_id = st.text_input("ID (Ej. J)")
        n_nom = st.text_input("Nombre (Ej. Química)")
        n_grp = st.text_input("Grupo (Ej. G4)")
        n_prof = st.text_input("Profesor (Ej. T4)")
        
        if st.form_submit_button("➕ Agregar al Grafo"):
            if n_id and n_grp and n_prof:
                
                n_id_limpio = n_id.strip().upper()
                n_grp_limpio = n_grp.strip().upper()
                n_prof_limpio = n_prof.strip().upper()
                
                # --- AQUÍ ESTÁ LA NUEVA VALIDACIÓN VISUAL ---
                # Revisamos si el ID ya existe en nuestra memoria de Streamlit
                if n_id_limpio in st.session_state.materias:
                    st.error(f"🛑 Error Matemático: El ID '{n_id_limpio}' ya existe en el sistema. Por definición formal, un grafo es un conjunto de vértices y no admite duplicados.")
                else:
                    # Si no existe, procedemos a crearlo normalmente
                    nodo = NodoMateria(n_id_limpio, n_nom, n_grp_limpio, n_prof_limpio)
                    
                    st.session_state.grafo.agregar_nodo(nodo)
                    st.session_state.materias[n_id_limpio] = nodo
                    st.session_state.resultados.clear() 
                    
                    st.rerun()
            else:
                st.warning("Debes llenar ID, Grupo y Profesor para detectar los choques.")

    st.markdown("---")
    st.header("3. Eliminar Materia")
    
    # Solo mostramos el menú si hay materias en el grafo
    if st.session_state.materias:
        # Creamos un menú desplegable con las letras actuales (A, B, C...)
        nodo_a_borrar = st.selectbox("Selecciona la materia a eliminar:", 
                                    list(st.session_state.materias.keys()))
        
        if st.button("❌ Eliminar del Grafo", use_container_width=True):
            # 1. Usamos TU función interna para borrar la matemática y sus aristas
            st.session_state.grafo.eliminar_nodo(nodo_a_borrar)
            
            # 2. Lo borramos de la memoria visual de Streamlit
            del st.session_state.materias[nodo_a_borrar]
            
            # 3. Borramos los resultados, ¡porque al quitar un nodo, el Número Cromático puede cambiar!
            st.session_state.resultados.clear()
            st.session_state.orden_coloreo.clear()
            
            # 4. Refrescamos la pantalla para que el círculo desaparezca instantáneamente
            st.rerun()
    else:
        st.info("El grafo está vacío.")

    st.markdown("---")
    st.header("4. Algoritmos de coloreo")
    
    modo_batalla = st.toggle("⚔️ Modo Comparación (A vs B)")
    
    orden_usuario = [] # Variable vacía por seguridad

    if modo_batalla:
        st.info("Compara dos algoritmos sobre la misma estructura de materias.")
        col_a, col_b = st.columns(2)
        with col_a:
            algo_A = st.selectbox("Algoritmo A:", ["Greedy", "Welsh-Powell", "DSatur", "ILP (Exacto)", "Zykov (Exacto)"], key="A")
        with col_b:
            algo_B = st.selectbox("Algoritmo B:", ["DSatur", "Greedy", "Welsh-Powell", "ILP (Exacto)", "Zykov (Exacto)"], key="B")
            
        # --- EL TRUCO: Si alguno de los dos es Greedy, mostramos la caja de orden ---
        if "Greedy" in [algo_A, algo_B] and st.session_state.materias:
            st.info("💡 ¡Elegiste Greedy en la batalla! Define su orden de evaluación para ponerle una trampa:")
            lista_actual = list(st.session_state.materias.keys())
            orden_usuario = st.multiselect(
                "Orden manual para Greedy:",
                options=lista_actual,
                default=lista_actual
            )
            
    else:
        # Modo de un solo algoritmo
        algoritmo_elegido = st.selectbox("Selecciona el Algoritmo:", 
                                        ["Greedy", "Welsh-Powell", "DSatur", "ILP (Exacto)", "Zykov (Exacto)"])
        
        if algoritmo_elegido == "Greedy" and st.session_state.materias:
            st.info("💡 Greedy es un algoritmo 'ciego' que depende del orden. ¡Ingrésalo para ponerle una trampa!")
            lista_actual = list(st.session_state.materias.keys())
            orden_usuario = st.multiselect(
                "Elige el orden de evaluación (Debes seleccionar todas):",
                options=lista_actual,
                default=lista_actual 
            )
    
    
    if st.button("▶️ EJECUTAR COLOREO", type="primary", use_container_width=True):
        if not st.session_state.materias:
            st.warning("El grafo está vacío.")
        else:
            with st.spinner("Calculando sistemas óptimos..."):
                
                if modo_batalla:
                    # 1. Validación de seguridad en la Batalla
                    if "Greedy" in [algo_A, algo_B]:
                        if len(orden_usuario) != len(st.session_state.materias):
                            st.error("⚠️ Para que Greedy compita, debes incluir TODAS las materias en el selector de orden.")
                            st.stop()
                    
                    st.session_state.modo_actual = "batalla"
                    st.session_state.nombre_A = algo_A
                    st.session_state.nombre_B = algo_B
                    
                    # Fíjate cómo Greedy ahora lee orden_usuario
                    funciones = {
                        "Greedy": lambda: algoritmos_coloreo.coloreo_greedy(st.session_state.grafo, orden_usuario),
                        "Welsh-Powell": lambda: algoritmos_coloreo.coloreo_welsh_powell(st.session_state.grafo),
                        "DSatur": lambda: algoritmos_coloreo.coloreo_dsatur(st.session_state.grafo),
                        "ILP (Exacto)": lambda: algoritmos_coloreo.coloreo_ilp(st.session_state.grafo),
                        "Zykov (Exacto)": lambda: algoritmos_coloreo.coloreo_zykov(st.session_state.grafo)
                    }
                    st.session_state.res_A = funciones[algo_A]()
                    st.session_state.res_B = funciones[algo_B]()

                    # --- AQUÍ VALIDAMOS EN MODO BATALLA ---
                    val_A = algoritmos_coloreo.validar_coloreo_propio(st.session_state.grafo, st.session_state.res_A)
                    val_B = algoritmos_coloreo.validar_coloreo_propio(st.session_state.grafo, st.session_state.res_B)
                    
                    if val_A and val_B:
                        st.success("Ambas coloraciones son propias y no tienen conflictos.")
                    else:
                        st.error("Se detectó un conflicto en al menos uno de los algoritmos.")
                        
                else:
                    st.session_state.modo_actual = "normal"
                    
                    if algoritmo_elegido == "Greedy":
                        if len(orden_usuario) != len(st.session_state.materias):
                            st.error("⚠️ Para usar Greedy, debes incluir TODAS las materias en el selector.")
                            st.stop() 
                        st.session_state.resultados = algoritmos_coloreo.coloreo_greedy(st.session_state.grafo, orden_usuario)
                    elif algoritmo_elegido == "Welsh-Powell":
                        st.session_state.resultados = algoritmos_coloreo.coloreo_welsh_powell(st.session_state.grafo)
                    elif algoritmo_elegido == "DSatur":
                        st.session_state.resultados = algoritmos_coloreo.coloreo_dsatur(st.session_state.grafo)
                    elif algoritmo_elegido == "ILP (Exacto)":
                        st.session_state.resultados = algoritmos_coloreo.coloreo_ilp(st.session_state.grafo)
                    elif algoritmo_elegido == "Zykov (Exacto)":
                        st.session_state.resultados = algoritmos_coloreo.coloreo_zykov(st.session_state.grafo)
                    
                    st.session_state.orden_coloreo = list(st.session_state.resultados.keys())

                    # --- AQUÍ VALIDAMOS EN MODO NORMAL ---
                    val_normal = algoritmos_coloreo.validar_coloreo_propio(st.session_state.grafo, st.session_state.resultados)
                    
                    if val_normal:
                        
                        # 2. Tarjeta de éxito estilizada
                        st.success("🎉 ¡Validación de Coloración Propia Exitosa!")
                        st.toast("El horario cumple con todas las restricciones operativas.", icon="✅")
                        
                        # 3. Construimos el grafo temporal para listar las relaciones validadas
                        import networkx as nx
                        
                        G_temp = nx.Graph()
                        mapa_ady = st.session_state.grafo.obtener_lista_adyacencia()
                        for nodo, enemigos in mapa_ady.items():
                            G_temp.add_node(nodo)
                            for e in enemigos:
                                G_temp.add_edge(nodo, e)
                        
                        # 4. Detalle expandible con la tabla de evaluación
                        with st.expander("Ver detalles de la validación"):
                            st.markdown("* **Resultado:** La coloración es propia. El horario no tiene conflictos.")
                            st.markdown(f"* **Relaciones analizadas:** {len(G_temp.edges())}")
                            
                            datos_eval = []
                            for u, v in G_temp.edges():
                                datos_eval.append({
                                    "Materia A": u,
                                    "Bloque A": st.session_state.resultados.get(u),
                                    "Materia B": v,
                                    "Bloque B": st.session_state.resultados.get(v)
                                })
                            
                            import pandas as pd
                            df_eval = pd.DataFrame(datos_eval)
                            st.dataframe(df_eval, use_container_width=True)
                            
                    else:
                        st.error("⚠️ Error en la Coloración: Se detectaron conflictos.")
                        st.toast("Existen materias en conflicto con el mismo bloque asignado.", icon="❌")
                        
                        # Mostramos qué materias chocan
                        import networkx as nx
                        
                        G_temp = nx.Graph()
                        mapa_ady = st.session_state.grafo.obtener_lista_adyacencia()
                        for nodo, enemigos in mapa_ady.items():
                            G_temp.add_node(nodo)
                            for e in enemigos:
                                G_temp.add_edge(nodo, e)
                        
                        conflictos = []
                        for u, v in G_temp.edges():
                            if st.session_state.resultados.get(u) == st.session_state.resultados.get(v):
                                conflictos.append((u, v))
                        
                        st.warning(f"Materias en conflicto directo: {conflictos}")

# SECCIÓN DE AUTOR
col1, col2 = st.columns([1, 4]) # Ajusta la proporción (1 parte foto, 4 partes texto)

with col1:
    # Puedes usar una URL de imagen o un archivo local 'foto.jpg'
    st.image("https://media.licdn.com/dms/image/v2/D4D03AQGBTSyoiVHM5g/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1668142166973?e=1779321600&v=beta&t=tInWiseg_1BFcO4oPNvK8QGq09yZ_dpg2z5vl0nvpDc", width=200) 

with col2:
    st.markdown("##### ANGEL SANCHEZ CABRERA")
    st.markdown("##### PG: 9.26")
    st.markdown("##### Testimonio Sobresaliente CENEVAL")
    st.markdown("##### Licenciatura en Ciencias de la Computación-BUAP")
    st.markdown("##### 3 años 5 meses de Experiencias Profesional")
st.divider() # Línea divisoria estética

# 4. CUERPO PRINCIPAL DE LA APLICACIÓN
st.title("🎓 Sistema de asignación eficiente de horarios académicos mediante coloreo de grafos")
st.markdown("Esta plataforma modela restricciones académicas usando Teoría de Grafos para encontrar el Número Cromático (bloques mínimos de tiempo).")


# --- MÉTRICAS ---
mapa_adyacencia = st.session_state.grafo.obtener_lista_adyacencia()
num_aristas = sum(len(enemigos) for enemigos in mapa_adyacencia.values()) // 2

if 'modo_actual' not in st.session_state:
    st.session_state.modo_actual = "normal"

num_bloques = "-" if st.session_state.modo_actual == "batalla" else (max(st.session_state.resultados.values()) if st.session_state.resultados else 0)

col1, col2, col3 = st.columns(3)
col1.metric("📚 Materias (Nodos)", len(st.session_state.materias))
col2.metric("⚔️ Conflictos (Aristas)", num_aristas)
col3.metric("⏱️ Bloques Requeridos", num_bloques if num_bloques != "-" else "Modo Batalla")

st.markdown("---")

# ==========================================
# RENDERIZADO VISUAL UNIVERSAL
# ==========================================
if st.session_state.materias:
    import time
    
    # 1. CREAMOS LA ESTRUCTURA BASE UNA SOLA VEZ
    G = nx.Graph()
    for nodo, enemigos in mapa_adyacencia.items():
        G.add_node(nodo)
        for e in enemigos:
            G.add_edge(nodo, e)
            
    if 'posiciones' not in st.session_state or len(st.session_state.posiciones) != len(G.nodes):
        st.session_state.posiciones = nx.spring_layout(G, seed=42)
    pos = st.session_state.posiciones

    # 2. FUNCIÓN MAESTRA CREADORA DE FOTOGRAMAS
    def generar_fotograma_universal(resultados, orden_coloreo, paso_limite):
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines')

        node_x, node_y, node_color, node_text = [], [], [], []
        PALETA = ['#CCCCCC', '#1F4564', '#FF9225', '#00B1DF', '#F1C40F', '#BEEDFC', '#AF7AC5', '#58D68D', '#ebf3a0', '#d2bead', '#CD6155']
        
        for nodo in G.nodes():
            x, y = pos[nodo]
            node_x.append(x)
            node_y.append(y)
            
            if resultados and nodo in orden_coloreo[:paso_limite]:
                bloque = resultados[nodo]
                color = PALETA[bloque % len(PALETA)]
                info_horario = f"<br><b>Bloque Asignado: {bloque}</b>"
            else:
                color = PALETA[0]
                info_horario = "<br><i>Buscando horario...</i>"
                
            node_color.append(color)
            mat_info = st.session_state.materias[nodo]
            node_text.append(f"<b>Materia {nodo}: {mat_info.materia}</b><br>Grupo: {mat_info.grupo}<br>Docente: {mat_info.docente}{info_horario}")

        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text', hoverinfo='text', 
            text=[str(n) for n in G.nodes()], textposition="middle center", hovertext=node_text,
            marker=dict(showscale=False, color=node_color, size=45, line_width=2, line_color='white'))

        fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), plot_bgcolor='rgba(0,0,0,0)'))
        return fig

    # ----------------------------------------
    # VISTA A: MODO BATALLA ANIMADO
    # ----------------------------------------
    if st.session_state.modo_actual == "batalla" and 'res_A' in st.session_state:
        st.markdown("### ⚔️ Batalla Algorítmica: Paso a Paso")
        
        orden_A = list(st.session_state.res_A.keys())
        orden_B = list(st.session_state.res_B.keys())
        max_pasos = len(st.session_state.materias)

        col_slider, col_play = st.columns([4, 1])
        with col_slider:
            paso_batalla = st.slider("Desliza para ver la competencia:", 0, max_pasos, max_pasos, key="slider_batalla")
        with col_play:
            st.write("")
            st.write("")
            btn_animar_batalla = st.button("▶️ Batalla Automática", type="primary", use_container_width=True)

        # ¡AQUÍ ESTÁ LA MAGIA DE LOS TAMAÑOS!
        # Cámbialo a [2, 1] si quieres la Izquierda más grande, o a [1, 2] si quieres la Derecha más grande.
        pantalla_izq, pantalla_der = st.columns([1, 1]) 
        
        with pantalla_izq:
            st.subheader(f"🛡️ {st.session_state.nombre_A}")
            st.metric("Bloques Usados", max(st.session_state.res_A.values()) if st.session_state.res_A else 0)
            marco_izq = st.empty() # Televisor izquierdo
            
        with pantalla_der:
            st.subheader(f"⚔️ {st.session_state.nombre_B}")
            st.metric("Bloques Usados", max(st.session_state.res_B.values()) if st.session_state.res_B else 0)
            marco_der = st.empty() # Televisor derecho

        if btn_animar_batalla:
            for fotograma in range(1, max_pasos + 1):
                # Le agregamos una "key" única a cada fotograma para que Streamlit no se confunda
                marco_izq.plotly_chart(generar_fotograma_universal(st.session_state.res_A, orden_A, fotograma), 
                                    use_container_width=True, key=f"anim_izq_{fotograma}")
                
                marco_der.plotly_chart(generar_fotograma_universal(st.session_state.res_B, orden_B, fotograma), 
                                    use_container_width=True, key=f"anim_der_{fotograma}")
                time.sleep(0.8)
        else:
            # También le ponemos llaves al estado estático
            marco_izq.plotly_chart(generar_fotograma_universal(st.session_state.res_A, orden_A, paso_batalla), 
                                use_container_width=True, key="estatico_izq")
            
            marco_der.plotly_chart(generar_fotograma_universal(st.session_state.res_B, orden_B, paso_batalla), 
                                use_container_width=True, key="estatico_der")

    # ----------------------------------------
    # VISTA B: MODO NORMAL ANIMADO
    # ----------------------------------------
    else:
        if st.session_state.resultados:
            st.markdown("### 🎬 Reproductor del Algoritmo")
            col_slider, col_play = st.columns([4, 1])
            with col_slider:
                paso_manual = st.slider("Desliza manualmente o presiona Auto-Play:", 
                                        0, len(st.session_state.orden_coloreo), len(st.session_state.orden_coloreo))
            with col_play:
                st.write("")
                st.write("")
                btn_animar = st.button("▶️ Auto-Play", type="primary", use_container_width=True)

            pantalla_grafo = st.empty()

            if btn_animar:
                for fotograma in range(1, len(st.session_state.orden_coloreo) + 1):
                    pantalla_grafo.plotly_chart(generar_fotograma_universal(st.session_state.resultados, st.session_state.orden_coloreo, fotograma), use_container_width=True)
                    time.sleep(0.8)
            else:
                pantalla_grafo.plotly_chart(generar_fotograma_universal(st.session_state.resultados, st.session_state.orden_coloreo, paso_manual), use_container_width=True)
        else:
            st.plotly_chart(generar_fotograma_universal({}, [], 0), use_container_width=True)

else:
    st.info("👈 Utiliza el Panel de Control para agregar materias o cargar la Tabla 1 y generar el grafo.")