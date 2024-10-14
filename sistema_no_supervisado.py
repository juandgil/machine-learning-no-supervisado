import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from fuzzywuzzy import process  # Para comparar cadenas
from colorama import Fore, Style  # Importar colorama

# Inicializar colorama
from colorama import init
init(autoreset=True)  # Para que los colores se reinicien automáticamente

# Cargar los datos desde un archivo CSV
data = pd.read_csv('datos_transporte_no_supervisado.csv')

# Preprocesamiento de datos
# Convertir las variables categóricas a numéricas
data['tráfico'] = data['Tráfico'].map({'Bajo': 0, 'Moderado': 1, 'Alto': 2})
data['clima'] = data['Clima'].map({'Soleado': 0, 'Nublado': 1, 'Lluvia': 2})

# Variables para clustering
X = data[['Área (km²)', 'tráfico', 'clima']]  # Seleccionar las características para el clustering

# Crear el modelo de KMeans
modelo = KMeans(n_clusters=3, random_state=42)  # Definir el número de clusters
modelo.fit(X)  # Entrenar el modelo

# Predecir los clusters
data['cluster'] = modelo.predict(X)  # Asignar el cluster a cada dato

# Visualizar los clusters
plt.figure(figsize=(10, 6))
plt.scatter(data['Área (km²)'], data['tráfico'], c=data['cluster'], cmap='viridis', marker='o')
plt.xlabel('Área (km²)')
plt.ylabel('Tráfico (0: Bajo, 1: Moderado, 2: Alto)')
plt.title('Clusters de Municipios')
plt.colorbar(label='Cluster')
plt.grid()
plt.show()

# Mostrar los datos con sus clusters
print(data[['Municipio', 'Área (km²)', 'Tráfico', 'Clima', 'Temperatura (°C)', 'Altitud (m)', 'cluster']])

# Función para sugerir el municipio más cercano
def sugerir_municipio(municipio):
    municipios = data['Municipio'].tolist()  # Obtener la lista de municipios
    mejor_coincidencia = process.extractOne(municipio, municipios)  # Encontrar la mejor coincidencia
    return mejor_coincidencia[0] if mejor_coincidencia[1] >= 70 else None  # Retornar la coincidencia si es suficientemente alta

# Función para calcular las características promedio de un cluster
def caracteristicas_promedio(cluster):
    cluster_data = data[data['cluster'] == cluster]
    if not cluster_data.empty:
        promedio_area = cluster_data['Área (km²)'].mean()
        promedio_trafico = cluster_data['Tráfico'].mode()[0]  # Usar la moda para el tráfico
        promedio_clima = cluster_data['Clima'].mode()[0]  # Usar la moda para el clima
        promedio_temperatura = cluster_data['Temperatura (°C)'].mean()  # Media de temperatura
        promedio_altitud = cluster_data['Altitud (m)'].mean()  # Media de altitud
        print(Fore.CYAN + f"Características promedio del cluster {cluster}:")
        print(f"Área promedio: {promedio_area:.2f} km²")
        print(f"Tráfico promedio: {promedio_trafico}")
        print(f"Clima promedio: {promedio_clima}")
        print(f"Temperatura promedio: {promedio_temperatura:.2f} °C")
        print(f"Altitud promedio: {promedio_altitud:.2f} m")
    else:
        print(Fore.RED + f"No hay datos en el cluster {cluster}.")

# Función para mostrar municipios similares
def municipios_similares(municipio):
    municipio_data = data[data['Municipio'].str.lower() == municipio.lower()]
    if not municipio_data.empty:
        cluster_predicho = municipio_data['cluster'].values[0]
        municipios_en_cluster = data[data['cluster'] == cluster_predicho]
        print(Fore.GREEN + f"Municipios similares a '{municipio}' en el cluster {cluster_predicho}:")
        print(municipios_en_cluster[['Municipio', 'Área (km²)', 'Tráfico', 'Clima', 'Temperatura (°C)', 'Altitud (m)']])
    else:
        sugerencia = sugerir_municipio(municipio)
        if sugerencia:
            print(Fore.YELLOW + f"Asumo que quieres decir '{sugerencia}'.")
            municipios_similares(sugerencia)  # Llamar recursivamente con la sugerencia
        else:
            print(Fore.RED + f"El municipio '{municipio}' no se encuentra en los datos.")

# Función para hacer preguntas al sistema no supervisado
def preguntar_sistema():
    while True:
        entrada = input(Fore.CYAN + "Ingrese el nombre del municipio, el número del cluster o 'salir' para terminar: ").strip()
        
        if entrada.lower() == 'salir':
            break
        
        # Intentar convertir la entrada a un número
        try:
            cluster_input = int(entrada)
            preguntar_cluster(cluster_input)
        except ValueError:
            # Si no se puede convertir a número, tratarlo como un municipio
            preguntar_municipio(entrada)

def preguntar_cluster(cluster):
    # Mostrar los municipios en un cluster específico
    municipios_en_cluster = data[data['cluster'] == cluster]
    if not municipios_en_cluster.empty:
        print(f"Los municipios en el cluster {cluster} son:")
        print(municipios_en_cluster[['Municipio', 'Área (km²)', 'Tráfico', 'Clima', 'Temperatura (°C)', 'Altitud (m)']])
        caracteristicas_promedio(cluster)  # Mostrar características promedio
    else:
        print(Fore.RED + f"No hay municipios en el cluster {cluster}.")

def preguntar_municipio(municipio):
    # Preguntar a qué cluster pertenece un municipio específico
    municipio_data = data[data['Municipio'].str.lower() == municipio.lower()]
    if not municipio_data.empty:
        cluster_predicho = municipio_data['cluster'].values[0]
        print(Fore.GREEN + f"El municipio '{municipio}' pertenece al cluster {cluster_predicho}.")
        municipios_similares(municipio)  # Mostrar municipios similares
    else:
        sugerencia = sugerir_municipio(municipio)
        if sugerencia:
            print(Fore.YELLOW + f"Asumo que quieres decir '{sugerencia}'.")
            # Asumir que la sugerencia es correcta
            municipio = sugerencia
            municipio_data = data[data['Municipio'].str.lower() == municipio.lower()]
            cluster_predicho = municipio_data['cluster'].values[0]
            print(Fore.GREEN + f"El municipio '{municipio}' pertenece al cluster {cluster_predicho}.")
            municipios_similares(municipio)  # Mostrar municipios similares
        else:
            print(Fore.RED + f"El municipio '{municipio}' no se encuentra en los datos.")

# uso de la función
if __name__ == "__main__":
    preguntar_sistema()
