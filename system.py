#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""This is an implementation of creaktive's rainbarf in Python 3. I did this
because rainbarf is broken in Mavericks."""


import pickle
import sys
from itertools import zip_longest

import psutil


interval = 1
history_length = 16
invert_color = True
use_braille = True

tmp_file = '/tmp/tmux_batteries_system.pkl'


def cpu_history():
    length = history_length
    if not use_braille:
        length = int((length + 1) / 2)
    try:
        with open(tmp_file, 'rb') as f:
            history = pickle.load(f)
    except FileNotFoundError:
        history = None
    if not history:
        history = [0] * length
    if len(history) <= length:
        history = [0] * (length - len(history)) + history
    truncate_idx = len(history) - length + 1
    history = history[truncate_idx:] + [psutil.cpu_percent(interval=interval)]
    with open(tmp_file, 'wb') as f:
        pickle.dump(history, f)
    return history


def braille(u, v, binary=False, fill=True, offset=1):
    def b(u):
        if u is None:
            return '0' * 4
        u += offset
        if binary:
            u = bin(u).lstrip('0b')
            return '0' * (4 - len(u)) + u
        pad = '0' * (4 - u)
        if fill:
            return pad + '1' * u
        if len(pad) == 4:
            return pad
        return pad + '1' + '0' * (3 - len(pad))
    u, v = b(u), b(v)
    c = (u[:-1] + v[:-1] + u[-1] + v[-1])[::-1]
    c = 0x2800 + int(c, 2)
    return chr(c)


def braille_graph(l, **kwargs):
    l = zip_longest(*([iter(l)] * 2), fillvalue=None)
    l = [braille(u, v, **kwargs) for u, v in l]
    return ''.join(l)


def format_history(history):
    braille_max = 3
    norm = lambda val, max_val: round(val / 100 * max_val)
    if use_braille:
        return braille_graph([norm(h, braille_max) for h in history])
    bars = '▁▃▄▅▆▇█'
    return ''.join([bars[norm(h, (len(bars) - 1))] for h in history])


def colorize(s, color):
    return '#[{select}={color}]{s}#[default]'.format(
        s=s, color=color, select='fg' if invert_color else 'bg')


def split_string_in_portions(string, portions):
    portions = [(p / sum(portions) * (len(string) - 1)) for p in portions]
    l = []
    idx = 0
    acc = 0
    for p in portions:
        acc += p
        end_idx = round(acc) + 1
        l.append(string[idx:end_idx])
        idx = end_idx
    return l


def format_with_memory(string):
    stat = psutil.virtual_memory()
    keys = [
        ('wired', 'red'),
        ('active', 'yellow'),
        ('inactive', 'blue'),
        ('free', 'green'),
        ('cached', 'cyan'),
        ('buffers', 'magenta')]
    portions = []
    colors = []
    for k, c in keys:
        try:
            portions.append(getattr(stat, k))
            colors.append(c)
        except AttributeError:
            pass
    portions = split_string_in_portions(string, portions)
    portions = [colorize(s, c) for s, c in zip(portions, colors)]
    return ''.join(portions)


def format():
    return format_with_memory(format_history(cpu_history()))


if __name__ == '__main__':
    sys.stdout.write(format())
    sys.stdout.flush()
