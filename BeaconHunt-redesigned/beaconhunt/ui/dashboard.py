"""Network Activity Overview page — matches the top view of the reference.

Layout (left to right):

  * Main column (~62%):
      - "Beaconing Activity (Last 24 Hours)" chart card.
      - "Suspicious Periodic Connections" table card.
  * Middle column (~22%):
      - "Network Topology" custom widget card.
      - "Recent Events" card with colored dots + "View all alerts" link.
  * Right sidebar (~16%):
      - "Beacon Analysis" card (12 potential beacons + ECG glyph).
      - "Top Beaconing Destinations" card with cyan progress bars.
      - "Detection Confidence" card with green donut (87%) + sparkline.
      - "Recent Events" card (repeat).

All data comes from :mod:`beaconhunt.ui.mock_data` so the page renders
identically to the reference screenshot.
"""
from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import styles
from .mock_data import (
    SUSPICIOUS_ROWS, RECENT_EVENTS, TOP_DESTINATIONS,
    POTENTIAL_BEACONS_COUNT, DETECTION_CONFIDENCE_PCT,
)
from .widgets import ActivityChart, DonutGauge, Sparkline, TopologyWidget


# ---- Event dot color lookup ----------------------------------------------

_EVENT_DOT_COLOR = {
    "green":  styles.THEME.green,
    "yellow": "#FACC15",
    "cyan":   styles.THEME.cyan,
}


class _Card(QFrame):
    """Convenience wrapper around QFrame#Card with a title + subtitle header."""

    def __init__(self, title: str, subtitle: str = "", parent: Optional[QWidget] = None) -> None:
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


# Allow `Optional` import without changing top-of-file imports.
from typing import Optional


