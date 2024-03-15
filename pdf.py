import fikTools.color as color
import copy
import fikTools.log as log
from fikTools.file import join as fk_join

# ReportLab

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import PageBreak
from reportlab.platypus import PageTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus.tableofcontents import TableOfContents

# Fonts

import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Styles

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle as PS

reportlab.rl_config.warnOnMissingFontGlyphs = 0

# Default values

_default_font_size = 10

_default_background = '#ffffff'
_default_foreground = '#000000'


# Configuration

_alignment = {
    'default': TA_LEFT,

    'centre': TA_CENTER,
    'justify': TA_JUSTIFY,
    'left': TA_LEFT,
    'right': TA_RIGHT,
}

_color = {
    # For some reason in the below using the 'color.' values does not work
    # Reportlab accepts the value, but sets the background to white

    'default': '#000000',  # color.BLACK,

    'black': '#000000',  # color.BLACK,
    'blue': '#0000ff',  # color.BLUE,
    'green': '#00ff00',  # color.GREEN,
    'grey1': '#555555',  # color.RGB(85, 85, 85),  # #555555
    'grey2': '#cccccc',  # color.GRAY80, # 204 (#cccccc)
    'grey3': '#eeeeee',  # color.RGB(238, 238, 238),  # #eeeeee
    'red': '#ff0000',  # color.RED,
    'white': '#ffffff',  # color.WHITE,
    'yellow': '#ffff00',  # color.YELLOW,
}

_font_sizes = {}

_styles = {}

