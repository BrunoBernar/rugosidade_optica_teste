"""
BCI - KNUCKLE SOFTWARE  [OpenGL Fork]
Author: Bruno Bernardinetti — Stellantis
Renderer: PyQt5 + pyqtgraph (OpenGL / hardware-accelerated)
"""

import sys, os, io, datetime, math, re, csv, threading, urllib.request, json, base64, webbrowser
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from scipy.ndimage import sobel, gaussian_filter1d
from scipy.interpolate import interp1d

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QComboBox, QCheckBox, QScrollArea, QSplitter, QFrame, QFileDialog,
    QMessageBox, QDialog, QProgressBar, QGroupBox, QSizePolicy, QTextEdit,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap, QImage, QPalette

import pyqtgraph as pg

# ── OpenGL + qualidade ────────────────────────────────────────────────────────
pg.setConfigOptions(useOpenGL=True)          # GPU rendering
pg.setConfigOptions(antialias=True)          # linhas suaves
pg.setConfigOption('background', '#0d1117')
pg.setConfigOption('foreground', '#c8d8e8')

# ── Paleta ────────────────────────────────────────────────────────────────────
BG      = '#0d1117'; BG2 = '#111820'; BG3 = '#050709'
ACCENT  = '#00e5ff'; GOLD = '#ffc107'; PURPLE = '#e040fb'
GREEN   = '#4caf50'; RED  = '#f44336'; ORANGE = '#ff9800'
FG      = '#c8d8e8'; FG_DIM = '#3a6070'; BORDER = '#1a2a34'
_C_OK   = '#2ecc71'; _C_NOK = '#e74c3c'; _C_PANEL = '#0e1a26'

def _pen(color, w=1.5):   return pg.mkPen(color=color, width=w)
def _brush(color, a=180): c = QColor(color); c.setAlpha(a); return pg.mkBrush(c)

# ── Versão / trial / paths ───────────────────────────────────────────────────
__version__      = 'v1.0.0'
_SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
_IS_DEV          = os.path.exists(os.path.join(_SCRIPT_DIR, '.git'))
_APP_DATA_DIR    = os.path.join(os.environ.get('APPDATA', _SCRIPT_DIR), 'BCI-Knuckle')
_INST_FILE       = os.path.join(_APP_DATA_DIR, 'inst.dat')
_SETT_FILE       = os.path.join(_APP_DATA_DIR, 'settings.json')
_TRIAL_DAYS      = 7
_CONTATO         = '+55 32 9 9965-0392'
_GH_API_LATEST   = 'https://api.github.com/repos/BrunoBernar/rugosidade_optica_teste/releases/latest'
_GH_API_RELEASES = 'https://api.github.com/repos/BrunoBernar/rugosidade_optica_teste/releases'
_GH_RELEASES_PAGE= 'https://github.com/BrunoBernar/rugosidade_optica_teste/releases'
MIN_FOTOS        = 10
AFNOR_ISO = [('N1','0.025'),('N2','0.05'),('N3','0.1'),('N4','0.2'),
             ('N5','0.4'),('N6','0.8'),('N7','1.6'),('N8','3.2'),
             ('N9','6.3'),('N10','12.5'),('N11','25.0'),('N12','50.0')]

# ── Settings / trial ─────────────────────────────────────────────────────────
def _get_settings():
    try:
        if os.path.exists(_SETT_FILE):
            with open(_SETT_FILE) as f: return json.loads(f.read())
    except Exception: pass
    return {}

def _save_settings(d):
    os.makedirs(_APP_DATA_DIR, exist_ok=True)
    with open(_SETT_FILE, 'w') as f: json.dump(d, f)

def _get_or_create_install_date():
    os.makedirs(_APP_DATA_DIR, exist_ok=True)
    if os.path.exists(_INST_FILE):
        try:
            raw = open(_INST_FILE).read().strip()
            return datetime.date.fromisoformat(base64.b64decode(raw.encode()).decode())
        except Exception: pass
    today = datetime.date.today()
    with open(_INST_FILE, 'w') as f:
        f.write(base64.b64encode(today.isoformat().encode()).decode())
    return today

def _trial_days_left():
    if _IS_DEV: return _TRIAL_DAYS
    return max(0, _TRIAL_DAYS - (datetime.date.today() - _get_or_create_install_date()).days)

def _check_update_async(current_ver, callback):
    if _IS_DEV: return
    sett = _get_settings()
    if not sett.get('auto_update', True): return
    try:
        days_since = (datetime.date.today() - datetime.date.fromisoformat(sett.get('last_update_check',''))).days
    except Exception: days_since = 999
    if days_since < 7: return
    def _w():
        try:
            req = urllib.request.Request(_GH_API_LATEST, headers={'User-Agent':'BCI-KNUCKLE'})
            with urllib.request.urlopen(req, timeout=6) as r: data = json.loads(r.read())
            latest = data.get('tag_name','').strip()
            sett['last_update_check'] = datetime.date.today().isoformat()
            _save_settings(sett)
            if latest and latest != current_ver: callback(latest, data)
        except Exception: pass
    threading.Thread(target=_w, daemon=True).start()

def _fetch_all_releases(callback):
    def _w():
        try:
            req = urllib.request.Request(_GH_API_RELEASES, headers={'User-Agent':'BCI-KNUCKLE'})
            with urllib.request.urlopen(req, timeout=8) as r: releases = json.loads(r.read())
            callback(releases if isinstance(releases, list) else [])
        except Exception: callback([])
    threading.Thread(target=_w, daemon=True).start()

def _download_and_run_update(release, status_cb):
    assets = release.get('assets', [])
    asset  = next((a for a in assets if a.get('name','').endswith('.exe')), None)
    if not asset: status_cb('no_asset'); return
    url  = asset['browser_download_url']
    dest = os.path.join(os.environ.get('TEMP', _SCRIPT_DIR), asset['name'])
    try:
        status_cb('downloading')
        req = urllib.request.Request(url, headers={'User-Agent':'BCI-KNUCKLE'})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest,'wb') as f:
            while True:
                chunk = r.read(65536)
                if not chunk: break
                f.write(chunk)
        status_cb('done:' + dest)
    except Exception as e: status_cb('error:' + str(e))

# ── Cálculo de rugosidade ─────────────────────────────────────────────────────
def extrair_metricas(caminho):
    img  = Image.open(caminho).convert('L'); img.thumbnail((512,512))
    arr  = np.array(img, dtype=np.float64); media = arr.mean()
    ra   = float(np.mean(np.abs(arr - media)))
    rq   = float(np.sqrt(np.mean((arr - media)**2)))
    flat = np.sort(arr.flatten())
    rz   = float(flat[-5:].mean() - flat[:5].mean())
    gx   = sobel(arr, axis=1); gy = sobel(arr, axis=0)
    grad = float(np.sqrt(gx**2 + gy**2).mean())
    hist, _ = np.histogram(arr.ravel(), bins=256, range=(0,255))
    p = hist/hist.sum(); p = p[p>0]
    ent = float(-np.sum(p*np.log2(p)))
    return dict(ra=ra,rq=rq,rz=rz,grad_energy=grad,entropia=ent,
                media=media,arr=arr,nome=os.path.basename(caminho))

def agregar_metricas(lista):
    keys = ['ra','rq','rz','grad_energy','entropia']; agg = {}
    for k in keys:
        vals = [r[k] for r in lista]
        agg[f'{k}_mean'] = float(np.mean(vals))
        agg[f'{k}_std']  = float(np.std(vals))
        agg[f'{k}_vals'] = vals
    hists = []
    for r in lista:
        c, edges = np.histogram(r['arr'].ravel(), bins=64, range=(0,255))
        hists.append(c/c.max())
    agg['hist_mean'] = np.mean(hists, axis=0); agg['hist_edges'] = edges; agg['n'] = len(lista)
    return agg

def classificar(ra_um):
    if ra_um <  0.1: return 'N1  - Espelho / super-acabamento',    ACCENT
    if ra_um <  0.2: return 'N2  - Retificacao fina',              '#00bcd4'
    if ra_um <  0.4: return 'N3  - Retificacao',                   '#009688'
    if ra_um <  0.8: return 'N4  - Retificacao grossa',            GREEN
    if ra_um <  1.6: return 'N5  - Torneamento / fresamento fino', '#8bc34a'
    if ra_um <  3.2: return 'N6  - Torneamento convencional',      GOLD
    if ra_um <  6.3: return 'N7  - Fresamento grosso',             ORANGE
    if ra_um < 12.5: return 'N8  - Desbaste',                      '#ff5722'
    if ra_um < 25.0: return 'N9  - Fundicao / forjamento',         RED
    return               'N10+ - Superficie bruta',                 '#b71c1c'

# ── Lame / press-fit ──────────────────────────────────────────────────────────
def lame_pressure(delta_mm, R_m, Eo_GPa, ro_m, vo, Ei_GPa, ri_m, vi):
    delta_m = delta_mm*1e-3; Eo_Pa = Eo_GPa*1e9; Ei_Pa = Ei_GPa*1e9
    hub   = (1/Eo_Pa)*((ro_m**2+R_m**2)/(ro_m**2-R_m**2)+vo)
    shaft = (1/Ei_Pa)*((R_m**2+ri_m**2)/(R_m**2-ri_m**2)-vi)
    return (delta_m/(R_m*(hub+shaft)))/1e6

def engagement_force(p_MPa, area_mm2, mu):
    F = p_MPa*area_mm2*mu; return F, F/9.81

def mu_eff_speed(mu_dry, mu_lubed, v_mm_s, v_ref=15.0):
    return mu_lubed + (mu_dry-mu_lubed)*math.exp(-max(v_mm_s,0)/v_ref)

def insertion_curve(p_MPa, d_mm, w_mm, mu_dry, mu_lubed, v_mm_s, n_pts=300, v_ref=15.0):
    mu_v = mu_eff_speed(mu_dry, mu_lubed, v_mm_s, v_ref)
    x    = np.linspace(0, w_mm, n_pts)
    A_x  = math.pi*d_mm*x
    return x, p_MPa*A_x*mu_dry/1000, p_MPa*A_x*mu_v/1000, mu_v

# ── XML / CSV parsing ─────────────────────────────────────────────────────────
def _xml_parse(filepath):
    tree = ET.parse(filepath); root = tree.getroot()
    def gv(tag):
        el = root.find(f'.//{tag}'); return el.get('Value') if el is not None else ''
    meta = {k:gv(t) for k,t in [('date','Date'),('time','Time'),('cycle','Cycle_number'),
            ('program','Measuring_program_name'),('block_x','Block_X'),('block_y','Block_Y')]}
    xs, ys = [], []
    pts = root.findall('.//Point') or root.findall('.//POINT') or root.findall('.//Pt')
    for pt in pts:
        x_el = pt.find('X-ABSOLUTE-') or pt.find('X_-ABSOLUTE-') or pt.find('X-Absolute') or pt.find('X')
        if x_el is None:
            for child in pt:
                if child.tag.upper().startswith('X'):
                    try: float((child.get('Value') or '').replace(',','.')); x_el=child; break
                    except: pass
        y_el = pt.find('Y') or pt.find('y')
        if x_el is not None and y_el is not None:
            try: xs.append(float(x_el.get('Value').replace(',','.'))); ys.append(float(y_el.get('Value').replace(',','.')))
            except: pass
    if not xs: raise ValueError(f'Nenhum ponto valido em {os.path.basename(filepath)}')
    return {'x': xs, 'y': ys, 'meta': meta}