class OverviewPage(QWidget):
    """The redesigned Network Activity Overview."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Content")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(16)

        # --- Page title ---
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Network Activity Overview")
        title.setObjectName("PageTitle")
        title_block.addWidget(title)
        sub = QLabel("Real-time view of network connections and potential beaconing behavior.")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(sub)
        outer.addLayout(title_block)

        # --- Three-column grid ---
        grid = QHBoxLayout()
        grid.setSpacing(14)

        # Left column: activity chart + suspicious table.
        left = QVBoxLayout()
        left.setSpacing(14)

        # Activity chart card.
        activity_card = _Card("Beaconing Activity", "Last 24 hours")
        # Legend row.
        legend = QHBoxLayout()
        legend.addStretch()
        self.leg_normal = QLabel("— Normal Traffic")
        self.leg_normal.setStyleSheet(
            f"color:{styles.THEME.cyan}; font-size:8.5pt; font-weight:600; padding-right:14px;"
        )
        legend.addWidget(self.leg_normal)
        self.leg_beacon = QLabel("● Detected Beacon")
        self.leg_beacon.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:8.5pt; font-weight:600;"
        )
        legend.addWidget(self.leg_beacon)
        activity_card.body.addLayout(legend)
        self.activity_chart = ActivityChart()
        self.activity_chart.setFixedHeight(220)
        activity_card.body.addWidget(self.activity_chart)
        left.addWidget(activity_card)

        # Suspicious table card.
        table_card = _Card("Suspicious Periodic Connections",
                           "Detected beaconing patterns across the network")
        self.table = self._build_suspicious_table()
        table_card.body.addWidget(self.table)
        left.addWidget(table_card)

        # Wrap left column in a fixed-width widget so the grid honors
        # the proportions deterministically.
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setMinimumWidth(820)
        grid.addWidget(left_widget, 68)

        # Middle column: topology + recent events.
        middle = QVBoxLayout()
        middle.setSpacing(14)

        topo_card = _Card("Network Topology", "LAB segment")
        self.topo = TopologyWidget()
        self.topo.setMinimumHeight(340)
        topo_card.body.addWidget(self.topo)
        middle.addWidget(topo_card)

        events_card = _Card("Recent Events", "")
        for ev in RECENT_EVENTS:
            row = self._make_event_row(ev)
            events_card.body.addLayout(row)
        # "View all alerts" link.
        link_row = QHBoxLayout()
        link_row.addStretch()
        self.view_all = QLabel("View all alerts →")
        self.view_all.setStyleSheet(
            f"color:{styles.THEME.cyan}; font-size:9pt; font-weight:600; padding-top:4px;"
        )
        self.view_all.setCursor(Qt.PointingHandCursor)
        link_row.addWidget(self.view_all)
        events_card.body.addLayout(link_row)
        middle.addWidget(events_card)

        middle_widget = QWidget()
        middle_widget.setLayout(middle)
        middle_widget.setMinimumWidth(260)
        grid.addWidget(middle_widget, 20)
        # Right sidebar: 4 stacked cards.
        right = QVBoxLayout()
        right.setSpacing(14)

        # Beacon Analysis card.
        ba = _Card("Beacon Analysis", "")
        ba_row = QHBoxLayout()
        ba_row.setSpacing(10)
        ba_count = QLabel(str(POTENTIAL_BEACONS_COUNT))
        ba_count.setStyleSheet(
            f"background:{styles.THEME.green}; color:#061A0E; "
            f"border-radius:18px; min-width:36px; min-height:36px; "
            f"font-size:14pt; font-weight:800; padding:4px;"
        )
        ba_count.setAlignment(Qt.AlignCenter)
        ba_row.addWidget(ba_count)
        ba_text = QVBoxLayout()
        ba_text.setSpacing(0)
        ba_text.addWidget(QLabel("Potential"))
        ba_text.addWidget(QLabel("Beacons"))
        for w in ba_text.children():
            pass
        # We want "Potential Beacons" two-line label that uses muted color.
        ba_label_potential = QLabel("Potential")
        ba_label_potential.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:500;"
        )
        ba_label_beacons = QLabel("Beacons")
        ba_label_beacons.setStyleSheet(
            f"color:{styles.THEME.text_primary}; font-size:11pt; font-weight:700;"
        )
        ba_text2 = QVBoxLayout()
        ba_text2.setSpacing(0)
        ba_text2.addWidget(ba_label_potential)
        ba_text2.addWidget(ba_label_beacons)
        ba_row.addLayout(ba_text2)
        ba_row.addStretch()
        # ECG glyph on the right.
        ecg = QLabel("∿")
        ecg.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:16pt; font-weight:800;"
        )
        ba_row.addWidget(ecg)
        ba.body.addLayout(ba_row)
        right.addWidget(ba)

        # Top beaconing destinations.
        td = _Card("Top Beaconing", "Destinations")
        for d in TOP_DESTINATIONS:
            row = QVBoxLayout()
            row.setSpacing(4)
            top = QHBoxLayout()
            ip_lbl = QLabel(d.ip)
            ip_lbl.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9.5pt; font-weight:600;"
            )
            top.addWidget(ip_lbl)
            top.addStretch()
            count_lbl = QLabel(str(d.count))
            count_lbl.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:600;"
            )
            top.addWidget(count_lbl)
            row.addLayout(top)
            # Progress bar mimic: a thin track + filled chunk.
            bar_wrap = QWidget()
            bar_wrap.setFixedHeight(5)
            bar_lay = QHBoxLayout(bar_wrap)
            bar_lay.setContentsMargins(0, 0, 0, 0)
            bar_lay.setSpacing(0)
            track = QFrame()
            track.setStyleSheet(
                f"background:{styles.THEME.progress_track}; border-radius:2px; max-height:5px;"
            )
            track.setFixedHeight(5)
            fill = QFrame()
            fill.setStyleSheet(
                f"background:{styles.THEME.cyan}; border-radius:2px; max-height:5px;"
            )
            fill.setFixedHeight(5)
            # Use a stretch-based layout: fill = bar_pct%, track = 100-bar_pct%.
            from PySide6.QtWidgets import QSizePolicy as QSP
            sp_fill = QSP(QSP.Preferred, QSP.Fixed)
            sp_track = QSP(QSP.Expanding, QSP.Fixed)
            # Set fixed widths via minimum widths on a horizontal sub-layout.
            sub = QHBoxLayout()
            sub.setContentsMargins(0, 0, 0, 0)
            sub.setSpacing(0)
            fill_w = QFrame()
            fill_w.setStyleSheet(
                f"background:{styles.THEME.cyan}; border-radius:2px;"
            )
            fill_w.setFixedHeight(5)
            track_w = QFrame()
            track_w.setStyleSheet(
                f"background:{styles.THEME.progress_track}; border-radius:2px;"
            )
            track_w.setFixedHeight(5)
            sub.addWidget(fill_w, d.bar_pct)
            sub.addWidget(track_w, 100 - d.bar_pct)
            bar_lay.addWidget(fill_w)
            # Replace bar_wrap content with sub layout instead.
            bar_wrap.setLayout(sub)
            # Remove the earlier track/fill widgets (they're unused).
            track.setParent(None)
            fill.setParent(None)
            row.addWidget(bar_wrap)
            td.body.addLayout(row)
            td.body.addSpacing(2)
        right.addWidget(td)

        # Detection confidence donut.
        dc = _Card("Detection", "Confidence")
        dc_row = QHBoxLayout()
        dc_row.setSpacing(12)
        self.donut = DonutGauge(
            value=DETECTION_CONFIDENCE_PCT,
            label=f"{DETECTION_CONFIDENCE_PCT}%",
            ring_color=styles.THEME.green,
            size=110,
        )
        dc_row.addWidget(self.donut)
        dc_text = QVBoxLayout()
        dc_text.setSpacing(2)
        dc_high = QLabel("High Confidence")
        dc_high.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:10pt; font-weight:700;"
        )
        dc_text.addWidget(dc_high)
        dc_desc = QLabel("Based on periodicity, timing and connection patterns.")
        dc_desc.setWordWrap(True)
        dc_desc.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:8.5pt;"
        )
        dc_text.addWidget(dc_desc)
        dc_row.addLayout(dc_text, 1)
        dc.body.addLayout(dc_row)
        dc.body.addSpacing(6)
        # Green sparkline below.
        from .mock_data import _gen_confidence_sparkline
        self.dc_spark = Sparkline(
            _gen_confidence_sparkline(),
            color=styles.THEME.green,
            height=28,
        )
        dc.body.addWidget(self.dc_spark)
        right.addWidget(dc)

        # Recent events repeat card.
        re = _Card("Recent Events", "")
        for ev in RECENT_EVENTS:
            row = self._make_event_row(ev, compact=True)
            re.body.addLayout(row)
        right.addWidget(re)

        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setMinimumWidth(220)
        grid.addWidget(right_widget, 12)

        outer.addLayout(grid, 1)

    # ------------------------------------------------------------------ helpers
    def _build_suspicious_table(self) -> QTableWidget:
        # Short header labels chosen to fit the column widths we allocate.
        cols = ["Time (UTC)", "Source", "Destination", "Int.",
                "Jitter", "Conf.", "Severity", "Status"]
        table = QTableWidget()
        table.setColumnCount(len(cols))
        table.setHorizontalHeaderLabels(cols)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setHighlightSections(False)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        table.horizontalHeader().setStretchLastSection(False)
        # Disable horizontal scrollbar — the table should always fit its
        # card width. Use Interactive mode with explicit widths that fit
        # the data, then Stretch on Time + Destination so they grow to
        # fill remaining space.
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        modes = [
            QHeaderView.Stretch,           # time
            QHeaderView.Interactive,       # source
            QHeaderView.Stretch,           # destination
            QHeaderView.Interactive,       # int
            QHeaderView.Interactive,       # jitter
            QHeaderView.Interactive,       # conf
            QHeaderView.Interactive,       # severity
            QHeaderView.Interactive,       # status
        ]
        for i, m in enumerate(modes):
            table.horizontalHeader().setSectionResizeMode(i, m)
        # Explicit widths for the Interactive columns — chosen to fit the
        # widest cell content (IPs, pill widgets, dot+label widgets) with
        # 8px cell padding each side.
        explicit_widths = {1: 95, 3: 55, 4: 60, 5: 60, 6: 90, 7: 110}
        for i, w in explicit_widths.items():
            table.horizontalHeader().resizeSection(i, w)
        # Never elide cell text — show full values (or clip them at the
        # cell boundary if they genuinely don't fit).
        table.setTextElideMode(Qt.ElideNone)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        # Populate.
        table.setRowCount(len(SUSPICIOUS_ROWS))
        for i, r in enumerate(SUSPICIOUS_ROWS):
            cells = [
                r.time_short,
                r.source,
                r.destination,
                r.interval,
                r.jitter,
                f"{r.confidence}%",
            ]
            for j, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setToolTip(f"{r.source} → {r.destination} ({r.interval}, {r.jitter})")
                table.setItem(i, j, item)
            # Severity pill.
            sev = QLabel(r.severity)
            sev.setObjectName({  # map level -> object name
                "High":   "SevHigh",
                "Medium": "SevMedium",
                "Low":    "SevLow",
            }[r.severity])
            sev.setAlignment(Qt.AlignCenter)
            table.setCellWidget(i, 6, sev)
            # Status with colored dot.
            status_widget = QWidget()
            sl = QHBoxLayout(status_widget)
            sl.setContentsMargins(0, 0, 0, 0)
            sl.setSpacing(6)
            dot_color = styles.THEME.active_dot if r.status == "Active" else styles.THEME.resolved_dot
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{dot_color}; font-size:10pt;")
            sl.addWidget(dot)
            status_lbl = QLabel(r.status)
            status_lbl.setObjectName(
                "StatusActive" if r.status == "Active" else "StatusResolved"
            )
            sl.addWidget(status_lbl, 1)
            table.setCellWidget(i, 7, status_widget)
        # Let the table expand to fill the card.
        table.setMinimumHeight(36 + 28 * len(SUSPICIOUS_ROWS) + 2)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return table

    def _make_event_row(self, ev, compact: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        dot_color = _EVENT_DOT_COLOR.get(ev.color, styles.THEME.green)
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{dot_color}; font-size:11pt; padding-top:1px;")
        dot.setFixedWidth(12)
        row.addWidget(dot)
        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        if compact:
            # Compact mode: title only, no detail line, smaller font.
            title = QLabel(ev.title)
            title.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:8.5pt; font-weight:600;"
            )
            text_col.addWidget(title)
            detail = QLabel(ev.detail)
            detail.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:7.5pt;"
            )
            text_col.addWidget(detail)
        else:
            title = QLabel(ev.title)
            title.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9.5pt; font-weight:600;"
            )
            text_col.addWidget(title)
            detail = QLabel(ev.detail)
            detail.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:8.5pt;"
            )
            text_col.addWidget(detail)
        row.addLayout(text_col, 1)
        if not compact:
            time_lbl = QLabel(ev.time)
            time_lbl.setStyleSheet(
                f"color:{styles.THEME.text_muted}; font-size:8.5pt; padding-top:2px;"
            )
            row.addWidget(time_lbl)
        return row
