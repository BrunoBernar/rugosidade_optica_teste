"""
Estimador de Rugosidade por Imagem de Microscopio

Author: Bruno Bernardinetti - Github = https://github.com/BrunoBernar/rugosidade_optica_teste
==================================================
Fluxo de uso:
  1. Carregue pelo menos 10 imagens da peca de REFERENCIA e informe seu Ra real (um)
  2. Carregue pelo menos 10 imagens da peca a MEDIR
  3. Clique em Analisar
  4. Clique em Exportar PDF para salvar o relatorio completo

Dependencias:
    pip install pillow numpy matplotlib scipy reportlab
"""

# ── Importacoes ───────────────────────────────────────────────────────────────

import tkinter as tk                                   # biblioteca padrao para criar interfaces graficas (GUI)
from tkinter import filedialog, messagebox             # dialogo de abrir arquivo e caixa de mensagem
import numpy as np                                     # biblioteca para calculo numerico e arrays
from PIL import Image, ImageTk                         # Pillow: abrir/converter imagens; ImageTk: exibir imagens no tkinter
import matplotlib                                      # biblioteca de graficos
matplotlib.use("Agg")                                  # define backend nao-interativo (necessario para salvar figura em memoria)
import matplotlib.pyplot as plt                        # interface principal de criacao de graficos
import matplotlib.backends.backend_agg as agg          # backend Agg para renderizacao em memoria (usado no PDF)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # widget que embute grafico matplotlib dentro do tkinter
from scipy.ndimage import sobel                        # filtro de Sobel para calcular gradiente da imagem (deteccao de bordas)
import os                                              # funcoes do sistema operacional (ex: pegar nome do arquivo)
import io                                              # manipulacao de streams em memoria (para salvar figura como bytes)
import datetime                                        # data e hora atual (usada no cabecalho do PDF)
import tempfile                                        # criacao de arquivos temporarios (reservado para uso futuro)

# ── Importacoes do ReportLab (geracao de PDF) ─────────────────────────────────

from reportlab.lib.pagesizes import A4                 # tamanho de pagina A4 em pontos (595 x 842 pts)
from reportlab.lib.units import mm                     # converte milimetros para pontos do ReportLab
from reportlab.lib import colors                       # paleta de cores do ReportLab
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # estilos de paragrafo prontos e personalizados
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image as RLImage, HRFlowable,
                                 KeepTogether)         # elementos de layout do PDF (documento, paragrafo, tabela, imagem, etc.)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT  # constantes de alinhamento de texto

# ── Constante global ──────────────────────────────────────────────────────────

MIN_FOTOS = 10                                         # numero minimo de fotos exigido por caso (referencia e medicao)

# ── Tabela de correlacao AFNOR (notacao francesa) / ISO 1302 ─────────────────

AFNOR_ISO = [                                          # lista de tuplas (classe ISO N, Ra maximo em um)
    ("N1",  "0.025"),                                  # N1: superficies de espelho / superacabamento
    ("N2",  "0.05"),                                   # N2: retificacao fina
    ("N3",  "0.1"),                                    # N3: retificacao
    ("N4",  "0.2"),                                    # N4: retificacao grossa
    ("N5",  "0.4"),                                    # N5: torneamento / fresamento fino
    ("N6",  "0.8"),                                    # N6: torneamento convencional
    ("N7",  "1.6"),                                    # N7: fresamento grosso (ex: R10 AFNOR = N7 ISO = Ra 6.3 um)
    ("N8",  "3.2"),                                    # N8: desbaste
    ("N9",  "6.3"),                                    # N9: fundicao / forjamento
    ("N10", "12.5"),                                   # N10: fundicao bruta
    ("N11", "25.0"),                                   # N11: corte a chama
    ("N12", "50.0"),                                   # N12: superficie bruta / nao usinada
]

# ── Funcoes de analise de imagem ──────────────────────────────────────────────

def extrair_metricas(caminho):
    """Abre uma imagem, converte para escala de cinza e calcula todas as metricas de textura."""
    img = Image.open(caminho).convert("L")             # abre a imagem e converte para escala de cinza (L = luminancia)
    img.thumbnail((512, 512))                          # redimensiona para no maximo 512x512 pixels (melhora performance)
    arr = np.array(img, dtype=np.float64)              # converte a imagem para array NumPy de pontos flutuantes

    media = arr.mean()                                 # calcula a media global de intensidade dos pixels (0 a 255)

    ra = float(np.mean(np.abs(arr - media)))           # Ra proxy: desvio medio absoluto em relacao a media (analogo ao Ra real de rugosidade)
    rq = float(np.sqrt(np.mean((arr - media) ** 2)))   # Rq proxy: raiz quadrada da media dos desvios ao quadrado (rugosidade RMS)

    flat = np.sort(arr.flatten())                      # achata o array 2D em 1D e ordena do menor para o maior pixel
    rz   = float(flat[-5:].mean() - flat[:5].mean())   # Rz proxy: media dos 5 pixels mais claros menos media dos 5 mais escuros (amplitude de picos e vales)

    gx = sobel(arr, axis=1)                            # aplica filtro de Sobel na direcao horizontal (gradiente em X)
    gy = sobel(arr, axis=0)                            # aplica filtro de Sobel na direcao vertical (gradiente em Y)
    grad_energy = float(np.sqrt(gx**2 + gy**2).mean())# calcula a magnitude do gradiente (norma euclidiana) e tira a media -> indica densidade de bordas/irregularidades

    hist, _ = np.histogram(arr.ravel(), bins=256, range=(0, 255))  # calcula histograma de intensidade com 256 bins (0 a 255)
    p = hist / hist.sum()                              # normaliza o histograma para obter distribuicao de probabilidade
    p = p[p > 0]                                       # remove bins com probabilidade zero (evita log(0))
    entropia = float(-np.sum(p * np.log2(p)))          # calcula entropia de Shannon em bits: mede a complexidade/heterogeneidade da textura

    return dict(                                       # retorna dicionario com todas as metricas calculadas
        ra=ra, rq=rq, rz=rz,                           # metricas de rugosidade proxies (unidades de intensidade)
        grad_energy=grad_energy,                       # energia do gradiente (Sobel)
        entropia=entropia,                             # entropia da distribuicao de pixels
        media=media,                                   # intensidade media da imagem
        arr=arr,                                       # array da imagem (necessario para graficos)
        nome=os.path.basename(caminho)                 # nome do arquivo sem o caminho completo
    )


def agregar_metricas(lista):
    """Recebe lista de resultados individuais e calcula media e desvio padrao de cada metrica."""
    keys = ["ra", "rq", "rz", "grad_energy", "entropia"]  # lista das metricas a agregar
    agg  = {}                                          # dicionario que vai acumular os resultados agregados

    for k in keys:                                     # itera sobre cada metrica
        vals = [r[k] for r in lista]                   # extrai os valores da metrica k de todas as imagens
        agg[f"{k}_mean"] = float(np.mean(vals))        # calcula e armazena a media dos valores
        agg[f"{k}_std"]  = float(np.std(vals))         # calcula e armazena o desvio padrao dos valores
        agg[f"{k}_vals"] = vals                        # armazena lista bruta de valores (usada nos graficos)

    hists = []                                         # lista para acumular histogramas normalizados de cada imagem
    for r in lista:                                    # itera sobre cada resultado individual
        c, edges = np.histogram(r["arr"].ravel(), bins=64, range=(0, 255))  # calcula histograma com 64 bins
        hists.append(c / c.max())                      # normaliza pelo valor maximo e adiciona a lista

    agg["hist_mean"]  = np.mean(hists, axis=0)         # calcula histograma medio (media pixel a pixel entre todas as imagens)
    agg["hist_edges"] = edges                          # armazena os limites dos bins para usar nos graficos
    agg["n"] = len(lista)                              # registra quantas imagens foram processadas

    return agg                                         # retorna o dicionario agregado completo


