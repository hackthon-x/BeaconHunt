"""BeaconHunt — dark cyber-security SOC dashboard palette + Qt stylesheet.

Visual language (matches the reference BEACONHUNT dashboard mockup):

  * Deep navy background (#0A0F1A) with slightly raised panel cards
    (#0F1826 / #111C2E) and 1px borders (#1E2D42).
  * Cyan accent (#00D4FF) for primary lines, links, active nav, sparklines.
  * Green accent (#22C55E / #4ADE80) for status dots, topology edges,
    confidence donuts, "High Confidence" pills.
  * Semantic severity pills: red (#DC2626 High), amber (#D97706 Medium),
    blue (#2563EB Low).
  * White titles, muted gray-blue (#8BA3BD) for secondary text.
  * Single dark theme — the reference is a dark SOC dashboard, so we ship
    one cohesive dark palette and skip the light/dark toggle.

The palette is exposed both as module-level constants (backwards
compatible with the existing BeaconHunt UI code that imports
``TEXT_PRIMARY`` etc.) and as a ``Theme`` dataclass.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    label: str

    # Chrome
    app_bg: str               # outermost window background
    header_bg: str            # top header bar
    header_border: str
    sidebar_bg: str
    sidebar_bg_to: str        # gradient stop
    sidebar_active_bg: str
    sidebar_active_bar: str
    sidebar_text: str
    sidebar_text_active: str
    sidebar_footer_text: str
    sidebar_divider: str

    # Cards / panels
    card_bg: str
    card_border: str
    card_alt_bg: str
    card_hover_bg: str

    # Text
    text_primary: str         # white-ish
    text_secondary: str       # muted gray-blue
    text_muted: str           # even more muted

    # Accents
    cyan: str                 # primary accent
    cyan_dim: str             # for less-prominent cyan elements
    cyan_tint: str            # translucent cyan background
    green: str                # status / detected / topology
    green_dim: str
    green_tint: str

    # Severity
    sev_high_bg: str
    sev_high_fg: str
    sev_med_bg: str
    sev_med_fg: str
    sev_low_bg: str
    sev_low_fg: str

    # Status
    active_dot: str           # green
    resolved_dot: str         # gray

    # Tables
    table_header_bg: str
    table_header_fg: str
    table_row_sep: str
    table_alt_row: str
    table_selected_bg: str
    table_selected_fg: str

    # Misc
    progress_track: str
    scrollbar_handle: str
    scrollbar_handle_hover: str
    tooltip_bg: str
    tooltip_fg: str
    divider: str

    # Chart colors
    chart_grid: str
    chart_spine: str
    chart_axis_label: str
    chart_legend_bg: str


# ---------------------------------------------------------------------------
# The dark SOC dashboard palette — the only theme this redesign ships with.
# ---------------------------------------------------------------------------

THEME = Theme(
    name="dark",
    label="SOC Dark",

    app_bg="#0A0F1A",
    header_bg="#0C1322",
    header_border="#1E2D42",
    sidebar_bg="#0B1220",
    sidebar_bg_to="#0E1726",
    sidebar_active_bg="#112038",
    sidebar_active_bar="#00D4FF",
    sidebar_text="#8BA3BD",
    sidebar_text_active="#FFFFFF",
    sidebar_footer_text="#5B6B7A",
    sidebar_divider="#1E2D42",

    card_bg="#0F1826",
    card_border="#1E2D42",
    card_alt_bg="#0D1522",
    card_hover_bg="#15233A",

    text_primary="#FFFFFF",
    text_secondary="#8BA3BD",
    text_muted="#5E7493",

    cyan="#00D4FF",
    cyan_dim="#0E8FB0",
    cyan_tint="rgba(0, 212, 255, 0.12)",
    green="#22C55E",
    green_dim="#16A34A",
    green_tint="rgba(34, 197, 94, 0.14)",

    sev_high_bg="#DC2626",
    sev_high_fg="#FFFFFF",
    sev_med_bg="#D97706",
    sev_med_fg="#FFFFFF",
    sev_low_bg="#2563EB",
    sev_low_fg="#FFFFFF",

    active_dot="#22C55E",
    resolved_dot="#64748B",

    table_header_bg="#0C1322",
    table_header_fg="#8BA3BD",
    table_row_sep="#1A2638",
    table_alt_row="#0D1522",
    table_selected_bg="#112038",
    table_selected_fg="#FFFFFF",

    progress_track="#1A2638",
    scrollbar_handle="#28395A",
    scrollbar_handle_hover="#3A4F73",
    tooltip_bg="#0F1826",
    tooltip_fg="#FFFFFF",
    divider="#1E2D42",

    chart_grid="#1A2638",
    chart_spine="#1E2D42",
    chart_axis_label="#8BA3BD",
    chart_legend_bg="#0F1826",
)


# ---- Module-level constants (back-compat with existing BeaconHunt UI) -----
# Existing files import names like ``TEXT_PRIMARY`` and ``ACCENT_TEAL`` from
# this module. Re-export them pointing at the dark palette so legacy widgets
# continue to work without changes.

SIDEBAR_BG = THEME.sidebar_bg
SIDEBAR_BG_GRADIENT_TO = THEME.sidebar_bg_to
SIDEBAR_ACTIVE_BG = THEME.sidebar_active_bg
SIDEBAR_ACTIVE_BAR = THEME.sidebar_active_bar
SIDEBAR_TEXT = THEME.sidebar_text
SIDEBAR_TEXT_ACTIVE = THEME.sidebar_text_active

CONTENT_BG = THEME.app_bg
CARD_BG = THEME.card_bg
CARD_BORDER = THEME.card_border

TEXT_PRIMARY = THEME.text_primary
TEXT_SECONDARY = THEME.text_secondary
TEXT_MUTED = THEME.text_muted

ACCENT_TEAL = THEME.cyan
ACCENT_TEAL_BRIGHT = THEME.cyan
ACCENT_TEAL_DARK = THEME.cyan_dim
TEAL_TINT = THEME.cyan_tint
TEAL_TINT_LIGHT = THEME.cyan_tint

GREEN_BG = THEME.green_tint
GREEN_FG = THEME.green
GREEN_BORDER = THEME.green
GREEN_BANNER_BG = THEME.green_tint

AMBER_BG = THEME.sev_med_bg
AMBER_FG = THEME.sev_med_fg
AMBER_BORDER = THEME.sev_med_bg

GRAY_BADGE_BG = "#1E293B"
GRAY_BADGE_FG = THEME.text_secondary
GRAY_BADGE_BORDER = THEME.divider

BLUE_TINT = "#172554"

TABLE_HEADER_BG = THEME.table_header_bg
TABLE_ROW_SEP = THEME.table_row_sep


# ---- Theme API (kept simple — single dark theme) --------------------------

def get_theme() -> Theme:
    return THEME


def current_theme_name() -> str:
    return THEME.name


def available_themes() -> list:
    return [THEME.name]


def set_theme(name: str) -> None:
    # Single-theme palette — accept the call as a no-op for back-compat.
    return None


def toggle_theme() -> str:
    return THEME.name


_LISTENERS: list = []


def register_listener(fn) -> None:
    if fn not in _LISTENERS:
        _LISTENERS.append(fn)


def unregister_listener(fn) -> None:
    if fn in _LISTENERS:
        _LISTENERS.remove(fn)


# ---- Severity badge helpers ----------------------------------------------

SEVERITY_BG = {
    "High": THEME.sev_high_bg,
    "Medium": THEME.sev_med_bg,
    "Low": THEME.sev_low_bg,
}
SEVERITY_FG = {
    "High": THEME.sev_high_fg,
    "Medium": THEME.sev_med_fg,
    "Low": THEME.sev_low_fg,
}


def severity_qss(level: str) -> str:
    bg = SEVERITY_BG.get(level, THEME.card_bg)
    fg = SEVERITY_FG.get(level, THEME.text_primary)
    return (
        f"background:{bg}; color:{fg}; border:none; border-radius:10px; "
        f"padding:3px 10px; font-size:8.5pt; font-weight:700; letter-spacing:0.5px;"
    )


# ---- Global QSS -----------------------------------------------------------
# Built once against THEME since the palette is static.

def _build_qss(t: Theme) -> str:
    return f"""
