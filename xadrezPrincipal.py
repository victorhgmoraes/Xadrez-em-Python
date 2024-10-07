import pygame as x
import xadrezBack, IAXadrez
import sys
from multiprocessing import Process, Queue

LARGURATABULEIRO = ALTURATABULEIRO = 612
LARGURAPAINELMOVELOG = 250
ALTURAPAINELMOVELOG = ALTURATABULEIRO #// 1/8 * 7
LARGURAINFORMACOESJOGO = LARGURATABULEIRO + LARGURAPAINELMOVELOG
DIMENSAO = 8
SQ_SIZE = ALTURATABULEIRO // DIMENSAO
ALTURAINFORMACOESJOGO = SQ_SIZE
MAX_FPS = 15 #15 de acordo com o video
IMAGENS = {}

x.mixer.init()  # Inicializa o mixer de som
SomMovimento = x.mixer.Sound('C:/Users/Wilson/Desktop/Xadrez/sons/MovimentoPeca.mp3')  # Carrega o som

def CarregarImagens():
    pecas = ['wP','wR','wQ','wK','wN','wB','bP','bR','bN','bB','bK','bQ']
    for peca in pecas:
        IMAGENS[peca] = x.transform.scale(x.image.load("imagens/" + peca + ".png"), (SQ_SIZE, SQ_SIZE))
        #É possível acessar uma imagem dizendo'IMAGES['wP']'