_document_sizes = {
    'A1': {
        'doc_width': 59.4 * cm,
        'doc_height': 84.1 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A1L': {
        'doc_width': 84.1 * cm,
        'doc_height': 59.4 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A2': {
        'doc_width': 42 * cm,
        'doc_height': 59.4 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A2L': {
        'doc_width': 59.4 * cm,
        'doc_height': 42 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A3': {
        'doc_width': 29.7 * cm,
        'doc_height': 42 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A3L': {
        'doc_width': 42 * cm,
        'doc_height': 29.7 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A4': {
        'doc_width': 21 * cm,
        'doc_height': 29.7 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A4L': {
        'doc_width': 29.7 * cm,
        'doc_height': 21 * cm,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'A5': {
        'doc_width': 14.8 * cm,
        'doc_height': 21 * cm,
        'top_margin': 1 * cm,
        'bottom_margin': 1 * cm,
        'left_margin': 1 * cm,
        'right_margin': 1 * cm,
    },
    'A6': {
        'doc_width': 10.5 * cm,
        'doc_height': 14.8 * cm,
        'top_margin': 1 * cm,
        'bottom_margin': 1 * cm,
        'left_margin': 1 * cm,
        'right_margin': 1 * cm,
    },
    'A6L': {
        'doc_width': 14.8 * cm,
        'doc_height': 10.5 * cm,
        'top_margin': 1 * cm,
        'bottom_margin': 1 * cm,
        'left_margin': 1 * cm,
        'right_margin': 1 * cm,
    },
    'A7': {
        'doc_width': 7.4 * cm,
        'doc_height': 10.5 * cm,
        'top_margin': 1 * cm,
        'bottom_margin': 1 * cm,
        'left_margin': 1 * cm,
        'right_margin': 1 * cm,
    },
    'US Letter': {
        'doc_width': 8 * inch,
        'doc_height': 11 * inch,
        'top_margin': 1.5 * cm,
        'bottom_margin': 1.5 * cm,
        'left_margin': 1.5 * cm,
        'right_margin': 1.5 * cm,
    },
    'Playing Card': {
        'doc_width': 6.2 * cm,
        'doc_height': 8.8 * cm,
        'top_margin': 0.1 * cm,
        'bottom_margin': 0.1 * cm,
        'left_margin': 0.2 * cm,
        'right_margin': 0.2 * cm,
    }
}

_init_done = False


class DocTemplateAllowingToC(BaseDocTemplate):

    def __init__(self, filename, page_size_code, number_pages, background_image, background_text, styles_for_toc, **kw):

        self.allowSplitting = 0

        self.page_size_code = page_size_code

        self.number_pages = number_pages

        self.background_image = background_image

        self.background_text = background_text

        self.styles_for_toc = {}

        for item in styles_for_toc:
            self.styles_for_toc[item[0]] = item[1]

        BaseDocTemplate.__init__(self, filename, **kw)

        # See https://code.activestate.com/recipes/123612-basedoctemplate-with-2-pagetemplate/

        page_template = PageTemplate(
            id='default',
            frames=[Frame(_document_sizes[page_size_code]['left_margin'], _document_sizes[page_size_code]['top_margin'], _document_sizes[page_size_code]['frame_width'], _document_sizes[page_size_code]['frame_height'], id='frame_1')],
            onPage=_set_canvas_background,
            onPageEnd=_set_canvas_foreground
        )

        self.addPageTemplates(page_template)

    def afterFlowable(self, flowable):

        # Registers TOC entries

        if flowable.__class__.__name__ == 'Paragraph':

            text = flowable.getPlainText()
            style = flowable.style.name

            if text.lower() not in ['', 'contents'] and style.lower() in self.styles_for_toc.keys():
                self.notify('TOCEntry', (self.styles_for_toc[style], text, self.page))


class DocTemplateWithoutToC(BaseDocTemplate):

    def __init__(self, filename, page_size_code, number_pages, background_image, background_text, **kw):
        self.allowSplitting = 0

        self.page_size_code = page_size_code

        self.number_pages = number_pages

        self.background_image = background_image

        self.background_text = background_text

        BaseDocTemplate.__init__(self, filename, **kw)

        # See https://code.activestate.com/recipes/123612-basedoctemplate-with-2-pagetemplate/

        page_template = PageTemplate(
            id='default',
            frames=[Frame(_document_sizes[page_size_code]['left_margin'], _document_sizes[page_size_code]['top_margin'], _document_sizes[page_size_code]['frame_width'], _document_sizes[page_size_code]['frame_height'], id='frame_1')],
            onPage=_set_canvas_background,
            onPageEnd=_set_canvas_foreground
        )

        self.addPageTemplates(page_template)


def _set_canvas_background(canvas, doc):
    if doc.number_pages and doc.page > 1:
        canvas.saveState()

        canvas.setFont('Default', 10)

        canvas.drawRightString(_document_sizes[doc.page_size_code]['page_x'], _document_sizes[doc.page_size_code]['page_y'], '%d' % (doc.page))

        canvas.restoreState()

    if doc.background_image is not None:
        canvas.drawImage(doc.background_image, 0, 0, width=_document_sizes[doc.page_size_code]['doc_width'], height=_document_sizes[doc.page_size_code]['doc_height'], mask=None)


def _set_canvas_foreground(canvas, doc):

    if doc.background_text is not None:

        canvas.saveState()

        canvas.setFillColor(doc.background_text['colour'] if 'colour' in doc.background_text.keys() else _color['red'])

        canvas.setFont('Default', doc.background_text['size'] if 'size' in doc.background_text.keys() else 74)

        canvas.rotate(45)

        canvas.drawCentredString(
            1.414 * _document_sizes[doc.page_size_code]['centre_x'],
            0,  # _document_sizes[doc.page_size_code]['centre_y'],
            doc.background_text['text'] if 'text' in doc.background_text.keys() else '(no text provided)'
        )

        canvas.restoreState()


def _init_document_sizes():
    original_document_sizes = copy.deepcopy(list(_document_sizes.keys()))

    for page_size in original_document_sizes:
        _document_sizes['{} portrait'.format(page_size)] = copy.deepcopy(_document_sizes[page_size])
        _document_sizes['{}P'.format(page_size)] = copy.deepcopy(_document_sizes[page_size])

        _document_sizes['{} landscape'.format(page_size)] = {
        'doc_width': _document_sizes[page_size]['doc_height'],
        'doc_height': _document_sizes[page_size]['doc_width'],
        'top_margin': _document_sizes[page_size]['left_margin'],
        'bottom_margin': _document_sizes[page_size]['right_margin'],
        'left_margin': _document_sizes[page_size]['bottom_margin'],
        'right_margin': _document_sizes[page_size]['top_margin'],
        }

        _document_sizes['{}L'.format(page_size)] = copy.deepcopy(_document_sizes['{} landscape'.format(page_size)])

    for page_size in _document_sizes.keys():
        _document_sizes[page_size]['frame_width'] = _document_sizes[page_size]['doc_width'] - _document_sizes[page_size]['left_margin'] - _document_sizes[page_size]['right_margin']
        _document_sizes[page_size]['frame_height'] = _document_sizes[page_size]['doc_height'] - _document_sizes[page_size]['top_margin'] - _document_sizes[page_size]['bottom_margin']

        _document_sizes[page_size]['page_x'] = _document_sizes[page_size]['doc_width'] / 2
        _document_sizes[page_size]['page_y'] = (_document_sizes[page_size]['bottom_margin'] / 2)

        _document_sizes[page_size]['centre_x'] = _document_sizes[page_size]['doc_width'] / 2
        _document_sizes[page_size]['centre_y'] = (_document_sizes[page_size]['doc_height'] / 2)


def _init_fonts(fonts_list, fonts_directory):
    # reportlab.rl_config.TTFSearchPath.append(get_config('fonts directory'))

    if 'Default' not in fonts_list.keys():
        fonts_list['Default'] = {
            '': 'Times New Roman.ttf',
            'Bold': 'Times New Roman Bold.ttf',
            'BoldItalic': 'Times New Roman Bold Italic.ttf',
            'Italic': 'Times New Roman Italic.ttf'
        }

    for font in fonts_list.keys():
        for font_type in fonts_list[font].keys():
            pdfmetrics.registerFont(TTFont('{}{}'.format(font, font_type), fk_join(fonts_directory, fonts_list[font][font_type])))
            # pdfmetrics.registerFont(TTFont('{}{}'.format(font, font_type), font_list[font][font_type]))

        registerFontFamily(font, normal=font, bold='{}Bold'.format(font), italic='{}Italic'.format(font), boldItalic='{}BoldItalic'.format(font))


def _init_styles(leading=1.2, space_before=0, space_after=0.3):
    global _font_sizes
    global _styles

    for category in _styles.keys():
        for key in _styles[category].keys():
            style = _styles[category][key]

            style['alignment'] = _alignment['default'] if 'alignment' not in style.keys() else _alignment[style['alignment']]

            if 'allowOrphans' not in style.keys():
                style['allowOrphans'] = True

            if 'allowWidows' not in style.keys():
                style['allowWidows'] = True

            if 'leftIndent' not in style.keys():
                style['leftIndent'] = 0

            style['background'] = color.WHITE if 'background' not in style.keys() else _color[style['background']]

            if 'font' not in style.keys():
                style['font'] = 'Regular'

            if 'fontsize' not in style.keys():
                style['fontsize'] = _font_sizes['']

            style['foreground'] = color.BLACK if 'foreground' not in style.keys() else _color[style['foreground']]

            style['leading'] = style['fontsize'] * (style['leading'] if 'leading' in style.keys() else leading)

            style['spaceBefore'] = style['fontsize'] * (style['spaceBefore'] if 'spaceBefore' in style.keys() else space_before)

            style['spaceAfter'] = style['fontsize'] * (style['spaceAfter'] if 'spaceAfter' in style.keys() else space_after)

            style['name_for_toc'] = style['name_for_toc'] if 'name_for_toc' in style.keys() else key


def init(font_sizes, fonts_list, fonts_directory, styles, leading, space_before, space_after):
    global _init_done
    global _font_sizes
    global _styles

    if _init_done:
        return

    # font_sizes is a basic dictionary, key is a descriptive string and value is a number (the size of the font)

    _font_sizes = copy.deepcopy(font_sizes)

    _init_fonts(fonts_list=fonts_list, fonts_directory=fonts_directory)

    # styles is a dictionary of dictionaries (categories then style entries), where the following style elements can be defined:
    # alignment, allowOrphans, allowWidows, background, firstLineIndent,
    # font, fontsize, foreground, leading, leftIndent, spaceAfter, spaceBefore

    _styles = copy.deepcopy(styles)

    _init_styles(leading=leading, space_before=space_before, space_after=space_after)

    _init_document_sizes()

    _init_done = True


def bolded(string):
    return '<b>{}</b>'.format(string)


def build_pdf(target_file, story, page_size, title='', subtitle='', styles_for_toc=[], toc_title_style=None, create_toc=True, toc_title='Contents', number_pages=True, background_image=None, background_text=None):
    check_init()

    full_story = []

    if title != '':
        title_page(story=full_story, title=title, subtitle=subtitle, page_break_before=False, page_break_after=True, page_size=page_size)

    if create_toc:

        if toc_title_style is None:
            toc_title_style = get_style('h1')

        document = DocTemplateAllowingToC(
            filename=target_file,
            page_size_code=page_size,
            number_pages=number_pages,
            background_text=background_text,
            background_image=background_image,
            styles_for_toc=styles_for_toc,
            pagesize=(_document_sizes[page_size]['doc_width'], _document_sizes[page_size]['doc_height']),
            leftMargin=_document_sizes[page_size]['left_margin'],
            rightMargin=_document_sizes[page_size]['right_margin'],
            topMargin=_document_sizes[page_size]['top_margin'],
            bottomMargin=_document_sizes[page_size]['bottom_margin']
        )

        toc = TableOfContents()

        toc.levelStyles = [
            get_style(preset='level1', preset_category='table_of_contents'),
            get_style(preset='level2', preset_category='table_of_contents'),
            get_style(preset='level3', preset_category='table_of_contents'),
            get_style(preset='level4', preset_category='table_of_contents'),
        ]

        full_story.append(Paragraph(toc_title, toc_title_style))

        full_story.append(toc)

        full_story.append(PageBreak())

    else:
        document = DocTemplateWithoutToC(
            filename=target_file,
            page_size_code=page_size,
            number_pages=number_pages,
            background_text=background_text,
            background_image=background_image,
            pagesize=(_document_sizes[page_size]['doc_width'], _document_sizes[page_size]['doc_height']),
            leftMargin=_document_sizes[page_size]['left_margin'],
            rightMargin=_document_sizes[page_size]['right_margin'],
            topMargin=_document_sizes[page_size]['top_margin'],
            bottomMargin=_document_sizes[page_size]['bottom_margin']
        )

    for item in story:
        full_story.append(item)

    try:
        document.multiBuild(full_story, canvasmaker=canvas.Canvas)

    except ValueError as exception:
        log.warning('could not generate file {}'.format(target_file))
        log.dump_traceback(exception)


def check_init():
    global _init_done

    if not _init_done:
        raise Exception ('pdf.init() has not been called')


def default_table_style(padding=2, box=False, grid=False):
    table_style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), padding),
        ('RIGHTPADDING', (0, 0), (-1, -1), padding),
        ('TOPPADDING', (0, 0), (-1, -1), padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
    ]

    if box:
        table_style.append(('BOX', (0, 0), (-1, -1), 0.5, color.BLACK))

    if grid:
        table_style.append(('GRID', (0, 0), (-1, -1), 0.5, color.BLACK))

    return table_style


