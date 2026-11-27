"""Beacon Analysis page — cross-destination comparison of beacon candidates.

This is the analyst's triage view: every detected beacon candidate laid
out in one comparison table, with summary stats, distribution charts,
and a mini timing chart for the currently selected row.

Layout:
  * Page title + subtitle.
  * Filter bar (severity filter, min-confidence filter, search box).
  * Four summary stat cards: Total Beacons, High Severity, Avg
    Confidence, Most Common Interval.
  * Two distribution charts side-by-side: confidence histogram (green
    bars) and interval distribution (cyan bars).
  * A wide comparison table (Source / Destination / Port / Protocol /
    Interval / Jitter / Confidence / Severity / Events / Bytes).
    Selecting a row updates the mini timing chart below it.
  * A mini timing chart for the selected beacon — same lollipop style
    as the Beacon Investigation page, drawn from the candidate's
    interval + jitter.

All data comes from ``beaconhunt.ui.mock_data.BEACON_CANDIDATES``.
"""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from . import styles
from .mock_data import BEACON_CANDIDATES, BeaconCandidate

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


# ---- Stat card ------------------------------------------------------------

class _StatCard(QFrame):
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


# ---- Card wrapper ---------------------------------------------------------

class _Card(QFrame):
    def __init__(self, title: str, subtitle: str = "",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)
        head = QHBoxLayout()
        head.setSpacing(8)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("CardTitle")
        titles.addWidget(self.title_lbl)
        if subtitle:
            self.sub_lbl = QLabel(subtitle)
            self.sub_lbl.setObjectName("CardSubtitle")
            titles.addWidget(self.sub_lbl)
        head.addLayout(titles)
        head.addStretch()
        outer.addLayout(head)
        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        outer.addLayout(self.body, 1)


# ---- Distribution charts --------------------------------------------------

