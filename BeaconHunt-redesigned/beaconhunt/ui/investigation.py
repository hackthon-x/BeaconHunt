"""Beacon Investigation page — matches the bottom view of the reference.

Layout (left to right):

  * Breadcrumb row: Live Traffic › Beacon Investigation.
  * Page title block.
  * Three columns:
      - Left (~62%):
          * "Beacon Timing Analysis" lollipop chart card (full width).
          * Row containing "Alert Queue" table (~70%) + "Beacon Frequency"
            donut card (~30%).
      - Middle (~20%):
          * "Beacon Pattern Details" key-value list card.
          * "Jittery" card with ±4s label + green jitter chart.
      - Right (~18%):
          * "Beacon Summary" stat rows card.
          * "Related Hosts" card with green user icons.
          * "Evidence" card with outline-document icons + chevrons.

All data comes from :mod:`beaconhunt.ui.mock_data`.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import styles
from .mock_data import (
    BEACON_SUMMARY, EVIDENCE_ROWS, PATTERN, RELATED_HOSTS, SUSPICIOUS_ROWS,
)
from .widgets import DonutGauge, JitterChart, TimingChart


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


class InvestigationPage(QWidget):
    """The redesigned Beacon Investigation page."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Content")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(14)

        # --- Breadcrumb ---
        crumb = QHBoxLayout()
        crumb.setSpacing(6)
        c1 = QLabel("Live Traffic")
        c1.setObjectName("Breadcrumb")
        crumb.addWidget(c1)
        sep = QLabel("›")
        sep.setObjectName("Breadcrumb")
        crumb.addWidget(sep)
        c2 = QLabel("Beacon Investigation")
        c2.setObjectName("BreadcrumbCurrent")
        crumb.addWidget(c2)
        crumb.addStretch()
        outer.addLayout(crumb)

        # --- Title ---
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Beacon Investigation")
        title.setObjectName("PageTitle")
        title_block.addWidget(title)
        sub = QLabel("Analyze periodic connections and validate beaconing behavior.")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(sub)
        outer.addLayout(title_block)

        # --- 3-column grid ---
        grid = QHBoxLayout()
        grid.setSpacing(14)

        # === LEFT column ===
        left = QVBoxLayout()
        left.setSpacing(14)

        # Timing analysis chart.
        timing_card = _Card("Beacon Timing Analysis", "")
        # Legend row.
        legend = QHBoxLayout()
        legend.addStretch()
        leg_conn = QLabel("● Connection")
        leg_conn.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:8.5pt; font-weight:600; padding-right:14px;"
        )
        legend.addWidget(leg_conn)
        leg_exp = QLabel("-- Expected")
        leg_exp.setStyleSheet(
            f"color:{styles.THEME.text_muted}; font-size:8.5pt; font-weight:600;"
        )
        legend.addWidget(leg_exp)
        timing_card.body.addLayout(legend)
        self.timing_chart = TimingChart()
        self.timing_chart.setFixedHeight(200)
        timing_card.body.addWidget(self.timing_chart)
        left.addWidget(timing_card)

        # Row: Alert Queue + Beacon Frequency.
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)

        # Alert Queue table.
        aq = _Card("Alert Queue", "")
        aq.setMinimumWidth(720)
        aq.body.addWidget(self._build_alert_table())
        bottom_row.addWidget(aq, 78)

        # Beacon Frequency donut.
        bf = _Card("Beacon Frequency", "")
        bf.setMinimumWidth(180)
        bf_row = QHBoxLayout()
        bf_row.addStretch()
        self.freq_donut = DonutGauge(
            value=75.0,
            label="300s",
            caption="Detected Interval",
            ring_color=styles.THEME.green,
            size=120,
        )
        bf_row.addWidget(self.freq_donut)
        bf_row.addStretch()
        bf.body.addLayout(bf_row)
        from .mock_data import _gen_confidence_sparkline
        spark = Sparkline(_gen_confidence_sparkline(),
                          color=styles.THEME.green, height=24)
        bf.body.addWidget(spark)
        bottom_row.addWidget(bf, 25)

        left.addLayout(bottom_row)
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setMinimumWidth(880)
        grid.addWidget(left_widget, 68)

        # === MIDDLE column ===
        middle = QVBoxLayout()
        middle.setSpacing(14)

        # Pattern details.
        pd = _Card("Beacon Pattern Details", "")
        for k, v in [
            ("Source", PATTERN.source),
            ("Destination", PATTERN.destination),
            ("Interval", PATTERN.interval),
            ("Jitter", PATTERN.jitter),
            ("First Seen", PATTERN.first_seen),
            ("Last Seen", PATTERN.last_seen),
            ("Confidence", f"{PATTERN.confidence}%"),
        ]:
            row = QHBoxLayout()
            key_lbl = QLabel(k)
            key_lbl.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:500;"
            )
            row.addWidget(key_lbl)
            row.addStretch()
            val_lbl = QLabel(v)
            val_lbl.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9.5pt; font-weight:600;"
            )
            row.addWidget(val_lbl)
            pd.body.addLayout(row)
        # Severity row with badge.
        sev_row = QHBoxLayout()
        sev_key = QLabel("Severity")
        sev_key.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:500;"
        )
        sev_row.addWidget(sev_key)
        sev_row.addStretch()
        sev_badge = QLabel(PATTERN.severity)
        sev_badge.setObjectName({
            "High":   "SevHigh",
            "Medium": "SevMedium",
            "Low":    "SevLow",
        }[PATTERN.severity])
        sev_badge.setAlignment(Qt.AlignCenter)
        sev_row.addWidget(sev_badge)
        pd.body.addLayout(sev_row)
        middle.addWidget(pd)

        # Jitter panel.
        jp = _Card("Jittery", "")
        big = QLabel("±4s")
        big.setStyleSheet(
            f"color:{styles.THEME.text_primary}; font-size:18pt; font-weight:800; padding:6px 0;"
        )
        jp.body.addWidget(big)
        jitter_label = QLabel("Jitter")
        jitter_label.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:8.5pt; font-weight:600; padding-bottom:4px;"
        )
        jp.body.addWidget(jitter_label)
        self.jitter_chart = JitterChart()
        self.jitter_chart.setFixedHeight(90)
        jp.body.addWidget(self.jitter_chart)
        middle.addWidget(jp)

        middle_widget = QWidget()
        middle_widget.setLayout(middle)
        middle_widget.setMinimumWidth(260)
        grid.addWidget(middle_widget, 18)

        # === RIGHT column ===
        right = QVBoxLayout()
        right.setSpacing(14)

        # Beacon summary.
        bs = _Card("Beacon Summary", "")
        for label, value in BEACON_SUMMARY:
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:500;"
            )
            row.addWidget(l)
            row.addStretch()
            v = QLabel(value)
            v.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:10pt; font-weight:700;"
            )
            row.addWidget(v)
            bs.body.addLayout(row)
        right.addWidget(bs)

        # Related hosts.
        rh = _Card("Related Hosts", "")
        for h in RELATED_HOSTS:
            row = QHBoxLayout()
            row.setSpacing(10)
            icon = QLabel("👤")
            icon.setStyleSheet(
                f"background:{styles.THEME.green_tint}; color:{styles.THEME.green}; "
                f"border-radius:8px; padding:2px 4px; font-size:11pt; "
                f"min-width:24px; min-height:24px;"
            )
            icon.setAlignment(Qt.AlignCenter)
            icon.setFixedSize(28, 28)
            row.addWidget(icon)
            label_col = QVBoxLayout()
            label_col.setSpacing(0)
            ip_lbl = QLabel(h.ip)
            ip_lbl.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9.5pt; font-weight:600;"
            )
            label_col.addWidget(ip_lbl)
            role_lbl = QLabel(f"({h.role})")
            role_lbl.setStyleSheet(
                f"color:{styles.THEME.text_muted}; font-size:8pt;"
            )
            label_col.addWidget(role_lbl)
            row.addLayout(label_col, 1)
            chev = QLabel("›")
            chev.setStyleSheet(
                f"color:{styles.THEME.text_muted}; font-size:14pt; font-weight:600;"
            )
            row.addWidget(chev)
            rh.body.addLayout(row)
        right.addWidget(rh)

        # Evidence.
        ev = _Card("Evidence", "")
        for e in EVIDENCE_ROWS:
            row = QHBoxLayout()
            row.setSpacing(10)
            icon = QLabel(e.icon)
            icon.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:12pt; "
                f"min-width:22px;"
            )
            icon.setAlignment(Qt.AlignCenter)
            row.addWidget(icon)
            label_col = QVBoxLayout()
            label_col.setSpacing(0)
            l1 = QLabel(e.label)
            l1.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9.5pt; font-weight:600;"
            )
            label_col.addWidget(l1)
            l2 = QLabel(e.detail)
            l2.setStyleSheet(
                f"color:{styles.THEME.text_muted}; font-size:8pt;"
            )
            label_col.addWidget(l2)
            row.addLayout(label_col, 1)
            chev = QLabel("›")
            chev.setStyleSheet(
                f"color:{styles.THEME.text_muted}; font-size:14pt; font-weight:600;"
            )
            row.addWidget(chev)
            ev.body.addLayout(row)
        right.addWidget(ev)

        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setMinimumWidth(240)
        grid.addWidget(right_widget, 14)

        outer.addLayout(grid, 1)

    # ------------------------------------------------------------------ helpers
    def _build_alert_table(self) -> QTableWidget:
        cols = ["Time (UTC)", "Source", "Destination", "Int.",
                "Conf.", "Severity", "Status"]
        table = QTableWidget()
        table.setColumnCount(len(cols))
        table.setHorizontalHeaderLabels(cols)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setHighlightSections(False)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        table.horizontalHeader().setStretchLastSection(False)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        modes = [
            QHeaderView.Stretch,
            QHeaderView.Interactive,
            QHeaderView.Stretch,
            QHeaderView.Interactive,
            QHeaderView.Interactive,
            QHeaderView.Interactive,
            QHeaderView.Interactive,
        ]
        for i, m in enumerate(modes):
            table.horizontalHeader().setSectionResizeMode(i, m)
        # Explicit widths for the Interactive columns.
        explicit_widths = {1: 95, 3: 55, 4: 60, 5: 90, 6: 110}
        for i, w in explicit_widths.items():
            table.horizontalHeader().resizeSection(i, w)
        # Never elide cell text — show full values.
        table.setTextElideMode(Qt.ElideNone)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setRowCount(len(SUSPICIOUS_ROWS))
        for i, r in enumerate(SUSPICIOUS_ROWS):
            cells = [
                r.time_short,
                r.source,
                r.destination,
                r.interval,
                f"{r.confidence}%",
            ]
            for j, text in enumerate(cells):
                item = QTableWidgetItem(text)
                table.setItem(i, j, item)
            # Severity pill.
            sev = QLabel(r.severity)
            sev.setObjectName({
                "High":   "SevHigh",
                "Medium": "SevMedium",
                "Low":    "SevLow",
            }[r.severity])
            sev.setAlignment(Qt.AlignCenter)
            table.setCellWidget(i, 5, sev)
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
            table.setCellWidget(i, 6, status_widget)
        # Let the table expand to fill the card vertically.
        table.setMinimumHeight(36 + 28 * len(SUSPICIOUS_ROWS) + 2)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return table


# Late import so Sparkline is available.
from .widgets import Sparkline  # noqa: E402
