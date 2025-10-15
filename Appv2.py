#==================================================================================================================================
#IMPORTAR BIBLIOTECAS
#==================================================================================================================================
import streamlit as st # Importa la biblioteca Streamlit para crear aplicaciones web interactivas.
import pandas as pd # Importa la biblioteca Pandas para manipulación y análisis de datos.
import base64 # Importa la biblioteca Base64 para codificar y decodificar datos.
import fpdf # Importa la biblioteca FPDF, aunque luego se importa directamente desde ella.
from fpdf import FPDF # Importa la clase FPDF desde la biblioteca FPDF para crear archivos PDF.

#==================================================================================================================================
#CONFIGURACIÓN DE LA PÁGINA
#==================================================================================================================================

st.set_page_config(layout="wide", page_icon='Logo_pagina.png', page_title="PharmPrev") # Configura la página de Streamlit con un diseño ancho, un icono y un título.

st.image("Logo.png") # Muestra una imagen en la aplicación Streamlit.

left, right = st.columns([1,1], gap="large") # Divide la página en dos columnas de igual tamaño con un espacio grande entre ellas.

#==================================================================================================================================
#COLUMNA IZQUIERDA
#==================================================================================================================================

with left: # Define el contenido de la columna izquierda.
    texto = '<p></p><i><p style="font-family:Cambria; font-size: 25px;">Datos identificativos del paciente</p></i>' # Define un texto HTML para el título de la sección.
    st.write(texto,unsafe_allow_html=True) # Muestra el texto HTML en la aplicación Streamlit.

    nombre = st.text_input(label="Nombre", placeholder = "Nombre") # Crea un campo de entrada de texto para el nombre del paciente.
    apellidos = st.text_input(label="Apellidos", placeholder = "Introduzca los apellidos separados por un espacio") # Crea un campo de entrada de texto para los apellidos del paciente.
    nhi = st.text_input(label="Nº Historia Clínica", placeholder = "Nº Historia Clínica") # Crea un campo de entrada de texto para el número de historia clínica del paciente.
    sexo = st.selectbox("Sexo",['-','Hombre','Mujer','Otro']) # Crea un menú desplegable para seleccionar el sexo del paciente.
    fecha_n = st.text_input(label="Fecha de nacimiento", placeholder = "(dd/mm/yyyy)") # Crea un campo de entrada de texto para la fecha de nacimiento del paciente.

#==================================================================================================================================
#COLUMNA DERECHA
#==================================================================================================================================

with right: # Define el contenido de la columna derecha.
    texto = '<p></p><i><p style="font-family:Cambria; font-size: 25px;">Datos patológicos</p></i>' # Define un texto HTML para el título de la sección.
    st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.

    enfermedad = st.text_input(label="Enfermedad actual", placeholder = "Escriba la principal patología del paciente") # Crea un campo de entrada de texto para la enfermedad actual del paciente.
    otras_e = st.text_input(label="Otras patologías", placeholder = "Introduzca las patologías separadas por comas") # Crea un campo de entrada de texto para otras patologías del paciente.

    texto = '<p></p><i><p style="font-family:Cambria; font-size: 25px;">Datos tratamiento</p></i>' # Define un texto HTML para el título de la sección.
    st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.
    tratamiento = st.text_input(label="Tratamiento", placeholder = "Introduzca los fármacos separados por comas") # Crea un campo de entrada de texto para el tratamiento del paciente.
    farmacos = tratamiento.split(',') # Divide la cadena de tratamiento en una lista de fármacos.
    farmacos = [i.strip().lower() for i in farmacos] # Elimina los espacios en blanco y convierte a minúsculas cada fármaco en la lista.

#==================================================================================================================================
#PARTE INFERIOR
#==================================================================================================================================

#DEFINICIÓN DE FUNCIONES
#_________________________________________________________________________________________________________________________________

