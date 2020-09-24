from typing import Dict, List, Tuple


def to_argument_dict(parameter_dict: Dict) -> Tuple[List, Dict]:
    positional_args = [f"--{parameter_dict['name']}"]
    short_name = parameter_dict.get('options', {}).get('short_name')
    if short_name is not None:
        positional_args.append(f"-{short_name}")

    keyword_args = {}
    if parameter_dict['data_type'] == bool:
        keyword_args['action'] = 'store_true'
    else:
        keyword_args['action'] = 'store'
        keyword_args['type'] = parameter_dict['data_type']
        keyword_args['choices'] = parameter_dict.get('choices')

    keyword_args['help'] = parameter_dict['description']

    if not parameter_dict['required']:
        keyword_args['default'] = parameter_dict['default']
    else:
        keyword_args['required'] = True

    return positional_args, keyword_args
