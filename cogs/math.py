import discord
import random
import time
import multiprocessing
from discord.ext import commands
from functools import partial
from decimal import Decimal, getcontext
from collections import Counter
getcontext().prec = 282822
getcontext().Emax = 50505050
getcontext().Emin = -50505050
from random import choice
import re
from math import sqrt, pow
import operator as ops
import asyncio

INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, DEC, EOF, POW = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', '.', 'EOF', '^'
)
GTHAN, LTHAN, MOD, SQRT = ('>', '<', '%', '√')

class MathError(Exception):
    pass

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type, value=repr(self.value))
    
    def __repr__(self):
        return self.__str__()
    
class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
    
    def error(self, err):
        raise MathError('Error: {}'.format(err))
    
    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) -1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
        
    def integer(self):
        """Return a (multidigit) integer or float consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit() or self.current_char == '.':
            if self.current_char == '.' and '.' in result:
                self.error('Decimal `.` already in equation')
            result += self.current_char
            self.advance()
        if '.' in result:
            return float(result)
        return int(result)
    
    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())
            
            if self.current_char == '.':
                return Token(DEC, self.integer())

            if self.current_char in '+-*/()^><%√':
                tk = Token({
                    '+':PLUS, '-':MINUS, '*':MUL, '/':DIV, '(':LPAREN, ')':RPAREN,
                    '^':POW, '>':GTHAN, '<':LTHAN, '%': MOD, '√': SQRT
                }[self.current_char], self.current_char)
                self.advance()
                return tk

            self.error('Unrecognised operator **{}**. Available operators: **+-*/()^><%√**'.format(self.current_char))

        return Token(EOF, None)

class AST(object):
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class UnOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.previous_token = Token(EOF, None)
    
    def error(self, err):
        raise MathError('Error: {}'.format(err))
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.previous_token = self.current_token
            self.current_token = self.lexer.get_next_token()
        else:
            self.error('After **{}** I got **{}**, but I was expecting **{}**'.format(
                self.previous_token.value, self.current_token.type.replace('EOF', 'end'), token_type))

    def factor(self):
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnOp(token, self.factor())
            #return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnOp(token, self.factor())
            #return node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            node = Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            #return node
        try:
            return node
        except UnboundLocalError:
            pass
        
    def term(self):
        node = self.factor()
        
        while self.current_token.type in (MUL, DIV, POW, GTHAN, LTHAN, MOD, SQRT):
            token = self.current_token
            if token.type in (MUL, DIV, POW, GTHAN, LTHAN, MOD, SQRT):
                self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.factor())
        return node
    
    def expr(self):
        node = self.term()
        
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
                #result = result + self.term()
            elif token.type == MINUS:
                self.eat(MINUS)
                #result = result - self.term()
            node = BinOp(left=node, op=token, right=self.term())
        return node
    
    def parse(self):
        node = self.expr()
        if self.current_token.type != EOF:
            self.error(f'Unable to complete expression. Check: **{self.current_token.value}**')
        return node

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
    
    def op(self, func, node):
        return func(self.visit(node.left), self.visit(node.right))

    def visit_BinOp(self, node):
        ntype = node.op.type
        if ntype in (PLUS, MINUS, MUL, DIV, POW, GTHAN, LTHAN, MOD):
            return self.op({
                PLUS: ops.add, MINUS: ops.sub, MUL: ops.mul, DIV: ops.truediv,
                POW: ops.pow, GTHAN: ops.gt, LTHAN: ops.lt, MOD: ops.mod
            }[ntype], node)
        elif ntype == SQRT:
            try:
                return self.op(lambda x,y: x*sqrt(y), node)
            except:
                return 1 * sqrt(self.visit(node.right))
    
    def visit_UnOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)
    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


def do_math(expression) -> str:
    if Counter(expression).get('^') > 1:
        return 'Error: Too many exponents in expression. Current limit: 1'
    try:
        lexer = Lexer(expression)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        if not isinstance(result, bool):
            return '{:,}'.format(result)
        return '{}'.format(result)
    except MathError as e:
        return str(e)

def exec_math(exp):
    #print(exp)
    f = partial(do_math, exp)
    p = multiprocessing.Process(target=f)
    p.start()
    p.join(1)
    if p.is_alive():
        result = 'Error: expression too complex. Try something simpler.'
        p.terminate()
        p.join()
    else:
        result = f()
    return result

async def run_math(exp, loop):
    future = loop.run_in_executor(None, exec_math, exp)
    try:
        result = await asyncio.wait_for(future, 2.2, loop=loop)
    except asyncio.TimeoutError:
        result = 'Error: expression too complex. That would have taken a while. Try something simpler.'
    return result
    

class Math():
    """Because who doesn't like to ~~have fun~~do math?"""
    def __init__(self, bot):
        
        self.loop = asyncio.new_event_loop()
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    @commands.command(name='math', aliases=['='])
    async def math(self, ctx, *math):
        
        exp=' '.join(math)
        result = await run_math(exp, self.loop)
        # result = await do_math(' '.join(math))
        asyncio.ensure_future(ctx.send(result[0:1999]))

def setup(bot):
    cog = Math(bot)
    bot.add_cog(cog)