def buscarAlelosGen(gen):
    """
    Busca los alelos de un gen específico utilizando la API CPIC.

    Args:
        gen (str): El símbolo del gen a buscar.

    Returns:
        list: Una lista ordenada de alelos únicos para el gen especificado.
    """
    import json # Importa la biblioteca JSON para trabajar con datos JSON.
    import requests # Importa la biblioteca Requests para realizar solicitudes HTTP.
    listaAlelos=[] # Inicializa una lista vacía para almacenar los alelos.
    url="https://api.cpicpgx.org/v1/allele?genesymbol=eq."+gen # Define la URL de la API CPIC para buscar alelos por símbolo de gen.
    response = requests.get(url) # Realiza una solicitud GET a la API.
    json_obtenido = response.json() # Convierte la respuesta JSON en un objeto Python.
    datos=json_obtenido # Asigna los datos JSON a la variable 'datos'.
    for i in range(len(datos)): # Itera sobre los datos para extraer los alelos.
        alelo=datos[i]["name"] # Obtiene el nombre del alelo.
        listaAlelos.append(alelo) # Agrega el alelo a la lista.
    setAlelos=set(listaAlelos) # Convierte la lista de alelos en un conjunto para eliminar duplicados.
    ListaFiltradaAlelos=(list(setAlelos)) # Convierte el conjunto de alelos en una lista.
    ListaFiltradaAlelos.sort() # Ordena la lista de alelos.
    return ListaFiltradaAlelos # Devuelve la lista filtrada y ordenada de alelos.

def ID_CPIC_Farmaco(nombreFarmaco):
    """
    Obtiene el ID de un fármaco en la base de datos CPIC.

    Args:
        nombreFarmaco (str): El nombre del fármaco a buscar.

    Returns:
        str: El ID del fármaco en CPIC, o una cadena vacía si no se encuentra.
    """
    import json # Importa la biblioteca JSON para trabajar con datos JSON.
    import requests # Importa la biblioteca Requests para realizar solicitudes HTTP.
    url="https://api.cpicpgx.org/v1/drug?name=eq."+nombreFarmaco # Define la URL de la API CPIC para buscar fármacos por nombre.
    response = requests.get(url) # Realiza una solicitud GET a la API.
    json_obtenido = response.json() # Convierte la respuesta JSON en un objeto Python.
    datos=json_obtenido # Asigna los datos JSON a la variable 'datos'.
    if len(datos) != 0: # Verifica si se encontraron datos.
        ID_Farmaco=datos[0]['drugid'] # Obtiene el ID del fármaco del primer resultado.
        return ID_Farmaco # Devuelve el ID del fármaco.
    else:
        return '' # Devuelve una cadena vacía si no se encuentra el fármaco.

def fenotipoSegunAlelos(gen,alelo1,alelo2):
    """
    Determina el fenotipo basado en los alelos de un gen.

    Args:
        gen (str): El símbolo del gen.
        alelo1 (str): El primer alelo.
        alelo2 (str): El segundo alelo.

    Returns:
        dict: Un diccionario con la información del fenotipo.
    """
    import json # Importa la biblioteca JSON para trabajar con datos JSON.
    import requests # Importa la biblioteca Requests para realizar solicitudes HTTP.
    listaAlelos=[] # Inicializa una lista vacía (no utilizada en la función).
    #url="https://api.cpicpgx.org/v1/diplotype?genesymbol=eq.CYP2C19&diplotype=eq.*17/*17" # URL de ejemplo comentada.
    url="https://api.cpicpgx.org/v1/diplotype?genesymbol=eq."+gen+"&diplotype=eq."+alelo1+"/"+alelo2 # Define la URL de la API CPIC para buscar el diplotipo.
    response= requests.get(url) # Realiza una solicitud GET a la API.
    json_obtenido = response.json() # Convierte la respuesta JSON en un objeto Python.
    datos=json_obtenido # Asigna los datos JSON a la variable 'datos'.
    return datos # Devuelve los datos JSON obtenidos.

