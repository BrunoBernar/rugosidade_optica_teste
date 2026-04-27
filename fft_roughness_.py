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

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.ndimage import sobel
import os, io, datetime, math

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

        if delta_max <= 0:
            messagebox.showerror("Erro", "dmax <= 0 -- sem interferencia no pior caso."); return

        self._lbl_shaft.config(text=f"Eixo: {sh_min:.4f}  a  {sh_max:.4f} mm")
        self._lbl_hub.config(  text=f"Furo: {ho_min:.4f}  a  {ho_max:.4f} mm")

        R  = d   / (2 * 1000)
        ri = di  / (2 * 1000)
        ro = do_ / (2 * 1000)

        pmax = lame_pressure(delta_max, R, Eo, ro, vo, Ei, ri, vi)
        pmin = lame_pressure(delta_min, R, Eo, ro, vo, Ei, ri, vi) if delta_min > 0 else 0.0

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
            text=f"  dmax={delta_max:.4f} mm  pmax={pmax:.2f} MPa  F_nom_seco={F_nom_dry_N:.0f} N",
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
            "Interferencia radial. Forcas calculadas para duas condicoes de atrito "
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
        ], [PW*0.35, PW*0.22, PW*0.22, PW*0.21]))
        story.append(tbl([
            ["Larg. nominal [mm]","Larg. lower [mm]","Larg. upper [mm]","mu seco","mu lubr."],
            [f"{r['w_nom']:.2f}", f"{r['w_lo']:.2f}", f"{r['w_up']:.2f}",
             f"{r['mu_dry']:.2f}", f"{r['mu_lubed']:.2f}"],
        ], [PW*0.22]*5))
        story.append(Paragraph("Resultados", s_s))
        pmin_str = f"{r['pmin']:.4f}" if r['pmin'] > 0 else "folga"
        story.append(tbl([
            ["Grandeza", "Valor", "Unidade"],
            ["Interferencia radial dmax", f"{r['delta_max']:.4f}", "mm"],
            ["Interferencia radial dmin", f"{r['delta_min']:.4f}", "mm"],
            ["Pressao pmax (Lame)",       f"{r['pmax']:.4f}",      "MPa"],
            ["Pressao pmin (Lame)",       pmin_str,                 "MPa"],
            ["Area A nominal",            f"{r['A_nom']:.2f}",     "mm2"],
            ["Area A lower",              f"{r['A_lo']:.2f}",      "mm2"],
            ["Area A upper",              f"{r['A_up']:.2f}",      "mm2"],
        ], [PW*0.50, PW*0.30, PW*0.20]))
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
# App principal com abas
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rugosidade + Interferencia  |  Bruno Bernardinetti - Stellantis")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(1100, 600)   # altura minima menor — scroll cuida do resto
        self.ra_sede_cal = None
        self._build_ui()

    def _build_ui(self):
        hdr=tk.Frame(self,bg=BG,padx=20,pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr,text="SURFACE ROUGHNESS  &  INTERFERENCE FIT ANALYZER",
                 font=("Courier",13,"bold"),fg=ACCENT,bg=BG).pack(anchor="w")
        tk.Label(hdr,text="Author: Bruno Bernardinetti - Stellantis  |  Contagem/BH - Brasil",
                 font=("Helvetica",9),fg=FG_DIM,bg=BG).pack(anchor="w")
        tk.Frame(self,bg=ACCENT,height=2).pack(fill="x")

        style=ttk.Style(self); style.theme_use("default")
        style.configure("TNotebook",background=BG,borderwidth=0,tabmargins=[0,0,0,0])
        style.configure("TNotebook.Tab",background=BG2,foreground=FG_DIM,
                        font=("Courier",10,"bold"),padding=[20,8],borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected",BG)],
                  foreground=[("selected",ACCENT)],
                  expand=[("selected",[0,0,0,2])])

        nb=ttk.Notebook(self); nb.pack(fill="both",expand=True)

        self._aba_rug=AbaRugosidade(nb,app_ref=self)
        nb.add(self._aba_rug,text="  Analise de Rugosidade  ")

        self._aba_int=AbaInterferencia(nb,app_ref=self)
        nb.add(self._aba_int,text="  Calculo de Interferencia  ")


if __name__ == "__main__":
    app = App()
    app.mainloop()

    