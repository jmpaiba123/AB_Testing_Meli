import pandas as pd

# Function to convert the string to a dictionary
def str_to_dict(exp_str):
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

# Function to explode the dictionary into separate rows
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