def urlGuia(farmaco,ID):
    """
    Obtiene la URL de la guía de un fármaco específico.

    Args:
        farmaco (str): El nombre del fármaco.
        ID (str): El ID de la guía.

    Returns:
        str: La URL de la guía del fármaco.
    """
    import json # Importa la biblioteca JSON para trabajar con datos JSON.
    import requests # Importa la biblioteca Requests para realizar solicitudes HTTP.
    url = 'https://api.cpicpgx.org/v1/drug?name=eq.'+farmaco+'&select=drugid,name,guideline_for_drug(*)' # Define la URL de la API CPIC para buscar información del fármaco y sus guías.
    response = requests.get(url) # Realiza una solicitud GET a la API.
    json_obtenido = response.json() # Convierte la respuesta JSON en un objeto Python.
    datos = json_obtenido # Asigna los datos JSON a la variable 'datos'.
    for i in datos: # Itera sobre los datos para encontrar la guía con el ID especificado.
        if i['guideline_for_drug']['id'] == ID: # Verifica si el ID de la guía coincide con el ID buscado.
            return i['guideline_for_drug']['url'] # Devuelve la URL de la guía.

def recomendacionClinica(gen,alelo1,alelo2,farmaco):
    """
    Obtiene la recomendación clínica basada en el gen, los alelos y el fármaco.

    Args:
        gen (str): El símbolo del gen.
        alelo1 (str): El primer alelo.
        alelo2 (str): El segundo alelo.
        farmaco (str): El nombre del fármaco.

    Returns:
        list: Una lista con el fenotipo, la recomendación clínica, el nombre de la guía y la URL de la guía.
    """
    lista = [] # Inicializa una lista vacía para almacenar los resultados.
    fenotipo = fenotipoSegunAlelos(gen,alelo1,alelo2) # Obtiene el fenotipo basado en los alelos.
    if len(fenotipo) != 0: # Verifica si se encontró un fenotipo.
        lookupkey= fenotipo[0]['lookupkey'] # Obtiene la clave de búsqueda del fenotipo.
        ID_Farmaco=ID_CPIC_Farmaco(farmaco) # Obtiene el ID del fármaco.
        import json # Importa la biblioteca JSON para trabajar con datos JSON.
        import requests # Importa la biblioteca Requests para realizar solicitudes HTTP.
        url='https://api.cpicpgx.org/v1/recommendation?select=drug(name), guideline(name), * &drugid=eq.'+ID_Farmaco+'&lookupkey=cs.{\"'+list(lookupkey.keys())[0]+'":"'+list(lookupkey.values())[0]+'"}' # Define la URL de la API CPIC para buscar recomendaciones basadas en el ID del fármaco y la clave de búsqueda.
        response = requests.get(url) # Realiza una solicitud GET a la API.
        json_obtenido = response.json() # Convierte la respuesta JSON en un objeto Python.
        datos=json_obtenido # Asigna los datos JSON a la variable 'datos'.
        if len(datos) != 0: # Verifica si se encontraron recomendaciones.
            lista.append(fenotipo[0]['generesult']) # Agrega el resultado del gen a la lista.
            lista.append(datos[0]['drugrecommendation'].encode('latin-1','ignore').decode('latin-1')) # Agrega la recomendación del fármaco a la lista, decodificando caracteres especiales.
            lista.append(datos[0]['guideline']['name']) # Agrega el nombre de la guía a la lista.
            lista.append(urlGuia(farmaco,datos[0]['guidelineid'])) # Agrega la URL de la guía a la lista.
    return lista # Devuelve la lista con los resultados.