def get_document_setting(setting, page_size):
    check_init()

    return _document_sizes[page_size][setting.lower()]


def get_font_size(size):
    global _font_sizes
    global _default_font_size

    return _font_sizes[size] if size in _font_sizes.keys() else (_font_sizes[''] if '' in _font_sizes.keys() else _default_font_size)


def get_style(preset='', preset_category='default', size=None, bold=None, italics=None, foreground=None, background=None, alignment=None):
    global _alignment
    global _font_sizes
    global _styles

    if preset == '':

        return PS(
            name='style',
            alignment=_alignment[alignment if alignment is not None else ''],
            allowOrphans=True,
            allowWidows=True,
            backColor=_default_background if background is None else background,
            fontName='{}{}{}'.format(
                'Default',
                'Bold' if (bold is not None and bold) else '',
                'Italic' if (italics is not None and italics) else ''
            ),
            fontSize=_font_sizes[size if size is not None else ''],
            leading=_font_sizes[size if size is not None else ''] * 1.2,
            spaceAfter=_font_sizes[size if size is not None else ''] * 0.6,
            spaceBefore=_font_sizes[size if size is not None else ''] * 0,
            textColor=_default_foreground if foreground is None else foreground
        )

    else:
        if preset_category not in _styles.keys():
            raise Exception ('Unknown category [{}]'.format(preset_category))

        if preset not in _styles[preset_category].keys():
            if 'default' in _styles.keys() and preset in _styles['default'].keys():
                preset_category = 'default'
            else:
                raise Exception ('Unknown style preset [{}] for category [{}]'.format(preset, preset_category))

        font = _styles[preset_category][preset]['font']

        if bold is not None:
            if bold:
                if 'bold' not in font.lower():
                    font += 'Bold'
            else:
                font = font.replace('Bold', '')

        if italics is not None:
            if italics:
                if 'italic' not in font.lower():
                    font += 'Italic'
            else:
                font = font.replace('Italic', '')

        return PS(
            name=_styles[preset_category][preset]['name_for_toc'],
            alignment=_styles[preset_category][preset]['alignment'],
            allowOrphans=_styles[preset_category][preset]['allowOrphans'],
            allowWidows=_styles[preset_category][preset]['allowWidows'],
            backColor=background if background is not None else _styles[preset_category][preset]['background'],
            fontName=font,
            fontSize=_styles[preset_category][preset]['fontsize'],
            leading=_styles[preset_category][preset]['leading'],
            leftIndent=_styles[preset_category][preset]['leftIndent'],
            spaceAfter=_styles[preset_category][preset]['spaceAfter'],
            spaceBefore=_styles[preset_category][preset]['spaceBefore'],
            textColor=foreground if foreground is not None else _styles[preset_category][preset]['foreground']
        )


