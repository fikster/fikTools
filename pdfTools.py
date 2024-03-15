import fikTools.color
from fikTools.file import join as fk_join
import fikTools.log
from config import get_config
import fikTools.imageTools
import fikTools.pdf

# ReportLab

from reportlab.platypus import Image

_image_sizes = {
    'base': {
        'master directory': get_config('images directory'),
        'master image type': 'png',

        'pdf directory': get_config('images directory'),
        'pdf image type': 'png',
        'pdf image width': 350,
    },
}


def init():
    font_sizes = fikTools.file.load_json_file(fk_join(get_config('settings directory'), 'font_sizes.json'))['data']

    fonts_list = fikTools.file.load_json_file(fk_join(get_config('settings directory'), 'fonts.json'))['data']

    styles = fikTools.file.load_json_file(fk_join(get_config('settings directory'), 'styles.json'))['data']

    fonts_directory = get_config('fonts directory')

    fikTools.pdf.init(font_sizes=font_sizes, fonts_list=fonts_list, fonts_directory=fonts_directory, styles=styles, leading=1.2, space_before=0, space_after=0.6)


def get_image_kinds():
    return _image_sizes.keys()


def get_image_size_parameters(category, code):
    return _image_sizes[category][code]


def get_image(stub, image_name, width, kind='master'):
    image = Image(get_image_location(
        stub,
        image_name,
        kind
    ), lazy=2)

    # h = image.drawHeight
    w = image.drawWidth

    image.drawWidth = width
    image.drawHeight *= image.drawWidth / w

    return image


def prep_images():
    for code in _image_sizes.keys():

        fikTools.file.mkdir(_image_sizes[code]['master directory'])

        for stub in ['master', 'pdf']:
            key = '{}_directory'.format(stub)
            if key in _image_sizes[code].keys():
                fikTools.file.mkdir(_image_sizes[code][key])

        for source_file in fikTools.file.get_files(_image_sizes[code]['master directory'], regexp='^.*\.{}$'.format(_image_sizes[code]['master_image_type'])):
            for stub in ['pdf']:
                key = '{} directory'.format(stub)
                if key not in _image_sizes[code].keys():
                    continue

                target_file = fikTools.file.join(_image_sizes[code][key], fikTools.file.extract_file_name(source_file)).replace('.{}'.format(_image_sizes[code]['master image type']), '.{}'.format(_image_sizes[code]['{} image type'.format(stub)]))

                if fikTools.file.is_older(target_file, [source_file]):
                    fikTools.imageTools.resize_image(source_file, target_file, _image_sizes[code]['{} image width'.format(stub)])


def get_image_file_list(category, kind='master'):
    return fikTools.file.get_files(
        _image_sizes[category]['{} directory'.format(kind)],
        regexp='^.*\.{}$'.format(_image_sizes[category]['{} image type'.format(kind)])
    )


def get_image_list(category, kind='master'):
    return list(map(
        lambda f: fikTools.file.extract_file_name(f).replace(
            '.{}'.format(_image_sizes[category]['{} image type'.format(kind)]),
            ''
        ),
        get_image_file_list(category, kind)
    ))


def get_image_location(category, image, kind='master'):
    extension = _image_sizes[category]['{} image type'.format(kind)]

    return fikTools.file.join(
        _image_sizes[category]['{} directory'.format(kind)],
        '{}.{}'.format(image, extension)
    )
