import pandas as pd
import streamlit as st
from fpdf import FPDF

from datetime import datetime
import io
import os
import base64
import openpyxl

'''

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Análisis de Alelos",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para diseño atractivo
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.4rem;
        color: #2E86AB;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.5rem;
    }
    .patient-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .result-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 10px 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .upload-box {
        border: 2px dashed #2E86AB;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


class PDFReport(FPDF):
    def header(self):
        # Logo o título del header
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'INFORME DE ANÁLISIS GENÉTICO', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    
    def add_patient_section(self, paciente_data):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'DATOS DEL PACIENTE', 0, 1)
        self.ln(5)
        
        self.set_font('Arial', '', 12)
        info_lines = [
            f"Nombre: {paciente_data['nombre']}",
            f"Edad: {paciente_data['edad']} años",
            f"Sexo: {paciente_data['sexo']}",
            f"ID Paciente: {paciente_data['id_paciente']}",
            f"Médico: {paciente_data['medico']}",
            f"Fecha de Nacimiento: {paciente_data['fecha_nacimiento']}"
        ]
        
        for line in info_lines:
            self.cell(0, 8, line, 0, 1)
        
        self.ln(10)
    
    def add_alleles_section(self, alelos_df):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'RESULTADOS DE ALELOS', 0, 1)
        self.ln(5)
        
        if alelos_df is not None and not alelos_df.empty:
            # Preparar datos para la tabla
            columns = alelos_df.columns.tolist()
            data = [columns] + alelos_df.values.tolist()
            
            # Configurar tabla
            col_widths = [40] * len(columns)  # Ajustar según necesidad
            
            self.set_font('Arial', 'B', 10)
            for i, column in enumerate(columns):
                self.cell(col_widths[i], 10, str(column), 1, 0, 'C')
            self.ln()
            
            self.set_font('Arial', '', 9)
            for row in alelos_df.values:
                for item in row:
                    self.cell(col_widths[0], 10, str(item), 1, 0, 'C')
                self.ln()
        else:
            self.set_font('Arial', 'I', 12)
            self.cell(0, 10, 'No hay datos de alelos disponibles', 0, 1)
        
        self.ln(10)
    
    def add_interpretation(self, interpretacion):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'INTERPRETACIÓN', 0, 1)
        self.ln(5)
        
        self.set_font('Arial', '', 11)
        # Manejar texto largo con multi_cell
        self.multi_cell(0, 8, interpretacion)
        self.ln(10)

def create_pdf(paciente_data, alelos_df, interpretacion):
    pdf = PDFReport()
    pdf.add_page()
    
    # Agregar secciones
    pdf.add_patient_section(paciente_data)
    pdf.add_alleles_section(alelos_df)
    pdf.add_interpretation(interpretacion)
    
    return pdf

'''

def lectura_csv(path):
    # Lectura del archivo csv con los datos de cada paciente.
    df = pd.read_csv("Genotype Matrix.csv", sep=';')
    # Los datos se pasan a un diccionario
    datos_dict = {df["Sample/Assay"][i]: {df.columns[j]: df[df.columns[j]][i] for j in range(1, len(df.columns))} for i in range(len(df))}
    # Tabla con las variantes y sus mutaciones asociadas
    tabla = {"CYP2D6": {"3": ["_"], "4": ["T"], "6": [ "_"], "7": ["G"],
                    "8": ["A"], "9": ["_"], "10*4": ["A"], "10": ["G"],
                    "12": ["T"], "14": ["T"], "15": ["_"], "17": ["A"],
                    "19": ["_"], "29": ["A"], "41": ["T"], "56B": ["A"],
                    "59": ["T"]},
         "UGT1A1": {"80": ["T"]},
         "DPYD": {"2A": [ "G","T" ], "13": ["C", "T"], "HapB3": ["T"], "D949V": ["A"]}}

    dict_pacientes = {}


    for i in datos_dict:
        dict_pacientes[i] = {}
        for j in datos_dict[i]:
            # Separacion de nombre de gen y variantes
            if "*" in j:
                separador = "*"
            elif "_" in j:
                separador = "_"
            snp = j.split(separador, 1)


            if snp[0] not in dict_pacientes[i]:
                dict_pacientes[i][snp[0]] = []

            # Manejo de Indeterminados
            if datos_dict[i][j] == "UND":
                dict_pacientes[i][snp[0]].append(("*1", "*1"))
                continue
            # Determinar genotipo 
            variante = []
            if datos_dict[i][j].split("/")[0] in tabla[snp[0]][snp[1]]:
                variante.append(f"{separador}{snp[1]}")
            else:
                variante.append(f"*1")

            if datos_dict[i][j].split("/")[1] in tabla[snp[0]][snp[1]]:
                variante.append(f"{separador}{snp[1]}")
            else:
                variante.append(f"*1")

            dict_pacientes[i][snp[0]].append(tuple(variante))

    # Eliminar duplicados
    for i in dict_pacientes:
        for j in dict_pacientes[i]:
            dict_pacientes[i][j] = list(set(dict_pacientes[i][j]))

    return dict_pacientes