def BuscarFarmacosRelacionadosGen(gen):
    """
    Busca fármacos relacionados con un gen específico utilizando la API PharmGKB.

    Args:
        gen (str): El símbolo del gen a buscar.

    Returns:
        list: Una lista ordenada de fármacos únicos relacionados con el gen especificado.
    """
    import json # Importa la biblioteca JSON para trabajar con datos JSON.
    import requests # Importa la biblioteca Requests para realizar solicitudes HTTP.
    listaFarmacos=[] # Inicializa una lista vacía para almacenar los fármacos.
    url="https://api.pharmgkb.org/v1/data/clinicalAnnotation?location.genes.symbol="+gen # Define la URL de la API PharmGKB para buscar anotaciones clínicas por símbolo de gen.
    response = requests.get(url) # Realiza una solicitud GET a la API.
    json_obtenido = response.json() # Convierte la respuesta JSON en un objeto Python.
    datos=json_obtenido # Asigna los datos JSON a la variable 'datos'.
    if datos['status'] == 'success': # Verifica si la solicitud a la API fue exitosa.
        for i in range(len(datos["data"])): # Itera sobre los datos para extraer los fármacos relacionados.
            farmaco=datos["data"][i]["relatedChemicals"][0]["name"] # Obtiene el nombre del fármaco relacionado.
            listaFarmacos.append(farmaco) # Agrega el fármaco a la lista.
    setFarmacos=set(listaFarmacos) # Convierte la lista de fármacos en un conjunto para eliminar duplicados.
    ListaFiltradaFarmacos=(list(setFarmacos)) # Convierte el conjunto de fármacos en una lista.
    ListaFiltradaFarmacos.sort() # Ordena la lista de fármacos.
    return ListaFiltradaFarmacos # Devuelve la lista filtrada y ordenada de fármacos.

#CÓDIGO DE STREAMLIT
#_________________________________________________________________________________________________________________________________

texto = '<p></p><i><p style="font-family:Cambria; font-size: 25px;">Datos genéticos</p></i>' # Define un texto HTML para el título de la sección.
st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.

col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,1], gap="large") # Divide la página en seis columnas de igual tamaño con un espacio grande entre ellas.

with col1: # Define el contenido de la columna 1.
    gen1 = st.text_input(label="Gen 1", placeholder = "Introduzca el gen") # Crea un campo de entrada de texto para el gen 1.
    lista1 = buscarAlelosGen(gen1) # Busca los alelos para el gen 1.
    alelo1_1 = st.selectbox("Alelo 1",['-']+lista1, key = 11) # Crea un menú desplegable para seleccionar el alelo 1 del gen 1.
    alelo1_2 = st.selectbox("Alelo 2",['-']+lista1, key = 12) # Crea un menú desplegable para seleccionar el alelo 2 del gen 1.
    
with col2: # Define el contenido de la columna 2.
    gen2 = st.text_input(label="Gen 2", placeholder = "Introduzca el gen") # Crea un campo de entrada de texto para el gen 2.
    lista2 = buscarAlelosGen(gen2) # Busca los alelos para el gen 2.
    alelo2_1 = st.selectbox("Alelo 1",['-']+lista2, key = 21) # Crea un menú desplegable para seleccionar el alelo 1 del gen 2.
    alelo2_2 = st.selectbox("Alelo 2",['-']+lista2, key = 22) # Crea un menú desplegable para seleccionar el alelo 2 del gen 2.

with col3: # Define el contenido de la columna 3.
    gen3 = st.text_input(label="Gen 3", placeholder = "Introduzca el gen") # Crea un campo de entrada de texto para el gen 3.
    lista3 = buscarAlelosGen(gen3) # Busca los alelos para el gen 3.
    alelo3_1 = st.selectbox("Alelo 1",['-']+lista3, key = 31) # Crea un menú desplegable para seleccionar el alelo 1 del gen 3.
    alelo3_2 = st.selectbox("Alelo 2",['-']+lista3, key = 32) # Crea un menú desplegable para seleccionar el alelo 2 del gen 3.
    
with col4: # Define el contenido de la columna 4.
    gen4 = st.text_input(label="Gen 4", placeholder = "Introduzca el gen") # Crea un campo de entrada de texto para el gen 4.
    lista4 = buscarAlelosGen(gen4) # Busca los alelos para el gen 4.
    alelo4_1 = st.selectbox("Alelo 1",['-']+lista4, key = 41) # Crea un menú desplegable para seleccionar el alelo 1 del gen 4.
    alelo4_2 = st.selectbox("Alelo 2",['-']+lista4, key = 42) # Crea un menú desplegable para seleccionar el alelo 2 del gen 4.
    
