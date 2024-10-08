import xadrezPrincipal
class ArmazenamentoJogo():
    def __init__(self):
        self.tabuleiro = [
            #tabuleiro em forma de lista 8x8 de 2 dimensões
            #composto por 2 caracteres onde representam as peças de acordo com a conotação atual do xadrez
            #1st caractere = color, 2nd = tipo da peça
            #"--" representa espaços em branco
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        self.FuncaoMovimentos = {'P' : self.getMovimentosPeao, 'R' : self.getMovimentosTorre, 'N' : self.getMovimentosCavalo,
                                'B' : self.getMovimentosBispo, 'Q' : self.getMovimentosRainha, 'K' : self.getMovimentosRei}
        self.whiteToMove = True
        self.MoveLog = []
        self.LocalizacaoReiBranco = (7, 4)
        self.LocalizacaoReiPreto = (0, 4)
        self.Chequemate = False
        self.Impasse = False
        self.em_Cheque = False
        self.pins = []
        self.cheques = []
        self.EnpassantPossivel = () #coordenadas para o quadrado onde o enpassant é possível
        self.EnpassantPossivelLog = [self.EnpassantPossivel]
        self.DireitoRoqueAtual = DireitosRoque(True, True, True, True)
        self.DireitosRoqueLog = [DireitosRoque(self.DireitoRoqueAtual.wks, self.DireitoRoqueAtual.bks,
                                                self.DireitoRoqueAtual.wqs, self.DireitoRoqueAtual.bqs)]
        self.Empate50Movimentos = False #Variavel para indicar empate
        #ESTE TIPO DE EMPATE NÃO FUNCIONA CONTRA IA, IMPROVAVEL A SUA IMPLEMENTAÇÃO PARA O MODO DE JOGO PLAYER VS IA
        self.Contador50Movimentos = 0  # Contador para rastrear a regra dos 50 movimentos
        self.HistoricoContadores = []
        self.pontuacaoBrancas = 0  # Inicializa a pontuação das peças brancas
        self.pontuacaoPretas = 0   # Inicializa a pontuação das peças pretas
        self.tempo_restante = 0
        self.historicoPosicoes = {}

    '''
    Pega um movimento como um parametro e executa(isso n funcionará para roques, promoção de peão e en-passant)
    '''
    def FazerMovimento(self, mover, tela = None, TocarSom = True):
        self.HistoricoContadores.append(self.Contador50Movimentos)
        self.tabuleiro[mover.LinhaInicial][mover.ColInicial] = "--"
        self.tabuleiro[mover.LinhaFinal][mover.ColFinal] = mover.PecaMovida
        self.MoveLog.append(mover)#guardar o movimento para poder voltar depois
        self.whiteToMove = not self.whiteToMove #trocar turno
        #atualiza a localização do rei se movido
        if TocarSom:
        # Toca o som do movimento da peça
            xadrezPrincipal.x.mixer.Sound.play(xadrezPrincipal.SomMovimento)

        # Se foi captura ou movimento de peão, resetar o contador
        if mover.PecaCapturada != '--' or mover.PecaMovida[1] == 'P':  
            self.Contador50Movimentos = 0
        else:
            self.Contador50Movimentos += 1

        # Verificar regra dos 50 movimentos (100 no total, 50 para cada lado)
        if self.Contador50Movimentos >= 100:  # Contagem inclui os dois jogadores
            self.Empate50Movimentos = True

        if mover.PecaMovida == 'wK':
            self.LocalizacaoReiBranco = (mover.LinhaFinal, mover.ColFinal)
        elif mover.PecaMovida == 'bK':
            self.LocalizacaoReiPreto = (mover.LinhaFinal, mover.ColFinal)

        #Promoção de Peão
        if mover.ePromocaoPeao:
            if tela is not None:
                peca_promovida = xadrezPrincipal.escolher_promocao(tela, mover.PecaMovida[0])
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal] = mover.PecaMovida[0] + peca_promovida
            else:
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal] = mover.PecaMovida[0] + 'Q'
        
        #Movimento Enpassant 
        if mover.eMovimentoEnpassant:
            self.tabuleiro[mover.LinhaInicial][mover.ColFinal] = '--' #capturando o peão

        #atualizar a variável enpassantPossivel
        if mover.PecaMovida[1] == 'P' and abs(mover.LinhaInicial - mover.LinhaFinal) == 2: #somente em avanço de peao de 2 quadrados
            self.EnpassantPossivel = ((mover.LinhaInicial + mover.LinhaFinal)//2, mover.ColInicial)
        else:
            self.EnpassantPossivel = ()

        #Movimento Roque
        if mover.eMovimentoRoque:
            if mover.ColFinal - mover.ColInicial == 2:  # movimento de roque do lado do rei
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal - 1] = self.tabuleiro[mover.LinhaFinal][
                    mover.ColFinal + 1]  # move a torre para o outro quadrado
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal + 1] = '--'  # apagar torre antiga
            else:  # movimento de roque do lado da rainha
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal + 1] = self.tabuleiro[mover.LinhaFinal][
                    mover.ColFinal - 2]  # move a torre para o outro quadrado
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal - 2] = '--'  # apagar torre antiga

        self.EnpassantPossivelLog.append(self.EnpassantPossivel)
        #Atualizar direitos de Roque - sempre que for uma torre ou um movimento de rei
        self.AtualizarDireitosRoque(mover)
        self.DireitosRoqueLog.append(DireitosRoque(self.DireitoRoqueAtual.wks, self.DireitoRoqueAtual.bks,
                                                self.DireitoRoqueAtual.wqs, self.DireitoRoqueAtual.bqs))
        
        # Atualiza o histórico de posições após o movimento
        self.atualizar_historico_posicoes()

        # Verificar repetição de 3 posições após o movimento
        if self.verificar_repeticao_posicoes() and tela is not None:
            if xadrezPrincipal.perguntar_empate_por_repeticao(tela):  # Se o jogador escolheu empatar
                return True  # Define FimDoJogo como True, finalizando o jogo
        return False  # Continua o jogo caso o empate não tenha sido escolhido
    
    '''
    desfazer o ultimo movimento feito
    '''
    def DesfazerMovimento(self):
        if len(self.MoveLog) != 0: #tenha certeza que há um movimento para desfazer
            mover = self.MoveLog.pop()
            self.tabuleiro[mover.LinhaInicial][mover.ColInicial] = mover.PecaMovida
            self.tabuleiro[mover.LinhaFinal][mover.ColFinal] = mover.PecaCapturada
            self.whiteToMove = not self.whiteToMove #trocar time de volta
            #Atualiza a localização do rei se preciso
            if mover.PecaMovida == 'wK':
                self.LocalizacaoReiBranco = (mover.LinhaInicial, mover.ColInicial)
            elif mover.PecaMovida == 'bK':
                self.LocalizacaoReiPreto = (mover.LinhaInicial, mover.ColInicial)
            #desfazer movimento enpassant
            if mover.eMovimentoEnpassant:
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal] = '--' #deixar os quadrados vazios
                self.tabuleiro[mover.LinhaInicial][mover.ColFinal] = mover.PecaCapturada
                self.EnpassantPossivel = (mover.LinhaFinal, mover.ColFinal)

            self.EnpassantPossivelLog.pop()
            self.EnpassantPossivel = self.EnpassantPossivelLog[-1]

            #desfazer avanço de peão de 2 quadrados
            if mover.PecaMovida[1] == 'P' and abs(mover.LinhaInicial - mover.LinhaFinal) == 2:
                self.EnpassantPossivel = ()
        #desfazer direitos de roque
        self.DireitosRoqueLog.pop() #desfazer do novo movimento de roqque do movimento que estamos desfazendo
        NovosDireitos = self.DireitosRoqueLog[-1] #pegar os direitosRoqueAtual para o ultimo da lista
        self.DireitoRoqueAtual = DireitosRoque(NovosDireitos.wks, NovosDireitos.bks, NovosDireitos.wqs, NovosDireitos.bqs)
        #desfazer Movimento Roque
        if mover.eMovimentoRoque:
            if mover.ColFinal - mover.ColInicial == 2:  # lado do rei
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal + 1] = self.tabuleiro[mover.LinhaFinal][mover.ColFinal - 1]
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal - 1] = '--'
            else:  # lado da rainha
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal - 2] = self.tabuleiro[mover.LinhaFinal][mover.ColFinal + 1]
                self.tabuleiro[mover.LinhaFinal][mover.ColFinal + 1] = '--'
        self.Chequemate = False
        self.Impasse = False
        if self.HistoricoContadores:
            #Restaure o contador do historico
            self.Contador50Movimentos = self.HistoricoContadores.pop()
    
    """
    Atualizar Direitos de Roque conforme o movimento
    """     
    def AtualizarDireitosRoque(self, mover):
        if mover.PecaCapturada == "wR":
            if mover.ColFinal == 0:  # torre esquerda
                self.DireitoRoqueAtual.wqs = False
            elif mover.ColFinal == 7:  # torre direita
                self.DireitoRoqueAtual.wks = False
        elif mover.PecaCapturada == "bR":
            if mover.ColFinal == 0:  # torre esquerda
                self.DireitoRoqueAtual.bqs = False
            elif mover.ColFinal == 7:  # torre direita
                self.DireitoRoqueAtual.bks = False

        if mover.PecaMovida == 'wK':
            self.DireitoRoqueAtual.wks = False
            self.DireitoRoqueAtual.wqs = False
        elif mover.PecaMovida == 'bK':
            self.DireitoRoqueAtual.bks = False
            self.DireitoRoqueAtual.bqs = False
        elif mover.PecaMovida == 'wR':
            if mover.LinhaInicial == 7:
                if mover.ColInicial == 0:  # torre esquerda
                    self.DireitoRoqueAtual.wqs = False
                elif mover.ColInicial == 7:  # torre direita
                    self.DireitoRoqueAtual.wks = False
        elif mover.PecaMovida == 'bR':
            if mover.LinhaInicial == 0:
                if mover.ColInicial == 0:  # torre esquerda
                    self.DireitoRoqueAtual.bqs = False
                elif mover.ColInicial == 7:  # torre direita
                    self.DireitoRoqueAtual.bks = False

    '''
    todos os movimentos considerando check 
    '''

    def getMovimentosValidos(self):
        if self.Empate50Movimentos:
            return [] # Não há mais movimentos válidos após o empate
        TempEnpassantPossivel = self.EnpassantPossivel
        TempDireitosRoque = DireitosRoque(self.DireitoRoqueAtual.wks, self.DireitoRoqueAtual.bks,
                                        self.DireitoRoqueAtual.wqs, self.DireitoRoqueAtual.bqs)
        # Algoritimo avançado
        movimentos = []
        self.em_Cheque, self.pins, self.cheques = self.ChecarParaPinsECheques()

        if self.whiteToMove:
            LinhaRei = self.LocalizacaoReiBranco[0]
            ColRei = self.LocalizacaoReiBranco[1]
        else:
            LinhaRei = self.LocalizacaoReiPreto[0]
            ColRei = self.LocalizacaoReiPreto[1]
        if self.em_Cheque:
            if len(self.cheques) == 1:  # apenas 1 cheque, bloquear o cheque ou mover o rei
                movimentos = self.getTodosMovimentosPossiveis()
                # Para bloquear o cheque você precisa colocar a peça em um dos quadrados entre a peça inimiga e seu rei
                checar = self.cheques[0]  # checar informação
                ChecarLinha = checar[0]
                ChecarCol = checar[1]
                ChecagemPeca = self.tabuleiro[ChecarLinha][ChecarCol]
                QuadradosValidos = []  # quadrados que as peças podem se mover
                # se cavalo, precisa capturar o cavalo ou mover seu rei, outras peças podem ser bloqueadas
                if ChecagemPeca[1] == "N":
                    QuadradosValidos = [(ChecarLinha, ChecarCol)]
                else:
                    for i in range(1, 8):
                        QuadradoValido = (LinhaRei + checar[2] * i,
                                          ColRei + checar[3] * i)  # checar[2] and checar[3] são as direções de cheque
                        QuadradosValidos.append(QuadradoValido)
                        if QuadradoValido[0] == ChecarLinha and QuadradoValido[
                            1] == ChecarCol:
                            break
                # descartar quaisquer movimentos que n bloqueiam o cheque ou mover o rei
                for i in range(len(movimentos) - 1, -1, -1):
                    if movimentos[i].PecaMovida[1] != "K":  # Mover n move o rei então é necessário bloquear ou capturar
                        if not (movimentos[i].LinhaFinal,
                                movimentos[i].ColFinal) in QuadradosValidos:  # mover não bloqueia ou captura peças
                            movimentos.remove(movimentos[i])
            else:  # cheque duplo, rei deve mover
                self.getMovimentosRei(LinhaRei, ColRei, movimentos)
        else:  # sem cheque, todos moviments validos
            movimentos = self.getTodosMovimentosPossiveis()
            if self.whiteToMove:
                self.getMovimentosRoque(self.LocalizacaoReiBranco[0], self.LocalizacaoReiBranco[1], movimentos)
            else:
                self.getMovimentosRoque(self.LocalizacaoReiPreto[0], self.LocalizacaoReiPreto[1], movimentos)

        if len(movimentos) == 0:
            if self.emCheque():
                self.Chequemate = True
            else:
                # TODO Impasse em movimentos repetitivos
                self.Impasse = True
        else:
            self.Chequemate = False
            self.Impasse = False

        self.DireitoRoqueAtual = TempDireitosRoque
        return movimentos
    
    '''
    Determina se o jogador do turno atual está em cheque
    '''
    def emCheque(self):
        if self.whiteToMove:
            return self.QuadSobreAtaque(self.LocalizacaoReiBranco[0], self.LocalizacaoReiBranco[1])
        else:
            return self.QuadSobreAtaque(self.LocalizacaoReiPreto[0], self.LocalizacaoReiPreto[1])

    '''
    Determina se o inimigo consegue atacar o quadrado
    '''
    def QuadSobreAtaque(self, l, c):
        self.whiteToMove = not self.whiteToMove #trocar para o turno do oponente
        movimentosOponente = self.getTodosMovimentosPossiveis()
        self.whiteToMove = not self.whiteToMove #Trocar turnos de volta
        for mover in movimentosOponente:
            if mover.LinhaFinal == l and mover.ColFinal == c: #Quadrado sobre ataque
                return True
        return False
    
    '''
    todos os movimentos sem considerar check
    '''

    def getTodosMovimentosPossiveis(self):
        movimentos = []
        for l in range(len(self.tabuleiro)): #numero de linhas
            for c in range(len(self.tabuleiro[l])): #numero de colunas na devida linha
                turno = self.tabuleiro[l][c][0]
                if (turno == 'w' and self.whiteToMove) or (turno == 'b' and not self.whiteToMove):
                    peca = self.tabuleiro[l][c][1]
                    self.FuncaoMovimentos[peca](l, c, movimentos) #chama a função apropriada para cada peça
        return movimentos
    
    '''
    Retorna se o jogador está em cheque, uma lista de pins e uma lista de cheques
    '''
    def ChecarParaPinsECheques(self):
        pins = [] #quadrados onde a peça pingada aliada está e a direção pingada
        cheques = [] #quadrados onde o inimigo está dando cheque
        em_Cheque = False
        if self.whiteToMove:
            CorInimigo = 'b'
            CorAliado = 'w'
            LinhaInicial = self.LocalizacaoReiBranco[0]
            ColInicial = self.LocalizacaoReiBranco[1]
        else: 
            CorInimigo = 'w'
            CorAliado = 'b'
            LinhaInicial = self.LocalizacaoReiPreto[0]
            ColInicial = self.LocalizacaoReiPreto[1]
        # verifique a partir do rei se há pins e cheques, acompanhe os pins
        direcoes = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(direcoes)):
            d = direcoes[j]
            PinPossivel = () #resetar pins possiveis
            for i in range(1, 8):
                LinhaFinal = LinhaInicial + d[0] * i
                ColFinal = ColInicial + d[1] * i
                if 0 <= LinhaFinal <= 7 and 0 <= ColFinal <= 7:
                    PecaFinal = self.tabuleiro[LinhaFinal][ColFinal]
                    if PecaFinal[0] == CorAliado and PecaFinal[1] != 'K':
                        if PinPossivel == (): #Primeira peça aliada pode ser pingada
                            PinPossivel = (LinhaFinal, ColFinal, d[0], d[1])
                        else: #segunda peça aliada, então sem pin ou cheque possivel nessa direção
                            break
                    elif PecaFinal[0] == CorInimigo:
                        tipoInimigo = PecaFinal[1]
                        if (0 <= j <= 3 and tipoInimigo == 'R') or (4 <= j <= 7 and tipoInimigo == 'B') or (
                            i == 1 and tipoInimigo == 'P' and ((CorInimigo == 'w' and 6 <= j <= 7) or (CorInimigo == 'b' and 4 <= j <= 5))) or (
                                tipoInimigo == 'Q') or (i == 1 and tipoInimigo == 'K'):
                            if PinPossivel == (): #Nenhuma peça bloqueando, então cheque
                                em_Cheque = True
                                cheques.append((LinhaFinal, ColFinal, d[0], d[1]))
                                break
                            else: #Peça bloqueando então tem pin 
                                pins.append(PinPossivel)
                                break
                        else: #Peça inimiga n dando cheque
                            break
                else:
                    break #fora do tabuleiro
        #checar para cheques de cavalo
        movimentosCavalo = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for mover in movimentosCavalo:
            LinhaFinal = LinhaInicial + mover[0]
            ColFinal = ColInicial + mover[1]
            if 0 <= LinhaFinal <= 7 and 0 <= ColFinal <= 7:
                PecaFinal = self.tabuleiro[LinhaFinal][ColFinal]
                if PecaFinal[0] == CorInimigo and PecaFinal[1] == 'N': #cavalo inimigo atacando o rei
                    em_Cheque = True
                    cheques.append((LinhaFinal, ColFinal, mover[0], mover[1]))
        return em_Cheque, pins, cheques
    
    def verificar_repeticao_posicoes(self):
        """
        Verifica se a posição atual foi repetida 3 vezes.
        """
        posicao_atual = (
            tuple(tuple(peca for peca in linha) for linha in self.tabuleiro),
            self.whiteToMove,
            (self.DireitoRoqueAtual.wks, self.DireitoRoqueAtual.wqs,
            self.DireitoRoqueAtual.bks, self.DireitoRoqueAtual.bqs),
            self.EnpassantPossivel
        )

        return self.historicoPosicoes.get(posicao_atual, 0) >= 3
    
    def atualizar_historico_posicoes(self):
        """
        Atualiza o histórico de posições com a posição atual.
        """
        posicao_atual = (
            tuple(tuple(peca for peca in linha) for linha in self.tabuleiro),
            self.whiteToMove,
            (self.DireitoRoqueAtual.wks, self.DireitoRoqueAtual.wqs,
            self.DireitoRoqueAtual.bks, self.DireitoRoqueAtual.bqs),
            self.EnpassantPossivel
        )

        if posicao_atual in self.historicoPosicoes:
            self.historicoPosicoes[posicao_atual] += 1
        else:
            self.historicoPosicoes[posicao_atual] = 1


    def verificar_empate_por_insuficiencia_material(self, tabuleiro):
        """Verifica se o jogo terminou em empate por insuficiência de material."""
        # Contadores para as peças
        num_rei_branco = 0
        num_rei_preto = 0
        num_bispo_branco = 0
        num_bispo_preto = 0
        num_cavalo_branco = 0
        num_cavalo_preto = 0
        num_outras_brancas = 0
        num_outras_pretas = 0
        # Percorrer o tabuleiro e contar as peças
        for linha in tabuleiro:
            for casa in linha:
                if casa == 'wK':  # Rei branco
                    num_rei_branco += 1
                elif casa == 'bK':  # Rei preto
                    num_rei_preto += 1
                elif casa == 'wB':  # Bispo branco
                    num_bispo_branco += 1
                elif casa == 'bB':  # Bispo preto
                    num_bispo_preto += 1
                elif casa == 'wN':  # Cavalo branco
                    num_cavalo_branco += 1
                elif casa == 'bN':  # Cavalo preto
                    num_cavalo_preto += 1
                # Contar qualquer outra peça que não seja rei, bispo ou cavalo
                elif casa.startswith('w') and casa[1] not in ['K', 'B', 'N']:
                    num_outras_brancas += 1
                elif casa.startswith('b') and casa[1] not in ['K', 'B', 'N']:
                    num_outras_pretas += 1
        # Rei contra Rei
        if num_rei_branco == 1 and num_rei_preto == 1 and \
        num_bispo_branco == 0 and num_bispo_preto == 0 and \
        num_cavalo_branco == 0 and num_cavalo_preto == 0 and \
        num_outras_brancas == 0 and num_outras_pretas == 0:
            return True
        # Rei e Bispo contra Rei
        if (num_rei_branco == 1 and num_rei_preto == 1 and num_bispo_branco == 1 and 
            num_bispo_preto == 0 and num_cavalo_branco == 0 and num_cavalo_preto == 0 and 
            num_outras_brancas == 0 and num_outras_pretas == 0) or \
        (num_rei_branco == 1 and num_rei_preto == 1 and num_bispo_preto == 1 and 
            num_bispo_branco == 0 and num_cavalo_branco == 0 and num_cavalo_preto == 0 and 
            num_outras_brancas == 0 and num_outras_pretas == 0):
            return True
        # Rei e Cavalo contra Rei
        if (num_rei_branco == 1 and num_rei_preto == 1 and num_cavalo_branco == 1 and 
            num_bispo_branco == 0 and num_bispo_preto == 0 and num_cavalo_preto == 0 and 
            num_outras_brancas == 0 and num_outras_pretas == 0) or \
        (num_rei_branco == 1 and num_rei_preto == 1 and num_cavalo_preto == 1 and 
            num_bispo_branco == 0 and num_bispo_preto == 0 and num_cavalo_branco == 0 and 
            num_outras_brancas == 0 and num_outras_pretas == 0):
            return True
        # Rei e Bispo contra Rei e Bispo (mesma cor)
        if num_rei_branco == 1 and num_rei_preto == 1 and \
        num_bispo_branco == 1 and num_bispo_preto == 1 and \
        num_cavalo_branco == 0 and num_cavalo_preto == 0 and \
        num_outras_brancas == 0 and num_outras_pretas == 0:
            # Verificar se os bispos estão na mesma cor de quadrado
            bispo_branco_pos = None
            bispo_preto_pos = None
            for linha_idx, linha in enumerate(tabuleiro):
                for col_idx, casa in enumerate(linha):
                    if casa == 'wB':
                        bispo_branco_pos = (linha_idx, col_idx)
                    elif casa == 'bB':
                        bispo_preto_pos = (linha_idx, col_idx)
            # Verifica se ambos os bispos estão na mesma cor (mesmo padrão de quadrado)
            if bispo_branco_pos and bispo_preto_pos:
                if (bispo_branco_pos[0] + bispo_branco_pos[1]) % 2 == (bispo_preto_pos[0] + bispo_preto_pos[1]) % 2:
                    return True
        # Rei e Bispo de cores opostas (insuficiência de material)
        if num_rei_branco == 1 and num_rei_preto == 1 and \
        num_bispo_branco == 1 and num_bispo_preto == 1 and \
        num_cavalo_branco == 0 and num_cavalo_preto == 0 and \
        num_outras_brancas == 0 and num_outras_pretas == 0:
            # Verificar se os bispos estão em casas opostas
            bispo_branco_pos = None
            bispo_preto_pos = None
            for linha_idx, linha in enumerate(tabuleiro):
                for col_idx, casa in enumerate(linha):
                    if casa == 'wB':
                        bispo_branco_pos = (linha_idx, col_idx)
                    elif casa == 'bB':
                        bispo_preto_pos = (linha_idx, col_idx)
            # Verifica se os bispos estão em casas de cores diferentes
            if bispo_branco_pos and bispo_preto_pos:
                if (bispo_branco_pos[0] + bispo_branco_pos[1]) % 2 != (bispo_preto_pos[0] + bispo_preto_pos[1]) % 2:
                    return True
        # Se não for nenhuma das condições de empate
        return False

    '''
    pegar todos os movimentos para peão localizado na linha, coluna e adicionar esse movimentos para a lista
    '''

    def getMovimentosPeao(self, l, c, movimentos):
        pecaPingada = False
        direcaoPin = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == l and self.pins[i][1] == c:
                pecaPingada = True
                direcaoPin = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            valorMovimentacao = -1
            LinhaInicial = 6
            CorInimigo = "b"
            LinhaRei, ColRei = self.LocalizacaoReiBranco
        else:
            valorMovimentacao = 1
            LinhaInicial = 1
            CorInimigo = "w"
            LinhaRei, ColRei = self.LocalizacaoReiPreto

        if self.tabuleiro[l + valorMovimentacao][c] == "--":  # Avanço de peão de 1 quadrado
            if not pecaPingada or direcaoPin == (valorMovimentacao, 0):
                movimentos.append(Movimento((l, c), (l + valorMovimentacao, c), self.tabuleiro))
                if l == LinhaInicial and self.tabuleiro[l + 2 * valorMovimentacao][c] == "--":  # Avanço de peão de 2 quadrado
                    movimentos.append(Movimento((l, c), (l + 2 * valorMovimentacao, c), self.tabuleiro))
        if c - 1 >= 0:  # captura para esquerda
            if not pecaPingada or direcaoPin == (valorMovimentacao, -1):
                if self.tabuleiro[l + valorMovimentacao][c - 1][0] == CorInimigo:
                    movimentos.append(Movimento((l, c), (l + valorMovimentacao, c - 1), self.tabuleiro))
                if (l + valorMovimentacao, c - 1) == self.EnpassantPossivel:
                    pecaAtacante = pecaBloqueadora = False
                    if LinhaRei == l:
                        if ColRei < c:  # rei está na esquerda do peão
                            # dentro: entre rei e peão
                            # fora: entre peão e borda
                            faixaInterna = range(ColRei + 1, c - 1)
                            faixaExterna = range(c + 1, 8)
                        else:  # rei na direita do peão
                            faixaInterna = range(ColRei - 1, c, -1)
                            faixaExterna = range(c - 2, -1, -1)
                        for i in faixaInterna:
                            if self.tabuleiro[l][i] != "--":  # alguma peça ao lado de blocos de peões en-passant
                                pecaBloqueadora = True
                        for i in faixaExterna:
                            quad = self.tabuleiro[l][i]
                            if quad[0] == CorInimigo and (quad[1] == "R" or quad[1] == "Q"):
                                pecaAtacante = True
                            elif quad != "--":
                                pecaBloqueadora = True
                    if not pecaAtacante or pecaBloqueadora:
                        movimentos.append(Movimento((l, c), (l + valorMovimentacao, c - 1), self.tabuleiro, eMovimentoEnpassant = True))
        if c + 1 <= 7:  # captura para direita
            if not pecaPingada or direcaoPin == (valorMovimentacao, +1):
                if self.tabuleiro[l + valorMovimentacao][c + 1][0] == CorInimigo:
                    movimentos.append(Movimento((l, c), (l + valorMovimentacao, c + 1), self.tabuleiro))
                if (l + valorMovimentacao, c + 1) == self.EnpassantPossivel:
                    pecaAtacante = pecaBloqueadora = False
                    if LinhaRei == l:
                        if ColRei < c:  # rei está na direita do peão
                            # dentro: entre rei e peão
                            # fora: entre peão e borda
                            faixaInterna = range(ColRei + 1, c)
                            faixaExterna = range(c + 2, 8)
                        else:  # rei na direita do peão
                            faixaInterna = range(ColRei - 1, c + 1, -1)
                            faixaExterna = range(c - 1, -1, -1)
                        for i in faixaInterna:
                            if self.tabuleiro[l][i] != "--":  # alguma peça ao lado de blocos de peões en-passant
                                pecaBloqueadora = True
                        for i in faixaExterna:
                            quad = self.tabuleiro[l][i]
                            if quad[0] == CorInimigo and (quad[1] == "R" or quad[1] == "Q"):
                                pecaAtacante = True
                            elif quad != "--":
                                pecaBloqueadora = True
                    if not pecaAtacante or pecaBloqueadora:
                        movimentos.append(Movimento((l, c), (l + valorMovimentacao, c + 1), self.tabuleiro, eMovimentoEnpassant = True))

    '''
    pegar todos os movimentos para torre localizado na linha, coluna e adicionar esse movimentos a lista
    '''

    def getMovimentosTorre(self, l, c, movimentos):
        PecaPingada = False
        DirecaoPin = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == l and self.pins[i][1] == c:
                PecaPingada = True
                DirecaoPin = (self.pins[i][2], self.pins[i][3])
                if self.tabuleiro[l][c][
                    1] != "Q":  # N pode remover a rainha do pin nos movimentos de torre, somente remove ele nos de bispo
                    self.pins.remove(self.pins[i])
                break
        direcoes = ((-1, 0), (0, -1), (1, 0), (0, 1))  #cima, esquerda, baixo, direita
        CorInimigo = "b" if self.whiteToMove else "w"
        for d in direcoes:
            for i in range(1, 8):
                LinhaFinal = l + d[0] * i
                ColFinal = c + d[1] * i
                if 0 <= LinhaFinal <= 7 and 0 <= ColFinal <= 7:  # No tabuleiro
                    if not PecaPingada or DirecaoPin == d or DirecaoPin == (-d[0], -d[1]):
                        PecaFinal = self.tabuleiro[LinhaFinal][ColFinal]
                        if PecaFinal == "--":  #quadrado vazio valido
                            movimentos.append(Movimento((l, c), (LinhaFinal, ColFinal), self.tabuleiro))
                        elif PecaFinal[0] == CorInimigo:  # capturar peça inimiga
                            movimentos.append(Movimento((l, c), (LinhaFinal, ColFinal), self.tabuleiro))
                            break
                        else:  # peça amiga
                            break
                else:  # fora do tabuleiro
                    break

    '''
    pegar todos os movimentos para cavalo localizado na linha, coluna e adicionar esse movimentos a lista
    '''

    def getMovimentosCavalo(self, l, c, movimentos):
        PecaPingada = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == l and self.pins[i][1] == c:
                PecaPingada = True
                self.pins.remove(self.pins[i])
                break
        movimentosCavalo = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        CorAliado = "w" if self.whiteToMove else "b"
        for mover in movimentosCavalo:
            LinhaFinal = l + mover[0]
            ColFinal = c + mover[1]
            if 0 <= LinhaFinal <= 7 and 0 <= ColFinal <= 7:
                if not PecaPingada:
                    PecaFinal = self.tabuleiro[LinhaFinal][ColFinal]
                    if PecaFinal[0] != CorAliado:  #não é uma peça aliada(vazio ou peça inimiga)
                        movimentos.append(Movimento((l, c), (LinhaFinal, ColFinal), self.tabuleiro))

    '''
    pegar todos os movimentos para bispo localizado na linha, coluna e adicionar esse movimentos a lista
    '''

    def getMovimentosBispo(self, l, c, movimentos):
        PecaPingada = False
        DirecaoPin = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == l and self.pins[i][1] == c:
                PecaPingada = True
                DirecaoPin = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        direcoes = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonais
        CorInimigo = "b" if self.whiteToMove else "w"
        for d in direcoes:
            for i in range(1, 8):
                LinhaFinal = l + d[0] * i
                ColFinal = c + d[1] * i
                if 0 <= LinhaFinal <= 7 and 0 <= ColFinal <= 7:  # checar se o movimento está dentro do tabuleiro
                    if not PecaPingada or DirecaoPin == d or DirecaoPin == (-d[0], -d[1]):
                        PecaFinal = self.tabuleiro[LinhaFinal][ColFinal]
                        if PecaFinal == "--":  # quadrado vazio é válido
                            movimentos.append(Movimento((l, c), (LinhaFinal, ColFinal), self.tabuleiro))
                        elif PecaFinal[0] == CorInimigo:  # capturar peça inimiga
                            movimentos.append(Movimento((l, c), (LinhaFinal, ColFinal), self.tabuleiro))
                            break
                        else:  # peça aliada
                            break
                else:  # fora do tabuleiro
                    break

    '''
    pegar todos os movimentos para Rainha localizado na linha, coluna e adicionar esse movimentos a lista
    '''

    def getMovimentosRainha(self, l, c, movimentos):
        self.getMovimentosTorre(l, c, movimentos)
        self.getMovimentosBispo(l, c, movimentos)

    '''
    pegar todos os movimentos para Rei localizado na linha, coluna e adicionar esse movimentos a lista
    '''

    def getMovimentosRei(self, l, c, movimentos):
        MovimentosLinha = (-1, -1, -1, 0, 0, 1, 1, 1)
        MovimentosCol = (-1, 0, 1, -1, 1, -1, 0, 1)
        CorAliado = "w" if self.whiteToMove else "b"
        for i in range(8):
            LinhaFinal = l + MovimentosLinha[i]
            ColFinal = c + MovimentosCol[i]
            if 0 <= LinhaFinal <= 7 and 0 <= ColFinal <= 7:
                PecaFinal = self.tabuleiro[LinhaFinal][ColFinal]
                if PecaFinal[0] != CorAliado:  # não é peça aliada (vazio ou peça inimiga)
                    #colocar rei no quadrado final e checar se tem cheque
                    if CorAliado == "w":
                        self.LocalizacaoReiBranco = (LinhaFinal, ColFinal)
                    else:
                        self.LocalizacaoReiPreto = (LinhaFinal, ColFinal)
                    em_Cheque, pins, cheques = self.ChecarParaPinsECheques()
                    if not em_Cheque:
                        movimentos.append(Movimento((l, c), (LinhaFinal, ColFinal), self.tabuleiro))
                    #Colocar rei na posição original
                    if CorAliado == "w":
                        self.LocalizacaoReiBranco = (l, c)
                    else:
                        self.LocalizacaoReiPreto = (l, c)

    '''
    Gerar todos os movimentos validos de roque para rei no (l, c) e adiciona-los na lista de movimentos
    '''
    def getMovimentosRoque(self, l, c, movimentos):
        if self.QuadSobreAtaque(l, c):
            return  # não poder fazer roque enquanto estiver sobre cheque
        if (self.whiteToMove and self.DireitoRoqueAtual.wks) or (
                not self.whiteToMove and self.DireitoRoqueAtual.bks):
            self.getMovimentosLadoRei(l, c, movimentos)
        if (self.whiteToMove and self.DireitoRoqueAtual.wqs) or (
                not self.whiteToMove and self.DireitoRoqueAtual.bqs):
            self.getMovimentosLadoRainha(l, c, movimentos)

    def getMovimentosLadoRei(self, l, c, movimentos):
        if self.tabuleiro[l][c + 1] == '--' and self.tabuleiro[l][c + 2] == '--':
            if not self.QuadSobreAtaque(l, c + 1) and not self.QuadSobreAtaque(l, c + 2):
                movimentos.append(Movimento((l, c), (l, c + 2), self.tabuleiro, eMovimentoRoque = True))

    def getMovimentosLadoRainha(self, l, c, movimentos):
        if self.tabuleiro[l][c - 1] == '--' and self.tabuleiro[l][c - 2] == '--' and self.tabuleiro[l][c - 3] == '--':
            if not self.QuadSobreAtaque(l, c - 1) and not self.QuadSobreAtaque(l, c - 2):
                movimentos.append(Movimento((l, c), (l, c - 2), self.tabuleiro, eMovimentoRoque = True))


