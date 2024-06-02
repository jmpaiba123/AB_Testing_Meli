import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
import logging
from bayesian_testing.experiments import DiscreteDataTest, BinaryDataTest

sns.set()

class AnalisisExperimento:
    def __init__(self, df):
        """
        Inicializa la clase AnalisisExperimento.

        Parámetros:
        df (pd.DataFrame): DataFrame que contiene los datos experimentales.
        """
        self.df = df

    @staticmethod
    def str_to_dict(exp_str):
        """
        Convierte una representación de cadena de un diccionario a un diccionario real.

        Parámetros:
        exp_str (str): La representación en cadena del diccionario.

        Retorna:
        dict: El diccionario convertido.
        """
        exp_str = exp_str.strip('{}')
        pairs = exp_str.split(', ')
        exp_dict = {key: value for key, value in (pair.split('=') for pair in pairs)}
        return exp_dict

    @staticmethod
    def explode_dict(row):
        """
        Expande un diccionario almacenado en una fila de un DataFrame en filas separadas.

        Parámetros:
        row (pd.Series): La fila del DataFrame que contiene el diccionario.

        Retorna:
        pd.DataFrame: El DataFrame expandido.
        """
        dict_items = row['experiments_dict'].items()
        expanded_rows = [
            {**row, 'experiment_key': key, 'experiment_value': value}
            for key, value in dict_items
        ]
        return pd.DataFrame(expanded_rows)

    @staticmethod
    def calcular_psi(esperado, actual):
        """
        Calcula el Índice de Estabilidad de Población (PSI) entre dos distribuciones.

        Parámetros:
        esperado (list): La distribución esperada.
        actual (list): La distribución actual.

        Retorna:
        float: El valor PSI calculado.
        """
        epsilon = 1e-10
        proporcion_esperada = np.array(esperado) / sum(esperado)
        proporcion_actual = np.array(actual) / sum(actual)
        psi = sum((proporcion_esperada - proporcion_actual) * np.log((proporcion_esperada + epsilon) / (proporcion_actual + epsilon)))
        return psi

    def analisis_experimento(self, nombre_experimento):
        """
        Realiza un análisis en el experimento especificado.

        Parámetros:
        nombre_experimento (str): El nombre del experimento a analizar.

        Retorna:
        None
        """
        df_filtrado = self.df[self.df.experiment == nombre_experimento]

        # Suprimir mensajes informativos de matplotlib
        logging.getLogger('matplotlib.category').setLevel(logging.ERROR)
        warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

        resultado = df_filtrado.groupby('date').agg({
            'experiment': 'first',
            'variant': lambda x: x.unique().tolist(),
            'participation_percent': lambda x: x.tolist(),
            'participants': 'sum',
            'buy_rate_percent': lambda x: x.tolist(),
            'buy_rate': 'mean'
        }).reset_index()

        resultado['participation_percent'] = resultado['participation_percent'].apply(lambda x: [round(i, 2) for i in x])

        print(resultado.to_string(index=False))
        print("")

        participacion_esperada = resultado['participation_percent'].iloc[0]
        participacion_actual = resultado['participation_percent'].iloc[1]

        psi = self.calcular_psi(participacion_esperada, participacion_actual)
        print("Índice de Estabilidad de Población (PSI) entre el primer y segundo vector:", psi)

        paleta_personalizada = sns.color_palette("tab10", df_filtrado['variant'].nunique())

        fig = plt.figure(figsize=(12, 6))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 1])

        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_facecolor('white')
        sns.lineplot(data=df_filtrado, x='date', y='buy_rate', hue='variant', marker='o', ax=ax1, palette=paleta_personalizada)
        ax1.set_ylabel('Tasa de Compra')
        ax1.set_title(f'Tasa de Compra por Día por Variante: {nombre_experimento}')
        ax1.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        ax1.set_ylim(0, df_filtrado['buy_rate'].max() * 2)

        ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
        ax2.set_facecolor('white')
        sns.barplot(data=df_filtrado, x='date', y='participants', hue='variant', dodge=True, alpha=0.6, ax=ax2, palette=paleta_personalizada)
        ax2.set_ylabel('Participantes')
        ax2.set_title('Participantes por Día por Variante')

        for p in ax2.patches:
            ax2.annotate(f'{p.get_height():.1f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', fontsize=10, color='black', xytext=(0, 10), textcoords='offset points')

        ax2.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        ax1.xaxis.set_tick_params(rotation=0)
        ax2.xaxis.set_tick_params(rotation=0)
        ax1.grid(True)
        ax2.grid(True)

        plt.tight_layout()
        plt.show()

    def default_count(self, nombre_experimento):
        """
        Realiza un análisis en el experimento especificado.

        Parámetros:
        nombre_experimento (str): El nombre del experimento a analizar.

        Retorna:
        DataFrame: Un DataFrame con el resultado del análisis.
        """
            # Filtrar el DataFrame por el experimento especificado
        df_filtrado = self.df[self.df.experiment == nombre_experimento]
        
        # Agrupar y agregar los datos por día
        resultado_diario = df_filtrado.groupby('date').agg(
            total_participants=('participants', 'sum'),
            total_purchases=('purchases', 'sum'),
            default_participants=('participants', lambda x: x[df_filtrado['variant'] == 'DEFAULT'].sum()),
            default_count=('variant', lambda x: (x == 'DEFAULT').count())
        ).reset_index()
        
        # Calcular el porcentaje de participantes por día en DEFAULT
        resultado_diario['default_participation_percent'] = (resultado_diario['default_participants'] / resultado_diario['total_participants']) * 100

        # Calcular los totales para todo el experimento
        total_participants = resultado_diario['total_participants'].sum()
        total_purchases = resultado_diario['total_purchases'].sum()
        total_default_participants = resultado_diario['default_participants'].sum()
        total_default_count = resultado_diario['default_count'].sum()

        # Crear un DataFrame para los totales
        total_data = {
            'date': ['Total'],
            'total_participants': [total_participants],
            'total_purchases': [total_purchases],
            'default_participants': [total_default_participants],
            'default_count': [total_default_count],
            'default_participation_percent': [(total_default_participants / total_participants) * 100]
        }
        resultado_total = pd.DataFrame(total_data)

        # Concatenar los resultados diarios con los totales
        resultado_final = pd.concat([resultado_diario, resultado_total], ignore_index=True)

        return resultado_final
    
    def get_experiments_with_high_default(self, threshold=10.0):
        """
        Obtiene una lista de experimentos con un porcentaje de participación en DEFAULT superior al umbral dado.

        Parámetros:
        threshold (float): El porcentaje de umbral para la participación en DEFAULT.

        Retorna:
        list: Una lista de nombres de experimentos que superan el umbral.
        """
        experiments_with_high_default = []
        for experiment in self.df['experiment'].unique():
            result = self.default_count(experiment)
            total_row = result[result['date'] == 'Total']
            if not total_row.empty and total_row['default_participation_percent'].iloc[0] > threshold:
                experiments_with_high_default.append(experiment)
        
        return experiments_with_high_default
    
    def exclude_high_default_experiments(self, high_default_experiments):
        """
        Excluye los experimentos de alto valor por defecto del DataFrame original.

        Parámetros:
        high_default_experiments (list): La lista de experimentos a excluir.

        Retorna:
        DataFrame: Un DataFrame con los experimentos excluidos.
        """
        filtered_df = self.df[~self.df['experiment'].isin(high_default_experiments)]
        return filtered_df

    def ab_test_discreto(self, nombre_experimento):
        """
        Realiza un análisis de prueba AB discreta en el experimento especificado.

        Parámetros:
        nombre_experimento (str): El nombre del experimento a analizar.

        Retorna:
        None
        """
        variantes_unicas = self.df[self.df.experiment == nombre_experimento].variant.unique()
        prueba_discreta = DiscreteDataTest([0, 1])

        for variante in variantes_unicas:
            datos_variante = self.df[(self.df.experiment == nombre_experimento) & (self.df.variant == variante)].purchase_funnel_flag.values
            prueba_discreta.add_variant_data(str(variante), datos_variante)

        resultados_evaluacion = prueba_discreta.evaluate()
        print(pd.DataFrame(resultados_evaluacion).to_markdown(tablefmt="grid", index=False))

    def ab_test_binario(self, nombre_experimento):
        """
        Realiza un análisis de prueba AB binaria en el experimento especificado.

        Parámetros:
        nombre_experimento (str): El nombre del experimento a analizar.

        Retorna:
        None
        """
        prueba_binaria = BinaryDataTest()
        variantes_unicas = self.df[self.df.experiment == nombre_experimento].variant.unique()

        for variante in variantes_unicas:
            datos_variante = self.df[(self.df.experiment == nombre_experimento) & (self.df.variant == variante)].purchase_funnel_flag.values
            prueba_binaria.add_variant_data(str(variante), datos_variante)

        resultados_evaluacion_binaria = prueba_binaria.evaluate()
        print(pd.DataFrame(resultados_evaluacion_binaria).to_markdown(tablefmt="grid", index=False))