with col5: # Define el contenido de la columna 5.
    gen5 = st.text_input(label="Gen 5", placeholder = "Introduzca el gen") # Crea un campo de entrada de texto para el gen 5.
    lista5 = buscarAlelosGen(gen5) # Busca los alelos para el gen 5.
    alelo5_1 = st.selectbox("Alelo 1",['-']+lista5, key = 51) # Crea un menú desplegable para seleccionar el alelo 1 del gen 5.
    alelo5_2 = st.selectbox("Alelo 2",['-']+lista5, key = 52) # Crea un menú desplegable para seleccionar el alelo 2 del gen 5.
    
with col6: # Define el contenido de la columna 6.
    gen6 = st.text_input(label="Gen 6", placeholder = "Introduzca el gen") # Crea un campo de entrada de texto para el gen 6.
    lista6 = buscarAlelosGen(gen1) # Busca los alelos para el gen 6 (usa gen1 por error, debería ser gen6).
    alelo6_1 = st.selectbox("Alelo 1",['-']+lista6, key = 61) # Crea un menú desplegable para seleccionar el alelo 1 del gen 6.
    alelo6_2 = st.selectbox("Alelo 2",['-']+lista6, key = 62) # Crea un menú desplegable para seleccionar el alelo 2 del gen 6.
    
genes = [gen1,gen2,gen3,gen4,gen5,gen6] # Crea una lista con los genes introducidos.
alelos1 = [alelo1_1,alelo2_1,alelo3_1,alelo4_1,alelo5_1,alelo6_1] # Crea una lista con los alelos 1 seleccionados.
alelos2 = [alelo1_2,alelo2_2,alelo3_2,alelo4_2,alelo5_2,alelo6_2] # Crea una lista con los alelos 2 seleccionados.

#==================================================================================================================================
#OBTENCIÓN DE RESULTADOS
#==================================================================================================================================

recomendaciones = dict() # Inicializa un diccionario para almacenar las recomendaciones.
for i in farmacos: # Itera sobre la lista de fármacos.
    recomendaciones[i] = dict() # Inicializa un diccionario para cada fármaco.
    for x, y, z in zip(genes, alelos1, alelos2): # Itera sobre los genes y sus alelos.
        if y != '-' and z != '-': # Verifica si se seleccionaron ambos alelos.
            recomendaciones[i][x] = recomendacionClinica(x,y,z,i) # Obtiene la recomendación clínica para el fármaco y el gen, y la almacena en el diccionario.
            
relaciones = dict() # Inicializa un diccionario para almacenar las relaciones entre genes y fármacos.
for x,y,z in zip(genes, alelos1, alelos2): # Itera sobre los genes y sus alelos.
    if y != '-' and z != '-': # Verifica si se seleccionaron ambos alelos.
        relaciones[x] = BuscarFarmacosRelacionadosGen(x) # Busca los fármacos relacionados con el gen y los almacena en el diccionario.
#====================================================================================================================================
#EXPORTAR COMO PDF
#====================================================================================================================================

st.markdown("***") # Muestra una línea horizontal en la aplicación Streamlit.
 
export_as_pdf = st.button("Generar PDF") # Crea un botón para generar el PDF.

report_text = "Hola" # Define un texto para el informe (no utilizado).

def create_download_link(val, filename):
    """Generates a link to download the given payload as pdf with given filename.
    """
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

class PDF(FPDF):
    """
    Clase para generar el PDF del informe.
    Hereda de la clase FPDF.
    """
    def header(self):
        """
        Encabezado del PDF.
        Incluye los logos y el título del informe.
        """
        # Logo
        self.image('Logo.png', 15, 12, 70)
        self.image('HUBU.png', 92, 14, 50)
        # Arial bold 15
        self.set_font('Times', 'I', 9)
        # Move to the right
        self.set_y(self.get_y()-9)
        self.set_x(-20)
        # Title
        self.cell(w = 0, h = 0, txt = 'Informe farmacogenético', border = 0, ln = 0,  align = 'R')
        self.ln(3.5)
        self.cell(w = 0, h = 0, txt = 'Unidad de Medicina de Precisión', border = 0, ln = 0,  align = 'R')
        self.ln(3.5)
        self.cell(w = 0, h = 0, txt = 'HUBU', border = 0, ln = 0,  align = 'R')
        # Line break
        self.ln(10)

    # Page footer
    def footer(self):
        """
        Pie de página del PDF.
        Incluye el número de página.
        """
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