def italicised(string):
    return '<i>{}</i>'.format(string)


def table(data, box=False, grid=True, row_heights=None, valign='top'):
    result = []

    table_style = default_table_style()

    if box:
        table_style.append(('BOX', (0, 0), (-1, -1), 0.5, color.BLACK))

    if grid:
        table_style.append(('GRID', (0, 0), (-1, -1), 0.5, color.BLACK))

    table_style.append(('VALIGN', (0, 0), (-1, -1), valign.upper()))

    # Find the table's dimensions

    max_row = -1
    max_column = -1
    for row in data:
        c = 0
        for column in row:
            horizontal_span = 1 if 'horizontal span' not in column.keys() else column['horizontal span']

            c += 1 + horizontal_span - 1
        if c > max_column:
            max_column = c
    max_row = len(data)

    # Build a table with empty entries
    table_row = []
    for c in range(0, max_column):
        table_row.append('')
    for r in range(0, max_row):
        result.append(copy.deepcopy(table_row))

    # Now fill the blanks
    r = 0
    for row in data:
        c = 0
        for column in row:
            horizontal_span = 1 if 'horizontal span' not in column.keys() else column['horizontal span']
            vertical_span = 1 if 'vertical span' not in column.keys() else column['vertical span']

            if 'line above' in column.keys() and column['line above']:
                table_style.append(('LINEABOVE', (c, r), (c + horizontal_span - 1, r + vertical_span - 1), 0.5, fikTools.colorBLACK))

            if 'line below' in column.keys() and column['line below']:
                table_style.append(('LINEBELOW', (c, r), (c + horizontal_span - 1, r + vertical_span - 1), 0.5, fikTools.colorBLACK))

            if 'horizontal shift' in column.keys():
                c += column['horizontal shift']

            if 'text override' in column.keys() and column['text override'] is not None:
                result[r][c] = column['text override']
            else:
                result[r][c] = Paragraph(
                    column['text'],
                    style=get_style(preset=column['style'],
                                    preset_category=column['style_category'],
                                    foreground=column['foreground'] if 'foreground' in column.keys() else None,
                                    background=column['background'] if 'background' in column.keys() else None,
                                    )
                )
            table_style.append(
                (
                    'SPAN',
                    (c, r),
                    (c + horizontal_span - 1, r + vertical_span - 1)
                )
            )
            if 'background' in column.keys():
                table_style.append(('BACKGROUND',
                                    (c, r),
                                    (c + horizontal_span - 1, r + vertical_span - 1),
                                    column['background']
                                    ))
            c += horizontal_span
        r += 1

    t = Table(result, style=table_style, rowHeights=row_heights)

    return t


