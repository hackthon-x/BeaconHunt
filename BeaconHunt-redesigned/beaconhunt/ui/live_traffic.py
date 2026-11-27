"""Live Traffic Monitor page — animated rolling view of simulated traffic.

The original BeaconHunt project is **offline-only**: it analyzes PCAP
captures and log files that the user opens manually, and never captures
live packets. That design decision is preserved here — this page does
not call ``scapy.sniff()`` and does not require root privileges.

Instead, this page demonstrates what a live-traffic panel would look
like inside the redesigned dashboard: a rolling 60-second traffic chart
that updates every second, a live events feed that periodically adds
new entries, and stat cards that tick up as "traffic" flows in. The
data is generated locally with ``random`` — it's a UI demo, not a
sensor.

If you want to wire this to a real sensor, replace the ``_tick`` method
with a call to your packet source (a scapy background sniffer, a
NetFlow collector, a syslog feed, etc.) and push real values into
``self._chart.push_value(...)`` and ``self._add_event(...)``.
"""
from __future__ import annotations

import random
from collections import deque
from typing import List

from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import styles

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


# ---- Stat card ------------------------------------------------------------

class _StatCard(QFrame):
    """One stat tile: label + big value + caption."""

    def __init__(self, label: str, value: str, caption: str,
                 color: str = None, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)
        self.label_lbl = QLabel(label)
        self.label_lbl.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:8.5pt; "
            f"font-weight:600; letter-spacing:0.5px;"
        )
        lay.addWidget(self.label_lbl)
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(
            f"color:{color or styles.THEME.text_primary}; "
            f"font-size:22pt; font-weight:800;"
        )
        lay.addWidget(self.value_lbl)
        self.caption_lbl = QLabel(caption)
        self.caption_lbl.setStyleSheet(
            f"color:{styles.THEME.text_muted}; font-size:8pt;"
        )
        lay.addWidget(self.caption_lbl)

    def set_value(self, value: str) -> None:
        self.value_lbl.setText(value)


# ---- Rolling chart --------------------------------------------------------

class _LiveChart(FigureCanvas):
    """Rolling 60-second line chart that updates on each ``push_value``."""

    def __init__(self, parent: QWidget = None) -> None:
        self.fig = Figure(figsize=(7, 3.2), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self._history: deque = deque([0] * 60, maxlen=60)
        self._apply_theme()
        self._draw()

    def _apply_theme(self) -> None:
        t = styles.THEME
        self.fig.patch.set_facecolor(t.card_bg)

    def push_value(self, value: float) -> None:
        self._history.append(value)
        self._draw()

    def _draw(self) -> None:
        t = styles.THEME
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        data = list(self._history)
        x = list(range(len(data)))
        # Rolling cyan line + soft fill.
        ax.plot(x, data, color=t.cyan, linewidth=1.8)
        ax.fill_between(x, data, 0, color=t.cyan, alpha=0.12)
        # Highlight the latest point with a green dot.
        ax.scatter([x[-1]], [data[-1]], color=t.green, s=42, zorder=5,
                   edgecolors=t.card_bg, linewidths=1.5)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 220)
        ax.set_xticks([])
        ax.set_yticks([0, 50, 100, 150, 200])
        ax.set_yticklabels(["0", "50", "100", "150", "200"],
                           color=t.chart_axis_label, fontsize=8)
        ax.tick_params(colors=t.chart_axis_label, length=0)
        for spine in ax.spines.values():
            spine.set_color(t.chart_spine)
        ax.grid(True, color=t.chart_grid, linewidth=0.7, axis="y")
        ax.set_axisbelow(True)
        self.fig.tight_layout(pad=0.5)
        self.draw()


# ---- Live Traffic page ----------------------------------------------------

# Simulated source/destination pools for the events feed.
_SRC_POOL = [
    "10.0.1.23", "10.0.1.5", "10.0.2.12", "10.0.3.8", "10.0.1.17",
    "10.0.4.2", "10.0.2.99",
]
_DST_POOL = [
    "192.0.2.10", "198.51.100.24", "203.0.113.77", "8.8.8.8",
    "1.1.1.1", "93.184.216.34", "104.16.132.229",
]
_PROTOCOLS = ["TCP", "UDP", "HTTPS", "DNS"]
_TITLES = [
    ("green",  "Outbound connection established"),
    ("cyan",   "DNS query resolved"),
    ("yellow", "Retransmission detected"),
    ("green",  "HTTPS handshake completed"),
    ("cyan",   "Keep-alive packet"),
    ("yellow", "Unusual port observed"),
    ("green",  "TCP SYN received"),
]


