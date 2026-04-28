"""
BCI - KNUCKLE SOFTWARE
Author: Bruno Bernardinetti — https://github.com/BrunoBernar/rugosidade_optica_teste
================================================================================

╔══════════════════════════════════════════════════════════════════════════════╗
║                          FLUXO DE USO — MÓDULOS                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MÓDULO 1 — Análise de Rugosidade  (aba "Analise de Rugosidade")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Estimar o Ra de uma peça a partir de imagens de microscópio,
          usando uma peça de referência com Ra real conhecido.

  1. Carregue as imagens da peça de REFERÊNCIA
       • Clique em "Adicionar fotos" no slot REFERENCIA
       • Selecione pelo menos 10 imagens (mesmo aumento e iluminação)
  2. Informe o Ra real da referência
       • Digite o valor em µm no campo "Ra real da referência"
       • Ex: 0.8 / 1.6 / 3.2 / 6.3
  3. Carregue as imagens da peça a MEDIR
       • Clique em "Adicionar fotos" no slot PECA A MEDIR
       • Mesmas condições de iluminação e magnificação da referência
  4. Clique em "ANALISAR"
       • O software calcula o fator de calibração (Ra_real / Ra_proxy)
       • Aplica o fator às imagens da peça a medir
       • Exibe Ra estimado ± desvio padrão e a classificação AFNOR/ISO
  5. (Opcional) Clique em "Exportar PDF"
       • Gera relatório completo com imagens, tabelas e resultado

  Notas:
    • Use Ctrl+clique para selecionar múltiplas fotos de uma vez
    • Quanto mais fotos, mais preciso o resultado (mínimo 10 por peça)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MÓDULO 2 — Cálculo de Interferência  (aba "Calculo de Interferencia")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Calcular pressão radial, tensões e forças de press-fit para
          ajustes com interferência (Equações de Lamé — cilindros de parede
          grossa), considerando condições secas e lubrificadas.

  1. Preencha os dados do EIXO (Shaft)
       • Young Ei [GPa], Poisson vi
       • Diâmetro interno di [mm] (eixo vazado) e nominal d [mm]
       • Desvios de tolerância superior e inferior [mm]
  2. Preencha os dados do CUBO / KNUCKLE (Hub)
       • Young Eo [GPa], Poisson vo
       • Diâmetro externo do [mm] e nominal do furo [mm]
       • Desvios de tolerância superior e inferior [mm]
  3. Preencha a GEOMETRIA DA INTERFACE
       • Largura nominal, mínima e máxima do contato [mm]
  4. Preencha os COEFICIENTES DE ATRITO
       • mu seco (ref. Stellantis: 0.40) e mu lubrificado (0.21)
  5. Preencha a RUGOSIDADE DA SUPERFÍCIE
       • Ra eixo e Ra cubo [µm] — usados para reduzir a interferência efetiva
  6. Clique em ">> CALCULAR INTERFERENCIA"
       • Resultados exibidos: diâmetros efetivos, interferência min/nom/max,
         pressão radial, tensões de von Mises, forças de press-in e press-out
         em condições secas e lubrificadas
  7. (Opcional) Clique em "Exportar PDF" para salvar o relatório completo

  Notas:
    • Todos os campos têm valores padrão baseados no knuckle Stellantis
    • A rugosidade reduz a interferência efetiva: d_eff = d_nom − (Ra_eixo + Ra_cubo)×1e−3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MÓDULO 3 — Comparador de Curvas XML  (aba "Comparador de Curvas XML")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Visualizar e comparar curvas Força × Curso de arquivos XML da
          prensa maXYmos NC (Kistler / Sinpac), separando OK e NOK.

  1. Clique em "➕ Adicionar XML(s)"
       • Selecione um ou mais arquivos .xml exportados pela prensa
       • A classificação OK/NOK é lida automaticamente do campo
         <Total_result> do XML; se ausente, é inferida pelo nome do arquivo
  2. (Opcional) Use os filtros "Ponto:" e "Ano:"
       • Selecione um MP específico (ex: MP-006) para ver apenas aquele ponto
       • Selecione um ano para filtrar por data no nome do arquivo
       • "Todos" = sem filtro (exibe tudo)
  3. (Opcional) Ajuste a classificação manualmente
       • Selecione um arquivo na lista → clique "✔ OK" ou "✘ NOK"
  4. (Opcional) Renomeie o label de exibição
       • Selecione → "✏ Renomear label"
  5. Defina a JANELA DE APROVAÇÃO (retângulo amarelo no gráfico)
       • X min / X max: faixa de curso relevante [mm]
       • Y min / Y max: limites de força [kN]
  6. Clique em "📊 Plotar / Atualizar" ou em "↺ Aplicar Janela"
       • Painel esquerdo do gráfico = curvas OK
       • Painel direito do gráfico = curvas NOK
  7. Use "Max curvas" e "Mostrar legenda" para controlar a visualização
  8. (Opcional) Clique em "💾 Salvar gráfico" para exportar PNG/PDF/SVG

  Notas:
    • Arquivos já carregados não são duplicados
    • O módulo serve de fonte para o Módulo 4 (botão "Importar OK do Comparador")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MÓDULO 4 — Golden Curve Analyzer  (aba "Golden Curve")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objetivo: Gerar uma curva teórica de referência ("Golden Curve") a partir
          de N curvas OK reais, e detectar anomalias em novas curvas.
          Sub-abas: Golden Curve | Anomalia | Estatísticas

  ── ETAPA 1: Carregar curvas de referência (OK) ────────────────────────────
  1a. Clique em "➕ Adicionar XML / CSV"
        • Selecione arquivos .xml ou .csv com curvas OK
        • Arquivos classificados como NOK são automaticamente recusados
  1b. OU clique em "⬆ Importar OK do Comparador"
        • Importa diretamente as curvas OK já carregadas no Módulo 3
  1c. (Opcional) Use os filtros "Ponto:" e "Ano:"
        • Filtra quais curvas aparecem na lista e são usadas na análise
        • Útil para gerar a Golden Curve de um MP específico ou período

  ── ETAPA 2: Ajustar parâmetros ────────────────────────────────────────────
  2a. Grau do polinômio (padrão 6) — ajuste polinomial sobre a curva média
  2b. Sigma anomalia (padrão 3) — limiar de desvios-padrão para detecção
  2c. Suavização gaussiana (padrão 2) — sigma do filtro sobre a curva média
  2d. Pontos de interpolação (padrão 500) — resolução da grade X
  2e. Marque/desmarque as visualizações: curvas individuais, banda de
      confiança (P5–P95), ajuste polinomial, ajuste spline

  ── ETAPA 3: Gerar a Golden Curve ──────────────────────────────────────────
  3. Clique em "▶▶ GERAR GOLDEN CURVE"
       • Exibe na sub-aba "Golden Curve":
           – Curvas OK individuais (cinza)
           – Banda de confiança P5–P95 (área sombreada)
           – Curva média suavizada
           – Ajuste polinomial / spline (opcional)
       • Exibe na sub-aba "Estatísticas":
           – Distribuição de força máxima por curva
           – Distribuição de força mínima
           – Desvio padrão ao longo do curso

  ── ETAPA 4: Detectar anomalia em nova curva ───────────────────────────────
  4a. Clique em "➕ Carregar curva(s) para teste"
        • Selecione XML ou CSV da curva a avaliar (pode ser NOK)
  4b. Clique em "🔍 Avaliar anomalia"
        • A curva é interpolada na mesma grade X da Golden Curve
        • Score de anomalia calculado (0–100): quanto mais alto, mais suspeito
        • Veredito automático: OK (score < 40 e < 5% fora da banda)
                               NOK (caso contrário)
        • Sub-aba "Anomalia" exibe a curva sobreposta à banda de confiança,
          destacando os pontos fora do limite em vermelho
  4c. Clique em "🗑 Limpar teste" para remover as curvas de teste

  ── Exportação ─────────────────────────────────────────────────────────────
  5a. "💾 Exportar coeficientes CSV" — salva os coeficientes do polinômio
  5b. "📄 Exportar PDF" — relatório completo com gráficos e estatísticas
  5c. "🖼 Salvar gráfico PNG" — imagem do gráfico atual

  Notas:
    • Mínimo de 3 curvas OK para gerar a Golden Curve
    • O filtro de Ponto/Ano afeta diretamente quais curvas entram na análise

================================================================================
Dependencias:
    pip install pillow numpy matplotlib scipy reportlab
================================================================================
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.ndimage import sobel
import os, io, datetime, math, re, subprocess, threading, urllib.request, json, base64, base64

# ── Versão e update ───────────────────────────────────────────────────────────
__version__  = "v1.0.0"          # atualizar a cada release/tag no git
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_GH_API_LATEST = (
    "https://api.github.com/repos/BrunoBernar/rugosidade_optica_teste/releases/latest"
)

def _get_app_version() -> str:
    """Dev: lê `git describe --tags`. Instalado (sem .git): usa __version__."""
    if os.path.exists(os.path.join(_SCRIPT_DIR, ".git")):
        try:
            r = subprocess.run(
                ["git", "describe", "--tags", "--always", "--dirty"],
                capture_output=True, text=True, cwd=_SCRIPT_DIR, timeout=3
            )
            if r.returncode == 0:
                return r.stdout.strip()
        except Exception:
            pass
    return __version__

_IS_DEV = os.path.exists(os.path.join(_SCRIPT_DIR, ".git"))

# ── Trial / Configurações ─────────────────────────────────────────────────────
_APP_DATA_DIR = os.path.join(os.environ.get("APPDATA", _SCRIPT_DIR), "BCI-Knuckle")
_INST_FILE    = os.path.join(_APP_DATA_DIR, "inst.dat")
_SETT_FILE    = os.path.join(_APP_DATA_DIR, "settings.json")
_TRIAL_DAYS   = 7
_CONTATO      = "+55 32 9 9965-0392"


def _get_settings() -> dict:
    try:
        if os.path.exists(_SETT_FILE):
            with open(_SETT_FILE) as f:
                return json.loads(f.read())
    except Exception:
        pass
    return {}


def _save_settings(d: dict):
    os.makedirs(_APP_DATA_DIR, exist_ok=True)
    with open(_SETT_FILE, "w") as f:
        json.dump(d, f)


def _get_or_create_install_date() -> datetime.date:
    os.makedirs(_APP_DATA_DIR, exist_ok=True)
    if os.path.exists(_INST_FILE):
        try:
            raw = open(_INST_FILE).read().strip()
            iso = base64.b64decode(raw.encode()).decode()
            return datetime.date.fromisoformat(iso)
        except Exception:
            pass
    today = datetime.date.today()
    with open(_INST_FILE, "w") as f:
        f.write(base64.b64encode(today.isoformat().encode()).decode())
    return today


def _trial_days_left() -> int:
    if _IS_DEV:
        return _TRIAL_DAYS
    install = _get_or_create_install_date()
    elapsed = (datetime.date.today() - install).days
    return max(0, _TRIAL_DAYS - elapsed)


def _check_update_async(current_ver: str, callback):
    """Só roda quando instalado (sem .git) e auto_update ativo nas configurações."""
    if _IS_DEV:
        return
    if not _get_settings().get("auto_update", True):
        return
    def _worker():
        try:
            req = urllib.request.Request(
                _GH_API_LATEST, headers={"User-Agent": "BCI-KNUCKLE-SOFTWARE"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read())
            latest = data.get("tag_name", "").strip()
            if latest and latest != current_ver:
                callback(latest)
        except Exception:
            pass
    threading.Thread(target=_worker, daemon=True).start()
# ─────────────────────────────────────────────────────────────────────────────

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image as RLImage, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

MIN_FOTOS = 10

# ─────────────────────────────────────────────────────────────────────────────
# Paleta de cores
# ─────────────────────────────────────────────────────────────────────────────

BG        = "#0d1117"
BG2       = "#111820"
BG3       = "#050709"
ACCENT    = "#00e5ff"
GOLD      = "#ffc107"
PURPLE    = "#e040fb"
GREEN     = "#4caf50"
RED       = "#f44336"
ORANGE    = "#ff9800"
FG        = "#c8d8e8"
FG_DIM    = "#3a6070"
FG_WARN   = "#7a6040"
BG_WARN   = "#1a1000"
BORDER    = "#1a2a34"
FONT_MONO = ("Courier", 9)
FONT_SMALL= ("Courier", 7)

AFNOR_ISO = [
    ("N1","0.025"),("N2","0.05"),("N3","0.1"),("N4","0.2"),
    ("N5","0.4"),("N6","0.8"),("N7","1.6"),("N8","3.2"),
    ("N9","6.3"),("N10","12.5"),("N11","25.0"),("N12","50.0"),
]

# ─────────────────────────────────────────────────────────────────────────────
# ScrollableFrame — frame com rolagem vertical (mousewheel incluso)
# ─────────────────────────────────────────────────────────────────────────────

class ScrollableFrame(tk.Frame):
    """
    Container que adiciona scroll vertical ao conteudo.
    Use self.inner para colocar widgets dentro.
    """
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)

        # Canvas principal (area que vai rolar)
        self._canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self._canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar vertical
        sb = tk.Scrollbar(self, orient="vertical",
                          command=self._canvas.yview,
                          bg=BG2, troughcolor=BG3,
                          activebackground=ACCENT)
        sb.pack(side="right", fill="y")
        self._canvas.configure(yscrollcommand=sb.set)

        # Frame interno onde o conteudo fica
        self.inner = tk.Frame(self._canvas, bg=BG)
        self._win_id = self._canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")

        # Redimensiona a scrollregion quando o conteudo muda
        self.inner.bind("<Configure>", self._on_inner_configure)
        # Faz o frame interno ocupar toda a largura do canvas
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Scroll com roda do mouse (Windows + Linux)
        self._canvas.bind("<Enter>",  self._bind_mousewheel)
        self._canvas.bind("<Leave>",  self._unbind_mousewheel)
        self.inner.bind("<Enter>",    self._bind_mousewheel)
        self.inner.bind("<Leave>",    self._unbind_mousewheel)

    def _on_inner_configure(self, event):
        """Atualiza a area de scroll quando o conteudo interno muda de tamanho."""
        self._canvas.configure(
            scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Faz o frame interno ter sempre a mesma largura do canvas."""
        self._canvas.itemconfig(self._win_id, width=event.width)

    def _bind_mousewheel(self, event):
        """Ativa scroll com roda do mouse ao entrar na area."""
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel_win)
        self._canvas.bind_all("<Button-4>",   self._on_mousewheel_linux_up)
        self._canvas.bind_all("<Button-5>",   self._on_mousewheel_linux_down)

    def _unbind_mousewheel(self, event):
        """Desativa scroll com roda do mouse ao sair da area."""
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_mousewheel_win(self, event):
        """Scroll Windows/Mac."""
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_up(self, event):
        """Scroll Linux — rolar para cima."""
        self._canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        """Scroll Linux — rolar para baixo."""
        self._canvas.yview_scroll(1, "units")

    def scroll_top(self):
        """Volta o scroll para o topo."""
        self._canvas.yview_moveto(0)


# ─────────────────────────────────────────────────────────────────────────────
# Funcoes de analise de imagem
# ─────────────────────────────────────────────────────────────────────────────

def extrair_metricas(caminho):
    img  = Image.open(caminho).convert("L")
    img.thumbnail((512, 512))
    arr  = np.array(img, dtype=np.float64)
    media = arr.mean()
    ra    = float(np.mean(np.abs(arr - media)))
    rq    = float(np.sqrt(np.mean((arr - media) ** 2)))
    flat  = np.sort(arr.flatten())
    rz    = float(flat[-5:].mean() - flat[:5].mean())
    gx    = sobel(arr, axis=1); gy = sobel(arr, axis=0)
    grad_energy = float(np.sqrt(gx**2 + gy**2).mean())
    hist, _ = np.histogram(arr.ravel(), bins=256, range=(0,255))
    p = hist / hist.sum(); p = p[p > 0]
    entropia = float(-np.sum(p * np.log2(p)))
    return dict(ra=ra, rq=rq, rz=rz, grad_energy=grad_energy,
                entropia=entropia, media=media, arr=arr,
                nome=os.path.basename(caminho))

def agregar_metricas(lista):
    keys = ["ra","rq","rz","grad_energy","entropia"]
    agg  = {}
    for k in keys:
        vals = [r[k] for r in lista]
        agg[f"{k}_mean"] = float(np.mean(vals))
        agg[f"{k}_std"]  = float(np.std(vals))
        agg[f"{k}_vals"] = vals
    hists = []
    for r in lista:
        c, edges = np.histogram(r["arr"].ravel(), bins=64, range=(0,255))
        hists.append(c / c.max())
    agg["hist_mean"]  = np.mean(hists, axis=0)
    agg["hist_edges"] = edges
    agg["n"] = len(lista)
    return agg

def classificar(ra_um):
    if ra_um <  0.1: return "N1  - Espelho / super-acabamento",    "#00e5ff"
    if ra_um <  0.2: return "N2  - Retificacao fina",              "#00bcd4"
    if ra_um <  0.4: return "N3  - Retificacao",                   "#009688"
    if ra_um <  0.8: return "N4  - Retificacao grossa",            "#4caf50"
    if ra_um <  1.6: return "N5  - Torneamento / fresamento fino", "#8bc34a"
    if ra_um <  3.2: return "N6  - Torneamento convencional",      "#ffc107"
    if ra_um <  6.3: return "N7  - Fresamento grosso",             "#ff9800"
    if ra_um < 12.5: return "N8  - Desbaste",                      "#ff5722"
    if ra_um < 25.0: return "N9  - Fundicao / forjamento",         "#f44336"
    return                   "N10+ - Superficie bruta",             "#b71c1c"

# ─────────────────────────────────────────────────────────────────────────────
# Calculo de interferencia — Stellantis Knuckle (Lame)
# ─────────────────────────────────────────────────────────────────────────────

def lame_pressure(delta_mm, R_m, Eo_GPa, ro_m, vo, Ei_GPa, ri_m, vi):
    """Pressao de interferencia pela equacao de Lame [MPa]."""
    delta_m = delta_mm * 1e-3
    Eo_Pa   = Eo_GPa  * 1e9
    Ei_Pa   = Ei_GPa  * 1e9
    hub_term   = (1 / Eo_Pa) * ((ro_m**2 + R_m**2) / (ro_m**2 - R_m**2) + vo)
    shaft_term = (1 / Ei_Pa) * ((R_m**2 + ri_m**2) / (R_m**2 - ri_m**2) - vi)
    p_Pa = delta_m / (R_m * (hub_term + shaft_term))
    return p_Pa / 1e6

def engagement_force(pressure_MPa, area_mm2, mu):
    """Forca de encaixe F = p x A x mu. Retorna (N, kgf)."""
    F_N   = pressure_MPa * area_mm2 * mu
    F_kgf = F_N / 9.81
    return F_N, F_kgf

def mu_eff_speed(mu_dry, mu_lubed, v_mm_s, v_ref=15.0):
    """Coeficiente de atrito efetivo vs velocidade de insercao (Stribeck simplificado).
    v->0: retorna mu_dry (sem filme).  v>>v_ref: converge para mu_lubed (filme completo).
    v_ref=15 mm/s e valor tipico para montagem prensada lubrificada."""
    return mu_lubed + (mu_dry - mu_lubed) * math.exp(-max(v_mm_s, 0.0) / v_ref)

def insertion_curve(p_MPa, d_mm, w_mm, mu_dry, mu_lubed, v_mm_s,
                    n_pts=300, v_ref=15.0):
    """Curva F(x) durante insercao do eixo no cubo.
    Retorna (x_mm, F_dry_kN, F_lubed_kN, mu_eff)."""
    mu_v = mu_eff_speed(mu_dry, mu_lubed, v_mm_s, v_ref)
    x = np.linspace(0.0, w_mm, n_pts)
    A_x = math.pi * d_mm * x          # area de contato progressiva [mm2]
    F_dry   = p_MPa * A_x * mu_dry  / 1000.0
    F_lubed = p_MPa * A_x * mu_v    / 1000.0
    return x, F_dry, F_lubed, mu_v

# ─────────────────────────────────────────────────────────────────────────────
# Widgets auxiliares
# ─────────────────────────────────────────────────────────────────────────────

def frame_card(parent, title, **kw):
    outer = tk.Frame(parent, bg=BG, highlightbackground=BORDER,
                     highlightthickness=1, **kw)
    tk.Label(outer, text=title.upper(), bg=BG2, fg=FG_DIM,
             font=FONT_SMALL, padx=8, pady=4, anchor="w").pack(fill="x")
    inner = tk.Frame(outer, bg=BG, padx=8, pady=6)
    inner.pack(fill="both", expand=True)
    return outer, inner

