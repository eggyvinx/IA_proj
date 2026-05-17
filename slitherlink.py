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
        for dr, dc in orientations:
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
        return count(edge == 1 for edge in self.board[(row, column)][1:])
    
    def get_inactive_edges(self, row: int, column: int) -> list:
        """Devolve o número de arestas inativas da célula enviada no argumento"""
        return count(edge == 0 for edge in self.board[(row, column)][1:])

    @staticmethod
    def parse_instance():
        board_data = {}
        rows = cols = 0
        top = right = bottom = left = 0
        
        for row_index, line in enumerate(stdin, start=1):
            row = line.split()
            
            cols = len(row) 
            rows = row_index
            
            for col_index, value in enumerate(row, start=1):
                board_data[(row_index, col_index)] = [value, top, right, bottom, left]
                
        return Board(board_data, rows, cols)

    def print_instance(self):
       for r in range(1, self.rows + 1):
            elementos = []
            for c in range(1, self.cols + 1):
                # Obtém os 4 últimos itens: [0, 0, 0, 0]
                sublista = self.board[(r, c)][-4:]
                # Converte cada número para string e junta todos sem espaço: "0000"
                bloco = ''.join(map(str, sublista))
                elementos.append(bloco)
            
            # Junta os blocos de cada coluna com um espaço entre eles
            print(' '.join(elementos))
    

class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        self.initial_state = SlitherlinkState(board)
        super().__init__(self.initial_state)
        #might be needed later
        self.board = board

    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de arestas que podem ser ativadas."""
        valid_actions = []
        board = state.board
        
        # 1. Gerar potenciais arestas horizontais
        for r in range(1, board.rows + 2):
            for c in range(1, board.cols + 1):
                if not self._is_edge_active(board, 'h', r, c):
                    if self._is_action_legal(state, 'h', r, c):
                        valid_actions.append(('h', r, c))
                        
        # 2. Gerar potenciais arestas verticais
        for r in range(1, board.rows + 1):
            for c in range(1, board.cols + 2):
                if not self._is_edge_active(board, 'v', r, c):
                    if self._is_action_legal(state, 'v', r, c):
                        valid_actions.append(('v', r, c))
                        
        return valid_actions

    def _is_action_legal(self, state, orientation, r, c):
        """Verifica se ativar a aresta (r, c) viola restrições locais."""
        board = state.board
        
        # Exemplo de verificação de grau do vértice:
        # Se for horizontal ('h', r, c), liga os pontos (r, c) e (r, c+1)
        # Deves verificar se esses pontos já têm grau 2.
        # (Precisas de implementar uma função que conte o grau de um nó r,c)
        
        # Exemplo de verificação de número da célula:
        # Uma aresta horizontal ('h', r, c) afeta as células (r, c) e (r-1, c)
        # Se o número de arestas ativas nessas células já for o máximo, retorna False.
        
        return True # Se passar em todos os testes

    def result(self, state: SlitherlinkState, action):
        # 1. Create a deep copy to ensure the original state remains immutable
        new_state = copy.deepcopy(state)
        
        # Access the actual dictionary inside the Board object for easier use
        board_dict = new_state.board.board

        # A ação é apenas um tuplo (orientation, row, col), logo não precisamos de um for loop
        orientation, row, col = action

        if orientation == 'h':
            # Horizontal edge at (row, col) is the TOP of (row, col)
            if (row, col) in board_dict:
                board_dict[(row, col)][1] = 1 # Index 1 = Top
            
            # AND the BOTTOM of the cell above (row-1, col)
            if (row - 1, col) in board_dict:
                board_dict[(row - 1, col)][3] = 1 # Index 3 = Bottom
                
        elif orientation == 'v':
            # Vertical edge at (row, col) is the LEFT of (row, col)
            if (row, col) in board_dict:
                board_dict[(row, col)][4] = 1 # Index 4 = Left
                
            # AND the RIGHT of the cell to the left (row, col-1)
            if (row, col - 1) in board_dict:
                board_dict[(row, col - 1)][2] = 1 # Index 2 = Right
                
        return new_state
        

    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        
        board = state.board
        
        # 1. Verificar se todas as células com números têm a quantidade correta de arestas
        for r in range(1, board.rows + 1):
            for c in range(1, board.cols + 1):
                cell_value = board.board[(r, c)][0]
                
                # Ignorar células vazias (representadas por '.' ou similar no input)
                if cell_value.isdigit():
                    required_edges = int(cell_value)
                    active_edges = board.get_active_edges(r, c)
                    
                    if active_edges != required_edges:
                        return False
        return self.is_closed_circuit(state)

    def is_closed_circuit(self, state: SlitherlinkState) -> bool:
        """
        Verifica se as arestas ativas formam um único circuito fechado.
        """
        board = state.board
        node_degrees = defaultdict(int)
        active_edges = []

        # Mapear arestas e calcular graus dos vértices
        for r in range(1, board.rows + 2):
            for c in range(1, board.cols + 2):
                # Aresta Horizontal (nó r,c para r,c+1)
                if c <= board.cols and self._is_edge_active(board, 'h', r, c):
                    node_degrees[(r, c)] += 1
                    node_degrees[(r, c + 1)] += 1
                    active_edges.append(((r, c), (r, c + 1)))

                # Aresta Vertical (nó r,c para r+1,c)
                if r <= board.rows and self._is_edge_active(board, 'v', r, c):
                    node_degrees[(r, c)] += 1
                    node_degrees[(r + 1, c)] += 1
                    active_edges.append(((r, c), (r + 1, c)))

        if not active_edges:
            return False

        # Todos os nós no circuito devem ter grau 2
        for node, degree in node_degrees.items():
            if degree != 0 and degree != 2:
                return False

        # Garantir que existe apenas UM ciclo (conectividade via BFS)
        start_node = active_edges[0][0]
        visited = {start_node}
        queue = [start_node]
        
        while queue:
            curr = queue.pop(0)
            for n1, n2 in active_edges:
                neighbor = None
                if n1 == curr: neighbor = n2
                elif n2 == curr: neighbor = n1
                
                if neighbor and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # O número de nós visitados deve ser igual ao total de nós ativos
        active_nodes_count = sum(1 for d in node_degrees.values() if d == 2)
        return len(visited) == active_nodes_count

    def _is_edge_active(self, board, orientation, r, c):
        """Verifica se uma aresta está ativa consultando o dicionário do tabuleiro."""
        b = board.board
        if orientation == 'h':
            if (r, c) in b and b[(r, c)][1] == 1: return True
            if (r - 1, c) in b and b[(r - 1, c)][3] == 1: return True
        else:
            if (r, c) in b and b[(r, c)][4] == 1: return True
            if (r, c - 1) in b and b[(r, c - 1)][2] == 1: return True
        return False 



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
    # Criar uma instância de Slytherlink:
    problem = Slitherlink(board)

    goal_node = depth_first_tree_search(problem)
    print("Solution:\n", goal_node.state.board.print_instance(), sep="")

