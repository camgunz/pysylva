import lark

from sylva import debug


class SelfReferentialFieldGatherer(lark.Visitor):

    def array_type_def(self, tree):
        debug('srft', f'array_type_def: {tree}')
        srf_name = tree.children[1].value
        for tree in tree.iter_subtrees():
            if not hasattr(tree.meta, 'self_referential_field_names'):
                tree.meta.self_referential_field_names = set()
            tree.meta.self_referential_field_names.add(srf_name)

    def c_array_type_def(self, tree):
        debug('srft', f'c_array_type_def: {tree}')
        srf_name = tree.children[1].value
        for tree in tree.iter_subtrees():
            if not hasattr(tree.meta, 'self_referential_field_names'):
                tree.meta.self_referential_field_names = set()
            tree.meta.self_referential_field_names.add(srf_name)

    def c_struct_type_def(self, tree):
        debug('srft', f'c_struct_type_def: {tree}')
        srf_name = tree.children[1].value
        for tree in tree.iter_subtrees():
            if not hasattr(tree.meta, 'self_referential_field_names'):
                tree.meta.self_referential_field_names = set()
            tree.meta.self_referential_field_names.add(srf_name)

    def c_union_type_def(self, tree):
        debug('srft', f'c_union_type_def: {tree}')
        srf_name = tree.children[1].value
        for tree in tree.iter_subtrees():
            if not hasattr(tree.meta, 'self_referential_field_names'):
                tree.meta.self_referential_field_names = set()
            tree.meta.self_referential_field_names.add(srf_name)

    def struct_type_def(self, tree):
        debug('srft', f'struct_type_def: {tree}')
        srf_name = tree.children[1].value
        for tree in tree.iter_subtrees():
            if not hasattr(tree.meta, 'self_referential_field_names'):
                tree.meta.self_referential_field_names = set()
            tree.meta.self_referential_field_names.add(srf_name)

    def variant_type_def(self, tree):
        debug('srft', f'variant_type_def: {tree}')
        srf_name = tree.children[1].value
        for tree in tree.iter_subtrees():
            if not hasattr(tree.meta, 'self_referential_field_names'):
                tree.meta.self_referential_field_names = set()
            tree.meta.self_referential_field_names.add(srf_name)