def entry_row(parent, label, default="", width=10, cor=ACCENT):
    row = tk.Frame(parent, bg=BG); row.pack(fill="x", pady=2)
    tk.Label(row, text=label, bg=BG, fg=FG_DIM, font=FONT_SMALL,
             width=28, anchor="w").pack(side="left")
    var = tk.StringVar(value=str(default))
    tk.Entry(row, textvariable=var, bg=BG2, fg=cor,
             font=("Courier",10,"bold"), insertbackground=cor,
             relief="flat", highlightthickness=1,
             highlightbackground=BORDER, width=width).pack(side="left", ipady=3)
    return var

def result_row(parent, label, var_text, cor=FG):
    row = tk.Frame(parent, bg=BG); row.pack(fill="x", pady=1)
    tk.Label(row, text=label, bg=BG, fg=FG_DIM, font=FONT_SMALL,
             width=32, anchor="w").pack(side="left")
    lbl = tk.Label(row, textvariable=var_text, bg=BG, fg=cor,
                   font=("Courier",10,"bold"), anchor="w")
    lbl.pack(side="left")
    return lbl

# ─────────────────────────────────────────────────────────────────────────────
# Slot de multiplas imagens
# ─────────────────────────────────────────────────────────────────────────────

class MultiImageSlot(tk.Frame):
    def __init__(self, parent, label, cor, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._cor=cor; self._caminhos=[]; self._tk_imgs=[]; self._idx=0
        top=tk.Frame(self,bg=BG); top.pack(fill="x",pady=(0,4))
        tk.Label(top,text=label,bg=BG,fg=cor,
                 font=("Courier",10,"bold")).pack(side="left")
        tk.Button(top,text="Limpar",command=self._limpar,
                  bg=BG2,fg=FG_DIM,font=FONT_MONO,relief="flat",
                  padx=6,pady=3,cursor="hand2").pack(side="right",padx=(0,4))
        tk.Button(top,text="+ Adicionar fotos",command=self._adicionar,
                  bg=BG2,fg=cor,font=FONT_MONO,relief="flat",
                  padx=8,pady=3,cursor="hand2").pack(side="right")
        self._canvas=tk.Canvas(self,bg=BG3,highlightthickness=1,
                               highlightbackground=BORDER,width=270,height=165)
        self._canvas.pack(fill="x")
        self._canvas.create_text(135,82,text="Nenhuma imagem",
                                 fill="#2a3a44",font=FONT_MONO,tags="ph")
        nav=tk.Frame(self,bg=BG); nav.pack(fill="x",pady=(3,0))
        tk.Button(nav,text="<",command=self._prev,bg=BG2,fg=FG_DIM,
                  font=FONT_MONO,relief="flat",width=2,cursor="hand2").pack(side="left")
        self._lbl_nav=tk.Label(nav,text="0 / 0",bg=BG,fg=FG_DIM,font=("Courier",7))
        self._lbl_nav.pack(side="left",expand=True)
        tk.Button(nav,text=">",command=self._next,bg=BG2,fg=FG_DIM,
                  font=FONT_MONO,relief="flat",width=2,cursor="hand2").pack(side="right")
        self._lbl_status=tk.Label(self,text="",bg=BG,fg=FG_DIM,
                                  font=("Courier",8),anchor="w")
        self._lbl_status.pack(fill="x",pady=(2,0))
        self._atualizar_status()

    def _adicionar(self):
        paths=filedialog.askopenfilenames(
            title="Selecionar imagens (Ctrl+clique para multiplas)",
            filetypes=[("Imagens","*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),("Todos","*.*")])
        if not paths: return
        for p in paths:
            if p not in self._caminhos: self._caminhos.append(p)
        self._idx=len(self._caminhos)-1
        self._atualizar_preview(); self._atualizar_status()

    def _limpar(self):
        self._caminhos=[]; self._tk_imgs=[]; self._idx=0
        self._canvas.delete("all")
        self._canvas.create_text(135,82,text="Nenhuma imagem",fill="#2a3a44",font=FONT_MONO)
        self._atualizar_status()

    def _prev(self):
        if not self._caminhos: return
        self._idx=(self._idx-1)%len(self._caminhos); self._atualizar_preview()

    def _next(self):
        if not self._caminhos: return
        self._idx=(self._idx+1)%len(self._caminhos); self._atualizar_preview()

    def _atualizar_preview(self):
        if not self._caminhos: return
        path=self._caminhos[self._idx]
        img=Image.open(path); img.thumbnail((270,165))
        tk_img=ImageTk.PhotoImage(img)
        self._tk_imgs.append(tk_img)
        if len(self._tk_imgs)>20: self._tk_imgs=self._tk_imgs[-20:]
        self._canvas.delete("all")
        cw=self._canvas.winfo_width() or 270
        ch=self._canvas.winfo_height() or 165
        self._canvas.create_image(cw//2,ch//2,image=tk_img,anchor="center")
        self._lbl_nav.config(
            text=f"{self._idx+1} / {len(self._caminhos)}  |  {os.path.basename(path)}")

    def _atualizar_status(self):
        n=len(self._caminhos); falta=max(0,MIN_FOTOS-n)
        if n==0:    txt,cor=f"0 fotos  —  minimo {MIN_FOTOS}",FG_DIM
        elif falta: txt,cor=f"{n} foto(s)  —  faltam {falta}",GOLD
        else:       txt,cor=f"{n} fotos  —  OK",GREEN
        self._lbl_status.config(text=txt,fg=cor)
        if n>0: self._lbl_nav.config(
            text=f"{self._idx+1} / {n}  |  {os.path.basename(self._caminhos[self._idx])}")
        else:   self._lbl_nav.config(text="0 / 0")

    @property
    def caminhos(self): return self._caminhos

# ─────────────────────────────────────────────────────────────────────────────
# Aba 1 — Analise de Rugosidade
# ─────────────────────────────────────────────────────────────────────────────

class AbaRugosidade(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._app=app_ref
        self._last_agg_ref=None; self._last_agg_med=None
        self._last_raw_ref=None; self._last_raw_med=None
        self._last_fator=None;   self._last_ra_real=None
        self._build()

    def _build(self):
        # ── ScrollableFrame envolve TODO o conteudo da aba ───────────────────
        scroller = ScrollableFrame(self)
        scroller.pack(fill="both", expand=True)
        body = scroller.inner   # todos os widgets vao aqui dentro

        # Layout em duas colunas dentro do frame scrollavel
        cols = tk.Frame(body, bg=BG)
        cols.pack(fill="x", padx=20, pady=14)

        # ── Coluna esquerda ───────────────────────────────────────────────────
        left = tk.Frame(cols, bg=BG)
        left.pack(side="left", fill="both", padx=(0,16))

        self._slot_ref = MultiImageSlot(left, "REFERENCIA", GOLD)
        self._slot_ref.pack(fill="x", pady=(0,6))

        ra_f, ra_i = frame_card(left, "Ra real da referencia (um)")
        ra_f.pack(fill="x", pady=(0,8))
        row=tk.Frame(ra_i,bg=BG); row.pack(fill="x")
        self._entry_ra = tk.Entry(row, bg=BG2, fg=GOLD,
                                  font=("Courier",13,"bold"),
                                  insertbackground=GOLD, relief="flat",
                                  highlightthickness=1, highlightbackground=BORDER, width=10)
        self._entry_ra.pack(side="left", padx=(0,8), ipady=4)
        tk.Label(row, text="ex: 0.8 / 1.6 / 3.2 / 6.3",
                 bg=BG, fg=FG_DIM, font=("Helvetica",8)).pack(side="left")

        self._slot_med = MultiImageSlot(left, "PECA A MEDIR", ACCENT)
        self._slot_med.pack(fill="x", pady=(0,8))

        self._btn_analisar = tk.Button(left, text="ANALISAR",
                                       command=self._analisar,
                                       bg=BG2, fg=ACCENT,
                                       font=("Courier",11,"bold"),
                                       relief="flat", pady=8, cursor="hand2",
                                       activebackground=BG, activeforeground=ACCENT)
        self._btn_analisar.pack(fill="x", pady=(0,4))

        self._btn_pdf = tk.Button(left, text="Exportar PDF",
                                  command=self._exportar_pdf,
                                  bg=BG2, fg=PURPLE,
                                  font=("Courier",10,"bold"),
                                  relief="flat", pady=8, cursor="hand2",
                                  activebackground=BG, activeforeground=PURPLE,
                                  state="disabled")
        self._btn_pdf.pack(fill="x")

        tk.Label(left,
            text="Ctrl+clique para selecionar multiplas fotos.\n"
                 "Mesma iluminacao e magnificacao nas duas pecas.",
            bg=BG_WARN, fg=FG_WARN, font=("Helvetica",8),
            justify="left", padx=10, pady=8).pack(fill="x", pady=(8,0))

        # ── Coluna direita ────────────────────────────────────────────────────
        right = tk.Frame(cols, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        cf, ci = frame_card(right, "Fator de calibracao")
        cf.pack(fill="x", pady=(0,4))
        frow=tk.Frame(ci,bg=BG); frow.pack(fill="x")
        self._lbl_fator = tk.Label(frow, text="—", bg=BG, fg=GOLD,
                                   font=("Courier",10,"bold"))
        self._lbl_fator.pack(side="left")
        tk.Label(frow, text="  um/u.i.  (Ra_real / Ra_proxy medio da referencia)",
                 bg=BG, fg=FG_DIM, font=("Helvetica",7)).pack(side="left")

        tab=tk.Frame(right,bg=BG); tab.pack(fill="x",pady=(0,4))
        tab.columnconfigure(0,weight=1); tab.columnconfigure(1,weight=1)
        tk.Label(tab,text="REFERENCIA (media +- dp)",bg=BG2,fg=GOLD,
                 font=FONT_SMALL,pady=2).grid(row=0,column=0,sticky="ew",padx=(0,4))
        tk.Label(tab,text="PECA MEDIDA (media +- dp)",bg=BG2,fg=ACCENT,
                 font=FONT_SMALL,pady=2).grid(row=0,column=1,sticky="ew")

        metricas_def=[("Ra  [um]","ra"),("Rq  [um]","rq"),("Rz  [um]","rz"),
                      ("Grad. energia","grad_energy"),("Entropia [bits]","entropia")]
        self._cells={}
        for ri,(label,key) in enumerate(metricas_def):
            for ci2,sn in enumerate(("ref","med")):
                cor=GOLD if sn=="ref" else ACCENT
                cell=tk.Frame(tab,bg=BG,highlightbackground=BORDER,highlightthickness=1)
                cell.grid(row=ri+1,column=ci2,sticky="ew",
                          padx=(0,4) if ci2==0 else 0,pady=1)
                tk.Label(cell,text=label,bg=BG2,fg=FG_DIM,
                         font=FONT_SMALL,padx=4,pady=1,anchor="w").pack(fill="x")
                lv=tk.Label(cell,text="—",bg=BG,fg=cor,
                            font=("Courier",10,"bold"),padx=4,pady=1,anchor="w")
                lv.pack(fill="x")
                ld=tk.Label(cell,text="",bg=BG,fg=FG_DIM,
                            font=("Courier",6),padx=4,pady=0,anchor="w")
                ld.pack(fill="x")
                self._cells[(sn,key)]=(lv,ld)

        cls_f,cls_i=frame_card(right,"Classificacao ISO estimada — peca medida")
        cls_f.pack(fill="x",pady=(0,4))
        self._lbl_classe=tk.Label(cls_i,text="—",bg=BG,fg=FG,
                                  font=("Courier",9,"bold"),anchor="w")
        self._lbl_classe.pack(fill="x")
        self._lbl_intervalo=tk.Label(cls_i,text="",bg=BG,fg=FG_DIM,
                                     font=("Courier",7),anchor="w")
        self._lbl_intervalo.pack(fill="x")

        # Graficos — tamanho FIXO para nao amassar ao rolar
        graf_frame = tk.Frame(body, bg=BG)
        graf_frame.pack(fill="x", padx=20, pady=(0,20))

        self._fig, axes = plt.subplots(1, 3, figsize=(13, 4), facecolor=BG)
        self._fig.tight_layout(pad=2.5)
        self._ax_hist, self._ax_box, self._ax_prof = axes
        for ax in axes:
            ax.set_facecolor(BG3)
            for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
            ax.tick_params(colors=FG_DIM, labelsize=7)

        # O canvas matplotlib fica com altura fixa — NAO expande com a janela
        self._canvas_mpl = FigureCanvasTkAgg(self._fig, master=graf_frame)
        widget = self._canvas_mpl.get_tk_widget()
        widget.pack(fill="x")          # fill horizontal mas altura fixa pelo figsize
        self._placeholder_graficos()

    # ── Analise ───────────────────────────────────────────────────────────────

    def _analisar(self):
        if len(self._slot_ref.caminhos)<MIN_FOTOS:
            messagebox.showwarning("Atencao",
                f"Referencia: {len(self._slot_ref.caminhos)} foto(s). Minimo: {MIN_FOTOS}."); return
        if len(self._slot_med.caminhos)<MIN_FOTOS:
            messagebox.showwarning("Atencao",
                f"Peca a medir: {len(self._slot_med.caminhos)} foto(s). Minimo: {MIN_FOTOS}."); return
        ra_str=self._entry_ra.get().strip().replace(",",".")
        try:
            ra_real=float(ra_str)
            if ra_real<=0: raise ValueError
        except ValueError:
            messagebox.showwarning("Atencao","Informe o Ra real da referencia (ex: 1.6)."); return

        self._btn_analisar.config(state="disabled",text="Processando...")
        self._btn_pdf.config(state="disabled"); self.update()
        try:
            raw_ref=[extrair_metricas(p) for p in self._slot_ref.caminhos]
            raw_med=[extrair_metricas(p) for p in self._slot_med.caminhos]
            agg_ref=agregar_metricas(raw_ref); agg_med=agregar_metricas(raw_med)
            fator=ra_real/agg_ref["ra_mean"]
            for key in ("ra","rq","rz"):
                agg_ref[f"{key}_cal"]     = agg_ref[f"{key}_mean"]*fator
                agg_ref[f"{key}_cal_std"] = agg_ref[f"{key}_std"] *fator
                agg_med[f"{key}_cal"]     = agg_med[f"{key}_mean"]*fator
                agg_med[f"{key}_cal_std"] = agg_med[f"{key}_std"] *fator
            self._last_agg_ref=agg_ref; self._last_agg_med=agg_med
            self._last_raw_ref=raw_ref; self._last_raw_med=raw_med
            self._last_fator=fator;     self._last_ra_real=ra_real
            self._app.ra_sede_cal=agg_med["ra_cal"]
            self._mostrar_resultados(agg_ref,agg_med,fator,raw_ref,raw_med)
            self._btn_pdf.config(state="normal")
        except Exception as e:
            messagebox.showerror("Erro",str(e))
        finally:
            self._btn_analisar.config(state="normal",text="ANALISAR")

    def _mostrar_resultados(self,ref,med,fator,raw_ref,raw_med):
        self._lbl_fator.config(text=f"{fator:.5f}")
        for sn,agg in (("ref",ref),("med",med)):
            for key in ("ra","rq","rz"):
                v,std=agg[f"{key}_cal"],agg[f"{key}_cal_std"]
                self._cells[(sn,key)][0].config(text=f"{v:.3f}")
                self._cells[(sn,key)][1].config(text=f"+- {std:.3f}  (dp n={agg['n']})")
            for key in ("grad_energy","entropia"):
                v,std=agg[f"{key}_mean"],agg[f"{key}_std"]
                self._cells[(sn,key)][0].config(text=f"{v:.2f}")
                self._cells[(sn,key)][1].config(text=f"+- {std:.2f}  (dp n={agg['n']})")
        ra_med=med["ra_cal"]; ra_std=med["ra_cal_std"]
        cls_txt,cls_cor=classificar(ra_med)
        self._lbl_classe.config(text=f"Ra = {ra_med:.3f} um   ->   {cls_txt}",fg=cls_cor)
        self._lbl_intervalo.config(
            text=f"Intervalo (1 dp):  {max(0,ra_med-ra_std):.3f}  a  {ra_med+ra_std:.3f} um")
        self._plotar_graficos(ref,med,raw_ref,raw_med)

    def _plotar_graficos(self,ref,med,raw_ref,raw_med):
        ra_r=[r["ra"]*(ref["ra_cal"]/ref["ra_mean"]) for r in raw_ref]
        ra_m=[r["ra"]*(med["ra_cal"]/med["ra_mean"]) for r in raw_med]

        ax=self._ax_hist; ax.clear(); ax.set_facecolor(BG3)
        edges=ref["hist_edges"]
        ax.plot(edges[:-1],ref["hist_mean"],color=GOLD, lw=0.9,alpha=0.85,label=f"Ref (n={ref['n']})")
        ax.plot(edges[:-1],med["hist_mean"],color=ACCENT,lw=0.9,alpha=0.85,label=f"Med (n={med['n']})")
        ax.legend(fontsize=7,facecolor=BG2,edgecolor=BORDER,labelcolor=FG)
        ax.set_title("Histograma medio",color=FG_DIM,fontsize=8,pad=3)
        ax.set_xlabel("Nivel de cinza",color=FG_DIM,fontsize=7)
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM,labelsize=7)

        ax2=self._ax_box; ax2.clear(); ax2.set_facecolor(BG3)
        bp=ax2.boxplot([ra_r,ra_m],patch_artist=True,
                       medianprops=dict(color=BG,lw=1.5),
                       whiskerprops=dict(color=FG_DIM),capprops=dict(color=FG_DIM),
                       flierprops=dict(marker="o",color=FG_DIM,markerfacecolor=FG_DIM,markersize=3))
        bp["boxes"][0].set_facecolor(GOLD+"55");  bp["boxes"][0].set_edgecolor(GOLD)
        bp["boxes"][1].set_facecolor(ACCENT+"55"); bp["boxes"][1].set_edgecolor(ACCENT)
        ax2.set_xticks([1,2]); ax2.set_xticklabels(["Ref","Medida"],color=FG_DIM,fontsize=7)
        ax2.set_title("Ra por imagem [um]",color=FG_DIM,fontsize=8,pad=3)
        for sp in ax2.spines.values(): sp.set_edgecolor(BORDER)
        ax2.tick_params(colors=FG_DIM,labelsize=7)

        ax3=self._ax_prof; ax3.clear(); ax3.set_facecolor(BG3)
        ax3.plot(ra_r,"o-",color=GOLD, ms=4,lw=1.0,alpha=0.85,label="Ref")
        ax3.plot(ra_m,"o-",color=ACCENT,ms=4,lw=1.0,alpha=0.85,label="Medida")
        ax3.axhline(np.mean(ra_r),color=GOLD, lw=0.7,ls="--",alpha=0.6)
        ax3.axhline(np.mean(ra_m),color=ACCENT,lw=0.7,ls="--",alpha=0.6)
        ax3.legend(fontsize=7,facecolor=BG2,edgecolor=BORDER,labelcolor=FG)
        ax3.set_title("Ra por foto [um]",color=FG_DIM,fontsize=8,pad=3)
        ax3.set_xlabel("Foto #",color=FG_DIM,fontsize=7)
        for sp in ax3.spines.values(): sp.set_edgecolor(BORDER)
        ax3.tick_params(colors=FG_DIM,labelsize=7)

        self._fig.tight_layout(pad=2.0); self._canvas_mpl.draw()

    def _placeholder_graficos(self):
        for ax in [self._ax_hist,self._ax_box,self._ax_prof]:
            ax.clear(); ax.set_facecolor(BG3)
            ax.text(0.5,0.5,"sem dados",transform=ax.transAxes,
                    ha="center",va="center",color="#2a3a44",fontsize=9)
            for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
            ax.tick_params(colors=FG_DIM,labelsize=7)
        self._canvas_mpl.draw()

    def _exportar_pdf(self):
        if self._last_agg_med is None:
            messagebox.showwarning("Atencao","Realize a analise antes de exportar."); return
        path=filedialog.asksaveasfilename(title="Salvar relatorio PDF",
            defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not path: return
        try:
            self._gerar_pdf(path)
            messagebox.showinfo("Sucesso",f"PDF salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF",str(e))

    def _gerar_pdf(self,path):
        ref=self._last_agg_ref; med=self._last_agg_med
        raw_r=self._last_raw_ref; raw_m=self._last_raw_med
        fator=self._last_fator; ra_real=self._last_ra_real
        fig_pdf,axes=plt.subplots(1,3,figsize=(11,3),facecolor="white")
        fig_pdf.tight_layout(pad=2.5)
        edges=ref["hist_edges"]
        ra_r=[r["ra"]*(ref["ra_cal"]/ref["ra_mean"]) for r in raw_r]
        ra_m=[r["ra"]*(med["ra_cal"]/med["ra_mean"]) for r in raw_m]
        axes[0].plot(edges[:-1],ref["hist_mean"],color="#c8860a",lw=1.2,label=f"Ref(n={ref['n']})")
        axes[0].plot(edges[:-1],med["hist_mean"],color="#0077aa",lw=1.2,label=f"Med(n={med['n']})")
        axes[0].legend(fontsize=7); axes[0].set_title("Histograma",fontsize=8); axes[0].tick_params(labelsize=7)
        bp=axes[1].boxplot([ra_r,ra_m],patch_artist=True,medianprops=dict(color="white",lw=1.5))
        bp["boxes"][0].set_facecolor("#ffc10755"); bp["boxes"][0].set_edgecolor("#c8860a")
        bp["boxes"][1].set_facecolor("#00e5ff55"); bp["boxes"][1].set_edgecolor("#0077aa")
        axes[1].set_xticks([1,2]); axes[1].set_xticklabels(["Ref","Med"],fontsize=7)
        axes[1].set_title("Ra por imagem [um]",fontsize=8); axes[1].tick_params(labelsize=7)
        axes[2].plot(ra_r,"o-",color="#c8860a",ms=4,lw=1,label="Ref")
        axes[2].plot(ra_m,"o-",color="#0077aa", ms=4,lw=1,label="Med")
        axes[2].axhline(np.mean(ra_r),color="#c8860a",lw=0.8,ls="--",alpha=0.7)
        axes[2].axhline(np.mean(ra_m),color="#0077aa", lw=0.8,ls="--",alpha=0.7)
        axes[2].legend(fontsize=7); axes[2].set_title("Ra por foto [um]",fontsize=8); axes[2].tick_params(labelsize=7)
        buf=io.BytesIO(); fig_pdf.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor="white")
        buf.seek(0); plt.close(fig_pdf)
        doc=SimpleDocTemplate(path,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=18*mm,bottomMargin=18*mm)
        W=A4[0]-40*mm; now=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        s_title =ParagraphStyle("t",fontSize=14,fontName="Helvetica-Bold",textColor=colors.HexColor("#003366"),spaceAfter=2)
        s_author=ParagraphStyle("a",fontSize=9, fontName="Helvetica-Bold",textColor=colors.HexColor("#003366"),spaceAfter=1)
        s_note  =ParagraphStyle("n",fontSize=7.5,fontName="Helvetica-Oblique",textColor=colors.HexColor("#666666"),spaceAfter=4)
        s_section=ParagraphStyle("s",fontSize=10,fontName="Helvetica-Bold",textColor=colors.HexColor("#003366"),spaceBefore=10,spaceAfter=4)
        s_body  =ParagraphStyle("b",fontSize=8.5,fontName="Helvetica",textColor=colors.black,spaceAfter=3)
        s_warn  =ParagraphStyle("w",fontSize=7.5,fontName="Helvetica-Oblique",textColor=colors.HexColor("#7a5000"),
                                backColor=colors.HexColor("#fff8e1"),spaceAfter=4,leftIndent=6,rightIndent=6)
        story=[]
        ht=Table([[Paragraph("RELATORIO DE ESTIMATIVA DE RUGOSIDADE",s_title),
                   Paragraph(f"Gerado em: {now}",ParagraphStyle("rt",fontSize=8,fontName="Helvetica",
                   textColor=colors.HexColor("#555555"),alignment=TA_RIGHT))]],colWidths=[W*0.65,W*0.35])
        ht.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(ht)
        story.append(Paragraph("Author: Bruno Bernardinetti - Stellantis",s_author))
        story.append(HRFlowable(width="100%",thickness=2,color=colors.HexColor("#003366"),spaceAfter=4))
        story.append(Paragraph("Nota: Se for usar notacao AFNOR (Francesa), utilize a correlacao com a ISO 1302 conforme tabela ao final.",s_note))
        story.append(Paragraph(f"Metodo: Analise de textura por imagem  |  Min. {MIN_FOTOS} imagens/caso  |  Calibracao por referencia",s_body))
        story.append(Paragraph("Parametros da Analise",s_section))
        pd2=Table([["Parametro","Referencia","Peca Medida"],
                   ["Numero de imagens",str(ref["n"]),str(med["n"])],
                   ["Ra real informado (um)",f"{ra_real:.3f}","—"],
                   ["Fator de calibracao (um/u.i.)",f"{fator:.5f}",f"{fator:.5f}"]],
                  colWidths=[W*0.40,W*0.30,W*0.30])
        pd2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#003366")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f4f8"),colors.white]),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cccccc")),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(pd2)
        story.append(Paragraph("Resultados das Metricas",s_section))
        mh=["Metrica","Ref\nMedia","Ref\n+- DP","Med\nMedia","Med\n+- DP"]; mr=[mh]
        for lbl,key,cal in [("Ra [um]","ra",True),("Rq [um]","rq",True),("Rz [um]","rz",True),
                             ("Grad. Energia","grad_energy",False),("Entropia [bits]","entropia",False)]:
            if cal: vr,sr,vm,sm=ref[f"{key}_cal"],ref[f"{key}_cal_std"],med[f"{key}_cal"],med[f"{key}_cal_std"]; fmt=".3f"
            else:   vr,sr,vm,sm=ref[f"{key}_mean"],ref[f"{key}_std"],med[f"{key}_mean"],med[f"{key}_std"]; fmt=".2f"
            mr.append([lbl,f"{vr:{fmt}}",f"+- {sr:{fmt}}",f"{vm:{fmt}}",f"+- {sm:{fmt}}"])
        mt=Table(mr,colWidths=[W*0.25,W*0.18,W*0.18,W*0.18,W*0.21])
        mt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#003366")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f4f8"),colors.white]),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cccccc")),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("BACKGROUND",(3,1),(4,1),colors.HexColor("#e3f2fd")),
            ("FONTNAME",(3,1),(3,1),"Helvetica-Bold")]))
        story.append(mt)
        story.append(Paragraph("Classificacao ISO 1302",s_section))
        ra_mv=med["ra_cal"]; ra_ms=med["ra_cal_std"]; cls_txt,_=classificar(ra_mv)
        story.append(Paragraph(f"Ra estimado: <b>{ra_mv:.3f} um  +/-  {ra_ms:.3f} um</b>",s_body))
        story.append(Paragraph(f"Classificacao: <b>{cls_txt}</b>",s_body))
        story.append(Paragraph(f"Intervalo (1 DP): {max(0,ra_mv-ra_ms):.3f} um a {ra_mv+ra_ms:.3f} um",s_body))
        story.append(Spacer(1,4))
        story.append(Paragraph("Aviso: Estimativa baseada em analise de imagem. Para resultados absolutos use rugosimetro calibrado.",s_warn))
        story.append(Paragraph("Graficos de Analise",s_section))
        story.append(RLImage(buf,width=W,height=W*3/11))
        story.append(Paragraph("Correlacao AFNOR x ISO 1302",s_section))
        ar=[["Classe AFNOR / ISO","Ra max [um]","Processo tipico"]]
        procs=["Superacabamento","Retif. fina","Retificacao","Retif. grossa",
               "Torn./fres. fino","Torn. convencional","Fresamento grosso","Desbaste",
               "Fund./forj. fino","Fundicao bruta","Corte a chama","Sup. bruta"]
        for (cn,rv),pr in zip(AFNOR_ISO,procs): ar.append([cn,rv,pr])
        at=Table(ar,colWidths=[W*0.25,W*0.20,W*0.55])
        at.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#003366")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),("ALIGN",(1,0),(1,-1),"CENTER"),("ALIGN",(0,0),(0,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f4f8"),colors.white]),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cccccc")),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
        story.append(at)
        story.append(Spacer(1,8))
        story.append(HRFlowable(width="100%",thickness=0.5,color=colors.HexColor("#cccccc"),spaceAfter=4))
        story.append(Paragraph(
            f"Gerado pelo Estimador de Rugosidade  |  Author: Bruno Bernardinetti - Stellantis  |  {now}",
            ParagraphStyle("footer",fontSize=7,fontName="Helvetica",
                           textColor=colors.HexColor("#888888"),alignment=TA_CENTER)))
        doc.build(story)



# ─────────────────────────────────────────────────────────────────────────────
# Presets de material e atrito
# ─────────────────────────────────────────────────────────────────────────────



# ─────────────────────────────────────────────────────────────────────────────
# Aba 2 — Calculo de Interferencia (Stellantis Knuckle)
# ─────────────────────────────────────────────────────────────────────────────

class AbaInterferencia(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._app = app_ref
        self._resultado = None
        self._build()

    def _build(self):
        scroller = ScrollableFrame(self)
        scroller.pack(fill="both", expand=True)
        W = scroller.inner

        PAD = dict(padx=20, pady=6)

        # ── Cabecalho ─────────────────────────────────────────────────────────
        hdr = tk.Frame(W, bg=BG2)
        hdr.pack(fill="x", padx=0, pady=(0,8))
        tk.Label(hdr, text="  KNUCKLE INTERFERENCE CALCULATOR — Stellantis",
                 bg=BG2, fg=PURPLE, font=("Courier",10,"bold"),
                 anchor="w", pady=8).pack(side="left")
        tk.Label(hdr, text="Equacoes de Lame  |  Cilindros de parede grossa  ",
                 bg=BG2, fg=FG_DIM, font=("Helvetica",8),
                 anchor="e").pack(side="right")

        # ── INPUTS — 3 colunas: Eixo | Cubo | Geometria+Atrito ──────────────────
        sec_in = tk.Frame(W, bg=BG)
        sec_in.pack(fill="x", **PAD)

        col_a = tk.Frame(sec_in, bg=BG)
        col_a.pack(side="left", fill="both", expand=True, padx=(0,10))
        col_b = tk.Frame(sec_in, bg=BG)
        col_b.pack(side="left", fill="both", expand=True, padx=(0,10))
        col_c = tk.Frame(sec_in, bg=BG)
        col_c.pack(side="left", fill="both", expand=True)

        # ── COL A: Eixo (Shaft) ─────────────────────────────────────────────
        ef, ei_f = frame_card(col_a, "Eixo (Shaft)")
        ef.pack(fill="x", pady=(0,6))
        tk.Label(ei_f, text="Parte INTERNA — eixo vazado",
                 bg=BG3, fg=GOLD, font=("Courier",8,"bold"),
                 anchor="w", padx=6, pady=4).pack(fill="x", pady=(0,4))
        self._Ei  = entry_row(ei_f, "Young Ei        [GPa]",  "210.0",  cor=GOLD)
        self._vi  = entry_row(ei_f, "Poisson vi",              "0.27",   cor=GOLD)
        self._di  = entry_row(ei_f, "Diam. interno di [mm]",  "40.291", cor=GOLD)
        self._d   = entry_row(ei_f, "Diam. nominal d  [mm]",  "78.0",   cor=GOLD)
        tk.Label(ei_f, text="Tolerancias do eixo:", bg=BG, fg=FG_DIM,
                 font=("Helvetica",8)).pack(anchor="w", pady=(6,0))
        self._tol_sh_up = entry_row(ei_f, "Desvio superior [mm]", "+0.040", cor=GOLD)
        self._tol_sh_lo = entry_row(ei_f, "Desvio inferior [mm]", "-0.013", cor=GOLD)
        self._lbl_shaft = tk.Label(ei_f, text="", bg=BG2, fg=GOLD,
                                   font=("Courier",8), anchor="w", padx=6, pady=3)
        self._lbl_shaft.pack(fill="x", pady=(3,0))

        # ── COL B: Cubo (Hub) ─────────────────────────────────────────────────
        hf, hi_f = frame_card(col_b, "Cubo (Hub / Knuckle)")
        hf.pack(fill="x", pady=(0,6))
        tk.Label(hi_f, text="Parte EXTERNA — cubo / knuckle",
                 bg=BG3, fg=ACCENT, font=("Courier",8,"bold"),
                 anchor="w", padx=6, pady=4).pack(fill="x", pady=(0,4))
        self._Eo  = entry_row(hi_f, "Young Eo        [GPa]",  "156.96", cor=ACCENT)
        self._vo  = entry_row(hi_f, "Poisson vo",              "0.27",   cor=ACCENT)
        self._do  = entry_row(hi_f, "Diam. externo do [mm]",  "81.65",  cor=ACCENT)
        self._dh  = entry_row(hi_f, "Diam. nominal furo [mm]","78.0",   cor=ACCENT)
        tk.Label(hi_f, text="Tolerancias do furo:", bg=BG, fg=FG_DIM,
                 font=("Helvetica",8)).pack(anchor="w", pady=(6,0))
        self._tol_ho_up = entry_row(hi_f, "Desvio superior [mm]", "-0.083", cor=ACCENT)
        self._tol_ho_lo = entry_row(hi_f, "Desvio inferior [mm]", "-0.113", cor=ACCENT)
        self._lbl_hub = tk.Label(hi_f, text="", bg=BG2, fg=ACCENT,
                                 font=("Courier",8), anchor="w", padx=6, pady=3)
        self._lbl_hub.pack(fill="x", pady=(3,0))

        # ── COL C: Geometria + Atrito ─────────────────────────────────────────
        gf2, gi_f = frame_card(col_c, "Geometria da interface")
        gf2.pack(fill="x", pady=(0,6))
        self._w_nom = entry_row(gi_f, "Largura nominal [mm]", "37.88", cor=FG)
        self._w_lo  = entry_row(gi_f, "Largura minima  [mm]", "33.80", cor=FG)
        self._w_up  = entry_row(gi_f, "Largura maxima  [mm]", "38.00", cor=FG)

        af, ai_f = frame_card(col_c, "Coeficientes de atrito")
        af.pack(fill="x", pady=(0,6))
        tk.Label(ai_f, text="Calculados simultaneamente (seco e lubrificado):",
                 bg=BG, fg=FG_DIM, font=("Helvetica",7)).pack(anchor="w", pady=(0,4))
        self._mu_dry   = entry_row(ai_f, "mu seco   (dry)",   "0.40", cor=RED)
        self._mu_lubed = entry_row(ai_f, "mu lubr.  (lubed)", "0.21", cor=GREEN)
        tk.Label(ai_f, text="Ref. Stellantis: seco=0.40  lubr.=0.21",
                 bg=BG, fg=FG_DIM, font=("Helvetica",7)).pack(fill="x", pady=(4,0))

        ruf, rui_f = frame_card(col_c, "Rugosidade da superficie (Ra)")
        ruf.pack(fill="x", pady=(0,6))
        tk.Label(rui_f, text="Reducao de interferencia efetiva:",
                 bg=BG, fg=FG_DIM, font=("Helvetica",7)).pack(anchor="w", pady=(0,4))
        self._ra_eixo = entry_row(rui_f, "Ra eixo  [um]", "0.8", cor=GOLD)
        self._ra_hub  = entry_row(rui_f, "Ra cubo  [um]", "6.3", cor=ACCENT)
        tk.Label(rui_f,
                 text=u"d_eff = d_nom − (Ra_eixo + Ra_cubo)×1e−3 mm",
                 bg=BG, fg=FG_DIM, font=("Helvetica",7)).pack(fill="x", pady=(4,0))

        # ── Botao calcular ────────────────────────────────────────────────────
        btn_frame = tk.Frame(W, bg=BG)
        btn_frame.pack(fill="x", padx=20, pady=(4,4))
        self._btn_calc = tk.Button(btn_frame, text=">>  CALCULAR INTERFERENCIA",
            command=self._calcular, bg=BG2, fg=PURPLE,
            font=("Courier",11,"bold"), relief="flat", pady=10, cursor="hand2",
            activebackground=BG, activeforeground=PURPLE)
        self._btn_calc.pack(fill="x")

        # ── Cabecalho de resultados ───────────────────────────────────────────
        tk.Frame(W, bg=PURPLE, height=2).pack(fill="x", padx=20, pady=(6,0))
        res_hdr = tk.Frame(W, bg=BG2)
        res_hdr.pack(fill="x", padx=0)
        tk.Label(res_hdr, text="  RESULTADOS",
                 bg=BG2, fg=PURPLE, font=("Courier",11,"bold"),
                 anchor="w", pady=6).pack(side="left")
        self._lbl_status = tk.Label(res_hdr, text="  aguardando calculo...",
                                    bg=BG2, fg=FG_DIM, font=("Courier",8), anchor="w")
        self._lbl_status.pack(side="left")

        # ── Resultados em 3 colunas ───────────────────────────────────────────
        sec_res = tk.Frame(W, bg=BG)
        sec_res.pack(fill="x", **PAD)
        rc1 = tk.Frame(sec_res, bg=BG)
        rc1.pack(side="left", fill="both", expand=True, padx=(0,8))
        rc2 = tk.Frame(sec_res, bg=BG)
        rc2.pack(side="left", fill="both", expand=True, padx=(0,8))
        rc3 = tk.Frame(sec_res, bg=BG)
        rc3.pack(side="left", fill="both", expand=True)

        # Col 1: Diametros + Interferencias
        df, di2 = frame_card(rc1, "Diametros calculados")
        df.pack(fill="x", pady=(0,6))
        self._v_sh_max = tk.StringVar(value="---"); self._v_sh_min = tk.StringVar(value="---")
        self._v_ho_max = tk.StringVar(value="---"); self._v_ho_min = tk.StringVar(value="---")
        result_row(di2, "Eixo maximo        [mm]", self._v_sh_max, cor=GOLD)
        result_row(di2, "Eixo minimo        [mm]", self._v_sh_min, cor=GOLD)
        result_row(di2, "Furo maximo        [mm]", self._v_ho_max, cor=ACCENT)
        result_row(di2, "Furo minimo        [mm]", self._v_ho_min, cor=ACCENT)
        if2, ii2 = frame_card(rc1, "Interferencia radial")
        if2.pack(fill="x")
        self._v_dmax = tk.StringVar(value="---"); self._v_dmin = tk.StringVar(value="---")
        result_row(ii2, "dmax - pior caso   [mm]", self._v_dmax, cor=ORANGE)
        result_row(ii2, "dmin - melhor caso [mm]", self._v_dmin, cor=GREEN)
        tk.Frame(ii2, bg=BORDER, height=1).pack(fill="x", pady=(4,2))
        self._v_corr_rug = tk.StringVar(value="---")
        result_row(ii2, "corr. rugos.       [mm]", self._v_corr_rug, cor=FG_DIM)
        self._v_dmax_eff = tk.StringVar(value="---"); self._v_dmin_eff = tk.StringVar(value="---")
        result_row(ii2, "dmax_eff (efetivo)  [mm]", self._v_dmax_eff, cor=ORANGE)
        result_row(ii2, "dmin_eff (efetivo)  [mm]", self._v_dmin_eff, cor=GREEN)

        # Col 2: Pressoes + Areas
        pf, pi2 = frame_card(rc2, "Pressao de contato (Lame)")
        pf.pack(fill="x", pady=(0,6))
        self._v_pmax = tk.StringVar(value="---"); self._v_pmin = tk.StringVar(value="---")
        result_row(pi2, "pmax  (dmax)       [MPa]", self._v_pmax, cor=ORANGE)
        result_row(pi2, "pmin  (dmin)       [MPa]", self._v_pmin, cor=GREEN)
        af2, ai2 = frame_card(rc2, "Areas de contato  A = pi x d x w")
        af2.pack(fill="x")
        self._v_A_nom = tk.StringVar(value="---")
        self._v_A_lo  = tk.StringVar(value="---")
        self._v_A_up  = tk.StringVar(value="---")
        result_row(ai2, "A nominal          [mm2]", self._v_A_nom, cor=FG)
        result_row(ai2, "A lower            [mm2]", self._v_A_lo,  cor=FG_DIM)
        result_row(ai2, "A upper            [mm2]", self._v_A_up,  cor=FG_DIM)

        # Col 3: Tabela de forcas
        ff, fi2 = frame_card(rc3, "Forca de encaixe / desencaixe")
        ff.pack(fill="x")
        tk.Label(fi2, text="p = pmax  (eixo max / furo min)",
                 bg=BG, fg=FG_DIM, font=("Helvetica",7)).pack(anchor="w", pady=(0,4))
        th = tk.Frame(fi2, bg=BG2)
        th.pack(fill="x")
        th.columnconfigure((0,1,2,3,4), weight=1)
        for ci_h, h in enumerate(["Caso","Seco [N]","Seco[kgf]","Lubr [N]","Lubr[kgf]"]):
            tk.Label(th, text=h, bg=BG2, fg=FG_DIM, font=FONT_SMALL,
                     anchor="center", padx=2, pady=3).grid(row=0, column=ci_h, sticky="ew")
        self._force_vars = {}
        for ri_f, (key, label, cor) in enumerate([
            ("nominal","Nominal",FG), ("lower","Lower",FG_DIM), ("upper","Upper",FG_DIM)
        ]):
            row_bg = BG3 if ri_f % 2 == 0 else BG
            rf = tk.Frame(fi2, bg=row_bg)
            rf.pack(fill="x")
            rf.columnconfigure((0,1,2,3,4), weight=1)
            tk.Label(rf, text=label, bg=row_bg, fg=cor,
                     font=FONT_SMALL, anchor="w", padx=4, pady=3).grid(row=0, column=0, sticky="ew")
            for ci_f, vk in enumerate(["dry_N","dry_kgf","lubed_N","lubed_kgf"]):
                v = tk.StringVar(value="---")
                self._force_vars[(key, vk)] = v
                tk.Label(rf, textvariable=v, bg=row_bg, fg=cor,
                         font=FONT_SMALL, anchor="center", pady=3).grid(row=0, column=ci_f+1, sticky="ew")
        avg_f = tk.Frame(fi2, bg=BG2)
        avg_f.pack(fill="x", pady=(4,0))
        avg_f.columnconfigure((0,1,2), weight=1)
        tk.Label(avg_f, text="Media nominal (dry+lubed)/2:", bg=BG2, fg=PURPLE,
                 font=FONT_SMALL, anchor="w", padx=4, pady=3).grid(row=0, column=0, sticky="ew")
        self._v_avg_N   = tk.StringVar(value="---")
        self._v_avg_kgf = tk.StringVar(value="---")
        tk.Label(avg_f, textvariable=self._v_avg_N,   bg=BG2, fg=PURPLE,
                 font=("Courier",9,"bold"), anchor="center").grid(row=0, column=1, sticky="ew")
        tk.Label(avg_f, textvariable=self._v_avg_kgf, bg=BG2, fg=PURPLE,
                 font=("Courier",9,"bold"), anchor="center").grid(row=0, column=2, sticky="ew")

        # ── Grafico ───────────────────────────────────────────────────────────
        tk.Frame(W, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(10,4))
        graf_frame = tk.Frame(W, bg=BG)
        graf_frame.pack(fill="x", padx=20, pady=(0,4))
        self._fig2, self._ax_interf = plt.subplots(1, 1, figsize=(13, 4.5), facecolor=BG)
        self._fig2.tight_layout(pad=2.5)
        self._ax_interf.set_facecolor(BG3)
        for sp in self._ax_interf.spines.values(): sp.set_edgecolor(BORDER)
        self._ax_interf.tick_params(colors=FG_DIM, labelsize=8)
        self._canvas_interf = FigureCanvasTkAgg(self._fig2, master=graf_frame)
        self._canvas_interf.get_tk_widget().pack(fill="x")
        self._placeholder_interf()

        # ── Curva de Inserção ─────────────────────────────────────────────────
        tk.Frame(W, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(10,4))
        ins_hdr_f = tk.Frame(W, bg=BG2)
        ins_hdr_f.pack(fill="x", padx=0)
        tk.Label(ins_hdr_f, text="  CURVA DE INSERCAO — Forca x Deslocamento",
                 bg=BG2, fg=ACCENT, font=("Courier",10,"bold"),
                 anchor="w", pady=6).pack(side="left")
        tk.Label(ins_hdr_f, text="Stribeck simplificado (v_ref=15 mm/s)  ",
                 bg=BG2, fg=FG_DIM, font=("Helvetica",8), anchor="e").pack(side="right")

        ins_ctrl = tk.Frame(W, bg=BG)
        ins_ctrl.pack(fill="x", padx=20, pady=(6,2))
        tk.Label(ins_ctrl, text="Velocidade [mm/s]:", bg=BG, fg=FG_DIM,
                 font=("Courier",9)).pack(side="left")
        self._v_ins_speed = tk.StringVar(value="10")
        tk.Entry(ins_ctrl, textvariable=self._v_ins_speed, width=7,
                 bg=BG2, fg=ACCENT, insertbackground=FG,
                 font=("Courier",10), relief="flat",
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(side="left", padx=(6,18))
        tk.Label(ins_ctrl, text="Comparar com [mm/s]:", bg=BG, fg=FG_DIM,
                 font=("Courier",9)).pack(side="left")
        self._v_ins_comp = tk.StringVar(value="2, 5, 20, 50, 100")
        tk.Entry(ins_ctrl, textvariable=self._v_ins_comp, width=24,
                 bg=BG2, fg=FG_DIM, insertbackground=FG,
                 font=("Courier",10), relief="flat",
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(side="left", padx=(6,16))
        tk.Button(ins_ctrl, text="Atualizar Curva",
                  command=self._atualizar_insercao,
                  bg=BG2, fg=ACCENT, font=("Courier",9,"bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2",
                  activebackground=BG, activeforeground=ACCENT).pack(side="left")


        ins_frame = tk.Frame(W, bg=BG)
        ins_frame.pack(fill="x", padx=20, pady=(0,4))
        self._fig_ins, self._ax_ins = plt.subplots(1, 1, figsize=(13, 4.5), facecolor=BG)
        self._fig_ins.tight_layout(pad=2.5)
        self._ax_ins.set_facecolor(BG3)
        for sp in self._ax_ins.spines.values(): sp.set_edgecolor(BORDER)
        self._ax_ins.tick_params(colors=FG_DIM, labelsize=8)
        self._canvas_ins = FigureCanvasTkAgg(self._fig_ins, master=ins_frame)
        self._canvas_ins.get_tk_widget().pack(fill="x")
        self._placeholder_insercao()

        # ── Botao PDF ─────────────────────────────────────────────────────────
        pdf_frame = tk.Frame(W, bg=BG)
        pdf_frame.pack(fill="x", padx=20, pady=(0,20))
        self._btn_pdf2 = tk.Button(pdf_frame, text="Exportar PDF",
            command=self._exportar_pdf, bg=BG2, fg=GOLD,
            font=("Courier",10,"bold"), relief="flat", pady=8, cursor="hand2",
            activebackground=BG, activeforeground=GOLD, state="disabled")
        self._btn_pdf2.pack(fill="x")

    # ── Helper ───────────────────────────────────────────────────────────────

    def _v(self, sv):
        return float(sv.get().replace(",", "."))

    # ── Calculo ───────────────────────────────────────────────────────────────

    def _calcular(self):
        try:
            Ei  = self._v(self._Ei);   vi  = self._v(self._vi)
            di  = self._v(self._di);   d   = self._v(self._d)
            sh_up = self._v(self._tol_sh_up); sh_lo = self._v(self._tol_sh_lo)
            Eo  = self._v(self._Eo);   vo  = self._v(self._vo)
            do_ = self._v(self._do);   dh  = self._v(self._dh)
            ho_up = self._v(self._tol_ho_up); ho_lo = self._v(self._tol_ho_lo)
            w_nom = self._v(self._w_nom)
            w_lo  = self._v(self._w_lo)
            w_up  = self._v(self._w_up)
            mu_dry   = self._v(self._mu_dry)
            mu_lubed = self._v(self._mu_lubed)
            ra_eixo  = self._v(self._ra_eixo)   # [um]
            ra_hub   = self._v(self._ra_hub)     # [um]
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores. Use ponto como decimal."); return

        if do_ <= d:
            messagebox.showerror("Erro", "Diam. externo do cubo (do) deve ser maior que d."); return
        if di >= d:
            messagebox.showerror("Erro", "Diam. interno do eixo (di) deve ser menor que d."); return

        sh_max = d  + sh_up;  sh_min = d  + sh_lo
        ho_max = dh + ho_up;  ho_min = dh + ho_lo
        delta_max = (sh_max - ho_min) / 2
        delta_min = (sh_min - ho_max) / 2

        # Correcao de rugosidade (DIN 7190): picos Ra de ambas as superficies se
        # aplanam durante a montagem, reduzindo a interferencia efetiva.
        # Converte Ra de um para mm (interferencia radial).
        corr_rug = (ra_eixo + ra_hub) * 1e-3   # [mm]
        delta_max_eff = delta_max - corr_rug
        delta_min_eff = delta_min - corr_rug

        if delta_max_eff <= 0:
            messagebox.showerror(
                "Erro",
                f"Interferencia efetiva dmax = {delta_max_eff:.4f} mm <= 0\n"
                f"(correcao de rugosidade = {corr_rug*1e3:.1f} um supera a interferencia nominal)."
            ); return

        self._lbl_shaft.config(text=f"Eixo: {sh_min:.4f}  a  {sh_max:.4f} mm")
        self._lbl_hub.config(  text=f"Furo: {ho_min:.4f}  a  {ho_max:.4f} mm")

        R  = d   / (2 * 1000)
        ri = di  / (2 * 1000)
        ro = do_ / (2 * 1000)

        pmax = lame_pressure(delta_max_eff, R, Eo, ro, vo, Ei, ri, vi)
        pmin = lame_pressure(delta_min_eff, R, Eo, ro, vo, Ei, ri, vi) if delta_min_eff > 0 else 0.0

        A_nom = math.pi * d * w_nom
        A_lo  = math.pi * d * w_lo
        A_up  = math.pi * d * w_up

        F_nom_dry_N,  F_nom_dry_kgf  = engagement_force(pmax, A_nom, mu_dry)
        F_nom_lub_N,  F_nom_lub_kgf  = engagement_force(pmax, A_nom, mu_lubed)
        F_lo_dry_N,   F_lo_dry_kgf   = engagement_force(pmax, A_lo,  mu_dry)
        F_lo_lub_N,   F_lo_lub_kgf   = engagement_force(pmax, A_lo,  mu_lubed)
        F_up_dry_N,   F_up_dry_kgf   = engagement_force(pmax, A_up,  mu_dry)
        F_up_lub_N,   F_up_lub_kgf   = engagement_force(pmax, A_up,  mu_lubed)
        avg_N   = (F_nom_dry_N + F_nom_lub_N) / 2
        avg_kgf = avg_N / 9.81

        self._resultado = dict(
            d=d, di=di, do_=do_, dh=dh, Ei=Ei, vi=vi, Eo=Eo, vo=vo,
            sh_max=sh_max, sh_min=sh_min, ho_max=ho_max, ho_min=ho_min,
            delta_max=delta_max, delta_min=delta_min,
            ra_eixo=ra_eixo, ra_hub=ra_hub, corr_rug=corr_rug,
            delta_max_eff=delta_max_eff, delta_min_eff=delta_min_eff,
            pmax=pmax, pmin=pmin,
            A_nom=A_nom, A_lo=A_lo, A_up=A_up,
            w_nom=w_nom, w_lo=w_lo, w_up=w_up,
            mu_dry=mu_dry, mu_lubed=mu_lubed,
            F_nom_dry_N=F_nom_dry_N, F_nom_dry_kgf=F_nom_dry_kgf,
            F_nom_lub_N=F_nom_lub_N, F_nom_lub_kgf=F_nom_lub_kgf,
            F_lo_dry_N=F_lo_dry_N,   F_lo_dry_kgf=F_lo_dry_kgf,
            F_lo_lub_N=F_lo_lub_N,   F_lo_lub_kgf=F_lo_lub_kgf,
            F_up_dry_N=F_up_dry_N,   F_up_dry_kgf=F_up_dry_kgf,
            F_up_lub_N=F_up_lub_N,   F_up_lub_kgf=F_up_lub_kgf,
            avg_N=avg_N, avg_kgf=avg_kgf,
        )
        self._lbl_status.config(
            text=(f"  dmax_eff={delta_max_eff:.4f} mm  (nom={delta_max:.4f} - rug={corr_rug*1e3:.1f}um)"
                  f"  pmax={pmax:.2f} MPa  F_nom_seco={F_nom_dry_N:.0f} N"),
            fg=GREEN)
        self._mostrar_resultado(self._resultado)
        self._btn_pdf2.config(state="normal")

    def _mostrar_resultado(self, r):
        self._v_sh_max.set(f"{r['sh_max']:.4f}")
        self._v_sh_min.set(f"{r['sh_min']:.4f}")
        self._v_ho_max.set(f"{r['ho_max']:.4f}")
        self._v_ho_min.set(f"{r['ho_min']:.4f}")
        self._v_dmax.set(f"{r['delta_max']:.4f}")
        dm = r['delta_min']
        self._v_dmin.set(f"{dm:.4f}" if dm > 0 else f"{dm:.4f}  FOLGA!")
        self._v_corr_rug.set(f"{r['corr_rug']*1e3:.2f} um  ({r['ra_eixo']:.2f}+{r['ra_hub']:.2f})")
        self._v_dmax_eff.set(f"{r['delta_max_eff']:.4f}")
        dme = r['delta_min_eff']
        self._v_dmin_eff.set(f"{dme:.4f}" if dme > 0 else f"{dme:.4f}  FOLGA!")
        self._v_pmax.set(f"{r['pmax']:.4f}")
        self._v_pmin.set(f"{r['pmin']:.4f}" if r['pmin'] > 0 else "folga")
        self._v_A_nom.set(f"{r['A_nom']:.2f}")
        self._v_A_lo.set( f"{r['A_lo']:.2f}")
        self._v_A_up.set( f"{r['A_up']:.2f}")
        for key, vals in [
            ("nominal", (r["F_nom_dry_N"], r["F_nom_dry_kgf"], r["F_nom_lub_N"], r["F_nom_lub_kgf"])),
            ("lower",   (r["F_lo_dry_N"],  r["F_lo_dry_kgf"],  r["F_lo_lub_N"],  r["F_lo_lub_kgf"])),
            ("upper",   (r["F_up_dry_N"],  r["F_up_dry_kgf"],  r["F_up_lub_N"],  r["F_up_lub_kgf"])),
        ]:
            for vk, val in zip(["dry_N","dry_kgf","lubed_N","lubed_kgf"], vals):
                self._force_vars[(key, vk)].set(f"{val:.1f}")
        self._v_avg_N.set(  f"{r['avg_N']:.1f} N")
        self._v_avg_kgf.set(f"{r['avg_kgf']:.1f} kgf")
        self._plotar(r)
        self._atualizar_insercao()

    def _plotar(self, r):
        ax = self._ax_interf; ax.clear(); ax.set_facecolor(BG3)
        casos = ["Nominal", "Lower", "Upper"]
        dry   = [r["F_nom_dry_N"]/1000, r["F_lo_dry_N"]/1000, r["F_up_dry_N"]/1000]
        lubed = [r["F_nom_lub_N"]/1000, r["F_lo_lub_N"]/1000, r["F_up_lub_N"]/1000]
        x = np.arange(len(casos)); bw = 0.35
        b1 = ax.bar(x - bw/2, dry,   bw, label=f"Seco   (mu={r['mu_dry']:.2f})",   color=ACCENT, alpha=0.85)
        b2 = ax.bar(x + bw/2, lubed, bw, label=f"Lubric (mu={r['mu_lubed']:.2f})", color=GREEN,  alpha=0.85)
        for bar in list(b1) + list(b2):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=7, color=FG_DIM)
        ax.set_xticks(x); ax.set_xticklabels(casos, color=FG_DIM, fontsize=9)
        ax.set_ylabel("Forca [kN]", color=FG_DIM, fontsize=8)
        ax.set_title(
            f"Forca de encaixe/desencaixe  |  p = {r['pmax']:.2f} MPa  |  dmax = {r['delta_max']:.4f} mm",
            color=FG_DIM, fontsize=8, pad=6)
        ax.legend(fontsize=8, facecolor=BG2, edgecolor=BORDER, labelcolor=FG, loc="upper right")
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM, labelsize=8)
        self._fig2.tight_layout(pad=2.0); self._canvas_interf.draw()

    def _placeholder_interf(self):
        ax = self._ax_interf; ax.clear(); ax.set_facecolor(BG3)
        ax.text(0.5, 0.5,
            "sem dados\nPreencha os parametros acima e clique   >>  CALCULAR INTERFERENCIA",
            transform=ax.transAxes, ha="center", va="center",
            color="#2a3a44", fontsize=9, multialignment="center")
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM, labelsize=8)
        self._canvas_interf.draw()

    def _placeholder_insercao(self):
        ax = self._ax_ins; ax.clear(); ax.set_facecolor(BG3)
        ax.text(0.5, 0.5,
            "sem dados\nPreencha os parametros e clique  >>  CALCULAR INTERFERENCIA",
            transform=ax.transAxes, ha="center", va="center",
            color="#2a3a44", fontsize=9, multialignment="center")
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM, labelsize=8)
        self._canvas_ins.draw()

    def _atualizar_insercao(self):
        if self._resultado is None:
            return
        try:
            v = float(self._v_ins_speed.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Velocidade invalida. Use ponto como decimal."); return
        try:
            comp = [float(s.strip()) for s in self._v_ins_comp.get().split(",") if s.strip()]
        except ValueError:
            comp = []
        self._plotar_insercao(self._resultado, v, comp, 0.0, 0.0)

    def _plotar_insercao(self, r, v_mm_s, comp_speeds=None, x0=0.0, apx=0.0):
        import matplotlib.transforms as mtransforms
        ax = self._ax_ins; ax.clear(); ax.set_facecolor(BG3)

        # Lista completa de velocidades (principal + comparacao), sem duplicatas, ordenada
        all_speeds = sorted(set([v_mm_s] + (comp_speeds or [])))
        n_v = len(all_speeds)

        # Paleta de verdes para curvas lubrificadas (mais velocidade = verde mais escuro)
        lub_palette = plt.cm.YlGn(np.linspace(0.35, 0.90, n_v))

        # Fase de aproximacao (F=0) + fase de insercao no referencial absoluto da maquina
        n_apx = max(2, int(apx * 3))
        x_apx = np.linspace(x0, x0 + apx, n_apx)
        F_apx = np.zeros(n_apx)

        # Curva seca (independe da velocidade) — calculada uma vez
        x_ins, F_dry, _, _ = insertion_curve(
            r["pmax"], r["d"], r["w_nom"], r["mu_dry"], r["mu_lubed"], 0.0)
        x_ins_abs = x_ins + x0 + apx  # deslocamento absoluto

        x_full     = np.concatenate([x_apx, x_ins_abs])
        F_dry_full = np.concatenate([F_apx, F_dry])

        # Linha horizontal de pico seco
        ax.axhline(F_dry[-1], color=ACCENT, lw=0.8, ls=":", alpha=0.5)

        # Curva seca — destaque visual alto, plotada por ultimo para ficar no topo
        ax.plot(x_full, F_dry_full, color=ACCENT, lw=2.5, zorder=20,
                label=f"— SECO  μ={r['mu_dry']:.2f}  │  F_max={F_dry[-1]:.2f} kN")

        # Curvas lubrificadas para cada velocidade
        for i, v in enumerate(all_speeds):
            is_main = abs(v - v_mm_s) < 0.01
            _, _, F_lub, mu_v = insertion_curve(
                r["pmax"], r["d"], r["w_nom"], r["mu_dry"], r["mu_lubed"], v)
            F_lub_full = np.concatenate([F_apx, F_lub])
            lw   = 2.3 if is_main else 1.4
            zord = 15  if is_main else 8
            ls   = "-" if is_main else "--"
            marker = " ★" if is_main else ""
            ax.plot(x_full, F_lub_full, ls=ls, color=lub_palette[i], lw=lw, zorder=zord,
                    label=f"Lubr. {v:.0f} mm/s{marker}  μ_ef={mu_v:.3f}  │  F={F_lub[-1]:.2f} kN")
            # Linha pontilhada de pico
            ax.axhline(F_lub[-1], color=lub_palette[i], lw=0.6, ls=":", alpha=0.35)

        # Marcadores de largura (no referencial absoluto)
        for w_val, w_lbl, w_col in [
            (r["w_nom"], "w_nom", PURPLE),
            (r["w_lo"],  "w_lo",  FG_DIM),
            (r["w_up"],  "w_up",  FG_DIM),
        ]:
            ax.axvline(x0 + apx + w_val, color=w_col, lw=1.0, ls="--", alpha=0.4)
            trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
            ax.text(x0 + apx + w_val + r["w_nom"] * 0.008, 0.03, w_lbl,
                    transform=trans, color=w_col, fontsize=7, va="bottom")

        # Eixo X: label "mm" posicionado à direita (igual à máquina)
        ax.set_xlabel("mm", color=FG_DIM, fontsize=9, labelpad=4)
        ax.xaxis.set_label_coords(1.02, -0.04)
        # Eixo Y: label "Kn" posicionado no topo, sem rotação (igual à máquina)
        ax.set_ylabel("Kn", rotation=0, color=FG_DIM, fontsize=9, labelpad=6)
        ax.yaxis.set_label_coords(-0.06, 1.03)
        mu_main = mu_eff_speed(r["mu_dry"], r["mu_lubed"], v_mm_s)
        ax.set_title(
            f"Curva de insercao  |  p={r['pmax']:.2f} MPa  |  seco={r['mu_dry']:.2f}  |  "
            f"lubr. v★={v_mm_s:.1f} mm/s → μ_ef={mu_main:.3f}  |  Stribeck v_ref=15 mm/s",
            color=FG_DIM, fontsize=8, pad=6)
        ncol = max(1, (n_v + 1 + 1) // 3)
        ax.legend(fontsize=7, facecolor=BG2, edgecolor=BORDER, labelcolor=FG,
                  loc="upper left", ncol=ncol)
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM, labelsize=8)
        ax.grid(True, linestyle="--", alpha=0.3, color=FG_DIM, linewidth=0.5)
        ax.set_xlim([x0, x0 + apx + r["w_nom"] * 1.05])
        ax.set_ylim([0, None])
        self._fig_ins.tight_layout(pad=2.0); self._canvas_ins.draw()

    def _exportar_pdf(self):
        if self._resultado is None:
            messagebox.showwarning("Atencao", "Realize o calculo antes de exportar."); return
        path = filedialog.asksaveasfilename(title="Salvar relatorio PDF",
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path: return
        try:
            self._gerar_pdf(path)
            messagebox.showinfo("Sucesso", f"PDF salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _gerar_pdf(self, path):
        r = self._resultado
        now = __import__("datetime").datetime.now().strftime("%d/%m/%Y %H:%M")
        fig_p, ax_p = plt.subplots(1, 1, figsize=(7, 3.5), facecolor="white")
        casos = ["Nominal", "Lower", "Upper"]
        dry   = [r["F_nom_dry_N"]/1000, r["F_lo_dry_N"]/1000, r["F_up_dry_N"]/1000]
        lubed = [r["F_nom_lub_N"]/1000, r["F_lo_lub_N"]/1000, r["F_up_lub_N"]/1000]
        x = __import__("numpy").arange(len(casos)); bw = 0.35
        ax_p.bar(x - bw/2, dry,   bw, label=f"Seco (mu={r['mu_dry']:.2f})",   color="#0077aa", alpha=0.85)
        ax_p.bar(x + bw/2, lubed, bw, label=f"Lubr (mu={r['mu_lubed']:.2f})", color="#22aa55", alpha=0.85)
        ax_p.set_xticks(x); ax_p.set_xticklabels(casos, fontsize=8)
        ax_p.set_ylabel("Forca [kN]", fontsize=8)
        ax_p.set_title("Forca de encaixe/desencaixe por caso de largura", fontsize=9)
        ax_p.legend(fontsize=7); ax_p.tick_params(labelsize=7)
        buf = __import__("io").BytesIO()
        fig_p.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
        buf.seek(0); plt.close(fig_p)

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, Image as RLImage, HRFlowable)
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT

        doc = SimpleDocTemplate(path, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=18*mm, bottomMargin=18*mm)
        PW = A4[0] - 40*mm
        s_t = ParagraphStyle("t", fontSize=14, fontName="Helvetica-Bold",
                              textColor=colors.HexColor("#003366"), spaceAfter=2)
        s_a = ParagraphStyle("a", fontSize=9,  fontName="Helvetica-Bold",
                              textColor=colors.HexColor("#003366"), spaceAfter=1)
        s_n = ParagraphStyle("n", fontSize=7.5, fontName="Helvetica-Oblique",
                              textColor=colors.HexColor("#666666"), spaceAfter=4)
        s_s = ParagraphStyle("s", fontSize=10, fontName="Helvetica-Bold",
                              textColor=colors.HexColor("#003366"), spaceBefore=10, spaceAfter=4)
        s_w = ParagraphStyle("w", fontSize=7.5, fontName="Helvetica-Oblique",
                              textColor=colors.HexColor("#7a5000"),
                              backColor=colors.HexColor("#fff8e1"),
                              spaceAfter=4, leftIndent=6, rightIndent=6)
        def tbl(data, cw):
            t = Table(data, colWidths=cw)
            t.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#003366")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),8),
                ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f4f8"),colors.white]),
                ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cccccc")),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ]))
            return t

        story = []
        ht = Table([[Paragraph("RELATORIO - KNUCKLE INTERFERENCE CALCULATOR", s_t),
                     Paragraph(f"Gerado em: {now}",
                     ParagraphStyle("rt", fontSize=8, fontName="Helvetica",
                     textColor=colors.HexColor("#555555"), alignment=TA_RIGHT))]],
                   colWidths=[PW*0.65, PW*0.35])
        ht.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                 ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(ht)
        story.append(Paragraph("Author: Bruno Bernardinetti - Stellantis", s_a))
        story.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor("#003366"), spaceAfter=4))
        story.append(Paragraph(
            "Metodo: Equacoes de Lame para cilindros de parede grossa. "
            "Interferencia radial com correcao de rugosidade (Ra_eixo + Ra_cubo). "
            "Forcas calculadas para duas condicoes de atrito "
            "(seco e lubrificado) e tres larguras (nominal, lower, upper).", s_n))
        story.append(Paragraph("Parametros de Entrada", s_s))
        story.append(tbl([
            ["Parametro", "Eixo (Shaft)", "Cubo (Hub)", "Unidade"],
            ["Young E",         f"{r['Ei']:.2f}",   f"{r['Eo']:.2f}",   "GPa"],
            ["Poisson nu",      f"{r['vi']:.3f}",   f"{r['vo']:.3f}",   "---"],
            ["Diam. nominal",   f"{r['d']:.3f}",    f"{r['dh']:.3f}",   "mm"],
            ["Diam. ext./int.", f"{r['di']:.3f} (int.)", f"{r['do_']:.3f} (ext.)", "mm"],
            ["Diam. maximo",    f"{r['sh_max']:.4f}", f"{r['ho_max']:.4f}", "mm"],
            ["Diam. minimo",    f"{r['sh_min']:.4f}", f"{r['ho_min']:.4f}", "mm"],
            ["Rugosidade Ra",   f"{r['ra_eixo']:.2f}",  f"{r['ra_hub']:.2f}",  "um"],
        ], [PW*0.35, PW*0.22, PW*0.22, PW*0.21]))
        story.append(tbl([
            ["Larg. nominal [mm]","Larg. lower [mm]","Larg. upper [mm]","mu seco","mu lubr."],
            [f"{r['w_nom']:.2f}", f"{r['w_lo']:.2f}", f"{r['w_up']:.2f}",
             f"{r['mu_dry']:.2f}", f"{r['mu_lubed']:.2f}"],
        ], [PW*0.22]*5))
        story.append(Paragraph("Resultados", s_s))
        pmin_str = f"{r['pmin']:.4f}" if r['pmin'] > 0 else "folga"
        dmin_eff_str = f"{r['delta_min_eff']:.4f}" if r['delta_min_eff'] > 0 else f"{r['delta_min_eff']:.4f}  FOLGA"
        story.append(tbl([
            ["Grandeza", "Valor", "Unidade"],
            ["Interferencia nominal dmax", f"{r['delta_max']:.4f}", "mm"],
            ["Interferencia nominal dmin", f"{r['delta_min']:.4f}", "mm"],
            [f"Correcao rugosidade (Ra_eixo={r['ra_eixo']:.2f} + Ra_cubo={r['ra_hub']:.2f})",
             f"{r['corr_rug']*1e3:.2f}", "um"],
            ["Interferencia efetiva dmax_eff", f"{r['delta_max_eff']:.4f}", "mm"],
            ["Interferencia efetiva dmin_eff", dmin_eff_str,                 "mm"],
            ["Pressao pmax (Lame, dmax_eff)", f"{r['pmax']:.4f}",           "MPa"],
            ["Pressao pmin (Lame, dmin_eff)", pmin_str,                      "MPa"],
            ["Area A nominal",               f"{r['A_nom']:.2f}",           "mm2"],
            ["Area A lower",                 f"{r['A_lo']:.2f}",            "mm2"],
            ["Area A upper",                 f"{r['A_up']:.2f}",            "mm2"],
        ], [PW*0.55, PW*0.25, PW*0.20]))
        story.append(Paragraph("Forcas de Encaixe / Desencaixe", s_s))
        story.append(tbl([
            ["Caso", "Seco [N]", "Seco [kgf]", "Lubr [N]", "Lubr [kgf]"],
            ["Nominal", f"{r['F_nom_dry_N']:.1f}", f"{r['F_nom_dry_kgf']:.1f}",
                        f"{r['F_nom_lub_N']:.1f}", f"{r['F_nom_lub_kgf']:.1f}"],
            ["Lower",   f"{r['F_lo_dry_N']:.1f}",  f"{r['F_lo_dry_kgf']:.1f}",
                        f"{r['F_lo_lub_N']:.1f}",  f"{r['F_lo_lub_kgf']:.1f}"],
            ["Upper",   f"{r['F_up_dry_N']:.1f}",  f"{r['F_up_dry_kgf']:.1f}",
                        f"{r['F_up_lub_N']:.1f}",  f"{r['F_up_lub_kgf']:.1f}"],
            ["Media nominal (dry+lubed)/2", f"{r['avg_N']:.1f}", f"{r['avg_kgf']:.1f}", "---","---"],
        ], [PW*0.30, PW*0.175, PW*0.175, PW*0.175, PW*0.175]))
        story.append(Paragraph("Grafico - Forca por Caso de Largura", s_s))
        story.append(RLImage(buf, width=PW*0.85, height=PW*0.85*3.5/7))
        story.append(Spacer(1, 6))

        # ── Curva de insercao no PDF ──────────────────────────────────────────
        try:
            v_pdf = float(self._v_ins_speed.get().replace(",", "."))
        except ValueError:
            v_pdf = 10.0
        try:
            comp_pdf = [float(s.strip()) for s in self._v_ins_comp.get().split(",") if s.strip()]
        except ValueError:
            comp_pdf = [2, 5, 20, 50, 100]

        all_speeds_pdf = sorted(set([v_pdf] + comp_pdf))
        n_v_pdf = len(all_speeds_pdf)
        lub_pal_pdf = plt.cm.YlGn(np.linspace(0.35, 0.90, n_v_pdf))

        fig_ins_p, ax_ins_p = plt.subplots(1, 1, figsize=(9, 4.0), facecolor="white")
        x_p, F_dry_p, _, _ = insertion_curve(
            r["pmax"], r["d"], r["w_nom"], r["mu_dry"], r["mu_lubed"], 0.0)
        ax_ins_p.axhline(F_dry_p[-1], color="#0055aa", lw=0.7, ls=":", alpha=0.5)
        for i, v_i in enumerate(all_speeds_pdf):
            is_main = abs(v_i - v_pdf) < 0.01
            _, _, F_lub_i, mu_i = insertion_curve(
                r["pmax"], r["d"], r["w_nom"], r["mu_dry"], r["mu_lubed"], v_i)
            lw = 2.0 if is_main else 1.2
            ls = "-" if is_main else "--"
            mk = " ★" if is_main else ""
            ax_ins_p.plot(x_p, F_lub_i, ls=ls, color=lub_pal_pdf[i], lw=lw,
                          label=f"Lubr. {v_i:.0f} mm/s{mk}  μ_ef={mu_i:.3f}  F={F_lub_i[-1]:.2f} kN")
            ax_ins_p.axhline(F_lub_i[-1], color=lub_pal_pdf[i], lw=0.5, ls=":", alpha=0.35)
        ax_ins_p.plot(x_p, F_dry_p, color="#0055aa", lw=2.2,
                      label=f"SECO  μ={r['mu_dry']:.2f}  F={F_dry_p[-1]:.2f} kN", zorder=10)
        ax_ins_p.axvline(r["w_nom"], color="#8800cc", lw=1.0, ls="--", alpha=0.5,
                         label=f"w_nom={r['w_nom']:.2f} mm")
        ax_ins_p.set_xlabel("mm", fontsize=9, labelpad=4)
        ax_ins_p.xaxis.set_label_coords(1.02, -0.04)
        ax_ins_p.set_ylabel("Kn", rotation=0, fontsize=9, labelpad=6)
        ax_ins_p.yaxis.set_label_coords(-0.06, 1.03)
        ax_ins_p.set_title(
            f"Curva de insercao  |  seco μ={r['mu_dry']:.2f}  |  "
            f"lubr. ★ v={v_pdf:.1f} mm/s  |  Stribeck v_ref=15 mm/s",
            fontsize=9)
        ncol_pdf = max(1, (n_v_pdf + 2) // 3)
        ax_ins_p.legend(fontsize=6.5, loc="upper left", ncol=ncol_pdf)
        ax_ins_p.tick_params(labelsize=7)
        ax_ins_p.set_xlim([0, None]); ax_ins_p.set_ylim([0, None])
        buf_ins = io.BytesIO()
        fig_ins_p.savefig(buf_ins, format="png", dpi=150, bbox_inches="tight", facecolor="white")
        buf_ins.seek(0); plt.close(fig_ins_p)

        story.append(Paragraph("Grafico - Curva de Insercao (Forca x Deslocamento)", s_s))
        story.append(RLImage(buf_ins, width=PW*0.85, height=PW*0.85*3.5/7))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f"Modelo de atrito: Stribeck simplificado (v_ref=15 mm/s). "
            f"Velocidade selecionada (★): {v_pdf:.1f} mm/s. "
            f"Velocidades comparadas: {', '.join(f'{v:.0f}' for v in all_speeds_pdf)} mm/s. "
            f"Curva seca independe da velocidade. A forca cresce linearmente com o deslocamento "
            f"(area de contato proporcional a insercao).", s_n))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            "Aviso: Calculos baseados na teoria classica de Lame (elasticidade linear). "
            "Nao considera gradientes termicos, dinamica ou fadiga. "
            "Validar com FEA para aplicacoes criticas.", s_w))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#cccccc"), spaceAfter=4))
        story.append(Paragraph(
            f"Gerado pelo Estimador de Rugosidade + Interferencia  |  "
            f"Author: Bruno Bernardinetti - Stellantis  |  {now}",
            ParagraphStyle("footer", fontSize=7, fontName="Helvetica",
                           textColor=colors.HexColor("#888888"), alignment=TA_CENTER)))
        doc.build(story)