def Principal():
    x.init()
    tela = x.display.set_mode((LARGURATABULEIRO + LARGURAPAINELMOVELOG, ALTURAINFORMACOESJOGO + ALTURATABULEIRO))
    # Chamar a seleção do modo de jogo
    JogadorUm, JogadorDois = DesenharModoJogo(tela)
    if JogadorUm is None and JogadorDois is None:
        return  # Caso o jogador feche o jogo na tela de seleção, encerrar o programa
    tempoSelecionado = SelecionarTempoDeJogo(tela)
    tempoJogador1 = tempoSelecionado * 60  # Tempo em segundos
    tempoJogador2 = tempoSelecionado * 60
    ultimoTempo = x.time.get_ticks()  # Marcar o tempo inicial
    if tempoSelecionado is None:
        return  # Se o jogador fechar a tela, encerre o programa
    tempo = x.time.Clock()
    tela.fill(x.Color("white"))
    MoveLogFonte = x.font.SysFont("Arial", 14, False, False)
    aj = xadrezBack.ArmazenamentoJogo()
    MovimentosValidos = aj.getMovimentosValidos()
    MovimentoFeito = False #variavel flag para quando um movimento é feito
    animar = False # variavel flag para quando formos animar um movimento
    CarregarImagens()
    #apenas fazer 1 vez, antes do looping while
    running = True
    QuadSelecionado = () #nenhum quadrado selecionado, manter informação do ultimo clique do usuário (tupla: (linha, coluna))
    CliquesJogador = [] #manter informação dos cliques do jogador (2 tuplas [(6,4),(4,4)])
    FimDoJogo = False
    IAPensando = False
    ProcessoEncontrarMovimento = None
    MovimentoDesfeito = False
    cronometroIniciado = False  # Flag para indicar se o cronômetro já foi iniciado
    vitorias_jogador1 = 0
    vitorias_jogador2 = 0
    while running:
        TurnoPessoa = (aj.whiteToMove and JogadorUm) or (not aj.whiteToMove and JogadorDois)
        botao_empate = DesenharInformacoesJogo(tela, aj, 0, 0, tempoJogador1, tempoJogador2, vitorias_jogador1, vitorias_jogador2)
        for e in x.event.get():
            if e.type == x.QUIT:
                x.quit()
                sys.exit()
            #mouse handler
            elif e.type == x.MOUSEBUTTONDOWN:
                pos = x.mouse.get_pos()
                if botao_empate.collidepoint(pos):
                    # Tratar clique no botão de empate
                    DesenharTextoFimDeJogo(tela, 'Empate!')
                    x.display.update()
                    x.time.delay(3000)  # Pausa para o jogador ver a mensagem
                    FimDoJogo = True  # Define que o jogo terminou
                elif not FimDoJogo:
                    localizacao = x.mouse.get_pos() #posição do mouse
                    col = localizacao[0]//SQ_SIZE
                    linha = localizacao[1]//SQ_SIZE
                    if QuadSelecionado == (linha, col) or col >= 8: #O usuário clicou no mesmo quadrado duas vezes
                        QuadSelecionado = () #deselecionar
                        CliquesJogador = [] #limpar cliques do jogador
                    else:
                        QuadSelecionado = (linha, col)
                        CliquesJogador.append(QuadSelecionado) #append nos dois primeiro e segundon cliques
                    if len(CliquesJogador) == 2 and TurnoPessoa: #depois do segundo clique
                        mover = xadrezBack.Movimento(CliquesJogador[0], CliquesJogador[1], aj.tabuleiro)
                        print(mover.getNotacaoXadrez())
                        for i in range(len(MovimentosValidos)):
                            if mover == MovimentosValidos[i]:
                                FimDoJogo = aj.FazerMovimento(MovimentosValidos[i], tela)
                                MovimentoFeito = True
                                animar = True
                                QuadSelecionado = () #resetar cliques do usuário
                                CliquesJogador = []
                                if not cronometroIniciado:  # Iniciar cronômetro após o primeiro movimento
                                    cronometroIniciado = True
                        if not MovimentoFeito:
                            CliquesJogador = [QuadSelecionado]
            #key handlers
            elif e.type == x.KEYDOWN:
                if e.key == x.K_z: #desfaz quando 'z' é pressionado
                    aj.DesfazerMovimento()
                    MovimentoFeito = True
                    animar = False
                    FimDoJogo = False
                    if IAPensando:
                        ProcessoEncontrarMovimento.terminate()
                        IAPensando = False
                    MovimentoDesfeito = True
                if e.key == x.K_r: #resetar o tabuleiro quando a tecla 'r' é pressionada
                    aj = xadrezBack.ArmazenamentoJogo()
                    MovimentosValidos = aj.getMovimentosValidos()
                    QuadSelecionado = ()
                    CliquesJogador = []
                    MovimentoFeito = False
                    animar = False
                    FimDoJogo = False
                    if IAPensando:
                        ProcessoEncontrarMovimento.terminate()
                        IAPensando = False
                    MovimentoDesfeito = True
                    # Reiniciar os cronômetros
                    tempoJogador1 = tempoSelecionado * 60  # Reiniciar tempo do jogador 1
                    tempoJogador2 = tempoSelecionado * 60  # Reiniciar tempo do jogador 2
                    cronometroIniciado = False  # Redefinir a flag do cronômetro
        #Localizador de movimento IA
        if not FimDoJogo and not TurnoPessoa and not MovimentoDesfeito:
            if not IAPensando:
                IAPensando = True
                print("Pensando...")
                returnQueue = Queue() #usado para passar dados entre sequencias de programas
                ProcessoEncontrarMovimento = Process(target = IAXadrez.EncontrarMelhorMovimento, args = (aj, MovimentosValidos, returnQueue))
                ProcessoEncontrarMovimento.start() #chama EncontrarMelhorMovimento(aj, movimentosValidos, returnQueue)
                
            if not ProcessoEncontrarMovimento.is_alive():
                MovimentoIA = returnQueue.get()
                if MovimentoIA is None:
                    MovimentoIA = IAXadrez.EncontrarMovimentoAleatorio(MovimentosValidos)
                aj.FazerMovimento(MovimentoIA)
                MovimentoFeito = True
                animar = True
                IAPensando = False

        if MovimentoFeito:
            if animar:
                MovimentoAnimado(aj.MoveLog[-1], tela, aj.tabuleiro, tempo)
            MovimentosValidos = aj.getMovimentosValidos()
            MovimentoFeito = False
            animar = False
            MovimentoDesfeito = False

        tempoAtual = x.time.get_ticks()
        deltaTempo = (tempoAtual - ultimoTempo) / 1000  # Diferença em segundos
        ultimoTempo = tempoAtual

        if aj.whiteToMove:  # Turno do jogador 1 (brancas)
            tempoJogador1 -= deltaTempo if cronometroIniciado else 0
        else:  # Turno do jogador 2 (pretas)
            tempoJogador2 -= deltaTempo if cronometroIniciado else 0

        FazerJogo(tela, aj, MovimentosValidos, QuadSelecionado, MoveLogFonte)
        DesenharInformacoesJogo(tela, aj, 0, 0, tempoJogador1, tempoJogador2, vitorias_jogador1, vitorias_jogador2)

        if tempoJogador1 <= 0:
            if not FimDoJogo:
                FimDoJogo = True
                vitorias_jogador2 += 1  # Incrementar vitórias do jogador 2
                DesenharTextoFimDeJogo(tela, 'Pretas vencem por tempo')
                # Pausa por 3000 milissegundos (3 segundos)
                x.display.update()  # Atualiza a tela para mostrar a mensagem
                x.time.delay(3000)  # Atraso de 3 segundos antes de prosseguir
        elif tempoJogador2 <= 0:
            if not FimDoJogo:
                FimDoJogo = True
                vitorias_jogador1 += 1  # Incrementar vitórias do jogador 1
                DesenharTextoFimDeJogo(tela, 'Brancas vencem por tempo')
                # Pausa por 3000 milissegundos (3 segundos)
                x.display.update()  # Atualiza a tela para mostrar a mensagem
                x.time.delay(3000)  # Atraso de 3 segundos antes de prosseguir
        # Verifica se houve chequemate, impasse, empate por 50 movimentos, ou insuficiência de material
        if aj.Chequemate or aj.Impasse or aj.Empate50Movimentos or aj.verificar_empate_por_insuficiencia_material(aj.tabuleiro):
            if not FimDoJogo:
                FimDoJogo = True
                if aj.Empate50Movimentos:
                    DesenharTextoFimDeJogo(tela, 'Empate por 50 movimentos')
                elif aj.Impasse: 
                    DesenharTextoFimDeJogo(tela, 'Empate por Afogamento')
                elif aj.verificar_empate_por_insuficiencia_material(aj.tabuleiro):
                    DesenharTextoFimDeJogo(tela, 'Empate por insuficiência de material')
                else:
                    # Caso de chequemate
                    vitorias_jogador2 += 1 if aj.whiteToMove else 0
                    vitorias_jogador1 += 1 if not aj.whiteToMove else 0
                    DesenharTextoFimDeJogo(tela, 'Pretas vencem por chequemate' if aj.whiteToMove else 'Brancas vencem por chequemate')
                
                # Pausa de 3 segundos para mostrar a mensagem de fim do jogo
                x.display.update()  # Atualiza a tela para mostrar a mensagem
                x.time.delay(3000)  # Atraso de 3 segundos antes de prosseguir

        # Atualização da tela e controle de FPS
        tempo.tick(MAX_FPS)
        x.display.flip()