class LiveTrafficPage(QWidget):
    """The redesigned Live Traffic Monitor page (animated mock data)."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setObjectName("Content")

        # Counters that tick up.
        self._total_packets = 0
        self._total_events = 0
        self._threats = 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(14)

        # --- Title row + listening indicator ---
        title_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title = QLabel("Live Traffic Monitor")
        title.setObjectName("PageTitle")
        title_col.addWidget(title)
        sub = QLabel("Real-time view of network traffic on interface eth0")
        sub.setObjectName("PageSubtitle")
        title_col.addWidget(sub)
        title_row.addLayout(title_col)
        title_row.addStretch()
        # LISTENING indicator.
        listen_row = QHBoxLayout()
        listen_row.setSpacing(8)
        self.dot = QLabel("●")
        self.dot.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:14pt; padding-top:1px;"
        )
        listen_row.addWidget(self.dot)
        self.listening_lbl = QLabel("LISTENING")
        self.listening_lbl.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:9pt; font-weight:700; "
            f"letter-spacing:1.5px;"
        )
        listen_row.addWidget(self.listening_lbl)
        title_row.addLayout(listen_row)
        outer.addLayout(title_row)

        # --- Stat cards row ---
        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        self.card_packets = _StatCard(
            "PACKETS/SEC", "0", "Current throughput",
            color=styles.THEME.cyan,
        )
        self.card_total = _StatCard(
            "TOTAL PACKETS", "0", "Since capture started",
        )
        self.card_events = _StatCard(
            "EVENTS", "0", "Connections observed",
        )
        self.card_threats = _StatCard(
            "SUSPICIOUS", "0", "Patterns flagged",
            color=styles.THEME.sev_high_fg,
        )
        for c in (self.card_packets, self.card_total,
                  self.card_events, self.card_threats):
            stat_row.addWidget(c, 1)
        outer.addLayout(stat_row)

        # --- Main grid: chart (left) + events feed (right) ---
        grid = QHBoxLayout()
        grid.setSpacing(14)

        # Left: rolling chart card.
        chart_card = QFrame()
        chart_card.setObjectName("Card")
        cl = QVBoxLayout(chart_card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(10)
        chead = QHBoxLayout()
        ctitle = QLabel("Traffic Rate (last 60 seconds)")
        ctitle.setObjectName("CardTitle")
        chead.addWidget(ctitle)
        chead.addStretch()
        cintf = QLabel("Interface: ")
        cintf.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt;"
        )
        chead.addWidget(cintf)
        cintf_name = QLabel("eth0")
        cintf_name.setStyleSheet(
            f"color:{styles.THEME.cyan}; font-size:9pt; font-weight:700;"
        )
        chead.addWidget(cintf_name)
        cl.addLayout(chead)
        self.chart = _LiveChart()
        self.chart.setFixedHeight(240)
        cl.addWidget(self.chart)
        # Hint about how to wire this to a real sensor.
        hint = QLabel(
            "ⓘ  Simulated traffic feed. Replace _tick() in live_traffic.py "
            "with a real packet source (scapy sniffer, NetFlow, syslog)."
        )
        hint.setStyleSheet(
            f"color:{styles.THEME.text_muted}; font-size:8pt;"
        )
        hint.setWordWrap(True)
        cl.addWidget(hint)
        grid.addWidget(chart_card, 65)

        # Right: live events feed.
        events_card = QFrame()
        events_card.setObjectName("Card")
        el = QVBoxLayout(events_card)
        el.setContentsMargins(16, 14, 16, 14)
        el.setSpacing(10)
        ehead = QHBoxLayout()
        etitle = QLabel("Live Events")
        etitle.setObjectName("CardTitle")
        ehead.addWidget(etitle)
        ehead.addStretch()
        elive = QLabel("● LIVE")
        elive.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:8.5pt; font-weight:700;"
        )
        ehead.addWidget(elive)
        el.addLayout(ehead)
        # Events table.
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time", "Source", "Destination", "Protocol"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        modes = [
            QHeaderView.ResizeToContents,
            QHeaderView.Stretch,
            QHeaderView.Stretch,
            QHeaderView.ResizeToContents,
        ]
        for i, m in enumerate(modes):
            self.table.horizontalHeader().setSectionResizeMode(i, m)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setTextElideMode(Qt.ElideNone)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        el.addWidget(self.table)
        grid.addWidget(events_card, 35)

        outer.addLayout(grid, 1)

        # --- Timer that drives the live updates ---
        self._timer = QTimer(self)
        self._timer.setInterval(1000)   # 1 second
        self._timer.timeout.connect(self._tick)
        # Don't start automatically — start when the page becomes visible.

    # ------------------------------------------------------------------ lifecycle
    def start(self) -> None:
        """Begin the live-updates timer. Call when the page is shown."""
        if not self._timer.isActive():
            self._timer.start()

    def stop(self) -> None:
        """Stop the live-updates timer. Call when the page is hidden."""
        if self._timer.isActive():
            self._timer.stop()

    # ------------------------------------------------------------------ tick
    def _tick(self) -> None:
        """One second of simulated traffic.

        Replace this method body with a real packet source to wire the
        page to live data.
        """
        # Generate a new packets/sec value with some smoothing.
        base = 90 + 30 * random.random()
        spike = 80 if random.random() < 0.15 else 0
        packets_per_sec = int(base + spike)
        self._total_packets += packets_per_sec
        self._total_events += 1
        if spike > 0 and random.random() < 0.4:
            self._threats += 1

        # Update chart.
        self.chart.push_value(packets_per_sec)

        # Update stat cards.
        self.card_packets.set_value(f"{packets_per_sec}")
        self.card_total.set_value(f"{self._total_packets:,}")
        self.card_events.set_value(f"{self._total_events:,}")
        self.card_threats.set_value(f"{self._threats}")

        # Add a new event row most ticks so the feed feels alive.
        if random.random() < 0.8:
            self._add_event()

    def _add_event(self) -> None:
        src = random.choice(_SRC_POOL)
        dst = random.choice(_DST_POOL)
        proto = random.choice(_PROTOCOLS)
        now = QTime.currentTime().toString("HH:mm:ss")
        # Prepend new row at the top.
        self.table.insertRow(0)
        cells = [now, src, dst, proto]
        for j, text in enumerate(cells):
            item = QTableWidgetItem(text)
            self.table.setItem(0, j, item)
        # Cap the table at 50 rows so memory doesn't grow unbounded.
        while self.table.rowCount() > 50:
            self.table.removeRow(self.table.rowCount() - 1)
