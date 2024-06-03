
<figure>
<img src='https://raw.githubusercontent.com/jmpaiba123/AB_Testing_Meli/main/data/Outputs/Images/AB_testing_Meli.png' width="850" height="400" />
<figcaption></figcaption>
</figure>


## **Ejercicio: AB Testing en MercadoLibre**
#### **Autor:** jmpaiba123

En Mercadolibre(MELI) navegan unos 80 millones de usuarios mensualmente, los cuáles generan un volumen de actividad y eventos enorme. para el desarrollo del reto accedimos a un [subset](https://raw.githubusercontent.com/jmpaiba123/AB_Testing_Meli/main/data/Inputs/Experiments%20DataSet%20For%20Excercise-small.csv) del mismo. El dataset que adjuntamos en el siguiente ejercicio, contiene porciones de la
navegación de nuestros usuarios en nuestra plataforma. 

<figure>
<img src='https://raw.githubusercontent.com/jmpaiba123/AB_Testing_Meli/main/data/Outputs/Images/dict_dataset.png' width="650" height="300" />
<figcaption></figcaption>
</figure>


El interés en dicho dataset radica en que describe las interacciones de los usuarios previo a realizar una compra (o no) en la plataforma. En el contexto de [MELI](https://medium.com/mercadolibre-tech/a-b-testing-meli-3a5ad2b4594d), se corren cientos de [AB testings](https://en.wikipedia.org/wiki/A/B_testing) para entender qué features/ideas/variantes llevan a los usuarios a comprar dentro de mercadolibre y que cosas no.

La columna experiments, tiene por objeto guardar un listado de todos los experimentos a los que fue sometido un usuario a lo largo de su navegación. Nótese que la
forma en la cual se guarda implica entries/tuplas del formato experiment_name => variant_id. Siendo estas interpretables como “al ver esta página el usuario {user_id}
participó del siguiente experimento {experiment_name}, viendo la variante {variant_id}”.


### **Solución del reto**

**Nivel 1**
Implementar una query, notebook o algoritmo que pueda leer este dataset y compute para cada experimento del dataset un número de compras asociadas de forma de poder
comparar cual de las n variantes de cada experimento fue mejor.

Para la solución  de este primer punto tenemos dentro de nuestro repositorio: 
1. **[csv_datos](https://raw.githubusercontent.com/jmpaiba123/AB_Testing_Meli/main/data/Inputs/Experiments%20DataSet%20For%20Excercise-small.csv):** archivo original con la información disponible para el desarrollo de la prueba
2. **[01_Lectura_dataset.ipynb](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/jupyter_notebooks/01_Lectura_dataset.ipynb):** notebook destinado para el dearrollo de la actividad, dentro del mismo se encuentra la documentación y desarrollo de las hipótesis destinadas al procesamiento de los datos.
3. **[utilities.py](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/python_scripts/utilities.py):** archivo .py, soporte fundamental para el desarrollo del challenge, se construyen y documentan funciones especificas para procesamiento y análisis de los datos.

**Insigths & assupmtions**

#### **1. Lectura de la información compartida y control de registros**
Control de registros de las variables disponibles, tenemos un aproximado de 150k registros o navegaciones, para el transcurso de dos días 202108 (01-02), para 7,817 clientes. Eventualmente se observa que a medida se avanza en el proceso de compra las porciones de navegación disminuyes significativamente, donde 76750 fueron eventos relacionados con la búsqueda y solamente 1,088 de compra. Imprimimos algunos de los registros de compra y búsqueda de nuestros clientes, y las primeras sesiones de navegación para un cliente cualquiera, observando que para los **event_name SEARCH o eventos de búsqueda no es posible identificar un item_id**, suceso de particular interés, puesto que para realizar seguimiento completo a la cadena de compra vamos a utilizar el item_id o artículo de interés. Validando el seguimiento de la cadena de compra de nuestro cliente **6498883** y su producto adquirido vía mercado libre **988145209**, confirmamos que :
 * eventos de **search** no tienen un ítem relacionado
 * dada la cantidad de eventos realizados durante la búsqueda, y el interés particular por determinar cual de las variantes aplicadas tuvo mayor éxito de compra, es necesario mapear o marcar cada uno de los mismos con una etiqueta positiva (1).
 
 #### **2. Marcación de experimentos y variantes exitosas en cadena de compra**

 Tomando en consideración todo lo mencionado anteriormente, y dando respuesta a la primera solicitud de nuestro ejercicio, buscaremos asignar de la manera más precisa, todos los eventos (y sus variantes correspondientes) involucrados en la cadena de cada una de las compras, tomando en consideración desde la navegación de búsqueda hasta la de compra. Acabamos de crear una variable **purchase_funnel_flag**, que nos permita asignar 1 a todas aquellas navegaciones **con información de item_id & user_id** relacionadas con la cadena de compra de algún artículo, o 0 en cualquier otro caso. Por otra parte, observando nuestro ejemplo anterior y la variable recientemente creada, la navegación de búsqueda, que posiblemente dio inicio a este proceso exitoso, no se marco positivamente, motivo por el cúal plantearemos un algoritmo adicional de identificación. Ordenaremos el dataframe por usuario y artículo de compra, encontraremos cada una de las búsquedas relacionadas con la cadena de compra (registro anterior: mismo usuario, mismo artículo, misma fecha; navegaciones del día anterior son no relacionadas) y asignaremos 1 a cada una de ellas.

 * Que hacer con cadenas de navegación interrumpidas por medía noche?

Finalmente hemos identificado positivamente las navegaciones involucradas en cada una de las cadenas de compra, inclusive las búsquedas. Del seguimiento de nuestro cliente tomado inicialmente, vemos que de sus dos compras hemos logrado identifcar toda su cadena de compra, contando las búsquedas o navegaciones señaladas a posteriori 799, son menores a la cantidad de compras iniciales 1.088, algo que nos da un parte de tranquilidad, puesto no hemos marcado búsquedas adicionales, pero **nos han faltado algúnas por etiquetar o los registros no se encontraban disponibles**. Y finalmente validamos que, después de los ajustes realizados nos mantenemos en 141.553 registros.

 #### **3. Apertura de las navegaciones, agrupaciones por experimento y variantes**

En la columna **experiments** se encuentra disponible toda la data de navegación, inicialmente crearemos diccionarios con la información allí contenida, algo que nos permite hacer mucho más fácil una apertura o explode de los experimentos, obteniendo así un registro para cada uno de los mismos. Nuevamente, nos será de gran utilidad nuestro paquete de funciones, construido en **[utilities.py](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/python_scripts/utilities.py)**




**Nivel 2**
Implementación de algunos checks correspondientes a la correctitud de los datos y a la confianza que se puede tener en los resultados, la naturaleza y selección de estos tests queda a discreción.

Para la solución  de este segundo punto tenemos dentro de nuestro repositorio: 
1. **[datos_agrupados](https://raw.githubusercontent.com/jmpaiba123/AB_Testing_Meli/main/data/Outputs/grouped_inf.csv):** archivo con información de los datos por experimento y día ya agrupados
2. **[datos_detallados_usuario](https://raw.githubusercontent.com/jmpaiba123/AB_Testing_Meli/main/data/Outputs/data_test.csv):** archivo con información similar a la anterior, en este caso por cada uno de los usuarios, bastante útil para el desarollo de inferencia estadística
3. **[02_validaciones_datos.ipynb](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/jupyter_notebooks/02_Validaciones_datos.ipynb):** notebook destinado para el dearrollo de la actividad, dentro del mismo se encuentra la documentación y desarrollo de las hipótesis destinadas al procesamiento de los datos.
4. **[utilities.py](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/python_scripts/utilities.py):** archivo .py, soporte fundamental para el desarrollo del challenge, se construyen y documentan funciones especificas para procesamiento y análisis de los datos.



**Insigths & assupmtions**

#### **Control de registros y consistencia entre dataframe detallada vs agrupada**

```python
print(df_detailed_experiments.shape)
print(df_detailed_experiments.head())
# Cantidad única de experimentos 
unique_experiments = df_detailed_experiments["experiment"].nunique()
print(f"Cantidad única de experimentos : {unique_experiments}\n")
# cantidad única de experimentos por día
experiments_per_day = df_detailed_experiments.groupby("date")["experiment"].nunique().reset_index()
print("Cantidad única de experimentos por día:")
print(experiments_per_day.to_string(index=False))
```

(154964, 7)
         date           experiment variant  user_id    path  \
0  2021-08-01  HideTransitionModal    6646   336575  mshops   
1  2021-08-01  HideTransitionModal    6646  3677574  mshops   
2  2021-08-01  HideTransitionModal    6647  2234611  mshops   
3  2021-08-01  HideTransitionModal    6647  3023131  mshops   
4  2021-08-01  HideTransitionModal    6647  9116431  mshops   

   purchase_funnel_flag  item_id  
0                     0        0  
1                     0        0  
2                     0        0  
3                     0        0  
4                     0        0  
Cantidad única de experimentos : 44

Cantidad única de experimentos por día:
      date  experiment
2021-08-01          43
2021-08-02          44


```python
print(df_grouped_experiments.shape)
print(df_grouped_experiments.head())
# Cantidad única de experimentos 
unique_experiments = df_grouped_experiments["experiment"].nunique()
print(f"Cantidad única de experimentos : {unique_experiments}\n")
# cantidad única de experimentos por día
experiments_per_day = df_grouped_experiments.groupby("date")["experiment"].nunique().reset_index()
print("Cantidad única de experimentos por día:")
print(experiments_per_day.to_string(index=False))
```

(143, 7)
         date           experiment  variant  participants  purchases  \
0  2021-08-01  HideTransitionModal     6646             2          0   
1  2021-08-01  HideTransitionModal     6647             3          0   
2  2021-08-01  HideTransitionModal     6993             5          0   
3  2021-08-01  HideTransitionModal  DEFAULT            12          0   
4  2021-08-01          address_hub     3574           189        143   

   buy_rate buy_rate_percent  
0  0.000000            0.00%  
1  0.000000            0.00%  
2  0.000000            0.00%  
3  0.000000            0.00%  
4  0.756614           75.66%  
Cantidad única de experimentos : 44

Cantidad única de experimentos por día:
      date  experiment
2021-08-01          43
2021-08-02          44

hacemos entonces un pequeño control de registros de la información con la cual vamos a trabajar, en pro de validar la correctitud de los datos y lograr mayor confianza en los resultados.

#### **validando variante DEFAULT**

En el contexto de lo revisado hasta el momento, entendemos la categoría DEFAULT como una variante que no fue exitosa al momento de generar el experimento, por lo que es necesario validar que comportamiento tiene dentro de cada uno de los experimentos planteados. se creó una función dentro nuestra librería exclusiva de nuestro proceso **utilities**, default_count, la cual nos ayudará a validar la presencia de la variante DEFAULT para cada experimento, en el caso del experimento 'seller-reputation-change', hemos encontrado de manera exitosa que no existe DEFAULT. Si embargo, es necesario validar cada uno de los 44 experimentos y tomar una la mejor decisión, en pro de realizar un ejercicio confiable.

De esta manera definimos un límite cercano al 5%, y excluiremos la información que no cumpla con lo mencionado anteriormente.


#### **Experimentos con al menos dos variantes**

Dado que la finalidad de nuestro ejercicio es llegar a validar cual de las n variantes fue mejor, seguiremos reduciendo nuestra población de estudio, considerando en este caso particular todos aquellos experimentos que tengan al menos dos variantes a comparar, la revisión para todos aquellos restantes podrá ser considerada en otro momento.

#### **Presencia de Usuarios en múltiples variantes**

Algo de igual forma importante para mantener la integridad de nuestros estudios, es garantizar que un usuario fue expueste exlusivamente a una única variante de los experimentos realizados, por ello seguiremos excluyendo información, y ahora excluiremos todos aquellos que no cumplan la condicion mencionada anteriormente


#### **Extensiones al ejercicio**

Algunas inquietudes para las cuales no se logra dar solución en este challenge, las dejaremos en consideración para futuros desarrollos.
 * como validar población e independencia entre los experimentos, para garantizar que no haya sesgos? 
 * que recomendaciones se tienen para las áreas de la empresa, para garantizar la independencia de los experimentos? 

 #### **Análisis de Resultados e Insights**

Aqui validaremos 3 experimentos de particular interés, y nos apoyaremos en analisis bayesianos, PSI, conteos discretos entre otros.

En AB testing, el enfoque bayesiano se utiliza para evaluar la efectividad relativa de diferentes variantes, como A y B. En lugar de basarse en pruebas de hipótesis clásicas, el enfoque bayesiano modela las tasas de conversión de las variantes como distribuciones de probabilidad.Se comienza con creencias previas sobre las tasas de conversión de las variantes (distribuciones a priori) y se actualizan con los datos observados durante el experimento. Esto resulta en distribuciones a posteriori que representan la probabilidad de que cada variante sea la mejor.El enfoque bayesiano proporciona una forma coherente de comparar las variantes y tomar decisiones basadas en la evidencia observada y en las creencias previas. También permite una mejor gestión de la incertidumbre y una interpretación más intuitiva de los resultados del AB testing.


El Índice de Estabilidad de Población (PSI) es una métrica utilizada en análisis estadístico para medir la estabilidad de la distribución de una población entre dos momentos temporales o entre dos muestras. El PSI evalúa la magnitud de los cambios en la distribución de la variable y proporciona una medida de la estabilidad relativa entre los dos grupos comparados. Un PSI cercano a cero indica una estabilidad alta, mientras que valores más altos indican una mayor discrepancia entre las distribuciones y, por lo tanto, una menor estabilidad. Esta métrica es especialmente útil en el análisis de experimentos A/B para evaluar la estabilidad de las características demográficas o del comportamiento de los usuarios entre diferentes variantes o períodos de tiempo.

**El tiempo no permitió trabjar en contrastes de hipótesis clásico, para validar o rechazar la hipótesis nula, la cual para este caso podría ser, asumir que las dos variantes tienen los mismas tasa de compra o resultados.**


**Nivel 3**
Implementar un API en el lenguaje de preferencia que permita consultar los resultados de un experimento para un día dado.

Para la solución  de este segundo punto tenemos dentro de nuestro repositorio: 
1. **[03_Implementacin_API.ipynb](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/jupyter_notebooks/03_Implementacion_API.ipynb):** notebook con el detalle, desarrollo e intrucciones para el lanzamiento de l API.

#### **Análisis de Resultados e Insights**

En el caso particular de la información compartida en nuestra API, es posible poner a disposición del cliente, datos relacionados con los resultados del experimento dentro del universo total


**Nivel 4**

Hostear dicha API en un proveedor cloud a elección y compartir los detalles de acceso a la misma para poder hacer consultas a dicha API hosteada.


Para la solución  de este segundo punto tenemos dentro de nuestro repositorio: 
1. **[04_lanzamiento_API_azure.ipynb](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/jupyter_notebooks/04_lanzamiento_API_azure.ipynb):** notebook con el instructivo al detalle para hostear la API en una web de azure.

Otros (archivos necesarios para hostear API): 
 * [.dockerignore](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/python_scripts/.dockerignore)
 * [Dockerfile](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/python_scripts/Dockerfile)
 * [app.py](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/python_scripts/app.py)
 * [gunicorn.conf.py](https://github.com/jmpaiba123/AB_Testing_Meli/blob/main/python_scripts/gunicorn.conf.py)