def _xml_auto_classify(filepath):
    if filepath.lower().endswith('.xml'):
        try:
            el = ET.parse(filepath).getroot().find('.//Total_result')
            if el is not None:
                v = el.get('Value','').strip().upper()
                if v in ('OK','NOK'): return v
        except: pass
    name = os.path.basename(filepath).upper()
    p_ok = name.rfind('_OK'); p_nok = name.rfind('_NOK')
    if p_nok == -1 and p_ok == -1: return 'OK'
    if p_nok == -1: return 'OK'
    if p_ok  == -1: return 'NOK'
    return 'NOK' if p_nok > p_ok else 'OK'

def _extract_mp(fp):
    m = re.search(r'MP-\d+', os.path.basename(fp), re.IGNORECASE)
    return m.group(0).upper() if m else ''

def _extract_year(fp):
    m = re.search(r'(20\d{2}|19\d{2})', os.path.basename(fp))
    return m.group(1) if m else ''

def _parse_xml_curve(filepath):
    root = ET.parse(filepath).getroot(); xs, ys = [], []
    for pt in root.findall('.//Point'):
        x_el = pt.find('X-ABSOLUTE-') or pt.find('X_-ABSOLUTE-') or pt.find('X-Absolute') or pt.find('X')
        if x_el is None:
            for c in pt:
                if c.tag.upper().startswith('X') and c.get('Value'):
                    try: float(c.get('Value').replace(',','.')); x_el=c; break
                    except: pass
        y_el = pt.find('Y') or pt.find('y')
        if x_el and y_el:
            try: xs.append(float(x_el.get('Value','').replace(',','.'))); ys.append(float(y_el.get('Value','').replace(',','.')))
            except: pass
    if not xs: raise ValueError(f'Sem pontos: {os.path.basename(filepath)}')
    return np.array(xs), np.array(ys)

def _parse_csv_curve(filepath):
    xs, ys = [], []
    with open(filepath, newline='', encoding='utf-8-sig') as f: raw = f.read(4096)
    sep = ','
    for s in [';','\t',',']:
        if raw.count(s) > raw.count(sep): sep = s
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        for row in csv.reader(f, delimiter=sep):
            if len(row) < 2: continue
            try:
                xs.append(float(row[0].strip().replace(',','.')))
                ys.append(float(row[1].strip().replace(',','.')))
            except: pass
    if len(xs) < 2: raise ValueError(f'Menos de 2 pontos: {os.path.basename(filepath)}')
    return np.array(xs), np.array(ys)

def parse_curve_file(fp):
    ext = os.path.splitext(fp)[1].lower()
    if ext == '.xml': return _parse_xml_curve(fp)
    if ext == '.csv': return _parse_csv_curve(fp)
    raise ValueError(f'Formato nao suportado: {ext}')

class _CurveEntry:
    def __init__(self, filepath, classification):
        self.filepath = filepath
        self.label    = os.path.splitext(os.path.basename(filepath))[0]
        self.classification = classification
        self.data = _xml_parse(filepath)
    @property
    def x(self): return self.data['x']
    @property
    def y(self): return self.data['y']

# ── GoldenCurveAnalyzer ───────────────────────────────────────────────────────
class GoldenCurveAnalyzer:
    def __init__(self, curves, n_interp=500, smooth_sigma=2.0):
        if len(curves) < 3: raise ValueError('Minimo de 3 curvas.')
        self.n_curves = len(curves); self.n_interp = n_interp; self.smooth = smooth_sigma
        self._raw = curves; self._compute()

    def _compute(self):
        x_min = max(c[0].min() for c in self._raw)
        x_max = min(c[0].max() for c in self._raw)
        if x_min >= x_max: raise ValueError('Curvas nao se sobrepoem no eixo X.')
        self.x_grid = np.linspace(x_min, x_max, self.n_interp); mat = []
        for x, y in self._raw:
            idx = np.argsort(x); xu, ui = np.unique(x[idx], return_index=True); yu = y[idx][ui]
            if len(xu) < 2: continue
            mat.append(interp1d(xu, yu, kind='linear', bounds_error=False, fill_value='extrapolate')(self.x_grid))
        self.matrix = np.array(mat); self.n_valid = len(mat)
        self.mean   = np.mean(self.matrix, axis=0); self.median = np.median(self.matrix, axis=0)
        self.std    = np.std(self.matrix, axis=0)
        self.p05    = np.percentile(self.matrix,  5, axis=0); self.p95 = np.percentile(self.matrix, 95, axis=0)
        self.p25    = np.percentile(self.matrix, 25, axis=0); self.p75 = np.percentile(self.matrix, 75, axis=0)
        self.mean_smooth = gaussian_filter1d(self.mean, sigma=self.smooth) if self.smooth > 0 else self.mean.copy()
        self.f_max_per_curve = self.matrix.max(axis=1)

    def fit_polynomial(self, degree=6):
        degree = max(1, min(degree, 12))
        coeffs = np.polyfit(self.x_grid, self.mean_smooth, degree)
        y_fit  = np.poly1d(coeffs)(self.x_grid)
        r2     = 1.0 - np.var(self.mean_smooth - y_fit) / np.var(self.mean_smooth)
        return dict(coeffs=coeffs, y_fit=y_fit, r2=r2, degree=degree)

    def fit_spline(self):
        from scipy.interpolate import UnivariateSpline
        spl   = UnivariateSpline(self.x_grid, self.mean_smooth, s=len(self.x_grid)*0.5, k=3)
        y_fit = spl(self.x_grid)
        r2    = 1.0 - np.var(self.mean_smooth - y_fit) / np.var(self.mean_smooth)
        return dict(y_fit=y_fit, r2=r2)

    def anomaly_score(self, x_new, y_new, sigma_thr=3.0):
        idx = np.argsort(x_new); xu, ui = np.unique(x_new[idx], return_index=True); yu = y_new[idx][ui]
        mask = (self.x_grid >= xu.min()) & (self.x_grid <= xu.max())
        if mask.sum() < 10: return dict(score=None, outside_frac=None, msg='Fora da faixa de X')
        y_i  = interp1d(xu, yu, kind='linear', bounds_error=False, fill_value='extrapolate')(self.x_grid[mask])
        mu   = self.mean[mask]; sg = np.where(self.std[mask] < 1e-9, 1e-9, self.std[mask])
        z    = np.abs(y_i - mu) / sg; outside = (z > sigma_thr).mean()
        score = float(np.clip(z.mean()/sigma_thr*50, 0, 100))
        return dict(score=score, outside_frac=outside,
                    verdict='OK' if outside<0.05 and score<40 else 'NOK', z=z, mask=mask)

# ── Qt style sheet ────────────────────────────────────────────────────────────
QSS = f"""
QMainWindow,QWidget {{ background:{BG}; color:{FG}; font-family:Courier; font-size:9pt; }}
QTabWidget::pane {{ border:none; }}
QTabBar::tab {{ background:{BG2}; color:{FG_DIM}; padding:8px 20px; font-weight:bold; }}
QTabBar::tab:selected {{ background:{BG}; color:{ACCENT}; border-bottom:2px solid {ACCENT}; }}
QPushButton {{ background:{BG2}; color:{FG}; border:none; padding:6px 12px; border-radius:3px; }}
QPushButton:hover {{ background:#1a2a34; color:{ACCENT}; }}
QLineEdit {{ background:{BG2}; color:{ACCENT}; border:1px solid {BORDER}; padding:3px 6px;
             font-weight:bold; font-size:10pt; }}
QListWidget {{ background:{BG3}; color:{FG}; border:none; font-size:8pt; font-family:Consolas; }}
QListWidget::item:selected {{ background:{ACCENT}; color:{BG}; }}
QComboBox {{ background:{BG2}; color:{FG}; border:1px solid {BORDER}; padding:3px 6px; font-size:8pt; }}
QComboBox::drop-down {{ border:none; width:20px; }}
QComboBox QAbstractItemView {{ background:{BG2}; color:{FG}; selection-background-color:{ACCENT}; }}
QScrollBar:vertical {{ background:{BG2}; width:8px; border:none; }}
QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:4px; }}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {{ height:0; }}
QCheckBox {{ color:{FG}; font-size:9pt; font-family:Helvetica; }}
QCheckBox::indicator {{ background:{BG2}; border:1px solid {BORDER}; width:13px; height:13px; }}
QCheckBox::indicator:checked {{ background:{ACCENT}; }}
QGroupBox {{ border:1px solid {BORDER}; margin-top:8px; color:{FG_DIM}; font-size:7pt; }}
QGroupBox::title {{ subcontrol-origin:margin; left:8px; color:{FG_DIM}; }}
QProgressBar {{ background:{BG2}; border:none; height:8px; }}
QProgressBar::chunk {{ background:{ACCENT}; }}
QSplitter::handle {{ background:{BORDER}; }}
"""

# ── Helpers Qt ────────────────────────────────────────────────────────────────
def _lbl(text, color=FG, bold=False, size=9, mono=True):
    w = QLabel(text)
    w.setStyleSheet(f'color:{color};font-weight:{"bold" if bold else "normal"};'
                    f'font-size:{size}pt;font-family:{"Courier" if mono else "Helvetica"};'
                    f'background:transparent;')
    return w

def _btn(text, color=FG, bg=BG2, bold=False):
    w = QPushButton(text)
    w.setStyleSheet(f'background:{bg};color:{color};font-weight:{"bold" if bold else "normal"};'
                    f'padding:6px 10px;border:none;border-radius:3px;')
    w.setCursor(Qt.PointingHandCursor)
    return w

def _entry(default='', color=ACCENT, width=10):
    w = QLineEdit(str(default))
    w.setStyleSheet(f'background:{BG2};color:{color};border:1px solid {BORDER};'
                    f'padding:3px 6px;font-weight:bold;font-size:10pt;')
    w.setMaximumWidth(width * 10)
    return w

def _setup_plot(pw, title='', xlabel='', ylabel=''):
    pw.setBackground(BG3)
    pw.showGrid(x=True, y=True, alpha=0.2)
    if title:  pw.setTitle(title,  color=FG_DIM, size='8pt')
    if xlabel: pw.setLabel('bottom', xlabel, color=FG_DIM)
    if ylabel: pw.setLabel('left',   ylabel, color=FG_DIM)
    pw.getAxis('bottom').setTextPen(pg.mkPen(FG_DIM))
    pw.getAxis('left').setTextPen(pg.mkPen(FG_DIM))
    return pw

def _fill_between(plot, x, y1, y2, color, alpha=30):
    c = QColor(color); c.setAlpha(alpha); brush = pg.mkBrush(c)
    c1 = pg.PlotCurveItem(x, y1, pen=None)
    c2 = pg.PlotCurveItem(x, y2, pen=None)
    fill = pg.FillBetweenItem(c1, c2, brush=brush)
    plot.addItem(fill)
    return fill

def _draw_boxplot(plot, positions, data_lists, color):
    for pos, data in zip(positions, data_lists):
        if not data: continue
        d = np.array(data); q1, med, q3 = np.percentile(d, [25,50,75])
        iqr = q3 - q1; wl = max(d.min(), q1 - 1.5*iqr); wh = min(d.max(), q3 + 1.5*iqr)
        c = QColor(color); c.setAlpha(100)
        # box
        bx = pg.PlotCurveItem([pos-.18,pos-.18,pos+.18,pos+.18,pos-.18],[q1,q3,q3,q1,q1],
                               pen=_pen(color,1.2), fillLevel=q1, brush=pg.mkBrush(c))
        plot.addItem(bx)
        plot.addItem(pg.PlotCurveItem([pos-.18,pos+.18],[med,med],pen=_pen('white',2)))
        for y0,y1_ in [(wl,q1),(q3,wh)]:
            plot.addItem(pg.PlotCurveItem([pos,pos],[y0,y1_],pen=_pen(color,1)))