class DireitosRoque():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
    

class Movimento():
    #mapeia teclas para valores
    # tecla = valor
    RanksParaLinhas = {"1" : 7,"2" : 6,"3" : 5,"4" : 4,
                    "5" : 3,"6" : 2,"7" : 1,"8" : 0}
    LinhasParaRanks = {v: t for t, v in RanksParaLinhas.items()}
    ArquivosParaColunas = {"a" : 0,"b" : 1,"c" : 2,"d" : 3,
                        "e" : 4,"f" : 5,"g" : 6,"h" : 7}
    ColunasParaArquivos = {v: t for t, v in ArquivosParaColunas.items()}

    def __init__(self, QuadInicial, QuadFinal, tabuleiro, eMovimentoEnpassant = False, eMovimentoRoque = False):
        self.LinhaInicial = QuadInicial[0]
        self.ColInicial = QuadInicial[1]
        self.LinhaFinal = QuadFinal[0]
        self.ColFinal = QuadFinal[1]
        self.PecaMovida = tabuleiro[self.LinhaInicial][self.ColInicial]
        self.PecaCapturada = tabuleiro[self.LinhaFinal][self.ColFinal]
        #Promoção de peão
        self.ePromocaoPeao = (self.PecaMovida == 'wP' and self.LinhaFinal == 0) or (self.PecaMovida == 'bP' and self.LinhaFinal == 7)
        #En passant
        self.eMovimentoEnpassant = eMovimentoEnpassant
        if self.eMovimentoEnpassant:
            self.PecaCapturada = 'wP' if self.PecaMovida == 'bP' else 'bP'
        #Movimento Roque
        self.eMovimentoRoque = eMovimentoRoque

        self.eCapturada = self.PecaCapturada != "--"
        self.idMovimento = self.LinhaInicial * 1000 + self.ColInicial * 100 + self.LinhaFinal * 10 + self.ColFinal

    '''
    Sobreescrever o metodo do igual
    '''
    def __eq__(self, outro):
        if isinstance(outro, Movimento):
            return self.idMovimento == outro.idMovimento
        return False

    def getNotacaoXadrez(self):
        if self.ePromocaoPeao:
            return self.getRankFile(self.LinhaFinal, self.ColFinal) + "Q"
        if self.eMovimentoRoque:
            if self.ColFinal == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.eMovimentoEnpassant:
            return self.getRankFile(self.LinhaInicial, self.ColInicial)[0] + "x" + self.getRankFile(self.LinhaFinal, self.LinhaFinal) + " e.p."
        if self.PecaCapturada != "--":
            if self.PecaMovida[1] == "P":
                return self.getRankFile(self.LinhaInicial, self.ColInicial)[0] + "x" + self.getRankFile(self.LinhaFinal, self.ColFinal)
            else:
                return self.PecaMovida[1] + "x" + self.getRankFile(self.LinhaFinal, self.ColFinal)
        else:
            if self.PecaMovida[1] == "P":
                return self.getRankFile(self.LinhaFinal, self.ColFinal)
            else:
                return self.PecaMovida[1] + self.getRankFile(self.LinhaFinal, self.ColFinal)

    def getRankFile(self, l, c):
        return self.ColunasParaArquivos[c] + self.LinhasParaRanks[l]

    def __str__(self):
        if self.eMovimentoRoque:
            return "0-0" if self.ColFinal == 6 else "0-0-0"

        QuadFinal = self.getRankFile(self.LinhaFinal, self.ColFinal)

        if self.PecaMovida[1] == "P":
            if self.eCapturada:
                return self.ColunasParaArquivos[self.ColInicial] + "x" + QuadFinal
            else:
                return QuadFinal + "Q" if self.ePromocaoPeao else QuadFinal

        MoverCorda = self.PecaMovida[1]
        if self.eCapturada:
            MoverCorda += "x"
        return MoverCorda + QuadFinal