* {{
    font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', 'DejaVu Sans', Arial, sans-serif;
    font-size: 10pt;
    color: {t.text_primary};
    outline: none;
}}
QMainWindow, QDialog {{ background: {t.app_bg}; }}

/* ---- Top header ---- */
QFrame#HeaderBar {{
    background: {t.header_bg};
    border-bottom: 1px solid {t.header_border};
}}
QLabel#HeaderLogo {{
    color: {t.text_primary};
    font-size: 14pt;
    font-weight: 800;
    letter-spacing: 2px;
}}
QLabel#HeaderLogoGlyph {{
    color: {t.cyan};
    font-size: 18pt;
    font-weight: 800;
}}
QLabel#PillLabEnv {{
    background: transparent;
    color: {t.cyan};
    border: 1px solid {t.sidebar_divider};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.5px;
}}
QLabel#MonitoringLabel {{
    color: {t.green};
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#HeaderStatLabel {{
    color: {t.text_secondary};
    font-size: 8pt;
    font-weight: 500;
    letter-spacing: 0.5px;
}}
QLabel#HeaderStatValue {{
    color: {t.text_primary};
    font-size: 13pt;
    font-weight: 800;
}}
QFrame#HeaderStatDivider {{
    background: {t.sidebar_divider};
    max-width: 1px;
}}

