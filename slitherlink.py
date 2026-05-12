#!/usr/bin/env python3
# slitherlink.py: Template para implementação do projeto de Inteligência Artificial 2025/2026.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 114962 Eduardo Rocha
# 113786 Sofia Rodrigues

import random, copy
from sys import stdin
from collections import defaultdict

import utils
from utils import *

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class SlitherlinkState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = SlitherlinkState.state_id
        SlitherlinkState.state_id += 1
    
    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe

class Board:
    """Representação interna de um tabuleiro de Slitherlink."""

    def __init__(self, board_data: dict, rows: int, cols: int):
        self.board = board_data
        self.rows = rows
        self.cols = cols

    def adjacent_cell(self, cell: tuple) -> list:
        """
        Retorna uma lista de tuplos (coordenadas) das células adjacentes 
        que existem dentro dos limites do tabuleiro.
        """
        row, col = cell
        adjacents = []

        # Definição dos movimentos: (delta_row, delta_col)
        # Cima, Baixo, Esquerda, Direita
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            neighbor = (row + dr, col + dc)
            
            # Verifica se o vizinho está dentro dos limites do dicionário
            if neighbor in self.board:
                adjacents.append(neighbor)
        
        return adjacents

    def get_cell_edges(self, row:int, column:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""
        return [('h', row, column), ('h', row + 1, column), ('v', row, column), ('v', row, column + 1)]

    def get_active_edges(self, row: int, column: int) -> list:
        """Devolve o número de arestas ativas da célula enviada no argumento"""
        
        todas_arestas = self.get_cell_edges(row, column)
        
        arestas_ativas = []
        
        for aresta in todas_arestas:
            if aresta in self.active_edges:
                arestas_ativas.append(aresta)
            
        return len(arestas_ativas)
    
    def get_inactive_edges(self, row: int, column: int) -> list:
        """Devolve o número de arestas inativas da célula enviada no argumento"""
        
        todas_arestas = self.get_cell_edges(row, column)
        
        arestas_inativas = []
        
        for aresta in todas_arestas:
            if aresta not in self.active_edges:
                arestas_inativas.append(aresta)
            
        return len(arestas_inativas)

    @staticmethod
    def parse_instance():
        board_data = {}
        rows = cols = 0
        top = right = bottom = left = 0
        
        for row_index, line in enumerate(stdin):
            row = line.split()
            
            # O número de colunas é o tamanho da linha (assumindo que a grelha é uniforme)
            cols = len(row) 
            # Cada vez que lemos uma linha, o total de linhas aumenta
            rows = row_index + 1 
            
            for col_index, value in enumerate(row):
                board_data[(row_index, col_index)] = [value, top, right, bottom, left]
                
        # Passamos o dicionário, o total de linhas e o total de colunas
        return Board(board_data, rows, cols)

    def print_instance(self):
        """Imprime o tabuleiro no formato indicado no enunciado."""
        for r in range(self.rows):
            # 1. ''.join(...) junta os 4 limites da célula (ex: 0000)
            # 2. ' '.join(...) junta todas as células da linha com um espaço a separá-las
            print(' '.join(''.join(str(edge) for edge in self.board[(r, c)][1:]) for c in range(self.cols)))

    def print_dicionario(dicionario: dict):
        """
        Imprime todas as chaves e os respetivos valores de um dicionário 
        linha a linha para facilitar a leitura.
        """
        if not dicionario:
            print("O dicionário está vazio.")
            return

        print(f"--- Conteúdo do Dicionário ({len(dicionario)} itens) ---")
        
        # .items() devolve um tuplo com (chave, valor) para cada elemento
        for chave, valor in dicionario.items():
            print(f"Chave: {chave} -> Valor: {valor}")
            
        print("-" * 40)


class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        # TODO
        self.gui = gui

    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    board = Board.parse_instance()

    print(board.adjacent_cell((2, 1)))
    board.print_instance()
    board.print_dicionario()


    """problem = Slitherlink(board)

    s0 = SlitherlinkState(board)

    s1 = problem.result(s0, [('h', 2, 1), ('v', 2, 1), ('v', 2, 2)])

    s1.board.print_instance()"""


