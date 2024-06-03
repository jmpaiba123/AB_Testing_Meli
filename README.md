
<figure>
<img src='https://raw.githubusercontent.com/jmpaiba123/AB_Testing_Meli/main/data/Outputs/Images/AB_testing_Meli.png' width="850" height="400" />
<figcaption></figcaption>
</figure>


## **Ejercicio: AB Testing en MercadoLibre**
#### **Autor:** jmpaiba123

En Mercadolibre(MELI) navegan unos 80 millones de usuarios mensualmente, los cuáles generan un volumen de actividad y eventos enorme. Hoy vas a poder acceder a un
subset del mismo. El dataset que adjuntamos en el siguiente ejercicio, contiene porciones de la
navegación de nuestros usuarios en nuestra plataforma. 







El interés en dicho dataset radica en que describe las interacciones de los usuarios previo a realizar una compra (o no) en la plataforma. En el contexto de [MELI](https://medium.com/mercadolibre-tech/a-b-testing-meli-3a5ad2b4594d),
se corren cientos de [AB testings](https://en.wikipedia.org/wiki/A/B_testing) para entender qué features/ideas/variantes llevan a los usuarios a comprar dentro de mercadolibre y que cosas no.

La columna experiments, tiene por objeto guardar un listado de todos los experimentos a los que fue sometido un usuario a lo largo de su navegación. Nótese que la
forma en la cual se guarda implica entries/tuplas del formato experiment_name => variant_id. Siendo estas interpretables como “al ver esta página el usuario {user_id}
participó del siguiente experimento {experiment_name}, viendo la variante {variant_id}”.

Dentro del repositorio se encuentran los siguientes archivos:

1. **AB_Desafío_MELI.ipynb:** notebook con el desarrollo de la actividad debidamente documentado incluyendo hipotesis y asunciones en el desarrollo del ejercicio.
2. **Ejercicio AB Challenge Experimentos Melidata - DS.pdf:** descripción del caso de negocio planteado.
3. **Experimentos.csv:** dataset con los datos suministrados.
4. **Insomnia - abc.png:** imagen con resultados de consultar la API para el experimento 'abc'.
5. **Insomnia - sa-on-vip.png:** imagen con resultados de consultar la API para el experimento 'sa-on-vip'.
6. **Insomnia - viewItemPageMigrationDesktopReviewsNoTabs:** imagen con resultados de consultar la API para el experimento 'viewItemPageMigrationDesktopReviewsNoTabs'.


## **Preparación del entorno**

Definimos los paquetes que vamos a utilizar


```python
# Preparamos el entorno

import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
```

Previamente hemos descargado los datos compartidos de [google drive](https://drive.google.com/file/d/1q-kVDe62HY-6SbLsetsi1s1vvYgzPUOi/view?usp=sharing) y los hemos cargado en nuestro [Github](https://github.com/JdrSosa/MELI), de tal modo que ahora importamos el dataset directamente desde nuestro repositorio:


```python
# Cargamos los datos y creamos el dataframe a utilizar

df_0 = pd.read_csv('https://raw.githubusercontent.com/JdrSosa/MELI/main/Experiments.csv',sep=",")
df_0.head()
```


```python
# Dimensiones del Dataframe
df_0.shape
```




    (141553, 6)




```python
# Cantidad de valores únicos por vaeriable
df_0.nunique()
```




    event_name          6
    item_id         45273
    timestamp      140582
    site                1
    experiments      1551
    user_id          7817
    dtype: int64




```python
# Tipos de variables
df_0.dtypes
```




    event_name      object
    item_id        float64
    timestamp       object
    site            object
    experiments     object
    user_id          int64
    dtype: object



## **Preprocesado de los datos**

Luego de observar los datos, vemos que podemos realizar algunos ajustes para trabajarlos de una forma más amigable. Inicialmente, vamos a agregar dos variables complementarias a la marca de tiempo que es de tipo "object", primero "datetime" que nos puede ayudar más adelante para ordenar la información y segundo, la variable "date" que nos puede permitir realizar agrupaciones por día.


```python
# Agregamos una variable llamada "date" que es una tranformación de la variable "timestamp" a formato fecha

df_0["datetime"] = pd.to_datetime(df_0["timestamp"], format="%Y-%m-%dT%H:%M:%S.%f%z")
df_0["date"] = pd.to_datetime(df_0["datetime"]).dt.date
df_0.head()
```





```python
# Presentamos el primer registro de la variable "experiments" para ver como esta compuesta
df_0.experiments[0]
```




    '{searchbackend/recommended-products=6157, mclics/ads-adsearch-boost-incremental-desktop-mla=3809, searchbackend/cbt-antiboost=6333, search/back-filters=5059, filters/sort-by-ranking=7057, search/best-seller-aa-testing-fail-fast-edition=4514, mclics/search-list-algorithms=5528, frontend/assetsCdnDomainMLU=DEFAULT, searchbackend/item-reputation=3824, search/remove-ecn-tag=4954, mclics/search-pads-none-desktop-mla=3478, mclics/show-pads-search-list=5146, searchbackend/seller-reputation-change=4553, cookiesConsentBanner=DEFAULT, frontend/assetsCdnDomainMLA=DEFAULT, search/best-seller-fail-fast-edition-MLA=4916, mclics/show-pads-global=5176}'



Ahora vamos a trabajar sobre la variable "experiments" donde vemos que tiene forma de tupla compuesta por experimento=variante y los diferentes experimentos a los que se sometió el usuario en ese momento estan separados por comas.

Una vez, revisado el primer registro, vamos a construir un bucle que nos permita iterar sobre cada par de elementos y construir un diccionario con los elementos de esta variable. 


```python
# Vamos a crear un diccionario a partir de la variable "experiments" donde cada $experimento=$variant_id esta separado por una coma
# Lo probamos sobre el primer registro de la variable "experiments"

cadena = df_0.experiments[0]
diccionario = {}
pares = cadena.strip("{}").split(", ")

for par in pares:
    clave, valor = par.split("=")
    diccionario[clave] = valor
    
diccionario
```




    {'searchbackend/recommended-products': '6157',
     'mclics/ads-adsearch-boost-incremental-desktop-mla': '3809',
     'searchbackend/cbt-antiboost': '6333',
     'search/back-filters': '5059',
     'filters/sort-by-ranking': '7057',
     'search/best-seller-aa-testing-fail-fast-edition': '4514',
     'mclics/search-list-algorithms': '5528',
     'frontend/assetsCdnDomainMLU': 'DEFAULT',
     'searchbackend/item-reputation': '3824',
     'search/remove-ecn-tag': '4954',
     'mclics/search-pads-none-desktop-mla': '3478',
     'mclics/show-pads-search-list': '5146',
     'searchbackend/seller-reputation-change': '4553',
     'cookiesConsentBanner': 'DEFAULT',
     'frontend/assetsCdnDomainMLA': 'DEFAULT',
     'search/best-seller-fail-fast-edition-MLA': '4916',
     'mclics/show-pads-global': '5176'}



Observamos la información del diccionario para el primer registro en forma de dataframe y vemos que este usuario en ese momento se sometió a 16 diferentes experimentos con sus correspondientes variantes:


```python
# Presentamos en forma de dataframe lo correspondiente al primer registro de la variable "experiments"

pd.DataFrame(diccionario.items(), columns=['experiment_name', 'variant_id'])
```




Una vez validado lo anterior, debemos aplicarlo a todo el dataframe, para ello, vamos a construir la función "convertir_a_diccionario", con la lógica probada previamente y luego de aplica a toda la variable "experiments":


```python
# Construimos la función "convertir_a_diccionario" a partir de lo revisado anteriormente para aplicarlo a toda la columna "experiments" del dataframe y creamos una nueva columna llamda "dict_exeriments"

def convertir_a_diccionario(cadena):
    diccionario = {}
    pares = cadena.strip("{}").split(", ")
    for par in pares:
        clave, valor = par.split("=")
        diccionario[clave] = valor
    return diccionario

df_0["dict_experiments"] = df_0["experiments"].apply(convertir_a_diccionario)
df_0.head()
```





Ahora, como se presenta en el [articulo de referencia ](https://medium.com/mercadolibre-tech/a-b-testing-meli-3a5ad2b4594d) vamos a ordenar los datos por ususario y datetime para visualizar toda su "cadena de navegación":


```python
# Ordenamos el Dataframe para ver la "cadena de navegación": lista ordenada de eventos por los que ha pasado un determinado usuario

df_0 = df_0.sort_values(['user_id','datetime', 'item_id'], ascending = [True, True, True], ignore_index=True)
df_0.head()
```






Para facilidad el tratamiento de los datos vamos a combinar lo probado anteriormente, de tal forma que convertimos "experiments" en diccionario y luego separamos dicho diccionario en dos columnas nuevas "experiment" y "variant_id" de tal modo que para cada usuario, su información se repetira tantas veces como experimentos haya tenido en cada registro:


```python
# Construimos una función que nos permite separar en dos columnas los elementos del diccionario obteniendo $experiment_name y $variant_id 
# De tal modo que para cada usuario vamos a poder ver todos los experimentos a los que fue sometido en cada evento

def dict_to_df(row):
    dictionary = row['experiments']
    pairs = dictionary.strip("{}").split(", ")
    data = {}
    for pair in pairs:
        key, value = pair.split("=")
        data[key] = value
    df = pd.DataFrame(data.items(), columns=['experiment', 'variant_id'])
    df['user_id'] = row['user_id']
    df['event_name'] = row['event_name']
    df['item_id'] = row['item_id']
    df['timestamp'] = row['timestamp']
    df['datetime'] = row['datetime']
    df['date'] = row['date']
    df['site'] = row['site']
    return df

df_1 = df_0.apply(dict_to_df, axis=1)
df_2 = pd.concat(df_1.to_list(), ignore_index=True)
df_2.head()
```





Ahora, nuevamente tomando el articulo de referencia, vamos a separar la columna "experiment" en dos con el separador "/" para distinguir entre el "path" y el experimento como tal:


```python
# Aplicamos la función split a la columna "experiment_name" y expandirla en nuevas columnas
nuevas_columnas = df_2["experiment"].str.split('/', expand=True)

# Asignamos nombres a las nuevas columnas
nuevas_columnas = nuevas_columnas.rename(columns={0: "path", 1: "experiment_name"})

# Unimos las nuevas columnas al DataFrame original
df_3 = pd.concat([df_2, nuevas_columnas], axis=1)

# Reordenamos el dataframe
df_3 = df_3[['user_id', 'event_name', 'item_id', 'timestamp', 'datetime', 'date', 'site', 'experiment', 'path', 'experiment_name', 'variant_id']]
df_3.head()
```






Listo lo anterior, debemos crear una variable binaria de 1s y 0s que nos permita identificar si el experimento termino en compra o no (conversion). Para ello, filtramos inicialmente el dataframe anterior, solo con los clientes que hicieron compra y vamos a asignar el valor de 1 a cada registro:


```python
# Presentamos la información de cuyos usuarios terminaron el compra al final de la "cadena de navegación" y agregamos una columna con 1s para estos usuarios que terminaron su "cadena de navegacion" en compra
df_buy_0 = df_3[df_3['event_name']=='BUY']
df_buy_0 = df_buy_0.assign(conversion_buy=1)
df_buy_0.head()
```





Como podemos observar, algunos clientes se repiten, esto porque en la etapa de compra ("BUY") tuvieron mas de un experimento. Sin embargo, podemos identificar que corresponden a un mismo "item_id", con lo cual, podemos descartar las demas variables y crear un dataframe más sencillo que con los elementos que necesitaremos de llave para cruzar, estos son "user_id" e "item_id" junto a la marca de conversion:


```python
# Arreglamos los datos que necesitaremos para hacer el join/merge mas adelante y saber si la "cadena de navegacón" tuvo conversión o no a compra
df_buy_1 = df_buy_0[['user_id', 'item_id', 'conversion_buy']].drop_duplicates()
df_buy_1
```






Ahora lo que sigue, es cruzar los dataframes, de tal modo que a cada "user_id", le peguemos si para ese "item_id" su "cadena de navegacion" terminó en compra o no. Con esto lo que hacemos es mapear toda la "cadena de navegación" y determinar si esa cadena termino en compra, independiente del momento de tiempo que se haya dado:


```python
# Hacemos la unión de las 2 tablas para saber cuales eventos terminaron en compra y cuales no con una variable binaria de 1s y 0s
df_4 = pd.merge(df_3, df_buy_1, on=['user_id','item_id'], how='left')
df_4['conversion_buy'] = df_4['conversion_buy'].fillna(0)
df_4['conversion_buy'] = df_4['conversion_buy'].astype(int)
df_4.head()
```






Debemos seguir revisando que los datos sean correctos para utilizarlos y que permitan sacar conclusiones confiables. Ahora vamos a filtrar los datos para un cliente en particular que realizó una compra y ver su "cadena de navegación":


```python
# Tomamos uno de los usuarios que termino en compra para ver su "cadena de navegación"
df_4[(df_4['user_id']==466) & (df_4['item_id']==789004239.0)]
```





En la salida anterior vemos un posible error que puede traer problemas o duplicidad de los datos. Por ejemplo, el experimento **buyingflow/user-track=6796** se repite varias veces en diferentes eventos, como son **CHECKOUT_1**, **CHECKOUT_1**, **CHECKOUT_1** y **BUY**. 

Para que esto no nos cause problemas vamos a quedarnos con la minima fecha a la que el usuario se enfrento a ese experimento, de tal modo que solo nos va a aparecer una vez dicho experimento por "cadena de navegación" y sera el primero al que el usuario se enfrentó:


```python
# En el paso anterior hemos visto que algunos usuarios se repien con la misma información, para ello nos vamos a quedar con la minima fecha, que seria el primer momento en que el ususario se enfrento al experimento
df_4 = df_4.groupby(['user_id', 'item_id', 'date','site', 'experiment', 'path', 'experiment_name', 'variant_id', 'conversion_buy'])['datetime'].min().reset_index()
df_4.head()
```









Volvemos a validar el usuario e item para validar que cada experimento aparezca una sola vez:


```python
# Validamos el mismo caso donde observamos que el ususario se repetia varias veces por ejemplo en el experimento "user-track = 6796" ahora aparece una sola vez por experimento
df_4[(df_4['user_id']==466) & (df_4['item_id']==789004239.0)]
```









Enhorabuena! 

El dataframe anterior tiene toda la información como la necesitamos para poder trabajarla.


```python
# Resumen información del dataframe final
print("Info dataset:")
print(df_4.info())
print('\n')
print("Valores unicos por variable:")
print(df_4.nunique())
```

    Info dataset:
    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 231517 entries, 0 to 231516
    Data columns (total 10 columns):
     #   Column           Non-Null Count   Dtype                                 
    ---  ------           --------------   -----                                 
     0   user_id          231517 non-null  int64                                 
     1   item_id          231517 non-null  float64                               
     2   date             231517 non-null  object                                
     3   site             231517 non-null  object                                
     4   experiment       231517 non-null  object                                
     5   path             231517 non-null  object                                
     6   experiment_name  231517 non-null  object                                
     7   variant_id       231517 non-null  object                                
     8   conversion_buy   231517 non-null  int64                                 
     9   datetime         231517 non-null  datetime64[ns, pytz.FixedOffset(-240)]
    dtypes: datetime64[ns, pytz.FixedOffset(-240)](1), float64(1), int64(2), object(6)
    memory usage: 17.7+ MB
    None
    
    
    Valores unicos por variable:
    user_id             6298
    item_id            41062
    date                   2
    site                   1
    experiment            23
    path                   7
    experiment_name       23
    variant_id            28
    conversion_buy         2
    datetime           45311
    dtype: int64
    

Nuevamente siguiendo el [articulo de referencia](https://medium.com/mercadolibre-tech/a-b-testing-meli-3a5ad2b4594d), vamos a crear un dataframe de resumen contando por fecha, la cantidad de ususarios que se sometieron a cada experimento y sus posibles variantes. Ademas, se agrega la suma de usuarios cuya "cadena de navegación" terminó en compra y se calcula la tasa de conversión como la cantidad de compras sobre el total de ususarios que vieron el experimento:


```python
# Vamos a presentar los resultados finales de forma similar al articulo de referencia: https://medium.com/mercadolibre-tech/a-b-testing-meli-3a5ad2b4594d

df_5 = df_4.groupby(['date', 'experiment_name', 'variant_id']) \
           .agg({'user_id': 'count', 'conversion_buy': 'sum'}) \
           .reset_index()
df_5 = df_5.rename(columns={"user_id": "users"})
df_5['conversion_rate'] = df_5['conversion_buy']/df_5['users']
df_5['conversion_rate_%'] = df_5['conversion_rate'] .apply(lambda x: '{:.2f}%'.format(x*100))
df_5 = df_5.sort_values(['date','experiment_name', 'conversion_rate_%', ], ascending = [True, True, False], ignore_index=True)
df_5
```









Ahora podemos filtrar la información para ver solamente aquellos experimentos que hayan tenido una conversión o que hayan terminado en compra. Esto podriamos hacerlo de dos formas diferentes:

### **Opción 1:**
Filtrar de todos los posibles experimentos, aquellos que hayan tenido mas de una variante para poder comparar.


```python
# Agrupamos los datos por experimento y fecha para contar el número de variantes
variant_counts_1 = df_5.groupby(['experiment_name', 'date'])['variant_id'].nunique()

# Filtramos los datos para aquellos experimentos con más de una variante 
df_6 = df_5.loc[(df_5['experiment_name'].isin(variant_counts_1[variant_counts_1 > 1].index.get_level_values(0)))].reset_index(drop=True)

# Mostramos el dataframe filtrado
df_6
```










### **Opción 2:** 
Filtrar todos de todos los posibles experimentos, aquellos que hayan llegado a compra (conversion=1) y luego filtrar de los que llegaron a comprar, los que tengan mas de una variante para poder comparar.


```python
# Podemos hacerlo de otra forma y es, filtrar primero aquellos experimentps que hayan terminado en compra y luego quedarnos con los que hayan tenido mas de 1 variante para comparar

df_7 = df_5[(df_5['conversion_buy']!=0)]

# Agrupamos los datos por experimento y fecha y contar el número de variantes
variant_counts_2 = df_7.groupby(['experiment_name', 'date'])['variant_id'].nunique()

# FiltraMmos los datos para aquellos experimentos con más de una variante 
df_7 = df_7.loc[(df_7['experiment_name'].isin(variant_counts_2[variant_counts_2 > 1].index.get_level_values(0)))].reset_index(drop=True)

# Mostramos el DataFrame filtrado
df_7
```










En el resultado anterior podemos ver 3 diferentes experimentos que se aplicaron en días diferentes cada uno con dos posibles variantes. Allí, se presenta la cantidad de usuarios que vieron cada experiment y cuantos de los que lo vieron luego realizaron una compra (conversion_rate).

Como parte de la revisión de los datos, para evaluar que sean correctos para sacar conclusiones, vamos a revisar la cantidad de posibles variantes para cada experimento:


```python
# Agrupar por experimento y variante contar el número de veces que aparece cada variante
variantes_por_experimento = df_4.groupby('experiment_name')['variant_id'].value_counts()
variantes_por_experimento
```




    experiment_name                             variant_id
    HideTransitionModal                         6647             53
                                                DEFAULT          44
                                                6993             35
                                                6646             34
    address_hub                                 3574           1171
    assetsCdnDomainMLA                          DEFAULT          25
    carousel-v2p-above-the-fold                 6786          16148
                                                6787          15091
                                                DEFAULT          34
    classiWordingFree                           2826             25
    compatibilityWidget                         5539             21
    cpgShowOnlyAddToCart                        6690             98
    escWebMLA                                   2874           1332
    remove-ecn-tag                              4954          28471
                                                DEFAULT          32
    sa-on-vip                                   6695           2990
                                                6696           2855
    secure_card                                 4612             25
    seller-with-tooltip                         4692          38530
    servicesQuoteUnification                    DEFAULT          25
    shippingCalculatorMigrationModalExperiment  6551          34070
                                                DEFAULT          33
    showV2V3BoxMessages                         6430          40623
                                                DEFAULT          44
    tendency-landing-enabled-MLA                6980           6384
    user-track                                  6796           1446
    viewItemPageMigrationDesktopHirableSRV      7174             53
                                                7175              8
    viewItemPageMigrationDesktopQuotableSRV     7179             42
                                                7178             17
    viewItemPageMigrationDesktopRES             5941           1755
    viewItemPageMigrationDesktopRESDev          6861              5
    viewItemPageMigrationDesktopReviewsNoTabs   4856          14785
                                                DEFAULT          11
    viewItemPageMigrationReturns                5208          25176
                                                DEFAULT          26
    Name: variant_id, dtype: int64



De igual forma es importante validar si alguna variante se repite para más de un experimento, que por suerte no es el caso:


```python
# Agrupar por variante y experimento y contar el número de veces que aparece cada experimento
experimentos_por_variante = df_4.groupby('variant_id')['experiment_name'].value_counts()
experimentos_por_variante
```




    variant_id  experiment_name                           
    2826        classiWordingFree                                25
    2874        escWebMLA                                      1332
    3574        address_hub                                    1171
    4612        secure_card                                      25
    4692        seller-with-tooltip                           38530
    4856        viewItemPageMigrationDesktopReviewsNoTabs     14785
    4954        remove-ecn-tag                                28471
    5208        viewItemPageMigrationReturns                  25176
    5539        compatibilityWidget                              21
    5941        viewItemPageMigrationDesktopRES                1755
    6430        showV2V3BoxMessages                           40623
    6551        shippingCalculatorMigrationModalExperiment    34070
    6646        HideTransitionModal                              34
    6647        HideTransitionModal                              53
    6690        cpgShowOnlyAddToCart                             98
    6695        sa-on-vip                                      2990
    6696        sa-on-vip                                      2855
    6786        carousel-v2p-above-the-fold                   16148
    6787        carousel-v2p-above-the-fold                   15091
    6796        user-track                                     1446
    6861        viewItemPageMigrationDesktopRESDev                5
    6980        tendency-landing-enabled-MLA                   6384
    6993        HideTransitionModal                              35
    7174        viewItemPageMigrationDesktopHirableSRV           53
    7175        viewItemPageMigrationDesktopHirableSRV            8
    7178        viewItemPageMigrationDesktopQuotableSRV          17
    7179        viewItemPageMigrationDesktopQuotableSRV          42
    DEFAULT     HideTransitionModal                              44
                showV2V3BoxMessages                              44
                carousel-v2p-above-the-fold                      34
                shippingCalculatorMigrationModalExperiment       33
                remove-ecn-tag                                   32
                viewItemPageMigrationReturns                     26
                assetsCdnDomainMLA                               25
                servicesQuoteUnification                         25
                viewItemPageMigrationDesktopReviewsNoTabs        11
    Name: experiment_name, dtype: int64



## **A/B Test Bayesiano** 

Una vez revisado todo lo anterior, lo siguiente sería realizar el A/B test para validar cual de las variantes es mejor. Esto lo haremos apoyandonos en el paqueta "[bayesian_testing](https://pypi.org/project/bayesian-testing/)" de python que permite evaluar A/B test desde un enfoque bayesiano.


```python
# Inatalamos el paquete que vamos a utilizar
!pip install bayesian_testing
```

    Looking in indexes: https://pypi.org/simple, https://us-python.pkg.dev/colab-wheels/public/simple/
    Collecting bayesian_testing
      Downloading bayesian_testing-0.5.4-py3-none-any.whl (28 kB)
    Requirement already satisfied: numpy<2.0.0,>=1.19.0 in /usr/local/lib/python3.9/dist-packages (from bayesian_testing) (1.22.4)
    Installing collected packages: bayesian_testing
    Successfully installed bayesian_testing-0.5.4
    

Vamos a trabajar con la opción para datos binarios ya que en este caso previamente hemos construido la variable de conversión compuesta por 1s y 0s.


```python
# Importamos del paquete "bayesian_testing" el test para datos binarios
from bayesian_testing.experiments import BinaryDataTest
```

Inicialmente probamos de forma básica como funciona el test para algun experimento o algunas variables. Esto se hace de forma manual o programática para ir validando la información: En este caso vamos a tomar las primeras variantes de nuestro dataframe de resumen correspondiente al experimento "carousel-v2p-above-the-fold" que se compone de dos posibles variantes:


```python
conv_test = BinaryDataTest()

variant_6787_conv = df_4['conversion_buy'][(df_4.variant_id == '6787')].values
variant_6786_conv = df_4['conversion_buy'][(df_4.variant_id == '6786')].values

conv_test.add_variant_data('6787', variant_6787_conv)
conv_test.add_variant_data('6786', variant_6786_conv)

conv_test.evaluate()
```




    [{'variant': '6787',
      'totals': 15091,
      'positives': 369,
      'positive_rate': 0.02445,
      'posterior_mean': 0.02448,
      'prob_being_best': 0.7371,
      'expected_loss': 0.0002736},
     {'variant': '6786',
      'totals': 16148,
      'positives': 377,
      'positive_rate': 0.02335,
      'posterior_mean': 0.02338,
      'prob_being_best': 0.2629,
      'expected_loss': 0.0013683}]



En el resultado anterior, podemos ver que la tasa de conversión, llamada "positive_rate" en este paquete, es mayor en la variante 6787, sin embargo, son bastante parecidas: 

1. variant 6787: 2,445%
2. variant 6786: 2,335%

Pero su probabilidad de ser el mejor ("prob_being_best") es bastante diferente:

1. variant 6787: 74,255%
2. variant 6786: 25,745%

Siendo mucho mayor para la variante 6787 la cual se consagra como la variante con mayor probabilidad de finalizar en compra para este experimento con una amplia diferencia.

Una vez revisado lo anterior, vamos a crear un diccionario que nos permita almacecar los resultados del test: conv_test.evaluate() a cada uno de los experimentos del dataframe. Lo anterior lo vamos a complementar con una serie de iteraciones que nos permitan calcular la información por fecha, experimento y variante. Con ello podremos realizar comparaciones del tipo:

El día DD-MM-YYYY el experimento XXX tuvo NNN variantes de las cuales la variante AAA presento una mayor probabilidad de ser la mejor.


```python
# Creamos un diccionario para almacenar los resultados de la prueba
results = {}

# Iteramos sobre cada fecha
for date in df_4['date'].unique():

    # Creamos un diccionario para almacenar los resultados de los experimentos de la fecha actual
    date_results = {}
    
    # Seleccionamos los datos correspondientes a la fecha actual
    date_data = df_4.loc[df_4['date'] == date]
    
    # Iteramos sobre cada experimento de la fecha actual
    for experiment in date_data['experiment_name'].unique():

        # Seleccionamos los datos correspondientes al experimento actual
        experiment_data = date_data.loc[date_data['experiment_name'] == experiment]
        
        # Creamos un objeto BinaryDataTest vacío
        conv_test = BinaryDataTest()
        
        # Iteramos sobre cada variante del experimento actual
        for variant in experiment_data['variant_id'].unique():

            # Seleccionamos los datos correspondientes a la variante actual
            variant_data = experiment_data.loc[experiment_data['variant_id'] == variant, 'conversion_buy'].values

            # Añadimos los datos de la variante actual al objeto BinaryDataTest
            conv_test.add_variant_data(variant, variant_data)
        
        # Calculamos las probabilidades de que cada variante sea la mejor dentro del experimento actual
        probabilities = conv_test.evaluate()
        
        # Añadimos las probabilidades calculadas al diccionario de resultados del experimento actual
        date_results[experiment] = probabilities
    
    # Añadimos el diccionario de resultados de los experimentos de la fecha actual al diccionario principal
    results[date] = date_results

# Mostramos el diccionario construido con los resultados del test
results
```








Lo anterior ha dejado guardados los resultados en un diccionario. Ahora, como lo hicimos al comienzo, vamos a transformar ese diccionario en un dataframe que nos permita visualizar mejor la información y realizar comparaciones entre experimentos por fecha, experimento y variantes junto a todas las métricas calculadas:


```python
# Creamos una lista vacía para almacenar los datos de cada experimento
data = []

# Iteramos sobre cada fecha en el diccionario
for date, experiments in results.items():

    # Iteramos sobre cada experimento en la fecha
    for experiment_name, variants in experiments.items():

        # Iteramos sobre cada variante en el experimento
        for variant_data in variants:

            # Exrtreamos los datos de variant_data
            variant = variant_data['variant']
            totals = variant_data['totals']
            positives = variant_data['positives']
            positive_rate = variant_data['positive_rate']
            posterior_mean = variant_data['posterior_mean']
            prob_being_best = variant_data['prob_being_best']
            expected_loss = variant_data['expected_loss']

            # Creamos un diccionario paara variant_data
            variant_dict = {'date': date,
                            'experiment_name': experiment_name,
                            'variant_id': variant,
                            'totals': totals,
                            'positives': positives,
                            'positive_rate': positive_rate,
                            'posterior_mean': posterior_mean,
                            'prob_being_best': prob_being_best,
                            'expected_loss': expected_loss}

            # Agregamos los datos del diccionario a la lista vacia que creamos al inicio
            data.append(variant_dict)

# Creamos un dataframe a partir de la lista "data"
results_df = pd.DataFrame(data)

# Ordernamos el dataframe
results_df = results_df.sort_values(['date', 'experiment_name', 'variant_id', 'positive_rate'], ascending = [True, True, True, True], ignore_index=True)

# Imprimimos el dataframe final
results_df
```









Justamente el dataframe anterior, nos permite comparar por fecha, todas las posibles variantes por experimento y comparar la cantidad de usuarios que vieron el experimento, la cantidad de usuarios cuya cadena de navegación termino en compra luego de ver el experimento ('positives'), la tasa de conversión ('positive_rate') y sobretodo, la probabilidad de que esa variante sea la mejor entre todas las posibles variantes del experimento ('prob_being_best')

## **Implementar API** 

Ahora para la implementación de la API vamos a crear un dataframe mas pequeño donde tengamos solamente las variables que necesitamos:


```python
# Creamos un dataframe mas pequeño con las variables a usar en la API
results_df_api = results_df[['date','experiment_name', 'variant_id', 'totals', 'positives']].drop_duplicates()
results_df_api
```










Para la creación de la API local, se utilizo el paquete [flask](https://flask.palletsprojects.com/en/2.2.x/api/), que nos permite definir la estructura de salida en el formato json que se solicitó y programar los parametros que se requieren para la consulta a traves de la URL con el metodo GET:


```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/experiment/<experiment_id>/result')
def get_experiment_results(experiment_id):

    # Obtenemos el valor del parámetro "day" para la solicitud HTTP
    day = request.args.get('day')
    
    # Validamos que la fecha proporcionada es correcta, de lo contrario mostrara el error "fecha invalida"
    try:
        day = pd.Timestamp(day).floor('D')
    except ValueError:
        return jsonify({'error': 'fecha invalida'}), 400
    
    # Filtramos los datos del dataframe para obtener los resultados del día y experimento que deseamos conocer
    filtered_results = results_df_api[(results_df_api['date'] == day) & (results_df_api['experiment_name'] == experiment_id)]
    
    # Si no hay resultados para ese día y ese experimento, se muestra el error "experimento no encontrado"
    if filtered_results.empty:
        return jsonify({'error': 'experimento no encontrado'}), 404
    
    # Calculamos los resultados requeridos, en este caso, total de participantes y total de compras
    total_participants = filtered_results['totals'].sum()
    winners = filtered_results.loc[filtered_results['positives'].idxmax(), 'variant_id']
    variants = []
    for index, row in filtered_results.iterrows():
        variants.append({
            'id': row['variant_id'],
            'numero_de_compras': str(row['positives'])
        })
    
    # Presentamos los resultados en el formato requerido
    results = {
        experiment_id: {
            'numero_de_participantes': str(total_participants),
            'ganador': winners,
            'variantes': variants
        }
    }
    return jsonify({'resultados': results})

# Iniicamos la API en el local host
if __name__ == '__main__':
    app.run()
```

     * Serving Flask app '__main__'
     * Debug mode: off
    2023-03-28 18:24:04,003 - werkzeug - INFO - [31m[1mWARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.[0m
     * Running on http://127.0.0.1:5000
    2023-03-28 18:24:04,004 - werkzeug - INFO - [33mPress CTRL+C to quit[0m
    

Es importante tener en cuenta que mientras la celda anterior se este ejecutando podremos realizar consultas a la API respectando la  estructura solicitada. Dichas consultas las podremos hacer a traves de nuestro navegador web o de alguna herramienta de desarrollo de API como son [Insomnia](https://insomnia.rest/) y [Postman](https://www.postman.com/). En este caso hemos probado algunos casos sobre los que retornan los siguientes resultados en la herramienta [Insomnia](https://insomnia.rest/):

1. http://localhost:5000/experiment/sa-on-vip/result?day=2021-08-01

<figure>
<img src='https://raw.githubusercontent.com/JdrSosa/MELI/main/Insomnia%20-%20sa-on-vip.png' width="1200" height="500" />
<figcaption></figcaption>
</figure>

2. http://localhost:5000/experiment/viewItemPageMigrationDesktopReviewsNoTabs/result?day=2021-08-01

<figure>
<img src='https://raw.githubusercontent.com/JdrSosa/MELI/main/Insomnia%20-%20viewItemPageMigrationDesktopReviewsNoTabs.png' width="1200" height="500" />
<figcaption></figcaption>
</figure>

3. http://localhost:5000/experiment/abc/result?day=2021-08-01

<figure>
<img src='https://raw.githubusercontent.com/JdrSosa/MELI/main/Insomnia%20-%20abc.png' width="1200" height="500" />
<figcaption></figcaption>
</figure>

Al finalizar las consultas de la API se debe detener la ejecución de la celda donde se ha creado previamente.

## **Consideraciones y Próximos pasos**

A partir de los datos suministrados se realizó un preprocesado que incluyo:

1. Agragar variables de fecha a partir de la marca de tiempo para ordenar la cadena de navegación y agrupar por YYYY-MM-DD.
2. Convertir a diccionario la variable 'experiments'.
3. Convertir a columas los items del diccionario para separar el 'experiment' y la 'variant_id'.
4. Separar la variable 'experiment_name' para obtener el 'path' y el 'experiment_name' propiamente realizado.
5. Agregar la marca con 1s a la target, esto es, 1 para todos los usuarios que hayan realizado compra y 0s para los que no.
6. Agregar la marca de conversión a todo el dataframe cruzando por 'user_id' e 'item_id' para ver toda la "cadena de navegación".
7. Quedarnos con la minima fecha en que el ususario se enfrento a cada experimento en su "cadena de navegación".

Se optó por tomar para cada posible "cadena de navegación" la minima fecha en la que el cliente se enfrento a cada experimento, de tal modo que solo se tiene para toda la cadena una aparición y no hay duplicidad en la información. Por otra parte, la llave que se utilizó para determinar si hubo o no conversión en la cadena fue el 'user_id' junto al 'item_id', de tal forma que se tienen todos los posibles experimentos con sus correspondientes variantes para cada evento y se puede concluir si eso terminó o no en compra.

Para calcular la tasa de conversión se agruparon todos los posibles experimentos con sus variantes por fecha y de calculó la cantidad de ususarios que vieron el experiento asi como la cantidad de ususarios que terminaron en compra, de este modo la tasa de conversión era la cantidad de compras sobre la cantidad de veces que se vió el experimento.

Luego, para determinar si efectivamente o no la variante tenia una mayor probabilidad de exito, se utilizo un test binario con enfoque bayesiano apoyandonos en el paquete "[bayesian_testing](https://pypi.org/project/bayesian-testing/), que nos permite utilizar todo el dataset y comparar de todas las posibles variantes cual tiene la mayor probabilidad de ser la mejor, y evidenciamos que no en todos los casos la variante que tiene una mayor tasa de conversión es la que tiene una mayor probabilidad de ser la mejor dentro del experimento.

En cuanto a la creación de la API se utilizo el paquete [flask](https://flask.palletsprojects.com/en/2.2.x/api/), que nos permite definir la estructura de salida en el formato json que se solicitó y programar los parametros que se requieren para la consulta a traves de la URL con el metodo GET.

Como próximos pasos, para trabajar con volumenes de datos mas grandes se pueden trabajar directamente el servidores cloud como [Amazon Web Services](https://aws.amazon.com/es/?nc2=h_lg), que permite tener todo integrado en su plataforma. Allí encontraremos soluciones en cuanto a maquinas viruales de gran capacidad para procesamiento de datos 'Amazon EC2' y tambien de almacenamiento como es el caso de 'Amazon S3'. 

Adicionalmente se podría pensar en un enfoque MLOps que es la aplicación de las prácticas DevOps en el desarrollo y puesta en producción de los modelos de 
machine learning, este enfoque viene de la combinación de los términos Machine Learning y Operations. La aplicación de las prácticas MLOps trata de agilizar el proceso de experimentación y desarrollo de modelos, facilitar y hacer más eficiente el proceso de desplegado y mantenimiento de los modelos ya puestos en producción y asegurar la calidad de los resultados obtenidos mediante estos modelos.

A lo anterior, de nuevo en la plataforma de amazon, se podría acudir a [Amazon Sagemaker](https://github.com/aws-solutions/mlops-workload-orchestrator) que es un servicio totalmente administrado de un extremo a otro en la nube de AWS para flujos de trabajo de aprendizaje automático. Se adapta a diferentes tipos de servicios de creación, capacitación e implementación de modelos, siendo el caso de uso principal el desarrollo de soluciones de ML. 