'''
Responsável pela parte gráfica
'''

def FazerJogo(tela, aj, MovimentosValidos, QuadSelecionado, MoveLogFonte):
    # Ajuste as coordenadas para onde as informações do jogo serão desenhadas
    x_offset = 0  # Ajuste conforme necessário, a posição X para desenhar as informações do jogo
    y_offset = ALTURATABULEIRO + 10  # Posição Y para desenhar as informações do jogo, logo abaixo do tabuleiro
    DesenharTabuleiro(tela) #desenhar quadrados
    QuadradosBrilhantes(tela, aj, MovimentosValidos, QuadSelecionado)
    DesenharPecas(tela, aj.tabuleiro) #desenhar peças no topo dos quadrados
    DesenharMoveLog(tela, aj, MoveLogFonte)

def checar_empate_repeticao(tela, aj):
    if aj.verificar_repeticao_movimentos():
        DesenharTextoFimDeJogo(tela, 'Repetição de 3 movimentos detectada. \n Declarar empate?')
        empate = DesenharBotaoEmpate3Movimentos(tela)
        if empate:
            return True  # Retorna True se o jogador declarar empate
    return False

"""
Função para desenhar botões 'Sim' e 'Não' para o empate por repetição de três movimentos.
Retorna True se o jogador escolher empatar, False caso contrário.
"""

