from qgis.PyQt.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat, QFont
from qgis.PyQt.QtCore import QRegExp


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'keyword': format('#b32424'),
    'operator': format('black'),
    'error': format('red'),
    'brace': format('black'),
    'defclass': format('#14866d'),
    'uri': format('#2a4b8d'),
    'prefixcls': format('#14866d'),
    'string': format('#ac6600'),
    'string2': format('darkMagenta'),
    'comment': format('#72777d'),
    'self': format('blue', 'italic'),
    'numbers': format('black'),
}


class SPARQLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'SELECT', 'INSERT', 'WHERE', 'ORDER', 'BY', 'LIMIT',
        'OFFSET', 'FROM', 'PREFIX', 'GRAPH', 'NAMED', 'BIND',
        'VALUES', 'ASC', 'DESC', 'FILTER', 'DISTINCT', 'REDUCED',
        'OPTIONAL', 'CONSTRUCT', 'ASK', 'DESCRIBE', 'BOUND', 'IF', 'SERVICE',
        'EXISTS', 'NOT', 'IN', 'STR', 'AS', 'LANG', 'DELETE', 'CREATE', 'CLEAR', 'DROP', 'LOAD', 'COPY', 'MOVE', 'ADD'
                                                                                                                 'IRI',
        'URI', 'False', 'a'
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    errorhighlightline = -1

    currentline = 0

    errorhighlightcol = -1

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document.document())
        # msgBox=QMessageBox()
        # msgBox.setText(document.toPlainText())
        # msgBox.exec()
        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'([?]\w+)', 1, STYLES['defclass']),
            (r'([<][h][t][t][p][:][/][/]\w+[>])', 0, STYLES['uri']),
            # 'class' followed by an identifier
            (r'(\w+[:]\w+)', 1, STYLES['uri']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]
        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in SPARQLHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in SPARQLHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in SPARQLHighlighter.braces]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        self.currentline += 1
        # msgBox=QMessageBox()
        # msgBox.setText(str(self.errorhighlightline))
        # msgBox.exec()
        # if self.errorhighlightline!=-1:
        #    self.setFormat(0, len(text), STYLES['error'])
        # else:
        #    # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