def determinar_genotipo_definitivo(datos_pacientes):
    """
    Determina el genotipo definitivo para cada gen de cada paciente
    """
    resultados = {}
    
    for paciente, genes in datos_pacientes.items():
        resultados[paciente] = {}
        
        for gen, alelos in genes.items():
            # Recoger todos los alelos únicos, excluyendo *1 cuando hay otros
            alelos_maternos_unicos = set()
            alelos_paternos_unicos = set()

            for alelo_materno, alelo_paterno in alelos:
                # Si ambos son *1, es el caso base (sin mutaciones)
                if alelo_materno == '*1' and alelo_paterno == '*1':
                    continue
                
                # Añadir alelos no silvestres
                
                if alelo_materno != '*1':
                    alelos_maternos_unicos.add(alelo_materno)
                if alelo_paterno != '*1':
                    alelos_paternos_unicos.add(alelo_paterno)

            if gen == "CYP2D6":
                # Manejo de Variante *10*4 Materno
                if "*10*4" in alelos_maternos_unicos and "*10" in alelos_maternos_unicos:
                    alelos_maternos_unicos.remove("*10*4")
                    if "*4" in alelos_maternos_unicos:
                        alelos_maternos_unicos.remove("*10")
                # Manejo de Variante *10*4 Paterno 
                if "*10*4" in alelos_paternos_unicos and "*10" in alelos_paternos_unicos:
                    alelos_paternos_unicos.remove("*10*4")
                    if "*4" in alelos_paternos_unicos:
                        alelos_paternos_unicos.remove("*10")
                #Manejo si estan en alelos distintos
                if "*10*4" in alelos_paternos_unicos and "*10" in alelos_maternos_unicos:
                    alelos_paternos_unicos.remove("*10*4")
                    if "*4" in alelos_maternos_unicos:
                        alelos_maternos_unicos.remove("*10")
                if "*10*4" in alelos_maternos_unicos and "*10" in alelos_paternos_unicos:
                    alelos_maternos_unicos.remove("*10*4")
                    if "*4" in alelos_paternos_unicos:
                        alelos_paternos_unicos.remove("*10")


            # Manejo de variante *80 como *28
            if gen == "UGT1A1":
                if alelos_maternos_unicos:
                    alelos_maternos_unicos = list(alelos_maternos_unicos)
                    alelos_maternos_unicos[0] = "*28"
                    alelos_maternos_unicos = set(alelos_maternos_unicos)
                if alelos_paternos_unicos:
                    alelos_paternos_unicos = list(alelos_paternos_unicos)
                    alelos_paternos_unicos[0] = "*28"
                    alelos_paternos_unicos = set(alelos_paternos_unicos)

            # Si no hay mutaciones, el genotipo es *1/*1
            if not alelos_maternos_unicos and not alelos_paternos_unicos:
                resultados[paciente][gen] = ('*1', '*1')
            # Si hay una mutación, es heterocigoto *1/mutación
            elif alelos_maternos_unicos and not alelos_paternos_unicos:
                mutacion = list(alelos_maternos_unicos)[0]
                resultados[paciente][gen] = ('*1', mutacion)
            # Si hay dos mutaciones, es heterocigoto mutación1/mutación2
            elif not alelos_maternos_unicos and alelos_paternos_unicos:
                mutacion = list(alelos_paternos_unicos)[0]
                resultados[paciente][gen] = ('*1', mutacion)
            elif alelos_maternos_unicos and alelos_paternos_unicos:

                mutacion_materna = list(alelos_maternos_unicos)[0]
                mutacion_paterna = list(alelos_paternos_unicos)[0]
                resultados[paciente][gen] = (mutacion_materna, mutacion_paterna)

    return resultados

