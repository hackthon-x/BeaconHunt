"""Custom QPainter widgets + matplotlib canvases for the redesigned UI.

  * ``DonutGauge``       — circular progress ring (confidence %, beacon frequency).
  * ``Sparkline``        — tiny inline line chart for header / sidebar sparklines.
  * ``TopologyWidget``   — custom-drawn network topology with center node and edges.
  * ``ActivityChart``    — matplotlib 24h beaconing activity chart (cyan baseline + green spikes).
  * ``TimingChart``      — matplotlib lollipop chart for beacon timing analysis.
  * ``JitterChart``      — matplotlib line chart for the jitter waveform.

All widgets read colors from :mod:`beaconhunt.ui.styles` so they stay in
sync with the dark SOC palette.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPainterPath, QLinearGradient
from PySide6.QtWidgets import QWidget

from . import styles

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


# ---- Donut gauge ----------------------------------------------------------

class DonutGauge(QWidget):
    """Circular progress ring with a centered label.

    ``value`` is 0..100 for a percentage ring. Pass ``label`` to put a
    custom string in the center (e.g. "300s" for the beacon frequency
    donut) and ``caption`` for the small text below the ring.
    """

    def __init__(
        self,
        value: float = 0.0,
        label: Optional[str] = None,
        caption: Optional[str] = None,
        ring_color: Optional[str] = None,
        size: int = 120,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._value = max(0.0, min(100.0, float(value)))
        self._label = label
        self._caption = caption
        self._ring_color = ring_color or styles.THEME.green
        self._size = size
        self.setFixedSize(size, size + (16 if caption else 0))

    def set_value(self, value: float, label: Optional[str] = None) -> None:
        self._value = max(0.0, min(100.0, float(value)))
        if label is not None:
            self._label = label
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        t = styles.THEME
        # Square area for the ring.
        ring_side = self._size
        margin = 10
        rect = QRectF(margin, margin, ring_side - 2 * margin, ring_side - 2 * margin)
        # Background ring (track).
        bg = QPen(QColor(t.progress_track), 9)
        bg.setCapStyle(Qt.RoundCap)
        p.setPen(bg)
        p.drawArc(rect, 0, 360 * 16)
        # Foreground arc (filled portion of the ring).
        fg = QPen(QColor(self._ring_color), 9)
        fg.setCapStyle(Qt.RoundCap)
        p.setPen(fg)
        span = int(self._value / 100.0 * 360 * 16)
        p.drawArc(rect, 90 * 16, -span)
        # Center label.
        p.setPen(QColor(t.text_primary))
        font = QFont()
        font.setPointSizeF(self._size / 8.0)
        font.setBold(True)
        p.setFont(font)
        text = self._label if self._label is not None else f"{self._value:.0f}%"
        p.drawText(rect, Qt.AlignCenter, text)
        # Optional caption below the ring.
        if self._caption:
            p.setPen(QColor(t.text_secondary))
            cap_font = QFont()
            cap_font.setPointSizeF(self._size / 14.0)
            p.setFont(cap_font)
            cap_rect = QRectF(0, ring_side, self.width(), 16)
            p.drawText(cap_rect, Qt.AlignCenter, self._caption)
        p.end()


# ---- Sparkline ------------------------------------------------------------

class Sparkline(QWidget):
    """Tiny inline line chart with optional filled area."""

    def __init__(
        self,
        values: Sequence[float],
        color: Optional[str] = None,
        fill: bool = True,
        height: int = 32,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._values = list(values)
        self._color = color or styles.THEME.cyan
        self._fill = fill
        self.setFixedHeight(height)
        self.setMinimumWidth(60)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())

    def set_values(self, values: Sequence[float]) -> None:
        self._values = list(values)
        self.update()

    def paintEvent(self, event) -> None:
        if not self._values:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = self.width(), self.height()
        vmin, vmax = min(self._values), max(self._values)
        if vmax == vmin:
            vmax = vmin + 1
        pad = 2
        n = len(self._values)
        pts = []
        for i, v in enumerate(self._values):
            x = pad + (w - 2 * pad) * (i / max(1, n - 1))
            y = pad + (h - 2 * pad) * (1 - (v - vmin) / (vmax - vmin))
            pts.append(QPointF(x, y))
        # Fill area.
        if self._fill and len(pts) >= 2:
            fill_path = QPainterPath(pts[0])
            for pt in pts[1:]:
                fill_path.lineTo(pt)
            fill_path.lineTo(QPointF(pts[-1].x(), h - pad))
            fill_path.lineTo(QPointF(pts[0].x(), h - pad))
            fill_path.closeSubpath()
            fill_color = QColor(self._color)
            fill_color.setAlpha(40)
            p.fillPath(fill_path, QBrush(fill_color))
        # Line.
        pen = QPen(QColor(self._color), 1.6)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        line_path = QPainterPath(pts[0])
        for pt in pts[1:]:
            line_path.lineTo(pt)
        p.drawPath(line_path)
        # End dot.
        p.setBrush(QColor(self._color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(pts[-1], 2.2, 2.2)
        p.end()


# ---- Network topology -----------------------------------------------------

class TopologyWidget(QWidget):
    """Custom-drawn star topology: center node + 5 surrounding nodes."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(360)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        t = styles.THEME
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        # Surrounding node positions (angle, distance_factor).
        # Order matches mock_data: LAB-DC-01 (top-left), WEB-01 (top-right),
        # LAB-WS-02 (left), DB-01 (right), INTERNET (bottom).
        from .mock_data import TOPOLOGY_NODES
        outer = [n for n in TOPOLOGY_NODES if not n.center]
        center = next((n for n in TOPOLOGY_NODES if n.center), None)
        # Compress the layout horizontally a bit and leave vertical room
        # for labels below the bottom node.
        radius_x = w * 0.28
        radius_y = h * 0.30
        # angles in degrees, 0 = right, 90 = up
        angles_deg = [135, 45, 180, 0, 270]
        positions = []
        import math
        for n, ang in zip(outer, angles_deg):
            a = math.radians(ang)
            # Nudge bottom node (INTERNET) upward so its label doesn't clip.
            yoff = -16 if ang == 270 else 0
            x = cx + radius_x * math.cos(a)
            y = cy - radius_y * math.sin(a) + yoff
            positions.append((n, x, y))
        # Draw glowing edges first.
        edge_pen = QPen(QColor(t.green), 2)
        edge_pen.setCapStyle(Qt.RoundCap)
        p.setPen(edge_pen)
        # Soft glow underlay.
        glow = QColor(t.green)
        glow.setAlpha(40)
        glow_pen = QPen(glow, 6)
        glow_pen.setCapStyle(Qt.RoundCap)
        for n, x, y in positions:
            p.setPen(glow_pen)
            p.drawLine(QPointF(cx, cy), QPointF(x, y))
            p.setPen(edge_pen)
            p.drawLine(QPointF(cx, cy), QPointF(x, y))
        # Draw outer nodes.
        node_r = 22
        for n, x, y in positions:
            self._draw_node(p, x, y, node_r, n.icon, n.name, n.ip, is_center=False)
        # Draw center node on top.
        if center:
            self._draw_node(p, cx, cy, 28, center.icon, center.name, center.ip, is_center=True)
        p.end()

    def _draw_node(self, p: QPainter, x: float, y: float, r: int,
                   icon: str, name: str, ip: str, is_center: bool) -> None:
        t = styles.THEME
        # Outer ring.
        if is_center:
            fill = QColor(t.green)
            edge = QColor(t.green)
            text_color = "#061A0E"
        else:
            fill = QColor("#112038")
            edge = QColor(t.card_border)
            text_color = t.text_primary
        # Glow for center.
        if is_center:
            glow = QColor(t.green)
            glow.setAlpha(60)
            p.setBrush(glow)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(x, y), r + 8, r + 8)
        p.setBrush(fill)
        pen = QPen(edge, 1.5)
        p.setPen(pen)
        p.drawEllipse(QPointF(x, y), r, r)
        # Icon glyph in the middle.
        p.setPen(QColor(text_color))
        font = QFont()
        font.setPointSizeF(r / 2.4)
        p.setFont(font)
        rect = QRectF(x - r, y - r, 2 * r, 2 * r)
        p.drawText(rect, Qt.AlignCenter, icon)
        # Labels below the node: name on top (white), IP underneath (muted).
        p.setPen(QColor(t.text_primary))
        name_font = QFont()
        name_font.setPointSizeF(8)
        name_font.setBold(True)
        p.setFont(name_font)
        name_rect = QRectF(x - 70, y + r + 4, 140, 14)
        p.drawText(name_rect, Qt.AlignCenter, name)
        p.setPen(QColor(t.text_secondary))
        ip_font = QFont()
        ip_font.setPointSizeF(7.5)
        p.setFont(ip_font)
        ip_rect = QRectF(x - 70, y + r + 18, 140, 12)
        p.drawText(ip_rect, Qt.AlignCenter, ip)


