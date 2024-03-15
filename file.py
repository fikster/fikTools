import csv
import json
from fikTools.log import get_log, get_warnings, fatal
import os
from os import listdir
from os.path import isfile, isdir, join
from shutil import copyfile
import re
import time
from pathlib import Path


def archive(source, destination, create_directory=False):
    if not exists(source):
        return

    root, extension = os.path.splitext(source)
    intermediate_file = '{}_{}{}'.format(root, time_of_last_update(source), extension)

    ignore, file = os.path.split(intermediate_file)
    final_file = os.path.join(destination, file)

    if create_directory and not exists(destination):
        mkdir(destination)

    # rename(source, intermediate_file)
    # rename(intermediate_file, final_file)
    move(source, final_file)


def copy(source, destination):
    return copyfile(source, destination)


def copy_dir(source, destination, substitutions={}):
    result = []

    log.message('copying {} to {}'.format(source, destination))

    mkdir(destination)

    for source_file in get_files(source):
        (root_dir, file) = os.path.split(source_file)

        # Manage the subdirectory
        subdir = root_dir.split('/')[-1]
        for entry in substitutions.keys():
            subdir = subdir.replace(entry, substitutions[entry])
        subdir = join(destination, subdir)
        mkdir(subdir)

        # Manage the file

        for entry in substitutions.keys():
            file = file.replace(entry, substitutions[entry])
        final_file = join(subdir, file)

        # Copy

        copy(source_file, final_file)

        result.append(final_file)

    return result


def delete(file):
    os.remove(file)


def exists(filename):
    return os.path.exists(filename)


def extract_directory_name(path):
    directory, ignore = os.path.split(path)

    return directory


def extract_file_name(path, without_extension=False):
    ignore, file = os.path.split(path)

    return file if without_extension is False else re.sub(r'\.[^.]+$', '', file)


def get_directories(directory, regexp='.*'):
    result = []

    pattern = re.compile(regexp)

    for file in [f for f in listdir(directory) if isdir(join(directory, f))]:

        match = pattern.match(file)

        if match is not None:
            # print(file)
            result.append(file)

    return list(map(lambda f: join(directory, f), result))


def get_files(directory, regexp='.*'):
    result = []

    pattern = re.compile(regexp)

    try:
        for file in [f for f in listdir(directory) if isfile(join(directory, f))]:

            match = pattern.match(file)

            if match is not None:
                result.append(file)

    except FileNotFoundError:
        result = []

    return list(map(lambda f: join(directory, f), result))


def get_files_and_directories(directory, regexp='.*', remove_directory=False):
    result = []

    pattern = re.compile(regexp)

    mkdir(directory)

    for file in [f for f in listdir(directory) if (isfile(join(directory, f)) or isdir(join(directory, f)))]:

        match = pattern.match(file)

        if match is not None:
            result.append(file)

    return result if remove_directory else list(map(lambda f: join(directory, f), result))


def get_files_recursively(directory, regexp='.*', file_names_only=False):
    # Get file names matching a pattern, across the directory and all its subdirectories
    result = []

    pattern = re.compile(regexp)

    # Add the files that match the pattern
    for file in [f for f in listdir(directory) if isfile(join(directory, f))]:

        match = pattern.match(file)

        if match is not None:
            result.append(file)

    # Parse the directories
    for dir in [f for f in listdir(directory) if isdir(join(directory, f))]:
        if file_names_only:
            result += get_files_recursively(join(directory, dir), regexp=regexp, file_names_only=file_names_only)
        else:
            result += list(map(lambda f: join(join(directory, dir), f), get_files_recursively(join(directory, dir), regexp=regexp, file_names_only=file_names_only)))

    return result


def get_numbered_file_name(directory, file, create_directories=False):

    if create_directories:
        mkdir(directory)

    filename, file_extension = os.path.splitext(file)
    file_extension = file_extension[1:]

    regexp_1 = '^' + filename + '_(.*)\\.' + file_extension
    regexp_2 = '^' + join(directory, filename) + '_(.*)\\.' + file_extension
    pattern = re.compile(regexp_2)

    counter = 0

    for f in get_files(directory, regexp=regexp_1):
        # log.debug('[' + f + '] vs [' + regexp_2 + ']', no_trace=True, file=__file__)
        match = pattern.match(f)  # match cannot be empty

        c = int(match[1])

        if counter < c:
            counter = c

    counter += 1

    return join(directory, filename + '_' + str(counter) + '.' + file_extension)


def is_directory(file):
    return isdir(file)


def is_file(file):
    return isfile(file)