# Función para formatear el resultado como string
def formatear_genotipos(resultados):
    formateados = {}
    for paciente, genes in resultados.items():
        formateados[paciente] = {}
        for gen, alelos in genes.items():
            formateados[paciente][gen] = f"{alelos[0]}/{alelos[1]}"
    return formateados


# Procesar
dict_pacientes = lectura_csv("Genotype Matrix.csv")
resultados = determinar_genotipo_definitivo(dict_pacientes)
resultados_formateados = formatear_genotipos(resultados)

#print(resultados_formateados)


df = pd.read_excel("CYP2D6_Diplotype_Phenotype_Table.xlsx")
diccionario_CYP2D6 = dict(zip(df.iloc[:, 0], zip(df.iloc[:, 1], df.iloc[:, 2])))
def fenotipo(genotipo):
    Sol = {}
    diccionario = genotipo
    for nombre in diccionario:
        Sol[nombre] = {}
        for gen in diccionario[nombre]:
            alelos = diccionario[nombre][gen].split('/')   
            if gen == 'DPYD' or gen == 'UGT1A1':
                if alelos[0] == "*1" and alelos[1] == "*1":       
                    Sol[nombre][gen] = [f"{alelos[0]}/{alelos[1]}", 1.0, 'Normal Metabolizer']
                elif alelos[0] != "*1" and alelos[1] != "*1":
                    Sol[nombre][gen] = [f"{alelos[0]}/{alelos[1]}", 0.0, 'Poor Metabolizer']
                else:
                    Sol[nombre][gen] = [f"{alelos[0]}/{alelos[1]}", 0.5,'Intermediate Metabolizer']
            else:
                Sol[nombre][gen] = [diccionario[nombre][gen]]
                Sol[nombre][gen].append(diccionario_CYP2D6[diccionario[nombre][gen]][0])
                Sol[nombre][gen].append(diccionario_CYP2D6[diccionario[nombre][gen]][1])
    return Sol

fenotipo_test = fenotipo(resultados_formateados)
print(fenotipo_test)


def recomendacionClinica(fenotipo):
    import json # Importa la biblioteca JSON para trabajar con datos JSON.
    import requests # Importa la biblioteca Requests para realizar solicitudes HTTP.
    resultado = fenotipo # Inicializa una lista vacía para almacenar los resultados.
    for paciente in fenotipo:
        for gen in fenotipo[paciente]:
            if gen == "CYP2D6":
                lookupkey= [gen, fenotipo[paciente][gen][1]] # Obtiene la clave de búsqueda del fenotipo.
                ID_Farmaco = "RxNorm:10324"
                url='https://api.cpicpgx.org/v1/recommendation?select=drug(name),guideline(name),*&drugid=eq.'+ID_Farmaco+'&lookupkey=cs.{\"'+lookupkey[0]+'":"'+lookupkey[1]+'"}' 
            elif gen == "DPYD":
                
                lookupkey= [gen, fenotipo[paciente][gen][2]] # Obtiene la clave de búsqueda del fenotipo.
                ID_Farmaco = "RxNorm:4492"
                url='https://api.cpicpgx.org/v1/recommendation?select=drug(name),guideline(name),*&drugid=eq.'+ID_Farmaco+'&lookupkey=cs.{\"'+lookupkey[0]+'":"'+lookupkey[1]+'"}' 
            elif gen == "UGT1A1":
                lookupkey= [gen, fenotipo[paciente][gen][2]] # Obtiene la clave de búsqueda del fenotipo.
                ID_Farmaco = "RxNorm:51499"
                url='https://api.cpicpgx.org/v1/recommendation?select=drug(name),guideline(name),*&drugid=eq.'+ID_Farmaco+'&lookupkey=cs.{\"'+lookupkey[0]+'":"'+lookupkey[1]+'"}' 
            response = requests.get(url) # Realiza una solicitud GET a la API.
            json_obtenido = response.json() # Convierte la respuesta JSON en un objeto Python.
            datos=json_obtenido # Asigna los datos JSON a la variable 'datos'.
            if len(datos) != 0: # Verifica si se encontraron recomendaciones.
                #print(datos)
                resultado[paciente][gen].append(datos[0]['drugrecommendation'].encode('latin-1','ignore').decode('latin-1')) # Agrega la recomendación del fármaco a la lista, decodificando caracteres especiales.
    return resultado # Devuelve la lista con los resultados.

