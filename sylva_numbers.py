#!/usr/bin/env python

import re
import pprint
import itertools

rx = re.compile(
    r'^[+-]?'
    r'('
    r'('
      r'(\d+)'
      r'(([iu])(8|16|32|64|128|256))'
      r'([cw])?'
    r')'
    r'|'
    r'('
      r'('
        r'(((\d+\.\d+)|(\d+\.)|(\.\d+))([Ee][+-]?\d+)?)|'
        r'(\d+[Ee][+-]?\d+)|'
        r'(\d+)'
      r')'
      r'(f(16|32|64|128|256))?'
      r'(ra|rd|ru|rz)?'
    r')'
    r')'
)

signs = ('', '+', '-')
exp_indicators = ('e', 'E')
rounds = ('', 'ra', 'rd', 'ru', 'rz')

dec_ints = ('', '3', '35')
dec_fracs = ('', '4', '46')
dec_vals = (
    list(dec_ints[1:]) +
    [f'{int}.{frac}' for int, frac in itertools.product(
        dec_ints,
        dec_fracs
    ) if int or frac]
)
dec_exp_vals = ('5', '57')
dec_exps = [''] + [f'{x}{y}{z}' for x, y, z in itertools.product(
    exp_indicators,
    signs,
    dec_exp_vals
)]

float_ints = ('', '4', '46')
float_fracs = ('', '5', '57')
float_vals = (
    list(float_ints[1:]) +
    [f'{int}.{frac}' for int, frac in itertools.product(
        float_ints,
        float_fracs
    ) if int or frac]
)
float_exp_vals = ('6', '68')
float_exps = [''] + [f'{x}{y}{z}' for x, y, z in itertools.product(
    exp_indicators,
    signs,
    float_exp_vals
)]
float_types = ('', 'f16', 'f32', 'f64', 'f128', 'f256')

int_vals = ('1', '12')
int_types = ('i', 'u')
int_sizes = ('8', '16', '32', '64', '128', '256')
int_overflows = ('', 'w', 'c')

numbers = (
    [
        f'{sign}{val}{exp}{round}'
        for sign, val, exp, round in itertools.product(
            signs,
            dec_vals,
            dec_exps,
            rounds
        )
    ] +
    [
        f'{sign}{val}{exp}{type}{round}'
        for sign, val, exp, type, round in itertools.product(
            signs,
            float_vals,
            float_exps,
            float_types,
            rounds
        )
    ] +
    [
        f'{sign}{val}{type}{size}{overflow}'
        for sign, val, type, size, overflow in itertools.product(
            signs,
            int_vals,
            int_types,
            int_sizes,
            int_overflows
        )
    ]
)

def pdir(x):
    pprint.pprint(dir(x))

def main():
    for number in numbers:
        match = rx.match(number)
        if not match:
            print(f"Couldn't match {number}")
            continue
        if match.group() != number:
            print(f'{match.group()} != {number}')

main()
