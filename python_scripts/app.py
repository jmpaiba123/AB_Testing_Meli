import os
import pandas as pd
from flask import (Flask, redirect, jsonify, render_template, request,
                   send_from_directory, url_for)


app = Flask(__name__)

try:
    df_results = pd.read_csv("grouped_inf.csv", sep=",")
    archivo_valido = not df_results.empty
except ValueError:
    print("error en la lectura del archivo") 


app = Flask(__name__)

@app.route('/experiment/<exp_name>/result')

def get_experiment_results(exp_name):

    print(archivo_valido)
    if not archivo_valido:
        return jsonify({'error': 'error en la lectura del archivo'}), 400

    # Obtenemos el valor del parámetro "day" para la solicitud HTTP
    day = request.args.get('day')
    print(day)
    print(exp_name)

    # Validamos que la fecha proporcionada es correcta, de lo contrario mostrara el error "fecha invalida"
    if len(day) == 0:
        return jsonify({'error': 'fecha invalida'}), 400
    try:
        day_validation = pd.Timestamp(day).floor('D')
    except ValueError:
        return jsonify({'error': 'fecha invalida'}), 400
    
    # Filtramos los datos del dataframe para obtener los resultados del día y experimento que deseamos conocer
    filtered_results = df_results[(df_results['experiment'] == exp_name)&(df_results['date'] == day)]
    print(filtered_results)
    # Si no hay resultados para ese día y ese experimento, se muestra el error "experimento no encontrado"
    if filtered_results.empty:
        return jsonify({'error': 'experimento no encontrado'}), 404
    
    # Calculamos los resultados requeridos, en este caso, total de participantes, total de compras y numero de participantes por variante
    total_participants = filtered_results['participants'].sum()
    winners = filtered_results.loc[filtered_results['purchases'].idxmax(), 'variant']
    variants = []
    for index, row in filtered_results.iterrows():
        variants.append({
            'id': row['variant'],
            'numero_de_compras': str(row['purchases']),
            'numero_de_participantes': str(row['participants'])
        })
    
    # Presentamos los resultados en el formato requerido
    results = {
        exp_name: {
            'numero_de_participantes': str(total_participants),
            'ganador': winners,
            'variantes': variants
        }
    }
    return jsonify({'resultados': results})

# Iniicamos la API en el local host
if __name__ == '__main__':
    app.run()