/* ---- Sidebar ---- */
QFrame#Sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {t.sidebar_bg}, stop:1 {t.sidebar_bg_to});
    border-right: 1px solid {t.sidebar_divider};
}}
QLabel#SidebarLogo {{
    color: {t.text_primary};
    font-size: 13pt;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 0;
}}
QLabel#SidebarLogoGlyph {{
    color: {t.cyan};
    font-size: 15pt;
    font-weight: 800;
    padding: 0;
}}
QLabel#SidebarLogoTag {{
    color: {t.text_muted};
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 0;
}}
QPushButton#NavButton {{
    background: transparent;
    color: {t.sidebar_text};
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 11px 18px 11px 18px;
    font-size: 10pt;
    font-weight: 500;
}}
QPushButton#NavButton:hover {{
    background: rgba(255,255,255,0.03);
    color: {t.sidebar_text_active};
}}
QPushButton#NavButton:checked {{
    background: {t.sidebar_active_bg};
    border-left: 3px solid {t.sidebar_active_bar};
    color: {t.sidebar_text_active};
}}
QFrame#NavRow {{
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
}}
QFrame#NavRow:hover {{
    background: rgba(255,255,255,0.03);
}}
QFrame#NavRow[checked="true"] {{
    background: {t.sidebar_active_bg};
    border-left: 3px solid {t.sidebar_active_bar};
}}
QLabel#NavBadge {{
    background: {t.green};
    color: #061A0E;
    border-radius: 9px;
    padding: 1px 7px;
    font-size: 8pt;
    font-weight: 800;
    min-width: 18px;
}}
QFrame#ThreatHuntCard {{
    background: {t.card_bg};
    border: 1px solid {t.card_border};
    border-radius: 10px;
}}
QLabel#ThreatHuntTitle {{
    color: {t.text_primary};
    font-size: 10pt;
    font-weight: 700;
}}
QLabel#ThreatHuntSub {{
    color: {t.text_secondary};
    font-size: 8.5pt;
}}
QLabel#SidebarFooterEnv {{
    color: {t.text_muted};
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 1.5px;
}}
QLabel#SidebarFooterUser {{
    color: {t.text_primary};
    font-size: 9.5pt;
    font-weight: 600;
}}

/* ---- Content ---- */
QWidget#Content {{ background: {t.app_bg}; }}
QLabel#PageTitle {{
    color: {t.text_primary};
    font-size: 18pt;
    font-weight: 800;
}}
QLabel#PageSubtitle {{
    color: {t.text_secondary};
    font-size: 10pt;
}}
QLabel#Breadcrumb {{
    color: {t.text_muted};
    font-size: 9pt;
}}
QLabel#BreadcrumbCurrent {{
    color: {t.text_secondary};
    font-size: 9pt;
    font-weight: 600;
}}

/* ---- Cards ---- */
QFrame#Card {{
    background: {t.card_bg};
    border: 1px solid {t.card_border};
    border-radius: 10px;
}}
QFrame#CardHover {{
    background: {t.card_bg};
    border: 1px solid {t.card_border};
    border-radius: 10px;
}}
QLabel#CardTitle {{
    color: {t.text_primary};
    font-size: 11pt;
    font-weight: 700;
}}
QLabel#CardSubtitle {{
    color: {t.text_secondary};
    font-size: 9pt;
}}
QLabel#CardLabel {{
    color: {t.text_secondary};
    font-size: 8.5pt;
    font-weight: 500;
    letter-spacing: 0.3px;
}}
QLabel#CardValue {{
    color: {t.text_primary};
    font-size: 16pt;
    font-weight: 800;
}}
QLabel#CardValueBig {{
    color: {t.text_primary};
    font-size: 22pt;
    font-weight: 800;
}}
QLabel#CardValueGreen {{
    color: {t.green};
    font-size: 16pt;
    font-weight: 800;
}}
QLabel#Muted {{ color: {t.text_secondary}; font-size: 9pt; }}
QLabel#TinyMuted {{ color: {t.text_muted}; font-size: 8pt; }}
QLabel#LinkCyan {{
    color: {t.cyan};
    font-size: 9pt;
    font-weight: 600;
}}

/* ---- Severity pills ---- */
QLabel#SevHigh {{
    background: {t.sev_high_bg}; color: {t.sev_high_fg};
    border: none; border-radius: 10px;
    padding: 3px 10px; font-size: 8.5pt; font-weight: 700; letter-spacing: 0.5px;
}}
QLabel#SevMedium {{
    background: {t.sev_med_bg}; color: {t.sev_med_fg};
    border: none; border-radius: 10px;
    padding: 3px 10px; font-size: 8.5pt; font-weight: 700; letter-spacing: 0.5px;
}}
QLabel#SevLow {{
    background: {t.sev_low_bg}; color: {t.sev_low_fg};
    border: none; border-radius: 10px;
    padding: 3px 10px; font-size: 8.5pt; font-weight: 700; letter-spacing: 0.5px;
}}
QLabel#StatusActive {{
    color: {t.text_primary};
    font-size: 9pt; font-weight: 600;
}}
QLabel#StatusResolved {{
    color: {t.text_secondary};
    font-size: 9pt; font-weight: 600;
}}