# ── UpdateBalloon (Qt version) ────────────────────────────────────────────────
class UpdateBalloon(QDialog):
    def __init__(self, parent, new_tag, release, on_details):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self._release = release; self._parent = parent; self._on_details = on_details
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f'QDialog{{background:{BG3};border:1px solid {ACCENT};}}')
        self.setFixedSize(360, 110)
        scr = QApplication.primaryScreen().geometry()
        self.move(scr.width()-370, scr.height()-160)

        lay = QVBoxLayout(self); lay.setContentsMargins(12,10,12,10)
        lay.addWidget(_lbl('BCI  —  ATUALIZAÇÃO DISPONÍVEL', ACCENT, bold=True, size=8))
        lay.addWidget(_lbl(f'Nova versão:  {new_tag}', FG, bold=True, size=10))
        row = QHBoxLayout()
        b1 = _btn('Atualizar agora  ›', BG, ACCENT, bold=True)
        b1.clicked.connect(self._update_now)
        b2 = _btn('Lembrar em 7 dias', FG_DIM, BG3)
        b2.clicked.connect(self._postpone)
        row.addWidget(b1); row.addWidget(b2); lay.addLayout(row)
        self.show()

    def _update_now(self):
        self.hide()
        dlg = UpdateModal(self._parent, self._release)
        dlg.exec_()

    def _postpone(self):
        sett = _get_settings(); sett['last_update_check'] = datetime.date.today().isoformat()
        _save_settings(sett); self.close()

class UpdateModal(QDialog):
    def __init__(self, parent, release):
        super().__init__(parent)
        self.setWindowTitle('Atualização Disponível')
        self.setFixedWidth(420)
        self.setStyleSheet(f'QDialog{{background:{BG};}}')
        lay = QVBoxLayout(self); lay.setSpacing(8); lay.setContentsMargins(24,20,24,20)
        lay.addWidget(_lbl('ATUALIZAÇÃO DISPONÍVEL', ACCENT, bold=True, size=13), 0, Qt.AlignCenter)
        lay.addWidget(_lbl(f'Versão instalada: {__version__}  →  Nova: {release.get("tag_name","")}',
                           FG_DIM, size=9), 0, Qt.AlignCenter)
        notes = release.get('body','').strip()[:300] or 'Acesse o GitHub para ver as novidades.'
        box = QFrame(); box.setStyleSheet(f'background:{BG2};border-radius:4px;')
        bl  = QVBoxLayout(box); bl.setContentsMargins(12,10,12,10)
        bl.addWidget(_lbl('Novidades:', FG_DIM, bold=True, size=8))
        bl.addWidget(_lbl(notes, FG, size=8, mono=False))
        lay.addWidget(box)

        self._lbl_status = _lbl('', FG_DIM, size=8)
        lay.addWidget(self._lbl_status, 0, Qt.AlignCenter)

        has_asset = bool(release.get('assets'))
        if has_asset:
            self._btn_dl = _btn('Baixar e instalar automaticamente', BG, ACCENT, bold=True)
            self._btn_dl.clicked.connect(lambda: self._do_download(release))
            lay.addWidget(self._btn_dl)

        b_gh = _btn('Ver versões no GitHub  ›', '#44aaff', BG)
        b_gh.clicked.connect(lambda: webbrowser.open(release.get('html_url', _GH_RELEASES_PAGE)))
        lay.addWidget(b_gh)

        b_later = _btn('Lembrar em 7 dias', FG_DIM, BG2)
        b_later.clicked.connect(lambda: [self._postpone(), self.accept()])
        lay.addWidget(b_later)

    def _postpone(self):
        sett = _get_settings(); sett['last_update_check'] = datetime.date.today().isoformat()
        _save_settings(sett)

    def _do_download(self, release):
        self._btn_dl.setEnabled(False); self._btn_dl.setText('Baixando...')
        def cb(status):
            if status == 'downloading':
                self._lbl_status.setText('Baixando instalador...')
            elif status.startswith('done:'):
                self._lbl_status.setText('Download concluído! Iniciando...')
                QTimer.singleShot(500, lambda: [os.startfile(status[5:]), QApplication.quit()])
            elif status == 'no_asset':
                self._lbl_status.setText('Sem asset. Abrindo GitHub...')
                webbrowser.open(release.get('html_url', _GH_RELEASES_PAGE))
            else:
                self._lbl_status.setText(f'Erro: {status[6:]}')
        threading.Thread(target=_download_and_run_update, args=(release, cb), daemon=True).start()

