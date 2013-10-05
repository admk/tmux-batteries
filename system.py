#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""This is an implementation of creaktive's rainbarf in Python 3. I did this
because rainbarf is broken in Mavericks."""


import sys
import pickle
import psutil


interval = 1
history_length = 8
invert_color = False

tmp_file = '/tmp/tmux_system.pkl'


def cpu_history():
    try:
        with open(tmp_file, 'rb') as f:
            history = pickle.load(f)
    except FileNotFoundError:
        history = None
    if not history:
        history = [0] * history_length
    if len(history) <= history_length:
        history = [0] * (history_length - len(history)) + history
    truncate_idx = len(history) - history_length + 1
    history = history[truncate_idx:] + [psutil.cpu_percent(interval=interval)]
    with open(tmp_file, 'wb') as f:
        pickle.dump(history, f)
    return history


def format_history(history):
    bars = '▁▃▄▅▆▇█'
    idx = lambda h: int(h / 100 * (len(bars) - 1))
    return ''.join([bars[idx(h)] for h in history])


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
    colors = ('red', 'yellow', 'blue', 'green', 'cyan')
    portions = [stat.wired, stat.active, stat.inactive, stat.free]
    try:
        portions.append(stat.cached)
    except AttributeError:
        pass
    portions = split_string_in_portions(string, portions)
    portions = [colorize(s, c) for s, c in zip(portions, colors)]
    return ''.join(portions)


def format():
    return format_with_memory(format_history(cpu_history()))


try:
    sys.stdout.write(format())
    sys.stdout.flush()
except Exception as e:
    print(e)
