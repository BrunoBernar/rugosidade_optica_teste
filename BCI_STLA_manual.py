"""
Gerador de manual PDF — BCI KNUCKLE SOFTWARE
Run: python gerar_manual.py
Output: manual.pdf (mesma pasta)
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 HRFlowable, Table, TableStyle)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUT      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual.pdf")
CONTATO  = "+55 32 9 9965-0392"

CYAN   = colors.HexColor("#00e5ff")
GOLD   = colors.HexColor("#ffc107")
PURPLE = colors.HexColor("#e040fb")
RED_C  = colors.HexColor("#f44336")
FG     = colors.HexColor("#c8d8e8")
FG_DIM = colors.HexColor("#6a8099")
BG2    = colors.HexColor("#111820")
BG3    = colors.HexColor("#1a1200")

ss = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, parent=ss["Normal"], **kw)

TITLE = S("T",  fontSize=22, textColor=CYAN,   spaceAfter=4,  alignment=TA_CENTER, fontName="Courier-Bold")
SUB   = S("Su", fontSize=10, textColor=FG_DIM, spaceAfter=14, alignment=TA_CENTER)
H1    = S("H1", fontSize=14, textColor=CYAN,   spaceBefore=16, spaceAfter=4,  fontName="Courier-Bold")
H2    = S("H2", fontSize=11, textColor=GOLD,   spaceBefore=10, spaceAfter=4,  fontName="Courier-Bold")
BODY  = S("Bo", fontSize=9,  textColor=FG,     spaceAfter=4,  leading=14)
STEP  = S("St", fontSize=9,  textColor=colors.white, spaceAfter=3, leftIndent=12, leading=13)
NOTE  = S("No", fontSize=8,  textColor=FG_DIM, spaceAfter=3,  leftIndent=12, fontName="Courier")
WARN  = S("Wa", fontSize=11, textColor=GOLD,   spaceAfter=6,  alignment=TA_CENTER, fontName="Courier-Bold")
CONT  = S("Co", fontSize=18, textColor=CYAN,   spaceAfter=4,  alignment=TA_CENTER, fontName="Courier-Bold")


def hr():
    return HRFlowable(width="100%", thickness=1, color=FG_DIM, spaceAfter=8, spaceBefore=4)


def trial_box():
    data = [
        [Paragraph("PERÍODO DE AVALIAÇÃO GRATUITA: 7 DIAS", WARN)],
        [Paragraph("Após o período de teste, entre em contato para adquirir sua licença:", BODY)],
        [Paragraph(CONTATO, CONT)],
        [Paragraph("WhatsApp / Telefone — Bruno Bernardinetti", NOTE)],
    ]
    t = Table(data, colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG3),
        ("BOX",        (0, 0), (-1, -1), 1.5, GOLD),
        ("ROWPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
    ]))
    return t


def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
    )
    story = []

    # Capa
    story += [
        Spacer(1, 18 * mm),
        Paragraph("BCI — KNUCKLE SOFTWARE", TITLE),
        Paragraph("Manual do Usuário", SUB),
        hr(),
        Paragraph("Versão 1.0.0  |  Bruno Bernardinetti — Stellantis Brasil", SUB),
        Spacer(1, 6 * mm),
        trial_box(),
        Spacer(1, 8 * mm),
    ]

    # Índice
    story += [
        Paragraph("MÓDULOS DISPONÍVEIS", H1),
        hr(),
        Paragraph("1. Análise de Rugosidade Óptica", BODY),
        Paragraph("2. Cálculo de Interferência — Equações de Lamé", BODY),
        Paragraph("3. Comparador de Curvas XML (Press-Fit)", BODY),
        Paragraph("4. Golden Curve Analyzer (Curva de Referência Estatística)", BODY),
        Spacer(1, 6 * mm),
    ]

    # Módulo 1
    story += [
        Paragraph("MÓDULO 1 — Análise de Rugosidade", H1), hr(),
        Paragraph(
            "Estima Ra (rugosidade média aritmética) de peças usinadas a partir de imagens "
            "de microscópio, usando uma peça de referência com Ra real conhecido.", BODY),
        Paragraph("Como usar:", H2),
        Paragraph("1. Carregue as imagens da peça de REFERÊNCIA (mínimo 10 imagens).", STEP),
        Paragraph("2. Informe o Ra real da referência em µm (ex: 0.8 / 1.6 / 3.2 / 6.3).", STEP),
        Paragraph("3. Carregue as imagens da peça a MEDIR — mesmas condições ópticas.", STEP),
        Paragraph("4. Clique em 'ANALISAR': Ra estimado ± desvio padrão + classificação AFNOR/ISO.", STEP),
        Paragraph("5. (Opcional) Exporte PDF com relatório completo.", STEP),
        Paragraph("Dica: Ctrl+clique para selecionar múltiplas fotos. Mais fotos = maior precisão.", NOTE),
        Spacer(1, 4 * mm),
    ]

    # Módulo 2
    story += [
        Paragraph("MÓDULO 2 — Cálculo de Interferência", H1), hr(),
        Paragraph(
            "Calcula pressão radial, tensões de von Mises e forças de press-fit/press-out "
            "para ajustes com interferência — Equações de Lamé para cilindros de parede grossa.", BODY),
        Paragraph("Parâmetros de entrada:", H2),
        Paragraph("• Eixo (Shaft): Young [GPa], Poisson, diâmetro nominal e interno, tolerâncias.", STEP),
        Paragraph("• Cubo (Hub/Knuckle): Young [GPa], Poisson, diâmetros e tolerâncias.", STEP),
        Paragraph("• Geometria: largura nominal, mínima e máxima do contato [mm].", STEP),
        Paragraph("• Atrito: mu seco (ref. Stellantis: 0.40) e mu lubrificado (0.21).", STEP),
        Paragraph("• Rugosidade: Ra eixo e Ra cubo [µm] — reduz interferência efetiva.", STEP),
        Paragraph("Saídas: interferência min/nom/max, pressão radial, von Mises, forças press-in/press-out.", NOTE),
        Spacer(1, 4 * mm),
    ]

    # Módulo 3
    story += [
        Paragraph("MÓDULO 3 — Comparador de Curvas XML", H1), hr(),
        Paragraph(
            "Visualiza e compara curvas Força × Curso exportadas de prensas maXYmos NC "
            "(Kistler/Sinpac), separando automaticamente OK e NOK.", BODY),
        Paragraph("Como usar:", H2),
        Paragraph("1. Clique em '➕ Adicionar XML(s)' e selecione os arquivos .xml da prensa.", STEP),
        Paragraph("2. A classificação OK/NOK é lida de <Total_result> ou inferida pelo nome do arquivo.", STEP),
        Paragraph("3. Use os filtros 'Ponto' e 'Ano' para visualizar subconjuntos específicos.", STEP),
        Paragraph("4. Clique em 'PLOTAR' para ver os dois painéis (OK | NOK) lado a lado.", STEP),
        Paragraph("5. Use 'Janela de Aprovação' para definir o envelope de aceitação visualmente.", STEP),
        Paragraph("6. Exporte como PNG, PDF ou SVG.", STEP),
        Spacer(1, 4 * mm),
    ]

    # Módulo 4
    story += [
        Paragraph("MÓDULO 4 — Golden Curve Analyzer", H1), hr(),
        Paragraph(
            "Gera curva de referência estatística ('golden curve') a partir de N curvas validadas, "
            "com bandas de confiança P5–P95 e detecção automática de anomalias.", BODY),
        Paragraph("Como usar:", H2),
        Paragraph("1. Carregue mínimo 3 curvas XML OK para construir a curva de referência.", STEP),
        Paragraph("2. Configure o grau do polinômio/spline e o sigma de anomalia.", STEP),
        Paragraph("3. Clique em 'GERAR GOLDEN CURVE'.", STEP),
        Paragraph("4. Na aba 'Anomalia', analise novas curvas contra a referência.", STEP),
        Paragraph("5. Score 0–100: quanto maior, mais anômala a curva.", STEP),
        Paragraph("Exporte coeficientes CSV e gráficos PDF/PNG.", NOTE),
        Spacer(1, 8 * mm),
    ]

    # Atualização
    story += [
        Paragraph("ATUALIZAÇÃO AUTOMÁTICA", H1), hr(),
        Paragraph(
            "O software verifica atualizações ao iniciar (requer internet). "
            "Pode ser desabilitado em Configurações (botão ⚙ no cabeçalho da janela).", BODY),
        Spacer(1, 6 * mm),
    ]

    # Contato final
    story += [
        Paragraph("SUPORTE E LICENCIAMENTO", H1), hr(),
        Paragraph("Para adquirir licença permanente ou obter suporte técnico:", BODY),
        Paragraph(CONTATO, CONT),
        Paragraph("WhatsApp / Telefone — Bruno Bernardinetti", NOTE),
        Spacer(1, 4 * mm),
        Paragraph("BCI - KNUCKLE SOFTWARE  |  Stellantis Brasil  |  v1.0.0", SUB),
    ]

    doc.build(story)
    print(f"[OK] manual.pdf gerado em: {OUT}")


if __name__ == "__main__":
    build()
