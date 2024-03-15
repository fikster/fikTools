from config import get_config
from file import get_files, load_text_file, save_json_file, join
import json
import re
import refData
from tools import code_to_name, name_to_code


_calc_detail = {
    'default': {
        'value': 0,
        'detail': '',
    },
}


def set_calc(value, detail, section='default'):

    global _calc_detail

    if section not in _calc_detail.keys():
        _calc_detail[section] = {}

    _calc_detail[section]['value'] = value
    _calc_detail[section]['detail'] = '{} ({})'.format(value, detail)


def add_calc(value, detail, section='default'):
    _calc_detail[section]['value'] += value
    _calc_detail[section]['detail'] += ' {} {} ({})'.format('+' if value >= 0 else '-', abs(value), detail)


def get_calc(section='default'):

    _calc_detail[section]['detail'] += ' = {}'.format(_calc_detail[section]['value'])

    return _calc_detail[section]['value'], _calc_detail[section]['detail']


def has_talent(character_data, talent, addendum=''):
    return '|{}!{}|'.format(talent.lower(), addendum.lower()) in refData.get_value(character_data, 'talents', 'all talents')


def get_talent_addendum(character_data, talent):  # This function is not efficient! Shouldn't call it often
    for key in refData.get_value(character_data, 'talents', 'all talents').split('|'):
        if key.startswith('{}!'.format(talent)):
            return get_talent_components(key)[1]

    return ''


def add_to_talent_list(character_data, talent, addendum=''):
    final_code = '!'.join([name_to_code(talent), name_to_code(addendum)])

    if '|{}|'.format(final_code) not in refData.get_value(character_data, 'talents', 'all talents'):
        refData.update_value(
            character_data,
            'talents',
            'all talents',
            '{}{}|'.format(
                refData.get_value(character_data, 'talents', 'all talents'),
                final_code,
            ),
        )


def has_equipment(character_data, equipment_code):
    return '|{}|'.format(equipment_code.lower()) in refData.get_value(character_data, 'base', 'all equipment')


def build_talent_code(code, override, addendum):
    return '!'.join([override if override != '' else code, addendum])


def get_talent_components(code):
    result = code.split('!')

    return result[0], result[1]  # code, addendum


def build_talent_name(code, override, addendum):
    name = refData.get_value(refData.get('talents'), code if override == '' else override, 'name')
    return '{}{}'.format(
        code_to_name(name) if name != '' else '{} (unrecognised talent)'.format(code_to_name(code if override == '' else override)),
        ' ({})'.format(str(addendum).title()) if addendum != '' else '',
    )


def update_stacking_talent(name, count):
    re_match = re.search('^(.*)\{\{(.+)\}\}(.*)$', name)
    if re_match is not None:
        start = re_match.group(1)
        variable = re_match.group(2)
        end = re_match.group(3)

        try:
            s = variable.split('/')
            numerator = float(s[0])
            denominator = float(s[1])
        except IndexError:
            numerator = float(variable)
            denominator = 1.0

        variable = int((float(count) * numerator) / denominator)

        name = '{}{}{}'.format(start, variable, end)

    re_match = re.search('^(.*)\{(.+)\}(.*)$', name)
    if re_match is not None:
        start = re_match.group(1)
        variable = re_match.group(2)
        end = re_match.group(3)

        try:
            s = variable.split('/')
            numerator = float(s[0])
            denominator = float(s[1])
        except IndexError:
            numerator = float(variable)
            denominator = 1.0

        variable = int((float(count) * numerator) / denominator)

        name = '{}{}{}'.format(start, variable, end)

    return name


def build_calculation_dependencies():

    return

    # Step 1: extract the input an output details from the calculation source files

    parsing_input = True  # Assume the first data is input
    input = []
    output = []
    raw_dependencies = {}
    dependencies = {}
    result = {}

    for file in get_files(get_config('python_calculation_scripts_directory'), regexp=get_config('python_calculation_scripts_files')):
        source = load_text_file(file)
        for line in source:
            re_match = re.search('# token (in|out)put: (.+)\|(.+)$', line.lower())
            if re_match is not None:
                kind = re_match.group(1)
                section = re_match.group(2).replace('*', '.+')
                code = re_match.group(3).replace('*', '.+')

                if kind == 'in':
                    if not parsing_input:  # We just finished parsing output - save that data and reset
                        # Save previous results
                        for o in output:
                            raw_dependencies[o] = []
                            for i in input:
                                raw_dependencies[o].append(i)
                        # Reset input and output
                        input = []
                        output = []
                        parsing_input = True
                    input.append('{}:{}'.format(section, code))
                else:  # Parsing output
                    parsing_input = False
                    output.append('{}:{}'.format(section, code))
                # Final processing
                for o in output:
                    raw_dependencies[o] = []
                    for i in input:
                        raw_dependencies[o].append(i)

    # print(json.dumps(raw_dependencies, indent=4, sort_keys=True))

    # Step 2: for each output item without a number, assign a starting number, and assign a lower number to all its input entries

    for entry in raw_dependencies.keys():
        add_dependency(entry, 1, raw_dependencies, dependencies)

    # print(json.dumps(dependencies, indent=4, sort_keys=True))

    for entry in dependencies.keys():
        if dependencies[entry] not in result.keys():
            result[dependencies[entry]] = []
        result[dependencies[entry]].append(entry)

    for entry in result.keys():
        result[entry] = sorted(result[entry])

    print(json.dumps(result, indent=4, sort_keys=True))

    save_json_file(join(get_config('base_reference_directory'), '{}.json'.format('calculated character elements')), {'dependency tree': result})

    exit()


def add_dependency(value, number, raw_dict, dep_dict):

    # TODO: if we change the ranking of an entry, all its up-dependencies need to be updated recursively
    # Might want to expand all wildcards - maybe replace with codes, e.g. [abilities], [skills]
    # Then want to tie the tree entries to the functions where they're calculated - noting that each
    # function should really only be called once, at the proper stage
    if value in dep_dict.keys():  # If the value is already accounted for, check whether it should be bumped further up the tree
        if dep_dict[value] > number:
            dep_dict[value] = number
        number = dep_dict[value]
    else:  # Do a wildcard lookup
        found_match = False
        for candidate in dep_dict.keys():
            re_match = re.search(candidate, value)
            if re_match is not None:
                found_match = True
                if dep_dict[candidate] > number:
                    dep_dict[candidate] = number
                number = dep_dict[candidate]

        if not found_match:
            dep_dict[value] = number

    # Process dependencies

    if value in raw_dict.keys():
        for entry in raw_dict[value]:
            add_dependency(entry, number - 1, raw_dict, dep_dict)
