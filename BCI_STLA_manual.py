"""
Gerador de documentacao tecnica PDF — BCI KNUCKLE SOFTWARE
Output: manual.pdf (mesma pasta)
"""
import os, datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak, KeepTogether
)

OUT     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual.pdf")
CONTATO = "+55 32 9 9965-0392"
VERSION = "v1.0.0"
REPO    = "github.com/BrunoBernar/rugosidade_optica_teste"
NOW     = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

# ── Paleta ────────────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#1a3a5c")
BLUE   = colors.HexColor("#2563a8")
LBLUE  = colors.HexColor("#dce8f5")
CYAN   = colors.HexColor("#00e5ff")
GOLD   = colors.HexColor("#ffc107")
LGRAY  = colors.HexColor("#f4f6f8")
MGRAY  = colors.HexColor("#c0ccd8")
DGRAY  = colors.HexColor("#4a5568")
BLACK  = colors.black
WHITE  = colors.white
WARN_Y = colors.HexColor("#fff8e1")
WARN_B = colors.HexColor("#e65100")
CODE_B = colors.HexColor("#eef2f7")

ss = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, parent=ss["Normal"], **kw)

COVER_TITLE = S("CT", fontSize=28, textColor=NAVY,  alignment=TA_CENTER, fontName="Helvetica-Bold",  spaceAfter=2)
COVER_SUB   = S("CS", fontSize=13, textColor=BLUE,  alignment=TA_CENTER, fontName="Helvetica-Oblique", spaceAfter=14)
H1  = S("H1", fontSize=13, textColor=NAVY,  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=3)
H2  = S("H2", fontSize=10, textColor=BLUE,  fontName="Helvetica-Bold", spaceBefore=7,  spaceAfter=2)
BODY= S("Bo", fontSize=9,  textColor=BLACK, leading=14, spaceAfter=4)
BULL= S("Bu", fontSize=9,  textColor=BLACK, leading=13, spaceAfter=2, leftIndent=14, firstLineIndent=-8)
NOTE= S("No", fontSize=8,  textColor=DGRAY, fontName="Helvetica-Oblique", leading=12, leftIndent=10, spaceAfter=3)
CODE= S("Co", fontSize=8,  textColor=NAVY,  fontName="Courier", leading=12, leftIndent=8, spaceAfter=2)
HDR = S("Hd", fontSize=7,  textColor=DGRAY, alignment=TA_LEFT)
FTR = S("Ft", fontSize=7,  textColor=DGRAY, alignment=TA_CENTER)

W = A4[0] - 40*mm  # largura útil


def hr(color=MGRAY):
    return HRFlowable(width="100%", thickness=0.5, color=color, spaceAfter=6, spaceBefore=2)

def h1(text):
    return [Paragraph(text, H1), hr(BLUE)]

def h2(text):
    return [Paragraph(text, H2)]

def body(text):
    return Paragraph(text, BODY)

def bullet(items):
    return [Paragraph(f"• {t}", BULL) for t in items]

def code(text):
    t = Table([[Paragraph(text, CODE)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), CODE_B),
        ("BOX",        (0,0),(-1,-1), 0.5, MGRAY),
        ("TOPPADDING", (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0),(-1,-1), 8),
    ]))
    return t

def warn(text):
    t = Table([[Paragraph(text, NOTE)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), WARN_Y),
        ("BOX",        (0,0),(-1,-1), 0.5, GOLD),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
        ("TOPPADDING", (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ]))
    return t

def tbl(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("FONTNAME",   (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,0),(-1,-1), 8),
        ("LEADING",    (0,0),(-1,-1), 11),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LGRAY]),
        ("GRID",       (0,0),(-1,-1), 0.4, MGRAY),
        ("ALIGN",      (0,0),(-1,-1), "CENTER"),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ]
    if header:
        style += [
            ("BACKGROUND", (0,0),(-1,0), NAVY),
            ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
            ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(style))
    return t

def sp(n=1):
    return Spacer(1, n*3*mm)

