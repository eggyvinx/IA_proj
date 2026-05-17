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
                # Obtém os 4 últimos itens e substitui -1 por 0
                sublista = [0 if x == -1 else x for x in self.board[(r, c)][-4:]]
                
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

    def _mark_zeros_forbidden(self, state: SlitherlinkState):
        """
        Marca as arestas de células com '0' como proibidas (-1) no dicionário.
        Isto previne que estas arestas sejam retornadas como ações.
        """
        board_dict = state.board.board
        for (r, c), data in board_dict.items():
            # data[0] é o valor da célula (string)
            if data[0] == '0':
                # Atualizar a própria célula (Top: 1, Right: 2, Bottom: 3, Left: 4)
                data[1] = data[2] = data[3] = data[4] = -1
                
                # Sincronizar também o estado com as células adjacentes que partilham a aresta
                if (r - 1, c) in board_dict: board_dict[(r - 1, c)][3] = -1 # Bottom da célula acima
                if (r, c + 1) in board_dict: board_dict[(r, c + 1)][4] = -1 # Left da célula à direita
                if (r + 1, c) in board_dict: board_dict[(r + 1, c)][1] = -1 # Top da célula abaixo
                if (r, c - 1) in board_dict: board_dict[(r, c - 1)][2] = -1 # Right da célula à esquerda

    def _is_edge_forbidden(self, board_dict: dict, orientation: str, r: int, c: int) -> bool:
        """
        Verifica se a aresta foi marcada como proibida (-1) numa iteração anterior.
        """
        if orientation == 'h':
            if (r, c) in board_dict and board_dict[(r, c)][1] == -1: return True
            if (r - 1, c) in board_dict and board_dict[(r - 1, c)][3] == -1: return True
        elif orientation == 'v':
            if (r, c) in board_dict and board_dict[(r, c)][4] == -1: return True
            if (r, c - 1) in board_dict and board_dict[(r, c - 1)][2] == -1: return True
        return False

    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de arestas ativáveis seguindo estratégias avançadas do Slitherlink."""
        valid_actions = []
        board = state.board
        
        # 1. Marcar células com 0 como proibidas (-1)
        self._mark_zeros_forbidden(state)
        
        # 2. ESTRATÉGIA C: Verificar '3's nos cantos do tabuleiro
        corners = [
            (1, 1, [('h', 1, 1), ('v', 1, 1)]), 
            (1, board.cols, [('h', 1, board.cols), ('v', 1, board.cols + 1)]), 
            (board.rows, 1, [('h', board.rows + 1, 1), ('v', board.rows, 1)]), 
            (board.rows, board.cols, [('h', board.rows + 1, board.cols), ('v', board.rows, board.cols + 1)]) 
        ]
        for r, c, mandatory_edges in corners:
            if (r, c) in board.board and board.board[(r, c)][0] == '3':
                corner_actions = []
                for orient, er, ec in mandatory_edges:
                    if not self._is_edge_active(board, orient, er, ec) and not self._is_edge_forbidden(board.board, orient, er, ec):
                        if self._is_action_legal(state, orient, er, ec):
                            corner_actions.append((orient, er, ec))
                if corner_actions:
                    return corner_actions

        # 3. ESTRATÉGIA D: Células Forçadas (Resolve "3 next to a 0" e "3s with an X")
        # Se as linhas ativas somadas com as livres vazias for igual ao exigido, as livres são forçadas.
        for r in range(1, board.rows + 1):
            for c in range(1, board.cols + 1):
                val = board.board[(r, c)][0]
                if val in '123':
                    req = int(val)
                    edges = [('h', r, c), ('h', r + 1, c), ('v', r, c), ('v', r, c + 1)]
                    active_count = 0
                    available_edges = []
                    
                    for orient, er, ec in edges:
                        if self._is_edge_active(board, orient, er, ec):
                            active_count += 1
                        elif not self._is_edge_forbidden(board.board, orient, er, ec):
                            available_edges.append((orient, er, ec))
                    
                    # Se as arestas em falta são exatamente as que estão disponíveis, ativamos todas!
                    if req - active_count == len(available_edges) and len(available_edges) > 0:
                        forced_actions = []
                        for orient, er, ec in available_edges:
                            if self._is_action_legal(state, orient, er, ec):
                                forced_actions.append((orient, er, ec))
                        if forced_actions:
                            return forced_actions

        # 4. ESTRATÉGIA E: Diagonal 2s (Transferring properties / Dedutibilidade Paralela)
        # Se uma aresta exterior de um 2 diagonal estiver ativada, a correspondente no outro 2 tem de refletir a continuidade.
        for r in range(1, board.rows):
            for c in range(1, board.cols):
                # Diagonal Top-Left para Bottom-Right
                if board.board[(r, c)][0] == '2' and board.board[(r + 1, c + 1)][0] == '2':
                    if self._is_edge_active(board, 'h', r, c) and not self._is_edge_active(board, 'h', r + 2, c + 1):
                        if self._is_action_legal(state, 'h', r + 2, c + 1): return [('h', r + 2, c + 1)]
                    if self._is_edge_active(board, 'v', r, c) and not self._is_edge_active(board, 'v', r + 1, c + 2):
                        if self._is_action_legal(state, 'v', r + 1, c + 2): return [('v', r + 1, c + 2)]
                
                # Diagonal Top-Right para Bottom-Left
                if board.board[(r, c + 1)][0] == '2' and board.board[(r + 1, c)][0] == '2':
                    if self._is_edge_active(board, 'h', r, c + 1) and not self._is_edge_active(board, 'h', r + 2, c):
                        if self._is_action_legal(state, 'h', r + 2, c): return [('h', r + 2, c)]
                    if self._is_edge_active(board, 'v', r, c + 2) and not self._is_edge_active(board, 'v', r + 1, c):
                        if self._is_action_legal(state, 'v', r + 1, c): return [('v', r + 1, c)]

        # 5. ESTRATÉGIA F: Padrões de 3s Adjacentes (Bónus muito forte no Slitherlink)
        # Dois '3' lado a lado forçam a aresta comum entre eles e as arestas exteriores paralelas.
        for r in range(1, board.rows + 1):
            for c in range(1, board.cols + 1):
                if board.board[(r, c)][0] == '3':
                    # 3s Adjacentes Horizontalmente
                    if (r, c + 1) in board.board and board.board[(r, c + 1)][0] == '3':
                        adj_3_actions = []
                        for orient, er, ec in [('v', r, c), ('v', r, c + 1), ('v', r, c + 2)]:
                            if not self._is_edge_active(board, orient, er, ec) and not self._is_edge_forbidden(board.board, orient, er, ec) and self._is_action_legal(state, orient, er, ec):
                                adj_3_actions.append((orient, er, ec))
                        if adj_3_actions: return adj_3_actions
                        
                    # 3s Adjacentes Verticalmente
                    if (r + 1, c) in board.board and board.board[(r + 1, c)][0] == '3':
                        adj_3_actions = []
                        for orient, er, ec in [('h', r, c), ('h', r + 1, c), ('h', r + 2, c)]:
                            if not self._is_edge_active(board, orient, er, ec) and not self._is_edge_forbidden(board.board, orient, er, ec) and self._is_action_legal(state, orient, er, ec):
                                adj_3_actions.append((orient, er, ec))
                        if adj_3_actions: return adj_3_actions

        # 6. ESTRATÉGIA B: Extensão de Caminhos (Grau 1)
        degree_1_vertices = []
        any_edge_active = False
        
        for r in range(1, board.rows + 2):
            for c in range(1, board.cols + 2):
                deg = self._get_vertex_degree(board, r, c)
                if deg > 0: any_edge_active = True
                if deg == 1: degree_1_vertices.append((r, c))
                    
        if any_edge_active:
            if degree_1_vertices:
                vr, vc = degree_1_vertices[0]
                potential_edges = [('h', vr, vc), ('h', vr, vc - 1), ('v', vr, vc), ('v', vr - 1, vc)]
                
                for orient, er, ec in potential_edges:
                    if orient == 'h' and (er < 1 or er > board.rows + 1 or ec < 1 or ec > board.cols): continue
                    if orient == 'v' and (er < 1 or er > board.rows or ec < 1 or ec > board.cols + 1): continue
                    
                    if not self._is_edge_active(board, orient, er, ec) and not self._is_edge_forbidden(board.board, orient, er, ec):
                        if self._is_action_legal(state, orient, er, ec):
                            valid_actions.append((orient, er, ec))
                
                return valid_actions
            else:
                return []
                
        # 7. ESTRATÉGIA A: Fallbacks / Início de Jogo 
        for r in range(1, board.rows + 1):
            for c in range(1, board.cols + 1):
                if board.board[(r, c)][0] == '3':
                    potential_edges = [('h', r, c), ('h', r + 1, c), ('v', r, c), ('v', r, c + 1)]
                    for orient, er, ec in potential_edges:
                        if not self._is_edge_forbidden(board.board, orient, er, ec):
                            if self._is_action_legal(state, orient, er, ec):
                                valid_actions.append((orient, er, ec))
                    if valid_actions: return valid_actions
                            
        for r in range(1, board.rows + 2):
            for c in range(1, board.cols + 1):
                if not self._is_edge_forbidden(board.board, 'h', r, c) and self._is_action_legal(state, 'h', r, c):
                    valid_actions.append(('h', r, c))
        for r in range(1, board.rows + 1):
            for c in range(1, board.cols + 2):
                if not self._is_edge_forbidden(board.board, 'v', r, c) and self._is_action_legal(state, 'v', r, c):
                    valid_actions.append(('v', r, c))
                    
        return valid_actions

    def _get_vertex_degree(self, board, vr, vc):
        """
        Conta quantas arestas ativas estão conectadas ao vértice (vr, vc).
        Um vértice pode ter no máximo 4 arestas à sua volta.
        """
        degree = 0
        # 1. Aresta horizontal que começa no vértice
        if self._is_edge_active(board, 'h', vr, vc): degree += 1
        # 2. Aresta horizontal que termina no vértice
        if self._is_edge_active(board, 'h', vr, vc - 1): degree += 1
        # 3. Aresta vertical que começa no vértice
        if self._is_edge_active(board, 'v', vr, vc): degree += 1
        # 4. Aresta vertical que termina no vértice
        if self._is_edge_active(board, 'v', vr - 1, vc): degree += 1
        
        return degree

    def _is_action_legal(self, state, orientation, r, c):
        """Verifica se ativar a aresta (r, c) viola restrições locais."""
        board = state.board

        # 1. VALIDAÇÃO DAS CÉLULAS (RESTRIÇÃO NUMÉRICA)
        # Identifica as duas células que partilham a aresta em análise
        if orientation == 'h':
            cells_to_check = [(r, c), (r - 1, c)]
        else:
            cells_to_check = [(r, c), (r, c - 1)]

        for cell_row, cell_col in cells_to_check:
            # Verifica se a célula existe nos limites do tabuleiro
            if (cell_row, cell_col) in board.board:
                cell_value = board.board[(cell_row, cell_col)][0]
                
                # Se a célula tiver uma pista numérica (0, 1, 2, 3)
                if cell_value.isdigit():
                    required_edges = int(cell_value)
                    active_edges = board.get_active_edges(cell_row, cell_col)
                    
                    # Se a célula já atingiu o número máximo de linhas permitidas,
                    # adicionar mais uma linha nesta aresta é ilegal.
                    if active_edges >= required_edges:
                        return False

        # 2. VALIDAÇÃO DOS VÉRTICES (GRAU DO CIRCUITO)
        # Identifica as coordenadas dos dois vértices (extremidades) da aresta
        if orientation == 'h':
            vertices = [(r, c), (r, c + 1)]
        else:
            vertices = [(r, c), (r + 1, c)]

        for vr, vc in vertices:
            # Se um dos vértices já tiver 2 linhas ligadas a ele, colocar uma
            # terceira linha criaria uma ramificação inválida no circuito.
            if self._get_vertex_degree(board, vr, vc) >= 2:
                return False

        # Se não violar nenhuma regra das células nem dos vértices, a ação é legal
        return True

    def result(self, state: SlitherlinkState, action):
        # 1. Create a deep copy to ensure the original state remains immutable
        new_state = copy.deepcopy(state)
        
        # Access the actual dictionary inside the Board object for easier use
        board_dict = new_state.board.board

        # Verifica se é uma lista de ações (exemplo 3) ou apenas uma
        if isinstance(action, tuple) and type(action[0]) is str:
            # É uma ação única no formato ('h', row, col)
            actions_to_apply = [action]
        else:
            # Já é uma lista de ações
            actions_to_apply = action

        # Aplica cada ação
        for act in actions_to_apply:
            orientation, row, col = act

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

    """board = Board.parse_instance()
    # Criar uma instância de Slytherlink:
    problem = Slitherlink(board)

    goal_node = depth_first_tree_search(problem)
    print("Solution:\n", goal_node.state.board.print_instance(), sep="")"""

    """"""

    """ # Ler grelha da figura 1a:
    board = Board.parse_instance()
    # Criar uma instância de Slytherlink:
    problem = Slitherlink(board)
    # Criar um estado com a configuração inicial:
    s0 = SlitherlinkState(board)
    # Aplicar as ações que resolvem a instância
    s2 = problem.result(s0, [ ('h', 2, 1), ('h', 2, 2), ('h', 2, 3), ('h', 2, 4), ('h', 2, 5), ('h', 2, 6), ('h', 3, 1), ('h', 3, 2), ('h', 3, 3), ('h', 3, 4), ('h', 3, 5), ('h', 3, 6), ('h', 4, 1), ('h', 4, 3), ('h', 4, 4), ('h', 4, 5), ('h', 4, 6), ('h', 5, 1), ('h', 5, 3), ('h', 5, 4), ('h', 5, 5), ('h', 5, 6), ('h', 6, 1), ('h', 6, 2), ('h', 6, 3), ('h', 6, 4), ('h', 6, 5), ('h', 6, 6), ('h', 7, 1), ('h', 7, 2), ('h', 7, 3), ('h', 7, 4), ('h', 7, 5), ('h', 7, 6), ('v', 1, 1), ('v', 1, 2), ('v', 1, 3), ('v', 1, 4), ('v', 1, 5), ('v', 1, 6), ('v', 1, 7), ('v', 2, 1), ('v', 2, 2), ('v', 2, 3), ('v', 2, 4), ('v', 2, 5), ('v', 2, 6), ('v', 2, 7), ('v', 3, 1), ('v', 3, 2), ('v', 3, 3), ('v', 3, 4), ('v', 3, 5), ('v', 3, 6), ('v', 3, 7), ('v', 4, 1), ('v', 4, 4), ('v', 4, 5), ('v', 4, 6), ('v', 4, 7), ('v', 5, 1), ('v', 5, 2), ('v', 5, 3), ('v', 5, 4), ('v', 5, 5), ('v', 5, 6), ('v', 5, 7), ('v', 6, 1), ('v', 6, 2), ('v', 6, 3), ('v', 6, 4), ('v', 6, 5), ('v', 6, 6), ('v', 6, 7)])
    print(s2.board.print_instance())

    s4 = problem.actions(s2)
    print(s4)
    # Verificar se foi atingida a solução
    #print(s2.board.print_instance())
    #print("\n")
    #print(s3.board.print_instance())"""
   
   ##comentatio a toa
   # Ler grelha da figura 1a:
    board = Board.parse_instance()
    # Criar uma instância de Slytherlink:
    problem = Slitherlink(board)
    # Obter o nó solução usando a procura em profundidade:
    goal_node = depth_first_tree_search(problem)
    # Verificar se foi atingida a solução
    print("Is goal?", problem.goal_test(goal_node.state))
    print("Solution:\n", goal_node.state.board.print(), sep="")


