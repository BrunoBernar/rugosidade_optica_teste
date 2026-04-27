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
import os, io, datetime

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
# Calculo de interferencia (Lame)
# ─────────────────────────────────────────────────────────────────────────────

def calcular_interferencia(p):
    d=p["d"]; L=p["L"]; De=p["De"]; di=p["di"]
    delta_nom=p["delta_nom"]
    E_m=p["E_manga"]; nu_m=p["nu_manga"]; Sy_m=p["Sy_manga"]
    E_r=p["E_rol"];   nu_r=p["nu_rol"];   Sy_r=p["Sy_rol"]
    Ra_s=p["Ra_sede"]; Ra_r=p["Ra_rol"]; k_rz=p["k_rz"]; mu=p["mu"]

    Rz_sede = 4.0 * Ra_s
    Rz_rol  = 4.0 * Ra_r
    delta_ef_um = delta_nom - k_rz * (Rz_sede + Rz_rol)
    delta_ef_mm = delta_ef_um / 1000.0

    if delta_ef_mm <= 0:
        raise ValueError(
            f"Interferencia efetiva negativa ({delta_ef_um:.2f} µm).\n"
            f"A rugosidade consome toda a interferencia nominal.\n"
            f"Reduza a rugosidade ou aumente a interferencia nominal.")

    C_m = (De**2 + d**2) / (De**2 - d**2) + nu_m
    C_r = (1.0 - nu_r) if di <= 0 else (d**2 + di**2) / (d**2 - di**2) - nu_r

    pressao = delta_ef_mm / (d * (C_m / E_m + C_r / E_r))
    F = mu * pressao * np.pi * d * L

    s_t_m  = pressao * (De**2 + d**2) / (De**2 - d**2)
    s_r_m  = -pressao
    s_VM_m = np.sqrt(s_t_m**2 - s_t_m * s_r_m + s_r_m**2)

    if di <= 0:
        s_t_r = -pressao; s_r_r = -pressao; s_VM_r = pressao
    else:
        s_t_r  = -pressao * (d**2 + di**2) / (d**2 - di**2)
        s_r_r  = -pressao
        s_VM_r = np.sqrt(s_t_r**2 - s_t_r * s_r_r + s_r_r**2)

    FS_m = Sy_m / s_VM_m if s_VM_m > 0 else float("inf")
    FS_r = Sy_r / s_VM_r if s_VM_r > 0 else float("inf")

    return dict(delta_nom=delta_nom, Rz_sede=Rz_sede, Rz_rol=Rz_rol,
                delta_ef=delta_ef_um, delta_ef_mm=delta_ef_mm,
                pressao=pressao, F_N=F, F_kN=F/1000,
                s_t_m=s_t_m, s_VM_m=s_VM_m,
                s_t_r=s_t_r, s_VM_r=s_VM_r,
                FS_m=FS_m, FS_r=FS_r, C_m=C_m, C_r=C_r)

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

MATERIAIS = {
    "Aco SAE 1045":      dict(E=210000, nu=0.30, Sy=355),
    "Aco SAE 4340":      dict(E=210000, nu=0.30, Sy=470),
    "Aco inox 316":      dict(E=193000, nu=0.27, Sy=290),
    "FF Nodular D600C":  dict(E=170000, nu=0.28, Sy=370),
    "FF Nodular D400":   dict(E=170000, nu=0.28, Sy=250),
    "FF Cinzento GH190": dict(E=120000, nu=0.26, Sy=190),
    "Rolamento (52100)": dict(E=210000, nu=0.30, Sy=1500),
    "Personalizado":     dict(E=210000, nu=0.30, Sy=355),
}

MU_TABLE = {
    ("aco", "aco", "seco"): 0.13, ("aco", "aco", "oleo"): 0.06,
    ("aco", "ff",  "seco"): 0.12, ("aco", "ff",  "oleo"): 0.06,
    ("ff",  "aco", "seco"): 0.12, ("ff",  "aco", "oleo"): 0.06,
    ("ff",  "ff",  "seco"): 0.10, ("ff",  "ff",  "oleo"): 0.05,
}

def _grupo(nome):
    n = nome.lower()
    return "ff" if any(x in n for x in ["ff","fundido","cinzento","nodular"]) else "aco"

def mu_auto(nm, nr, cond):
    g1,g2 = _grupo(nm), _grupo(nr)
    return MU_TABLE.get((g1,g2,cond), MU_TABLE.get((g2,g1,cond), 0.12))


# ─────────────────────────────────────────────────────────────────────────────
# Aba 2 — Calculo de Interferencia
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Aba 2 — Calculo de Interferencia
# ─────────────────────────────────────────────────────────────────────────────

