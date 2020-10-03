from typing import Dict, List, Tuple


def to_argument_dict(parameter_dict: Dict) -> Tuple[List, Dict]:
    positional_args = [f"--{parameter_dict['name']}"]
    short_name = parameter_dict.get('options', {}).get('short_name')
    if short_name is not None:
        positional_args.append(f"-{short_name}")

    data_type = parameter_dict['data_type']

    keyword_args = {}
    if data_type is bool:
        keyword_args['action'] = 'store_true'
    else:
        keyword_args['action'] = 'store'
        keyword_args['choices'] = parameter_dict.get('choices')
        if data_type is list:
            keyword_args['type'] = str
        else:
            keyword_args['type'] = parameter_dict['data_type']

    keyword_args['help'] = parameter_dict['description']

    if not parameter_dict['required']:
        keyword_args['default'] = parameter_dict['default']
        if data_type is list:
            keyword_args['nargs'] = '*'
    else:
        keyword_args['required'] = True
        if data_type is list:
            keyword_args['nargs'] = '+'

    return positional_args, keyword_args
