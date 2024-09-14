import pygame as x
import xadrezBack

WIDTH = HEIGHT = 712
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #15 de acordo com o video
IMAGES = {}

def CarregarImagens():
    pecas = ['wP','wR','wQ','wK','wN','wB','bP','bR','bN','bB','bK','bQ']
    for peca in pecas:
        IMAGES[peca] = x.transform.scale(x.image.load("imagens/" + peca + ".png"), (SQ_SIZE, SQ_SIZE))
        #É possível acessar uma imagem dizendo'IMAGES['wP']'

def Principal():
    x.init()
    tela = x.display.set_mode((WIDTH, HEIGHT))
    tempo = x.time.Clock()
    tela.fill(x.Color("white"))
    aj = xadrezBack.ArmazenamentoJogo()
    movimentosValidos = aj.getMovimentosValidos()
    movimentoFeito = False #variavel flag para quando um movimento é feito
    animar = False # variavel flag para quando formos animar um movimento
    CarregarImagens()
    #apenas fazer 1 vez, antes do looping while
    running = True
    quadSelecionado = () #nenhum quadrado selecionado, manter informação do ultimo clique do usuário (tupla: (linha, coluna))
    CliquesJogador = [] #manter informação dos cliques do jogador (2 tuplas [(6,4),(4,4)])
    FimDoJogo = False
    while running:
        for e in x.event.get():
            if e.type == x.QUIT:
                running = False
            #mouse handler
            elif e.type == x.MOUSEBUTTONDOWN:
                if not FimDoJogo:
                    localizacao = x.mouse.get_pos() #posição do mouse
                    col = localizacao[0]//SQ_SIZE
                    linha = localizacao[1]//SQ_SIZE
                    if quadSelecionado == (linha, col): #O usuário clicou no mesmo quadrado duas vezes
                        quadSelecionado = () #deselecionar
                        CliquesJogador = [] #limpar cliques do jogador
                    else:
                        quadSelecionado = (linha, col)
                        CliquesJogador.append(quadSelecionado) #append nos dois primeiro e segundon cliques
                    if len(CliquesJogador) == 2: #depois do segundo clique
                        mover = xadrezBack.Movimento(CliquesJogador[0], CliquesJogador[1], aj.tabuleiro)
                        print(mover.pegarNotaçãoXadrez())
                        for i in range(len(movimentosValidos)):
                            if mover == movimentosValidos[i]:
                                aj.FazerMovimento(movimentosValidos[i])
                                movimentoFeito = True
                                animar = True
                                quadSelecionado = () #resetar cliques do usuário
                                CliquesJogador = []
                        if not movimentoFeito:
                            CliquesJogador = [quadSelecionado]
            #key handlers
            elif e.type == x.KEYDOWN:
                if e.key == x.K_z: #desfaz quando 'z' é pressionado
                    aj.DesfazerMovimento()
                    movimentoFeito = True
                    animar = False
                if e.key == x.K_r: #resetar o tabuleiro quando a tecla 'r' é pressionada
                    aj = xadrezBack.ArmazenamentoJogo()
                    movimentosValidos = aj.getMovimentosValidos()
                    quadSelecionado = ()
                    CliquesJogador = []
                    movimentoFeito = False
                    animar = False

        if movimentoFeito:
            if animar:
                MovimentoAnimado(aj.moveLog[-1], tela, aj.tabuleiro, tempo)
            movimentosValidos = aj.getMovimentosValidos()
            movimentoFeito = False
            animar = False

        FazerJogo(tela, aj, movimentosValidos, quadSelecionado)

        if aj.Chequemate:
            FimDoJogo = True
            if aj.whiteToMove:
                DesenharTexto(tela, 'Peças pretas vencem por chequemate')
            else:
                DesenharTexto(tela, 'Peças brancas vencem por chequemate')
        elif aj.Impasse:
            FimDoJogo = True
            DesenharTexto(tela, 'Afogamento')

        tempo.tick(MAX_FPS)
        x.display.flip()

'''
quadrado brilhante selecionado e movimentos para peça selecionada
'''