# ── Cabeçalho / rodapé de página ──────────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(NAVY)
        canvas.drawString(20*mm, h - 13*mm, "BCI - KNUCKLE SOFTWARE | Documentacao Tecnica")
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DGRAY)
        canvas.drawRightString(w - 20*mm, h - 13*mm, f"Bruno Bernardinetti | Stellantis")
        canvas.setStrokeColor(MGRAY)
        canvas.setLineWidth(0.4)
        canvas.line(20*mm, h - 15*mm, w - 20*mm, h - 15*mm)

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DGRAY)
        canvas.drawString(20*mm, 12*mm, f"Gerado em: {NOW}")
        canvas.drawCentredString(w/2, 12*mm, f"Pagina {doc.page}")
        canvas.drawRightString(w - 20*mm, 12*mm, REPO)
        canvas.line(20*mm, 14*mm, w - 20*mm, 14*mm)
    canvas.restoreState()


# ── BUILD ─────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=22*mm, bottomMargin=22*mm,
    )

    story = []

    # ── CAPA ──────────────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("DOCUMENTACAO TECNICA", S("dc", fontSize=11, textColor=BLUE,
            alignment=TA_CENTER, fontName="Helvetica-Oblique", spaceAfter=4)),
        Paragraph("BCI — KNUCKLE SOFTWARE", COVER_TITLE),
        hr(NAVY),
        Paragraph("Surface Roughness &amp; Interference Fit Analyzer", COVER_SUB),
        sp(2),
    ]
    cover_data = [
        ["Parametro", "Informacao"],
        ["Autor",       "Bruno Bernardinetti"],
        ["Organizacao", "Stellantis | Brasil"],
        ["Versao",      VERSION],
        ["Repositorio", REPO],
        ["Gerado em",   NOW],
        ["Descricao",   "Descricao dos calculos, algoritmos e funcionalidades dos quatro modulos."],
    ]
    story.append(tbl(cover_data, [55*mm, W - 55*mm]))
    story.append(PageBreak())

    # ── 1. INTRODUÇÃO ──────────────────────────────────────────────────────────
    story += h1("1. Introducao")
    story.append(body(
        "Este documento descreve os fundamentos matematicos, algoritmos e funcionalidades do "
        "<b>BCI - KNUCKLE SOFTWARE</b>, desenvolvido por Bruno Bernardinetti (Stellantis). "
        "A ferramenta integra quatro modulos principais de engenharia de produto e qualidade:"
    ))
    story += bullet([
        "<b>Modulo 1 — Analise de Rugosidade por Imagem:</b> estimativa do parametro Ra a partir de analise de textura de imagens digitais de microscopio.",
        "<b>Modulo 2 — Calculo de Interferencia (Knuckle Press-Fit):</b> calculo de pressao e forca de encaixe pelas equacoes de Lame para cilindros de parede grossa.",
        "<b>Modulo 3 — Comparador de Curvas XML:</b> visualizacao e classificacao OK/NOK de curvas Forca x Curso exportadas por prensas maXYmos NC (Kistler/Sinpac).",
        "<b>Modulo 4 — Golden Curve Analyzer:</b> geracao de curva teorica de referencia a partir de N curvas OK reais, com deteccao estatistica de anomalias em novas curvas.",
    ])
    story.append(sp())
    story.append(warn(
        "AVISO: O software nao substitui medicao direta por rugosimetro calibrado nem analise por "
        "elementos finitos (FEA). Os resultados sao estimativas de engenharia para triagem e monitoramento de processo."
    ))
    story.append(sp())
    story.append(body(
        "<b>Versao e atualizacoes:</b> o software verifica automaticamente novas versoes no GitHub a cada 7 dias "
        "(apenas quando instalado fora do ambiente de desenvolvimento). Um balao de notificacao estilo Windows aparece "
        "quando uma nova versao e detectada. Em Configuracoes (botao ⚙) e possivel verificar manualmente e escolher "
        "qual versao baixar. O botao ? abre este documento de ajuda."
    ))
    story.append(body(
        "<b>Requisitos:</b> Python 3.10+ | pip install pillow numpy matplotlib scipy reportlab"
    ))
    story.append(PageBreak())

    # ── 2. MÓDULO 1 ────────────────────────────────────────────────────────────
    story += h1("2. Modulo 1 — Analise de Rugosidade por Imagem")
    story += h2("2.1 Visao Geral do Metodo")
    story.append(body(
        "A rugosidade superficial Ra e normalmente medida por instrumentos de contato (rugosimetros) ou opticos. "
        "Este modulo utiliza a correlacao entre metricas de textura de imagens digitais em escala de cinza e o "
        "parametro Ra medido em uma peca de referencia, implementando uma calibracao por fator de proporcionalidade."
    ))
    story.append(body("<b>Fluxo de uso (minimo 10 imagens por peca):</b>"))
    story += bullet([
        "Carregar imagens da peca de REFERENCIA com Ra real conhecido.",
        "Informar o Ra real da referencia em micrometros (ex: 0.8 / 1.6 / 3.2 / 6.3).",
        "Carregar imagens da peca a MEDIR — mesmas condicoes de iluminacao e magnificacao.",
        "Clicar em ANALISAR. O software calcula o fator de calibracao e exibe o Ra estimado.",
        "(Opcional) Exportar relatorio PDF completo.",
    ])

    story += h2("2.2 Extracao de Metricas por Imagem")
    story.append(body(
        "Cada imagem e processada pela funcao <b>extrair_metricas()</b>. A imagem e convertida para escala de cinza "
        "(modo L) e redimensionada para no maximo 512x512 pixels. As metricas calculadas sobre o array de pixels I (0-255) sao:"
    ))
    met_data = [
        ["Metrica", "Formula", "Significado"],
        ["Ra (proxy)",          "mean( |I - mean(I)| )",                   "Desvio medio absoluto dos pixels. Proxy para rugosidade media."],
        ["Rq",                  "sqrt( mean( (I - mean(I))^2 ) )",          "Rugosidade RMS dos tons de cinza. Equivale ao desvio padrao da imagem."],
        ["Rz",                  "mean(5 maximos) - mean(5 minimos)",        "Altura media entre picos e vales extremos. Robusto a outliers."],
        ["Energia do Gradiente","mean( sqrt(Gx^2 + Gy^2) )",               "Filtro de Sobel. Mede variacao espacial."],
        ["Entropia",            "-sum( p * log2(p) )",                      "Entropia do histograma de 256 niveis."],
    ]
    story.append(tbl(met_data, [32*mm, 60*mm, W - 92*mm]))
    story.append(Paragraph(
        "onde Gx e Gy sao os filtros de Sobel horizontal e vertical (scipy.ndimage.sobel), "
        "e p e o vetor de probabilidades do histograma de 256 bins.", NOTE))

    story += h2("2.3 Calibracao pelo Fator de Escala")
    story.append(body("O Ra calculado diretamente da imagem esta em unidades de imagem (u.i.). A conversao e feita por:"))
    story.append(code("fator = Ra_real_ref / Ra_proxy_medio_ref"))
    story.append(code("Metrica_cal = Metrica_proxy x fator"))
    story.append(warn(
        "PREMISSA: O metodo assume relacao linear entre valores de pixel e micrometros para aquele conjunto de imagens. "
        "Mudancas na iluminacao, lente ou aumento invalidam o fator."
    ))

    story += h2("2.4 Agregacao Estatistica")
    story.append(body(
        "Para cada conjunto de imagens a funcao <b>agregar_metricas()</b> calcula media (mean) e desvio padrao (std) "
        "de cada metrica sobre todas as imagens, alem do histograma normalizado medio (64 bins, 0-255)."
    ))

    story += h2("2.5 Classificacao ISO 1302 / AFNOR")
    story.append(body("O Ra estimado e classificado nas classes de acabamento conforme ISO 1302:"))
    iso_data = [
        ["Classe ISO", "Ra max (um)", "Processo tipico"],
        ["N1","0.025","Superacabamento / espelho"],["N2","0.05","Retificacao fina"],
        ["N3","0.1","Retificacao"],["N4","0.2","Retificacao grossa"],
        ["N5","0.4","Torneamento / fresamento fino"],["N6","0.8","Torneamento convencional"],
        ["N7","1.6","Fresamento grosso"],["N8","3.2","Desbaste"],
        ["N9","6.3","Fundicao / forjamento"],["N10","12.5","Fundicao bruta"],
        ["N11","25.0","Corte a chama"],["N12","50.0+","Superficie bruta"],
    ]
    story.append(tbl(iso_data, [25*mm, 30*mm, W - 55*mm]))

    story += h2("2.6 Graficos e Exportacao")
    story += bullet([
        "Histograma medio: distribuicao de tons de cinza para referencia e peca medida.",
        "Boxplot de Ra: distribuicao por imagem para cada conjunto.",
        "Ra por foto: evolucao do Ra calibrado ao longo das imagens do conjunto.",
    ])
    story.append(body("O botao <b>Exportar PDF</b> gera relatorio completo em A4 com tabelas, resultados, graficos e tabela AFNOR/ISO."))
    story.append(PageBreak())

    # ── 3. MÓDULO 2 ────────────────────────────────────────────────────────────
    story += h1("3. Modulo 2 — Calculo de Interferencia (Knuckle Press-Fit)")
    story += h2("3.1 Contexto de Aplicacao")
    story.append(body(
        "Este modulo calcula pressao de contato e forcas de encaixe/desencaixe de um ajuste com interferencia (press-fit) "
        "entre dois cilindros concentricos — tipicamente eixo (shaft) e cubo (hub/knuckle). O metodo e baseado nas equacoes "
        "de Lame para cilindros de parede grossa em regime elastico linear. Valores padrao correspondem ao knuckle Stellantis."
    ))

    story += h2("3.2 Equacoes de Lame — Pressao de Interferencia")
    story.append(body("Para dois cilindros em ajuste de interferencia, a pressao de contato p na interface de raio R e dada por:"))
    story.append(code("p = delta_eff / [ R x (C_hub + C_shaft) ]"))
    story.append(body("com os termos de compliance de cada componente:"))
    story.append(code("C_hub   = (1/Eo) x [ (Ro^2 + R^2) / (Ro^2 - R^2) + vo ]"))
    story.append(code("C_shaft = (1/Ei) x [ (R^2 + Ri^2) / (R^2 - Ri^2) - vi ]"))
    lame_data = [
        ["Simbolo","Unidade","Descricao"],
        ["delta_eff","mm","Interferencia radial efetiva (apos correcao de rugosidade)"],
        ["R","m","Raio nominal da interface (d_nom / 2)"],
        ["Ro","m","Raio externo do cubo"],
        ["Ri","m","Raio interno do eixo (vazado)"],
        ["Eo, Ei","GPa","Modulos de Young do cubo e do eixo"],
        ["vo, vi","---","Coeficientes de Poisson do cubo e do eixo"],
        ["p","MPa","Pressao de contato na interface"],
    ]
    story.append(tbl(lame_data, [22*mm, 20*mm, W - 42*mm]))
    story.append(warn(
        "VALIDADE: Equacoes assumem material homogeneo, isotropico e elasticidade linear. Nao considera gradientes "
        "termicos, carregamentos dinamicos nem fadiga de contato. Para aplicacoes criticas, validar com FEA."
    ))

    story += h2("3.3 Tolerancias e Calculo da Interferencia")
    story.append(code(
        "d_eixo_max = d_nom + desvio_superior_eixo\n"
        "d_furo_min = d_nom + desvio_inferior_furo\n"
        "delta_max  = (d_eixo_max - d_furo_min) / 2   [pior caso]\n"
        "delta_min  = (d_eixo_min - d_furo_max) / 2   [melhor caso]"
    ))

    story += h2("3.4 Correcao de Rugosidade (DIN 7190)")
    story.append(body("Em um press-fit real, os picos de rugosidade se aplainam plasticamente durante a montagem, reduzindo a interferencia efetiva:"))
    story.append(code("delta_eff = delta_nom - (Ra_eixo + Ra_cubo) x 10^-3  [mm]"))
    story.append(body("onde Ra_eixo e Ra_cubo estao em micrometros. O valor Ra da sede pode ser importado automaticamente do Modulo 1."))

    story += h2("3.5 Forca de Encaixe")
    story.append(body("A forca necessaria para empurrar o eixo no cubo e:"))
    story.append(code("F = p x A x mu   onde   A = pi x d x w"))
    story.append(body(
        "O calculo e realizado para tres larguras (nominal, lower, upper) e duas condicoes de atrito (seco e lubrificado). "
        "Valores de referencia Stellantis: mu_seco = 0.40, mu_lubr = 0.21."
    ))

    story += h2("3.6 Modelo de Atrito de Stribeck")
    story.append(body("O coeficiente de atrito efetivo em montagem lubrificada e modelado por transicao exponencial:"))
    story.append(code("mu_ef(v) = mu_lubr + (mu_seco - mu_lubr) x exp(-v / v_ref)"))
    story.append(body("com v_ref = 15 mm/s. A curva de insercao F(x) exibe multiplas velocidades para comparacao."))

    story += h2("3.7 Outputs do Modulo")
    story += bullet([
        "Diametros maximos e minimos de eixo e furo.",
        "Interferencias radiais nominais e efetivas (com correcao de rugosidade).",
        "Pressoes de contato pmax e pmin pelas equacoes de Lame [MPa].",
        "Tabela completa de forcas (seco e lubrificado) para nominal, lower e upper [N e kgf].",
        "Grafico de barras comparativo das forcas por caso.",
        "Curva de insercao F(x) com modelo de Stribeck para multiplas velocidades.",
    ])
    story.append(PageBreak())

    # ── 4. MÓDULO 3 ────────────────────────────────────────────────────────────
    story += h1("4. Modulo 3 — Comparador de Curvas XML")
    story += h2("4.1 Finalidade")
    story.append(body(
        "Este modulo importa, visualiza e classifica curvas Forca x Curso de prensas de montagem exportadas em "
        "formato XML (maXYmos NC, Kistler/Sinpac). Suporta o controle de qualidade de press-fit em linha de producao."
    ))

    story += h2("4.2 Parsing do XML e Auto-Classificacao")
    story.append(body("O parser XML e robusto a variantes de nome de tag (X-ABSOLUTE-, X_-ABSOLUTE-, X-Absolute, X). A classificacao OK/NOK e determinada em tres niveis de prioridade:"))
    story += bullet([
        "<b>1. Campo &lt;Total_result&gt;:</b> lido diretamente do XML (valor 'OK' ou 'NOK').",
        "<b>2. Sufixo _OK / _NOK</b> no nome do arquivo.",
        "<b>3. Classificacao manual</b> pelo usuario atraves dos botoes na interface.",
    ])
    story.append(body("Metadados extraidos: Data, Hora, Numero do ciclo, Programa de medicao, Block_X, Block_Y."))

    story += h2("4.3 Filtros de Ponto e Ano")
    story.append(body(
        "O modulo extrai automaticamente o codigo MP (ex: MP-006) e o ano (ex: 2022) do nome do arquivo via "
        "expressao regular. Os filtros <b>Ponto:</b> e <b>Ano:</b> permitem exibir apenas curvas de um ponto de "
        "medicao ou periodo especifico, sem remover os demais arquivos carregados."
    ))

    story += h2("4.4 Janela de Aprovacao")
    story.append(body(
        "O usuario define um retangulo no espaco Curso x Forca (X_min, X_max, Y_min, Y_max). O grafico sobrepoe "
        "essa janela em amarelo sobre todas as curvas. A janela e apenas visual — a classificacao OK/NOK depende do XML ou da acao manual."
    ))

    story += h2("4.5 Visualizacao e Exportacao")
    story.append(body(
        "As curvas sao exibidas em dois paineis lado a lado (OK / NOK). O usuario pode limitar o numero de curvas "
        "visiveis, ativar/desativar legenda, renomear labels e salvar o grafico em PNG, PDF ou SVG."
    ))

    story += h2("4.6 Integracao com o Modulo 4")
    story.append(body(
        "As curvas OK carregadas no Modulo 3 podem ser importadas diretamente para o Modulo 4 pelo botao "
        "<b>'Importar OK do Comparador'</b>, sem necessidade de selecionar os arquivos novamente."
    ))
    story.append(PageBreak())

    # ── 5. MÓDULO 4 ────────────────────────────────────────────────────────────
    story += h1("5. Modulo 4 — Golden Curve Analyzer")
    story += h2("5.1 Conceito e Objetivo")
    story.append(body(
        "O modulo aprende o comportamento nominal esperado de um press-fit a partir de N curvas OK reais, gerando "
        "uma 'curva doura' (golden curve) estatisticamente robusta. Com ela e possivel:"
    ))
    story += bullet([
        "Obter a curva teorica media com banda de confianca calibrada nos dados reais.",
        "Ajustar uma equacao polinomial ou spline cubica exportavel.",
        "Detectar automaticamente anomalias em novas curvas via score estatistico.",
    ])

    story += h2("5.2 Importacao de Curvas — Formatos Suportados")
    fmt_data = [
        ["Formato","Extensao","Parser","Detalhes"],
        ["XML Prensa",".xml","_parse_xml()","Kistler/Sinpac. Robusto a variantes de nome de tag X. Curvas NOK sao automaticamente rejeitadas."],
        ["CSV",".csv","_parse_csv()","Detecta separador automaticamente (virgula, ponto-e-virgula, tab). Decimal: ponto ou virgula."],
    ]
    story.append(tbl(fmt_data, [22*mm, 20*mm, 24*mm, W - 66*mm]))

    story += h2("5.3 Filtros de Ponto e Ano")
    story.append(body(
        "Da mesma forma que no Modulo 3, filtros de Ponto (MP) e Ano permitem restringir quais curvas entram no "
        "calculo da Golden Curve, sem remover os arquivos carregados."
    ))

    story += h2("5.4 Algoritmo de Calculo — GoldenCurveAnalyzer")
    story += h2("5.4.1 Grade de Interpolacao")
    story.append(body(
        "A grade X comum e definida do maior X_min ao menor X_max entre todas as curvas (interseccao dos dominios). "
        "Cada curva e interpolada linearmente (scipy.interpolate.interp1d) nessa grade com N pontos (padrao 500)."
    ))

    story += h2("5.4.2 Estatisticas Ponto a Ponto")
    story.append(body("Sobre a matriz de curvas interpoladas (n_curvas x N_pontos):"))
    stat_data = [
        ["Grandeza","Calculo","Uso"],
        ["mean","Media aritmetica por coluna","Curva media — base da golden curve"],
        ["std","Desvio padrao por coluna","Largura da banda de incerteza"],
        ["median","Mediana por coluna","Robusto a outliers"],
        ["P05/P95","Percentis 5% e 95%","Banda de confianca ampla"],
        ["P25/P75","Percentis 25% e 75% (IQR)","Banda interquartil"],
        ["mean_smooth","Filtro gaussiano sobre mean","Curva suavizada (sigma configuravel)"],
    ]
    story.append(tbl(stat_data, [28*mm, 55*mm, W - 83*mm]))

    story += h2("5.4.3 Ajuste Polinomial")
    story.append(body(
        "Ajusta um polinomio de grau N (padrao 6, maximo 12) sobre a curva media suavizada por minimos quadrados "
        "(numpy.polyfit). O coeficiente de determinacao e calculado como:"
    ))
    story.append(code("R2 = 1 - Var(residuos) / Var(media_suavizada)"))
    story.append(body("Os coeficientes sao exportaveis em CSV com a tabela completa da golden curve."))

    story += h2("5.4.4 Ajuste Spline Cubico")
    story.append(body(
        "Ajusta um spline cubico de suavizacao (scipy.interpolate.UnivariateSpline, k=3) sobre a curva media "
        "suavizada. O parametro s (suavizacao) padronizado em N_pontos x 0.5."
    ))

    story += h2("5.5 Deteccao de Anomalia — Score Estatistico")
    story.append(body("Para uma curva nova (x_new, y_new), o algoritmo:"))
    story += bullet([
        "Interpola a curva nova na grade X da golden curve (apenas na interseccao de dominios).",
        "Calcula o z-score ponto a ponto: z(x) = |F_nova(x) - mean(x)| / std(x).",
        "Calcula a fracao de pontos acima do limiar sigma (padrao 3.0): outside_frac.",
        "Calcula o score de anomalia: score = clip( mean(z) / sigma_thr x 50, 0, 100 ).",
        "Emite veredito: OK se outside_frac &lt; 5% e score &lt; 40, caso contrario NOK.",
    ])
    anom_data = [
        ["Grandeza","Formula","Interpretacao"],
        ["z(x)","|F_nova - mean| / std","Desvios-padrao locais da curva nova"],
        ["outside_frac","mean(z > sigma_thr)","Fracao de pontos fora do limiar"],
        ["score","clip(mean(z)/thr * 50, 0, 100)","Score 0=perfeito, 100=muito anomalo"],
        ["Veredito OK","outside < 0.05 e score < 40","Dentro da faixa da golden curve"],
    ]
    story.append(tbl(anom_data, [28*mm, 60*mm, W - 88*mm]))

    story += h2("5.6 Sub-abas de Visualizacao")
    vis_data = [
        ["Sub-aba","Conteudo"],
        ["Golden Curve","Curvas OK individuais (cinza), bandas P5-P95 e IQR, curva media suavizada, ajuste polinomial e spline (opcionais)."],
        ["Anomalia","Golden curve de fundo + curvas de teste coloridas por veredito (verde=OK, vermelho=NOK). Score e veredito na legenda."],
        ["Estatisticas","Histograma de F_max por curva, desvio padrao ao longo do curso, residuos do ajuste polinomial com R2."],
    ]
    story.append(tbl(vis_data, [30*mm, W - 30*mm]))

    story += h2("5.7 Exportacao")
    story += bullet([
        "<b>Exportar coeficientes CSV:</b> coeficientes do polinomio + tabela golden curve completa.",
        "<b>Exportar PDF:</b> relatorio com sumario, tabela de coeficientes e graficos.",
        "<b>Salvar grafico PNG:</b> imagem da sub-aba Golden Curve em alta resolucao (200 dpi).",
    ])
    story.append(PageBreak())

    # ── 6. ARQUITETURA ─────────────────────────────────────────────────────────
    story += h1("6. Arquitetura de Software")
    story += h2("6.1 Tecnologias e Dependencias")
    dep_data = [
        ["Biblioteca","Versao min.","Uso principal"],
        ["Python","3.10","Linguagem base. Type hints com | requerem 3.10+."],
        ["tkinter","built-in","Interface grafica (GUI) com abas e canvas."],
        ["NumPy","1.24","Calculos numericos vetorizados."],
        ["Pillow (PIL)","9.0","Abertura e conversao de imagens para array."],
        ["SciPy","1.10","Filtro Sobel, interpolacao, spline, ajuste."],
        ["Matplotlib","3.7","Graficos embedded na GUI e geracao de figuras."],
        ["ReportLab","3.6","Geracao de relatorios PDF com tabelas e graficos."],
        ["xml.etree","built-in","Parsing de arquivos XML das prensas."],
        ["threading","built-in","Verificacao assincrona de versao no GitHub."],
    ]
    story.append(tbl(dep_data, [30*mm, 22*mm, W - 52*mm]))

    story += h2("6.2 Estrutura de Classes")
    cls_data = [
        ["Classe","Responsabilidade"],
        ["App","Janela principal. Inicializa abas e compartilha estado. Gerencia versao, trial e notificacao de update."],
        ["ScrollableFrame","Container com scroll vertical e suporte a roda do mouse (Windows, Linux, Mac)."],
        ["MultiImageSlot","Widget para selecao, preview e navegacao de multiplas imagens no Modulo 1."],
        ["AbaRugosidade","Modulo 1: analise de rugosidade por imagem."],
        ["AbaInterferencia","Modulo 2: calculo de interferencia press-fit (Lame)."],
        ["AbaXMLComparator","Modulo 3: importacao, filtragem e visualizacao de curvas XML."],
        ["AbaGoldenCurve","Modulo 4: golden curve, anomalia e estatisticas."],
        ["GoldenCurveAnalyzer","Logica estatistica pura (sem GUI) do Modulo 4."],
        ["_CurveEntry","Entidade de dados para uma curva XML (dados + metadados + classe)."],
        ["_UpdateBalloon","Balao estilo Windows 7 para notificacao de nova versao disponivel."],
        ["_ProgressModal","Barra de progresso modal para carregamento de mais de 100 curvas."],
    ]
    story.append(tbl(cls_data, [38*mm, W - 38*mm]))

    story += h2("6.3 Fluxo de Dados entre Modulos")
    story.append(body(
        "O estado <b>ra_sede_cal</b> calculado no Modulo 1 e armazenado na instancia App e pode alimentar o campo "
        "Ra do cubo no Modulo 2. As curvas OK do Modulo 3 sao acessadas pelo Modulo 4 via referencia "
        "<b>app._aba_xml.entries</b>, sem duplicacao de dados em memoria."
    ))

    story += h2("6.4 Versao, Trial e Atualizacao")
    story.append(body(
        "A versao e exibida no titulo da janela. Em modo desenvolvimento (pasta com .git), a versao e lida via "
        "<b>git describe --tags</b>. Em modo instalado, usa a constante __version__. "
        "O sistema de trial usa um arquivo base64-obfuscado em %APPDATA%\\BCI-Knuckle\\inst.dat. "
        "A verificacao de updates ocorre uma vez a cada 7 dias e e feita em thread separada "
        "(sem bloquear a GUI), consultando a GitHub Releases API."
    ))
    story.append(PageBreak())

    # ── 7. INSTRUÇÕES DE USO ───────────────────────────────────────────────────
    story += h1("7. Instrucoes de Uso Resumidas")
    story += h2("7.1 Modulo 1 — Analise de Rugosidade")
    story += bullet([
        "1. Aba 'Analise de Rugosidade' → clicar em '+ Adicionar fotos' no slot REFERENCIA → selecionar ≥10 imagens.",
        "2. Informar o Ra real da referencia em micrometros (ex: 1.6).",
        "3. Clicar em '+ Adicionar fotos' no slot PECA A MEDIR → selecionar ≥10 imagens.",
        "4. Clicar em ANALISAR. Resultados e graficos sao exibidos automaticamente.",
        "5. (Opcional) Exportar PDF do relatorio completo.",
    ])
    story += h2("7.2 Modulo 2 — Calculo de Interferencia")
    story += bullet([
        "1. Preencher parametros do EIXO: Young, Poisson, diametros, tolerancias, Ra.",
        "2. Preencher parametros do CUBO: idem.",
        "3. Informar largura de contato (nominal, lower, upper) e coeficientes de atrito.",
        "4. Clicar em '>> CALCULAR INTERFERENCIA'. Resultados e graficos exibidos.",
        "5. Ajustar velocidade de insercao e clicar 'Atualizar Curva' para re-plotar.",
        "6. (Opcional) Exportar PDF.",
    ])
    story += h2("7.3 Modulo 3 — Comparador de Curvas XML")
    story += bullet([
        "1. Clicar em 'Adicionar XML(s)' e selecionar arquivos da prensa.",
        "2. Usar filtros Ponto/Ano para segmentar a visualizacao.",
        "3. (Opcional) Reclassificar manualmente curvas com os botoes OK / NOK.",
        "4. Definir janela de aprovacao (X/Y min/max) e clicar 'Aplicar Janela'.",
        "5. Salvar grafico em PNG/PDF/SVG.",
    ])
    story += h2("7.4 Modulo 4 — Golden Curve")
    story += bullet([
        "1. Carregar curvas OK via 'Adicionar XML / CSV' OU 'Importar OK do Comparador'.",
        "2. (Opcional) Aplicar filtros Ponto/Ano para selecionar subconjunto.",
        "3. Ajustar parametros: grau do polinomio, sigma, suavizacao, N pontos.",
        "4. Clicar em 'GERAR GOLDEN CURVE'.",
        "5. Para deteccao de anomalia: carregar curva(s) de teste → 'Avaliar anomalia'.",
        "6. Exportar coeficientes CSV, PDF ou PNG conforme necessario.",
    ])
    story.append(PageBreak())

    # ── 8. REFERÊNCIAS ─────────────────────────────────────────────────────────
    story += h1("8. Referencias Normativas e Bibliograficas")
    story += bullet([
        "ISO 1302:2002 — Geometrical product specifications (GPS) — Indication of surface texture in technical product documentation.",
        "DIN 7190-1:2017 — Interference fits — Part 1: Calculation and design rules.",
        "Lame, G. (1852) — Lecons sur la theorie mathematique de l'elasticite des corps solides.",
        "Shigley, J.E.; Budynas, R.G. (2011) — Mechanical Engineering Design, 9a ed. McGraw-Hill.",
        "Stribeck, R. (1902) — Die wesentlichen Eigenschaften der Gleit- und Rollenlager. VDI.",
        "Gonzalez, R.C.; Woods, R.E. (2018) — Digital Image Processing, 4a ed. Pearson.",
        "AFNOR NF E 05-015 — Etat de surface — Rugosite.",
        "SciPy Documentation — scipy.interpolate.interp1d, UnivariateSpline, scipy.ndimage.sobel.",
    ])
    story.append(sp(4))
    story.append(hr(NAVY))
    story.append(Paragraph(
        f"BCI - KNUCKLE SOFTWARE  |  Documentacao Tecnica  |  "
        f"Author: Bruno Bernardinetti - Stellantis  |  {NOW}", FTR))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print(f"[OK] manual.pdf gerado em: {OUT}")


if __name__ == "__main__":
    build()
