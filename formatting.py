"""Data formatting functions."""

def format_pairings(pairings_dict):
    """Format pairings results in D3-friendly format.

    Input:
    {'bread': 1.0, 'cake': 4.0, 
                   'carrot cake': 2.0, 
                   'date': 1.0, 
                   ... }

    Output:
    dataset = {'children': [
                {'Name': 'Olives', 'Count': 4319},
                {'Name': 'Tea', 'Count': 4159}, ... ]
              }
    """
    dataset = {"children": []}

    for pairing in pairings_dict.items():
        inner_dict = {}
        inner_dict["Name"] = pairing[0]
        inner_dict["Count"] = pairing[1]
        dataset["children"].append(inner_dict)

    return dataset