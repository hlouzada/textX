from arpeggio import Optional, EOF
from arpeggio import ZeroOrMore as ArpeggioZeroOrMore
from arpeggio import RegExMatch as _
from arpeggio import PTNodeVisitor, visit_parse_tree


def id():
    return _(r'[^\d\W]\w*\b')  # from lang.py


def parent():
    return 'parent', '(', id, ')'


def navigation():
    return Optional('~'), id


def brackets():
    return '(', path, ')'


def dots():
    return _(r'\.+')


def path_element():
    return [parent, brackets, navigation]


def zero_or_more():
    return path_element, '*'


def path():
    return Optional(['^', dots]), ArpeggioZeroOrMore(
        [zero_or_more, path_element], '.'), [
        zero_or_more, path_element]


def rrel():
    return path, EOF


class Parent:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return 'parent({})'.format(self.type)


class Navigation:
    def __init__(self, name, consume_name):
        self.name = name
        self.consume_name = consume_name

    def __repr__(self):
        return '~' + self.name if self.consume_name else self.name


class Brackets:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return '(' + str(self.path) + ')'


class Dots:
    def __init__(self, num):
        self.num = num

    def __repr__(self):
        return ('.' * self.num)


class ZeroOrMore:
    def __init__(self, path_element):
        self.path_element = path_element

    def __repr__(self):
        return str(self.path_element) + '*'


class Path:
    def __init__(self, path_elements):
        print("create Path :" + str(path_elements))
        self.path_elements = path_elements
        if (self.path_elements[0] == '^'):
            self.path_elements[0] = ZeroOrMore(Brackets(Path([Dots(2)])))

    def __repr__(self):
        if isinstance(self.path_elements[0], Dots):
            return str(self.path_elements[0]) + '.'.join(
                map(lambda x: str(x), self.path_elements[1:]))
        else:
            return '.'.join(map(lambda x: str(x), self.path_elements))


class RrelVisitor(PTNodeVisitor):

    def visit_parent(self, node, children):
        return Parent(children[0])

    def visit_navigation(self, node, children):
        if len(children) == 1:
            return Navigation(children[0], False)
        else:
            return Navigation(children[1], True)

    def visit_brackets(self, node, children):
        assert(len(children) == 1)  # a path
        return Brackets(children[0])

    def visit_dots(self, node, children):
        return Dots(len(node.value))

    def visit_zero_or_more(self, node, children):
        return ZeroOrMore(children[0])

    def visit_path(self, node, children):
        return Path(children)

    def visit_path_element(self, node, children):
        assert(len(children) == 1)
        return children[0]


def parse(rrel_expression):
    """
    This function parses a rrel path and returns a RREL expression tree.

    Args:
        rrel_expression: the RREL expression.

    Returns:
        A RREL expression tree.
    """
    from arpeggio import ParserPython
    parser = ParserPython(rrel, reduce_tree=False)
    parse_tree = parser.parse(rrel_expression)
    return visit_parse_tree(parse_tree, RrelVisitor())


def find(obj, lookup_string, rrel_tree):
    """
    This function gets all/one element from a model
    object based on an rrel tree (query).

    Args:
        obj: model object (starting point of the search)
        lookup_string: dot sepaarted name
        rrel_tree: the query

    Returns:
        The result of the query (first match), a
        Postponed object, or None (nothing found).
    """
    pass