/* ---- Buttons ---- */
QPushButton {{
    background: {t.cyan};
    color: #061018;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 700;
    min-height: 18px;
}}
QPushButton:hover {{ background: #33DFFF; }}
QPushButton:disabled {{ background: #2A3A52; color: #5E7493; }}
QPushButton[secondary="true"] {{
    background: {t.card_bg};
    color: {t.text_primary};
    border: 1px solid {t.card_border};
}}
QPushButton[secondary="true"]:hover {{ background: {t.card_hover_bg}; border-color: {t.scrollbar_handle}; }}
QPushButton[outline="true"] {{
    background: transparent;
    color: {t.cyan};
    border: 1px solid {t.cyan};
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
}}
QPushButton[outline="true"]:hover {{ background: {t.cyan_tint}; }}

/* Filter tabs (Alerts page) */
QPushButton#FilterTab {{
    background: {t.card_bg};
    color: {t.text_secondary};
    border: 1px solid {t.card_border};
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 9.5pt;
}}
QPushButton#FilterTab:hover {{
    background: {t.card_hover_bg};
    color: {t.text_primary};
}}
QPushButton#FilterTab:checked {{
    background: {t.cyan};
    color: #061018;
    border: 1px solid {t.cyan};
}}

/* Report list rows */
QFrame#ReportRow {{
    background: {t.card_bg};
    border: 1px solid {t.card_border};
    border-radius: 8px;
}}
QFrame#ReportRow:hover {{
    background: {t.card_hover_bg};
    border-color: {t.scrollbar_handle};
}}

/* ---- Inputs ---- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: {t.card_bg};
    border: 1px solid {t.card_border};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {t.cyan};
    selection-color: #061018;
    color: {t.text_primary};
}}
QLineEdit:focus, QComboBox:focus {{ border: 1px solid {t.cyan}; }}
QLineEdit::placeholder {{ color: {t.text_muted}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {t.text_secondary};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {t.card_bg};
    border: 1px solid {t.card_border};
    border-radius: 4px;
    selection-background-color: {t.sidebar_active_bg};
    selection-color: {t.text_primary};
    color: {t.text_primary};
    outline: none;
}}

/* ---- Tables ---- */
QTableWidget {{
    background: {t.card_bg};
    alternate-background-color: {t.table_alt_row};
    gridline-color: transparent;
    border: none;
    selection-background-color: {t.table_selected_bg};
    selection-color: {t.table_selected_fg};
    color: {t.text_primary};
}}
QTableWidget::item {{
    padding: 8px 8px;
    border-bottom: 1px solid {t.table_row_sep};
    color: {t.text_primary};
}}
QTableWidget::item:selected {{ background: {t.table_selected_bg}; }}
QHeaderView::section {{
    background: {t.table_header_bg};
    color: {t.table_header_fg};
    padding: 9px 12px;
    border: none;
    border-bottom: 1px solid {t.card_border};
    font-weight: 600;
    font-size: 8.5pt;
    letter-spacing: 0.3px;
}}
QHeaderView::section:first {{ border-top-left-radius: 10px; }}
QHeaderView::section:last {{ border-top-right-radius: 10px; }}
QTableCornerButton::section {{ background: {t.table_header_bg}; border: none; }}

/* ---- Progress bar ---- */
QProgressBar {{
    background: {t.progress_track};
    border: none;
    border-radius: 3px;
    text-align: center;
    color: transparent;
    height: 6px;
}}
QProgressBar::chunk {{
    background: {t.cyan};
    border-radius: 3px;
}}

/* ---- Scrollbar ---- */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {t.scrollbar_handle}; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {t.scrollbar_handle_hover}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {t.scrollbar_handle}; border-radius: 5px; min-width: 30px; }}
QScrollBar::handle:horizontal:hover {{ background: {t.scrollbar_handle_hover}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}

/* ---- Tooltip ---- */
QToolTip {{
    background: {t.tooltip_bg};
    color: {t.tooltip_fg};
    border: 1px solid {t.card_border};
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 9pt;
}}

/* ---- Status bar ---- */
QStatusBar {{ background: {t.header_bg}; color: {t.text_secondary}; border-top: 1px solid {t.header_border}; }}

/* ---- Text edit ---- */
QTextEdit {{
    background: {t.card_bg};
    color: {t.text_primary};
    border: 1px solid {t.card_border};
    border-radius: 6px;
}}
"""


QSS: str = _build_qss(THEME)
