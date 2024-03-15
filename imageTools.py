import PIL
import os


_colour = {
    'black': [0, 0, 0],
    'white': [1, 1, 1],
    'dark grey': [.23, .23, .23],
    'light grey': [.83, .83, .83],
    'dark red': [.56, .33, .23],
    'dark yellow': [.82, .63, .35],
    'light red': [.81, .74, .71],
    'red': [1., 0., 0.],
    'green': [0., 1., 0.],
    'blue': [0., 0., 1.],
    'yellow': [1., 1., 0.],
    'cyan': [0., 1., 1.],
    'magenta': [1., 0., 1.]
}


def set_colour(c, colour, kind='fill'):

    if colour is None:
        return

    if isinstance(colour, str):
        if colour not in _colour.keys():
            return

        colour = _colour[colour]

    if kind == 'fill':
        c.setFillColorRGB(colour[0], colour[1], colour[2])
    elif kind == 'stroke':
        c.setStrokeColorRGB(colour[0], colour[1], colour[2])


def draw_line(c, x_0, y_0, x_1, y_1, width=None, colour=None):

    _set_parameters(c, width, colour)

    p = c.beginPath()

    p.moveTo(x_0, y_0)

    p.lineTo(x_1, y_1)

    p.close()

    c.drawPath(p)


def _set_parameters(c, stroke_width=None, stroke_colour=None, fill_colour=None):
    if stroke_colour is not None:
        set_colour(c, stroke_colour, kind='stroke')

    if fill_colour is not None:
        set_colour(c, fill_colour, kind='fill')

    if stroke_width is not None:
        c.setLineWidth(stroke_width)


def draw_circle(c, x, y, radius, stroke=0, stroke_width=None, stroke_colour=None, fill=1, fill_colour=None):

    _set_parameters(c, stroke_width, stroke_colour, fill_colour)

    c.circle(
        x,
        y,
        radius
    )


def draw_string(c, x, y, string, colour=None, centered=False):

    _set_parameters(c, None, None, colour)

    if centered is True:
        c.drawCentredString(x, y, string)
    else:
        c.drawString(x, y, string)


def draw_rectangle(c, x, y, width, height, stroke=0, stroke_width=None, stroke_colour=None, fill=1, fill_colour=None,
                   radius=None):

    _set_parameters(c, stroke_width, stroke_colour, fill_colour)

    if radius is None:
        c.rect(x, y, width, height, stroke=stroke, fill=fill)
    else:
        c.roundRect(x, y, width, height, radius=radius, stroke=stroke, fill=fill)


def resize_image(source_file, target_file, width):
    d, f = os.path.split(source_file)

    image = PIL.Image.open(source_file)

    (w, h) = image.size

    new_w = int(width)
    new_h = int(h * width / w)

    try:

        transparency_removed = PIL.Image.new('RGB', image.size, (255, 255, 255))

        transparency_removed.paste(image, image)

    except:

        transparency_removed = image

    if width > 0:
        transparency_removed.convert('RGB').resize((new_w, new_h)).save(target_file)
    else:
        transparency_removed.convert('RGB').save(target_file)
