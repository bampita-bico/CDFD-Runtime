from dsl.tokens import TokenType
from dsl.ast_nodes import (
    DefineNode, SetNode, PatientNode, ApplyNode, ModifyNode,
    RunNode, ScenarioNode, ObserveNode, SweepNode, DiscoverNode, LinkNode,
    AnalyzeNode, BifurcateNode, EmergeNode, AttractorNode, InfoFlowNode,
    VacuumNode, KnotNode, ResolveNode, SystemNode, RuleNode
)


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_type=None, expected_value=None):
        tok = self.tokens[self.pos]
        if expected_type and tok.type != expected_type:
            raise ParseError(f"Expected {expected_type}, got {tok}")
        if expected_value and tok.value != expected_value:
            raise ParseError(f"Expected '{expected_value}', got '{tok.value}'")
        self.pos += 1
        return tok

    def parse(self):
        ast = []
        while self.peek().type != TokenType.EOF:
            node = self._parse_statement()
            if node is not None:
                ast.append(node)
        return ast

    def _parse_statement(self):
        tok = self.peek()
        if tok.type == TokenType.EOF:
            return None
        if tok.type != TokenType.KEYWORD:
            self.pos += 1
            return None
        kw = tok.value
        if kw == "RUN":
            return self._parse_run()
        if kw == "DEFINE":
            return self._parse_define()
        if kw == "SET":
            return self._parse_set()
        if kw == "PATIENT":
            return self._parse_patient()
        if kw == "APPLY":
            return self._parse_apply()
        if kw == "SCENARIO":
            return self._parse_scenario()
        if kw == "OBSERVE":
            return self._parse_observe()
        if kw == "SWEEP":
            return self._parse_sweep()
        if kw == "DISCOVER":
            return self._parse_discover()
        if kw == "LINK":
            return self._parse_link()
        if kw == "ANALYZE":
            return self._parse_analysis_block(AnalyzeNode)
        if kw == "BIFURCATE":
            return self._parse_analysis_block(BifurcateNode)
        if kw == "EMERGE":
            return self._parse_analysis_block(EmergeNode)
        if kw == "ATTRACTOR":
            return self._parse_analysis_block(AttractorNode)
        if kw == "INFOFLOW":
            return self._parse_analysis_block(InfoFlowNode)
        if kw == "SPAWN":
            return self._parse_spawn()
        if kw == "RESOLVE":
            return self._parse_resolve()
        if kw == "SYSTEM":
            return self._parse_system()
        if kw == "RULE":
            return self._parse_rule()
        self.pos += 1
        return None

    def _parse_define(self):
        self.consume(TokenType.KEYWORD, "DEFINE")
        type_tok = self.consume(TokenType.KEYWORD)
        if type_tok.value == "Vacuum":
            self.consume(TokenType.LBRACE)
            data = self._parse_kv_block()
            return VacuumNode(data)
        name_tok = self.consume(TokenType.IDENTIFIER)
        return DefineNode(type_tok.value, name_tok.value)

    def _parse_spawn(self):
        self.consume(TokenType.KEYWORD, "SPAWN")
        type_tok = self.consume(TokenType.KEYWORD, "Knot")
        self.consume(TokenType.LBRACE)
        data = self._parse_kv_block()
        return KnotNode(data)

    def _parse_resolve(self):
        self.consume(TokenType.KEYWORD, "RESOLVE")
        target_tok = self.consume(TokenType.KEYWORD, "Spectrum")
        return ResolveNode(target_tok.value)

    def _parse_set(self):
        self.consume(TokenType.KEYWORD, "SET")
        key_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.COLON)
        val_tok = self.consume()
        return SetNode(key_tok.value, val_tok.value)

    def _parse_patient(self):
        self.consume(TokenType.KEYWORD, "PATIENT")
        name_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LBRACE)
        data = self._parse_kv_block()
        return PatientNode(name_tok.value, data)

    def _parse_apply(self):
        self.consume(TokenType.KEYWORD, "APPLY")
        cond_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.KEYWORD, "TO")
        target_tok = self.consume(TokenType.IDENTIFIER)
        return ApplyNode(cond_tok.value, target_tok.value)

    def _parse_scenario(self):
        self.consume(TokenType.KEYWORD, "SCENARIO")
        name_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LBRACE)
        steps = []
        while self.peek().type != TokenType.RBRACE and self.peek().type != TokenType.EOF:
            node = self._parse_statement()
            if node is not None:
                steps.append(node)
        if self.peek().type == TokenType.RBRACE:
            self.pos += 1
        return ScenarioNode(name_tok.value, steps)

    def _parse_observe(self):
        self.consume(TokenType.KEYWORD, "OBSERVE")
        self.consume(TokenType.LBRACE)
        data = self._parse_kv_block()
        metrics = data.get("metrics", [])
        return ObserveNode(metrics)

    def _parse_sweep(self):
        self.consume(TokenType.KEYWORD, "SWEEP")
        param_tok = self.consume(TokenType.IDENTIFIER)
        values = self._parse_list()
        return SweepNode(param_tok.value, values)

    def _parse_discover(self):
        self.consume(TokenType.KEYWORD, "DISCOVER")
        self.consume(TokenType.LBRACE)
        data = self._parse_kv_block()
        return DiscoverNode(data)

    def _parse_analysis_block(self, node_class):
        self.pos += 1  # consume the keyword token
        params = {}
        if self.peek().type == TokenType.LBRACE:
            self.consume(TokenType.LBRACE)
            params = self._parse_kv_block()
        return node_class(params)

    def _parse_link(self):
        self.consume(TokenType.KEYWORD, "LINK")
        src_tok = self.consume(TokenType.IDENTIFIER)
        tgt_tok = self.consume(TokenType.IDENTIFIER)
        return LinkNode(src_tok.value, tgt_tok.value)

    def _parse_run(self):
        self.consume(TokenType.KEYWORD, "RUN")
        self.consume(TokenType.KEYWORD, "Engine")
        self.consume(TokenType.LBRACE)
        params = self._parse_kv_block()
        return RunNode(params)

    def _parse_system(self):
        self.consume(TokenType.KEYWORD, "SYSTEM")
        name_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LBRACE)
        data = self._parse_kv_block()
        return SystemNode(
            name=name_tok.value,
            flux_expr=data.get("flux"),
            constraint_expr=data.get("constraint"),
            state_expr=data.get("state"),
        )

    def _parse_rule(self):
        self.consume(TokenType.KEYWORD, "RULE")
        name_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LBRACE)
        # expect: IF psi > threshold ACTION action_name
        # handled as loose token stream inside the block
        condition_psi = None
        threshold = None
        action = None
        while self.peek().type not in (TokenType.RBRACE, TokenType.EOF):
            tok = self.peek()
            if tok.type == TokenType.KEYWORD and tok.value == "IF":
                self.pos += 1  # consume IF
                condition_psi = self.consume(TokenType.IDENTIFIER).value  # "psi"
                # comparator (">", "<") is not a token — already dropped by lexer
                threshold_tok = self.peek()
                if threshold_tok.type == TokenType.NUMBER:
                    threshold = float(threshold_tok.value)
                    self.pos += 1
            elif tok.type == TokenType.KEYWORD and tok.value == "ACTION":
                self.pos += 1  # consume ACTION
                action = self.consume(TokenType.IDENTIFIER).value
            else:
                self.pos += 1
        if self.peek().type == TokenType.RBRACE:
            self.pos += 1
        return RuleNode(name=name_tok.value, condition_psi=condition_psi,
                        threshold=threshold, action=action)

    def _parse_kv_block(self):
        data = {}
        while self.peek().type not in (TokenType.RBRACE, TokenType.EOF):
            if self.peek().type == TokenType.KEYWORD and self.peek().value == "RUN":
                node = self._parse_run()
                data["_run"] = node
                continue
            if self.peek().type == TokenType.KEYWORD and self.peek().value == "MODIFY":
                node = self._parse_modify()
                data.setdefault("_modify", []).append(node)
                continue
            if self.peek().type not in (TokenType.IDENTIFIER, TokenType.KEYWORD):
                self.pos += 1
                continue
            key_tok = self.consume()
            if self.peek().type != TokenType.COLON:
                continue
            self.consume(TokenType.COLON)
            value = self._parse_value()
            data[key_tok.value] = value
        if self.peek().type == TokenType.RBRACE:
            self.pos += 1
        return data

    def _parse_modify(self):
        self.consume(TokenType.KEYWORD, "MODIFY")
        target_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LBRACE)
        data = self._parse_kv_block()
        return ModifyNode(target_tok.value, data)

    def _parse_value(self):
        tok = self.peek()
        if tok.type == TokenType.LBRACKET:
            return self._parse_list()
        if tok.type == TokenType.NUMBER:
            self.pos += 1
            return tok.value
        if tok.type in (TokenType.IDENTIFIER, TokenType.KEYWORD, TokenType.STRING):
            self.pos += 1
            return tok.value
        self.pos += 1
        return None

    def _parse_list(self):
        self.consume(TokenType.LBRACKET)
        items = []
        while self.peek().type != TokenType.RBRACKET and self.peek().type != TokenType.EOF:
            if self.peek().type == TokenType.COMMA:
                self.pos += 1
                continue
            tok = self.peek()
            self.pos += 1
            items.append(tok.value)
        if self.peek().type == TokenType.RBRACKET:
            self.pos += 1
        return items


def parse(tokens):
    return Parser(tokens).parse()
