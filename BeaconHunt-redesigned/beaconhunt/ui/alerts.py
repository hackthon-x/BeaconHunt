"""Alerts page — consolidated alert queue with interactive status updates.

Layout:
  * Page title + subtitle.
  * Filter tab bar: All / Open / Acknowledged / Resolved. Each tab shows
    its count and updates the alert list when clicked.
  * Four stat cards: Total Alerts, Critical (High), Avg Response, Open
    Rate.
  * Two-column body:
      - Left (wider): Alert Queue — a vertical list of alert cards.
        Each card shows severity pill, title, source → destination
        with interval, timestamp + age, status pill, and Acknowledge /
        Resolve action buttons (which actually update the alert status
        and refresh the list + stats).
      - Right: Priority Breakdown card (visual bars for High/Medium/Low
        counts) and a Recent Activity log card.

All data comes from ``beaconhunt.ui.mock_data.ALERTS`` (a list of
dicts so the page can mutate status at runtime).
"""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStackedWidget,
    QVBoxLayout, QWidget,
)

from . import styles
from .mock_data import ALERTS, open_alerts_count


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

    def set_value(self, value: str) -> None:
        self.value_lbl.setText(value)


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


# ---- Filter tab -----------------------------------------------------------

class _FilterTab(QPushButton):
    """A single filter tab button (All / Open / Acknowledged / Resolved)."""

    def __init__(self, label: str, count: int,
                 parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setObjectName("FilterTab")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self._label = label
        self._count = count
        self._refresh()
        self.setMinimumHeight(34)

    def set_count(self, count: int) -> None:
        self._count = count
        self._refresh()

    def _refresh(self) -> None:
        self.setText(f"{self._label}  ({self._count})")


# ---- Alert card -----------------------------------------------------------

class _AlertCard(QFrame):
    """One alert entry in the queue."""

    acknowledged = Signal(int)   # alert id
    resolved = Signal(int)       # alert id

    def __init__(self, alert: dict, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._alert = alert
        self.setObjectName("AlertCard")
        # Style as a card with a left-edge severity color stripe.
        sev = alert["severity"]
        sev_color = {
            "High":   styles.THEME.sev_high_bg,
            "Medium": styles.THEME.sev_med_bg,
            "Low":    styles.THEME.sev_low_bg,
        }[sev]
        self.setStyleSheet(
            f"QFrame#AlertCard {{"
            f"  background:{styles.THEME.card_bg};"
            f"  border: 1px solid {styles.THEME.card_border};"
            f"  border-left: 4px solid {sev_color};"
            f"  border-radius: 8px;"
            f"}}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)

        # Row 1: severity pill + title (left), timestamp + age (right).
        top = QHBoxLayout()
        top.setSpacing(10)
        sev_pill = QLabel(sev.upper())
        sev_pill.setObjectName({
            "High":   "SevHigh",
            "Medium": "SevMedium",
            "Low":    "SevLow",
        }[sev])
        sev_pill.setAlignment(Qt.AlignCenter)
        top.addWidget(sev_pill)
        title = QLabel(alert["title"])
        title.setStyleSheet(
            f"color:{styles.THEME.text_primary}; font-size:11pt; font-weight:700;"
        )
        top.addWidget(title, 1)
        ts = QLabel(f"{alert['timestamp']}  ·  {alert['age']}")
        ts.setStyleSheet(
            f"color:{styles.THEME.text_muted}; font-size:9pt;"
        )
        top.addWidget(ts)
        lay.addLayout(top)

        # Row 2: source → destination with interval.
        meta = QLabel(
            f"{alert['source']}  →  {alert['destination']}  ·  interval {alert['interval']}"
        )
        meta.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9.5pt; font-weight:500;"
        )
        lay.addWidget(meta)

        # Row 3: detail (smaller muted text).
        detail = QLabel(alert["detail"])
        detail.setStyleSheet(
            f"color:{styles.THEME.text_muted}; font-size:8.5pt;"
        )
        detail.setWordWrap(True)
        lay.addWidget(detail)

        # Row 4: status pill (left) + action buttons (right).
        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        status_pill = QLabel(alert["status"])
        status_obj = {
            "Open":          "StatusActive",
            "Acknowledged":  "AckBadge",
            "Resolved":      "StatusResolved",
        }[alert["status"]]
        status_pill.setObjectName(status_obj)
        status_pill.setAlignment(Qt.AlignCenter)
        bottom.addWidget(status_pill)
        bottom.addStretch()
        # Acknowledge button — disabled if already ack'd or resolved.
        self.btn_ack = QPushButton("Acknowledge")
        self.btn_ack.setProperty("secondary", True)
        self.btn_ack.setCursor(Qt.PointingHandCursor)
        self.btn_ack.clicked.connect(
            lambda _checked=False, aid=alert["id"]: self.acknowledged.emit(aid)
        )
        if alert["status"] != "Open":
            self.btn_ack.setEnabled(False)
        bottom.addWidget(self.btn_ack)
        # Resolve button — disabled if already resolved.
        self.btn_res = QPushButton("Resolve")
        self.btn_res.setProperty("outline", True)
        self.btn_res.setCursor(Qt.PointingHandCursor)
        self.btn_res.clicked.connect(
            lambda _checked=False, aid=alert["id"]: self.resolved.emit(aid)
        )
        if alert["status"] == "Resolved":
            self.btn_res.setEnabled(False)
        bottom.addWidget(self.btn_res)
        lay.addLayout(bottom)


# ---- Alerts page ----------------------------------------------------------

# Acknowledged badge style — override at runtime via stylesheet.
_ACK_BADGE_QSS = (
    f"background:#1E3A8A; color:#93C5FD; border:none; border-radius:10px; "
    f"padding:3px 10px; font-size:8.5pt; font-weight:700; letter-spacing:0.5px;"
)


class AlertsPage(QWidget):
    """Consolidated alert queue with interactive Acknowledge/Resolve."""

    # Emitted when an alert's status changes — the main window can use
    # this to update the sidebar badge count.
    alerts_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Content")
        self._filter = "All"
        # Take a shallow copy so we can mutate status without touching the
        # module-level list (keeps the page self-contained).
        self._alerts: List[dict] = [dict(a) for a in ALERTS]

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(14)

        # --- Title ---
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Alerts")
        title.setObjectName("PageTitle")
        title_block.addWidget(title)
        sub = QLabel("Consolidated alert queue across the last 24 hours.")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(sub)
        outer.addLayout(title_block)

        # --- Filter tab bar ---
        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(8)
        self.tabs: dict = {}
        for key, label in [("All", "All"), ("Open", "Open"),
                           ("Acknowledged", "Acknowledged"),
                           ("Resolved", "Resolved")]:
            tab = _FilterTab(label, 0)
            tab.clicked.connect(lambda _checked=False, k=key: self._set_filter(k))
            self.tabs[key] = tab
            tabs_row.addWidget(tab)
        tabs_row.addStretch()
        outer.addLayout(tabs_row)

        # --- Stat cards row ---
        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        self.card_total = _StatCard(
            "TOTAL ALERTS", "0", "Across last 24h",
            color=styles.THEME.cyan,
        )
        self.card_critical = _StatCard(
            "CRITICAL", "0", "High severity",
            color=styles.THEME.sev_high_fg,
        )
        self.card_response = _StatCard(
            "AVG RESPONSE", "—", "Mean acknowledge time",
        )
        self.card_open_rate = _StatCard(
            "OPEN RATE", "0%", "Open / total",
            color=styles.THEME.sev_med_fg,
        )
        for c in (self.card_total, self.card_critical,
                  self.card_response, self.card_open_rate):
            stat_row.addWidget(c, 1)
        outer.addLayout(stat_row)

        # --- Body: alert queue (left) + sidebar (right) ---
        body = QHBoxLayout()
        body.setSpacing(14)

        # Left: alert queue in a scrollable card.
        queue_card = _Card("Alert Queue",
                           "Click Acknowledge or Resolve to update status")
        # Scroll area for the alert cards.
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea {{ background:transparent; border:none; }}"
            f"QScrollBar:vertical {{ background:transparent; width:8px; }}"
        )
        self._queue_container = QWidget()
        self._queue_lay = QVBoxLayout(self._queue_container)
        self._queue_lay.setContentsMargins(0, 0, 8, 0)
        self._queue_lay.setSpacing(10)
        self._queue_lay.addStretch()
        scroll.setWidget(self._queue_container)
        queue_card.body.addWidget(scroll)
        body.addWidget(queue_card, 68)

        # Right: priority breakdown + recent activity.
        right = QVBoxLayout()
        right.setSpacing(14)

        # Priority breakdown card.
        prio_card = _Card("Priority Breakdown",
                          "Open alerts by severity")
        self._prio_bars = {}
        for sev, color in [("High", styles.THEME.sev_high_bg),
                            ("Medium", styles.THEME.sev_med_bg),
                            ("Low", styles.THEME.sev_low_bg)]:
            row = QVBoxLayout()
            row.setSpacing(4)
            top = QHBoxLayout()
            lbl = QLabel(sev)
            lbl.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9.5pt; font-weight:600;"
            )
            top.addWidget(lbl)
            top.addStretch()
            count_lbl = QLabel("0")
            count_lbl.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:600;"
            )
            top.addWidget(count_lbl)
            row.addLayout(top)
            # Progress bar mimic: fill + track using QFrame stretch.
            bar_wrap = QWidget()
            bar_wrap.setFixedHeight(6)
            bar_lay = QHBoxLayout(bar_wrap)
            bar_lay.setContentsMargins(0, 0, 0, 0)
            bar_lay.setSpacing(0)
            fill = QFrame()
            fill.setStyleSheet(
                f"background:{color}; border-radius:3px;"
            )
            fill.setFixedHeight(6)
            track = QFrame()
            track.setStyleSheet(
                f"background:{styles.THEME.progress_track}; border-radius:3px;"
            )
            track.setFixedHeight(6)
            bar_lay.addWidget(fill, 0)
            bar_lay.addWidget(track, 100)
            row.addWidget(bar_wrap)
            prio_card.body.addLayout(row)
            self._prio_bars[sev] = (count_lbl, fill, track)
        right.addWidget(prio_card)

        # Recent activity card.
        act_card = _Card("Recent Activity",
                         "Latest status changes")
        for entry in self._recent_activity_entries():
            row = QHBoxLayout()
            row.setSpacing(8)
            dot_color = {
                "Open":      styles.THEME.sev_med_bg,
                "Resolved":  styles.THEME.green,
                "Acknowledged": styles.THEME.cyan,
            }.get(entry["action"], styles.THEME.text_muted)
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{dot_color}; font-size:9pt; padding-top:1px;")
            dot.setFixedWidth(10)
            row.addWidget(dot)
            text = QLabel(entry["text"])
            text.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9pt; font-weight:500;"
            )
            row.addWidget(text, 1)
            ts = QLabel(entry["time"])
            ts.setStyleSheet(
                f"color:{styles.THEME.text_muted}; font-size:8pt;"
            )
            row.addWidget(ts)
            act_card.body.addLayout(row)
        right.addWidget(act_card)

        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setMinimumWidth(260)
        body.addWidget(right_widget, 32)

        outer.addLayout(body, 1)

        # Apply the Acknowledged badge stylesheet globally to this page.
        self.setStyleSheet(self.styleSheet() + f"\nQLabel#AckBadge {{ {_ACK_BADGE_QSS} }}")

        # Initial population.
        self._set_filter("All")

    # ------------------------------------------------------------------ helpers
    def open_count(self) -> int:
        """Return the current number of Open alerts (after user actions)."""
        return sum(1 for a in self._alerts if a["status"] == "Open")

    def _recent_activity_entries(self) -> List[dict]:
        """Build a short recent-activity feed from the alerts list."""
        # Sort by timestamp descending and take the top 6.
        sorted_alerts = sorted(self._alerts,
                               key=lambda a: a["timestamp"], reverse=True)[:6]
        return [
            {
                "action": a["status"],
                "text": f"#{a['id']}  {a['title'][:40]}",
                "time":  a["timestamp"],
            }
            for a in sorted_alerts
        ]

    def _set_filter(self, key: str) -> None:
        self._filter = key
        for k, tab in self.tabs.items():
            tab.setChecked(k == key)
        self._refresh()

    def _counts(self) -> dict:
        return {
            "All": len(self._alerts),
            "Open": sum(1 for a in self._alerts if a["status"] == "Open"),
            "Acknowledged": sum(1 for a in self._alerts if a["status"] == "Acknowledged"),
            "Resolved": sum(1 for a in self._alerts if a["status"] == "Resolved"),
        }

    def _refresh(self) -> None:
        counts = self._counts()
        # Update tab counts.
        for k, tab in self.tabs.items():
            tab.set_count(counts[k])
        # Update stat cards.
        self.card_total.set_value(str(counts["All"]))
        self.card_critical.set_value(
            str(sum(1 for a in self._alerts
                    if a["severity"] == "High" and a["status"] != "Resolved"))
        )
        self.card_response.set_value("8m")
        open_rate = (counts["Open"] / counts["All"] * 100) if counts["All"] else 0
        self.card_open_rate.set_value(f"{open_rate:.0f}%")
        # Update priority breakdown (Open alerts by severity).
        open_alerts = [a for a in self._alerts if a["status"] == "Open"]
        max_count = max(1, len(open_alerts))
        for sev, (count_lbl, fill, track) in self._prio_bars.items():
            n = sum(1 for a in open_alerts if a["severity"] == sev)
            count_lbl.setText(str(n))
            # Update the fill/track stretch factors.
            bar_lay = fill.parent().layout()
            bar_lay.setStretchFactor(fill, n)
            bar_lay.setStretchFactor(track, max_count - n)
        # Rebuild the alert queue.
        self._rebuild_queue()

    def _rebuild_queue(self) -> None:
        # Remove all existing alert cards (keep the trailing stretch).
        while self._queue_lay.count() > 1:
            item = self._queue_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        # Filter the alerts.
        if self._filter == "All":
            visible = list(self._alerts)
        else:
            visible = [a for a in self._alerts if a["status"] == self._filter]
        # Insert new cards before the trailing stretch.
        for a in visible:
            card = _AlertCard(a)
            card.acknowledged.connect(self._on_ack)
            card.resolved.connect(self._on_resolve)
            self._queue_lay.insertWidget(self._queue_lay.count() - 1, card)

    # ------------------------------------------------------------------ actions
    def _on_ack(self, alert_id: int) -> None:
        for a in self._alerts:
            if a["id"] == alert_id and a["status"] == "Open":
                a["status"] = "Acknowledged"
                break
        self._refresh()
        self.alerts_changed.emit()

    def _on_resolve(self, alert_id: int) -> None:
        for a in self._alerts:
            if a["id"] == alert_id and a["status"] != "Resolved":
                a["status"] = "Resolved"
                break
        self._refresh()
        self.alerts_changed.emit()