#resultado_final = recomendacionClinica(fenotipo_test)



'''
def main():
    # Header principal
    st.markdown('<div class="main-header">🧬 SISTEMA DE ANÁLISIS DE ALELOS</div>', unsafe_allow_html=True)
    
    # Sidebar para navegación
    with st.sidebar:
        st.markdown("### 📊 Navegación")
        page = st.radio("Selecciona una sección:", 
                       ["📝 Datos del Paciente", "📤 Cargar Alelos", "📄 Generar Reporte"])
        
        st.markdown("---")
        st.markdown("### 💡 Información")
        st.info("""
        Esta aplicación permite:
        - Cargar datos de pacientes
        - Subir archivos CSV con alelos
        - Generar reportes en PDF
        """)
    
    # Inicializar session state
    if 'paciente_data' not in st.session_state:
        st.session_state.paciente_data = None
    if 'alelos_df' not in st.session_state:
        st.session_state.alelos_df = None
    
    # Sección 1: Datos del Paciente
    if page == "📝 Datos del Paciente":
        st.markdown('<div class="sub-header">📝 INFORMACIÓN DEL PACIENTE</div>', unsafe_allow_html=True)
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre completo *", placeholder="Ej: Juan Pérez García")
                edad = st.number_input("Edad *", min_value=0, max_value=120, value=30)
                sexo = st.selectbox("Sexo *", ["Masculino", "Femenino", "Otro"])
            
            with col2:
                id_paciente = st.text_input("ID del Paciente *", placeholder="Ej: PAC-001")
                medico = st.text_input("Médico solicitante *", placeholder="Ej: Dr. Ana López")
                fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=datetime(1990, 1, 1))
            
            # Información adicional
            st.markdown("### Información Adicional")
            col3, col4 = st.columns(2)
            with col3:
                telefono = st.text_input("Teléfono", placeholder="+34 600 000 000")
                email = st.text_input("Email", placeholder="paciente@email.com")
            with col4:
                direccion = st.text_area("Dirección", placeholder="Calle...")
                observaciones = st.text_area("Observaciones clínicas")
            
            submitted = st.form_submit_button("💾 Guardar Datos del Paciente")
            
            if submitted:
                if nombre and edad and sexo and id_paciente and medico:
                    st.session_state.paciente_data = {
                        'nombre': nombre,
                        'edad': edad,
                        'sexo': sexo,
                        'id_paciente': id_paciente,
                        'medico': medico,
                        'fecha_nacimiento': fecha_nacimiento.strftime("%d/%m/%Y"),
                        'telefono': telefono,
                        'email': email,
                        'direccion': direccion,
                        'observaciones': observaciones
                    }
                    st.success("✅ Datos del paciente guardados correctamente!")
                else:
                    st.error("❌ Por favor, completa todos los campos obligatorios (*)")
    
    # Sección 2: Cargar Alelos
    elif page == "📤 Cargar Alelos":
        st.markdown('<div class="sub-header">📤 CARGA DE ARCHIVOS CSV</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Sube tu archivo CSV con los alelos", type=['csv'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            try:
                # Leer el archivo CSV
                df = pd.read_csv(uploaded_file)
                st.session_state.alelos_df = df
                
                st.success(f"✅ Archivo cargado correctamente! ({len(df)} registros)")
                
                # Mostrar preview
                st.markdown("### 📋 Vista previa de los datos:")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Estadísticas básicas
                st.markdown("### 📊 Estadísticas del archivo:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Registros", len(df))
                with col2:
                    st.metric("Columnas", len(df.columns))
                with col3:
                    st.metric("Tamaño", f"{uploaded_file.size / 1024:.1f} KB")
                    
            except Exception as e:
                st.error(f"❌ Error al cargar el archivo: {str(e)}")
        
        # Ejemplo de formato esperado
        with st.expander("📝 ¿Qué formato debe tener el CSV?"):
            st.markdown("""
            **Ejemplo de estructura esperada:**
            ```
            gen,alelo1,alelo2,frecuencia,interpretacion
            HLA-A,01:01,02:01,0.15,Alta frecuencia
            HLA-B,08:01,44:02,0.08,Media frecuencia
            HLA-DRB1,03:01,04:01,0.12,Baja frecuencia
            ```
            """)
    
    # Sección 3: Generar Reporte
    elif page == "📄 Generar Reporte":
        st.markdown('<div class="sub-header">📄 GENERAR REPORTE PDF</div>', unsafe_allow_html=True)
        
        # Verificar que tenemos datos
        if st.session_state.paciente_data is None:
            st.warning("⚠️ Primero ingresa los datos del paciente en la sección '📝 Datos del Paciente'")
            return
        
        if st.session_state.alelos_df is None:
            st.warning("⚠️ Primero carga un archivo CSV en la sección '📤 Cargar Alelos'")
            return
        
        # Mostrar resumen
        st.markdown('<div class="patient-card">', unsafe_allow_html=True)
        st.markdown(f"### 👤 Paciente: {st.session_state.paciente_data['nombre']}")
        st.markdown(f"**ID:** {st.session_state.paciente_data['id_paciente']} | **Edad:** {st.session_state.paciente_data['edad']} | **Médico:** {st.session_state.paciente_data['medico']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"**📊 Datos de alelos cargados:** {len(st.session_state.alelos_df)} registros")
        
        # Interpretación personalizada
        st.markdown("### 🧪 Interpretación de Resultados")
        interpretacion = st.text_area(
            "Escribe la interpretación clínica de los resultados:",
            value="Los resultados del análisis genético muestran el perfil de alelos del paciente. "
                  "Se recomienda revisar los hallazgos en el contexto clínico particular del paciente "
                  "y considerar la correlación con la presentación sintomática.",
            height=150
        )
        
        # Generar PDF
        if st.button("🖨️ Generar Reporte PDF"):
            with st.spinner("Generando reporte PDF..."):
                try:
                    pdf = create_pdf(
                        st.session_state.paciente_data,
                        st.session_state.alelos_df,
                        interpretacion
                    )
                    
                    # Guardar PDF en bytes
                    pdf_bytes = pdf.output(dest='S').encode('latin1')
                    
                    # Crear botón de descarga
                    st.success("✅ Reporte generado correctamente!")
                    
                    st.download_button(
                        label="📥 Descargar Reporte PDF",
                        data=pdf_bytes,
                        file_name=f"reporte_{st.session_state.paciente_data['id_paciente']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                    )
                    
                    # Vista previa del PDF (opcional)
                    with st.expander("👁️ Vista previa del PDF (primeras páginas)"):
                        st.info("Nota: Esta es una representación simplificada. Descarga el PDF para ver el documento completo.")
                        st.markdown("**Contenido del reporte:**")
                        st.json({
                            "Paciente": st.session_state.paciente_data['nombre'],
                            "ID": st.session_state.paciente_data['id_paciente'],
                            "Registros de alelos": len(st.session_state.alelos_df),
                            "Fecha de generación": datetime.now().strftime("%d/%m/%Y %H:%M")
                        })
                        
                except Exception as e:
                    st.error(f"❌ Error al generar el PDF: {str(e)}")

if __name__ == "__main__":
    main()

'''