def classificar(ra_um):
    """Classifica a superfície segundo a escala ISO 1302 a partir do Ra em micrometros."""
    if ra_um <  0.1: return "N1  - Espelho / super-acabamento",    "#00e5ff"  # Ra < 0.1 um
    if ra_um <  0.2: return "N2  - Retificacao fina",              "#00bcd4"  # Ra < 0.2 um
    if ra_um <  0.4: return "N3  - Retificacao",                   "#009688"  # Ra < 0.4 um
    if ra_um <  0.8: return "N4  - Retificacao grossa",            "#4caf50"  # Ra < 0.8 um
    if ra_um <  1.6: return "N5  - Torneamento / fresamento fino", "#8bc34a"  # Ra < 1.6 um
    if ra_um <  3.2: return "N6  - Torneamento convencional",      "#ffc107"  # Ra < 3.2 um
    if ra_um <  6.3: return "N7  - Fresamento grosso",             "#ff9800"  # Ra < 6.3 um (AFNOR R9 / R10)
    if ra_um < 12.5: return "N8  - Desbaste",                      "#ff5722"  # Ra < 12.5 um
    if ra_um < 25.0: return "N9  - Fundicao / forjamento",         "#f44336"  # Ra < 25.0 um
    return                   "N10+ - Superficie bruta",             "#b71c1c"  # Ra >= 25 um


# ── Paleta de cores e fontes da interface ─────────────────────────────────────

BG        = "#0d1117"   # cor de fundo principal (preto azulado escuro)
BG2       = "#111820"   # cor de fundo secundaria (cabecalhos de cards)
BG3       = "#050709"   # cor de fundo terciaria (canvas de imagem, mais escuro)
ACCENT    = "#00e5ff"   # cor de destaque ciano (peca medida)
GOLD      = "#ffc107"   # cor dourada (peca de referencia)
FG        = "#c8d8e8"   # cor de texto principal (branco azulado)
FG_DIM    = "#3a6070"   # cor de texto secundaria (cinza esverdeado)
FG_WARN   = "#7a6040"   # cor de texto de aviso (amarelo escuro)
BG_WARN   = "#1a1000"   # cor de fundo de aviso (marrom muito escuro)
BORDER    = "#1a2a34"   # cor de bordas dos cards
GREEN     = "#4caf50"   # cor verde (indicador de status OK)
FONT_MONO = ("Courier", 9)   # fonte monoespaco padrao para valores
FONT_SMALL= ("Courier", 7)   # fonte monoespaco pequena para rotulos de cabecalho


def frame_card(parent, title, **kw):
    """Cria um widget tipo 'card' com borda, titulo e area interna. Retorna (outer, inner)."""
    outer = tk.Frame(parent, bg=BG, highlightbackground=BORDER,
                     highlightthickness=1, **kw)           # frame externo com borda fina
    tk.Label(outer, text=title.upper(), bg=BG2, fg=FG_DIM,
             font=FONT_SMALL, padx=8, pady=4, anchor="w").pack(fill="x")  # label de titulo do card
    inner = tk.Frame(outer, bg=BG, padx=8, pady=6)        # frame interno onde o conteudo e colocado
    inner.pack(fill="both", expand=True)                   # expande para preencher o card
    return outer, inner                                    # retorna referencia aos dois frames


# ── Classe do slot de multiplas imagens ───────────────────────────────────────

