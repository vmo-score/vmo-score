"""Module implementing some useful methods."""

import shelve

import yaml


def save_shelf(filepath, field, obj):
    """Save an object into a file.

    Args:
        filepath (str): Path of the file
        field (str): Id of the object in the file
        obj (object): Object to be saved
    """
    shelf = shelve.open(filepath)
    shelf[field] = obj
    shelf.close()


def load_shelve(filepath, field):
    """Load a file into an object.

    Args:
        filepath (str): String representing the path of the file
        field (str): identifier of the object

    Returns:
        dict: Dictionary representing the object
    """
    shelf = shelve.open(filepath)
    info = shelf[field]
    shelf.close()
    return info


def generate_configuration(filepath, pn):
    """Generate a configuration file for the Petri Net.

    Args:
        filepath (str): String representing the path of the output
        pn (PetriNet): A Petri Net
    """
    output = {'control': None,
              'global': [{'tempo': None}],
              'conditions': None,
              'actions': None
              }

    conditions = []
    for t in pn.pn.transition():
        t_values = {'time-min': t.min_time,
                    'transition': str(t.name),
                    'time-max': t.max_time,
                    'condition': str(t.guard)}
        conditions.append(t_values)

    output['conditions'] = None if len(conditions) == 0 else conditions

    with open(filepath, 'w') as f:
        yaml.dump(output, f, default_flow_style=False)


def load_configuration(filepath):
    """Load a configuration file.

    Args:
        filepath: String representing the path of the configuration file

    Returns:
        dict: Dictionary representing the configuration file
    """
    with open(filepath, 'r') as f:
        conf = yaml.load(f)
        return conf
