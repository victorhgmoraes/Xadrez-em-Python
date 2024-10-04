import random

pontuacaoPeca = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}

pontuacaoCavalo = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

pontuacaoBispo = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

pontuacaoTorre = [[4, 3, 4, 4, 4, 4, 3, 4],
            [4, 4, 4, 4, 4, 4, 4, 4],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 2, 3, 4, 4, 3, 2, 1],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [4, 4, 4, 4, 4, 4, 4, 4],
            [4, 3, 4, 4, 4, 4, 3, 4]]

pontuacaoRainha = [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

pontuacaoPeaoBranco = [[8, 8, 8, 8, 8, 8, 8, 8],
                [8, 8, 8, 8, 8, 8, 8, 8],
                [5, 6, 6, 7, 7, 6, 6, 5],
                [2, 3, 3, 5, 5, 3, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 1, 1, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0]]

pontuacaoPeaoPreto = [[0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 1, 1, 1],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 3, 5, 5, 3, 3, 2],
                [5, 6, 6, 7, 7, 6, 6, 5],
                [8, 8, 8, 8, 8, 8, 8, 8],
                [8, 8, 8, 8, 8, 8, 8, 8]]

PontuacoesDePecaPosicao = {"N": pontuacaoCavalo, "Q": pontuacaoRainha, "B": pontuacaoBispo, "R": pontuacaoTorre, "bP": pontuacaoPeaoPreto, 
                        "wP": pontuacaoPeaoBranco}

CHEQUEMATE = 1000
IMPASSE = 0
DEPTH = 3

"""
pega e retorna um movimento valido aleatorio
"""

def EncontrarMovimentoAleatorio(movimentosValidos):
    return movimentosValidos[random.randint(0, len(movimentosValidos)-1)]

'''
Encontrar melhor movimento, min max sem recursividade
'''

def EncontrarMelhorMovimentoMinMaxSemREC(aj, movimentosValidos):
    MultiplicadorDeTurno = 1 if aj.whiteToMove else -1
    pontuacaoMinMaxOponente = CHEQUEMATE
    MelhorMovimentoJogador = None
    random.shuffle(movimentosValidos)
    for MovimentoJogador in movimentosValidos:
        aj.FazerMovimento(MovimentoJogador)
        movimentosOponente = aj.getMovimentosValidos()
        if aj.Impasse:
            pontuacaoMaxOponente = IMPASSE
        elif aj.Chequemate:
            pontuacaoMaxOponente = -CHEQUEMATE
        else:
            pontuacaoMaxOponente = -CHEQUEMATE
            for movimentoOponente in movimentosOponente:
                aj.FazerMovimento(movimentoOponente)
                aj.getMovimentosValidos()
                if aj.Chequemate:
                    pontuacao = CHEQUEMATE
                elif aj.Impasse:
                    pontuacao = IMPASSE
                else:
                    pontuacao = -MultiplicadorDeTurno * pontuacaoMaterial(aj.tabuleiro)
                if pontuacao > pontuacaoMaxOponente:
                    pontuacaoMaxOponente = pontuacao
                aj.DesfazerMovimento()
        if pontuacaoMaxOponente < pontuacaoMinMaxOponente:
            pontuacaoMinMaxOponente = pontuacaoMaxOponente
            MelhorMovimentoJogador = MovimentoJogador
        aj.DesfazerMovimento()
    return MelhorMovimentoJogador

'''
método auxiliar para fazer a primeira chamada recursiva
'''
def EncontrarMelhorMovimento(aj, movimentosValidos, returnQueue):
    global ProximoMovimento
    ProximoMovimento = None
    random.shuffle(movimentosValidos)
    # EncontrarMovimentoMinMax(aj, movimentosValidos, DEPTH, aj.whiteToMove)
    EncontrarMovimentoNegaMaxAlphaBeta(aj, movimentosValidos, DEPTH, -CHEQUEMATE, CHEQUEMATE, 1 if aj.whiteToMove else -1)
    returnQueue.put(ProximoMovimento)

