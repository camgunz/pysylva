import lark


def Parser(start='module'):
    return lark.Lark.open(
        'Sylva.lark',
        rel_to=__file__,
        parser='lalr',
        propagate_positions=True,
        maybe_placeholders=True,
        start=start,
    )
