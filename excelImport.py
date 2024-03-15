from config import get_config
from fikTools.file import save_csv_file, save_text_file, join, is_older, get_files, load_json_file, save_json_file, load_text_file
import fikTools.log
import os
import time


def get_table_info(wb, tab_name):
    ws = wb[tab_name]

    string = ws.cell(row=1, column=2).value

    log.debug('Processing tab {}: {}'.format(tab_name, string), trace_level='ref data import', file=__file__)

    top, bottom = string.split(':')

    return {
        'tab name': tab_name,
        'first row': int(top.split(',')[0]),
        'last row': int(bottom.split(',')[0]),
        'first column': int(top.split(',')[1]),
        'last column': int(bottom.split(',')[1]),
    }


def process_excel(wb, table_info, csv_file):

    ws = wb[table_info['tab name']]

    sheet_data = []

    log.debug('Sheet: {}, rows {} to {}, columns {} to {}'.format(table_info['tab name'], table_info['first row'], table_info['last row'], table_info['first column'], table_info['last column']), trace_level='ref data import', file=__file__)

    row_count = 0
    for row in ws.values:
        row_count += 1
        if row_count >= table_info['first row']:
            row_data = []
            column_count = 0
            for cell in row:
                column_count += 1
                if column_count >= table_info['first column']:
                    row_data.append(cell)
                if column_count > table_info['last column']:
                    break

            sheet_data.append(row_data)
            if row_count > table_info['last row']:
                break

    save_csv_file(csv_file, sheet_data)


def save_data_types(code, data):
    save_text_file(join(get_config('data_types_reference_directory'), '{}.txt'.format(code)), ':'.join(sorted(data)), create_directories=True)


def update_data_types():
    text_files = get_files(get_config('data_types_reference_directory'), r'.*\.txt')
    manually_managed_data_types_file = join(get_config('data_types_reference_directory'), '_base data types.json')
    data_types_file = join(get_config('load_first_reference_directory'), 'data types.json')

    if is_older(data_types_file, text_files + [manually_managed_data_types_file]):
        # log.message('loading data types file {}'.format(manually_managed_data_types_file), file=__file__)
        data_types = load_json_file(manually_managed_data_types_file)['data types']

        for file in text_files:
            ignore, file_name = os.path.split(file)
            code, ignore = os.path.splitext(file_name)

            type_data = load_text_file(file)
            # log.message('loading data types file {}'.format(file), file=__file__)

            if len(type_data) > 0:
                data_types[code] = {
                    'constraint': 'pick:{}'.format(type_data[0]),
                    'note': 'auto-generated',
                }

        save_json_file(data_types_file, {'data types': data_types}, create_directories=True)


def set_max_time(previous_set, new_set):
    # Check and set the time stamps

    max_time = 0

    for key in new_set.keys():
        for key_2 in new_set[key].keys():
            if key in previous_set.keys() and key_2 in previous_set[key]:
                if new_set[key][key_2]['value'] == previous_set[key][key_2]['value'] and new_set[key][key_2]['name'] == previous_set[key][key_2]['name']:
                    if 'ts' in previous_set[key][key_2].keys():
                        new_set[key][key_2]['ts'] = previous_set[key][key_2]['ts']
                    else:
                        new_set[key][key_2]['ts'] = time.time()
            else:
                new_set[key][key_2]['ts'] = time.time()

            if max_time < new_set[key][key_2]['ts']:
                max_time = new_set[key][key_2]['ts']

    return max_time


def set_max_time_2(previous_set, new_set):
    # Check and set the time stamps

    max_time = 0

    for key in new_set.keys():
        for key_2 in new_set[key].keys():
            for key_3 in new_set[key][key_2].keys():
                if key in previous_set.keys() and key_2 in previous_set[key] and key_3 in previous_set[key][key_2]:
                    if new_set[key][key_2][key_3]['value'] == previous_set[key][key_2][key_3]['value'] and new_set[key][key_2][key_3]['name'] == previous_set[key][key_2][key_3]['name']:
                        if 'ts' in previous_set[key][key_2][key_3].keys():
                            new_set[key][key_2][key_3]['ts'] = previous_set[key][key_2][key_3]['ts']
                        else:
                            new_set[key][key_2][key_3]['ts'] = time.time()
                else:
                    new_set[key][key_2][key_3]['ts'] = time.time()

                if max_time < new_set[key][key_2][key_3]['ts']:
                    max_time = new_set[key][key_2][key_3]['ts']

    return max_time
