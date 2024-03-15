import os
import sys
import time
import traceback


_log = {}
_stop_watch = {}
_trace_levels = []
_warnings = {}


def _message(msg, no_trace=False, trace_level=None, file='', send_to_screen=True):
    global _trace_levels

    if trace_level is not None and trace_level not in _trace_levels:
        return

    log_message = '{}{}'.format('' if no_trace else '{}: '.format(f_name(file)), msg)
    _log[time.time()] = log_message

    if send_to_screen:
        print(log_message)


def f_name(file=''):
    return '{}{}() called from {}()'.format(
        '{}.'.format(os.path.basename(file).replace('.py', '')) if file != '' else '',
        # sys._getframe(3).f_code.co_name,
        # sys._getframe(4).f_code.co_name
        sys._getframe(2).f_code.co_name,
        sys._getframe(3).f_code.co_name
    )


def get_log():
    return _log


def get_warnings(section=''):
    return _warnings[section] if section != '' else _warnings.keys()


def set_trace_levels(trace_levels):
    global _trace_levels

    _trace_levels = trace_levels


def debug(msg, no_trace=False, trace_level=None, file='', send_to_screen=True):
    _message('(debug) {}'.format(msg), no_trace=no_trace, trace_level=trace_level, file=file, send_to_screen=send_to_screen)


def dump_traceback(exception, send_to_screen=True):
    
    # Save to file
    
    tb = exception.__traceback__

    while tb:
        error("{}: {}".format(tb.tb_frame.f_code.co_filename, tb.tb_lineno), no_trace=True, send_to_screen=False)
        tb = tb.tb_next

    # Print to the screen
    
    if send_to_screen:
        traceback.print_exception(type(exception), exception, exception.__traceback__)


def error(msg, no_trace=False, trace_level=None, file='', send_to_screen=True):
    _message(' ** ERROR: {}'.format(msg), no_trace=no_trace, trace_level=trace_level, file=file, send_to_screen=send_to_screen)


def fatal(msg, no_trace=False, trace_level=None, file='', send_to_screen=True):

    traceback.print_stack()

    _message(' ** FATAL ERROR: {}'.format(msg), no_trace=no_trace, trace_level=trace_level, file=file, send_to_screen=send_to_screen)
    
    exit()


def message(msg, no_trace=False, trace_level=None, file='', send_to_screen=True):
    _message(msg, no_trace=no_trace, trace_level=trace_level, file=file, send_to_screen=send_to_screen)


def not_implemented(text, partial=False, fatal=False, trace_level=None, file='', send_to_screen=True):
    warning('{} is not {}implemented yet'.format(text, 'fully ' if partial else ''), no_trace=True,  trace_level=trace_level, file=file, send_to_screen=send_to_screen)

    if fatal:
        exit()


def start_stopwatch(watch='stop watch', cumulative=False):
    global _stop_watch

    if watch not in _stop_watch.keys():
        _stop_watch[watch] = {
            'start_timestamp': 0,
            'elapsed': 0,
            'cumulative': cumulative,
        }

    _stop_watch[watch]['start_timestamp'] = time.time()


def stop_stopwatch(watch='stop watch', trace_level=None, file=''):
    global _stop_watch

    now = time.time()

    if _stop_watch[watch]['cumulative']:
        _stop_watch[watch]['elapsed'] += now - _stop_watch[watch]['start_timestamp']
    else:
        _stop_watch[watch]['elapsed'] = now - _stop_watch[watch]['start_timestamp']
        show_stopwatch(watch=watch, trace_level=trace_level, file=file)


def show_stopwatch(watch='stop watch', trace_level=None, file=''):
    _message('{}: {:.2f}s'.format(watch, _stop_watch[watch]['elapsed']), no_trace=True, trace_level=trace_level, file=file)


def warning(msg, no_trace=False, trace_level=None, file='', archive_section='', send_to_screen=True):
    _message(' * Warning: {}'.format(msg), no_trace=no_trace, trace_level=trace_level, file=file, send_to_screen=send_to_screen)

    if archive_section != '':
        if archive_section not in _warnings.keys():
            _warnings[archive_section] = []

        _warnings[archive_section].append(msg)


def warning_reset(archive_section):
    _warnings[archive_section] = []
