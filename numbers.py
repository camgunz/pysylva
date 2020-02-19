#!/usr/bin/env python

import re
import pprint
import itertools

fp_rx = re.compile(
    r'^[+-]??'
    (
        r'\d+\.\d+([Ee][+-]??\d+)?'
        r'\d+\.([Ee][+-]??\d+)?'
        r'\d+[Ee][+-]??\d+'
        r'\.\d+([Ee][+-]??\d+)?'
    ) +
    r'f\d+' +
    r'(ru|rd|rz|ra)?'
)

int_rx = re.compile(
    r'^[+-]??'
    r'\d+' +
    r'(i|u)\d+' +
    r'(w|c)?'
)

signs = ('', '+', '-')

float_ints = ('', '4', '46')
float_fracs = ('', '5', '57')
float_vals = [f'{int}.{frac}' for int, frac in itertools.product(
    float_ints,
    float_fracs
) if int or frac]
float_exp_indicators = ('e', 'E')
float_exp_vals = ('6', '68')
float_exps = [''] + [f'{x}{y}{z}' for x, y, z in itertools.product(
    float_exp_indicators,
    signs,
    float_exp_vals
)]
float_rounds = ('', 'ru', 'rd', 'rz', 'ra')

int_vals = ('1', '12')
int_types = ('i', 'u')
int_overflows = ('', 'w', 'c')

numbers = [
    f'{sign}{val}{exp}f32{round}'
    for sign, val, exp, round in itertools.product(
        signs,
        float_vals,
        float_exps,
        float_rounds
    )
] + [
    f'{sign}{val}{type}8{overflow}'
    for sign, val, type, overflow in itertools.product(
        signs,
        int_vals,
        int_types,
        int_overflows
    )
]

def pdir(x):
    pprint.pprint(dir(x))

def main():
    number_count = len(numbers)
    mismatch_count = 0

    for number in numbers:
        fp_match = fp_rx.match(number)
        int_match = int_rx.match(number)
        if not fp_match and not int_match:
            print(f"Couldn't match {number}")
        elif fp_match and int_match:
            print(f'Ambiguous number {number}')
        elif fp_match and fp_match.group() != number:
            print(f'Mismatched float: {number} != {fp_match.group()}')
        elif int_match and int_match.group() != number:
            print(f'Mismatched int: {number} != {int_match.group()}')

main()