# ─────────────────────────────────────────────────────────────────────────────
# Comparador de Curvas XML  (Force Curve Comparator — Knuckle Press-Fit)
# ─────────────────────────────────────────────────────────────────────────────

import xml.etree.ElementTree as ET
import matplotlib.patches as mpatches

_C_OK    = "#2ecc71"
_C_NOK   = "#e74c3c"
_C_PANEL = "#2a2a3e"
_C_BTN   = "#313244"
_C_SEL   = "#89b4fa"
_C_DIM   = "#a6adc8"
_OK_SH   = ["#2ecc71","#27ae60","#1abc9c","#52be80","#76d7a8","#a9dfbf"]
_NOK_SH  = ["#e74c3c","#c0392b","#e67e22","#d35400","#f1948a","#f5b7b1"]


def _xml_parse(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    def gv(tag):
        el = root.find(f".//{tag}")
        return el.get("Value") if el is not None else ""
    meta = {k: gv(t) for k, t in [
        ("date","Date"),("time","Time"),("cycle","Cycle_number"),
        ("program","Measuring_program_name"),
        ("block_x","Block_X"),("block_y","Block_Y")]}
    xs, ys = [], []
    pts = (root.findall(".//Point") or
           root.findall(".//POINT") or
           root.findall(".//point") or
           root.findall(".//Pt"))
    for pt in pts:
        x_el = pt.find("X-ABSOLUTE-")
        if x_el is None: x_el = pt.find("X_-ABSOLUTE-")
        if x_el is None: x_el = pt.find("X-Absolute")
        if x_el is None: x_el = pt.find("X-absolute")
        if x_el is None: x_el = pt.find("X")
        if x_el is None:
            for child in pt:
                if child.tag.upper().startswith("X"):
                    try:
                        float((child.get("Value") or "").replace(",", "."))
                        x_el = child
                        break
                    except (ValueError, AttributeError):
                        pass
        y_el = pt.find("Y")
        if y_el is None: y_el = pt.find("y")
        if x_el is not None and y_el is not None:
            try:
                xs.append(float(x_el.get("Value").replace(",",".")))
                ys.append(float(y_el.get("Value").replace(",",".")))
            except (ValueError, AttributeError):
                pass
    if not xs:
        raise ValueError(f"Nenhum ponto <Point> válido em {os.path.basename(filepath)}")
    return {"x": xs, "y": ys, "meta": meta}


def _xml_auto_classify(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".xml":
        try:
            tree = ET.parse(filepath)
            el = tree.getroot().find(".//Total_result")
            if el is not None:
                val = el.get("Value", "").strip().upper()
                if val in ("OK", "NOK"):
                    return val
        except Exception:
            pass
    name = os.path.basename(filepath).upper()
    pos_ok  = name.rfind("_OK")
    pos_nok = name.rfind("_NOK")
    if pos_nok == -1 and pos_ok == -1:
        pos_ok = name.rfind("OK"); pos_nok = name.rfind("NOK")
    if pos_nok == -1 and pos_ok == -1: return "OK"
    if pos_nok == -1: return "OK"
    if pos_ok  == -1: return "NOK"
    return "NOK" if pos_nok > pos_ok else "OK"


def _extract_mp(filepath):
    """Extrai código MP do nome do arquivo, ex: 'MP-006' de 'Part_ST030_MP-006_2022-...'"""
    m = re.search(r'MP-\d+', os.path.basename(filepath), re.IGNORECASE)
    return m.group(0).upper() if m else ""


def _extract_year(filepath):
    """Extrai ano de 4 dígitos do nome do arquivo, ex: '2022'."""
    m = re.search(r'(20\d{2}|19\d{2})', os.path.basename(filepath))
    return m.group(1) if m else ""


class _CurveEntry:
    def __init__(self, filepath, classification):
        self.filepath       = filepath
        self.label          = os.path.splitext(os.path.basename(filepath))[0]
        self.classification = classification
        self.data           = _xml_parse(filepath)
    @property
    def x(self):    return self.data["x"]
    @property
    def y(self):    return self.data["y"]
    @property
    def meta(self): return self.data["meta"]


class AbaXMLComparator(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.entries: list[_CurveEntry] = []
        self._shown_entries: list[_CurveEntry] = []
        self._build()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        # ── Painel esquerdo ──────────────────────────────────────────────────
        left = tk.Frame(outer, bg=_C_PANEL, width=300)
        left.pack(side="left", fill="y", padx=(8,0), pady=8)
        left.pack_propagate(False)

        tk.Label(left, text="Force Curve Comparator",
                 bg=_C_PANEL, fg=_C_SEL,
                 font=("Segoe UI",11,"bold")).pack(pady=(12,2))
        tk.Label(left, text="Knuckle Press-Fit  |  Stellantis",
                 bg=_C_PANEL, fg=_C_DIM,
                 font=("Segoe UI",8)).pack(pady=(0,8))

        # ── Filtros MP / Ano ─────────────────────────────────────────────────
        ff = tk.Frame(left, bg=_C_PANEL)
        ff.pack(fill="x", padx=6, pady=(0, 2))
        tk.Label(ff, text="Ponto:", bg=_C_PANEL, fg=_C_DIM,
                 font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", pady=1)
        self._filter_mp = tk.StringVar(value="Todos")
        self._cb_mp = ttk.Combobox(ff, textvariable=self._filter_mp,
                                   values=["Todos"], state="readonly",
                                   font=("Segoe UI", 8), width=10)
        self._cb_mp.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=1)
        tk.Label(ff, text="Ano:", bg=_C_PANEL, fg=_C_DIM,
                 font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w", pady=1)
        self._filter_year = tk.StringVar(value="Todos")
        self._cb_year = ttk.Combobox(ff, textvariable=self._filter_year,
                                     values=["Todos"], state="readonly",
                                     font=("Segoe UI", 8), width=10)
        self._cb_year.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=1)
        ff.columnconfigure(1, weight=1)
        self._cb_mp.bind("<<ComboboxSelected>>",
                         lambda _: (self._refresh_list(), self._plot()))
        self._cb_year.bind("<<ComboboxSelected>>",
                           lambda _: (self._refresh_list(), self._plot()))

        lf = tk.Frame(left, bg=_C_PANEL)
        lf.pack(fill="both", expand=True, padx=6)
        self._lb = tk.Listbox(lf, bg=_C_BTN, fg="#cdd6f4",
                              selectbackground=_C_SEL, selectforeground="#000",
                              font=("Consolas",8), relief="flat", bd=0,
                              activestyle="none", exportselection=False)
        self._lb.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(lf, orient="vertical", command=self._lb.yview)
        sb.pack(side="right", fill="y")
        self._lb.config(yscrollcommand=sb.set)
        self._lb.bind("<<ListboxSelect>>", self._on_select)

        self._detail = tk.StringVar(value="")
        tk.Label(left, textvariable=self._detail, bg=_C_PANEL, fg=_C_DIM,
                 font=("Consolas",8), justify="left",
                 wraplength=280).pack(padx=8, pady=(4,0))

        tk.Frame(left, bg="#45475a", height=1).pack(fill="x", padx=10, pady=6)

        for text, cmd in [
            ("➕  Adicionar XML(s)",    self._add_files),
            ("🗑  Remover selecionado", self._remove_selected),
            ("✏  Renomear label",       self._rename_label),
        ]:
            self._btn(left, text, cmd).pack(fill="x", padx=8, pady=2)

        tk.Label(left, text="Classificação manual:",
                 bg=_C_PANEL, fg=_C_DIM, font=("Segoe UI",8)).pack(pady=(6,0))
        cf = tk.Frame(left, bg=_C_PANEL)
        cf.pack(fill="x", padx=8, pady=2)
        self._btn(cf,"✔  OK",  lambda: self._set_class("OK"),
                  color="#1e4d2b", fg=_C_OK).pack(side="left",expand=True,fill="x",padx=(0,2))
        self._btn(cf,"✘  NOK", lambda: self._set_class("NOK"),
                  color="#4d1e1e", fg=_C_NOK).pack(side="left",expand=True,fill="x")

        tk.Frame(left, bg="#45475a", height=1).pack(fill="x", padx=10, pady=6)

        self._btn(left,"📊  Plotar / Atualizar",
                  self._plot, color="#1e3a5f", fg=_C_SEL).pack(fill="x",padx=8,pady=2)
        self._btn(left,"💾  Salvar gráfico",
                  self._save_plot).pack(fill="x",padx=8,pady=2)
        self._btn(left,"🗑  Limpar tudo",
                  self._clear_all).pack(fill="x",padx=8,pady=2)

        # Janela de aprovação
        tk.Frame(left, bg="#45475a", height=1).pack(fill="x", padx=10, pady=6)
        tk.Label(left, text="Janela de Aprovação",
                 bg=_C_PANEL, fg=_C_SEL,
                 font=("Segoe UI",9,"bold")).pack(pady=(0,4))
        wg = tk.Frame(left, bg=_C_PANEL)
        wg.pack(fill="x", padx=8)

        def _we(row, col, label, default):
            tk.Label(wg, text=label, bg=_C_PANEL, fg=_C_DIM,
                     font=("Segoe UI",8), anchor="w").grid(
                     row=row, column=col*2, sticky="w",
                     padx=(6 if col else 0, 2), pady=2)
            var = tk.StringVar(value=default)
            tk.Entry(wg, textvariable=var, width=7, bg=_C_BTN, fg="#cdd6f4",
                     insertbackground="#cdd6f4", relief="flat",
                     highlightthickness=1, highlightbackground="#45475a",
                     font=("Consolas",9)).grid(
                     row=row, column=col*2+1, sticky="ew",
                     padx=(0, 8 if col else 4), pady=2)
            return var

        self._wx0 = _we(0,0,"X min","115")
        self._wx1 = _we(0,1,"X max","130")
        self._wy0 = _we(1,0,"Y min","9.80")
        self._wy1 = _we(1,1,"Y max","58.00")

        self._btn(left,"↺  Aplicar Janela",
                  self._plot, color="#1e3a5f", fg=_C_SEL).pack(fill="x",padx=8,pady=(6,2))

        # Visualização
        tk.Frame(left, bg="#45475a", height=1).pack(fill="x", padx=10, pady=6)
        tk.Label(left, text="Visualização",
                 bg=_C_PANEL, fg=_C_SEL,
                 font=("Segoe UI",9,"bold")).pack(pady=(0,4))
        vg = tk.Frame(left, bg=_C_PANEL)
        vg.pack(fill="x", padx=8, pady=(0,4))
        tk.Label(vg, text="Max curvas:", bg=_C_PANEL, fg=_C_DIM,
                 font=("Segoe UI",8)).grid(row=0,column=0,sticky="w",pady=2)
        self._max_var = tk.StringVar(value="Todas")
        mc = ttk.Combobox(vg, textvariable=self._max_var, width=8,
                          values=["Todas","1","2","3","5","10","20","50"],
                          state="readonly", font=("Segoe UI",8))
        mc.grid(row=0,column=1,sticky="w",padx=(6,0),pady=2)
        mc.bind("<<ComboboxSelected>>", lambda _: self._plot())
        self._legend_var = tk.BooleanVar(value=True)
        tk.Checkbutton(vg, text="Mostrar legenda", variable=self._legend_var,
                       bg=_C_PANEL, fg=_C_DIM, selectcolor=_C_BTN,
                       activebackground=_C_PANEL, activeforeground=_C_SEL,
                       font=("Segoe UI",8),
                       command=self._plot).grid(row=1,column=0,columnspan=2,sticky="w",pady=2)

        self._status = tk.StringVar(value="Nenhum arquivo carregado.")
        tk.Label(left, textvariable=self._status, bg=_C_PANEL, fg=_C_DIM,
                 font=("Segoe UI",8), wraplength=280,
                 justify="left").pack(pady=(6,10),padx=8)

        # ── Painel direito — gráfico ─────────────────────────────────────────
        right = tk.Frame(outer, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self._fig, self._axes = plt.subplots(1,2,figsize=(12,5.8),facecolor="#181825")
        self._style_axes()
        self._canvas = FigureCanvasTkAgg(self._fig, master=right)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        tb_frame = tk.Frame(right, bg="#181825")
        tb_frame.pack(fill="x")
        NavigationToolbar2Tk(self._canvas, tb_frame).update()
        self._canvas.draw()

    # ── helpers ──────────────────────────────────────────────────────────────
    def _btn(self, parent, text, cmd, color=_C_BTN, fg="#cdd6f4"):
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=fg,
                         activebackground=_C_SEL, activeforeground="#000",
                         relief="flat", bd=0, padx=8, pady=5,
                         font=("Segoe UI",9), cursor="hand2")

    def _style_axes(self):
        for ax, (title, color) in zip(self._axes,[("OK",_C_OK),("NOK",_C_NOK)]):
            ax.set_facecolor("#1e1e2e")
            ax.tick_params(colors="#cdd6f4", labelsize=9)
            for sp in ax.spines.values():
                sp.set_color("#45475a"); sp.set_linewidth(0.8)
            ax.grid(True,color="#313244",linewidth=0.6,linestyle="--",alpha=0.7)
            ax.set_title(title,color=color,fontsize=13,fontweight="bold",pad=10)
            ax.set_xlabel("Curso [mm]",color="#cdd6f4",fontsize=10)
            ax.set_ylabel("Força [kN]",color="#cdd6f4",fontsize=10)

    def _update_filter_options(self):
        mps   = sorted(set(filter(None, (_extract_mp(e.filepath)   for e in self.entries))))
        years = sorted(set(filter(None, (_extract_year(e.filepath) for e in self.entries))))
        self._cb_mp["values"]   = ["Todos"] + mps
        self._cb_year["values"] = ["Todos"] + years
        if self._filter_mp.get() not in ["Todos"] + mps:
            self._filter_mp.set("Todos")
        if self._filter_year.get() not in ["Todos"] + years:
            self._filter_year.set("Todos")

    def _filtered_entries(self):
        mp_f   = self._filter_mp.get()
        year_f = self._filter_year.get()
        return [e for e in self.entries
                if (mp_f   == "Todos" or _extract_mp(e.filepath)   == mp_f)
                and (year_f == "Todos" or _extract_year(e.filepath) == year_f)]

    def _refresh_list(self):
        self._update_filter_options()
        self._shown_entries = self._filtered_entries()
        self._lb.delete(0, "end")
        for e in self._shown_entries:
            icon  = "✔" if e.classification == "OK" else "✘"
            color = _C_OK if e.classification == "OK" else _C_NOK
            self._lb.insert("end", f" {icon}  {e.label}")
            self._lb.itemconfig("end", fg=color)
        n_ok  = sum(1 for e in self._shown_entries if e.classification == "OK")
        n_nok = sum(1 for e in self._shown_entries if e.classification == "NOK")
        total = len(self.entries)
        shown = len(self._shown_entries)
        filt  = f" (de {total})" if shown != total else ""
        self._status.set(f"{shown}{filt} arquivo(s) — {n_ok} OK / {n_nok} NOK")

    # ── ações ─────────────────────────────────────────────────────────────────
    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Selecionar arquivos XML",
            filetypes=[("XML files","*.xml"),("All files","*.*")])
        added = 0
        for path in paths:
            if any(e.filepath == path for e in self.entries):
                continue
            try:
                self.entries.append(_CurveEntry(path, _xml_auto_classify(path)))
                added += 1
            except Exception as err:
                messagebox.showerror("Erro ao carregar",
                                     f"{os.path.basename(path)}:\n{err}")
        if added:
            self._refresh_list(); self._plot()

    def _remove_selected(self):
        sel = self._lb.curselection()
        if not sel: return
        entry = self._shown_entries[sel[0]]
        self.entries.remove(entry)
        self._detail.set("")
        self._refresh_list(); self._plot()

    def _clear_all(self):
        if not self.entries: return
        if messagebox.askyesno("Limpar","Remover todos os arquivos?"):
            self.entries.clear()
            self._detail.set("")
            self._refresh_list()
            for ax in self._axes: ax.cla()
            self._style_axes()
            self._fig.tight_layout(pad=2.5)
            self._canvas.draw()

    def _rename_label(self):
        sel = self._lb.curselection()
        if not sel:
            messagebox.showinfo("Renomear","Selecione um arquivo na lista primeiro.")
            return
        idx = sel[0]
        win = tk.Toplevel(self)
        win.title("Renomear"); win.configure(bg=_C_PANEL)
        win.geometry("340x120"); win.resizable(False,False)
        tk.Label(win,text="Novo label:",bg=_C_PANEL,fg="#cdd6f4",
                 font=("Segoe UI",10)).pack(pady=(14,4))
        ent = tk.Entry(win,font=("Segoe UI",10),bg=_C_BTN,
                       fg="#cdd6f4",insertbackground="#cdd6f4",relief="flat")
        ent.insert(0,self._shown_entries[idx].label)
        ent.pack(padx=20,fill="x"); ent.focus()
        def apply(e=None):
            v = ent.get().strip()
            if v: self._shown_entries[idx].label = v
            self._refresh_list(); win.destroy()
        ent.bind("<Return>",apply)
        self._btn(win,"Confirmar",apply,color=_C_SEL,fg="#000").pack(pady=8)

    def _set_class(self, cls):
        sel = self._lb.curselection()
        if not sel:
            messagebox.showinfo("Classificar","Selecione um arquivo na lista primeiro.")
            return
        self._shown_entries[sel[0]].classification = cls
        self._refresh_list(); self._plot()

    def _on_select(self, _=None):
        sel = self._lb.curselection()
        if not sel: return
        e = self._shown_entries[sel[0]]; m = e.meta
        self._detail.set(
            f"Classe   : {e.classification}\n"
            f"Programa : {m.get('program','')}\n"
            f"Data/Hora: {m.get('date','')} {m.get('time','')}\n"
            f"Ciclo    : {m.get('cycle','')}\n"
            f"Pontos   : {len(e.x)}\n"
            f"Curso max: {max(e.x):.2f} mm\n"
            f"Força max: {max(e.y):.3f} kN")

    def _plot(self):
        shown    = self._shown_entries if self._shown_entries else self._filtered_entries()
        ok_list  = [e for e in shown if e.classification == "OK"]
        nok_list = [e for e in shown if e.classification == "NOK"]
        for ax in self._axes: ax.cla()
        self._style_axes()

        max_val = self._max_var.get()
        max_n = None if max_val == "Todas" else int(max_val)
        show_leg = self._legend_var.get()

        def draw_group(ax, entries, shades, title, color):
            n_total  = len(entries)
            visible  = entries[:max_n] if max_n is not None else entries
            hidden   = n_total - len(visible)
            suffix   = f" (+{hidden} oculta{'s' if hidden!=1 else ''})" if hidden else ""
            ax.set_title(f"{title}  ({n_total} curva{'s' if n_total!=1 else ''}){suffix}",
                         color=color, fontsize=13, fontweight="bold", pad=10)
            for i, e in enumerate(visible):
                ax.plot(e.x, e.y, color=shades[i % len(shades)],
                        linewidth=1.5, alpha=0.85, label=e.label)
            if visible and show_leg:
                ax.legend(loc="upper left", fontsize=8,
                          facecolor="#2a2a3e", edgecolor="#45475a",
                          labelcolor="#cdd6f4", framealpha=0.9)

        draw_group(self._axes[0], ok_list,  _OK_SH,  "OK",  _C_OK)
        draw_group(self._axes[1], nok_list, _NOK_SH, "NOK", _C_NOK)

        import numpy as np
        all_x = [x for e in shown for x in e.x]
        if all_x:
            ticks = np.arange(int(min(all_x)//5)*5,
                              int(max(all_x)//5)*5+10, 5)
            for ax in self._axes:
                ax.set_xticks(ticks)
                ax.tick_params(axis="x",labelsize=9,rotation=0)

        try:
            wx0=float(self._wx0.get()); wx1=float(self._wx1.get())
            wy0=float(self._wy0.get()); wy1=float(self._wy1.get())
            for ax in self._axes:
                ax.add_patch(mpatches.Rectangle(
                    (wx0,wy0),wx1-wx0,wy1-wy0,
                    linewidth=1.8,edgecolor="#f1c40f",
                    facecolor="#f1c40f",alpha=0.08,zorder=5))
                ax.plot([wx0,wx1,wx1,wx0,wx0],[wy0,wy0,wy1,wy1,wy0],
                        color="#f1c40f",linewidth=1.8,zorder=6)
                ax.axhline(wy0,color="#f1c40f",lw=0.6,ls=":",alpha=0.5,zorder=4)
                ax.axhline(wy1,color="#f1c40f",lw=0.6,ls=":",alpha=0.5,zorder=4)
                ax.text(wx0-0.5,wy0,f"{wy0:.2f} kN",color="#f1c40f",
                        fontsize=8,va="center",ha="right",zorder=7)
                ax.text(wx0-0.5,wy1,f"{wy1:.2f} kN",color="#f1c40f",
                        fontsize=8,va="center",ha="right",zorder=7)
        except (ValueError,AttributeError):
            pass

        self._fig.tight_layout(pad=2.5)
        self._canvas.draw()
        self._status.set(f"{len(self.entries)} curva(s)  —  "
                         f"{len(ok_list)} OK / {len(nok_list)} NOK")

    def _save_plot(self):
        if not self.entries:
            messagebox.showinfo("Salvar","Nenhuma curva carregada."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile="force_curves_comparison.png",
            filetypes=[("PNG","*.png"),("PDF","*.pdf"),("SVG","*.svg")])
        if path:
            self._fig.savefig(path,dpi=200,bbox_inches="tight",
                              facecolor=self._fig.get_facecolor())
            self._status.set(f"Salvo: {os.path.basename(path)}")


# ─────────────────────────────────────────────────────────────────────────────
# Modulo 4 — Golden Curve Analyzer
# ─────────────────────────────────────────────────────────────────────────────

import csv, xml.etree.ElementTree as ET
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

try:
    from reportlab.platypus import HRFlowable
    _HAS_REPORTLAB = True
except ImportError:
    _HAS_REPORTLAB = False

N_INTERP = 500
POLY_MAX  = 12

_C_OK    = "#2ecc71"
_C_NOK   = "#e74c3c"
_C_PANEL = "#1a2230"
_C_BTN   = "#1e2d3d"
_C_SEL   = "#00e5ff"
_C_DIM   = "#3a6070"


def _parse_xml(filepath):
    """Extrai vetores X, Y de arquivo XML de prensa (Kistler/Sinpac)."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    xs, ys = [], []
    for pt in root.findall(".//Point"):
        x_el = pt.find("X-ABSOLUTE-")
        if x_el is None: x_el = pt.find("X_-ABSOLUTE-")
        if x_el is None: x_el = pt.find("X-Absolute")
        if x_el is None: x_el = pt.find("X")
        if x_el is None:
            for child in pt:
                if child.tag.upper().startswith("X") and child.get("Value") is not None:
                    try:
                        float(child.get("Value").replace(",", "."))
                        x_el = child
                        break
                    except (ValueError, AttributeError):
                        pass
        y_el = pt.find("Y")
        if y_el is None: y_el = pt.find("y")
        if x_el is not None and y_el is not None:
            try:
                xs.append(float(x_el.get("Value", "").replace(",", ".")))
                ys.append(float(y_el.get("Value", "").replace(",", ".")))
            except (ValueError, AttributeError):
                pass
    if not xs:
        raise ValueError(f"Nenhum ponto valido em {os.path.basename(filepath)}")
    return np.array(xs), np.array(ys)


def _parse_csv(filepath):
    """
    Extrai X, Y de CSV. Aceita virgula, ponto-e-virgula ou tabulacao
    como separador, e ponto ou virgula como decimal.
    """
    xs, ys = [], []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        raw = f.read(4096)
    sep = ","
    for s in [";", "\t", ","]:
        if raw.count(s) > raw.count(sep):
            sep = s
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            if len(row) < 2:
                continue
            try:
                x_str = row[0].strip().replace(",", ".") if sep != "," else row[0].strip()
                y_str = row[1].strip().replace(",", ".") if sep != "," else row[1].strip()
                xs.append(float(x_str))
                ys.append(float(y_str))
            except ValueError:
                continue
    if len(xs) < 2:
        raise ValueError(f"Menos de 2 pontos validos em {os.path.basename(filepath)}")
    return np.array(xs), np.array(ys)


def parse_curve_file(filepath):
    """Dispatcher: escolhe parser pelo tipo de arquivo."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".xml":
        return _parse_xml(filepath)
    elif ext == ".csv":
        return _parse_csv(filepath)
    else:
        raise ValueError(f"Formato nao suportado: {ext}")


class GoldenCurveAnalyzer:
    """
    Recebe lista de pares (x_arr, y_arr) de curvas OK e calcula:
    curva media, banda de confianca, ajuste polinomial/spline e score de anomalia.
    """

    def __init__(self, curves: list[tuple[np.ndarray, np.ndarray]],
                 n_interp: int = N_INTERP,
                 smooth_sigma: float = 2.0):
        if len(curves) < 3:
            raise ValueError("Minimo de 3 curvas para analise.")
        self.n_curves  = len(curves)
        self.n_interp  = n_interp
        self.smooth    = smooth_sigma
        self._raw      = curves
        self._compute()

    def _compute(self):
        x_min = max(c[0].min() for c in self._raw)
        x_max = min(c[0].max() for c in self._raw)
        if x_min >= x_max:
            raise ValueError(
                "As curvas nao se sobrepoem no eixo X. "
                "Verifique se todas as curvas cobrem a mesma faixa de curso.")
        self.x_grid = np.linspace(x_min, x_max, self.n_interp)
        mat = []
        for x, y in self._raw:
            idx  = np.argsort(x)
            xu, ui = np.unique(x[idx], return_index=True)
            yu = y[idx][ui]
            if len(xu) < 2:
                continue
            f = interp1d(xu, yu, kind="linear",
                         bounds_error=False, fill_value="extrapolate")
            mat.append(f(self.x_grid))
        self.matrix   = np.array(mat)
        self.n_valid  = len(mat)
        self.mean     = np.mean(self.matrix, axis=0)
        self.median   = np.median(self.matrix, axis=0)
        self.std      = np.std(self.matrix, axis=0)
        self.p05      = np.percentile(self.matrix,  5, axis=0)
        self.p95      = np.percentile(self.matrix, 95, axis=0)
        self.p25      = np.percentile(self.matrix, 25, axis=0)
        self.p75      = np.percentile(self.matrix, 75, axis=0)
        self.mean_smooth = (gaussian_filter1d(self.mean, sigma=self.smooth)
                            if self.smooth > 0 else self.mean.copy())
        self.f_max_per_curve = self.matrix.max(axis=1)
        self.f_min_per_curve = self.matrix.min(axis=1)

    def fit_polynomial(self, degree: int = 6) -> dict:
        degree = max(1, min(degree, POLY_MAX))
        coeffs = np.polyfit(self.x_grid, self.mean_smooth, degree)
        poly   = np.poly1d(coeffs)
        y_fit  = poly(self.x_grid)
        resid  = self.mean_smooth - y_fit
        r2     = 1.0 - np.var(resid) / np.var(self.mean_smooth)
        return dict(coeffs=coeffs, poly=poly, y_fit=y_fit, r2=r2, degree=degree)

    def fit_spline(self, smoothing: float | None = None) -> dict:
        from scipy.interpolate import UnivariateSpline
        s = smoothing if smoothing is not None else len(self.x_grid) * 0.5
        spl   = UnivariateSpline(self.x_grid, self.mean_smooth, s=s, k=3)
        y_fit = spl(self.x_grid)
        resid = self.mean_smooth - y_fit
        r2    = 1.0 - np.var(resid) / np.var(self.mean_smooth)
        return dict(spl=spl, y_fit=y_fit, r2=r2)

    def anomaly_score(self, x_new: np.ndarray, y_new: np.ndarray,
                      sigma_thr: float = 3.0) -> dict:
        idx  = np.argsort(x_new)
        xu, ui = np.unique(x_new[idx], return_index=True)
        yu = y_new[idx][ui]
        mask = (self.x_grid >= xu.min()) & (self.x_grid <= xu.max())
        if mask.sum() < 10:
            return dict(score=None, outside_frac=None, msg="Fora da faixa de X")
        f   = interp1d(xu, yu, kind="linear",
                       bounds_error=False, fill_value="extrapolate")
        y_i = f(self.x_grid[mask])
        mu  = self.mean[mask]; sg = self.std[mask]
        sg  = np.where(sg < 1e-9, 1e-9, sg)
        z   = np.abs(y_i - mu) / sg
        outside = (z > sigma_thr).mean()
        score   = float(np.clip(z.mean() / sigma_thr * 50, 0, 100))
        verdict = "OK" if outside < 0.05 and score < 40 else "NOK"
        return dict(score=score, outside_frac=outside,
                    verdict=verdict, z=z, mask=mask)


class AbaGoldenCurve(tk.Frame):
    """
    Aba 4 — Golden Curve Analyzer.
    Adicione ao notebook: nb.add(AbaGoldenCurve(nb), text="  Golden Curve  ")
    """

    def __init__(self, parent, app_ref=None, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._app     = app_ref
        self._files:  list[str]  = []
        self._curves: list       = []
        self._analyzer: GoldenCurveAnalyzer | None = None
        self._poly_result: dict  | None = None
        self._spl_result:  dict  | None = None
        self._test_curves: list  = []
        self._build()

    def _btn(self, parent, text, cmd, fg=ACCENT, bg=BG2):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg, font=FONT_MONO, relief="flat",
                         padx=10, pady=5, cursor="hand2",
                         activebackground=BG, activeforeground=fg)

    def _build(self):
        root_frame = tk.Frame(self, bg=BG)
        root_frame.pack(fill="both", expand=True)

        # ── painel esquerdo ───────────────────────────────────────────────
        left = tk.Frame(root_frame, bg=_C_PANEL, width=310)
        left.pack(side="left", fill="y", padx=(8, 0), pady=8)
        left.pack_propagate(False)

        tk.Label(left, text="GOLDEN CURVE ANALYZER",
                 bg=_C_PANEL, fg=ACCENT, font=("Courier", 10, "bold"),
                 pady=10).pack()
        tk.Label(left, text="Curva teorica a partir de N curvas OK reais",
                 bg=_C_PANEL, fg=FG_DIM, font=("Helvetica", 8)).pack(pady=(0, 8))
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=8)

        tk.Label(left, text="1. CURVAS DE REFERENCIA (OK)",
                 bg=_C_PANEL, fg=GOLD, font=FONT_SMALL, pady=8).pack(anchor="w", padx=10)
        self._btn(left, "➕  Adicionar XML / CSV",
                  self._add_ok_files, fg=GOLD).pack(fill="x", padx=8, pady=2)
        self._btn(left, "⬆  Importar OK do Comparador",
                  self._add_from_comparator, fg=ACCENT).pack(fill="x", padx=8, pady=2)
        self._btn(left, "🗑  Limpar curvas OK",
                  self._clear_ok, fg=FG_DIM).pack(fill="x", padx=8, pady=2)
        self._lbl_n = tk.Label(left, text="0 curvas carregadas",
                               bg=_C_PANEL, fg=FG_DIM, font=FONT_SMALL)
        self._lbl_n.pack(anchor="w", padx=12, pady=(2, 4))

        # ── Filtros MP / Ano ─────────────────────────────────────────────────
        gf = tk.Frame(left, bg=_C_PANEL)
        gf.pack(fill="x", padx=8, pady=(0, 2))
        tk.Label(gf, text="Ponto:", bg=_C_PANEL, fg=FG_DIM,
                 font=FONT_SMALL).grid(row=0, column=0, sticky="w", pady=1)
        self._gc_filter_mp = tk.StringVar(value="Todos")
        self._gc_cb_mp = ttk.Combobox(gf, textvariable=self._gc_filter_mp,
                                      values=["Todos"], state="readonly",
                                      font=FONT_SMALL, width=10)
        self._gc_cb_mp.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=1)
        tk.Label(gf, text="Ano:", bg=_C_PANEL, fg=FG_DIM,
                 font=FONT_SMALL).grid(row=1, column=0, sticky="w", pady=1)
        self._gc_filter_year = tk.StringVar(value="Todos")
        self._gc_cb_year = ttk.Combobox(gf, textvariable=self._gc_filter_year,
                                        values=["Todos"], state="readonly",
                                        font=FONT_SMALL, width=10)
        self._gc_cb_year.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=1)
        gf.columnconfigure(1, weight=1)
        self._gc_cb_mp.bind("<<ComboboxSelected>>",   lambda _: self._refresh_list())
        self._gc_cb_year.bind("<<ComboboxSelected>>", lambda _: self._refresh_list())

        lb_f = tk.Frame(left, bg=_C_PANEL)
        lb_f.pack(fill="x", padx=8, pady=(0, 4))
        self._lb = tk.Listbox(lb_f, bg=BG3, fg=FG, font=("Courier", 7),
                              height=7, relief="flat", bd=0,
                              selectbackground=ACCENT, selectforeground=BG,
                              activestyle="none", exportselection=False)
        self._lb.pack(side="left", fill="x", expand=True)
        sb2 = ttk.Scrollbar(lb_f, orient="vertical", command=self._lb.yview)
        sb2.pack(side="right", fill="y")
        self._lb.config(yscrollcommand=sb2.set)

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=8, pady=4)

        tk.Label(left, text="2. PARAMETROS DA ANALISE",
                 bg=_C_PANEL, fg=PURPLE, font=FONT_SMALL, pady=6).pack(anchor="w", padx=10)

        pg = tk.Frame(left, bg=_C_PANEL)
        pg.pack(fill="x", padx=10, pady=(0, 4))

        def prow(parent, label, default, width=6):
            r = tk.Frame(parent, bg=_C_PANEL); r.pack(fill="x", pady=2)
            tk.Label(r, text=label, bg=_C_PANEL, fg=FG_DIM, font=FONT_SMALL,
                     width=22, anchor="w").pack(side="left")
            v = tk.StringVar(value=str(default))
            tk.Entry(r, textvariable=v, bg=BG3, fg=ACCENT,
                     font=("Courier", 9, "bold"), insertbackground=ACCENT,
                     relief="flat", highlightthickness=1,
                     highlightbackground=BORDER, width=width).pack(side="left", ipady=2)
            return v

        self._v_npoly  = prow(pg, "Grau do polinomio",    6)
        self._v_sigma  = prow(pg, "Sigma anomalia (thr)", 3)
        self._v_smooth = prow(pg, "Suavizacao gaussiana", 2)
        self._v_npts   = prow(pg, "Pontos interpolacao",  500)

        ck = tk.Frame(left, bg=_C_PANEL); ck.pack(fill="x", padx=10, pady=4)
        self._show_raw  = tk.BooleanVar(value=True)
        self._show_band = tk.BooleanVar(value=True)
        self._show_poly = tk.BooleanVar(value=True)
        self._show_spl  = tk.BooleanVar(value=False)
        for var, label in [(self._show_raw,  "Mostrar curvas individuais"),
                           (self._show_band, "Banda de confianca"),
                           (self._show_poly, "Ajuste polinomial"),
                           (self._show_spl,  "Ajuste spline")]:
            tk.Checkbutton(ck, text=label, variable=var,
                           bg=_C_PANEL, fg=FG_DIM, selectcolor=BG3,
                           activebackground=_C_PANEL, activeforeground=ACCENT,
                           font=FONT_SMALL, command=self._replot
                           ).pack(anchor="w", pady=1)

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=8, pady=4)
        self._btn(left, "▶▶  GERAR GOLDEN CURVE",
                  self._analisar, fg=ACCENT, bg="#0a2030").pack(fill="x", padx=8, pady=(0, 4))
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=8, pady=4)

        tk.Label(left, text="3. DETECCAO DE ANOMALIA",
                 bg=_C_PANEL, fg=RED, font=FONT_SMALL, pady=6).pack(anchor="w", padx=10)
        self._btn(left, "➕  Carregar curva(s) para teste",
                  self._add_test_curves, fg=RED).pack(fill="x", padx=8, pady=2)
        self._lbl_test = tk.Label(left, text="0 curvas de teste",
                                  bg=_C_PANEL, fg=FG_DIM, font=FONT_SMALL)
        self._lbl_test.pack(anchor="w", padx=12)
        self._btn(left, "🔍  Avaliar anomalia",
                  self._avaliar_anomalia, fg=ORANGE).pack(fill="x", padx=8, pady=(4, 2))
        self._btn(left, "🗑  Limpar teste",
                  self._clear_test, fg=FG_DIM).pack(fill="x", padx=8, pady=2)
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=8, pady=4)

        self._btn(left, "💾  Exportar coeficientes CSV",
                  self._export_coeffs, fg=GREEN).pack(fill="x", padx=8, pady=2)
        self._btn(left, "📄  Exportar PDF",
                  self._export_pdf, fg=PURPLE).pack(fill="x", padx=8, pady=2)
        self._btn(left, "🖼  Salvar grafico PNG",
                  self._save_png, fg=FG_DIM).pack(fill="x", padx=8, pady=2)

        self._status = tk.StringVar(value="Aguardando curvas...")
        tk.Label(left, textvariable=self._status, bg=_C_PANEL, fg=FG_DIM,
                 font=FONT_SMALL, wraplength=290, justify="left",
                 pady=6).pack(padx=8, fill="x")

        # ── painel direito — graficos ─────────────────────────────────────
        right = tk.Frame(root_frame, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        nb_style = ttk.Style()
        nb_style.configure("Inner.TNotebook", background=BG, borderwidth=0)
        nb_style.configure("Inner.TNotebook.Tab", background=BG2, foreground=FG_DIM,
                           font=FONT_SMALL, padding=[12, 5])
        nb_style.map("Inner.TNotebook.Tab",
                     background=[("selected", BG)],
                     foreground=[("selected", ACCENT)])

        self._nb_inner = ttk.Notebook(right, style="Inner.TNotebook")
        self._nb_inner.pack(fill="both", expand=True)

        tab_gc = tk.Frame(self._nb_inner, bg=BG)
        self._nb_inner.add(tab_gc, text="  Golden Curve  ")
        self._fig, self._ax = plt.subplots(figsize=(11, 5.5), facecolor=BG)
        self._style_ax(self._ax, "Golden Curve  —  F(x) media + banda de confianca")
        self._cv_gc = FigureCanvasTkAgg(self._fig, master=tab_gc)
        self._cv_gc.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(self._cv_gc, tab_gc).update()

        tab_an = tk.Frame(self._nb_inner, bg=BG)
        self._nb_inner.add(tab_an, text="  Anomalia  ")
        self._fig_an, self._ax_an = plt.subplots(figsize=(11, 5.5), facecolor=BG)
        self._style_ax(self._ax_an, "Deteccao de Anomalia  —  Curva nova vs Golden Curve")
        self._cv_an = FigureCanvasTkAgg(self._fig_an, master=tab_an)
        self._cv_an.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(self._cv_an, tab_an).update()

        tab_st = tk.Frame(self._nb_inner, bg=BG)
        self._nb_inner.add(tab_st, text="  Estatisticas  ")
        self._fig_st, self._axes_st = plt.subplots(1, 3, figsize=(13, 4.5), facecolor=BG)
        self._fig_st.tight_layout(pad=2.5)
        for ax in self._axes_st:
            self._style_ax(ax, "")
        self._cv_st = FigureCanvasTkAgg(self._fig_st, master=tab_st)
        self._cv_st.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(self._cv_st, tab_st).update()

        self._placeholder_all()

    def _style_ax(self, ax, title=""):
        ax.set_facecolor(BG3)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM, labelsize=8)
        if title:
            ax.set_title(title, color=FG_DIM, fontsize=9, pad=6)

    def _placeholder_all(self):
        for ax, cv in [(self._ax, self._cv_gc), (self._ax_an, self._cv_an)]:
            ax.cla(); self._style_ax(ax)
            ax.text(0.5, 0.5,
                    "Carregue curvas OK e clique em  ▶▶  GERAR GOLDEN CURVE",
                    transform=ax.transAxes,
                    ha="center", va="center", color="#2a3a44", fontsize=10)
            cv.draw()
        for ax in self._axes_st:
            ax.cla(); self._style_ax(ax)
            ax.text(0.5, 0.5, "sem dados", transform=ax.transAxes,
                    ha="center", va="center", color="#2a3a44", fontsize=9)
        self._cv_st.draw()

    def _add_ok_files(self):
        paths = filedialog.askopenfilenames(
            title="Selecionar curvas OK (XML ou CSV)",
            filetypes=[("Suportados", "*.xml *.csv"), ("XML Prensa", "*.xml"),
                       ("CSV", "*.csv"), ("Todos", "*.*")])
        if not paths:
            return
        errs, added, rejected_nok = [], 0, []
        for p in paths:
            if p in self._files:
                continue
            if _xml_auto_classify(p) == "NOK":
                rejected_nok.append(os.path.basename(p))
                continue
            try:
                x, y = parse_curve_file(p)
                self._files.append(p)
                self._curves.append((x, y))
                added += 1
            except Exception as e:
                errs.append(f"{os.path.basename(p)}: {e}")
        self._refresh_list()
        if rejected_nok:
            messagebox.showwarning(
                "Importacoes NOK recusadas",
                f"{len(rejected_nok)} arquivo(s) recusado(s) por classificacao NOK:\n" +
                "\n".join(rejected_nok[:15]) +
                (f"\n... +{len(rejected_nok)-15} outros" if len(rejected_nok) > 15 else ""))
        if errs:
            messagebox.showwarning("Avisos de importacao",
                                   "\n".join(errs[:10]) +
                                   (f"\n... +{len(errs)-10} erros" if len(errs) > 10 else ""))
        self._status.set(f"+{added} curvas adicionadas.  Total: {len(self._curves)}")

    def _clear_ok(self):
        self._files.clear(); self._curves.clear()
        self._analyzer = None; self._poly_result = None; self._spl_result = None
        self._lb.delete(0, "end")
        self._lbl_n.config(text="0 curvas carregadas")
        self._status.set("Curvas OK removidas.")
        self._placeholder_all()

    def _add_from_comparator(self):
        if self._app is None or not hasattr(self._app, "_aba_xml"):
            messagebox.showwarning("Atencao",
                "Modulo de Comparacao nao disponivel."); return
        ok_entries = [e for e in self._app._aba_xml.entries
                      if e.classification == "OK"]
        if not ok_entries:
            messagebox.showinfo("Importar do Comparador",
                "Nenhuma curva OK carregada no Comparador de Curvas XML."); return
        added = skipped = 0
        for e in ok_entries:
            if e.filepath in self._files:
                skipped += 1
                continue
            self._files.append(e.filepath)
            self._curves.append((np.array(e.x), np.array(e.y)))
            added += 1
        self._refresh_list()
        msg = f"+{added} curva(s) OK importada(s) do Comparador.  Total: {len(self._curves)}"
        if skipped:
            msg += f"  ({skipped} ja existiam)"
        self._status.set(msg)

    def _add_test_curves(self):
        paths = filedialog.askopenfilenames(
            title="Curvas para teste de anomalia (XML ou CSV)",
            filetypes=[("Suportados", "*.xml *.csv"), ("Todos", "*.*")])
        if not paths:
            return
        errs, added = [], 0
        for p in paths:
            try:
                x, y = parse_curve_file(p)
                self._test_curves.append((x, y, os.path.basename(p)))
                added += 1
            except Exception as e:
                errs.append(f"{os.path.basename(p)}: {e}")
        self._lbl_test.config(text=f"{len(self._test_curves)} curvas de teste")
        if errs:
            messagebox.showwarning("Avisos", "\n".join(errs[:5]))

    def _clear_test(self):
        self._test_curves.clear()
        self._lbl_test.config(text="0 curvas de teste")
        self._ax_an.cla(); self._style_ax(self._ax_an)
        self._ax_an.text(0.5, 0.5, "sem dados de teste",
                         transform=self._ax_an.transAxes,
                         ha="center", va="center", color="#2a3a44", fontsize=9)
        self._cv_an.draw()

    def _gc_update_filter_options(self):
        mps   = sorted(set(filter(None, (_extract_mp(p)   for p in self._files))))
        years = sorted(set(filter(None, (_extract_year(p) for p in self._files))))
        self._gc_cb_mp["values"]   = ["Todos"] + mps
        self._gc_cb_year["values"] = ["Todos"] + years
        if self._gc_filter_mp.get() not in ["Todos"] + mps:
            self._gc_filter_mp.set("Todos")
        if self._gc_filter_year.get() not in ["Todos"] + years:
            self._gc_filter_year.set("Todos")

    def _gc_filtered_indices(self):
        mp_f   = self._gc_filter_mp.get()
        year_f = self._gc_filter_year.get()
        return [i for i, p in enumerate(self._files)
                if (mp_f   == "Todos" or _extract_mp(p)   == mp_f)
                and (year_f == "Todos" or _extract_year(p) == year_f)]

    def _refresh_list(self):
        self._gc_update_filter_options()
        idxs = self._gc_filtered_indices()
        self._lb.delete(0, "end")
        for i in idxs:
            p = self._files[i]
            ext = os.path.splitext(p)[1].upper()
            self._lb.insert("end", f" [{ext}]  {os.path.basename(p)}")
        total = len(self._files)
        shown = len(idxs)
        filt  = f" (de {total})" if shown != total else ""
        self._lbl_n.config(text=f"{shown}{filt} curvas carregadas")

    def _get_params(self):
        def _f(v, default):
            try:    return float(v.get().replace(",", "."))
            except: return default
        return {
            "degree":   int(_f(self._v_npoly,  6)),
            "sigma":    _f(self._v_sigma,  3.0),
            "smooth":   _f(self._v_smooth, 2.0),
            "n_interp": int(_f(self._v_npts, 500)),
        }

    def _analisar(self):
        idxs = self._gc_filtered_indices()
        curves_to_use = [self._curves[i] for i in idxs]
        if len(curves_to_use) < 3:
            messagebox.showwarning("Atencao",
                "Carregue pelo menos 3 curvas OK (visíveis no filtro atual) para gerar a Golden Curve."); return
        p = self._get_params()
        self._status.set("Processando..."); self.update()
        try:
            self._analyzer = GoldenCurveAnalyzer(
                curves_to_use, n_interp=p["n_interp"], smooth_sigma=p["smooth"])
            self._poly_result = self._analyzer.fit_polynomial(degree=p["degree"])
            self._spl_result  = self._analyzer.fit_spline()
            self._replot()
            self._plot_stats()
            az = self._analyzer
            self._status.set(
                f"OK  |  {az.n_valid} curvas  |  "
                f"X: [{az.x_grid[0]:.1f}, {az.x_grid[-1]:.1f}] mm  |  "
                f"F_media_max: {az.mean.max():.3f} kN  |  "
                f"R2_poly: {self._poly_result['r2']:.4f}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self._status.set(f"Erro: {e}")

    def _replot(self):
        if self._analyzer is None:
            return
        az = self._analyzer; p = self._get_params()
        ax = self._ax; ax.cla(); self._style_ax(ax)
        x  = az.x_grid

        if self._show_raw.get():
            n_show  = min(az.n_valid, 200)
            palette = plt.cm.Blues(np.linspace(0.25, 0.6, n_show))
            step    = max(1, az.n_valid // n_show)
            for i, row in enumerate(az.matrix[::step][:n_show]):
                ax.plot(x, row, color=palette[i % n_show], lw=0.5, alpha=0.35)

        if self._show_band.get():
            ax.fill_between(x, az.p05, az.p95, color=ACCENT, alpha=0.10, label="P5–P95")
            ax.fill_between(x, az.p25, az.p75, color=ACCENT, alpha=0.18, label="IQR (P25–P75)")
            ax.fill_between(x, az.mean - az.std, az.mean + az.std,
                            color=GOLD, alpha=0.18, label="mean ± 1σ")

        ax.plot(x, az.mean_smooth, color=GOLD, lw=2.5, zorder=20,
                label=f"Media suavizada (n={az.n_valid})")

        if self._show_poly.get() and self._poly_result:
            pr = self._poly_result
            ax.plot(x, pr["y_fit"], color=PURPLE, lw=1.8, ls="--", zorder=18,
                    label=f"Polinomio grau {pr['degree']}  R²={pr['r2']:.4f}")

        if self._show_spl.get() and self._spl_result:
            sr = self._spl_result
            ax.plot(x, sr["y_fit"], color=GREEN, lw=1.8, ls=":", zorder=17,
                    label=f"Spline cubico  R²={sr['r2']:.4f}")

        ax.set_xlabel("Curso [mm]", color=FG_DIM, fontsize=9)
        ax.set_ylabel("Forca [kN]", color=FG_DIM, fontsize=9)
        ax.set_title(
            f"Golden Curve  |  n={az.n_valid} curvas OK  |  "
            f"F_max_medio={az.mean.max():.3f} kN  |  σ_max={az.std.max():.3f} kN",
            color=FG_DIM, fontsize=9, pad=6)
        ax.legend(fontsize=8, facecolor=BG2, edgecolor=BORDER,
                  labelcolor=FG, loc="upper left")
        ax.grid(True, ls="--", alpha=0.2, color=FG_DIM, lw=0.5)
        self._fig.tight_layout(pad=1.8)
        self._cv_gc.draw()

    def _plot_stats(self):
        if self._analyzer is None:
            return
        az = self._analyzer
        for ax in self._axes_st:
            ax.cla(); self._style_ax(ax)

        ax0 = self._axes_st[0]
        ax0.hist(az.f_max_per_curve, bins=min(30, az.n_valid),
                 color=GOLD, alpha=0.8, edgecolor=BG3, lw=0.5)
        ax0.axvline(az.f_max_per_curve.mean(), color=ACCENT, lw=1.5, ls="--",
                    label=f"media={az.f_max_per_curve.mean():.3f}")
        ax0.set_title("Distribuicao de F_max", color=FG_DIM, fontsize=8, pad=4)
        ax0.set_xlabel("F_max [kN]", color=FG_DIM, fontsize=7)
        ax0.legend(fontsize=7, facecolor=BG2, edgecolor=BORDER, labelcolor=FG)

        ax1 = self._axes_st[1]
        ax1.plot(az.x_grid, az.std, color=ORANGE, lw=1.5)
        ax1.fill_between(az.x_grid, 0, az.std, color=ORANGE, alpha=0.25)
        ax1.set_title("Desvio padrao F(x)", color=FG_DIM, fontsize=8, pad=4)
        ax1.set_xlabel("Curso [mm]", color=FG_DIM, fontsize=7)
        ax1.set_ylabel("σ [kN]", color=FG_DIM, fontsize=7)

        ax2 = self._axes_st[2]
        if self._poly_result:
            resid = az.mean_smooth - self._poly_result["y_fit"]
            ax2.plot(az.x_grid, resid, color=PURPLE, lw=1.2)
            ax2.axhline(0, color=FG_DIM, lw=0.8, ls="--", alpha=0.5)
            ax2.fill_between(az.x_grid, resid, 0, color=PURPLE, alpha=0.2)
            ax2.set_title(
                f"Residuos do polinomio  R²={self._poly_result['r2']:.5f}",
                color=FG_DIM, fontsize=8, pad=4)
            ax2.set_xlabel("Curso [mm]", color=FG_DIM, fontsize=7)
            ax2.set_ylabel("Residuo [kN]", color=FG_DIM, fontsize=7)

        for ax in self._axes_st:
            ax.grid(True, ls="--", alpha=0.2, color=FG_DIM, lw=0.5)
            for sp in ax.spines.values():
                sp.set_edgecolor(BORDER)
            ax.tick_params(colors=FG_DIM, labelsize=7)
        self._fig_st.tight_layout(pad=2.0)
        self._cv_st.draw()

    def _avaliar_anomalia(self):
        if self._analyzer is None:
            messagebox.showwarning("Atencao", "Gere a Golden Curve primeiro."); return
        if not self._test_curves:
            messagebox.showwarning("Atencao", "Carregue pelo menos uma curva de teste."); return
        p  = self._get_params()
        az = self._analyzer
        ax = self._ax_an; ax.cla(); self._style_ax(ax)
        x  = az.x_grid

        ax.fill_between(x, az.mean - az.std, az.mean + az.std,
                        color=GOLD, alpha=0.15, label="mean ± 1σ (golden)")
        ax.fill_between(x, az.p05, az.p95,
                        color=ACCENT, alpha=0.08, label="P5–P95 (golden)")
        ax.plot(x, az.mean_smooth, color=GOLD, lw=2.0, zorder=10, label="Golden mean")

        ok_pal  = ["#2ecc71", "#27ae60", "#1abc9c", "#52be80"]
        nok_pal = ["#e74c3c", "#c0392b", "#e67e22", "#d35400"]
        ok_i = nok_i = 0

        resultados = []
        for xt, yt, name in self._test_curves:
            res     = az.anomaly_score(xt, yt, sigma_thr=p["sigma"])
            verdict = res.get("verdict", "N/A")
            score   = res.get("score")
            out_f   = res.get("outside_frac")
            resultados.append((name, verdict, score, out_f))

            idx = np.argsort(xt)
            xu, ui = np.unique(xt[idx], return_index=True)
            yu   = yt[idx][ui]
            mask = (x >= xu.min()) & (x <= xu.max())
            f_i  = interp1d(xu, yu, bounds_error=False, fill_value="extrapolate")
            y_i  = f_i(x[mask])

            if verdict == "OK":
                cor = ok_pal[ok_i % len(ok_pal)]; ok_i += 1
            else:
                cor = nok_pal[nok_i % len(nok_pal)]; nok_i += 1

            lbl = (f"{'✔' if verdict=='OK' else '✘'} {name[:22]}  score={score:.1f}"
                   if score is not None else name)
            ax.plot(x[mask], y_i, color=cor, lw=1.8, alpha=0.9,
                    ls="-" if verdict == "OK" else "--", label=lbl, zorder=15)

        ax.set_xlabel("Curso [mm]", color=FG_DIM, fontsize=9)
        ax.set_ylabel("Forca [kN]", color=FG_DIM, fontsize=9)
        ax.set_title(
            f"Anomalia  |  σ_thr={p['sigma']}  |  "
            f"{sum(1 for _,v,_,_ in resultados if v=='OK')} OK  /  "
            f"{sum(1 for _,v,_,_ in resultados if v=='NOK')} NOK",
            color=FG_DIM, fontsize=9, pad=6)
        ax.legend(fontsize=7, facecolor=BG2, edgecolor=BORDER, labelcolor=FG,
                  loc="upper left", ncol=2)
        ax.grid(True, ls="--", alpha=0.2, color=FG_DIM, lw=0.5)
        self._fig_an.tight_layout(pad=1.8)
        self._cv_an.draw()
        self._nb_inner.select(1)

        linhas = [f"{'Arquivo':<35}  {'Verdict':<6}  {'Score':>6}  {'%fora':>6}"]
        linhas.append("-" * 60)
        for name, v, sc, of in resultados:
            sc_s = f"{sc:6.1f}" if sc is not None else "   N/A"
            of_s = f"{of*100:5.1f}%" if of is not None else "   N/A"
            linhas.append(f"{name[:35]:<35}  {v:<6}  {sc_s}  {of_s}")
        messagebox.showinfo("Resultado Anomalia", "\n".join(linhas))

    def _export_coeffs(self):
        if self._poly_result is None:
            messagebox.showwarning("Atencao", "Gere a Golden Curve primeiro."); return
        path = filedialog.asksaveasfilename(
            title="Salvar coeficientes CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")])
        if not path: return
        try:
            pr = self._poly_result; az = self._analyzer
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["# Golden Curve — Coeficientes Polinomiais"])
                w.writerow(["# Gerado em",
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
                w.writerow(["# N curvas",       az.n_valid])
                w.writerow(["# Grau polinomio", pr["degree"]])
                w.writerow(["# R2",             f"{pr['r2']:.6f}"])
                w.writerow(["# X_min [mm]",     f"{az.x_grid[0]:.4f}"])
                w.writerow(["# X_max [mm]",     f"{az.x_grid[-1]:.4f}"])
                w.writerow([])
                w.writerow(["Ordem (grau)", "Coeficiente"])
                for i, c in enumerate(pr["coeffs"]):
                    w.writerow([pr["degree"] - i, f"{c:.10e}"])
                w.writerow([])
                w.writerow(["# Tabela Golden Curve (X, F_media, F_std, P05, P95)"])
                w.writerow(["X_mm", "F_mean_kN", "F_std_kN",
                             "F_P05_kN", "F_P95_kN", "F_poly_kN"])
                for j in range(len(az.x_grid)):
                    w.writerow([f"{az.x_grid[j]:.4f}", f"{az.mean[j]:.5f}",
                                f"{az.std[j]:.5f}",  f"{az.p05[j]:.5f}",
                                f"{az.p95[j]:.5f}",  f"{pr['y_fit'][j]:.5f}"])
            messagebox.showinfo("Sucesso", f"Coeficientes salvos em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _save_png(self):
        if self._analyzer is None:
            messagebox.showwarning("Atencao", "Gere a Golden Curve primeiro."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")])
        if path:
            self._fig.savefig(path, dpi=200, bbox_inches="tight",
                              facecolor=self._fig.get_facecolor())
            self._status.set(f"Salvo: {os.path.basename(path)}")

    def _export_pdf(self):
        if not _HAS_REPORTLAB:
            messagebox.showerror("Erro",
                "ReportLab nao instalado.\npip install reportlab"); return
        if self._analyzer is None:
            messagebox.showwarning("Atencao", "Gere a Golden Curve primeiro."); return
        path = filedialog.asksaveasfilename(
            title="Salvar PDF", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")])
        if not path: return
        try:
            self._gerar_pdf(path)
            messagebox.showinfo("Sucesso", f"PDF salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro ao gerar PDF", str(e))

    def _gerar_pdf(self, path):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, Image as RLImage,
                                        HRFlowable)
        from reportlab.lib.enums import TA_CENTER

        az = self._analyzer; pr = self._poly_result
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        fig_p, axes_p = plt.subplots(1, 2, figsize=(12, 4.5), facecolor="white")
        x = az.x_grid

        axes_p[0].fill_between(x, az.p05, az.p95, color="#aaddff", alpha=0.5, label="P5–P95")
        axes_p[0].fill_between(x, az.mean - az.std, az.mean + az.std,
                                color="#ffcc44", alpha=0.4, label="mean ± 1σ")
        axes_p[0].plot(x, az.mean_smooth, color="#c8860a", lw=2.2,
                       label=f"Media (n={az.n_valid})")
        if pr:
            axes_p[0].plot(x, pr["y_fit"], color="#6600cc", lw=1.6, ls="--",
                           label=f"Poly grau {pr['degree']} R²={pr['r2']:.4f}")
        axes_p[0].set_title("Golden Curve", fontsize=10)
        axes_p[0].set_xlabel("Curso [mm]", fontsize=9)
        axes_p[0].set_ylabel("Forca [kN]", fontsize=9)
        axes_p[0].legend(fontsize=7); axes_p[0].grid(True, alpha=0.3)
        axes_p[0].tick_params(labelsize=8)

        axes_p[1].plot(x, az.std, color="#e67e22", lw=1.8)
        axes_p[1].fill_between(x, 0, az.std, color="#e67e22", alpha=0.25)
        axes_p[1].set_title("Desvio Padrao σ(x)", fontsize=10)
        axes_p[1].set_xlabel("Curso [mm]", fontsize=9)
        axes_p[1].set_ylabel("σ [kN]", fontsize=9)
        axes_p[1].grid(True, alpha=0.3); axes_p[1].tick_params(labelsize=8)

        buf = io.BytesIO()
        fig_p.tight_layout()
        fig_p.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
        buf.seek(0); plt.close(fig_p)

        doc = SimpleDocTemplate(path, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=18*mm, bottomMargin=18*mm)
        PW = A4[0] - 40*mm

        def s(name, **kw):
            return ParagraphStyle(name, fontName="Helvetica",
                                  fontSize=9, textColor=colors.black, **kw)

        s_title  = s("t", fontSize=14, fontName="Helvetica-Bold",
                     textColor=colors.HexColor("#003366"), spaceAfter=4)
        s_sec    = s("s", fontSize=10, fontName="Helvetica-Bold",
                     textColor=colors.HexColor("#003366"), spaceBefore=10, spaceAfter=4)
        s_author = s("a", fontName="Helvetica-Bold",
                     textColor=colors.HexColor("#003366"), spaceAfter=2)
        s_foot   = s("f", fontSize=7, textColor=colors.HexColor("#888888"),
                     alignment=TA_CENTER)

        def tbl(data, cw):
            t = Table(data, colWidths=cw)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",   (0, 0), (-1, -1), 8),
                ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
                ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.HexColor("#f0f4f8"), colors.white]),
                ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            return t

        story = [
            Paragraph("RELATORIO — GOLDEN CURVE ANALYZER", s_title),
            Paragraph("Author: Bruno Bernardinetti - Stellantis", s_author),
            HRFlowable(width="100%", thickness=2,
                       color=colors.HexColor("#003366"), spaceAfter=6),
            Paragraph("Sumario da Analise", s_sec),
            tbl([["Parametro", "Valor"],
                 ["N curvas OK",       str(az.n_valid)],
                 ["X_min [mm]",        f"{az.x_grid[0]:.3f}"],
                 ["X_max [mm]",        f"{az.x_grid[-1]:.3f}"],
                 ["F_max medio [kN]",  f"{az.mean.max():.4f}"],
                 ["F_max std   [kN]",  f"{az.std.max():.4f}"],
                 ["Grau polinomio",    str(pr["degree"]) if pr else "N/A"],
                 ["R² polinomio",      f"{pr['r2']:.6f}" if pr else "N/A"],
                 ["Gerado em",         now],
                ], [PW*0.55, PW*0.45]),
            Spacer(1, 6),
            Paragraph("Coeficientes do Polinomio  F(x) = Σ aᵢ·xⁱ", s_sec),
        ]

        if pr:
            rows = [["Ordem (grau)", "Coeficiente"]]
            for i, c in enumerate(pr["coeffs"]):
                rows.append([str(pr["degree"] - i), f"{c:.8e}"])
            story.append(tbl(rows, [PW*0.35, PW*0.65]))

        story += [
            Spacer(1, 6),
            Paragraph("Graficos da Golden Curve", s_sec),
            RLImage(buf, width=PW, height=PW*4.5/12),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=0.5,
                       color=colors.HexColor("#cccccc"), spaceAfter=4),
            Paragraph(
                f"Golden Curve Analyzer  |  Bruno Bernardinetti - Stellantis  |  {now}",
                s_foot),
        ]
        doc.build(story)


# ─────────────────────────────────────────────────────────────────────────────
# App principal com abas
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self._ver = _get_app_version()
        self.title(f"BCI - KNUCKLE SOFTWARE  {self._ver}")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(1100, 600)
        self.ra_sede_cal = None
        self._build_ui()
        self._check_trial()
        _check_update_async(self._ver, lambda tag: self.after(0, lambda: self._show_update_banner(tag)))

    # ── helpers de versão / help ──────────────────────────────────────────────
    def _show_update_banner(self, new_tag: str):
        banner = tk.Frame(self, bg="#0e2b0e", padx=10, pady=4)
        banner.pack(fill="x", before=self._nb)
        tk.Label(
            banner,
            text=f"  Nova versão disponível: {new_tag}  —  "
                 "github.com/BrunoBernar/rugosidade_optica_teste",
            font=("Helvetica", 9), fg="#44ff88", bg="#0e2b0e"
        ).pack(side="left")
        tk.Button(
            banner, text=" ✕ ", font=("Helvetica", 9),
            bg="#0e2b0e", fg="#44ff88", relief="flat", cursor="hand2",
            command=banner.destroy
        ).pack(side="right")

    def _check_trial(self):
        days = _trial_days_left()
        if days <= 0 and not _IS_DEV:
            self.after(150, self._show_trial_expired_modal)
        elif days <= 3 and not _IS_DEV:
            self.after(300, lambda: self._show_trial_banner(days))

    def _show_trial_banner(self, days: int):
        banner = tk.Frame(self, bg="#2b1a00", padx=10, pady=5)
        banner.pack(fill="x", before=self._nb)
        tk.Label(
            banner,
            text=f"  ⏱ AVALIAÇÃO GRATUITA — {days} dia(s) restante(s)"
                 f"  |  Licença: {_CONTATO}",
            font=("Helvetica", 9), fg="#ffcc44", bg="#2b1a00"
        ).pack(side="left")
        tk.Button(banner, text=" ✕ ", font=("Helvetica", 9),
                  bg="#2b1a00", fg="#ffcc44", relief="flat", cursor="hand2",
                  command=banner.destroy).pack(side="right")

    def _show_trial_expired_modal(self):
        win = tk.Toplevel(self)
        win.title("Período de avaliação encerrado")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.quit)
        tk.Label(win, text="PERÍODO DE AVALIAÇÃO ENCERRADO",
                 font=("Courier", 13, "bold"), fg=RED, bg=BG).pack(pady=(30, 8), padx=50)
        tk.Label(win,
                 text="Seu teste gratuito de 7 dias expirou.\n\n"
                      "Para continuar usando o BCI - KNUCKLE SOFTWARE\n"
                      "entre em contato para adquirir sua licença:",
                 font=("Helvetica", 10), fg=FG, bg=BG, justify="center").pack(pady=8)
        tk.Label(win, text=_CONTATO,
                 font=("Courier", 18, "bold"), fg=ACCENT, bg=BG).pack(pady=12)
        tk.Label(win, text="WhatsApp / Telefone",
                 font=("Helvetica", 8), fg=FG_DIM, bg=BG).pack()
        tk.Button(win, text="Fechar software", font=("Helvetica", 10, "bold"),
                  bg=RED, fg="white", relief="flat", padx=24, pady=8,
                  command=self.quit).pack(pady=24)
        win.update_idletasks()
        w = win.winfo_reqwidth(); h = win.winfo_reqheight()
        sw = win.winfo_screenwidth(); sh = win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _open_settings(self):
        sett = _get_settings()
        auto = sett.get("auto_update", True)
        win = tk.Toplevel(self)
        win.title("Configurações")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        tk.Label(win, text="CONFIGURAÇÕES",
                 font=("Courier", 11, "bold"), fg=ACCENT, bg=BG).pack(pady=(20, 10), padx=30)
        frm = tk.Frame(win, bg=BG2, padx=20, pady=15)
        frm.pack(fill="x", padx=20, pady=4)
        var = tk.BooleanVar(value=auto)
        tk.Checkbutton(
            frm, text="Verificar atualizações automaticamente ao iniciar",
            variable=var, bg=BG2, fg=FG, activebackground=BG2,
            activeforeground=FG, selectcolor=BG, font=("Helvetica", 9)
        ).pack(anchor="w")
        def _save():
            sett["auto_update"] = var.get()
            _save_settings(sett)
            win.destroy()
        tk.Button(win, text="Salvar", font=("Helvetica", 10, "bold"),
                  bg=ACCENT, fg=BG, relief="flat", padx=20, pady=6,
                  command=_save).pack(pady=(10, 20))

    def _open_help(self):
        candidates = [
            os.path.join(_SCRIPT_DIR, "manual.pdf"),
            os.path.join(_SCRIPT_DIR, "Manual.pdf"),
            os.path.join(_SCRIPT_DIR, "BCI_KNUCKLE_MANUAL.pdf"),
            os.path.join(_SCRIPT_DIR, "ajuda.pdf"),
        ]
        for pdf in candidates:
            if os.path.exists(pdf):
                os.startfile(pdf)
                return
        messagebox.showinfo(
            "Ajuda — BCI KNUCKLE SOFTWARE",
            "Manual não encontrado.\n\n"
            "Coloque o arquivo 'manual.pdf' na mesma pasta do software e tente novamente."
        )

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG, padx=20, pady=10)
        hdr.pack(fill="x")

        # lado esquerdo — título + autor
        left = tk.Frame(hdr, bg=BG)
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="BCI - KNUCKLE SOFTWARE",
                 font=("Courier", 13, "bold"), fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(left,
                 text="Author: Bruno Bernardinetti - Stellantis  |  Brasil",
                 font=("Helvetica", 9), fg=FG_DIM, bg=BG).pack(anchor="w")

        # lado direito — versão + botão "?"
        right = tk.Frame(hdr, bg=BG)
        right.pack(side="right", anchor="ne")
        tk.Label(right, text=self._ver,
                 font=("Courier", 9), fg=FG_DIM, bg=BG).pack(anchor="e")
        btn_row = tk.Frame(right, bg=BG)
        btn_row.pack(anchor="e", pady=(6, 0))
        tk.Button(
            btn_row, text=" ⚙ ", font=("Courier", 10),
            bg=BG2, fg=FG_DIM, relief="flat", cursor="hand2",
            activebackground=BG2, activeforeground=FG,
            command=self._open_settings
        ).pack(side="left", padx=(0, 4))
        tk.Button(
            btn_row, text=" ? ", font=("Courier", 10, "bold"),
            bg=BG2, fg=ACCENT, relief="flat", cursor="hand2",
            activebackground=BG2, activeforeground=ACCENT,
            command=self._open_help
        ).pack(side="left")

        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

        style=ttk.Style(self); style.theme_use("default")
        style.configure("TNotebook",background=BG,borderwidth=0,tabmargins=[0,0,0,0])
        style.configure("TNotebook.Tab",background=BG2,foreground=FG_DIM,
                        font=("Courier",10,"bold"),padding=[20,8],borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected",BG)],
                  foreground=[("selected",ACCENT)],
                  expand=[("selected",[0,0,0,2])])

        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True)
        nb = self._nb

        self._aba_rug=AbaRugosidade(nb,app_ref=self)
        nb.add(self._aba_rug,text="  Analise de Rugosidade  ")

        self._aba_int=AbaInterferencia(nb,app_ref=self)
        nb.add(self._aba_int,text="  Calculo de Interferencia  ")

        self._aba_xml=AbaXMLComparator(nb)
        nb.add(self._aba_xml,text="  Comparador de Curvas XML  ")

        self._aba_golden=AbaGoldenCurve(nb, app_ref=self)
        nb.add(self._aba_golden,text="  Golden Curve  ")


if __name__ == "__main__":
    app = App()
    app.mainloop()

    