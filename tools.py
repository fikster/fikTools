import re
import unicodedata

pattern = re.compile(r'(?<!^)(?=[A-Z])')

abilities = {
    'cha': 'charisma',
    'con': 'constitution',
    'dex': 'dexterity',
    'int': 'intelligence',
    'str': 'strength',
    'wis': 'wisdom',
}

numbers_as_string = {
    0: 'zero',
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
}

sizes = {
    'f': 'fine',
    'd': 'diminutive',
    't': 'tiny',
    's': 'small',
    'm': 'medium',
    'l': 'large',
    'h': 'huge',
    'g': 'gargantuan',
    'c': 'colossal',
}

training_levels = {
    'untrained': 0,
    'trained': 2,
    'expert': 4,
    'master': 6,
    'legendary': 8,
}


def ability_short_code_to_full_code(code):
    code = code.strip().lower()

    return code if code in abilities.values() else (abilities[code] if code in abilities.keys() else code)


def camel_case_to_capitalised(name):
    return pattern.sub(' ', name).title()


def camel_case_to_snake_case(name):
    return pattern.sub('_', name).lower()


def capitalise_words(string):
    for w in string.lower().split(' '):

        for w2 in w.split('\n'):
            w2 = w2.translate(
                str.maketrans('', '', ',.;:…!?@#$\'"“”″+()[]{}0123456789')
            )  # - , ’ and ’ are considered valid values

    return string


def code_to_name(string):
    return string.title() \
        .replace("'S", "'s") \
        .replace(' A ', ' a ') \
        .replace(' Ac ', ' AC') \
        .replace('Ac ', 'AC ') \
        .replace(' An ', ' an ') \
        .replace(' At ', ' at ') \
        .replace('Dc', 'DC') \
        .replace('Dmg', 'dmg') \
        .replace('Hd', 'HD') \
        .replace('Hp', 'HP') \
        .replace(' Ii ', ' II ') \
        .replace(' Iii ', ' III ') \
        .replace(' Is ', ' is ') \
        .replace(' Iv ', ' IV ') \
        .replace(' Of ', ' of ') \
        .replace(' The ', ' the ') \
        .replace(' Vs ', ' vs. ') \
        .replace(' Vs.', ' vs. ')


def get_abilities():
    return sorted(abilities.values())


def get_next_training_level(level):
    level = level.lower()

    if level == 'untrained':
        return 'trained'
    elif level == 'trained':
        return 'expert'
    elif level == 'expert':
        return 'master'
    elif level == 'master':
        return 'legendary'
    else:
        return level


def get_sizes():
    return sorted(sizes.values())


def get_training_bonus(level):
    level = level.lower()

    return training_levels[level] if level in training_levels.keys() else 0


def indexed_code(prefix, index, suffix='', size=2):
    template = '{{}} {{:0{}d}}{{}}'.format(size)
    try:
        return template.format(prefix, int(index), ' {}'.format(suffix) if suffix != '' else '')
    except ValueError:
        return '{} {}{}'.format(prefix, index, ' {}'.format(suffix) if suffix != '' else '')


def is_better_training(candidate, reference):
    candidate_bonus = get_training_bonus(candidate)
    reference_bonus = get_training_bonus(reference)

    return candidate_bonus > reference_bonus


def name_to_code(string):
    return string.strip().lower() \
        .replace("'", '') \
        .replace(' / ', ' ') \
        .replace('(', '') \
        .replace(')', '') \
        .replace(',', '') \
        .replace(' - ', '') \
        .replace(' -', '') \
        .replace('- ', '') \
        .replace('.', '') \
        .replace('â', 'a') \
        .replace("’", '')


def number_to_string(number):
    try:
        return '{}{}'.format('+' if int(number) >= 0 else '', number)
    except TypeError:
        return ''
    except ValueError:
        return ''