def is_older(file, file_set, is_older_than_all=False, trace=False, verbose=False):

    # Will return true if the file is older than *any* file in the file set to compare with

    file_timestamp = time_of_last_update(file)

    if trace is True:
        print('File to compare is {} and its timestamp is {}'.format(
            file,
            str(file_timestamp)
        ))

    if isinstance(file_set, str):
        file_set = [file_set]

    count = 0

    for f in file_set:

        if trace is True:
            print('File from comparison set is {} and its timestamp {}'.format(
                f,
                str(time_of_last_update(f))
            ))

        if file_timestamp < time_of_last_update(f):
            count += 1

            if verbose is True:
                print('{} is older than {}'.format(file, f))

            if trace is True:
                print(' → is older')

            if is_older_than_all is False:
                return True

        if trace is True:
            print(' → is not older')

    if is_older_than_all is True and count == len(file_set):
        return True

    return False


def is_more_recent(file, file_set, is_more_recent_than_all=False, trace=False):
    # Will return true if the file is older than *any* file in the file set to compare with

    file_timestamp = time_of_last_update(file)

    if trace is True:
        print('File to compare is {} and its timestamp is {}'.format(
            file,
            str(file_timestamp)
        ))

    if isinstance(file_set, str):
        file_set = [file_set]

    count = 0

    for f in file_set:

        if trace is True:
            print('File from comparison set is {} and its timestamp {}'.format(
                f,
                str(time_of_last_update(f))
            ))

        if file_timestamp > time_of_last_update(f):
            count += 1

            if trace is True:
                print(' → is more recent')

            if is_more_recent_than_all is False:
                return True

        if trace is True:
            print(' → is not more recent')

    if is_more_recent_than_all is True and count == len(file_set):
        return True

    return False


def join(directory, filename=''):
    if isinstance(directory, str):
        return os.path.join(directory, filename)

    result = directory[0]
    for item in directory[1:]:
        result = os.path.join(result, item)
    return result


def load_csv_file(source_file):
    data = []

    with open(source_file, newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',', quotechar='"')

        for row in csv_data:
            data.append(row)

    return data


def load_json_file(source_file):
    with open(source_file) as source_data:
        try:
            return json.load(source_data)
        except json.decoder.JSONDecodeError:
            fatal('could not parse JSON file {}'.format(source_file))


def load_text_file(source_file):
    with open(source_file) as source_data:
        return source_data.readlines()


def mkdir(directory):
    if not exists(directory):
        return os.makedirs(directory)
    elif isdir(directory):
        return True
    else:
        return False


def move(source, destination):
    if isdir(destination):
        ignore, source_file = os.path.split(source)
        destination = os.path.join(destination, source_file)

    rename(source, destination)


def remove_dir_and_contents(directory):
    # Will not recursively remove directories, only files
    for file in get_files(directory):
        delete(file)

    rmdir(directory)


def rename(source, destination):
    os.rename(source, destination)


def rmdir(directory):
    os.rmdir(directory)


def touch(file, create=False):
    if not exists(file) and not create:
        return

    Path(file).touch()


def save_csv_file(target_file, data, create_directories=False):

    if create_directories:
        mkdir(os.path.dirname(target_file))

    with open(target_file, mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for element in data:
            writer.writerow(element)


def save_json_file(target_file, data, create_directories=False):

    if create_directories:
        mkdir(os.path.dirname(target_file))

    with open(target_file, 'w', encoding='utf-8') as target:
        json.dump(data, target, sort_keys=True, ensure_ascii=False, indent=4)


def save_log(directory='.', add_timestamps=False):
    text = []

    log_data = get_log()

    for ts in sorted(log_data.keys()):
        text.append('{}{}'.format(
            '{}: '.format(time.strftime('%Y-%0m-%0d %0H:%0M:%0S')) if add_timestamps else '',
            log_data[ts]
        ))

    file = get_numbered_file_name(directory=directory, file='log.txt', create_directories=True)
    save_text_file(file, '\n'.join(text))


def save_text_file(target_file, data, create_directories=False):

    if create_directories:
        mkdir(os.path.dirname(target_file))

    with open(target_file, 'w', encoding='utf-8') as target:
        target.write(data)


def save_warnings(directory='.'):
    warnings_file = join(directory, 'warnings.csv')
    warnings = {}
    flattened_warnings = []

    # Load existing warnings

    if exists(warnings_file):
        for line in load_csv_file(warnings_file):
            section = line[0]
            warning = line[1]
            if section not in warnings.keys():
                warnings[section] = []
            warnings[section].append(warning)

    # Get new set of warnings

    for section in get_warnings():
        warnings[section] = []  # This will automatically replace older versions of the section
        for warning in get_warnings(section):
            warnings[section].append(warning)

    for section in sorted(warnings.keys(), key=lambda x: '' if x is None else x):
        for warning in sorted(warnings[section]):
            flattened_warnings.append([section, warning])

    save_csv_file(warnings_file, flattened_warnings, create_directories=True)


def time_of_last_update(filename, check_directory_content=False):
    if check_directory_content:
        ts = time_of_last_update(filename, check_directory_content=False)
        if is_directory(filename):
            for file in (get_files(filename)):
                ts_2 = time_of_last_update(file, check_directory_content=check_directory_content)
                if ts_2 > ts:
                    ts = ts_2

        return ts

    if os.path.exists(filename):

        file = os.stat(filename)

        return file.st_mtime

    return 0