class _ConfidenceHistogram(FigureCanvas):
    """Histogram of candidate confidence values (green bars)."""

    def __init__(self, candidates: List[BeaconCandidate],
                 parent: QWidget = None) -> None:
        self.fig = Figure(figsize=(5, 2.5), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self._candidates = candidates
        self._apply_theme()
        self._draw()

    def _apply_theme(self) -> None:
        t = styles.THEME
        self.fig.patch.set_facecolor(t.card_bg)

    def update_candidates(self, candidates: List[BeaconCandidate]) -> None:
        self._candidates = candidates
        self._draw()

    def _draw(self) -> None:
        t = styles.THEME
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        # Bin the confidence values into 5 buckets: 0-20, 20-40, ..., 80-100.
        bins = [0, 20, 40, 60, 80, 100]
        counts = [0] * (len(bins) - 1)
        for c in self._candidates:
            for i in range(len(bins) - 1):
                if bins[i] <= c.confidence < bins[i + 1] or (
                    i == len(bins) - 2 and c.confidence == 100
                ):
                    counts[i] += 1
                    break
        labels = ["0-20", "20-40", "40-60", "60-80", "80-100"]
        ax.bar(labels, counts, color=t.green, edgecolor=t.card_bg, linewidth=1)
        ax.set_ylim(0, max(counts) + 1 if counts else 1)
        ax.set_ylabel("Beacons", color=t.chart_axis_label, fontsize=8)
        ax.set_xlabel("Confidence %", color=t.chart_axis_label, fontsize=8)
        ax.tick_params(colors=t.chart_axis_label, length=0, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(t.chart_spine)
        ax.grid(True, color=t.chart_grid, linewidth=0.7, axis="y")
        ax.set_axisbelow(True)
        self.fig.tight_layout(pad=0.5)
        self.draw()


class _IntervalDistribution(FigureCanvas):
    """Bar chart of how many beacons use each interval (cyan bars)."""

    def __init__(self, candidates: List[BeaconCandidate],
                 parent: QWidget = None) -> None:
        self.fig = Figure(figsize=(5, 2.5), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self._candidates = candidates
        self._apply_theme()
        self._draw()

    def _apply_theme(self) -> None:
        t = styles.THEME
        self.fig.patch.set_facecolor(t.card_bg)

    def update_candidates(self, candidates: List[BeaconCandidate]) -> None:
        self._candidates = candidates
        self._draw()

    def _draw(self) -> None:
        t = styles.THEME
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        # Group by interval_sec.
        from collections import Counter
        counter = Counter(c.interval_sec for c in self._candidates)
        intervals = sorted(counter.keys())
        counts = [counter[i] for i in intervals]
        labels = [f"{i}s" for i in intervals]
        ax.bar(labels, counts, color=t.cyan, edgecolor=t.card_bg, linewidth=1)
        ax.set_ylim(0, max(counts) + 1 if counts else 1)
        ax.set_ylabel("Beacons", color=t.chart_axis_label, fontsize=8)
        ax.set_xlabel("Interval", color=t.chart_axis_label, fontsize=8)
        ax.tick_params(colors=t.chart_axis_label, length=0, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(t.chart_spine)
        ax.grid(True, color=t.chart_grid, linewidth=0.7, axis="y")
        ax.set_axisbelow(True)
        self.fig.tight_layout(pad=0.5)
        self.draw()


# ---- Mini timing chart (for selected row) --------------------------------

class _MiniTimingChart(FigureCanvas):
    """Small lollipop chart for the selected beacon's interval pattern."""

    def __init__(self, parent: QWidget = None) -> None:
        self.fig = Figure(figsize=(6, 2.2), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self._apply_theme()
        self._draw_empty()

    def _apply_theme(self) -> None:
        t = styles.THEME
        self.fig.patch.set_facecolor(t.card_bg)

    def _draw_empty(self) -> None:
        t = styles.THEME
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        ax.text(0.5, 0.5, "Select a beacon row to view its timing pattern",
                ha="center", va="center", transform=ax.transAxes,
                color=t.text_muted, fontsize=9)
        ax.set_axis_off()
        self.fig.tight_layout(pad=0.3)
        self.draw()

    def draw_candidate(self, c: BeaconCandidate) -> None:
        t = styles.THEME
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(t.card_bg)
        import random
        rng = random.Random(hash((c.source, c.destination, c.interval_sec)) & 0xFFFF)
        # Generate event_count intervals around the candidate's interval_sec
        # with jitter drawn from [0, jitter_sec].
        n = c.event_count
        intervals = [
            c.interval_sec + rng.randint(-c.jitter_sec, c.jitter_sec)
            for _ in range(n)
        ]
        x = list(range(1, n + 1))
        for xi, yi in zip(x, intervals):
            ax.plot([xi, xi], [0, yi], color=t.green, linewidth=1.8, alpha=0.85)
        ax.scatter(x, intervals, color=t.green, s=60, zorder=5,
                   edgecolors=t.card_bg, linewidths=1.5)
        ax.axhline(c.interval_sec, color=t.text_muted, linestyle="--",
                   linewidth=1.2)
        ax.set_ylim(0, max(intervals) + c.jitter_sec + 50 if intervals else 100)
        ax.set_xticks(x)
        ax.set_xticklabels([f"#{i}" for i in x],
                           color=t.chart_axis_label, fontsize=7)
        ax.tick_params(colors=t.chart_axis_label, length=0, labelsize=7)
        for spine in ax.spines.values():
            spine.set_color(t.chart_spine)
        ax.grid(True, color=t.chart_grid, linewidth=0.7, axis="y")
        ax.set_axisbelow(True)
        self.fig.tight_layout(pad=0.3)
        self.draw()


# ---- Beacon Analysis page -------------------------------------------------

class BeaconAnalysisPage(QWidget):
    """Cross-destination comparison view of all detected beacon candidates."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Content")
        self._all = list(BEACON_CANDIDATES)
        self._filtered: List[BeaconCandidate] = list(self._all)
        self._selected: Optional[BeaconCandidate] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(14)

        # --- Title ---
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Beacon Analysis")
        title.setObjectName("PageTitle")
        title_block.addWidget(title)
        sub = QLabel("Cross-destination comparison of detected beaconing patterns.")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(sub)
        outer.addLayout(title_block)

        # --- Filter bar ---
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        sev_label = QLabel("Severity:")
        sev_label.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:600;"
        )
        filter_row.addWidget(sev_label)
        self.sev_combo = QComboBox()
        self.sev_combo.addItems(["All", "High", "Medium", "Low"])
        self.sev_combo.setFixedWidth(120)
        self.sev_combo.currentTextChanged.connect(self._refilter)
        filter_row.addWidget(self.sev_combo)
        conf_label = QLabel("Min confidence:")
        conf_label.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:600;"
        )
        filter_row.addWidget(conf_label)
        self.conf_combo = QComboBox()
        self.conf_combo.addItems(["0%", "50%", "60%", "70%", "80%", "90%"])
        self.conf_combo.setFixedWidth(80)
        self.conf_combo.currentTextChanged.connect(self._refilter)
        filter_row.addWidget(self.conf_combo)
        filter_row.addSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search source or destination IP…")
        self.search.setFixedWidth(260)
        self.search.textChanged.connect(self._refilter)
        filter_row.addWidget(self.search)
        filter_row.addStretch()
        self.count_lbl = QLabel(f"{len(self._filtered)} candidates")
        self.count_lbl.setStyleSheet(
            f"color:{styles.THEME.text_muted}; font-size:9pt; font-weight:600;"
        )
        filter_row.addWidget(self.count_lbl)
        outer.addLayout(filter_row)

        # --- Stat cards row ---
        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        self.card_total = _StatCard(
            "TOTAL BEACONS", "0", "Detected candidates",
            color=styles.THEME.cyan,
        )
        self.card_high = _StatCard(
            "HIGH SEVERITY", "0", "Confidence ≥ 80%",
            color=styles.THEME.sev_high_fg,
        )
        self.card_avg = _StatCard(
            "AVG CONFIDENCE", "0%", "Across all candidates",
        )
        self.card_top = _StatCard(
            "MOST COMMON", "—", "Interval observed",
            color=styles.THEME.green,
        )
        for c in (self.card_total, self.card_high, self.card_avg, self.card_top):
            stat_row.addWidget(c, 1)
        outer.addLayout(stat_row)

        # --- Distribution charts row ---
        charts_row = QHBoxLayout()
        charts_row.setSpacing(14)
        conf_card = _Card("Confidence Distribution",
                          "How candidates are distributed by score")
        self.conf_chart = _ConfidenceHistogram(self._filtered)
        self.conf_chart.setFixedHeight(180)
        conf_card.body.addWidget(self.conf_chart)
        charts_row.addWidget(conf_card, 1)
        intv_card = _Card("Interval Distribution",
                          "How many beacons use each interval")
        self.intv_chart = _IntervalDistribution(self._filtered)
        self.intv_chart.setFixedHeight(180)
        intv_card.body.addWidget(self.intv_chart)
        charts_row.addWidget(intv_card, 1)
        outer.addLayout(charts_row)

        # --- Comparison table ---
        table_card = _Card("Beacon Comparison",
                           "Select a row to inspect its timing pattern below")
        self.table = self._build_table()
        table_card.body.addWidget(self.table)
        outer.addWidget(table_card, 1)

        # --- Mini timing chart for selected row ---
        timing_card = _Card("Selected Beacon Timing",
                            "Interval pattern for the selected candidate")
        self.mini_chart = _MiniTimingChart()
        self.mini_chart.setFixedHeight(160)
        timing_card.body.addWidget(self.mini_chart)
        outer.addWidget(timing_card)

        # Initial population.
        self._refilter()

    # ------------------------------------------------------------------ helpers
    def _build_table(self) -> QTableWidget:
        cols = ["Source", "Destination", "Port", "Proto",
                "Int.", "Jitter", "Conf.", "Severity",
                "Events", "Bytes", "Status"]
        table = QTableWidget()
        table.setColumnCount(len(cols))
        table.setHorizontalHeaderLabels(cols)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setHighlightSections(False)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        table.horizontalHeader().setStretchLastSection(False)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Stretch the first two columns, fixed widths for the short ones.
        modes = [
            QHeaderView.Stretch,            # source
            QHeaderView.Stretch,            # destination
            QHeaderView.Interactive,        # port
            QHeaderView.Interactive,        # proto
            QHeaderView.Interactive,        # int
            QHeaderView.Interactive,        # jitter
            QHeaderView.Interactive,        # conf
            QHeaderView.Interactive,        # severity
            QHeaderView.Interactive,        # events
            QHeaderView.Interactive,        # bytes
            QHeaderView.Interactive,        # status
        ]
        for i, m in enumerate(modes):
            table.horizontalHeader().setSectionResizeMode(i, m)
        # Tighter widths so the table fits the card without horizontal clip.
        explicit = {2: 50, 3: 55, 4: 55, 5: 60, 6: 50, 7: 80, 8: 60, 9: 70, 10: 90}
        for i, w in explicit.items():
            table.horizontalHeader().resizeSection(i, w)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setTextElideMode(Qt.ElideNone)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.itemSelectionChanged.connect(self._on_row_selected)
        return table

    def _refilter(self) -> None:
        sev = self.sev_combo.currentText()
        min_conf = int(self.conf_combo.currentText().rstrip("%"))
        needle = self.search.text().strip().lower()
        self._filtered = []
        for c in self._all:
            if sev != "All" and c.severity != sev:
                continue
            if c.confidence < min_conf:
                continue
            if needle and needle not in c.source.lower() and needle not in c.destination.lower():
                continue
            self._filtered.append(c)
        self._populate_table()
        self._update_stats()
        self._update_charts()
        self.count_lbl.setText(f"{len(self._filtered)} candidates")

    def _populate_table(self) -> None:
        # Block selection signals while repopulating so we don't fire a
        # spurious selection on a row that's about to be replaced.
        self.table.blockSignals(True)
        self.table.setRowCount(len(self._filtered))
        for i, c in enumerate(self._filtered):
            cells = [
                c.source,
                c.destination,
                str(c.port),
                c.protocol,
                f"{c.interval_sec}s",
                f"±{c.jitter_sec}s",
                f"{c.confidence}%",
                c.severity,
                str(c.event_count),
                f"{c.bytes_total:,}",
                c.status,
            ]
            for j, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, c)
                self.table.setItem(i, j, item)
            # Severity pill cell widget.
            sev = QLabel(c.severity)
            sev.setObjectName({
                "High":   "SevHigh",
                "Medium": "SevMedium",
                "Low":    "SevLow",
            }[c.severity])
            sev.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(i, 7, sev)
            # Status with colored dot.
            status_widget = QWidget()
            sl = QHBoxLayout(status_widget)
            sl.setContentsMargins(0, 0, 0, 0)
            sl.setSpacing(6)
            dot_color = (styles.THEME.active_dot
                         if c.status == "Active"
                         else styles.THEME.resolved_dot)
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{dot_color}; font-size:10pt;")
            sl.addWidget(dot)
            status_lbl = QLabel(c.status)
            status_lbl.setObjectName(
                "StatusActive" if c.status == "Active" else "StatusResolved"
            )
            sl.addWidget(status_lbl, 1)
            self.table.setCellWidget(i, 10, status_widget)
        self.table.blockSignals(False)
        # Auto-select the first row so the mini timing chart shows data
        # immediately on first render and after each refilter.
        if self._filtered:
            self.table.selectRow(0)
            self._on_row_selected()

    def _update_stats(self) -> None:
        total = len(self._filtered)
        high = sum(1 for c in self._filtered if c.severity == "High")
        avg = (sum(c.confidence for c in self._filtered) / total) if total else 0
        # Most common interval.
        from collections import Counter
        counter = Counter(c.interval_sec for c in self._filtered)
        top_interval = f"{counter.most_common(1)[0][0]}s" if counter else "—"
        self.card_total.value_lbl.setText(str(total))
        self.card_high.value_lbl.setText(str(high))
        self.card_avg.value_lbl.setText(f"{avg:.0f}%")
        self.card_top.value_lbl.setText(top_interval)

    def _update_charts(self) -> None:
        self.conf_chart.update_candidates(self._filtered)
        self.intv_chart.update_candidates(self._filtered)

    def _on_row_selected(self) -> None:
        items = self.table.selectedItems()
        if not items:
            return
        c = items[0].data(Qt.UserRole)
        if c is None:
            return
        self._selected = c
        self.mini_chart.draw_candidate(c)