if export_as_pdf: # Verifica si se presionó el botón de generar PDF.
    pdf = PDF() # Crea una instancia de la clase PDF.
    pdf.alias_nb_pages() # Define un alias para el número total de páginas.
    pdf.set_margins(left = 20.0, top = 25.0, right = 20.0) # Define los márgenes del PDF.
    pdf.add_page() # Agrega una página al PDF.
    pdf.set_font('Times', 'I', 20) # Define la fuente y el tamaño de la letra.
    pdf.cell(40, 10, 'Datos personales', ln = 1) # Agrega una celda con el título "Datos personales".
    
    pdf.set_fill_color(r = 227, g = 252, b = 255) # Define el color de relleno de las celdas.
    pdf.set_draw_color(r = 0, g = 5, b = 48) # Define el color del borde de las celdas.
    
    pdf.multi_cell(w = 170, h = 30, border = 1, fill = True) # Agrega una celda múltiple con borde y relleno.
    pdf.set_font('Times', '', 12) # Define la fuente y el tamaño de la letra.
    pdf.set_y(pdf.get_y()-25) # Ajusta la posición vertical.
    pdf.cell(w = 0, txt = f'Nombre: {nombre}', align = 'L') # Agrega una celda con el nombre del paciente.
    pdf.set_x(-90) # Ajusta la posición horizontal.
    pdf.cell(w = 0, txt = f'Sexo: {sexo}', align = 'L') # Agrega una celda con el sexo del paciente.
    pdf.ln(9) # Agrega un salto de línea.
    pdf.cell(w = 0, txt = f'Apellidos: {apellidos}', align = 'L') # Agrega una celda con los apellidos del paciente.
    pdf.set_x(-90) # Ajusta la posición horizontal.
    pdf.cell(w = 0, txt = f'Fecha de nacimiento: {fecha_n}', align = 'L') # Agrega una celda con la fecha de nacimiento del paciente.
    pdf.ln(9) # Agrega un salto de línea.
    pdf.cell(w = 0, txt = f'Nº Historia Clínica: {nhi}', align = 'L', ln = 1) # Agrega una celda con el número de historia clínica del paciente.
    pdf.ln(9) # Agrega un salto de línea.
    
    pdf.set_font('Times', 'I', 20) # Define la fuente y el tamaño de la letra.
    pdf.cell(40, 10, 'Datos patológicos', ln = 1) # Agrega una celda con el título "Datos patológicos".
    pdf.set_font('Times', '', 12) # Define la fuente y el tamaño de la letra.
    pdf.multi_cell(w = 170, h = 10, txt = f'Enfermedad actual: {enfermedad}\nOtras patologías: {otras_e}\nTratamiento: {tratamiento}', border = 1, fill = True) # Agrega una celda múltiple con la información patológica del paciente.
    pdf.ln(3) # Agrega un salto de línea.
    
    pdf.set_font('Times', 'I', 20) # Define la fuente y el tamaño de la letra.
    pdf.cell(40, 10, 'Fenotipo y recomendación de dosis', ln = 1) # Agrega una celda con el título "Fenotipo y recomendación de dosis".
    texto = '' # Inicializa una cadena vacía para almacenar el texto de las recomendaciones.
    for i in recomendaciones: # Itera sobre los fármacos.
        texto += 'En relación con el fármaco ' + i + ':\n' # Agrega el nombre del fármaco al texto.       
        for x in recomendaciones[i]: # Itera sobre los genes.
            if len(recomendaciones[i][x]) == 0: # Verifica si no hay información sobre interacciones.
                texto += 'No hay información sobre interacciones con '+ x +' para esos alelos.\n' # Agrega un mensaje indicando que no hay información.
            else: # Si hay información sobre interacciones.
                texto += 'El fenotipo para '+ x +' es '+ recomendaciones[i][x][0] + '. Recomendación clínica: ' + recomendaciones[i][x][1]+' Fuente de información: '+recomendaciones[i][x][2]+' ('+recomendaciones[i][x][3]+').\n' # Agrega la información del fenotipo y la recomendación clínica al texto.
        texto += '\n' # Agrega un salto de línea.
    pdf.set_font('Times', '', 12) # Define la fuente y el tamaño de la letra.
    pdf.multi_cell(w = 170, h = 6, txt = texto, border = 1, fill = True, align = 'L') # Agrega una celda múltiple con el texto de las recomendaciones.
    pdf.ln(3) # Agrega un salto de línea.
    
    pdf.set_font('Times', 'I', 20) # Define la fuente y el tamaño de la letra.
    pdf.cell(40,10,'Interacciones con fármacos',ln=1) # Agrega una celda con el título "Interacciones con fármacos".
    texto = '' # Inicializa una cadena vacía para almacenar el texto de las interacciones.
    for i in relaciones: # Itera sobre las relaciones entre genes y fármacos.
        texto += 'Fármacos metabolizados por ' + i + ': ' + str(', '.join(relaciones[i]))+'.\n\n' # Agrega la información de las interacciones al texto.
    pdf.set_font('Times', '', 12) # Define la fuente y el tamaño de la letra.
    pdf.multi_cell(w = 170, h = 6, txt = texto, border = 1, fill = True, align = 'L') # Agrega una celda múltiple con el texto de las interacciones.
        
    
    html = create_download_link(pdf.output(dest="S").encode('latin-1'), f"Informe paciente {nhi}") # Crea un enlace para descargar el PDF.

    st.markdown(html, unsafe_allow_html=True) # Muestra el enlace de descarga en la aplicación Streamlit.
    