def number_to_number_as_string(number):
    try:
        number = int(number)
        return numbers_as_string[number] if number in numbers_as_string.keys() else str(number)
    except ValueError:
        return str(number)


def percent_encode_url(url):
    return url \
        .replace('%', '%25') \
        .replace(' ', '%20') \
        .replace('!', '%21') \
        .replace('#', '%23') \
        .replace('$', '%24') \
        .replace('&', '%26') \
        .replace("'", '%27') \
        .replace('(', '%28') \
        .replace(')', '%29') \
        .replace('*', '%2A') \
        .replace('+', '%2B') \
        .replace(',', '%2C') \
        .replace('/', '%2F') \
        .replace(':', '%3A') \
        .replace(';', '%3B') \
        .replace('=', '%3D') \
        .replace('?', '%3F') \
        .replace('@', '%40') \
        .replace('[', '%5B') \
        .replace(']', '%5D') \


def replace_none_with_empty_string(array):
    result = []
    for item in array:
        result.append('' if item is None else item)

    return result


def size_short_code_to_full_code(code):
    code = code.strip().lower()

    return code if code in sizes.values() else sizes[code]


def snake_case_to_camel_case(name):
    return ''.join(word.title() for word in name.split('_'))


def snake_case_to_capitalised(name):
    return ' '.join(word.title() for word in name.split('_'))


def strip_accents(text):
    text = unicodedata.normalize('NFD', text) \
        .encode('ascii', 'ignore') \
        .decode('utf-8')

    return str(text)


def string_to_wiki_code(name, replace_dashes=False):
    result = camel_case_to_capitalised(
        strip_accents(name).replace("'", '')
            .replace('’', '')
            .replace('“', '')
            .replace('”', '')
            .replace(',', '')
            .replace('(', ' ')
            .replace('?', '')
    ) \
        .replace(')', '') \
        .replace(' ', '') \
        .replace('/', '')

    if replace_dashes:
        result = result.replace('-', '')

    # print('{} -> {}'.format(name, result))

    return result


def ticks_string(tick_symbol, full_length, separator_frequency=None):
    result = ''

    c = 0
    for i in range(0, full_length):
        if separator_frequency is not None and c == separator_frequency:
            result += ' '
            c = 0
        result += tick_symbol
        c += 1

    return result


def title(string):
    return string.title() \
        .replace('’S', '’s') \
        .replace('1St', '1st') \
        .replace('2Nd', '2nd') \
        .replace('3Rd', '3rd') \
        .replace('4Th', '4th') \
        .replace('5Th', '5th') \
        .replace('6Th', '6th') \
        .replace('7Th', '7th') \
        .replace('8Th', '8th') \
        .replace('9Th', '9th') \
        .replace('Ère', 'ère') \
        .replace('Ème', 'ème') \
        .replace('(S)', '(s)')


def truncate_long_string(string, max_size):
    return string if len(string) < int(max_size) else '{}(…)'.format(string[0:max_size])


def update_structure(current, latest):
    changed = False

    # for item in latest:
    # 	print('1A')
    # 	print(item)
    # 	print(type(item))
    # 	print('1B')
    # 	if item not in current:
    # 		changed = True
    # 		current[item] = latest[item]
    # 	else:
    # 		for item_2 in latest[item]:
    # 			print('2A')
    # 			print(item_2)
    # 			print(type(item_2))
    # 			print('2B')
    # 			if item_2 not in current[item]:
    # 				if isinstance(item_2, (str)):
    # 					changed = True
    # 					current[item][item_2] = latest[item][item_2]

    for item in latest:
        # print('Found item of type ' + str(type(item)) + ':')
        print(item)

        if item not in current:
            print(item + 'is not present')
            changed = True
            if isinstance(item, str):
                current[item] = latest[item]
            elif isinstance(item, dict):
                changed &= update_structure(current[item], latest[item])
            else:
                print('Found [' + str(item) + '] with unrecognised type [' + str(type(item)) + ']')

    return changed