class AbaInterferencia(tk.Frame):
    def __init__(self, parent, app_ref, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._app = app_ref
        self._resultado = None
        self._cond_used = "seco"
        self._mat_manga = "FF Nodular D600C"
        self._mat_rol   = "Rolamento (52100)"
        self._delta_lbl = "nominal"
        self._d_min_um = self._d_max_um = self._d_nom_um = 0
        self._build()

    def _build(self):
        scroller = ScrollableFrame(self)
        scroller.pack(fill="both", expand=True)
        W = scroller.inner   # alias

        PAD = dict(padx=20, pady=6)

        # ══════════════════════════════════════════════════════════════════════
        # Cabecalho da aba
        # ══════════════════════════════════════════════════════════════════════
        hdr = tk.Frame(W, bg=BG2)
        hdr.pack(fill="x", padx=0, pady=(0,8))
        tk.Label(hdr, text="  CALCULO DE INTERFERENCIA — ROLAMENTO / MANGA DE EIXO",
                 bg=BG2, fg=PURPLE, font=("Courier",10,"bold"),
                 anchor="w", pady=8).pack(side="left")
        tk.Label(hdr,
                 text="Equacoes de Lame  |  VDI 2230  |  ISO 286  ",
                 bg=BG2, fg=FG_DIM, font=("Helvetica",8),
                 anchor="e").pack(side="right")

        # ══════════════════════════════════════════════════════════════════════
        # SECAO 1 — INPUTS (duas colunas lado a lado)
        # ══════════════════════════════════════════════════════════════════════
        sec_in = tk.Frame(W, bg=BG)
        sec_in.pack(fill="x", **PAD)

        col_a = tk.Frame(sec_in, bg=BG)
        col_a.pack(side="left", fill="both", expand=True, padx=(0,10))

        col_b = tk.Frame(sec_in, bg=BG)
        col_b.pack(side="left", fill="both", expand=True)

        # ── COL A: Geometria + Tolerancias manga ──────────────────────────────

        gf,gi = frame_card(col_a, "Geometria do ajuste")
        gf.pack(fill="x", pady=(0,6))
        tk.Label(gi,
            text="MANGA (furo — externa)  recebe  ROLAMENTO OD (interna)",
            bg=BG3, fg=ACCENT, font=("Courier",8,"bold"),
            anchor="w", padx=6, pady=5).pack(fill="x", pady=(0,4))
        self._d  = entry_row(gi, "Diam. nominal interface d  [mm]", "78.0",  cor=ACCENT)
        self._L  = entry_row(gi, "Comprimento ajuste L       [mm]", "38.0",  cor=ACCENT)
        self._De = entry_row(gi, "Diam. ext. da manga De     [mm]", "81.65", cor=ACCENT)
        self._di = entry_row(gi, "Diam. int. anel ext. di    [mm]", "72.77", cor=ACCENT)
        tk.Label(gi,
            text="di = diam. interno do anel externo do rolamento (do desenho).\n"
                 "di = 0 somente se o anel for macico.",
            bg=BG, fg=FG_DIM, font=("Helvetica",7),
            justify="left").pack(fill="x", pady=(2,0))

        sf,si = frame_card(col_a, "Tolerancias — Furo da manga  (parte EXTERNA)")
        sf.pack(fill="x", pady=(0,6))
        tk.Label(si,
            text="O furo da manga RECEBE o rolamento. O furo e MENOR que o OD.\n"
                 "Ex. do desenho:  O78 -0.083 / -0.113\n"
                 "  es = -0.083   ei = -0.113\n"
                 "  Furo entre 77.887 e 77.917 mm",
            bg=BG, fg=FG_DIM, font=("Helvetica",7),
            justify="left", wraplength=380).pack(fill="x", pady=(0,4))
        self._sede_d  = entry_row(si, "Diam. nominal furo manga   [mm]", "78.0",   cor=ACCENT)
        self._sede_es = entry_row(si, "Desvio superior es         [mm]", "-0.083", cor=ACCENT)
        self._sede_ei = entry_row(si, "Desvio inferior ei         [mm]", "-0.113", cor=ACCENT)
        self._lbl_sede_calc = tk.Label(si, text="", bg=BG2, fg=GREEN,
                                       font=("Courier",8), anchor="w", padx=6, pady=3)
        self._lbl_sede_calc.pack(fill="x", pady=(3,0))

        # ── COL B: Tolerancias rolamento + materiais ──────────────────────────

        rf2,ri3 = frame_card(col_b, "Tolerancias — OD anel externo rolamento  (parte INTERNA)")
        rf2.pack(fill="x", pady=(0,6))
        tk.Label(ri3,
            text="O OD do rolamento e MAIOR que o furo da manga — gera interferencia.\n"
                 "Ex. do desenho:  O78.03 -0.014 / -0.027\n"
                 "  ES = -0.014   EI = -0.027\n"
                 "  OD entre 78.003 e 78.016 mm",
            bg=BG, fg=FG_DIM, font=("Helvetica",7),
            justify="left", wraplength=380).pack(fill="x", pady=(0,4))
        self._rol_D  = entry_row(ri3, "Diam. nominal OD rolamento [mm]", "78.03",  cor=GOLD)
        self._rol_ES = entry_row(ri3, "Desvio superior ES         [mm]", "-0.014", cor=GOLD)
        self._rol_EI = entry_row(ri3, "Desvio inferior EI         [mm]", "-0.027", cor=GOLD)
        self._lbl_rol_calc = tk.Label(ri3, text="", bg=BG2, fg=GOLD,
                                      font=("Courier",8), anchor="w", padx=6, pady=3)
        self._lbl_rol_calc.pack(fill="x", pady=(3,0))

        mf2,mi2 = frame_card(col_b, "Material — Manga / Sede")
        mf2.pack(fill="x", pady=(0,6))
        self._mat_manga_var = tk.StringVar(value="FF Nodular D600C")
        cb_m = ttk.Combobox(mi2, textvariable=self._mat_manga_var,
                            values=list(MATERIAIS.keys()),
                            state="readonly", font=("Helvetica",9))
        cb_m.pack(fill="x", pady=(0,4)); cb_m.bind("<<ComboboxSelected>>", self._on_mat_manga)
        self._E_m  = entry_row(mi2, "Modulo E      [MPa]",       "170000", cor=ACCENT)
        self._nu_m = entry_row(mi2, "Poisson nu",                 "0.28",   cor=ACCENT)
        self._Sy_m = entry_row(mi2, "Tensao escoa. Sy   [MPa]",   "370",    cor=ACCENT)

        rf3,ri4 = frame_card(col_b, "Material — Anel externo do rolamento")
        rf3.pack(fill="x", pady=(0,6))
        self._mat_rol_var = tk.StringVar(value="Rolamento (52100)")
        cb_r = ttk.Combobox(ri4, textvariable=self._mat_rol_var,
                            values=list(MATERIAIS.keys()),
                            state="readonly", font=("Helvetica",9))
        cb_r.pack(fill="x", pady=(0,4)); cb_r.bind("<<ComboboxSelected>>", self._on_mat_rol)
        self._E_r  = entry_row(ri4, "Modulo E      [MPa]",       "210000", cor=GOLD)
        self._nu_r = entry_row(ri4, "Poisson nu",                 "0.30",   cor=GOLD)
        self._Sy_r = entry_row(ri4, "Tensao escoa. Sy   [MPa]",   "1500",   cor=GOLD)

        # ══════════════════════════════════════════════════════════════════════
        # SECAO 2 — RUGOSIDADE + CONDICAO (duas colunas)
        # ══════════════════════════════════════════════════════════════════════
        sec_rug = tk.Frame(W, bg=BG)
        sec_rug.pack(fill="x", **PAD)

        col_c = tk.Frame(sec_rug, bg=BG)
        col_c.pack(side="left", fill="both", expand=True, padx=(0,10))
        col_d = tk.Frame(sec_rug, bg=BG)
        col_d.pack(side="left", fill="both", expand=True)

        rugf,rugi = frame_card(col_c, "Rugosidade das superficies")
        rugf.pack(fill="x", pady=(0,0))
        self._Ra_sede = entry_row(rugi, "Ra furo manga        [µm]", "6.3", cor=ACCENT)
        self._Ra_rol  = entry_row(rugi, "Ra OD rolamento      [µm]", "0.4", cor=GOLD)
        self._k_rz    = entry_row(rugi, "Fator alisamento k_Rz",     "0.8", cor=FG_DIM)
        tk.Button(rugi, text="Importar Ra da Aba 1 (analise de imagem)",
                  command=self._importar_ra,
                  bg=BG2, fg=ACCENT, font=FONT_MONO, relief="flat",
                  pady=4, cursor="hand2",
                  activebackground=BG, activeforeground=ACCENT).pack(fill="x", pady=(4,0))
        self._lbl_import = tk.Label(rugi, text="", bg=BG, fg=GREEN,
                                    font=("Courier",7), anchor="w")
        self._lbl_import.pack(fill="x")
        tk.Label(rugi,
            text="Rz estimado = 4 x Ra  |  k_Rz = 0.6 a 0.8 (VDI 2230)",
            bg=BG, fg=FG_DIM, font=("Helvetica",7)).pack(fill="x", pady=(3,0))

        cf2,ci2 = frame_card(col_d, "Condicao de montagem")
        cf2.pack(fill="x", pady=(0,0))
        self._cond_var = tk.StringVar(value="seco")
        for val,lbl,cor in [("seco","  A SECO  (sem lubrificante)",ACCENT),
                             ("oleo","  COM OLEO / GRAXA",GOLD)]:
            tk.Radiobutton(ci2, text=lbl, variable=self._cond_var,
                           value=val, bg=BG, fg=cor, selectcolor=BG2,
                           activebackground=BG, activeforeground=cor,
                           font=("Courier",10,"bold"),
                           command=self._on_cond_change).pack(anchor="w", pady=2)
        self._mu = entry_row(ci2, "µ  (atrito estatico)", "0.12", cor=ACCENT)
        self._lbl_mu_hint = tk.Label(ci2, text="", bg=BG, fg=FG_DIM,
                                     font=("Helvetica",7), anchor="w")
        self._lbl_mu_hint.pack(fill="x")
        tk.Label(ci2,
            text="Seco  — Aco/Aco: 0.12-0.15  |  Aco/FF: 0.10-0.14\n"
                 "Oleo  — Aco/Aco: 0.05-0.08  |  Aco/FF: 0.04-0.07",
            bg=BG, fg=FG_DIM, font=("Helvetica",7),
            justify="left").pack(fill="x", pady=(4,0))

        # ══════════════════════════════════════════════════════════════════════
        # SECAO 3 — BOTOES + DELTA PREVIEW (largura total)
        # ══════════════════════════════════════════════════════════════════════
        sec_btn = tk.Frame(W, bg=BG)
        sec_btn.pack(fill="x", **PAD)

        col_e = tk.Frame(sec_btn, bg=BG)
        col_e.pack(side="left", fill="both", expand=True, padx=(0,10))
        col_f = tk.Frame(sec_btn, bg=BG)
        col_f.pack(side="left", fill="both", expand=True)

        # Pre-visualizacao da interferencia
        prev_f, prev_i = frame_card(col_e, "Pre-visualizacao das tolerancias")
        prev_f.pack(fill="x")
        tk.Button(prev_i,
            text="Calcular faixa de interferencia das tolerancias",
            command=self._preview_interferencia,
            bg=BG2, fg=ACCENT, font=("Courier",9,"bold"), relief="flat",
            pady=5, cursor="hand2",
            activebackground=BG, activeforeground=ACCENT).pack(fill="x", pady=(0,6))
        self._v_dmin = tk.StringVar(value="—")
        self._v_dnom = tk.StringVar(value="—")
        self._v_dmax = tk.StringVar(value="—")
        result_row(prev_i, "δ minima  (pior caso)      [µm]", self._v_dmin, cor=ORANGE)
        result_row(prev_i, "δ nominal (media)          [µm]", self._v_dnom, cor=GREEN)
        result_row(prev_i, "δ maxima  (melhor caso)    [µm]", self._v_dmax, cor=ACCENT)
        self._lbl_delta_aviso = tk.Label(prev_i, text="", bg=BG, fg=FG_DIM,
                                         font=("Courier",7), anchor="w")
        self._lbl_delta_aviso.pack(fill="x", pady=(2,0))

        # Selecao + botoes
        sel_f, sel_i = frame_card(col_f, "Usar para calculo + Acoes")
        sel_f.pack(fill="x")
        self._delta_choice = tk.StringVar(value="nominal")
        for val,lbl in [("minima", "δ minima — pior caso (menor forca)"),
                        ("nominal","δ nominal — valor medio"),
                        ("maxima", "δ maxima — maior forca de montagem")]:
            tk.Radiobutton(sel_i, text=lbl, variable=self._delta_choice,
                           value=val, bg=BG, fg=FG, selectcolor=BG2,
                           activebackground=BG, activeforeground=ACCENT,
                           font=("Helvetica",9)).pack(anchor="w")

        self._btn_calc = tk.Button(sel_i,
            text="▶  CALCULAR INTERFERENCIA",
            command=self._calcular,
            bg=BG2, fg=PURPLE, font=("Courier",11,"bold"),
            relief="flat", pady=10, cursor="hand2",
            activebackground=BG, activeforeground=PURPLE)
        self._btn_calc.pack(fill="x", pady=(8,4))

        self._btn_pdf2 = tk.Button(sel_i,
            text="Exportar PDF",
            command=self._exportar_pdf,
            bg=BG2, fg=GOLD, font=("Courier",10,"bold"),
            relief="flat", pady=6, cursor="hand2",
            activebackground=BG, activeforeground=GOLD,
            state="disabled")
        self._btn_pdf2.pack(fill="x")

        # ══════════════════════════════════════════════════════════════════════
        # SECAO 4 — RESULTADOS (largura total, fundo destacado)
        # ══════════════════════════════════════════════════════════════════════
        tk.Frame(W, bg=PURPLE, height=2).pack(fill="x", padx=20, pady=(10,0))
        res_hdr = tk.Frame(W, bg=BG2)
        res_hdr.pack(fill="x", padx=0)
        tk.Label(res_hdr,
            text="  RESULTADOS DO CALCULO",
            bg=BG2, fg=PURPLE, font=("Courier",11,"bold"),
            anchor="w", pady=6).pack(side="left")
        self._lbl_delta_usado = tk.Label(res_hdr, text="  aguardando calculo...",
                                          bg=BG2, fg=FG_DIM,
                                          font=("Courier",8), anchor="w")
        self._lbl_delta_usado.pack(side="left")

        # Resultados em 3 colunas
        sec_res = tk.Frame(W, bg=BG)
        sec_res.pack(fill="x", **PAD)

        rc1 = tk.Frame(sec_res, bg=BG); rc1.pack(side="left", fill="both", expand=True, padx=(0,8))
        rc2 = tk.Frame(sec_res, bg=BG); rc2.pack(side="left", fill="both", expand=True, padx=(0,8))
        rc3 = tk.Frame(sec_res, bg=BG); rc3.pack(side="left", fill="both", expand=True)

        # Coluna 1 — Interferencia
        if2,ii2 = frame_card(rc1, "Interferencia")
        if2.pack(fill="x", pady=(0,6))
        self._v_delta_nom2 = tk.StringVar(value="—")
        self._v_rz_sede    = tk.StringVar(value="—")
        self._v_rz_rol     = tk.StringVar(value="—")
        self._v_delta_ef   = tk.StringVar(value="—")
        result_row(ii2, "δ usada             [µm]", self._v_delta_nom2)
        result_row(ii2, "Rz furo manga       [µm]", self._v_rz_sede,  cor=ACCENT)
        result_row(ii2, "Rz OD rolamento     [µm]", self._v_rz_rol,   cor=GOLD)
        result_row(ii2, "δ EFETIVA           [µm]", self._v_delta_ef, cor=GREEN)

        # Coluna 1 — Pressao e forca
        pf2,pi2 = frame_card(rc1, "Pressao e Forca")
        pf2.pack(fill="x")
        self._v_pressao = tk.StringVar(value="—")
        self._v_F_kN    = tk.StringVar(value="—")
        self._v_F_N     = tk.StringVar(value="—")
        result_row(pi2, "Pressao p     [MPa]", self._v_pressao, cor=PURPLE)
        result_row(pi2, "Forca F       [kN]",  self._v_F_kN,   cor=PURPLE)
        result_row(pi2, "Forca F       [N]",   self._v_F_N,    cor=FG_DIM)

        # Coluna 2 — Tensoes
        tf2,ti2 = frame_card(rc2, "Tensoes nas pecas")
        tf2.pack(fill="x", pady=(0,6))
        self._v_st_m = tk.StringVar(value="—"); self._v_vm_m = tk.StringVar(value="—")
        self._v_st_r = tk.StringVar(value="—"); self._v_vm_r = tk.StringVar(value="—")
        result_row(ti2, "Hoop manga (int.) [MPa]", self._v_st_m,  cor=ACCENT)
        result_row(ti2, "Von Mises manga   [MPa]", self._v_vm_m,  cor=ACCENT)
        result_row(ti2, "Hoop rolamento    [MPa]", self._v_st_r,  cor=GOLD)
        result_row(ti2, "Von Mises rolam.  [MPa]", self._v_vm_r,  cor=GOLD)

        # Coluna 3 — Fatores de seguranca
        sf2,si2 = frame_card(rc3, "Fatores de seguranca  (Sy / Von Mises)")
        sf2.pack(fill="x")
        self._v_FS_m = tk.StringVar(value="—"); self._v_FS_r = tk.StringVar(value="—")
        self._lbl_FS_m_sem = tk.Label(si2, text="", bg=BG,
                                      font=("Courier",9,"bold"), anchor="w")
        self._lbl_FS_r_sem = tk.Label(si2, text="", bg=BG,
                                      font=("Courier",9,"bold"), anchor="w")
        result_row(si2, "FS manga",    self._v_FS_m, cor=FG)
        self._lbl_FS_m_sem.pack(fill="x")
        result_row(si2, "FS rolamento",self._v_FS_r, cor=FG)
        self._lbl_FS_r_sem.pack(fill="x")

        # ══════════════════════════════════════════════════════════════════════
        # SECAO 5 — GRAFICO (largura total)
        # ══════════════════════════════════════════════════════════════════════
        tk.Frame(W, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(10,4))
        graf_frame2 = tk.Frame(W, bg=BG)
        graf_frame2.pack(fill="x", padx=20, pady=(0,20))

        self._fig2, self._ax_interf = plt.subplots(1, 1, figsize=(13, 4.5), facecolor=BG)
        self._fig2.tight_layout(pad=2.5)
        self._ax_interf.set_facecolor(BG3)
        for sp in self._ax_interf.spines.values(): sp.set_edgecolor(BORDER)
        self._ax_interf.tick_params(colors=FG_DIM, labelsize=8)
        self._canvas_interf = FigureCanvasTkAgg(self._fig2, master=graf_frame2)
        self._canvas_interf.get_tk_widget().pack(fill="x")
        self._placeholder_interf()

        # Aplica presets iniciais
        self._on_mat_manga()
        self._on_mat_rol()
        self._on_cond_change()

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_mat_manga(self, event=None):
        m = MATERIAIS[self._mat_manga_var.get()]
        self._E_m.set(str(m["E"])); self._nu_m.set(str(m["nu"])); self._Sy_m.set(str(m["Sy"]))
        self._on_cond_change()

    def _on_mat_rol(self, event=None):
        m = MATERIAIS[self._mat_rol_var.get()]
        self._E_r.set(str(m["E"])); self._nu_r.set(str(m["nu"])); self._Sy_r.set(str(m["Sy"]))
        self._on_cond_change()

    def _on_cond_change(self, event=None):
        cond = self._cond_var.get()
        nm = self._mat_manga_var.get(); nr = self._mat_rol_var.get()
        mu = mu_auto(nm, nr, cond)
        self._mu.set(f"{mu:.2f}")
        c = "seco" if cond=="seco" else "com oleo"
        self._lbl_mu_hint.config(
            text=f"Sugerido ({c}): µ = {mu:.2f}  —  {nm.split()[0]} / {nr.split()[0]}")

    def _preview_interferencia(self):
        try:
            sd=float(self._sede_d.get().replace(",",".")); ses=float(self._sede_es.get().replace(",","."))
            sei=float(self._sede_ei.get().replace(",",".")); rD=float(self._rol_D.get().replace(",","."))
            rES=float(self._rol_ES.get().replace(",",".")); rEI=float(self._rol_EI.get().replace(",","."))
        except ValueError:
            messagebox.showwarning("Atencao","Verifique os valores de tolerancia."); return

        sm_max = sd+ses; sm_min = sd+sei   # furo manga: max e min
        ro_max = rD+rES; ro_min = rD+rEI   # OD rolamento: max e min

        self._lbl_sede_calc.config(text=f"Furo manga: {sm_min:.4f}  a  {sm_max:.4f} mm")
        self._lbl_rol_calc.config( text=f"OD rolam.:  {ro_min:.4f}  a  {ro_max:.4f} mm")

        # δ = OD_rolamento - furo_manga (positivo = interferencia)
        d_max = (ro_max - sm_min) * 1000
        d_min = (ro_min - sm_max) * 1000
        d_nom = (d_max + d_min) / 2

        self._v_dmax.set(f"{d_max:.1f} µm" if d_max>0 else f"{d_max:.1f} µm  ⚠ FOLGA!")
        self._v_dmin.set(f"{d_min:.1f} µm" if d_min>0 else f"{d_min:.1f} µm  ⚠ FOLGA!")
        self._v_dnom.set(f"{d_nom:.1f} µm")

        if d_min <= 0:
            self._lbl_delta_aviso.config(
                text="ATENCAO: δ minima <= 0 — pode haver folga no pior caso!", fg=RED)
        elif d_min < 20:
            self._lbl_delta_aviso.config(
                text="Aviso: δ minima pequena — verifique retencao axial.", fg=ORANGE)
        else:
            self._lbl_delta_aviso.config(
                text=f"Interferencia confirmada em todos os casos.", fg=GREEN)

        self._d_min_um = d_min; self._d_max_um = d_max; self._d_nom_um = d_nom

    def _importar_ra(self):
        ra = getattr(self._app, "ra_sede_cal", None)
        if ra is None:
            messagebox.showwarning("Atencao","Execute a analise na Aba 1 primeiro."); return
        self._Ra_sede.set(f"{ra:.4f}")
        self._lbl_import.config(text=f"Importado Aba 1: Ra = {ra:.4f} µm")

    def _calcular(self):
        self._preview_interferencia()
        try:
            sd=float(self._sede_d.get().replace(",",".")); ses=float(self._sede_es.get().replace(",","."))
            sei=float(self._sede_ei.get().replace(",",".")); rD=float(self._rol_D.get().replace(",","."))
            rES=float(self._rol_ES.get().replace(",",".")); rEI=float(self._rol_EI.get().replace(",","."))

            sm_max=sd+ses; sm_min=sd+sei; ro_max=rD+rES; ro_min=rD+rEI
            d_max_um=(ro_max-sm_min)*1000; d_min_um=(ro_min-sm_max)*1000
            d_nom_um=(d_max_um+d_min_um)/2

            choice=self._delta_choice.get()
            delta_used = {"minima":d_min_um,"maxima":d_max_um,"nominal":d_nom_um}[choice]
            lbl_used   = {"minima":"δ minima","maxima":"δ maxima","nominal":"δ nominal"}[choice]

            if delta_used <= 0:
                messagebox.showerror("Erro",
                    f"{lbl_used} = {delta_used:.1f} µm — folga, nao interferencia.\n"
                    "Revise as tolerancias."); return

            params = dict(
                d=float(self._d.get().replace(",",".")),
                L=float(self._L.get().replace(",",".")),
                De=float(self._De.get().replace(",",".")),
                di=float(self._di.get().replace(",",".")),
                delta_nom=delta_used,
                E_manga=float(self._E_m.get().replace(",",".")),
                nu_manga=float(self._nu_m.get().replace(",",".")),
                Sy_manga=float(self._Sy_m.get().replace(",",".")),
                E_rol=float(self._E_r.get().replace(",",".")),
                nu_rol=float(self._nu_r.get().replace(",",".")),
                Sy_rol=float(self._Sy_r.get().replace(",",".")),
                Ra_sede=float(self._Ra_sede.get().replace(",",".")),
                Ra_rol=float(self._Ra_rol.get().replace(",",".")),
                k_rz=float(self._k_rz.get().replace(",",".")),
                mu=float(self._mu.get().replace(",",".")),
            )
        except ValueError:
            messagebox.showerror("Erro","Verifique os valores. Use ponto como decimal."); return

        if params["De"]<=params["d"]:
            messagebox.showerror("Erro","De deve ser maior que d."); return
        if params["di"]>0 and params["di"]>=params["d"]:
            messagebox.showerror("Erro","di deve ser menor que d."); return

        try:
            res = calcular_interferencia(params)
        except ValueError as e:
            messagebox.showerror("Interferencia insuficiente",str(e)); return
        except Exception as e:
            messagebox.showerror("Erro no calculo",str(e)); return

        self._resultado=res; self._params=params
        self._delta_lbl=lbl_used; self._d_min_um=d_min_um
        self._d_max_um=d_max_um;  self._d_nom_um=d_nom_um
        self._cond_used=self._cond_var.get()
        self._mat_manga=self._mat_manga_var.get()
        self._mat_rol=self._mat_rol_var.get()

        cond_str = "Seco" if self._cond_used=="seco" else "Com oleo/graxa"
        self._lbl_delta_usado.config(
            text=f"  {lbl_used} = {delta_used:.1f} µm  |  {cond_str}  |  µ = {params['mu']:.2f}",
            fg=GREEN)
        self._mostrar_resultado(res)
        self._btn_pdf2.config(state="normal")

    def _mostrar_resultado(self, r):
        self._v_delta_nom2.set(f"{r['delta_nom']:.1f} µm")
        self._v_rz_sede.set(   f"{r['Rz_sede']:.2f} µm")
        self._v_rz_rol.set(    f"{r['Rz_rol']:.2f} µm")
        self._v_delta_ef.set(  f"{r['delta_ef']:.2f} µm  ({r['delta_ef']/r['delta_nom']*100:.1f}%)")
        self._v_pressao.set(   f"{r['pressao']:.2f}")
        self._v_F_kN.set(      f"{r['F_kN']:.3f}")
        self._v_F_N.set(       f"{r['F_N']:.0f}")
        self._v_st_m.set(      f"{r['s_t_m']:.1f}  (trac.)")
        self._v_vm_m.set(      f"{r['s_VM_m']:.1f}")
        self._v_st_r.set(      f"{r['s_t_r']:.1f}  (comp.)" if r['s_t_r']<0 else f"{r['s_t_r']:.1f}")
        self._v_vm_r.set(      f"{r['s_VM_r']:.1f}")
        for fs,lv,ls in [(r["FS_m"],self._v_FS_m,self._lbl_FS_m_sem),
                          (r["FS_r"],self._v_FS_r,self._lbl_FS_r_sem)]:
            lv.set(f"{fs:.2f}")
            if fs>=2.0:   c,t=GREEN,  "  OK (FS >= 2.0)"
            elif fs>=1.2: c,t=ORANGE, "  ATENCAO (1.2 <= FS < 2.0)"
            else:         c,t=RED,    "  RISCO (FS < 1.2)"
            ls.config(text=t, fg=c)
        self._plotar_interferencia(self._params, r)

    def _plotar_interferencia(self, p, r):
        ax=self._ax_interf; ax.clear(); ax.set_facecolor(BG3)
        d=p["d"]; De=p["De"]; pressao=r["pressao"]
        radii=np.linspace(d/2, De/2, 300)
        sig=(pressao*(d/2)**2/((De/2)**2-(d/2)**2))*(1+(De/2)**2/radii**2)
        ax.fill_between(radii,0,sig,alpha=0.2,color=ACCENT)
        ax.plot(radii,sig,color=ACCENT,lw=2,label="Tensao hoop manga (tracao)")
        ax.axhline(p["Sy_manga"],color=RED,   lw=1.2,ls="--",alpha=0.9,
                   label=f"Sy manga = {p['Sy_manga']:.0f} MPa  (FS={r['FS_m']:.2f})")
        ax.axvline(d/2,          color=GOLD,  lw=1.0,ls=":",alpha=0.8,
                   label=f"r_int = {d/2:.2f} mm")
        ax.axvline(De/2,         color=FG_DIM,lw=1.0,ls=":",alpha=0.8,
                   label=f"r_ext = {De/2:.2f} mm")
        ax.axhline(pressao,      color=PURPLE,lw=1.2,ls="--",alpha=0.9,
                   label=f"p = {pressao:.2f} MPa")
        cond="seco" if self._cond_used=="seco" else "com oleo"
        ax.set_title(
            f"Distribuicao tensao hoop — manga  |  "
            f"δ={r['delta_nom']:.1f} µm  δef={r['delta_ef']:.1f} µm  "
            f"p={pressao:.1f} MPa  F={r['F_kN']:.2f} kN  ({cond})",
            color=FG_DIM, fontsize=8, pad=6)
        ax.set_xlabel("Raio [mm]",color=FG_DIM,fontsize=8)
        ax.set_ylabel("Tensao hoop [MPa]",color=FG_DIM,fontsize=8)
        ax.legend(fontsize=8,facecolor=BG2,edgecolor=BORDER,labelcolor=FG,loc="upper right")
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM,labelsize=8)
        self._fig2.tight_layout(pad=2.0); self._canvas_interf.draw()

    def _placeholder_interf(self):
        ax=self._ax_interf; ax.clear(); ax.set_facecolor(BG3)
        ax.text(0.5,0.5,
            "sem dados\nPreencha os parametros acima e clique   ▶ CALCULAR INTERFERENCIA",
            transform=ax.transAxes,ha="center",va="center",
            color="#2a3a44",fontsize=9,multialignment="center")
        for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
        ax.tick_params(colors=FG_DIM,labelsize=8)
        self._canvas_interf.draw()

    def _exportar_pdf(self):
        if self._resultado is None:
            messagebox.showwarning("Atencao","Realize o calculo antes de exportar."); return
        path=filedialog.asksaveasfilename(title="Salvar relatorio PDF",
            defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not path: return
        try:
            self._gerar_pdf_interferencia(path)
            messagebox.showinfo("Sucesso",f"PDF salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro",str(e))

    def _gerar_pdf_interferencia(self, path):
        r=self._resultado; p=self._params
        now=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        cond_str="A seco" if self._cond_used=="seco" else "Com oleo/graxa"

        fig_p,ax_p=plt.subplots(1,1,figsize=(7,3.5),facecolor="white")
        radii=np.linspace(p["d"]/2,p["De"]/2,200)
        sig=r["pressao"]*(p["d"]/2)**2/((p["De"]/2)**2-(p["d"]/2)**2)*(1+(p["De"]/2)**2/radii**2)
        ax_p.fill_between(radii,0,sig,alpha=0.2,color="#0077aa")
        ax_p.plot(radii,sig,color="#0077aa",lw=1.5,label="Hoop manga")
        ax_p.axhline(p["Sy_manga"],color="red",lw=1,ls="--",label=f"Sy={p['Sy_manga']:.0f} MPa")
        ax_p.axhline(r["pressao"],color="purple",lw=1,ls="--",label=f"p={r['pressao']:.1f} MPa")
        ax_p.set_title("Distribuicao tensao hoop na manga",fontsize=9)
        ax_p.set_xlabel("Raio [mm]",fontsize=8); ax_p.set_ylabel("Tensao [MPa]",fontsize=8)
        ax_p.legend(fontsize=7); ax_p.tick_params(labelsize=7)
        buf=io.BytesIO()
        fig_p.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor="white")
        buf.seek(0); plt.close(fig_p)

        doc=SimpleDocTemplate(path,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,
                              topMargin=18*mm,bottomMargin=18*mm)
        W=A4[0]-40*mm
        s_t =ParagraphStyle("t",fontSize=14,fontName="Helvetica-Bold",textColor=colors.HexColor("#003366"),spaceAfter=2)
        s_a =ParagraphStyle("a",fontSize=9, fontName="Helvetica-Bold",textColor=colors.HexColor("#003366"),spaceAfter=1)
        s_n =ParagraphStyle("n",fontSize=7.5,fontName="Helvetica-Oblique",textColor=colors.HexColor("#666666"),spaceAfter=4)
        s_s =ParagraphStyle("s",fontSize=10,fontName="Helvetica-Bold",textColor=colors.HexColor("#003366"),spaceBefore=10,spaceAfter=4)
        s_b =ParagraphStyle("b",fontSize=8.5,fontName="Helvetica",textColor=colors.black,spaceAfter=3)
        s_w =ParagraphStyle("w",fontSize=7.5,fontName="Helvetica-Oblique",textColor=colors.HexColor("#7a5000"),
                             backColor=colors.HexColor("#fff8e1"),spaceAfter=4,leftIndent=6,rightIndent=6)
        def tbl(data,cw):
            t=Table(data,colWidths=cw)
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

        story=[]
        ht=Table([[Paragraph("RELATORIO — CALCULO DE INTERFERENCIA",s_t),
                   Paragraph(f"Gerado em: {now}",
                   ParagraphStyle("rt",fontSize=8,fontName="Helvetica",
                   textColor=colors.HexColor("#555555"),alignment=TA_RIGHT))]],
                 colWidths=[W*0.65,W*0.35])
        ht.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(ht)
        story.append(Paragraph("Author: Bruno Bernardinetti - Stellantis",s_a))
        story.append(HRFlowable(width="100%",thickness=2,color=colors.HexColor("#003366"),spaceAfter=4))
        story.append(Paragraph(
            "Metodo: Equacoes de Lame — ajuste com interferencia. "
            "Interferencia efetiva descontando alisamento de asperezas (VDI 2230). "
            "Configuracao: OD do anel externo do rolamento prensado no furo da manga.",s_n))

        story.append(Paragraph("Tolerancias e Interferencia",s_s))
        story.append(tbl([
            ["Grandeza","Furo manga (externa)","OD rolamento (interna)","Unidade"],
            ["Diam. nominal",
             f"{float(self._sede_d.get()):.3f} (furo)",
             f"{float(self._rol_D.get()):.3f} (OD)","mm"],
            ["Desvio superior", self._sede_es.get(), self._rol_ES.get(),"mm"],
            ["Desvio inferior", self._sede_ei.get(), self._rol_EI.get(),"mm"],
            ["Diam. maximo",
             f"{float(self._sede_d.get())+float(self._sede_es.get()):.4f}",
             f"{float(self._rol_D.get())+float(self._rol_ES.get()):.4f}","mm"],
            ["Diam. minimo",
             f"{float(self._sede_d.get())+float(self._sede_ei.get()):.4f}",
             f"{float(self._rol_D.get())+float(self._rol_EI.get()):.4f}","mm"],
            ["delta minima",  f"{self._d_min_um:.1f}","—","µm"],
            ["delta nominal", f"{self._d_nom_um:.1f}","—","µm"],
            ["delta maxima",  f"{self._d_max_um:.1f}","—","µm"],
            ["delta USADA",   f"{p['delta_nom']:.1f}  ({self._delta_lbl})","—","µm"],
        ],[W*0.35,W*0.22,W*0.22,W*0.21]))

        story.append(Paragraph("Parametros de Calculo",s_s))
        story.append(tbl([
            ["Parametro","Manga (furo)","Rolamento (OD)","Unidade"],
            ["Material",         self._mat_manga,             self._mat_rol,          "—"],
            ["Modulo E",         f"{p['E_manga']:.0f}",       f"{p['E_rol']:.0f}",    "MPa"],
            ["Poisson nu",       f"{p['nu_manga']:.3f}",      f"{p['nu_rol']:.3f}",   "—"],
            ["Tensao escoa. Sy", f"{p['Sy_manga']:.0f}",      f"{p['Sy_rol']:.0f}",   "MPa"],
            ["Ra superficie",    f"{p['Ra_sede']:.3f}",       f"{p['Ra_rol']:.3f}",   "µm"],
            ["Diam. ext. De",    f"{p['De']:.2f}",            "—",                    "mm"],
            ["Diam. int. di",    "—",                         f"{p['di']:.2f}",       "mm"],
            ["Comprimento L",    f"{p['L']:.1f}",             "—",                    "mm"],
            ["Condicao",         cond_str,                    "—",                    "—"],
            ["Coef. atrito µ",   f"{p['mu']:.3f}",            "—",                    "—"],
            ["Fator k_Rz",       f"{p['k_rz']:.2f}",          "—",                    "—"],
        ],[W*0.35,W*0.22,W*0.22,W*0.21]))

        story.append(Paragraph("Resultados",s_s))
        fm="OK" if r["FS_m"]>=2 else ("ATENCAO" if r["FS_m"]>=1.2 else "RISCO")
        fr="OK" if r["FS_r"]>=2 else ("ATENCAO" if r["FS_r"]>=1.2 else "RISCO")
        story.append(tbl([
            ["Grandeza","Valor","Unidade","Observacao"],
            ["Rz furo manga (4xRa)",  f"{r['Rz_sede']:.2f}","µm","Estimado de Ra"],
            ["Rz OD rolamento (4xRa)",f"{r['Rz_rol']:.2f}", "µm","Estimado de Ra"],
            ["Interferencia efetiva", f"{r['delta_ef']:.2f}","µm",f"{r['delta_ef']/r['delta_nom']*100:.1f}% do nominal"],
            ["Pressao de contato p",  f"{r['pressao']:.2f}", "MPa","Eq. de Lame"],
            ["Forca mont./extrac.",   f"{r['F_kN']:.3f}",   "kN", f"= {r['F_N']:.0f} N  |  {cond_str}"],
            ["Tensao hoop manga",     f"{r['s_t_m']:.1f}",  "MPa","Tracao, sup. interna"],
            ["Von Mises manga",       f"{r['s_VM_m']:.1f}", "MPa",""],
            ["Tensao hoop rolamento", f"{r['s_t_r']:.1f}",  "MPa","Compressao"],
            ["Von Mises rolamento",   f"{r['s_VM_r']:.1f}", "MPa",""],
            ["FS manga",              f"{r['FS_m']:.2f}",   "—",  fm],
            ["FS rolamento",          f"{r['FS_r']:.2f}",   "—",  fr],
        ],[W*0.35,W*0.15,W*0.15,W*0.35]))

        story.append(Paragraph("Grafico — Distribuicao de Tensao Hoop na Manga",s_s))
        story.append(RLImage(buf,width=W*0.85,height=W*0.85*3.5/7))
        story.append(Spacer(1,4))
        story.append(Paragraph(
            "Aviso: Calculos baseados na teoria classica de Lame (elasticidade linear). "
            "Nao considera gradientes termicos, dinamica ou fadiga. "
            "Validar com FEA para aplicacoes criticas.",s_w))
        story.append(Spacer(1,8))
        story.append(HRFlowable(width="100%",thickness=0.5,
                                color=colors.HexColor("#cccccc"),spaceAfter=4))
        story.append(Paragraph(
            f"Gerado pelo Estimador de Rugosidade + Interferencia  |  "
            f"Author: Bruno Bernardinetti - Stellantis  |  {now}",
            ParagraphStyle("footer",fontSize=7,fontName="Helvetica",
                           textColor=colors.HexColor("#888888"),alignment=TA_CENTER)))
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

    