import pandas as pd
import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
from bayesian_testing.experiments import BinaryDataTest


def str_to_dict(exp_str):
    """
    funcion convertir en str un diccionario
    exp_str: es la variable sobre la cual se desea operar
    """
    # Remove the curly braces
    exp_str = exp_str.strip('{}')
    # Split into key-value pairs
    pairs = exp_str.split(', ')
    # Split each pair and convert to dictionary
    exp_dict = {}
    for pair in pairs:
        key, value = pair.split('=')
        exp_dict[key] = value
    return exp_dict


def explode_dict(row):
    """
    funcion para abrir diccionario
    """
    dict_items = row['experiments_dict'].items()
    expanded_rows = []
    for key, value in dict_items:
        new_row = row.copy()
        new_row['experiment_key'] = key
        new_row['experiment_value'] = value
        expanded_rows.append(new_row)
    return pd.DataFrame(expanded_rows)


# Function to calculate PSI
def calculate_psi(expected, actual):
    # Handling division by zero
    epsilon = 1e-10
    
    # Calculate expected and actual proportions
    expected_prop = np.array(expected) / sum(expected)
    actual_prop = np.array(actual) / sum(actual)
    
    # Calculate PSI
    psi = sum((expected_prop - actual_prop) * np.log((expected_prop + epsilon) / (actual_prop + epsilon)))
    
    return psi


def analisis_experimento(df,nombre_experimento):
    df_filtered = df[df.experiment == nombre_experimento]


    result = df_filtered.groupby('date').agg({
        'experiment': 'first',
        'variant': lambda x: x.unique().tolist(),
        'participation_percent': lambda x: x.tolist(), 
        'participants': 'sum',
        'buy_rate_percent': lambda x: x.tolist(), 
        'buy_rate': 'mean'}).reset_index()

    result['participation_percent'] = result['participation_percent'].apply(lambda x: [round(i, 2) for i in x])

    # Names of variants each day
    print(result.to_string(index=False))

    print("")

        # Get participation percentages for the first and second vectors from the DataFrame
    expected_participation_percent = result['participation_percent'].iloc[0]
    actual_participation_percent = result['participation_percent'].iloc[1]

    # Calculate PSI
    psi = calculate_psi(expected_participation_percent, actual_participation_percent)
    print("Population Stability Index (PSI) between first and second vectors:", psi)

    # Define a custom palette
    custom_palette = sns.color_palette("tab10", df_filtered['variant'].nunique())

    # Create a figure and a set of subplots
    fig = plt.figure(figsize=(14, 7))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1])  # Create a 2-row grid

    # Create the first subplot for the line graph
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('white')  # set background color to white

    # Plot the line graph on the primary y-axis
    sns.lineplot(data=df_filtered, x='date', y='buy_rate', hue='variant', marker='o', ax=ax1, palette=custom_palette)
    ax1.set_ylabel('Buy Rate')
    ax1.set_title('Buy Rate Each Day by Variant: ' + nombre_experimento)
    ax1.legend(loc='upper right', bbox_to_anchor=(1.15, 1))

    # Set y-axis limit to double the maximum rate
    max_rate = df_filtered['buy_rate'].max()
    ax1.set_ylim(0, max_rate * 2)

    # Create a second subplot for the bar graph
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)  # Share x-axis with ax1
    ax2.set_facecolor('white')  # set background color to white

    # Plot the bar graph on the secondary y-axis
    sns.barplot(data=df_filtered, x='date', y='participants', hue='variant', dodge=True, alpha=0.6, ax=ax2, palette=custom_palette)
    ax2.set_ylabel('Participants')
    ax2.set_title('Participants Each Day by Variant')

    # Add text annotations for participation percent above each bar
    for p in ax2.patches:
        ax2.annotate('{:.1f}'.format(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=10, color='black', xytext=(0, 10),
                    textcoords='offset points')

    # Adjust the legend
    ax2.legend(loc='upper right', bbox_to_anchor=(1.15, 1))

    # Synchronize x-axis ticks and grid lines
    ax1.xaxis.set_tick_params(rotation=0)
    ax2.xaxis.set_tick_params(rotation=0)
    ax1.grid(True)
    ax2.grid(True)

    plt.tight_layout()
    plt.show()



    return