# ═══════════════════════════════════════════════════════════════════════════════
# Tab 1 — Análise de Rugosidade
# ═══════════════════════════════════════════════════════════════════════════════
class ImageSlot(QFrame):
    def __init__(self, label, color):
        super().__init__()
        self._color = color; self._paths = []; self._idx = 0
        self.setStyleSheet(f'background:{BG};')
        lay = QVBoxLayout(self); lay.setSpacing(4); lay.setContentsMargins(0,0,0,0)

        top = QHBoxLayout()
        top.addWidget(_lbl(label, color, bold=True, size=10))
        top.addStretch()
        self._btn_add = _btn('+ Adicionar fotos', color, BG)
        self._btn_add.clicked.connect(self._add)
        self._btn_clr = _btn('Limpar', FG_DIM, BG)
        self._btn_clr.clicked.connect(self._clear)
        top.addWidget(self._btn_add); top.addWidget(self._btn_clr)
        lay.addLayout(top)

        self._preview = QLabel()
        self._preview.setFixedSize(270, 165)
        self._preview.setStyleSheet(f'background:{BG3};border:1px solid {BORDER};')
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setText('Nenhuma imagem')
        lay.addWidget(self._preview)

        nav = QHBoxLayout()
        self._btn_prev = _btn('<', FG_DIM, BG); self._btn_prev.setFixedWidth(28)
        self._btn_next = _btn('>', FG_DIM, BG); self._btn_next.setFixedWidth(28)
        self._btn_prev.clicked.connect(self._prev)
        self._btn_next.clicked.connect(self._next)
        self._lbl_nav = _lbl('0 / 0', FG_DIM, size=7)
        nav.addWidget(self._btn_prev); nav.addWidget(self._lbl_nav, 1, Qt.AlignCenter)
        nav.addWidget(self._btn_next)
        lay.addLayout(nav)

        self._lbl_status = _lbl(f'0 fotos  —  minimo {MIN_FOTOS}', FG_DIM, size=8, mono=False)
        lay.addWidget(self._lbl_status)

    def _add(self):
        paths, _ = QFileDialog.getOpenFileNames(self, 'Selecionar imagens', '',
            'Imagens (*.jpg *.jpeg *.png *.bmp *.tif *.tiff);;Todos (*.*)')
        for p in paths:
            if p not in self._paths: self._paths.append(p)
        if self._paths: self._idx = len(self._paths)-1; self._update_preview()
        self._update_status()

    def _clear(self):
        self._paths = []; self._idx = 0
        self._preview.setPixmap(QPixmap()); self._preview.setText('Nenhuma imagem')
        self._update_status()

    def _prev(self):
        if self._paths: self._idx = (self._idx-1) % len(self._paths); self._update_preview()

    def _next(self):
        if self._paths: self._idx = (self._idx+1) % len(self._paths); self._update_preview()

    def _update_preview(self):
        if not self._paths: return
        p = self._paths[self._idx]
        pix = QPixmap(p).scaled(270, 165, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._preview.setPixmap(pix); self._preview.setText('')
        self._lbl_nav.setText(f'{self._idx+1} / {len(self._paths)}  |  {os.path.basename(p)}')

    def _update_status(self):
        n = len(self._paths); falta = max(0, MIN_FOTOS-n)
        if n == 0:   txt, c = f'0 fotos  —  minimo {MIN_FOTOS}', FG_DIM
        elif falta:  txt, c = f'{n} foto(s)  —  faltam {falta}', GOLD
        else:        txt, c = f'{n} fotos  —  OK', GREEN
        self._lbl_status.setText(txt)
        self._lbl_status.setStyleSheet(f'color:{c};font-size:8pt;background:transparent;')
        if n: self._lbl_nav.setText(f'{self._idx+1} / {n}  |  {os.path.basename(self._paths[self._idx])}')
        else: self._lbl_nav.setText('0 / 0')

    @property
    def paths(self): return self._paths


class TabRugosidade(QWidget):
    sig_ra = pyqtSignal(float)

    def __init__(self):
        super().__init__(); self._last_agg_ref = None; self._last_agg_med = None
        self._last_raw_ref = None; self._last_raw_med = None; self._fator = None
        self._build()

    def _build(self):
        root = QHBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(16)

        # ── Coluna esquerda ───────────────────────────────────────────────────
        left = QVBoxLayout(); left.setSpacing(8)

        self._slot_ref = ImageSlot('REFERENCIA', GOLD)
        self._slot_med = ImageSlot('PECA A MEDIR', ACCENT)
        left.addWidget(self._slot_ref)

        ra_box = QGroupBox('Ra real da referencia (um)')
        ra_box.setStyleSheet(f'QGroupBox{{border:1px solid {BORDER};margin-top:8px;color:{FG_DIM};font-size:7pt;}}'
                             f'QGroupBox::title{{subcontrol-origin:margin;left:8px;}}')
        ra_lay = QHBoxLayout(ra_box)
        self._entry_ra = _entry('1.6', GOLD, 8)
        ra_lay.addWidget(self._entry_ra)
        ra_lay.addWidget(_lbl('ex: 0.8 / 1.6 / 3.2 / 6.3', FG_DIM, size=8, mono=False))
        left.addWidget(ra_box)
        left.addWidget(self._slot_med)

        self._btn_anal = _btn('ANALISAR', ACCENT, BG2, bold=True)
        self._btn_anal.setFixedHeight(38)
        self._btn_anal.clicked.connect(self._analisar)
        left.addWidget(self._btn_anal)

        warn = QLabel('Mesma iluminacao e magnificacao nas duas pecas.\nMinimo 10 fotos por conjunto.')
        warn.setStyleSheet(f'background:#1a1000;color:#7a6040;padding:8px;font-size:8pt;')
        warn.setWordWrap(True)
        left.addWidget(warn)
        left.addStretch()
        root.addLayout(left, 0)

        # ── Coluna direita ────────────────────────────────────────────────────
        right = QVBoxLayout(); right.setSpacing(6)

        # Fator
        frow = QHBoxLayout()
        frow.addWidget(_lbl('Fator de calibracao:', FG_DIM, size=8))
        self._lbl_fator = _lbl('—', GOLD, bold=True, size=10)
        frow.addWidget(self._lbl_fator); frow.addWidget(_lbl('um/u.i.', FG_DIM, size=8))
        frow.addStretch(); right.addLayout(frow)

        # Tabela de metricas
        grid = QGridLayout(); grid.setSpacing(2)
        grid.addWidget(_lbl('REFERENCIA', GOLD, bold=True, size=7), 0, 1, Qt.AlignCenter)
        grid.addWidget(_lbl('PECA MEDIDA', ACCENT, bold=True, size=7), 0, 2, Qt.AlignCenter)
        self._metric_cells = {}
        labels = [('Ra  [um]','ra'),('Rq  [um]','rq'),('Rz  [um]','rz'),
                  ('Grad.','grad_energy'),('Entropia','entropia')]
        for ri, (ltext, key) in enumerate(labels):
            grid.addWidget(_lbl(ltext, FG_DIM, size=8), ri+1, 0)
            for ci, sn in enumerate(('ref','med')):
                cor = GOLD if sn=='ref' else ACCENT
                lv = _lbl('—', cor, bold=True, size=10)
                ld = _lbl('', FG_DIM, size=6)
                cell = QVBoxLayout(); cell.setSpacing(0); cell.addWidget(lv); cell.addWidget(ld)
                frame = QFrame(); frame.setStyleSheet(f'background:{BG2};border-radius:3px;')
                frame.setLayout(cell); frame.setContentsMargins(4,2,4,2)
                grid.addWidget(frame, ri+1, ci+1)
                self._metric_cells[(sn,key)] = (lv, ld)
        right.addLayout(grid)

        # Classificacao
        self._lbl_classe = _lbl('—', FG, bold=True, size=9)
        right.addWidget(self._lbl_classe)
        self._lbl_intervalo = _lbl('', FG_DIM, size=7)
        right.addWidget(self._lbl_intervalo)

        # Graficos pyqtgraph ── 3 plots em linha
        plot_lay = QHBoxLayout(); plot_lay.setSpacing(6)
        self._pw_hist = pg.PlotWidget(); _setup_plot(self._pw_hist, 'Histograma', 'Tom de cinza', 'Frequencia norm.')
        self._pw_box  = pg.PlotWidget(); _setup_plot(self._pw_box,  'Ra por imagem (boxplot)', 'Conjunto', 'Ra [u.i.]')
        self._pw_prof = pg.PlotWidget(); _setup_plot(self._pw_prof, 'Ra por foto (calibrado)', 'Foto', 'Ra [um]')
        for pw in (self._pw_hist, self._pw_box, self._pw_prof):
            pw.setMinimumHeight(200)
            plot_lay.addWidget(pw)
        right.addLayout(plot_lay, 1)
        root.addLayout(right, 1)

    def _analisar(self):
        if len(self._slot_ref.paths) < MIN_FOTOS:
            QMessageBox.warning(self, 'Atencao', f'Referencia: {len(self._slot_ref.paths)} foto(s). Minimo: {MIN_FOTOS}.'); return
        if len(self._slot_med.paths) < MIN_FOTOS:
            QMessageBox.warning(self, 'Atencao', f'Peca a medir: {len(self._slot_med.paths)} foto(s). Minimo: {MIN_FOTOS}.'); return
        try:
            ra_real = float(self._entry_ra.text().replace(',','.'))
            if ra_real <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, 'Atencao', 'Informe o Ra real da referencia (ex: 1.6).'); return

        self._btn_anal.setEnabled(False); self._btn_anal.setText('Processando...')
        QApplication.processEvents()
        try:
            raw_ref = [extrair_metricas(p) for p in self._slot_ref.paths]
            raw_med = [extrair_metricas(p) for p in self._slot_med.paths]
            agg_ref = agregar_metricas(raw_ref); agg_med = agregar_metricas(raw_med)
            fator   = ra_real / agg_ref['ra_mean']
            for key in ('ra','rq','rz'):
                agg_ref[f'{key}_cal']     = agg_ref[f'{key}_mean']*fator
                agg_ref[f'{key}_cal_std'] = agg_ref[f'{key}_std'] *fator
                agg_med[f'{key}_cal']     = agg_med[f'{key}_mean']*fator
                agg_med[f'{key}_cal_std'] = agg_med[f'{key}_std'] *fator
            self._last_agg_ref = agg_ref; self._last_agg_med = agg_med
            self._last_raw_ref = raw_ref; self._last_raw_med = raw_med; self._fator = fator
            self.sig_ra.emit(agg_med['ra_cal'])
            self._show_results(agg_ref, agg_med, fator, raw_ref, raw_med)
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))
        finally:
            self._btn_anal.setEnabled(True); self._btn_anal.setText('ANALISAR')

    def _show_results(self, ref, med, fator, raw_ref, raw_med):
        self._lbl_fator.setText(f'{fator:.5f}')
        for sn, agg in (('ref',ref),('med',med)):
            for key in ('ra','rq','rz'):
                v, s = agg[f'{key}_cal'], agg[f'{key}_cal_std']
                self._metric_cells[(sn,key)][0].setText(f'{v:.3f}')
                self._metric_cells[(sn,key)][1].setText(f'+- {s:.3f}  (n={agg["n"]})')
            for key in ('grad_energy','entropia'):
                v, s = agg[f'{key}_mean'], agg[f'{key}_std']
                self._metric_cells[(sn,key)][0].setText(f'{v:.2f}')
                self._metric_cells[(sn,key)][1].setText(f'+- {s:.2f}')
        ra = med['ra_cal']; ra_std = med['ra_cal_std']
        cls_txt, cls_cor = classificar(ra)
        self._lbl_classe.setText(f'Ra = {ra:.3f} um   →   {cls_txt}')
        self._lbl_classe.setStyleSheet(f'color:{cls_cor};font-weight:bold;font-size:9pt;background:transparent;')
        self._lbl_intervalo.setText(f'Intervalo (1dp):  {max(0,ra-ra_std):.3f}  a  {ra+ra_std:.3f} um')
        self._plot_graphs(ref, med, raw_ref, raw_med, fator)

    def _plot_graphs(self, ref, med, raw_ref, raw_med, fator):
        # Histograma
        pw = self._pw_hist; pw.clear()
        edges = ref['hist_edges']; mid = (edges[:-1]+edges[1:])/2
        pw.plot(mid, ref['hist_mean'], pen=_pen(GOLD,1.5), name='Referencia')
        pw.plot(mid, med['hist_mean'], pen=_pen(ACCENT,1.5), name='Medida')
        pw.addLegend(offset=(5,5))

        # Boxplot Ra calibrado
        pw2 = self._pw_box; pw2.clear()
        ref_vals = [m['ra']*fator for m in raw_ref]
        med_vals = [m['ra']*fator for m in raw_med]
        _draw_boxplot(pw2, [0], [ref_vals], GOLD)
        _draw_boxplot(pw2, [1], [med_vals], ACCENT)
        ax = pw2.getAxis('bottom'); ax.setTicks([[(0,'Referencia'),(1,'Medida')]])

        # Ra por foto
        pw3 = self._pw_prof; pw3.clear()
        rv = [m['ra']*fator for m in raw_ref]
        mv = [m['ra']*fator for m in raw_med]
        pw3.plot(list(range(len(rv))), rv, pen=_pen(GOLD,1.5), symbol='o', symbolSize=5,
                 symbolBrush=_brush(GOLD), name='Referencia')
        pw3.plot(list(range(len(mv))), mv, pen=_pen(ACCENT,1.5), symbol='o', symbolSize=5,
                 symbolBrush=_brush(ACCENT), name='Medida')
        pw3.addLegend(offset=(5,5))


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 2 — Cálculo de Interferência
# ═══════════════════════════════════════════════════════════════════════════════
class TabInterferencia(QWidget):
    def __init__(self):
        super().__init__(); self._resultado = None; self._build()

    def _field(self, label, default, lay, color=ACCENT):
        row = QHBoxLayout()
        row.addWidget(_lbl(label, FG_DIM, size=8))
        e = _entry(default, color, 9)
        row.addWidget(e); lay.addLayout(row)
        return e

    def _build(self):
        root = QHBoxLayout(self); root.setContentsMargins(12,12,12,12); root.setSpacing(12)

        # ── Painel esquerdo — inputs ──────────────────────────────────────────
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f'QScrollArea{{background:{BG};border:none;}}')
        scroll.setFixedWidth(380)
        inner = QWidget(); inner.setStyleSheet(f'background:{BG};')
        form  = QVBoxLayout(inner); form.setSpacing(6); form.setContentsMargins(8,8,8,8)

        def grp(title):
            g = QGroupBox(title)
            g.setStyleSheet(f'QGroupBox{{border:1px solid {BORDER};margin-top:8px;color:{FG_DIM};font-size:7pt;}}'
                            f'QGroupBox::title{{subcontrol-origin:margin;left:8px;}}')
            l = QVBoxLayout(g); l.setSpacing(3); return g, l

        g, l = grp('EIXO (Shaft)'); form.addWidget(g)
        self._Ei   = self._field('Young Ei [GPa]',     '200',  l)
        self._vi   = self._field('Poisson vi',          '0.3',  l)
        self._di   = self._field('Diam. interno di [mm]','0',   l)
        self._d    = self._field('Diam. nominal d [mm]','51.988',l)
        self._tol_sh_up = self._field('Tol. superior eixo [mm]','0.050',l)
        self._tol_sh_lo = self._field('Tol. inferior eixo [mm]','0.030',l)
        self._ra_eixo   = self._field('Ra eixo [um]',  '0.8',  l)

        g, l = grp('CUBO / KNUCKLE (Hub)'); form.addWidget(g)
        self._Eo   = self._field('Young Eo [GPa]', '200',  l)
        self._vo   = self._field('Poisson vo',      '0.3',  l)
        self._do   = self._field('Diam. externo do [mm]','100', l)
        self._dh   = self._field('Diam. nominal furo dh [mm]','51.988',l)
        self._tol_ho_up = self._field('Tol. superior furo [mm]','0',    l)
        self._tol_ho_lo = self._field('Tol. inferior furo [mm]','-0.016',l)
        self._ra_hub    = self._field('Ra cubo [um]',  '1.6',  l)

        g, l = grp('GEOMETRIA DA INTERFACE'); form.addWidget(g)
        self._w_nom = self._field('Largura nominal [mm]', '27',   l)
        self._w_lo  = self._field('Largura lower [mm]',   '25.5', l)
        self._w_up  = self._field('Largura upper [mm]',   '28.5', l)

        g, l = grp('ATRITO'); form.addWidget(g)
        self._mu_dry   = self._field('mu seco',       '0.40', l)
        self._mu_lubed = self._field('mu lubrificado','0.21', l)

        btn_calc = _btn('>> CALCULAR INTERFERENCIA', ACCENT, BG2, bold=True)
        btn_calc.setFixedHeight(40); btn_calc.clicked.connect(self._calcular)
        form.addWidget(btn_calc)

        g, l = grp('RESULTADOS'); form.addWidget(g)
        self._result_labels = {}
        for key, txt in [('shaft_range','Eixo [mm]'),('hub_range','Furo [mm]'),
                         ('delta_max','delta_max [mm]'),('delta_min','delta_min [mm]'),
                         ('corr_rug','Corr. rugosidade [um]'),('delta_max_eff','delta_max_eff [mm]'),
                         ('pmax','p_max [MPa]'),('pmin','p_min [MPa]')]:
            row = QHBoxLayout()
            row.addWidget(_lbl(txt, FG_DIM, size=8))
            v = _lbl('—', ACCENT, bold=True, size=9); row.addWidget(v)
            l.addLayout(row); self._result_labels[key] = v

        g, l = grp('VELOCIDADE DE INSERÇÃO'); form.addWidget(g)
        self._v_ins = self._field('Velocidade [mm/s]','5.0',l,GOLD)
        b_ins = _btn('Atualizar Curva', GOLD, BG2)
        b_ins.clicked.connect(self._update_insertion)
        l.addWidget(b_ins)

        self._lbl_status = _lbl('', GREEN, size=8, mono=False)
        self._lbl_status.setWordWrap(True)
        form.addWidget(self._lbl_status)
        form.addStretch()
        scroll.setWidget(inner); root.addWidget(scroll)

        # ── Painel direito — plots ────────────────────────────────────────────
        right = QVBoxLayout()
        self._pw_bar = pg.PlotWidget()
        _setup_plot(self._pw_bar, 'Forca de encaixe por caso', 'Caso', 'Forca [kN]')
        self._pw_bar.setMinimumHeight(220)

        self._pw_ins = pg.PlotWidget()
        _setup_plot(self._pw_ins, 'Curva de insercao — Stribeck', 'mm', 'kN')
        self._pw_ins.setMinimumHeight(220)

        right.addWidget(self._pw_bar, 1)
        right.addWidget(self._pw_ins, 1)
        root.addLayout(right, 1)

    def _v(self, entry):
        return float(entry.text().replace(',','.'))

    def _calcular(self):
        try:
            Ei=self._v(self._Ei); vi=self._v(self._vi); di=self._v(self._di); d=self._v(self._d)
            sh_up=self._v(self._tol_sh_up); sh_lo=self._v(self._tol_sh_lo)
            Eo=self._v(self._Eo); vo=self._v(self._vo); do_=self._v(self._do); dh=self._v(self._dh)
            ho_up=self._v(self._tol_ho_up); ho_lo=self._v(self._tol_ho_lo)
            w_nom=self._v(self._w_nom); w_lo=self._v(self._w_lo); w_up=self._v(self._w_up)
            mu_dry=self._v(self._mu_dry); mu_lub=self._v(self._mu_lubed)
            ra_e=self._v(self._ra_eixo); ra_h=self._v(self._ra_hub)
        except ValueError:
            QMessageBox.critical(self,'Erro','Verifique os valores. Use ponto como decimal.'); return

        sh_max=d+sh_up; sh_min=d+sh_lo; ho_max=dh+ho_up; ho_min=dh+ho_lo
        delta_max=(sh_max-ho_min)/2; delta_min=(sh_min-ho_max)/2
        corr=(ra_e+ra_h)*1e-3
        dmax_eff=delta_max-corr; dmin_eff=delta_min-corr
        if dmax_eff<=0:
            QMessageBox.critical(self,'Erro',f'Interferencia efetiva <= 0 ({dmax_eff:.4f} mm)'); return
        R=d/(2e3); ri=di/(2e3); ro=do_/(2e3)
        pmax=lame_pressure(dmax_eff,R,Eo,ro,vo,Ei,ri,vi)
        pmin=lame_pressure(dmin_eff,R,Eo,ro,vo,Ei,ri,vi) if dmin_eff>0 else 0.0
        A_nom=math.pi*d*w_nom; A_lo=math.pi*d*w_lo; A_up=math.pi*d*w_up
        F_nd,_=engagement_force(pmax,A_nom,mu_dry); F_nl,_=engagement_force(pmax,A_nom,mu_lub)
        F_ld,_=engagement_force(pmax,A_lo,mu_dry);  F_ll,_=engagement_force(pmax,A_lo,mu_lub)
        F_ud,_=engagement_force(pmax,A_up,mu_dry);  F_ul,_=engagement_force(pmax,A_up,mu_lub)
        self._resultado = dict(d=d,di=di,do_=do_,Ei=Ei,vi=vi,Eo=Eo,vo=vo,
            sh_max=sh_max,sh_min=sh_min,ho_max=ho_max,ho_min=ho_min,
            delta_max=delta_max,delta_min=delta_min,corr=corr,
            dmax_eff=dmax_eff,dmin_eff=dmin_eff,pmax=pmax,pmin=pmin,
            w_nom=w_nom,w_lo=w_lo,w_up=w_up,mu_dry=mu_dry,mu_lub=mu_lub,
            F_nd=F_nd,F_nl=F_nl,F_ld=F_ld,F_ll=F_ll,F_ud=F_ud,F_ul=F_ul)

        self._result_labels['shaft_range'].setText(f'{sh_min:.4f}  a  {sh_max:.4f}')
        self._result_labels['hub_range'].setText(f'{ho_min:.4f}  a  {ho_max:.4f}')
        self._result_labels['delta_max'].setText(f'{delta_max:.4f}')
        self._result_labels['delta_min'].setText(f'{delta_min:.4f}' + (' FOLGA!' if delta_min<0 else ''))
        self._result_labels['corr_rug'].setText(f'{corr*1e3:.2f}  ({ra_e:.2f}+{ra_h:.2f})')
        self._result_labels['delta_max_eff'].setText(f'{dmax_eff:.4f}')
        self._result_labels['pmax'].setText(f'{pmax:.4f}')
        self._result_labels['pmin'].setText(f'{pmin:.4f}' if pmin>0 else 'folga')
        self._lbl_status.setText(f'dmax_eff={dmax_eff:.4f} mm  pmax={pmax:.2f} MPa  F_nom_seco={F_nd:.0f} N')
        self._plot_bar(); self._update_insertion()

    def _plot_bar(self):
        r = self._resultado; pw = self._pw_bar; pw.clear()
        casos = ['Nominal','Lower','Upper']
        dry   = [r['F_nd']/1000, r['F_ld']/1000, r['F_ud']/1000]
        lubed = [r['F_nl']/1000, r['F_ll']/1000, r['F_ul']/1000]
        x = np.arange(3)
        b1 = pg.BarGraphItem(x=x-0.2, height=dry,   width=0.35, brush=_brush(ACCENT,200), pen=_pen(BG3,0.5))
        b2 = pg.BarGraphItem(x=x+0.2, height=lubed, width=0.35, brush=_brush(GREEN,200),  pen=_pen(BG3,0.5))
        pw.addItem(b1); pw.addItem(b2)
        for xi, (d, l) in enumerate(zip(dry,lubed)):
            t1=pg.TextItem(f'{d:.2f}',color=ACCENT,anchor=(0.5,1)); t1.setPos(xi-0.2,d); pw.addItem(t1)
            t2=pg.TextItem(f'{l:.2f}',color=GREEN,  anchor=(0.5,1)); t2.setPos(xi+0.2,l); pw.addItem(t2)
        pw.getAxis('bottom').setTicks([[(i,c) for i,c in enumerate(casos)]])
        pw.setTitle(f'Forca de encaixe  |  p={r["pmax"]:.2f} MPa  |  dmax={r["delta_max"]:.4f} mm',
                    color=FG_DIM, size='8pt')

    def _update_insertion(self):
        if self._resultado is None: return
        try: v = float(self._v_ins.text().replace(',','.'))
        except: return
        r = self._resultado; pw = self._pw_ins; pw.clear()
        x, F_dry, F_lub, mu_v = insertion_curve(r['pmax'],r['d'],r['w_nom'],r['mu_dry'],r['mu_lub'],v)
        pw.plot(x, F_dry, pen=_pen(ACCENT,2.5), name=f'Seco  mu={r["mu_dry"]:.2f}')
        pw.plot(x, F_lub, pen=_pen(GREEN, 2.0), name=f'Lubr. {v:.0f} mm/s  mu_ef={mu_v:.3f}')
        pw.addLegend(offset=(5,5))
        pw.setTitle(f'Curva de insercao  |  p={r["pmax"]:.2f} MPa  |  Stribeck v_ref=15 mm/s',
                    color=FG_DIM, size='8pt')

    def set_ra_sede(self, ra):
        self._ra_hub.setText(f'{ra:.3f}')


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 3 — Comparador de Curvas XML
# ═══════════════════════════════════════════════════════════════════════════════
class TabXMLComparator(QWidget):
    def __init__(self):
        super().__init__()
        self.entries: list[_CurveEntry] = []
        self._shown: list[_CurveEntry]  = []
        self._build()

    def _build(self):
        root = QHBoxLayout(self); root.setContentsMargins(8,8,8,8); root.setSpacing(8)

        # ── Painel esquerdo ───────────────────────────────────────────────────
        left = QFrame(); left.setFixedWidth(290)
        left.setStyleSheet(f'QFrame{{background:{_C_PANEL};border-radius:4px;}}')
        llay = QVBoxLayout(left); llay.setContentsMargins(8,12,8,12); llay.setSpacing(6)

        llay.addWidget(_lbl('Force Curve Comparator', '#89b4fa', bold=True, size=11, mono=False))
        llay.addWidget(_lbl('Knuckle Press-Fit  |  Stellantis', FG_DIM, size=8, mono=False))

        # Filtros
        ff = QGridLayout()
        ff.addWidget(_lbl('Ponto:', FG_DIM, size=8), 0, 0)
        self._cb_mp = QComboBox(); self._cb_mp.addItem('Todos')
        self._cb_mp.currentTextChanged.connect(lambda _: (self._refresh_list(), self._plot()))
        ff.addWidget(self._cb_mp, 0, 1)
        ff.addWidget(_lbl('Ano:', FG_DIM, size=8), 1, 0)
        self._cb_year = QComboBox(); self._cb_year.addItem('Todos')
        self._cb_year.currentTextChanged.connect(lambda _: (self._refresh_list(), self._plot()))
        ff.addWidget(self._cb_year, 1, 1)
        llay.addLayout(ff)

        self._lb = QListWidget()
        self._lb.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._lb.itemSelectionChanged.connect(self._on_select)
        llay.addWidget(self._lb, 1)

        self._lbl_detail = _lbl('', FG_DIM, size=8, mono=False)
        self._lbl_detail.setWordWrap(True)
        llay.addWidget(self._lbl_detail)

        def sep(): f=QFrame(); f.setFrameShape(QFrame.HLine); f.setStyleSheet(f'color:{BORDER};'); return f

        llay.addWidget(sep())
        for txt, fn in [('➕  Adicionar XML(s)', self._add_files),
                        ('🗑  Remover selecionado', self._remove_selected),
                        ('✏  Renomear label', self._rename_label)]:
            b = _btn(txt, '#cdd6f4', '#313244'); b.clicked.connect(fn); llay.addWidget(b)

        llay.addWidget(_lbl('Classificacao manual:', FG_DIM, size=8, mono=False))
        cf = QHBoxLayout()
        b_ok  = _btn('✔  OK',  _C_OK,  '#1e4d2b'); b_ok.clicked.connect(lambda: self._set_class('OK'))
        b_nok = _btn('✘  NOK', _C_NOK, '#4d1e1e'); b_nok.clicked.connect(lambda: self._set_class('NOK'))
        cf.addWidget(b_ok); cf.addWidget(b_nok); llay.addLayout(cf)

        llay.addWidget(sep())
        for txt, fn, c in [('📊  Plotar / Atualizar', self._plot, '#89b4fa'),
                            ('💾  Salvar grafico',     self._save_plot, FG_DIM),
                            ('🗑  Limpar tudo',        self._clear_all, FG_DIM)]:
            b = _btn(txt, c, '#1e3a5f' if c == '#89b4fa' else '#313244')
            b.clicked.connect(fn); llay.addWidget(b)

        llay.addWidget(sep())
        llay.addWidget(_lbl('Janela de Aprovacao', '#89b4fa', bold=True, size=9, mono=False))
        wg = QGridLayout()
        def we(row, col, label, default):
            wg.addWidget(_lbl(label, FG_DIM, size=8), row, col*2)
            e = QLineEdit(default); e.setStyleSheet(f'background:#313244;color:#cdd6f4;border:none;padding:2px;')
            e.setMaximumWidth(70); wg.addWidget(e, row, col*2+1); return e
        self._wx0=we(0,0,'X min','115'); self._wx1=we(0,1,'X max','130')
        self._wy0=we(1,0,'Y min','9.80'); self._wy1=we(1,1,'Y max','58.00')
        llay.addLayout(wg)
        b_ap = _btn('↺  Aplicar Janela', '#89b4fa', '#1e3a5f')
        b_ap.clicked.connect(self._plot); llay.addWidget(b_ap)

        llay.addWidget(sep())
        vg = QGridLayout()
        vg.addWidget(_lbl('Max curvas:', FG_DIM, size=8), 0, 0)
        self._cb_max = QComboBox(); self._cb_max.addItems(['Todas','1','2','3','5','10','20','50'])
        self._cb_max.currentTextChanged.connect(lambda _: self._plot())
        vg.addWidget(self._cb_max, 0, 1)
        self._chk_legend = QCheckBox('Mostrar legenda')
        self._chk_legend.setChecked(True); self._chk_legend.stateChanged.connect(lambda _: self._plot())
        vg.addWidget(self._chk_legend, 1, 0, 1, 2)
        llay.addLayout(vg)

        self._lbl_status = _lbl('Nenhum arquivo carregado.', FG_DIM, size=8, mono=False)
        self._lbl_status.setWordWrap(True)
        llay.addWidget(self._lbl_status)
        root.addWidget(left)

        # ── Painel direito — 2 plots OK/NOK ──────────────────────────────────
        right = QWidget(); rlay = QVBoxLayout(right); rlay.setContentsMargins(0,0,0,0)
        self._glw = pg.GraphicsLayoutWidget(); self._glw.setBackground('#181825')
        self._p_ok  = self._glw.addPlot(title='OK')
        self._p_nok = self._glw.addPlot(title='NOK')
        for p, color in [(self._p_ok,_C_OK),(self._p_nok,_C_NOK)]:
            p.setLabel('bottom','Curso [mm]'); p.setLabel('left','Forca [kN]')
            p.showGrid(x=True,y=True,alpha=0.3)
            p.setTitle(p.titleLabel.text, color=color, size='12pt')
        rlay.addWidget(self._glw)
        root.addWidget(right, 1)

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self,'Selecionar XML(s)','','XML (*.xml);;Todos (*.*)')
        if not paths: return
        added = errs = 0
        for p in paths:
            if any(e.filepath==p for e in self.entries): continue
            try:
                cls = _xml_auto_classify(p)
                self.entries.append(_CurveEntry(p, cls)); added += 1
            except Exception as e:
                errs += 1
        self._update_filters(); self._refresh_list(); self._plot()
        self._lbl_status.setText(f'+{added} arquivo(s).  Total: {len(self.entries)}.' +
                                  (f'  {errs} erro(s).' if errs else ''))

    def _remove_selected(self):
        for item in self._lb.selectedItems():
            idx = self._lb.row(item)
            if 0 <= idx < len(self._shown):
                self.entries.remove(self._shown[idx])
        self._update_filters(); self._refresh_list(); self._plot()

    def _rename_label(self):
        sel = self._lb.selectedItems()
        if not sel: return
        idx = self._lb.row(sel[0])
        if 0 <= idx < len(self._shown):
            dlg = QDialog(self); dlg.setWindowTitle('Renomear')
            dlg.setStyleSheet(f'background:{BG};')
            dlay = QVBoxLayout(dlg)
            dlay.addWidget(_lbl('Novo label:', FG_DIM, size=9))
            entry = QLineEdit(self._shown[idx].label)
            entry.setStyleSheet(f'background:{BG2};color:{ACCENT};border:1px solid {BORDER};padding:4px;')
            dlay.addWidget(entry)
            bb = QHBoxLayout(); ok = _btn('OK',ACCENT,BG2); cancel = _btn('Cancelar',FG_DIM,BG2)
            ok.clicked.connect(dlg.accept); cancel.clicked.connect(dlg.reject)
            bb.addWidget(ok); bb.addWidget(cancel); dlay.addLayout(bb)
            if dlg.exec_() == QDialog.Accepted:
                self._shown[idx].label = entry.text(); self._refresh_list()

    def _set_class(self, cls):
        for item in self._lb.selectedItems():
            idx = self._lb.row(item)
            if 0 <= idx < len(self._shown):
                self._shown[idx].classification = cls
        self._refresh_list(); self._plot()

    def _on_select(self):
        sel = self._lb.selectedItems()
        if not sel: return
        idx = self._lb.row(sel[0])
        if 0 <= idx < len(self._shown):
            e = self._shown[idx]
            m = e.meta; self._lbl_detail.setText(
                f'{e.classification}  |  {m.get("date","")} {m.get("time","")}  |  '
                f'Ciclo:{m.get("cycle","")}  |  MP:{_extract_mp(e.filepath)}')

    def _update_filters(self):
        mps   = sorted(set(filter(None,(_extract_mp(e.filepath)   for e in self.entries))))
        years = sorted(set(filter(None,(_extract_year(e.filepath) for e in self.entries))))
        self._cb_mp.blockSignals(True); self._cb_year.blockSignals(True)
        cur_mp = self._cb_mp.currentText(); cur_yr = self._cb_year.currentText()
        self._cb_mp.clear();   self._cb_mp.addItems(['Todos']+mps)
        self._cb_year.clear(); self._cb_year.addItems(['Todos']+years)
        self._cb_mp.setCurrentText(cur_mp   if cur_mp   in ['Todos']+mps   else 'Todos')
        self._cb_year.setCurrentText(cur_yr if cur_yr   in ['Todos']+years else 'Todos')
        self._cb_mp.blockSignals(False); self._cb_year.blockSignals(False)

    def _filtered(self):
        mp=self._cb_mp.currentText(); yr=self._cb_year.currentText()
        return [e for e in self.entries
                if (mp=='Todos' or _extract_mp(e.filepath)==mp)
                and (yr=='Todos' or _extract_year(e.filepath)==yr)]

    def _refresh_list(self):
        self._shown = self._filtered(); self._lb.clear()
        for e in self._shown:
            c = _C_OK if e.classification=='OK' else _C_NOK
            item = QListWidgetItem(f'[{e.classification}]  {e.label}')
            item.setForeground(QColor(c)); self._lb.addItem(item)

    def _get_window(self):
        try:
            return (float(self._wx0.text()), float(self._wx1.text()),
                    float(self._wy0.text()), float(self._wy1.text()))
        except: return None

    def _plot(self):
        self._p_ok.clear(); self._p_nok.clear()
        ok_entries  = [e for e in self._shown if e.classification=='OK']
        nok_entries = [e for e in self._shown if e.classification=='NOK']
        mx_txt = self._cb_max.currentText()
        mx = None if mx_txt=='Todas' else int(mx_txt)
        ok_pal  = [f'#{int(46+i*(206-46)/max(1,len(ok_entries)-1)):02x}cc{int(113+i*(177-113)/max(1,len(ok_entries)-1)):02x}' for i in range(len(ok_entries))]
        nok_pal = [f'#e7{int(60+i*(130-60)/max(1,len(nok_entries)-1)):02x}3c' for i in range(len(nok_entries))]
        for entries, plot, palette in [(ok_entries,self._p_ok,ok_pal),(nok_entries,self._p_nok,nok_pal)]:
            shown = entries[:mx] if mx else entries
            legend = plot.addLegend() if (self._chk_legend.isChecked() and shown) else None
            for i, e in enumerate(shown):
                c = palette[i % len(palette)] if palette else '#ffffff'
                plot.plot(e.x, e.y, pen=_pen(c,1.2), name=e.label[:20] if legend else None)
        win = self._get_window()
        if win:
            x0,x1,y0,y1 = win
            for plot in (self._p_ok, self._p_nok):
                ri = pg.LinearRegionItem(values=[x0,x1], movable=False,
                    brush=pg.mkBrush(255,255,0,20), pen=_pen('#ffff00',1))
                plot.addItem(ri)
        n_ok=len(ok_entries); n_nok=len(nok_entries)
        self._lbl_status.setText(f'OK: {n_ok}  |  NOK: {n_nok}  |  Total: {n_ok+n_nok}')

    def _save_plot(self):
        if not self.entries: QMessageBox.information(self,'Salvar','Nenhuma curva carregada.'); return
        path, _ = QFileDialog.getSaveFileName(self,'Salvar grafico','force_curves.png',
                                              'PNG (*.png);;SVG (*.svg)')
        if path:
            exporter = pg.exporters.ImageExporter(self._glw.scene())
            exporter.export(path)
            self._lbl_status.setText(f'Salvo: {os.path.basename(path)}')

    def _clear_all(self):
        self.entries.clear(); self._shown.clear(); self._lb.clear()
        self._p_ok.clear(); self._p_nok.clear()
        self._lbl_status.setText('Nenhum arquivo carregado.')


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 4 — Golden Curve Analyzer
# ═══════════════════════════════════════════════════════════════════════════════
class TabGoldenCurve(QWidget):
    def __init__(self, get_xml_tab):
        super().__init__()
        self._get_xml_tab = get_xml_tab
        self._files=[]; self._curves=[]; self._analyzer=None
        self._poly_result=None; self._spl_result=None; self._test_curves=[]
        self._build()

    def _btn_side(self, text, fn, color=ACCENT, bg=BG2):
        b = _btn(text, color, bg); b.clicked.connect(fn); return b

    def _build(self):
        root = QHBoxLayout(self); root.setContentsMargins(8,8,8,8); root.setSpacing(8)

        # ── Painel esquerdo ───────────────────────────────────────────────────
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f'QScrollArea{{background:{_C_PANEL};border:none;}}')
        scroll.setFixedWidth(320)
        inner = QWidget(); inner.setStyleSheet(f'background:{_C_PANEL};')
        slay  = QVBoxLayout(inner); slay.setSpacing(6); slay.setContentsMargins(8,12,8,12)

        slay.addWidget(_lbl('GOLDEN CURVE ANALYZER', ACCENT, bold=True, size=10))
        slay.addWidget(_lbl('Curva teorica a partir de N curvas OK', FG_DIM, size=8, mono=False))

        def hsep(): f=QFrame(); f.setFrameShape(QFrame.HLine); f.setStyleSheet(f'color:{BORDER};'); return f

        slay.addWidget(hsep())
        slay.addWidget(_lbl('1. CURVAS DE REFERENCIA (OK)', GOLD, bold=True, size=8))
        slay.addWidget(self._btn_side('➕  Adicionar XML / CSV', self._add_ok_files, GOLD))
        slay.addWidget(self._btn_side('⬆  Importar OK do Comparador', self._add_from_comparator, ACCENT))
        slay.addWidget(self._btn_side('🗑  Limpar curvas OK', self._clear_ok, FG_DIM))
        self._lbl_n = _lbl('0 curvas carregadas', FG_DIM, size=8)
        slay.addWidget(self._lbl_n)

        # Filtros
        fg = QGridLayout()
        fg.addWidget(_lbl('Ponto:',FG_DIM,size=8),0,0)
        self._gc_cb_mp = QComboBox(); self._gc_cb_mp.addItem('Todos')
        self._gc_cb_mp.currentTextChanged.connect(lambda _: self._refresh_list())
        fg.addWidget(self._gc_cb_mp,0,1)
        fg.addWidget(_lbl('Ano:',FG_DIM,size=8),1,0)
        self._gc_cb_yr = QComboBox(); self._gc_cb_yr.addItem('Todos')
        self._gc_cb_yr.currentTextChanged.connect(lambda _: self._refresh_list())
        fg.addWidget(self._gc_cb_yr,1,1)
        slay.addLayout(fg)

        self._lb = QListWidget(); self._lb.setMaximumHeight(120)
        slay.addWidget(self._lb)

        slay.addWidget(hsep())
        slay.addWidget(_lbl('2. PARAMETROS DA ANALISE', PURPLE, bold=True, size=8))

        def prow(lbl_txt, default):
            r = QHBoxLayout(); r.addWidget(_lbl(lbl_txt, FG_DIM, size=8))
            e = _entry(default, ACCENT, 6); r.addWidget(e); slay.addLayout(r); return e

        self._v_npoly  = prow('Grau do polinomio', '6')
        self._v_sigma  = prow('Sigma anomalia',    '3')
        self._v_smooth = prow('Suavizacao',        '2')
        self._v_npts   = prow('Pontos interp.',    '500')

        self._chk_raw  = QCheckBox('Curvas individuais'); self._chk_raw.setChecked(True)
        self._chk_band = QCheckBox('Banda P5-P95');       self._chk_band.setChecked(True)
        self._chk_poly = QCheckBox('Ajuste polinomial');  self._chk_poly.setChecked(True)
        self._chk_spl  = QCheckBox('Ajuste spline');      self._chk_spl.setChecked(False)
        for chk in (self._chk_raw,self._chk_band,self._chk_poly,self._chk_spl):
            slay.addWidget(chk)

        b_gen = _btn('▶▶  GERAR GOLDEN CURVE', ACCENT, '#0a2030', bold=True)
        b_gen.clicked.connect(self._analisar); slay.addWidget(b_gen)

        slay.addWidget(hsep())
        slay.addWidget(_lbl('3. DETECCAO DE ANOMALIA', RED, bold=True, size=8))
        slay.addWidget(self._btn_side('➕  Carregar curva(s) para teste', self._add_test, RED))
        self._lbl_test = _lbl('0 curvas de teste', FG_DIM, size=8)
        slay.addWidget(self._lbl_test)
        slay.addWidget(self._btn_side('🔍  Avaliar anomalia', self._avaliar, ORANGE))
        slay.addWidget(self._btn_side('🗑  Limpar teste', self._clear_test, FG_DIM))

        slay.addWidget(hsep())
        slay.addWidget(self._btn_side('💾  Exportar coeficientes CSV', self._export_csv, GREEN))
        slay.addWidget(self._btn_side('🖼  Salvar grafico PNG', self._save_png, FG_DIM))

        self._lbl_status = _lbl('Aguardando curvas...', FG_DIM, size=8, mono=False)
        self._lbl_status.setWordWrap(True)
        slay.addWidget(self._lbl_status)
        slay.addStretch()
        scroll.setWidget(inner); root.addWidget(scroll)

        # ── Painel direito — sub-tabs ─────────────────────────────────────────
        right = QTabWidget()
        right.setStyleSheet(f'QTabWidget::pane{{border:none;}} '
                            f'QTabBar::tab{{background:{BG2};color:{FG_DIM};padding:6px 14px;}} '
                            f'QTabBar::tab:selected{{background:{BG};color:{ACCENT};}}')

        self._pw_gc = pg.PlotWidget(); _setup_plot(self._pw_gc,'Golden Curve  —  F(x)','Curso [mm]','Forca [kN]')
        right.addTab(self._pw_gc, 'Golden Curve')

        self._pw_an = pg.PlotWidget(); _setup_plot(self._pw_an,'Deteccao de Anomalia','Curso [mm]','Forca [kN]')
        right.addTab(self._pw_an, 'Anomalia')

        stat_w = QWidget(); stat_lay = QHBoxLayout(stat_w); stat_lay.setContentsMargins(0,0,0,0)
        self._pw_st0 = pg.PlotWidget(); _setup_plot(self._pw_st0,'Distr. F_max','F_max [kN]','N')
        self._pw_st1 = pg.PlotWidget(); _setup_plot(self._pw_st1,'Desvio padrao F(x)','Curso [mm]','sigma [kN]')
        self._pw_st2 = pg.PlotWidget(); _setup_plot(self._pw_st2,'Residuos polinomio','Curso [mm]','Residuo [kN]')
        stat_lay.addWidget(self._pw_st0); stat_lay.addWidget(self._pw_st1); stat_lay.addWidget(self._pw_st2)
        right.addTab(stat_w, 'Estatisticas')

        root.addWidget(right, 1)

    def _add_ok_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self,'Selecionar curvas OK','',
            'Suportados (*.xml *.csv);;XML (*.xml);;CSV (*.csv);;Todos (*.*)')
        if not paths: return
        added = errs = 0
        for p in paths:
            if p in self._files: continue
            if _xml_auto_classify(p) == 'NOK': continue
            try: x,y=parse_curve_file(p); self._files.append(p); self._curves.append((x,y)); added+=1
            except Exception as e: errs+=1
        self._refresh_list()
        self._lbl_status.setText(f'+{added} curvas.  Total: {len(self._curves)}.' + (f'  {errs} erro(s).' if errs else ''))

    def _clear_ok(self):
        self._files.clear(); self._curves.clear(); self._analyzer=None
        self._poly_result=None; self._spl_result=None; self._lb.clear()
        self._lbl_n.setText('0 curvas carregadas'); self._pw_gc.clear(); self._pw_an.clear()

    def _add_from_comparator(self):
        xml_tab = self._get_xml_tab()
        if not xml_tab: return
        ok_entries = [e for e in xml_tab.entries if e.classification=='OK']
        if not ok_entries: QMessageBox.information(self,'Importar','Nenhuma curva OK no Comparador.'); return
        added = 0
        for e in ok_entries:
            if e.filepath in self._files: continue
            self._files.append(e.filepath); self._curves.append((np.array(e.x),np.array(e.y))); added+=1
        self._refresh_list(); self._lbl_status.setText(f'+{added} curvas importadas.')

    def _add_test(self):
        paths, _ = QFileDialog.getOpenFileNames(self,'Curvas de teste','','Suportados (*.xml *.csv);;Todos (*.*)')
        for p in paths:
            try: x,y=parse_curve_file(p); self._test_curves.append((x,y,os.path.basename(p)))
            except Exception as e: pass
        self._lbl_test.setText(f'{len(self._test_curves)} curvas de teste')

    def _clear_test(self):
        self._test_curves.clear(); self._lbl_test.setText('0 curvas de teste'); self._pw_an.clear()

    def _gc_filtered_indices(self):
        mp=self._gc_cb_mp.currentText(); yr=self._gc_cb_yr.currentText()
        return [i for i,p in enumerate(self._files)
                if (mp=='Todos' or _extract_mp(p)==mp) and (yr=='Todos' or _extract_year(p)==yr)]

    def _refresh_list(self):
        mps   = sorted(set(filter(None,(_extract_mp(p)   for p in self._files))))
        years = sorted(set(filter(None,(_extract_year(p) for p in self._files))))
        for cb, cur, opts in [(self._gc_cb_mp,self._gc_cb_mp.currentText(),mps),
                              (self._gc_cb_yr,self._gc_cb_yr.currentText(),years)]:
            cb.blockSignals(True); cb.clear(); cb.addItems(['Todos']+opts)
            cb.setCurrentText(cur if cur in ['Todos']+opts else 'Todos'); cb.blockSignals(False)
        idxs = self._gc_filtered_indices(); self._lb.clear()
        for i in idxs:
            self._lb.addItem(QListWidgetItem(f'[{os.path.splitext(self._files[i])[1].upper()}]  {os.path.basename(self._files[i])}'))
        self._lbl_n.setText(f'{len(idxs)} de {len(self._files)} curvas visíveis')

    def _get_params(self):
        def f(e, d):
            try: return float(e.text().replace(',','.'))
            except: return d
        return dict(degree=int(f(self._v_npoly,6)), sigma=f(self._v_sigma,3.0),
                    smooth=f(self._v_smooth,2.0), n_interp=int(f(self._v_npts,500)))

    def _analisar(self):
        idxs = self._gc_filtered_indices()
        curves = [self._curves[i] for i in idxs]
        if len(curves) < 3:
            QMessageBox.warning(self,'Atencao','Carregue pelo menos 3 curvas OK.'); return
        p = self._get_params(); self._lbl_status.setText('Processando...'); QApplication.processEvents()
        try:
            self._analyzer   = GoldenCurveAnalyzer(curves, n_interp=p['n_interp'], smooth_sigma=p['smooth'])
            self._poly_result = self._analyzer.fit_polynomial(degree=p['degree'])
            self._spl_result  = self._analyzer.fit_spline()
            self._replot(); self._plot_stats()
            az = self._analyzer
            self._lbl_status.setText(f'OK  |  {az.n_valid} curvas  |  F_max_med={az.mean.max():.3f} kN  |  R2={self._poly_result["r2"]:.4f}')
        except Exception as e:
            QMessageBox.critical(self,'Erro',str(e)); self._lbl_status.setText(f'Erro: {e}')

    def _replot(self):
        if not self._analyzer: return
        az = self._analyzer; p = self._get_params(); pw = self._pw_gc; pw.clear(); x = az.x_grid

        if self._chk_raw.isChecked():
            n_show = min(az.n_valid, 200); step = max(1, az.n_valid//n_show)
            alpha = max(20, int(80/n_show))
            for row in az.matrix[::step][:n_show]:
                pw.plot(x, row, pen=pg.mkPen(QColor(100,150,200,alpha), width=0.5))

        if self._chk_band.isChecked():
            _fill_between(pw, x, az.p05, az.p95, ACCENT, 20)
            _fill_between(pw, x, az.p25, az.p75, ACCENT, 40)
            _fill_between(pw, x, az.mean-az.std, az.mean+az.std, GOLD, 35)

        pw.plot(x, az.mean_smooth, pen=_pen(GOLD,2.5), name=f'Media suavizada (n={az.n_valid})')

        if self._chk_poly.isChecked() and self._poly_result:
            pr = self._poly_result
            pw.plot(x, pr['y_fit'], pen=pg.mkPen(PURPLE,width=1.8,style=Qt.DashLine),
                    name=f'Poly grau {pr["degree"]}  R²={pr["r2"]:.4f}')

        if self._chk_spl.isChecked() and self._spl_result:
            sr = self._spl_result
            pw.plot(x, sr['y_fit'], pen=pg.mkPen(GREEN,width=1.8,style=Qt.DotLine),
                    name=f'Spline  R²={sr["r2"]:.4f}')

        pw.addLegend(offset=(5,5))

    def _plot_stats(self):
        if not self._analyzer: return
        az = self._analyzer; x = az.x_grid
        # F_max histogram
        pw0 = self._pw_st0; pw0.clear()
        y, edges = np.histogram(az.f_max_per_curve, bins=min(30,az.n_valid))
        pw0.plot(edges, np.append(y,0), stepMode='right', fillLevel=0, brush=_brush(GOLD,180))
        mn = az.f_max_per_curve.mean()
        pw0.addItem(pg.InfiniteLine(pos=mn, angle=90, pen=_pen(ACCENT,1.5), label=f'media={mn:.3f}'))
        # std(x)
        pw1 = self._pw_st1; pw1.clear()
        pw1.plot(x, az.std, pen=_pen(ORANGE,1.5))
        _fill_between(pw1, x, np.zeros_like(x), az.std, ORANGE, 60)
        # Residuals
        pw2 = self._pw_st2; pw2.clear()
        if self._poly_result:
            resid = az.mean_smooth - self._poly_result['y_fit']
            pw2.plot(x, resid, pen=_pen(PURPLE,1.2))
            pw2.addItem(pg.InfiniteLine(pos=0, angle=0, pen=_pen(FG_DIM,0.8)))
            _fill_between(pw2, x, np.zeros_like(x), resid, PURPLE, 60)

    def _avaliar_anomalia(self):  # alias
        self._avaliar()

    def _avaliar(self):
        if not self._analyzer: QMessageBox.warning(self,'Atencao','Gere a Golden Curve primeiro.'); return
        if not self._test_curves: QMessageBox.warning(self,'Atencao','Carregue curvas de teste.'); return
        p = self._get_params(); az = self._analyzer; pw = self._pw_an; pw.clear()
        _fill_between(pw, az.x_grid, az.p05, az.p95, ACCENT, 25)
        pw.plot(az.x_grid, az.mean_smooth, pen=_pen(GOLD,2), name='Golden Curve')
        for x_t, y_t, name in self._test_curves:
            res = az.anomaly_score(x_t, y_t, sigma_thr=p['sigma'])
            if res.get('score') is None:
                color = FG_DIM
                label_txt = f'{name}: {res["msg"]}'
            else:
                color = GREEN if res['verdict']=='OK' else RED
                label_txt = f'{name}: {res["verdict"]}  score={res["score"]:.1f}  outside={res["outside_frac"]:.2%}'
            pw.plot(x_t, y_t, pen=_pen(color,1.5), name=label_txt)
        pw.addLegend(offset=(5,5))

    def _export_csv(self):
        if not self._analyzer or not self._poly_result:
            QMessageBox.warning(self,'Atencao','Gere a Golden Curve primeiro.'); return
        path, _ = QFileDialog.getSaveFileName(self,'Exportar CSV','golden_curve.csv','CSV (*.csv)')
        if not path: return
        az = self._analyzer; pr = self._poly_result
        with open(path,'w',newline='',encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['# Coeficientes polinomio grau',pr['degree'],'R2',pr['r2']])
            w.writerow(['X','mean','std','p05','p95','poly_fit'])
            for i,xi in enumerate(az.x_grid):
                w.writerow([f'{xi:.4f}',f'{az.mean[i]:.5f}',f'{az.std[i]:.5f}',
                             f'{az.p05[i]:.5f}',f'{az.p95[i]:.5f}',f'{pr["y_fit"][i]:.5f}'])
        self._lbl_status.setText(f'Exportado: {os.path.basename(path)}')

    def _save_png(self):
        path, _ = QFileDialog.getSaveFileName(self,'Salvar PNG','golden_curve.png','PNG (*.png)')
        if path:
            exp = pg.exporters.ImageExporter(self._pw_gc.plotItem)
            exp.export(path); self._lbl_status.setText(f'Salvo: {os.path.basename(path)}')


# ═══════════════════════════════════════════════════════════════════════════════
# MainWindow
# ═══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        import subprocess
        ver = __version__
        if _IS_DEV:
            try:
                r = subprocess.run(['git','describe','--tags','--always','--dirty'],
                    capture_output=True,text=True,cwd=_SCRIPT_DIR,timeout=3)
                if r.returncode==0: ver = r.stdout.strip()
            except: pass
        self._ver = ver
        self.setWindowTitle(f'BCI - KNUCKLE SOFTWARE  [OpenGL]  {ver}')
        self.resize(1400, 820)
        self._build_ui()
        self._check_trial()
        _check_update_async(self._ver, self._on_update)

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_lay = QVBoxLayout(central); main_lay.setContentsMargins(0,0,0,0); main_lay.setSpacing(0)

        # Header
        hdr = QFrame(); hdr.setStyleSheet(f'background:{BG};')
        hlay = QHBoxLayout(hdr); hlay.setContentsMargins(20,10,20,10)
        left_h = QVBoxLayout()
        left_h.addWidget(_lbl('BCI - KNUCKLE SOFTWARE  [OpenGL]', ACCENT, bold=True, size=13))
        left_h.addWidget(_lbl('Author: Bruno Bernardinetti — Stellantis  |  Brasil', FG_DIM, size=9, mono=False))
        hlay.addLayout(left_h); hlay.addStretch()
        right_h = QVBoxLayout(); right_h.setAlignment(Qt.AlignRight)
        right_h.addWidget(_lbl(self._ver, FG_DIM, size=9))
        btn_row = QHBoxLayout()
        b_sett = _btn(' ⚙ ', FG_DIM, BG2); b_sett.clicked.connect(self._open_settings)
        b_help = _btn(' ? ', ACCENT, BG2, bold=True); b_help.clicked.connect(self._open_help)
        btn_row.addWidget(b_sett); btn_row.addWidget(b_help)
        right_h.addLayout(btn_row); hlay.addLayout(right_h)
        main_lay.addWidget(hdr)

        # Linha decorativa
        line = QFrame(); line.setFixedHeight(2); line.setStyleSheet(f'background:{ACCENT};')
        main_lay.addWidget(line)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            f'QTabWidget::pane{{border:none;background:{BG};}}'
            f'QTabBar::tab{{background:{BG2};color:{FG_DIM};font-weight:bold;font-family:Courier;'
            f'font-size:10pt;padding:8px 20px;border:none;}}'
            f'QTabBar::tab:selected{{background:{BG};color:{ACCENT};border-bottom:2px solid {ACCENT};}}'
        )

        self._tab_rug  = TabRugosidade()
        self._tab_int  = TabInterferencia()
        self._tab_xml  = TabXMLComparator()
        self._tab_gc   = TabGoldenCurve(get_xml_tab=lambda: self._tab_xml)

        self._tab_rug.sig_ra.connect(self._tab_int.set_ra_sede)

        self._tabs.addTab(self._tab_rug, '  Analise de Rugosidade  ')
        self._tabs.addTab(self._tab_int, '  Calculo de Interferencia  ')
        self._tabs.addTab(self._tab_xml, '  Comparador de Curvas XML  ')
        self._tabs.addTab(self._tab_gc,  '  Golden Curve  ')
        main_lay.addWidget(self._tabs, 1)

    def _on_update(self, tag, release):
        balloon = UpdateBalloon(self, tag, release, self._open_settings)
        balloon.show()

    def _check_trial(self):
        if _IS_DEV: return
        days = _trial_days_left()
        if days <= 0:
            QTimer.singleShot(150, self._show_trial_expired)
        elif days <= 3:
            QTimer.singleShot(300, lambda: self._show_trial_banner(days))

    def _show_trial_banner(self, days):
        banner = QFrame(); banner.setStyleSheet('background:#2b1a00;padding:4px;')
        blay = QHBoxLayout(banner); blay.setContentsMargins(10,4,10,4)
        blay.addWidget(QLabel(f'⏱ AVALIAÇÃO GRATUITA — {days} dia(s) restante(s)  |  Licença: {_CONTATO}'))
        close = _btn(' ✕ ', '#ffcc44', '#2b1a00')
        close.clicked.connect(banner.deleteLater)
        blay.addWidget(close)
        self.centralWidget().layout().insertWidget(1, banner)

    def _show_trial_expired(self):
        dlg = QDialog(self); dlg.setWindowTitle('Período de avaliação encerrado')
        dlg.setStyleSheet(f'background:{BG};')
        dlg.setFixedWidth(400)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(30,30,30,30); lay.setSpacing(12)
        lay.addWidget(_lbl('PERÍODO DE AVALIAÇÃO ENCERRADO', RED, bold=True, size=13), 0, Qt.AlignCenter)
        lay.addWidget(_lbl('Seu teste gratuito de 7 dias expirou.\nPara continuar, adquira sua licença:',
                           FG, size=10, mono=False), 0, Qt.AlignCenter)
        lay.addWidget(_lbl(_CONTATO, ACCENT, bold=True, size=18), 0, Qt.AlignCenter)
        b = _btn('Fechar software', 'white', RED, bold=True)
        b.clicked.connect(QApplication.quit); lay.addWidget(b, 0, Qt.AlignCenter)
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowCloseButtonHint)
        dlg.exec_()
        QApplication.quit()

    def _open_settings(self):
        sett = _get_settings()
        dlg  = QDialog(self); dlg.setWindowTitle('Configuracoes')
        dlg.setStyleSheet(f'QDialog{{background:{BG};}}'); dlg.setFixedWidth(380)
        lay  = QVBoxLayout(dlg); lay.setContentsMargins(24,20,24,20); lay.setSpacing(10)
        lay.addWidget(_lbl('CONFIGURAÇÕES', ACCENT, bold=True, size=11), 0, Qt.AlignCenter)

        box = QGroupBox('ATUALIZAÇÃO')
        box.setStyleSheet(f'QGroupBox{{background:{BG2};border-radius:4px;padding:10px;}}'
                          f'QGroupBox::title{{color:{FG_DIM};font-size:7pt;subcontrol-origin:margin;left:8px;}}')
        bl = QVBoxLayout(box)
        chk = QCheckBox('Verificar atualizações automaticamente ao iniciar')
        chk.setChecked(sett.get('auto_update', True)); bl.addWidget(chk)

        self._lbl_chk_result = _lbl('', FG_DIM, size=8, mono=False)
        bl.addWidget(self._lbl_chk_result)

        def check_now():
            self._lbl_chk_result.setText('Verificando...')
            def cb(releases):
                if not releases:
                    self._lbl_chk_result.setText('Sem conexao ou nenhuma versao encontrada.')
                    return
                tag = releases[0].get('tag_name','?')
                if tag == self._ver:
                    self._lbl_chk_result.setText(f'✔ Voce usa a versao mais recente ({self._ver})')
                else:
                    self._lbl_chk_result.setText(f'Nova versao disponivel: {tag}')
            _fetch_all_releases(cb)

        b_chk = _btn('Verificar agora', ACCENT, BG); b_chk.clicked.connect(check_now); bl.addWidget(b_chk)
        lay.addWidget(box)

        def save():
            sett['auto_update'] = chk.isChecked(); _save_settings(sett); dlg.accept()

        bb = QHBoxLayout()
        b_save = _btn('Salvar', BG, ACCENT, bold=True); b_save.clicked.connect(save)
        b_can  = _btn('Cancelar', FG_DIM, BG2);         b_can.clicked.connect(dlg.reject)
        bb.addWidget(b_save); bb.addWidget(b_can); lay.addLayout(bb)
        dlg.exec_()

    def _open_help(self):
        dlg = QDialog(self); dlg.setWindowTitle('Ajuda — BCI KNUCKLE SOFTWARE')
        dlg.setStyleSheet(f'QDialog{{background:{BG};}}'); dlg.resize(820, 640)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(10,10,10,10)
        txt = QTextEdit(); txt.setReadOnly(True)
        txt.setStyleSheet(f'background:#0d1117;color:{FG};font-family:Courier;font-size:9pt;border:none;padding:10px;')

        def h1(t): txt.append(f'\n{"━"*68}\n  {t}\n{"━"*68}')
        def h2(t): txt.append(f'\n  {t}')
        def body(t): txt.append(f'  {t}')
        def bullet(items):
            for i in items: txt.append(f'    • {i}')

        txt.append(f'  BCI — KNUCKLE SOFTWARE  |  Documentacao Tecnica  [OpenGL Fork]')
        txt.append(f'  Autor: Bruno Bernardinetti — Stellantis  |  {self._ver}')
        h1('1. INTRODUCAO')
        bullet(['Modulo 1 — Rugosidade por Imagem (Ra)','Modulo 2 — Interferencia Press-Fit (Lame)',
                'Modulo 3 — Comparador Curvas XML (maXYmos/Kistler)','Modulo 4 — Golden Curve + Anomalia'])
        h1('2. MODULO 1 — RUGOSIDADE')
        body('Ra proxy = mean(|I - mean(I)|)  calibrado por Ra_real_ref / Ra_proxy_medio')
        h2('Como usar:')
        bullet(['1. Carregar >=10 imagens REFERENCIA com Ra real conhecido.',
                '2. Informar Ra real em micrometros.','3. Carregar >=10 imagens PECA A MEDIR.',
                '4. Clicar ANALISAR.','5. (Opcional) Exportar PDF.'])
        h1('3. MODULO 2 — INTERFERENCIA')
        body('p = delta_eff / [R x (C_hub + C_shaft)]  — Equacoes de Lame')
        body('delta_eff = delta_nom - (Ra_eixo + Ra_cubo) x 1e-3  [DIN 7190]')
        body('F = p x A x mu  |  Stribeck: mu_ef(v) = mu_lub + (mu_dry-mu_lub) x exp(-v/15)')
        h1('4. MODULO 3 — COMPARADOR XML')
        bullet(['Classificacao: campo <Total_result> > sufixo _OK/_NOK > manual',
                'Filtros Ponto/Ano por regex do nome do arquivo.',
                'Janela de aprovacao: retangulo X/Y no grafico.'])
        h1('5. MODULO 4 — GOLDEN CURVE')
        body('z(x)=|F_nova-mean|/std  |  score=clip(mean(z)/thr*50,0,100)  |  OK se score<40 e outside<5%')
        h1('6. FORK OPENGL')
        body('Renderer: PyQt5 + pyqtgraph com useOpenGL=True e antialias=True')
        body('GPU: DirectX/OpenGL hardware acceleration para todos os graficos.')
        body('Benchmarks tipicos: 10-50x mais rapido que matplotlib/Agg em curvas densas.')
        h1('7. REFERENCIAS')
        bullet(['ISO 1302:2002','DIN 7190-1:2017','Lame (1852)','Shigley & Budynas (2011)',
                'Stribeck (1902)','Gonzalez & Woods (2018)'])
        txt.append(f'\n  github.com/BrunoBernar/rugosidade_optica_teste')

        lay.addWidget(txt)
        b_close = _btn('Fechar', FG, BG2); b_close.clicked.connect(dlg.accept)
        lay.addWidget(b_close, 0, Qt.AlignCenter)
        dlg.exec_()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