class MultiImageSlot(tk.Frame):
    """
    Widget que gerencia um conjunto de imagens para um caso (referencia ou medicao).
    Permite adicionar multiplas fotos, navegar entre elas e limpar a selecao.
    """

    def __init__(self, parent, label, cor, **kw):
        super().__init__(parent, bg=BG, **kw)              # inicializa o Frame pai com cor de fundo
        self._cor      = cor                               # cor de destaque para este slot (gold ou cyan)
        self._caminhos = []                                # lista de caminhos das imagens selecionadas
        self._tk_imgs  = []                                # lista de referencias PhotoImage (evita coleta de lixo pelo GC)
        self._idx      = 0                                 # indice da imagem atualmente exibida no preview

        # Barra superior com titulo e botoes
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 4))                    # empacota horizontalmente com espaco abaixo
        tk.Label(top, text=label, bg=BG, fg=cor,
                 font=("Courier", 10, "bold")).pack(side="left")  # label com nome do slot (REFERENCIA / PECA A MEDIR)
        tk.Button(top, text="Limpar", command=self._limpar,
                  bg=BG2, fg=FG_DIM, font=FONT_MONO, relief="flat",
                  padx=6, pady=3, cursor="hand2").pack(side="right", padx=(0, 4))  # botao para limpar todas as imagens
        tk.Button(top, text="+ Adicionar fotos", command=self._adicionar,
                  bg=BG2, fg=cor, font=FONT_MONO, relief="flat",
                  padx=8, pady=3, cursor="hand2").pack(side="right")  # botao para abrir dialogo de selecao de imagens

        # Canvas de preview da imagem atual
        self._canvas = tk.Canvas(self, bg=BG3, highlightthickness=1,
                                 highlightbackground=BORDER, width=270, height=165)  # area de exibicao da imagem
        self._canvas.pack(fill="x")                        # expande horizontalmente
        self._canvas.create_text(135, 82, text="Nenhuma imagem",
                                 fill="#2a3a44", font=FONT_MONO, tags="ph")  # texto placeholder quando nao ha imagem

        # Barra de navegacao entre imagens
        nav = tk.Frame(self, bg=BG)
        nav.pack(fill="x", pady=(3, 0))                    # empacota com espaco acima
        tk.Button(nav, text="<", command=self._prev, bg=BG2, fg=FG_DIM,
                  font=FONT_MONO, relief="flat", width=2, cursor="hand2").pack(side="left")   # botao voltar imagem
        self._lbl_nav = tk.Label(nav, text="0 / 0", bg=BG, fg=FG_DIM,
                                 font=("Courier", 7))
        self._lbl_nav.pack(side="left", expand=True)       # label central que mostra "3 / 10 | nome_arquivo.jpg"
        tk.Button(nav, text=">", command=self._next, bg=BG2, fg=FG_DIM,
                  font=FONT_MONO, relief="flat", width=2, cursor="hand2").pack(side="right")  # botao avancar imagem

        # Label de status (quantas fotos / faltam quantas)
        self._lbl_status = tk.Label(self, text="", bg=BG, fg=FG_DIM,
                                    font=("Courier", 8), anchor="w")
        self._lbl_status.pack(fill="x", pady=(2, 0))       # empacota abaixo da navegacao
        self._atualizar_status()                           # atualiza o status inicial (0 fotos)

    def _adicionar(self):
        """Abre dialogo para selecionar uma ou mais imagens e adiciona a lista."""
        paths = filedialog.askopenfilenames(               # abre seletor de arquivo multiplo
            title="Selecionar imagens (Ctrl+clique para multiplas)",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
                       ("Todos", "*.*")])                  # filtra por formatos de imagem suportados
        if not paths:                                      # se usuario cancelou, nao faz nada
            return
        for p in paths:                                    # itera sobre os arquivos selecionados
            if p not in self._caminhos:                    # evita duplicatas na lista
                self._caminhos.append(p)                   # adiciona caminho a lista
        self._idx = len(self._caminhos) - 1               # move o preview para a ultima imagem adicionada
        self._atualizar_preview()                          # atualiza o canvas com a nova imagem
        self._atualizar_status()                           # atualiza o contador de fotos

    def _limpar(self):
        """Remove todas as imagens da lista e reseta o preview."""
        self._caminhos = []                                # esvazia a lista de caminhos
        self._tk_imgs  = []                                # libera referencias de imagem
        self._idx = 0                                      # reseta o indice para zero
        self._canvas.delete("all")                         # limpa o canvas
        self._canvas.create_text(135, 82, text="Nenhuma imagem",
                                 fill="#2a3a44", font=FONT_MONO)  # recoloca o placeholder
        self._atualizar_status()                           # atualiza o status para "0 fotos"

    def _prev(self):
        """Navega para a imagem anterior na lista (com wrap-around)."""
        if not self._caminhos: return                      # se nao ha imagens, ignora
        self._idx = (self._idx - 1) % len(self._caminhos) # decrementa o indice com wrap-around circular
        self._atualizar_preview()                          # exibe a nova imagem

    def _next(self):
        """Navega para a proxima imagem na lista (com wrap-around)."""
        if not self._caminhos: return                      # se nao ha imagens, ignora
        self._idx = (self._idx + 1) % len(self._caminhos) # incrementa o indice com wrap-around circular
        self._atualizar_preview()                          # exibe a nova imagem

    def _atualizar_preview(self):
        """Carrega e exibe a imagem atual (self._idx) no canvas de preview."""
        if not self._caminhos: return                      # guarda curto: nao faz nada se lista vazia
        path = self._caminhos[self._idx]                   # pega o caminho da imagem atual
        img  = Image.open(path)                            # abre a imagem com Pillow
        img.thumbnail((270, 165))                          # redimensiona mantendo proporcao para caber no canvas
        tk_img = ImageTk.PhotoImage(img)                   # converte para formato compativel com tkinter
        self._tk_imgs.append(tk_img)                       # guarda referencia (sem isso o GC apaga a imagem)
        if len(self._tk_imgs) > 20:                        # limita o cache a 20 imagens para nao consumir muita memoria
            self._tk_imgs = self._tk_imgs[-20:]            # mantém apenas as 20 mais recentes
        self._canvas.delete("all")                         # limpa o canvas antes de desenhar
        cw = self._canvas.winfo_width()  or 270            # largura atual do canvas (ou 270 se ainda nao renderizou)
        ch = self._canvas.winfo_height() or 165            # altura atual do canvas (ou 165 se ainda nao renderizou)
        self._canvas.create_image(cw//2, ch//2, image=tk_img, anchor="center")  # desenha a imagem centralizada
        self._lbl_nav.config(                              # atualiza o label de navegacao com indice e nome do arquivo
            text=f"{self._idx + 1} / {len(self._caminhos)}  |  "
                 f"{os.path.basename(path)}")

    def _atualizar_status(self):
        """Atualiza o label de status com contagem de fotos e feedback visual."""
        n     = len(self._caminhos)                        # quantidade atual de fotos
        falta = max(0, MIN_FOTOS - n)                      # quantas fotos ainda faltam para atingir o minimo
        if n == 0:
            txt, cor = f"0 fotos  —  minimo {MIN_FOTOS}", FG_DIM   # nenhuma foto carregada
        elif falta > 0:
            txt, cor = f"{n} foto(s)  —  faltam {falta}", GOLD     # abaixo do minimo: amarelo de aviso
        else:
            txt, cor = f"{n} fotos  —  OK", GREEN                  # atingiu o minimo: verde de confirmacao
        self._lbl_status.config(text=txt, fg=cor)          # aplica texto e cor no label
        if n > 0:                                          # se ha imagens, atualiza o label de navegacao
            self._lbl_nav.config(
                text=f"{self._idx + 1} / {n}  |  "
                     f"{os.path.basename(self._caminhos[self._idx])}")
        else:
            self._lbl_nav.config(text="0 / 0")            # reseta label se nao ha imagens

    @property
    def caminhos(self):
        """Propriedade que expoe a lista de caminhos (readonly)."""
        return self._caminhos

    def pronto(self):
        """Retorna True se o numero minimo de fotos foi atingido."""
        return len(self._caminhos) >= MIN_FOTOS


# ── Classe principal da aplicacao ─────────────────────────────────────────────

class App(tk.Tk):
    """
    Janela principal do aplicativo. Contem os dois slots de imagem,
    campo de Ra da referencia, tabela de resultados, graficos e botao de PDF.
    """

    def __init__(self):
        super().__init__()                                 # inicializa a janela raiz do tkinter
        self.title("Estimador de Rugosidade - Amostragem multipla")  # titulo da janela
        self.configure(bg=BG)                              # aplica cor de fundo escura
        self.resizable(True, True)                         # permite redimensionar janela em ambas as direcoes
        self.minsize(1050, 720)                            # tamanho minimo da janela em pixels

        # Variaveis para armazenar resultados da ultima analise (usadas no PDF)
        self._last_agg_ref  = None                         # metricas agregadas da referencia
        self._last_agg_med  = None                         # metricas agregadas da peca medida
        self._last_raw_ref  = None                         # lista de resultados individuais da referencia
        self._last_raw_med  = None                         # lista de resultados individuais da peca medida
        self._last_fator    = None                         # fator de calibracao calculado
        self._last_ra_real  = None                         # Ra real informado pelo usuario

        self._build_ui()                                   # constroi todos os widgets da interface

    # ── Construcao da interface ────────────────────────────────────────────────

    def _build_ui(self):
        """Monta todos os widgets da janela principal."""

        # Cabecalho superior
        hdr = tk.Frame(self, bg=BG, padx=20, pady=12)
        hdr.pack(fill="x")                                 # ocupa toda a largura da janela
        tk.Label(hdr, text="SURFACE ROUGHNESS ESTIMATOR",
                 font=("Courier", 13, "bold"), fg=ACCENT, bg=BG).pack(anchor="w")  # titulo principal em ciano
        tk.Label(hdr,
                 text=f"Amostragem multipla (min. {MIN_FOTOS} fotos por caso)  |  "
                      "Calibracao por referencia  |  Microscopio USB",
                 font=("Helvetica", 9), fg=FG_DIM, bg=BG).pack(anchor="w")  # subtitulo descritivo
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x") # linha separadora ciano

        # Frame do corpo principal dividido em duas colunas
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=14)  # ocupa o restante da janela com margem

        # ── Coluna esquerda: controles de entrada ─────────────────────────────

        left = tk.Frame(body, bg=BG, width=330)
        left.pack(side="left", fill="y", padx=(0, 16))    # coluna fixa de 330px a esquerda
        left.pack_propagate(False)                         # impede que o frame encolha com o conteudo

        # Slot de imagens da referencia (dourado)
        self._slot_ref = MultiImageSlot(left, "REFERENCIA", GOLD)
        self._slot_ref.pack(fill="x", pady=(0, 6))        # ocupa largura total com espaco abaixo

        # Card com campo de entrada do Ra real da referencia
        ra_f, ra_i = frame_card(left, "Ra real da referencia (um)")
        ra_f.pack(fill="x", pady=(0, 8))                  # card com borda e titulo
        row = tk.Frame(ra_i, bg=BG)
        row.pack(fill="x")                                 # linha interna para alinhar entry e label
        self._entry_ra = tk.Entry(row, bg=BG2, fg=GOLD,   # campo de texto para digitar o Ra real
                                  font=("Courier", 13, "bold"),
                                  insertbackground=GOLD, relief="flat",
                                  highlightthickness=1, highlightbackground=BORDER,
                                  width=10)
        self._entry_ra.pack(side="left", padx=(0, 8), ipady=4)  # alinha a esquerda com padding interno
        tk.Label(row, text="ex: 0.8 / 1.6 / 3.2 / 6.3",
                 bg=BG, fg=FG_DIM, font=("Helvetica", 8)).pack(side="left")  # dica de valores tipicos

        # Slot de imagens da peca a medir (ciano)
        self._slot_med = MultiImageSlot(left, "PECA A MEDIR", ACCENT)
        self._slot_med.pack(fill="x", pady=(0, 8))        # ocupa largura total com espaco abaixo

        # Botao principal de analise
        self._btn_analisar = tk.Button(
            left, text="ANALISAR", command=self._analisar,
            bg=BG2, fg=ACCENT, font=("Courier", 11, "bold"),
            relief="flat", pady=8, cursor="hand2",
            activebackground=BG, activeforeground=ACCENT)
        self._btn_analisar.pack(fill="x", pady=(0, 4))    # ocupa largura total

        # Botao de exportar PDF (fica desabilitado ate a primeira analise)
        self._btn_pdf = tk.Button(
            left, text="Exportar PDF", command=self._exportar_pdf,
            bg=BG2, fg="#e040fb", font=("Courier", 10, "bold"),
            relief="flat", pady=8, cursor="hand2",
            activebackground=BG, activeforeground="#e040fb",
            state="disabled")                              # comeca desabilitado essa MERDA BUGA AS VEZES CUIDADO!
        self._btn_pdf.pack(fill="x")                      # ocupa largura total

        # Label de aviso sobre condicoes de captura
        tk.Label(left,
            text="Ctrl+clique no seletor para multiplas fotos.\n"
                 "Mesma iluminacao e magnificacao nas duas pecas.",
            bg=BG_WARN, fg=FG_WARN, font=("Helvetica", 8),
            justify="left", padx=10, pady=8).pack(fill="x", pady=(8, 0))  # aviso em fundo amarelo escuro

        # ── Coluna direita: resultados e graficos ──────────────────────────────

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)  # ocupa o restante da largura e toda a altura

        # Card do fator de calibracao
        cf, ci = frame_card(right, "Fator de calibracao")
        cf.pack(fill="x", pady=(0, 4))                    # card pequeno no topo
        frow = tk.Frame(ci, bg=BG)
        frow.pack(fill="x")
        self._lbl_fator = tk.Label(frow, text="—", bg=BG, fg=GOLD,
                                   font=("Courier", 10, "bold"))  # exibe o valor calculado do fator (um/u.i.)
        self._lbl_fator.pack(side="left")
        tk.Label(frow, text="  um / u.i.   (Ra_real / Ra_proxy medio da referencia)",
                 bg=BG, fg=FG_DIM, font=("Helvetica", 7)).pack(side="left")  # descricao do fator

        # Tabela comparativa: Referencia vs Peca Medida
        tab = tk.Frame(right, bg=BG)
        tab.pack(fill="x", pady=(0, 4))                   # frame que contem a grade de celulas
        tab.columnconfigure(0, weight=1)                   # coluna referencia com peso igual
        tab.columnconfigure(1, weight=1)                   # coluna medicao com peso igual

        # Cabecalhos das colunas
        tk.Label(tab, text="REFERENCIA  (media +- dp)", bg=BG2, fg=GOLD,
                 font=FONT_SMALL, pady=2).grid(row=0, column=0, sticky="ew", padx=(0,4))  # titulo coluna referencia
        tk.Label(tab, text="PECA MEDIDA  (media +- dp)", bg=BG2, fg=ACCENT,
                 font=FONT_SMALL, pady=2).grid(row=0, column=1, sticky="ew")              # titulo coluna medicao

        # Definicao das metricas da tabela: (rotulo, chave no dicionario)
        metricas_def = [
            ("Ra  [um]",        "ra"),          # rugosidade media (Ra)
            ("Rq  [um]",        "rq"),          # rugosidade RMS (Rq)
            ("Rz  [um]",        "rz"),          # amplitude media pico-vale (Rz)
            ("Grad. energia",   "grad_energy"), # energia do gradiente de Sobel
            ("Entropia [bits]", "entropia"),    # entropia da textura
        ]

        self._cells = {}                                   # dicionario para acessar as celulas depois (slot, key) -> (lbl_val, lbl_dp)
        for r_idx, (label, key) in enumerate(metricas_def):       # itera sobre as 5 metricas
            for c_idx, slot_name in enumerate(("ref", "med")):    # itera sobre as 2 colunas (referencia e medicao)
                cor = GOLD if slot_name == "ref" else ACCENT       # cor dourada para referencia, ciana para medicao
                cell = tk.Frame(tab, bg=BG, highlightbackground=BORDER,
                                highlightthickness=1)              # frame de cada celula com borda
                cell.grid(row=r_idx+1, column=c_idx, sticky="ew", # posiciona na grade
                          padx=(0,4) if c_idx==0 else 0, pady=1)  # pequeno espaco entre colunas
                tk.Label(cell, text=label, bg=BG2, fg=FG_DIM,
                         font=FONT_SMALL, padx=4, pady=1, anchor="w").pack(fill="x")  # rotulo da metrica no cabecalho da celula
                lbl_val = tk.Label(cell, text="—", bg=BG, fg=cor,
                                   font=("Courier", 10, "bold"), padx=4, pady=1, anchor="w")
                lbl_val.pack(fill="x")                    # label do valor principal (ex: "1.583")
                lbl_dp = tk.Label(cell, text="", bg=BG, fg=FG_DIM,
                                  font=("Courier", 6), padx=4, pady=0, anchor="w")
                lbl_dp.pack(fill="x")                     # label do desvio padrao (ex: "+- 0.042  (dp  n=10)")
                self._cells[(slot_name, key)] = (lbl_val, lbl_dp)  # armazena referencia para atualizar depois

        # Card de classificacao ISO da peca medida
        cls_f, cls_i = frame_card(right, "Classificacao ISO estimada — peca medida")
        cls_f.pack(fill="x", pady=(0, 4))
        self._lbl_classe = tk.Label(cls_i, text="—", bg=BG, fg=FG,
                                    font=("Courier", 9, "bold"), anchor="w")  # exibe classe ISO e Ra estimado
        self._lbl_classe.pack(fill="x")
        self._lbl_intervalo = tk.Label(cls_i, text="", bg=BG, fg=FG_DIM,
                                       font=("Courier", 7), anchor="w")       # exibe intervalo de confianca (1 DP)
        self._lbl_intervalo.pack(fill="x")

        # Graficos matplotlib embutidos
        self._fig, axes = plt.subplots(1, 3, figsize=(9, 3.8),
                                        facecolor="#0d1117")       # figura com 3 subplots lado a lado, tamanho aumentado
        self._fig.tight_layout(pad=2.0)                            # ajusta espacamento entre subplots
        self._ax_hist, self._ax_box, self._ax_prof = axes          # desempacota os 3 eixos nomeados

        for ax in axes:                                            # aplica estilo escuro em todos os eixos
            ax.set_facecolor(BG3)                                  # fundo escuro para cada subplot
            for sp in ax.spines.values(): sp.set_edgecolor(BORDER) # bordas do grafico em cinza escuro
            ax.tick_params(colors=FG_DIM, labelsize=6)             # ticks em cinza esverdeado, fonte pequena

        self._canvas_mpl = FigureCanvasTkAgg(self._fig, master=right)  # embute a figura matplotlib no frame tkinter
        self._canvas_mpl.get_tk_widget().pack(fill="both", expand=True) # expande para ocupar todo o espaco restante
        self._placeholder_graficos()                               # exibe "sem dados" nos graficos inicialmente

    # ── Logica de analise ─────────────────────────────────────────────────────

    def _analisar(self):
        """Valida as entradas, processa todas as imagens e exibe os resultados."""

        # Verifica se ha fotos suficientes em cada slot
        if len(self._slot_ref.caminhos) < MIN_FOTOS:
            messagebox.showwarning("Atencao",
                f"Referencia: {len(self._slot_ref.caminhos)} foto(s). Minimo: {MIN_FOTOS}.")
            return                                         # interrompe se nao atingiu o minimo

        if len(self._slot_med.caminhos) < MIN_FOTOS:
            messagebox.showwarning("Atencao",
                f"Peca a medir: {len(self._slot_med.caminhos)} foto(s). Minimo: {MIN_FOTOS}.")
            return                                         # interrompe se nao atingiu o minimo

        # Valida o campo de Ra real
        ra_str = self._entry_ra.get().strip().replace(",", ".")  # le o campo e substitui virgula por ponto
        try:
            ra_real = float(ra_str)                        # tenta converter para float
            if ra_real <= 0: raise ValueError              # Ra negativo ou zero nao faz sentido
        except ValueError:
            messagebox.showwarning("Atencao", "Informe o Ra real da referencia (ex: 1.6).")
            return                                         # interrompe se valor invalido

        # Desabilita o botao durante o processamento
        self._btn_analisar.config(state="disabled", text="Processando...")
        self._btn_pdf.config(state="disabled")
        self.update()                                      # forca atualizacao da GUI antes do processamento pesado

        try:
            # Extrai metricas de cada imagem individualmente
            raw_ref = [extrair_metricas(p) for p in self._slot_ref.caminhos]  # lista de dicionarios para referencia
            raw_med = [extrair_metricas(p) for p in self._slot_med.caminhos]  # lista de dicionarios para medicao

            # Agrega (media + desvio) sobre todas as imagens
            agg_ref = agregar_metricas(raw_ref)            # metricas agregadas da referencia
            agg_med = agregar_metricas(raw_med)            # metricas agregadas da medicao

            # Calcula o fator de calibracao: converte unidades de intensidade -> micrometros
            fator = ra_real / agg_ref["ra_mean"]           # fator = Ra_real_informado / Ra_proxy_medio_da_referencia

            # Aplica o fator nas metricas dimensionais (Ra, Rq, Rz) de ambos os casos
            for key in ("ra", "rq", "rz"):
                agg_ref[f"{key}_cal"]     = agg_ref[f"{key}_mean"] * fator  # valor calibrado da referencia
                agg_ref[f"{key}_cal_std"] = agg_ref[f"{key}_std"]  * fator  # desvio padrao calibrado da referencia
                agg_med[f"{key}_cal"]     = agg_med[f"{key}_mean"] * fator  # valor calibrado da medicao
                agg_med[f"{key}_cal_std"] = agg_med[f"{key}_std"]  * fator  # desvio padrao calibrado da medicao

            # Armazena resultados para uso posterior no PDF
            self._last_agg_ref = agg_ref
            self._last_agg_med = agg_med
            self._last_raw_ref = raw_ref
            self._last_raw_med = raw_med
            self._last_fator   = fator
            self._last_ra_real = ra_real

            # Atualiza a interface com os resultados
            self._mostrar_resultados(agg_ref, agg_med, fator, raw_ref, raw_med)
            self._btn_pdf.config(state="normal")           # habilita o botao de PDF apos analise bem-sucedida

        except Exception as e:
            messagebox.showerror("Erro", str(e))           # exibe mensagem de erro se algo falhar

        finally:
            self._btn_analisar.config(state="normal", text="ANALISAR")  # reabilita botao independente do resultado

    # ── Atualizacao da interface com resultados ────────────────────────────────

    def _mostrar_resultados(self, ref, med, fator, raw_ref, raw_med):
        """Preenche as celulas da tabela e os labels de classificacao com os resultados calculados."""

        self._lbl_fator.config(text=f"{fator:.5f}")        # exibe o fator de calibracao com 5 casas decimais

        # Preenche cada celula da tabela para referencia e medicao
        for slot_name, agg in (("ref", ref), ("med", med)):
            for key in ("ra", "rq", "rz"):                 # metricas com calibracao em micrometros
                v, std = agg[f"{key}_cal"], agg[f"{key}_cal_std"]   # valor calibrado e desvio padrao calibrado
                self._cells[(slot_name, key)][0].config(text=f"{v:.3f}")         # atualiza label de valor
                self._cells[(slot_name, key)][1].config(
                    text=f"+- {std:.3f}  (dp  n={agg['n']})")       # atualiza label de desvio

            for key in ("grad_energy", "entropia"):        # metricas sem calibracao (em unidades proprias)
                v, std = agg[f"{key}_mean"], agg[f"{key}_std"]      # media e desvio padrao brutos
                self._cells[(slot_name, key)][0].config(text=f"{v:.2f}")         # atualiza label de valor
                self._cells[(slot_name, key)][1].config(
                    text=f"+- {std:.2f}  (dp  n={agg['n']})")       # atualiza label de desvio

        # Atualiza a classificacao ISO e o intervalo de confianca
        ra_med  = med["ra_cal"]                            # Ra calibrado da peca medida
        ra_std  = med["ra_cal_std"]                        # desvio padrao calibrado da peca medida
        cls_txt, cls_cor = classificar(ra_med)             # obtem texto e cor da classe ISO
        self._lbl_classe.config(
            text=f"Ra = {ra_med:.3f} um   ->   {cls_txt}", fg=cls_cor)  # exibe Ra e classe
        self._lbl_intervalo.config(
            text=f"Intervalo (1 dp):  "
                 f"{max(0, ra_med - ra_std):.3f}  a  {ra_med + ra_std:.3f} um")  # intervalo Ra +/- 1 DP

        self._plotar_graficos(ref, med, raw_ref, raw_med)  # atualiza os graficos

    def _plotar_graficos(self, ref, med, raw_ref, raw_med):
        """Plota os 3 graficos: histograma comparativo, boxplot e Ra por foto."""

        # Calcula Ra calibrado de cada imagem individual para os graficos
        ra_r = [r["ra"] * (ref["ra_cal"] / ref["ra_mean"]) for r in raw_ref]  # Ra calibrado de cada foto da referencia
        ra_m = [r["ra"] * (med["ra_cal"] / med["ra_mean"]) for r in raw_med]  # Ra calibrado de cada foto da medicao

        # Grafico 1: Histograma medio comparativo
        ax = self._ax_hist
        ax.clear(); ax.set_facecolor(BG3)                  # limpa e reaplica fundo escuro
        edges = ref["hist_edges"]                          # limites dos bins (compartilhados entre os dois histogramas)
        ax.plot(edges[:-1], ref["hist_mean"], color=GOLD,  lw=0.9, alpha=0.85,
                label=f"Ref (n={ref['n']})")               # linha dourada = distribuicao de intensidade da referencia
        ax.plot(edges[:-1], med["hist_mean"], color=ACCENT, lw=0.9, alpha=0.85,
                label=f"Med (n={med['n']})")               # linha ciana = distribuicao de intensidade da medicao
        ax.legend(fontsize=6, facecolor=BG2, edgecolor=BORDER, labelcolor=FG)  # legenda com estilo escuro
        ax.set_title("Histograma medio", color=FG_DIM, fontsize=7, pad=3)       # titulo do grafico
        ax.set_xlabel("Nivel de cinza", color=FG_DIM, fontsize=6)               # eixo X
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)                  # bordas do grafico
        ax.tick_params(colors=FG_DIM, labelsize=6)                              # ticks

        # Grafico 2: Boxplot do Ra por imagem
        ax2 = self._ax_box
        ax2.clear(); ax2.set_facecolor(BG3)
        bp = ax2.boxplot([ra_r, ra_m], patch_artist=True,  # cria boxplot com duas caixas
                         medianprops=dict(color=BG, lw=1.5),           # linha da mediana
                         whiskerprops=dict(color=FG_DIM),              # bigodes
                         capprops=dict(color=FG_DIM),                  # tampas dos bigodes
                         flierprops=dict(marker="o", color=FG_DIM,
                                         markerfacecolor=FG_DIM, markersize=3))  # outliers
        bp["boxes"][0].set_facecolor(GOLD  + "55"); bp["boxes"][0].set_edgecolor(GOLD)   # caixa da referencia dourada
        bp["boxes"][1].set_facecolor(ACCENT+ "55"); bp["boxes"][1].set_edgecolor(ACCENT) # caixa da medicao ciana
        ax2.set_xticks([1, 2])
        ax2.set_xticklabels(["Ref", "Medida"], color=FG_DIM, fontsize=6)  # rotulos dos eixos
        ax2.set_title("Ra por imagem [um]", color=FG_DIM, fontsize=7, pad=3)
        for sp in ax2.spines.values(): sp.set_edgecolor(BORDER)
        ax2.tick_params(colors=FG_DIM, labelsize=6)

        # Grafico 3: Ra de cada foto em sequencia (dispersao temporal)
        ax3 = self._ax_prof
        ax3.clear(); ax3.set_facecolor(BG3)
        ax3.plot(ra_r, "o-", color=GOLD,  ms=3, lw=0.8, alpha=0.85, label="Ref")    # linha dourada da referencia
        ax3.plot(ra_m, "o-", color=ACCENT, ms=3, lw=0.8, alpha=0.85, label="Medida") # linha ciana da medicao
        ax3.axhline(np.mean(ra_r), color=GOLD,  lw=0.6, ls="--", alpha=0.6)  # linha tracejada da media da referencia
        ax3.axhline(np.mean(ra_m), color=ACCENT, lw=0.6, ls="--", alpha=0.6) # linha tracejada da media da medicao
        ax3.legend(fontsize=6, facecolor=BG2, edgecolor=BORDER, labelcolor=FG)
        ax3.set_title("Ra por foto [um]", color=FG_DIM, fontsize=7, pad=3)
        ax3.set_xlabel("Foto #", color=FG_DIM, fontsize=6)
        for sp in ax3.spines.values(): sp.set_edgecolor(BORDER)
        ax3.tick_params(colors=FG_DIM, labelsize=6)

        self._fig.tight_layout(pad=1.5)                    # reajusta espacamento dos subplots
        self._canvas_mpl.draw()                            # redesenha o canvas com os novos graficos

    def _placeholder_graficos(self):
        """Exibe mensagem 'sem dados' em todos os graficos (estado inicial)."""
        for ax in [self._ax_hist, self._ax_box, self._ax_prof]:
            ax.clear(); ax.set_facecolor(BG3)              # limpa e reaplica fundo escuro
            ax.text(0.5, 0.5, "sem dados", transform=ax.transAxes,
                    ha="center", va="center", color="#2a3a44", fontsize=8)  # texto centralizado em cinza
            for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
            ax.tick_params(colors=FG_DIM, labelsize=6)
        self._canvas_mpl.draw()                            # renderiza o estado placeholder

    # ── Exportacao de PDF ─────────────────────────────────────────────────────

    def _exportar_pdf(self):
        """Abre dialogo de salvar arquivo e dispara a geracao do PDF."""
        if self._last_agg_med is None:                     # guarda curto: exige analise previa
            messagebox.showwarning("Atencao", "Realize a analise antes de exportar.")
            return

        path = filedialog.asksaveasfilename(               # abre dialogo "Salvar como"
            title="Salvar relatorio PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")])
        if not path:                                       # usuario cancelou
            return

        try:
            self._gerar_pdf(path)                          # chama a funcao que monta o PDF
            messagebox.showinfo("Sucesso", f"PDF salvo em:\n{path}")  # confirma o salvamento
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF", str(e))  # exibe erro se algo falhar

    def _gerar_pdf(self, path):
        """Monta e salva o relatorio PDF completo com metricas, graficos e tabela AFNOR/ISO."""

        # Recupera os dados da ultima analise
        ref     = self._last_agg_ref                       # metricas agregadas da referencia
        med     = self._last_agg_med                       # metricas agregadas da medicao
        raw_r   = self._last_raw_ref                       # resultados individuais da referencia
        raw_m   = self._last_raw_med                       # resultados individuais da medicao
        fator   = self._last_fator                         # fator de calibracao
        ra_real = self._last_ra_real                       # Ra real informado

        # Gera a figura matplotlib em branco (fundo branco para o PDF)
        fig_pdf, axes = plt.subplots(1, 3, figsize=(11, 3), facecolor="white")
        fig_pdf.tight_layout(pad=2.5)                      # espacamento entre subplots

        edges = ref["hist_edges"]                          # limites dos bins do histograma
        ra_r  = [r["ra"] * (ref["ra_cal"] / ref["ra_mean"]) for r in raw_r]  # Ra calibrado por foto (referencia)
        ra_m  = [r["ra"] * (med["ra_cal"] / med["ra_mean"]) for r in raw_m]  # Ra calibrado por foto (medicao)

        # Subplot 1 do PDF: histograma comparativo (cores para fundo branco)
        ax0 = axes[0]
        ax0.plot(edges[:-1], ref["hist_mean"], color="#c8860a", lw=1.2,
                 label=f"Ref (n={ref['n']})")              # dourado escuro para contraste em branco
        ax0.plot(edges[:-1], med["hist_mean"], color="#0077aa", lw=1.2,
                 label=f"Med (n={med['n']})")              # azul para contraste em branco
        ax0.legend(fontsize=7)
        ax0.set_title("Histograma medio", fontsize=8)
        ax0.set_xlabel("Nivel de cinza", fontsize=7)
        ax0.tick_params(labelsize=7)

        # Subplot 2 do PDF: boxplot do Ra por imagem
        ax1 = axes[1]
        bp = ax1.boxplot([ra_r, ra_m], patch_artist=True,
                         medianprops=dict(color="white", lw=1.5))  # mediana branca
        bp["boxes"][0].set_facecolor("#ffc10755"); bp["boxes"][0].set_edgecolor("#c8860a")  # caixa referencia
        bp["boxes"][1].set_facecolor("#00e5ff55"); bp["boxes"][1].set_edgecolor("#0077aa")  # caixa medicao
        ax1.set_xticks([1, 2])
        ax1.set_xticklabels(["Ref", "Medida"], fontsize=7)
        ax1.set_title("Ra por imagem [um]", fontsize=8)
        ax1.tick_params(labelsize=7)

        # Subplot 3 do PDF: Ra por foto em sequencia
        ax2 = axes[2]
        ax2.plot(ra_r, "o-", color="#c8860a", ms=4, lw=1, label="Ref")
        ax2.plot(ra_m, "o-", color="#0077aa",  ms=4, lw=1, label="Medida")
        ax2.axhline(np.mean(ra_r), color="#c8860a", lw=0.8, ls="--", alpha=0.7)  # media da referencia
        ax2.axhline(np.mean(ra_m), color="#0077aa",  lw=0.8, ls="--", alpha=0.7) # media da medicao
        ax2.legend(fontsize=7)
        ax2.set_title("Ra por foto [um]", fontsize=8)
        ax2.set_xlabel("Foto #", fontsize=7)
        ax2.tick_params(labelsize=7)

        # Salva a figura como PNG em um buffer de memoria (sem criar arquivo temporario)
        buf = io.BytesIO()                                 # buffer em memoria
        fig_pdf.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                        facecolor="white")                 # salva com 150 DPI e fundo branco
        buf.seek(0)                                        # volta o cursor do buffer para o inicio
        plt.close(fig_pdf)                                 # fecha a figura para liberar memoria

        # ── Montagem do PDF com ReportLab ─────────────────────────────────────

        doc = SimpleDocTemplate(                           # cria o documento PDF
            path, pagesize=A4,                             # pagina A4
            leftMargin=20*mm, rightMargin=20*mm,           # margens laterais de 20mm
            topMargin=18*mm, bottomMargin=18*mm)           # margens superior/inferior de 18mm

        W = A4[0] - 40*mm                                  # largura util da pagina (A4 menos margens)

        # Define estilos de paragrafo personalizados
        styles = getSampleStyleSheet()                     # estilos padrao do ReportLab

        s_title  = ParagraphStyle("title",  fontSize=14, fontName="Helvetica-Bold",
                                  textColor=colors.HexColor("#003366"), spaceAfter=2)   # titulo principal azul escuro
        s_sub    = ParagraphStyle("sub",    fontSize=8, fontName="Helvetica",
                                  textColor=colors.HexColor("#555555"), spaceAfter=2)   # subtitulo cinza
        s_author = ParagraphStyle("author", fontSize=9, fontName="Helvetica-Bold",
                                  textColor=colors.HexColor("#003366"), spaceAfter=1)   # autor em negrito azul
        s_note   = ParagraphStyle("note",   fontSize=7.5, fontName="Helvetica-Oblique",
                                  textColor=colors.HexColor("#666666"), spaceAfter=4)   # nota em italico cinza
        s_section= ParagraphStyle("section",fontSize=10, fontName="Helvetica-Bold",
                                  textColor=colors.HexColor("#003366"),
                                  spaceBefore=10, spaceAfter=4)                         # secao em negrito azul
        s_body   = ParagraphStyle("body",   fontSize=8.5, fontName="Helvetica",
                                  textColor=colors.black, spaceAfter=3)                 # paragrafo normal
        s_warn   = ParagraphStyle("warn",   fontSize=7.5, fontName="Helvetica-Oblique",
                                  textColor=colors.HexColor("#7a5000"),
                                  backColor=colors.HexColor("#fff8e1"),
                                  spaceAfter=4, leftIndent=6, rightIndent=6)            # aviso com fundo amarelo claro

        story = []                                         # lista de elementos que compoem o PDF (ordem de impressao)
        now   = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")  # data/hora atual formatada

        # Cabecalho: titulo + data/hora em linha
        header_data = [[
            Paragraph("RELATORIO DE ESTIMATIVA DE RUGOSIDADE", s_title),  # titulo a esquerda
            Paragraph(f"Gerado em: {now}", ParagraphStyle(                  # data a direita
                "rt", fontSize=8, fontName="Helvetica",
                textColor=colors.HexColor("#555555"), alignment=TA_RIGHT))
        ]]
        header_tbl = Table(header_data, colWidths=[W*0.65, W*0.35])  # tabela de 2 colunas para cabecalho
        header_tbl.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),         # alinhamento vertical centralizado
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),          # espacamento inferior
        ]))
        story.append(header_tbl)                           # adiciona cabecalho ao PDF

        story.append(Paragraph("Author: Bruno Bernardinetti - Stellantis", s_author))  # linha de autoria
        story.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor("#003366"), spaceAfter=4))       # linha separadora azul

        story.append(Paragraph(                            # nota sobre AFNOR/ISO
            "Nota: Se for usar notacao AFNOR (Francesa), utilize a correlacao com a "
            "ISO 1302 conforme tabela ao final deste relatorio.", s_note))

        story.append(Paragraph(                            # descricao do metodo
            f"Metodo: Analise de textura por imagem de microscopio USB digital  |  "
            f"Minimo de {MIN_FOTOS} imagens por caso  |  "
            f"Calibracao por peca de referencia", s_body))

        # Secao de parametros da analise
        story.append(Paragraph("Parametros da Analise", s_section))

        param_data = [                                     # dados da tabela de parametros
            ["Parametro", "Referencia", "Peca Medida"],
            ["Numero de imagens", str(ref["n"]), str(med["n"])],
            ["Ra real informado (um)", f"{ra_real:.3f}", "—"],
            ["Fator de calibracao (um/u.i.)", f"{fator:.5f}", f"{fator:.5f}"],
        ]
        param_files_ref = "\n".join(
            [os.path.basename(p) for p in self._slot_ref.caminhos])  # lista de arquivos da referencia
        param_files_med = "\n".join(
            [os.path.basename(p) for p in self._slot_med.caminhos])  # lista de arquivos da medicao

        ptbl = Table(param_data, colWidths=[W*0.40, W*0.30, W*0.30])  # tabela de parametros com 3 colunas
        ptbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#003366")),  # cabecalho azul escuro
            ("TEXTCOLOR",    (0,0), (-1,0), colors.white),                # texto branco no cabecalho
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),            # negrito no cabecalho
            ("FONTSIZE",     (0,0), (-1,-1), 8),                          # fonte 8pt
            ("ALIGN",        (0,0), (-1,-1), "CENTER"),                   # centralizado
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),                   # verticalmente centrado
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.HexColor("#f0f4f8"), colors.white]),                  # zebrado azul claro / branco
            ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),  # grade cinza fina
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ]))
        story.append(ptbl)                                 # adiciona tabela de parametros ao PDF

        # Secao de metricas
        story.append(Paragraph("Resultados das Metricas", s_section))

        met_header = ["Metrica", "Referencia\nMedia", "Referencia\n+- DP",
                      "Peca Medida\nMedia", "Peca Medida\n+- DP"]       # cabecalho da tabela de metricas
        met_rows = [met_header]                            # inicializa com cabecalho

        metrics_list = [                                   # definicao das metricas: (rotulo, chave, calibrado?)
            ("Ra [um]",             "ra",           True),   # Ra: calibrado em micrometros
            ("Rq [um]",             "rq",           True),   # Rq: calibrado em micrometros
            ("Rz [um]",             "rz",           True),   # Rz: calibrado em micrometros
            ("Energia Gradiente",   "grad_energy",  False),  # gradiente: sem calibracao (u.i.)
            ("Entropia [bits]",     "entropia",     False),  # entropia: sem calibracao (bits)
        ]

        for label, key, calibrado in metrics_list:         # itera sobre as metricas e monta as linhas da tabela
            if calibrado:                                   # metricas com fator de calibracao aplicado
                v_r, std_r = ref[f"{key}_cal"], ref[f"{key}_cal_std"]
                v_m, std_m = med[f"{key}_cal"], med[f"{key}_cal_std"]
                fmt = ".3f"                                # 3 casas decimais para micrometros
            else:                                          # metricas sem calibracao
                v_r, std_r = ref[f"{key}_mean"], ref[f"{key}_std"]
                v_m, std_m = med[f"{key}_mean"], med[f"{key}_std"]
                fmt = ".2f"                                # 2 casas decimais
            met_rows.append([label, f"{v_r:{fmt}}", f"+- {std_r:{fmt}}",
                              f"{v_m:{fmt}}", f"+- {std_m:{fmt}}"])

        cw = [W*0.25, W*0.18, W*0.18, W*0.18, W*0.21]    # larguras das 5 colunas da tabela de metricas
        mtbl = Table(met_rows, colWidths=cw)
        mtbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#003366")),  # cabecalho azul
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1),
             [colors.HexColor("#f0f4f8"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("BACKGROUND",    (3,1), (4,1), colors.HexColor("#e3f2fd")),  # destaque azul claro nas colunas de Ra da medicao
            ("FONTNAME",      (3,1), (3,1), "Helvetica-Bold"),            # negrito no Ra da medicao
        ]))
        story.append(mtbl)

        # Secao de classificacao ISO
        story.append(Paragraph("Classificacao ISO 1302", s_section))

        ra_m_val  = med["ra_cal"]                          # Ra calibrado final da peca medida
        ra_m_std  = med["ra_cal_std"]                      # desvio padrao calibrado
        cls_txt, _ = classificar(ra_m_val)                 # texto da classe ISO

        story.append(Paragraph(
            f"Ra estimado da peca medida: <b>{ra_m_val:.3f} um  +/-  {ra_m_std:.3f} um</b>",
            s_body))                                       # Ra com intervalo
        story.append(Paragraph(
            f"Classificacao: <b>{cls_txt}</b>", s_body))   # classe ISO
        story.append(Paragraph(
            f"Intervalo de confianca (1 DP):  "
            f"{max(0, ra_m_val - ra_m_std):.3f} um  a  {ra_m_val + ra_m_std:.3f} um",
            s_body))                                       # limite inferior e superior
        story.append(Spacer(1, 4))                         # espaco vertical
        story.append(Paragraph(
            "Aviso: Os valores sao estimativas baseadas em analise de imagem. "
            "Para resultados absolutos, utilize rugosimetro de contato ou optico calibrado.",
            s_warn))                                       # aviso sobre limitacoes do metodo

        # Secao de graficos (imagem PNG embutida)
        story.append(Paragraph("Graficos de Analise", s_section))
        img_rl = RLImage(buf, width=W, height=W * 3/11)   # embute a imagem do buffer com proporcao 11:3
        story.append(img_rl)                               # adiciona os graficos ao PDF

        # Secao da tabela AFNOR / ISO 1302
        story.append(Paragraph(
            "Correlacao AFNOR (Notacao Francesa) x ISO 1302", s_section))
        story.append(Paragraph(
            "Referencia: NF E 05-015 / ISO 1302. "
            "As classes N da notacao francesa AFNOR correspondem diretamente "
            "as classes N da ISO 1302 com os seguintes valores de Ra:", s_body))

        afnor_rows = [["Classe (AFNOR / ISO 1302)", "Ra maximo [um]", "Processo tipico"]]  # cabecalho
        processos  = [                                     # descricao do processo tipico por classe
            "Superacabamento / lapidacao",
            "Retificacao fina / polimento",
            "Retificacao",
            "Retificacao grossa",
            "Torneamento / fresamento fino",
            "Torneamento convencional",
            "Fresamento grosso",
            "Desbaste",
            "Fundicao / forjamento fino",
            "Fundicao bruta",
            "Corte a chama",
            "Superficie bruta / nao usinada",
        ]
        for (cls_n, ra_val), proc in zip(AFNOR_ISO, processos):  # monta as linhas da tabela AFNOR/ISO
            afnor_rows.append([cls_n, ra_val, proc])

        atbl = Table(afnor_rows, colWidths=[W*0.25, W*0.20, W*0.55])  # tabela de 3 colunas
        atbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#003366")),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("ALIGN",         (1,0), (1,-1), "CENTER"),    # coluna Ra centralizada
            ("ALIGN",         (0,0), (0,-1), "CENTER"),    # coluna Classe centralizada
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1),
             [colors.HexColor("#f0f4f8"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story.append(atbl)                                 # adiciona tabela AFNOR ao PDF

        # Rodape com linha separadora e identificacao
        story.append(Spacer(1, 8))                         # espaco antes do rodape
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#cccccc"), spaceAfter=4))  # linha separadora cinza fina
        story.append(Paragraph(
            f"Documento gerado automaticamente pelo Estimador de Rugosidade  |  "
            f"Author: Bruno Bernardinetti - Stellantis  |  {now}",
            ParagraphStyle("footer", fontSize=7, fontName="Helvetica",
                           textColor=colors.HexColor("#888888"),
                           alignment=TA_CENTER)))           # rodape centralizado em cinza

        doc.build(story)                                   # compila todos os elementos e salva o arquivo PDF


# ── Ponto de entrada do programa ──────────────────────────────────────────────

if __name__ == "__main__":
    app = App()          # cria a instancia da janela principal
    app.mainloop()       # inicia o loop de eventos do tkinter (mantem a janela aberta)