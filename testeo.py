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

print(fenotipoSegunAlelos("CYP2D6", "*1", "*4"))