def EncontrarMovimentoMinMax(aj, movimentosValidos, depth, whiteToMove):
    global ProximoMovimento
    if depth == 0:
        return pontuacaoMaterial(aj.tabuleiro)
    
    if whiteToMove:
        pontuacaoMax = -CHEQUEMATE
        for mover in movimentosValidos:
            aj.FazerMovimento(mover)
            ProximosMovimentos = aj.getMovimentosValidos()
            pontuacao = EncontrarMovimentoMinMax(aj, ProximosMovimentos, depth - 1, False)
            if pontuacao > pontuacaoMax:
                pontuacaoMax = pontuacao
                if depth == DEPTH:
                    ProximoMovimento = mover
                aj.DesfazerMovimento()
            return pontuacaoMax
        
    else:
        pontuacaoMin = CHEQUEMATE
        for mover in movimentosValidos:
            aj.FazerMovimento(mover)
            ProximosMovimentos = aj.getMovimentosValidos()
            pontuacao = EncontrarMovimentoMinMax(aj, ProximosMovimentos, depth - 1, True)
            if pontuacao < pontuacaoMin:
                pontuacaoMin = pontuacao
                if depth == DEPTH:
                    ProximoMovimento = mover
            aj.DesfazerMovimento()
        return pontuacaoMin

def EncontrarMovimentoNegaMaxAlphaBeta(aj, movimentosValidos, depth, alpha, beta, MultiplicadorDeTurno):
    global ProximoMovimento
    if depth == 0:
        return MultiplicadorDeTurno * pontuacaoTabuleiro(aj)
    # mover ordem - implementar mais tarde
    pontuacaoMax = -CHEQUEMATE
    for mover in movimentosValidos:
        aj.FazerMovimento(mover)
        ProximosMovimentos = aj.getMovimentosValidos()
        pontuacao = -EncontrarMovimentoNegaMaxAlphaBeta(aj, ProximosMovimentos, depth - 1, -beta, -alpha, -MultiplicadorDeTurno)
        if pontuacao > pontuacaoMax:
            pontuacaoMax = pontuacao
            if depth == DEPTH:
                ProximoMovimento = mover
        aj.DesfazerMovimento()
        if pontuacaoMax > alpha:
            alpha = pontuacaoMax
        if alpha >= beta:
            break
    return pontuacaoMax
    
'''
Uma pontuação positiva é boa para as brancas, uma negativa é boa para as pretas
'''
def pontuacaoTabuleiro(aj):
    if aj.Chequemate:
        if aj.whiteToMove:
            return -CHEQUEMATE #pretas vencem
        else:
            return CHEQUEMATE #brancas vencem
    elif aj.Impasse:
        return IMPASSE
    
    pontuacao = 0
    for l in range(len(aj.tabuleiro)):
        for c in range(len(aj.tabuleiro[l])):
            quad = aj.tabuleiro[l][c]
            if quad != "--":
                #pontuação de acordo com a posição
                PontuacaoDePecaPosicao = 0
                if quad[1] != "K": #sem tabela posicional para rei
                    if quad[1] == "P": #para peões
                        PontuacaoDePecaPosicao = PontuacoesDePecaPosicao[quad][l][c]
                    else: #para outras peças
                        PontuacaoDePecaPosicao = PontuacoesDePecaPosicao[quad[1]][l][c]

                if quad[0] == 'w':
                    pontuacao += pontuacaoPeca[quad[1]] + PontuacaoDePecaPosicao
                elif quad[0] == 'b':
                    pontuacao -= pontuacaoPeca[quad[1]] + PontuacaoDePecaPosicao

    return pontuacao


'''
Pontuar o tabuleiro beseado no material
'''
def pontuacaoMaterial(tabuleiro):
    pontuacao = 0
    for l in tabuleiro:
        for quad in l:
            if quad[0] == 'w':
                pontuacao += pontuacaoPeca[quad[1]]
            elif quad[0] == 'b':
                pontuacao -= pontuacaoPeca[quad[1]]
            
    return pontuacao
