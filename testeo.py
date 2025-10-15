def buscarAlelosGen(gen):
    import json
    import requests
    listaAlelos=[]
    url="https://api.cpicpgx.org/v1/allele?genesymbol=eq."+gen
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    for i in range(len(datos)):
        alelo=datos[i]["name"]
        listaAlelos.append(alelo)
    setAlelos=set(listaAlelos)
    ListaFiltradaAlelos=(list(setAlelos))
    ListaFiltradaAlelos.sort()
    return ListaFiltradaAlelos

def ID_CPIC_Farmaco(nombreFarmaco):
    import json
    import requests
    url="https://api.cpicpgx.org/v1/drug?name=eq."+nombreFarmaco
    response = requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    if len(datos) != 0:
        ID_Farmaco=datos[0]['drugid']
        return ID_Farmaco
    else:
        return ''

def fenotipoSegunAlelos(gen,alelo1,alelo2):
    import json
    import requests
    listaAlelos=[]
    #url="https://api.cpicpgx.org/v1/diplotype?genesymbol=eq.CYP2C19&diplotype=eq.*17/*17"
    url="https://api.cpicpgx.org/v1/diplotype?genesymbol=eq."+gen+"&diplotype=eq."+alelo1+"/"+alelo2
    response= requests.get(url)
    json_obtenido = response.json()
    datos=json_obtenido
    return datos

def recomendacionClinica(gen,alelo1,alelo2,farmaco):
    
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

print(recomendacionClinica("CYP2D6", "*4", "*10", "tamoxifen"))