#==================================================================================================================================
#MOSTRAR RESULTADOS
#==================================================================================================================================   
texto = '<center><p style="font-family:Cambria; font-size: 35px;">Informe Final</p></center>' # Define un texto HTML para el título de la sección.
st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.
#--------------------------------------------------------------------------------------------------------------------------
texto = '<i><p style="font-family:Cambria; font-size: 22px;"><u>Fenotipo y recomendación de dosis</u></p></i>' # Define un texto HTML para el título de la sección.
st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.

for i in recomendaciones: # Itera sobre los fármacos.
    texto = '<p style="text-indent: 30px; font-family:Cambria; font-size: 18px;">En relación con el fármaco <b>'+i+'</b>:</p>' # Define un texto HTML para el nombre del fármaco.
    st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.          
    for x in recomendaciones[i]: # Itera sobre los genes.
        if len(recomendaciones[i][x]) == 0: # Verifica si no hay información sobre interacciones.
            texto = '<p style="text-indent: 50px; font-family:Cambria; font-size: 15px;">No hay información sobre interacciones con <b>'+x+'</b> para esos alelos.</p>' # Define un texto HTML indicando que no hay información.
            st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.
        else: # Si hay información sobre interacciones.
            texto = '<p style="text-indent: 50px; font-family:Cambria; font-size: 15px;">El fenotipo para <b>'+x+'</b> es '+recomendaciones[i][x][0]+'. Recomendación clínica: '+recomendaciones[i][x][1]+' Fuente de información: <a href="'+recomendaciones[i][x][3]+'" target= "_blank">'+recomendaciones[i][x][2]+'</a></p>' # Define un texto HTML con la información del fenotipo y la recomendación clínica.
            st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.
#--------------------------------------------------------------------------------------------------------------------------   
texto = '<i><p style="font-family:Cambria; font-size: 22px;"><u>Interacciones con otros fármacos</u></p></i>' # Define un texto HTML para el título de la sección.
st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.

for i in relaciones: # Itera sobre las relaciones entre genes y fármacos.
    texto = '<p style="text-indent: 30px; font-family:Cambria; font-size: 15px;">Fármacos metabolizados por <b>'+i+'</b>: '+str(', '.join(relaciones[i]))+'.'+'</p>' # Define un texto HTML con la información de las interacciones.
    st.write(texto,unsafe_allow_html = True) # Muestra el texto HTML en la aplicación Streamlit.