# ---- Matplotlib chart base ------------------------------------------------

class _BaseChart(FigureCanvas):
    """Base class with theme-aware figure setup."""

    def __init__(self, figsize=(7, 3.0), parent: Optional[QWidget] = None) -> None:
        self.fig = Figure(figsize=figsize, dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self._apply_theme()
        styles.register_listener(self._on_theme_change)

    def _on_theme_change(self, theme) -> None:
        self._apply_theme()
        self._draw()
        self.draw()

    def _apply_theme(self) -> None:
        t = styles.THEME
        self.fig.patch.set_facecolor(t.card_bg)

    def _draw(self) -> None:
        raise NotImplementedError


# ---- Activity chart (24h beaconing) --------------------------------------

class ActivityChart(_BaseChart):
    """Cyan baseline noisy traffic + tall green beacon spikes."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__((7, 3.2), parent)
        self._draw()

    def _draw(self) -> None:
        from .mock_data import _gen_24h_activity
        t = styles.THEME
        hours, baseline, beacon_hours, beacon_heights = _gen_24h_activity()
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        # Baseline cyan noisy traffic.
        ax.plot(hours, baseline, color=t.cyan, linewidth=1.8, label="Normal Traffic")
        ax.fill_between(hours, baseline, 0, color=t.cyan, alpha=0.08)
        # Beacon detection spikes (vertical stems with green dots).
        import numpy as np
        for h, ht in zip(beacon_hours, beacon_heights):
            # Find baseline value at hour h (rounded)
            base = baseline[min(h, len(baseline) - 1)]
            ax.plot([h, h], [base, ht], color=t.green, linewidth=1.6, alpha=0.85)
            ax.scatter([h], [ht], color=t.green, s=45, zorder=5,
                       edgecolors=t.card_bg, linewidths=1.2,
                       label="Detected Beacon" if h == beacon_hours[0] else None)
        # Axes.
        ax.set_xlim(0, 24)
        ax.set_ylim(0, 200)
        ax.set_xticks(range(0, 25, 3))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 25, 3)],
                           color=t.chart_axis_label, fontsize=8)
        ax.set_yticks([0, 50, 100, 150, 200])
        ax.set_yticklabels([str(v) for v in [0, 50, 100, 150, 200]],
                           color=t.chart_axis_label, fontsize=8)
        ax.tick_params(colors=t.chart_axis_label, length=0)
        for spine in ax.spines.values():
            spine.set_color(t.chart_spine)
        ax.grid(True, color=t.chart_grid, linewidth=0.7, axis="y")
        ax.set_axisbelow(True)
        ax.set_xlabel("")
        ax.set_ylabel("")
        # Legend top-right.
        # (Legend is rendered above the chart card by the dashboard, so we
        # skip the in-plot legend here to avoid duplication.)
        self.fig.tight_layout(pad=0.5)
        self.draw()


# ---- Timing chart (lollipop) ---------------------------------------------

class TimingChart(_BaseChart):
    """Green lollipop chart: interval vs time, with dashed expected line."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__((7, 2.8), parent)
        self._draw()

    def _draw(self) -> None:
        from .mock_data import _gen_timing_chart
        t = styles.THEME
        times, intervals = _gen_timing_chart()
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        import numpy as np
        x = np.arange(len(times))
        # Stems.
        for xi, yi in zip(x, intervals):
            ax.plot([xi, xi], [0, yi], color=t.green, linewidth=1.8, alpha=0.85)
        # Dot tops.
        ax.scatter(x, intervals, color=t.green, s=70, zorder=5,
                   edgecolors=t.card_bg, linewidths=1.5, label="Connection")
        # Expected interval dashed line at 600s.
        ax.axhline(600, color=t.text_muted, linestyle="--", linewidth=1.2,
                   label="Expected Interval")
        ax.set_ylim(0, 1200)
        ax.set_yticks([0, 300, 600, 900, 1200])
        ax.set_yticklabels(["0s", "300s", "600s", "900s", "1200s"],
                           color=t.chart_axis_label, fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(times, color=t.chart_axis_label, fontsize=8)
        ax.tick_params(colors=t.chart_axis_label, length=0)
        for spine in ax.spines.values():
            spine.set_color(t.chart_spine)
        ax.grid(True, color=t.chart_grid, linewidth=0.7, axis="y")
        ax.set_axisbelow(True)
        # Legend rendered above the chart card by the investigation page;
        # skip the in-plot legend here.
        self.fig.tight_layout(pad=0.5)
        self.draw()


# ---- Jitter chart ---------------------------------------------------------

class JitterChart(_BaseChart):
    """Small green line chart of jitter values with a spike near the end."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__((4, 1.4), parent)
        self._draw()

    def _draw(self) -> None:
        from .mock_data import _gen_jitter_chart
        t = styles.THEME
        idx, jitter = _gen_jitter_chart()
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        ax.plot(idx, jitter, color=t.green, linewidth=1.8, marker="o",
                markersize=4, markerfacecolor=t.green,
                markeredgecolor=t.card_bg)
        ax.fill_between(idx, jitter, 0, color=t.green, alpha=0.12)
        ax.set_ylim(0, 10)
        ax.set_xticks([])
        # Hide y-axis labels entirely — the panel is too narrow for them
        # and the "±4s" label above the chart already conveys the value.
        ax.set_yticks([])
        ax.tick_params(colors=t.chart_axis_label, length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(True, color=t.chart_grid, linewidth=0.6, axis="y")
        ax.set_axisbelow(True)
        self.fig.tight_layout(pad=0.3)
        self.draw()
