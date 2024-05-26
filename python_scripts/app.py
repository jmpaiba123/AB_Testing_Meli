import os
import pandas as pd
from flask import (Flask, redirect, jsonify, render_template, request,
                   send_from_directory, url_for)

df_results = pd.read_csv("/Users/juanmanuelpaiba/Documents/Juan_Paiba/AB_Testing_Meli/data/Outputs/grouped_inf.csv", sep = ";")


app = Flask(__name__)


@app.route('/')


def get_experiment_results(experiment_id):

    # Obtenemos el valor del parámetro "day" para la solicitud HTTP
    day = request.args.get('day')
    
    # Validamos que la fecha proporcionada es correcta, de lo contrario mostrara el error "fecha invalida"
    try:
        day = pd.Timestamp(day).floor('D')
    except ValueError:
        return jsonify({'error': 'fecha invalida'}), 400
    
    # Filtramos los datos del dataframe para obtener los resultados del día y experimento que deseamos conocer
    filtered_results = df_results[(df_results['date'] == day) & (df_results['experiment_name'] == experiment_id)]
    
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

def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