def QuadradosBrilhantes(tela, aj, movimentosValidos, quadSelecionado):
    if (len(aj.moveLog)) > 0:
        UltimoMovimento = aj.moveLog[-1]
        s = x.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(x.Color('green'))
        tela.blit(s, (UltimoMovimento.ColFinal * SQ_SIZE, UltimoMovimento.LinhaFinal * SQ_SIZE))
    if quadSelecionado != ():
        l, c = quadSelecionado
        if aj.tabuleiro[l][c][0] == (
                'w' if aj.whiteToMove else 'b'):  # Quadrado selecionado é uma peça que pode ser movida
            # Quadrado brilhante selecionado
            s = x.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Valor de transparência 0 -> transparentw, 255 -> opaco
            s.fill(x.Color('blue'))
            tela.blit(s, (c * SQ_SIZE, l * SQ_SIZE))
            # movimentos brilhantes desse quadrado
            s.fill(x.Color('yellow'))
            for mover in movimentosValidos:
                if mover.LinhaInicial == l and mover.ColInicial == c:
                    tela.blit(s, (mover.ColFinal * SQ_SIZE, mover.LinhaFinal * SQ_SIZE))
'''
Responsável pela parte gráfica
'''

def FazerJogo(tela, aj, movimentosValidos, quadSelecionado):
    DesenharTabuleiro(tela) #desenhar quadrados
    QuadradosBrilhantes(tela, aj, movimentosValidos, quadSelecionado)
    DesenharPecas(tela, aj.tabuleiro) #desenhar peças no topo dos quadrados

'''
Desenhar quadrados
'''

def DesenharTabuleiro(tela):
    global cores
    cores = [x.Color("White"), x.Color("grey")]
    for l in range(DIMENSION):
        for c in range(DIMENSION):
            cor = cores[((l + c) % 2)]
            x.draw.rect(tela, cor, x.Rect(c*SQ_SIZE, l*SQ_SIZE, SQ_SIZE, SQ_SIZE))
'''
Desenhar peças
'''
def DesenharPecas(tela, tabuleiro):
    for l in range(DIMENSION):
        for c in range(DIMENSION):
            peca = tabuleiro[l][c]
            if peca != "--": #não é quadrado vazio
                tela.blit(IMAGES[peca], x.Rect(c*SQ_SIZE, l*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animar movimento
'''
def MovimentoAnimado(mover, tela, tabuleiro, tempo):
    global cores
    dL = mover.LinhaFinal - mover.LinhaInicial
    dC = mover.ColFinal - mover.ColInicial
    FramesPorQuad = 10  # frames para mover um quadrado
    ContadorFrames = (abs(dL) + abs(dC)) * FramesPorQuad
    for frame in range(ContadorFrames + 1):
        l, c = (mover.LinhaInicial + dL * frame / ContadorFrames, mover.ColInicial + dC * frame / ContadorFrames)
        DesenharTabuleiro(tela)
        DesenharPecas(tela, tabuleiro)
        # apague a peça movida de seu quadrado final
        cor = cores[(mover.LinhaFinal + mover.ColFinal) % 2]
        QuadFinal = x.Rect(mover.ColFinal * SQ_SIZE, mover.LinhaFinal * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        x.draw.rect(tela, cor, QuadFinal)
        # desenhe a peça capturada no retângulo
        if mover.pecaGravada != '--':
            if mover.eMovimentoEnpassant:
                LinhaEnpassant = mover.LinhaFinal + 1 if mover.pecaGravada[0] == 'b' else mover.LinhaFinal - 1
                QuadFinal = x.Rect(mover.ColFinal * SQ_SIZE, LinhaEnpassant * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            tela.blit(IMAGES[mover.pecaGravada], QuadFinal)
        # desenhar peça movendo
        tela.blit(IMAGES[mover.pecaMovida], x.Rect(c * SQ_SIZE, l * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        x.display.flip()
        tempo.tick(60)

def DesenharTexto(tela, texto):
    fonte = x.font.SysFont("Helvetica", 32, True, False)
    TextoObj = fonte.render(texto, 0, x.Color("gray"))
    TextoLocalizacao = x.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - TextoObj.get_width() / 2, HEIGHT / 2 - TextoObj.get_height() / 2)
    tela.blit(TextoObj, TextoLocalizacao)
    TextoObj = fonte.render(texto, 0, x.Color('black'))
    tela.blit(TextoObj, TextoLocalizacao.move(2, 2))

if __name__ == "__main__":
    Principal()