def table_entry(text, style=None, foreground='#000000', background='#ffffff', horizontal_span=1, vertical_span=1, line_above=None, line_below=None, text_override=None, horizontal_shift=0, page_colour_scheme=None):

    if style is not None:
        try:
            category, preset = style.split(':')

        except ValueError:
            category = 'default'
            preset = style
    else:
        category = 'default'
        preset = 'body'

    result = {
        'text': text,
        'style': preset,
        'style_category': category,
        'horizontal span': horizontal_span,
        'vertical span': vertical_span,
        'horizontal shift': horizontal_shift,
        'foreground': page_colour_scheme['default']['foreground'] if foreground is None else foreground,
        'background': page_colour_scheme['default']['background'] if background is None else background,
        'line above': line_above,
        'line below': line_below,
        'text override': text_override,
    }

    return result


def title_page(story, page_size, title, subtitle='', page_break_before=False, page_break_after=False, add_to_toc=['', '']):
    check_init()

    if page_break_before:
        story.append(PageBreak())

    if title != '':
        page_story = [[Paragraph(title, get_style('doc_title'))], [Paragraph(subtitle, get_style('doc_subtitle'))]]

        t = Table(page_story, colWidths=_document_sizes[page_size]['frame_width'], rowHeights=[_document_sizes[page_size]['frame_height'] * 0.5, _document_sizes[page_size]['frame_height'] * 0.33])

        t.setStyle(TableStyle([
            # ('GRID', (0, 0), (-1, -1), 0.5, fikTools.color.BLACK),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('VALIGN', (-1, -1), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))

        story.append(t)

    if add_to_toc[0] != '':
        story.append(Paragraph(add_to_toc[0], get_style(add_to_toc[1])))

    if page_break_after:
        story.append(PageBreak())