def DesenharBotaoEmpate3Movimentos(tela):
    fonte = x.font.SysFont("Arial", 36, True, False)
    textoSim = fonte.render("Sim", True, x.Color("white"))
    textoNao = fonte.render("Não", True, x.Color("white"))

    larguraBotao = textoSim.get_width() + 50
    alturaBotao = textoSim.get_height() + 20

    distanciaAbaixoTexto = 80
    botaoSim = x.Rect(LARGURATABULEIRO // 2 - larguraBotao // 2 - 70, ALTURATABULEIRO // 2 + distanciaAbaixoTexto, larguraBotao, alturaBotao)
    botaoNao = x.Rect(LARGURATABULEIRO // 2 + larguraBotao // 2 - 40, ALTURATABULEIRO // 2 + distanciaAbaixoTexto, larguraBotao, alturaBotao)

    desenharBotao(tela, botaoSim, textoSim)
    desenharBotao(tela, botaoNao, textoNao)
    x.display.update()

    # Retorna os botões, e a lógica de verificação fica no loop principal
    return botaoSim, botaoNao

'''
Desenhar Seleção de modo de jogo
'''
def DesenharModoJogo(tela):
    fonteTitulo = x.font.SysFont("Arial", 48, True, False)
    fonteBotao = x.font.SysFont("Arial", 36, True, False)
    # Carrega e redimensiona a imagem de fundo
    imagemDeFundo = x.image.load("imagens/xadrez.jpg")  # Substitua pelo caminho da sua imagem
    imagemDeFundo = x.transform.scale(imagemDeFundo, (LARGURATABULEIRO + LARGURAPAINELMOVELOG, ALTURATABULEIRO + ALTURAINFORMACOESJOGO))
    # Desenha a imagem de fundo
    tela.blit(imagemDeFundo, (0, 0))
    # Desenha o título com sombra
    tituloTexto = fonteTitulo.render("Selecione o Modo de Jogo", True, x.Color("white"))
    sombraTitulo = fonteTitulo.render("Selecione o Modo de Jogo", True, x.Color("black"))
    # Centralizar o título
    tituloX = (LARGURATABULEIRO + LARGURAPAINELMOVELOG) // 2 - tituloTexto.get_width() // 2
    tituloY = ALTURATABULEIRO // 4
    tela.blit(sombraTitulo, (tituloX + 2, tituloY + 2))  # Sombra
    tela.blit(tituloTexto, (tituloX, tituloY))  # Texto principal
    # Desenhar os botões
    modoPessoaPessoa = fonteBotao.render("Pessoa vs Pessoa", True, x.Color("white"))
    modoPessoaIA = fonteBotao.render("Pessoa vs IA", True, x.Color("white"))
    # Configuração dos botões
    larguraBotao = max(modoPessoaPessoa.get_width(), modoPessoaIA.get_width()) + 40
    alturaBotao = modoPessoaPessoa.get_height() + 20
    botaoPessoaPessoa = x.Rect((LARGURATABULEIRO + LARGURAPAINELMOVELOG) // 2 - larguraBotao // 2, 
                               ALTURATABULEIRO // 2 - 60, larguraBotao, alturaBotao)
    botaoPessoaIA = x.Rect((LARGURATABULEIRO + LARGURAPAINELMOVELOG) // 2 - larguraBotao // 2, 
                           ALTURATABULEIRO // 2 + 60, larguraBotao, alturaBotao)
    # Desenho dos botões com bordas arredondadas
    desenharBotao(tela, botaoPessoaPessoa, modoPessoaPessoa)
    desenharBotao(tela, botaoPessoaIA, modoPessoaIA)
    x.display.flip()
    # Lógica de interação do usuário
    esperandoEscolha = True
    while esperandoEscolha:
        for e in x.event.get():
            if e.type == x.QUIT:
                return None, None  # Ao fechar a janela, retornar None para encerrar o jogo
            elif e.type == x.MOUSEBUTTONDOWN:
                pos = x.mouse.get_pos()

                # Verifica se o clique foi em um dos botões
                if botaoPessoaPessoa.collidepoint(pos):
                    return True, True  # Ambos jogadores são pessoas
                elif botaoPessoaIA.collidepoint(pos):
                    return True, False  # Jogador 1 é pessoa, Jogador 2 é IA
            # Efeito de hover (realce ao passar o mouse)
            pos = x.mouse.get_pos()
            if botaoPessoaPessoa.collidepoint(pos):
                desenharBotao(tela, botaoPessoaPessoa, modoPessoaPessoa, corBotao=(34, 40, 49))  # Realçar
            else:
                desenharBotao(tela, botaoPessoaPessoa, modoPessoaPessoa)
            if botaoPessoaIA.collidepoint(pos):
                desenharBotao(tela, botaoPessoaIA, modoPessoaIA, corBotao=(34, 40, 49))  # Realçar
            else:
                desenharBotao(tela, botaoPessoaIA, modoPessoaIA)
            x.display.flip()

# Função auxiliar para desenhar botões com bordas arredondadas
def desenharBotao(tela, retangulo, texto, corBotao=(57, 54, 70), corBorda=(109, 93, 110), larguraBorda=5):
    # Desenha a borda arredondada
    x.draw.rect(tela, corBorda, retangulo.inflate(10, 10), border_radius=15)
    # Desenha o fundo do botão
    x.draw.rect(tela, corBotao, retangulo, border_radius=15)
    # Renderiza o texto no centro do botão
    tela.blit(texto, (retangulo.x + (retangulo.width - texto.get_width()) // 2, 
                      retangulo.y + (retangulo.height - texto.get_height()) // 2))

def SelecionarTempoDeJogo(tela):
    fonteTitulo = x.font.SysFont("Arial", 48, True, False)
    fonteBotao = x.font.SysFont("Arial", 36, True, False)
    # Carrega e redimensiona a imagem de fundo
    imagemDeFundo = x.image.load("imagens/xadrez.jpg")  # Substitua pelo caminho da sua imagem
    imagemDeFundo = x.transform.scale(imagemDeFundo, (LARGURATABULEIRO + LARGURAPAINELMOVELOG, ALTURATABULEIRO + ALTURAINFORMACOESJOGO))
    # Desenha a imagem de fundo
    tela.blit(imagemDeFundo, (0, 0))
    # Desenha o título com sombra
    tituloTexto = fonteTitulo.render("Escolha o tempo de jogo", True, x.Color("white"))
    sombraTitulo = fonteTitulo.render("Escolha o tempo de jogo", True, x.Color("black"))
    # Centralizar o título
    tituloX = (LARGURATABULEIRO + LARGURAPAINELMOVELOG) // 2 - tituloTexto.get_width() // 2
    tituloY = ALTURATABULEIRO // 4
    tela.blit(sombraTitulo, (tituloX + 2, tituloY + 2))  # Sombra
    tela.blit(tituloTexto, (tituloX, tituloY))  # Texto principal
    # Desenhar os botões
    botao30Min = fonteBotao.render("30 minutos", True, x.Color("white"))
    botao10Min = fonteBotao.render("10 minutos", True, x.Color("white"))
    botao3Min = fonteBotao.render("3 minutos", True, x.Color("white"))
    # Configuração dos botões
    larguraBotao = max(botao30Min.get_width(), botao10Min.get_width(), botao3Min.get_width()) + 40
    alturaBotao = botao30Min.get_height() + 20
    # Adiciona a margem de 20 pixels entre os botões
    margem = 20
    botao30MinRect = x.Rect((LARGURATABULEIRO + LARGURAPAINELMOVELOG) // 2 - larguraBotao // 2, 
                             ALTURATABULEIRO // 2 - 60, larguraBotao, alturaBotao)
    botao10MinRect = x.Rect((LARGURATABULEIRO + LARGURAPAINELMOVELOG) // 2 - larguraBotao // 2, 
                            botao30MinRect.bottom + margem, larguraBotao, alturaBotao)
    botao3MinRect = x.Rect((LARGURATABULEIRO + LARGURAPAINELMOVELOG) // 2 - larguraBotao // 2, 
                            botao10MinRect.bottom + margem, larguraBotao, alturaBotao)
    # Desenho dos botões com bordas arredondadas
    desenharBotao(tela, botao30MinRect, botao30Min)
    desenharBotao(tela, botao10MinRect, botao10Min)
    desenharBotao(tela, botao3MinRect, botao3Min)
    x.display.flip()

    # Lógica de interação do usuário
    esperandoEscolha = True
    while esperandoEscolha:
        for e in x.event.get():
            if e.type == x.QUIT:
                return None  # Ao fechar a janela, retornar None para encerrar o jogo
            elif e.type == x.MOUSEBUTTONDOWN:
                pos = x.mouse.get_pos()
                # Verifica se o clique foi em um dos botões
                if botao30MinRect.collidepoint(pos):
                    return 30  # Retorna 30 minutos
                elif botao10MinRect.collidepoint(pos):
                    return 10  # Retorna 10 minutos
                elif botao3MinRect.collidepoint(pos):
                    return 3  # Retorna 3 minutos            
            # Efeito de hover (realce ao passar o mouse)
            pos = x.mouse.get_pos()
            if botao30MinRect.collidepoint(pos):
                desenharBotao(tela, botao30MinRect, botao30Min, corBotao=(34, 40, 49))  # Realçar
            else:
                desenharBotao(tela, botao30MinRect, botao30Min)               
            if botao10MinRect.collidepoint(pos):
                desenharBotao(tela, botao10MinRect, botao10Min, corBotao=(34, 40, 49))  # Realçar
            else:
                desenharBotao(tela, botao10MinRect, botao10Min)
            if botao3MinRect.collidepoint(pos):
                desenharBotao(tela, botao3MinRect, botao3Min, corBotao=(34, 40, 49))  # Realçar
            else:
                desenharBotao(tela, botao3MinRect, botao3Min)
            x.display.flip()

# Função auxiliar para desenhar botões com bordas arredondadas
def desenharBotao(tela, retangulo, texto, corBotao=(57, 54, 70), corBorda=(109, 93, 110), larguraBorda=5):
    # Desenha a borda arredondada
    x.draw.rect(tela, corBorda, retangulo.inflate(10, 10), border_radius=15)
    # Desenha o fundo do botão
    x.draw.rect(tela, corBotao, retangulo, border_radius=15)
    # Renderiza o texto no centro do botão
    tela.blit(texto, (retangulo.x + (retangulo.width - texto.get_width()) // 2, 
                      retangulo.y + (retangulo.height - texto.get_height()) // 2))

'''
Desenhar quadrados
'''

def DesenharTabuleiro(tela):
    global cores
    cores = [x.Color("White"), x.Color("grey")]
    for l in range(DIMENSAO):
        for c in range(DIMENSAO):
            cor = cores[((l + c) % 2)]
            x.draw.rect(tela, cor, x.Rect(c*SQ_SIZE, l*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def DesenharInformacoesJogo(tela, aj, x_offset, y_offset, tempoJogador1, tempoJogador2, vitorias_jogador1, vitorias_jogador2):
    # Ajuste a posição Y para colocar a faixa branca apenas na parte inferior da tela
    InformacoesJogoRect = x.Rect(0, ALTURATABULEIRO, LARGURAINFORMACOESJOGO, ALTURAINFORMACOESJOGO)
    x.draw.rect(tela, x.Color('white'), InformacoesJogoRect)
    # Assumindo que aj.pontuacaoBrancas, aj.pontuacaoPretas e aj.tempo_restante estão definidos
    fonte = x.font.SysFont("Arial", 32, True, False)
    # Garantir que o tempo não seja negativo
    if tempoJogador1 < 0:
        tempoJogador1 = 0
    if tempoJogador2 < 0:
        tempoJogador2 = 0
    tempoJogador1Texto = fonte.render(f"J1: {int(tempoJogador1//60)}:{int(tempoJogador1%60):02d}", True, x.Color('black'))
    tempoJogador2Texto = fonte.render(f"J2: {int(tempoJogador2//60)}:{int(tempoJogador2%60):02d}", True, x.Color('black'))
    texto_placar = fonte.render(f"Placar: {vitorias_jogador1} - {vitorias_jogador2}", True, x.Color('black'))
    # Exibir o tempo abaixo do tabuleiro, centralizado
    # Ajustando as posições dos textos
    tela.blit(tempoJogador1Texto, (LARGURATABULEIRO//2 - tempoJogador1Texto.get_width() - 150, ALTURATABULEIRO + 20 + y_offset))
    tela.blit(tempoJogador2Texto, (LARGURATABULEIRO//2 -100, ALTURATABULEIRO + 20 + y_offset))
    tela.blit(texto_placar, (LARGURATABULEIRO//2 + 90, ALTURATABULEIRO + 20 + y_offset))
    # Criar o botão de empate
    botao_empate_rect = x.Rect(LARGURATABULEIRO//2 + 305, ALTURATABULEIRO + y_offset, 255, 100)  # Botão centralizado
    x.draw.rect(tela, x.Color('lightgray'), botao_empate_rect)  # Cor do botão
    texto_empate = fonte.render("Empate", True, x.Color('black'))
    tela.blit(texto_empate, (botao_empate_rect.x + 70, botao_empate_rect.y + 20))  # Posiciona o texto no botão

    return botao_empate_rect  # Retorna o retângulo do botão

'''
quadrado brilhante selecionado e movimentos para peça selecionada
'''

def QuadradosBrilhantes(tela, aj, MovimentosValidos, QuadSelecionado):
    if (len(aj.MoveLog)) > 0:
        UltimoMovimento = aj.MoveLog[-1]
        s = x.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(x.Color('green'))
        tela.blit(s, (UltimoMovimento.ColFinal * SQ_SIZE, UltimoMovimento.LinhaFinal * SQ_SIZE))
    if QuadSelecionado != ():
        l, c = QuadSelecionado
        if aj.tabuleiro[l][c][0] == (
                'w' if aj.whiteToMove else 'b'):  # Quadrado selecionado é uma peça que pode ser movida
            # Quadrado brilhante selecionado
            s = x.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Valor de transparência 0 -> transparentw, 255 -> opaco
            s.fill(x.Color('blue'))
            tela.blit(s, (c * SQ_SIZE, l * SQ_SIZE))
            # movimentos brilhantes desse quadrado
            s.fill(x.Color('yellow'))
            for mover in MovimentosValidos:
                if mover.LinhaInicial == l and mover.ColInicial == c:
                    tela.blit(s, (mover.ColFinal * SQ_SIZE, mover.LinhaFinal * SQ_SIZE))
'''
Desenhar peças
'''
def DesenharPecas(tela, tabuleiro):
    for l in range(DIMENSAO):
        for c in range(DIMENSAO):
            peca = tabuleiro[l][c]
            if peca != "--": #não é quadrado vazio
                tela.blit(IMAGENS[peca], x.Rect(c*SQ_SIZE, l*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draws the move log.
"""
def DesenharMoveLog(tela, aj, fonte):
    MoveLogRect = x.Rect(LARGURATABULEIRO, 0, LARGURAPAINELMOVELOG, ALTURAPAINELMOVELOG)
    x.draw.rect(tela, x.Color('black'), MoveLogRect)
    MoveLog = aj.MoveLog
    MoveTextos = []
    for i in range(0, len(MoveLog), 2):
        MoverString = str(i // 2 + 1) + '. ' + str(MoveLog[i]) + " "
        if i + 1 < len(MoveLog):
            MoverString += str(MoveLog[i + 1]) + "  "
        MoveTextos.append(MoverString)

    MovimentosPorLinha = 3
    padding = 5
    LineSpacing = 2
    textoY = padding
    for i in range(0, len(MoveTextos), MovimentosPorLinha):
        texto = ""
        for j in range(MovimentosPorLinha):
            if i + j < len(MoveTextos):
                texto += MoveTextos[i + j]
        ObjetoTexto = fonte.render(texto, True, x.Color('white'))
        LocalizacaoTexto = MoveLogRect.move(padding, textoY)
        tela.blit(ObjetoTexto, LocalizacaoTexto)
        textoY += ObjetoTexto.get_height() + LineSpacing

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
        if mover.PecaCapturada != '--':
            if mover.eMovimentoEnpassant:
                LinhaEnpassant = mover.LinhaFinal + 1 if mover.PecaCapturada[0] == 'b' else mover.LinhaFinal - 1
                QuadFinal = x.Rect(mover.ColFinal * SQ_SIZE, LinhaEnpassant * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            tela.blit(IMAGENS[mover.PecaCapturada], QuadFinal)
        # desenhar peça movendo
        tela.blit(IMAGENS[mover.PecaMovida], x.Rect(c * SQ_SIZE, l * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        x.display.flip()
        tempo.tick(120)

def DesenharTextoFimDeJogo(tela, texto, deslocamento_vertical = 0):
    fonte = x.font.SysFont("Helvetica", 32, True, False)

    # Divide o texto em linhas
    linhas = texto.split('\n')

    # Desenha cada linha do texto
    for i, linha in enumerate(linhas):
        TextoObj = fonte.render(linha, 0, x.Color("gray"))
        LocalizacaoTexto = x.Rect(0, 0, LARGURATABULEIRO, ALTURATABULEIRO).move(
            LARGURATABULEIRO / 2 - TextoObj.get_width() / 2,
            ALTURATABULEIRO / 2 - TextoObj.get_height() / 2 + i * 40 + deslocamento_vertical  # Ajuste vertical baseado na linha
        )
        tela.blit(TextoObj, LocalizacaoTexto)

        # Adiciona sombra
        TextoObj = fonte.render(linha, 0, x.Color('black'))
        tela.blit(TextoObj, LocalizacaoTexto.move(2, 2))

def perguntar_empate_por_repeticao(tela):
    DesenharTextoFimDeJogo(tela, 'Repetição de 3 posições detectada. \n Declarar empate?')
    botaoSim, botaoNao = DesenharBotaoEmpate3Movimentos(tela)  # Desenha os botões "Sim" e "Não"
    
    empateEscolhido = False  # Flag para saber se o jogador já fez uma escolha
    
    while not empateEscolhido:
        for e in x.event.get():
            if e.type == x.QUIT:
                return False  # Sai do jogo, sem declarar empate
            elif e.type == x.MOUSEBUTTONDOWN:  # Verifica se um botão foi clicado
                pos = x.mouse.get_pos()  # Pega a posição do clique
                
                if botaoSim.collidepoint(pos):  # Jogador clicou em "Sim"
                    DesenharTextoFimDeJogo(tela, 'Empate por repetição de 3 posições', -70)  # Mostra a mensagem de empate
                    x.display.update()
                    x.time.delay(3000)  # Pausa para o jogador ver a mensagem final de empate
                    return True  # Jogador escolheu empatar, retornar True para indicar que o jogo deve terminar
                    
                elif botaoNao.collidepoint(pos):  # Jogador clicou em "Não"
                    return False  # Jogador escolheu continuar jogando

if __name__ == "__main__":
    Principal()