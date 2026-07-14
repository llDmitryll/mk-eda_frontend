from dataclasses import dataclass

from ply import lex, yacc  # type: ignore


@dataclass
class VerilogParserResult:
    keyword: str
    module_name: str
    names: list[str]
    nodes: list[tuple[str, str, list[str]]]


class VerilogParser:
    reserved = {
        "module": "MODULE",
        "endmodule": "ENDMODULE",
        "input": "INPUT",
        "output": "OUTPUT",
        "wire": "WIRE",
        "and": "AND",
        "nand": "NAND",
        "or": "OR",
        "nor": "NOR",
        "xor": "XOR",
        "xnor": "XNOR",
        "buf": "BUF",
        "not": "NOT",
        "reg": "REG",
        "assign": "ASSIGN",
    }

    tokens = list(reserved.values()) + [
        "IDENTIFIER",
        "COMMA",
        "SEMICOLON",
        "COLON",
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "QUESTION_MARK",
        "NUMBER",
        "UNARY_OPERATOR",
        "BINARY_OPERATOR",
        "LBRACE",
        "RBRACE",
        "EQUALS",
    ]

    t_COMMA = r","
    t_SEMICOLON = r";"
    t_COLON = r":"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_QUESTION_MARK = r"\?"
    t_UNARY_OPERATOR = r"[!~+-]"
    t_BINARY_OPERATOR = r"(\+|\-|\*|\/|\&|\||\^|==|!=|<=|>=|<<|>>|&&|\|\|)"
    t_LBRACE = r"{"
    t_RBRACE = r"}"
    t_EQUALS = r"="

    def t_IDENTIFIER(self, t: lex.LexToken) -> lex.LexToken:
        r"""[a-zA-Z_][a-zA-Z_0-9$]*"""
        t.type = self.reserved.get(t.value.lower(), "IDENTIFIER")  # type: ignore
        return t

    def t_NUMBER(self, t: lex.LexToken) -> lex.LexToken:
        r"""\d+"""
        t.value = int(t.value)  # type: ignore
        return t

    t_ignore = """ \t"""

    def t_newline(self, t: lex.LexToken) -> None:
        r"""\n+"""
        t.lexer.lineno += len(t.value)  # type: ignore

    def t_error(self, t: lex.LexToken) -> None:
        print(f"Illegal character {t.value[0]!r}")  # type: ignore
        t.lexer.skip(1)  # type: ignore

    def p_module(self, p: yacc.YaccProduction) -> None:
        """module : MODULE IDENTIFIER port_declaration SEMICOLON ENDMODULE
        | MODULE IDENTIFIER port_declaration SEMICOLON list_of_items ENDMODULE"""
        if len(p) == 6:
            p[0] = ("module", p[2], p[3], None)
        elif len(p) == 7:
            p[0] = ("module", p[2], p[3], p[5])

    def p_port_declaration(self, p: yacc.YaccProduction) -> None:
        """port_declaration : LPAREN list_of_ports RPAREN"""
        p[0] = p[2]

    def p_list_of_ports(self, p: yacc.YaccProduction) -> None:
        """list_of_ports : list_of_ports COMMA IDENTIFIER
        | IDENTIFIER"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_list_of_items(self, p: yacc.YaccProduction) -> None:
        """list_of_items : list_of_items module_item
        | module_item"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_module_item(self, p: yacc.YaccProduction) -> None:
        """module_item : input_declaration
        | output_declaration
        | net_declaration
        | reg_declaration
        | gate_declaration
        | continuous_assign"""
        p[0] = p[1]

    def p_input_declaration(self, p: yacc.YaccProduction) -> None:
        """input_declaration : INPUT range list_of_variables SEMICOLON
        | INPUT list_of_variables SEMICOLON"""
        if len(p) == 5:
            p[0] = ("input", p[2], p[3])
        elif len(p) == 4:
            p[0] = ("input", None, p[2])

    def p_output_declaration(self, p: yacc.YaccProduction) -> None:
        """output_declaration : OUTPUT range list_of_variables SEMICOLON
        | OUTPUT list_of_variables SEMICOLON"""
        if len(p) == 5:
            p[0] = ("output", p[2], p[3])
        elif len(p) == 4:
            p[0] = ("output", None, p[2])

    def p_reg_declaration(self, p: yacc.YaccProduction) -> None:
        """reg_declaration : REG range list_of_variables SEMICOLON
        | REG list_of_variables SEMICOLON"""
        if len(p) == 5:
            p[0] = ("reg", p[2], p[3])
        elif len(p) == 4:
            p[0] = ("reg", None, p[2])

    def p_net_declaration(self, p: yacc.YaccProduction) -> None:
        """net_declaration : WIRE range list_of_variables SEMICOLON
        | WIRE list_of_variables SEMICOLON"""
        if len(p) == 5:
            p[0] = ("wire", p[2], p[3])
        elif len(p) == 4:
            p[0] = ("wire", None, p[2])

    def p_list_of_variables(self, p: yacc.YaccProduction) -> None:
        """list_of_variables : list_of_variables COMMA IDENTIFIER
        | IDENTIFIER"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_range(self, p: yacc.YaccProduction) -> None:
        """range : LBRACKET expression COLON expression RBRACKET"""
        p[0] = ("range", p[2], p[4])

    def p_gate_declaration(self, p: yacc.YaccProduction) -> None:
        """gate_declaration : gate_type list_of_gate_instances SEMICOLON"""
        p[0] = (p[1], p[2])

    def p_list_of_gate_instances(self, p: yacc.YaccProduction) -> None:
        """list_of_gate_instances : list_of_gate_instances COMMA gate_instance
        | gate_instance"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_gate_type(self, p: yacc.YaccProduction) -> None:
        """gate_type : AND
        | OR
        | XOR
        | NAND
        | NOR
        | XNOR
        | BUF
        | NOT
        """
        p[0] = p[1]

    def p_gate_instance(self, p: yacc.YaccProduction) -> None:
        """gate_instance : IDENTIFIER range LPAREN list_of_expressions RPAREN
        | IDENTIFIER LPAREN list_of_expressions RPAREN
        | LPAREN list_of_expressions RPAREN"""
        if len(p) == 6:
            p[0] = ("gate_instance", p[1], p[2], p[4])
        elif len(p) == 5:
            p[0] = ("gate_instance", p[1], None, p[3])
        elif len(p) == 4:
            p[0] = ("gate_instance", None, None, p[2])

    def p_expression(self, p: yacc.YaccProduction) -> None:
        """expression : primary
        | UNARY_OPERATOR primary
        | expression BINARY_OPERATOR expression
        | expression QUESTION_MARK expression COLON expression
        """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ("unary_op", p[1], p[2])
        elif len(p) == 4:
            p[0] = ("binary_op", p[2], p[1], p[3])
        elif len(p) == 6:
            p[0] = ("ternary_op", p[1], p[3], p[5])

    def p_primary(self, p: yacc.YaccProduction) -> None:
        """primary : NUMBER
        | IDENTIFIER
        | IDENTIFIER LBRACKET expression RBRACKET
        | IDENTIFIER LBRACKET constant_expression COLON constant_expression RBRACKET
        | concatenation
        """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = ("index", p[1], p[3])
        elif len(p) == 6:
            p[0] = ("slice", p[1], p[3], p[5])
        else:
            p[0] = p[1]

    def p_constant_expression(self, p: yacc.YaccProduction) -> None:
        """constant_expression : expression"""
        p[0] = p[1]

    def p_concatenation(self, p: yacc.YaccProduction) -> None:
        """concatenation : LBRACE list_of_expressions RBRACE"""
        p[0] = ("concatenation", p[2])

    def p_list_of_expressions(self, p: yacc.YaccProduction) -> None:
        """list_of_expressions : list_of_expressions COMMA expression
        | expression
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_continuous_assign(self, p: yacc.YaccProduction) -> None:
        """continuous_assign : ASSIGN list_of_assignments SEMICOLON"""
        p[0] = ("continuous_assign", p[2])

    def p_list_of_assignments(self, p: yacc.YaccProduction) -> None:
        """list_of_assignments : list_of_assignments COMMA assignment
        | assignment"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_assignment(self, p: yacc.YaccProduction) -> None:
        """assignment : lvalue EQUALS expression"""
        p[0] = ("assignment", p[1], p[3])

    def p_lvalue(self, p: yacc.YaccProduction) -> None:
        """lvalue : IDENTIFIER
        | IDENTIFIER LBRACKET expression RBRACKET
        | IDENTIFIER LBRACKET constant_expression COLON constant_expression RBRACKET
        | concatenation"""
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = ("index_lvalue", p[1], p[3])
        elif len(p) == 6:
            p[0] = ("slice_lvalue", p[1], p[3], p[5])
        else:
            p[0] = p[1]

    def p_error(self, p: yacc.YaccProduction) -> None:
        if p:
            print("Syntax error at '%s'" % p.value)  # type: ignore
        else:
            print("Syntax error at EOF")

    def __init__(self) -> None:
        self.lexer = lex.lex(module=self)  # type: ignore
        self.parser = yacc.yacc(module=self, write_tables=False, debug=True)  # type: ignore

    def parse(self, verilog_code: str) -> VerilogParserResult:
        return VerilogParserResult(*self.parser.parse(verilog_code))  # type: ignore
