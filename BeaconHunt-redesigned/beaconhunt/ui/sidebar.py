"""Left navigation sidebar — matches the reference BEACONHUNT dashboard.

Layout:
  * Logo block: ring/target glyph + "BEACONHUNT" wordmark.
  * Vertical nav list: Overview, Live Traffic, Beacon Analysis,
    Alerts (with green "7" badge), Reports.
  * Bottom-pinned "Threat Hunting" promo card with a shield glyph.
  * Footer block: avatar + "Analyst" + "LAB ENVIRONMENT".

Nav rows are custom ``_NavRow`` widgets (a clickable QFrame) so the
label and optional badge render with predictable widths — using a
QHBoxLayout inside a QPushButton was clipping the text in some Qt
themes.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget,
)

from . import styles


# (key, glyph, label, badge_text_or_None)
NAV_ITEMS = [
    ("overview", "⌂", "Overview",        None),
    ("live",     "📡", "Live Traffic",    None),
    ("beacon",   "◎", "Beacon Analysis", None),
    ("alerts",   "⚑", "Alerts",          "7"),
    ("reports",  "▤", "Reports",         None),
]


class _NavRow(QFrame):
    """A single nav item: glyph + label + optional badge.

    Behaves like a checkable button — emits ``clicked`` on mouse release,
    tracks ``checked`` state, and paints the active highlight via
    QSS ``QFrame#NavRow[checked="true"]``.
    """

    clicked = Signal()

    def __init__(self, glyph: str, label: str,
                 badge_text: Optional[str] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("NavRow")
        self._checked = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Apply QSS via dynamic property.
        self.setProperty("checked", False)
        # Set attribute so QSS [checked="true"] selector works after repolish.
        self.setAttribute(Qt.WA_StyledBackground, True)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 14, 0)
        lay.setSpacing(10)

        self.glyph_lbl = QLabel(glyph)
        self.glyph_lbl.setStyleSheet(
            f"color:{styles.THEME.cyan}; font-size:13pt; padding:0; "
            f"background:transparent; border:none;"
        )
        self.glyph_lbl.setFixedWidth(20)
        self.glyph_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.glyph_lbl)

        self.label_lbl = QLabel(label)
        self.label_lbl.setStyleSheet(
            f"color:{styles.THEME.sidebar_text}; font-size:10pt; font-weight:500; "
            f"padding:0; background:transparent; border:none;"
        )
        lay.addWidget(self.label_lbl, 1)

        if badge_text:
            self.badge = QLabel(badge_text)
            self.badge.setStyleSheet(
                f"background:{styles.THEME.green}; color:#061A0E; "
                f"border-radius:9px; padding:1px 8px; font-size:8pt; "
                f"font-weight:800; min-width:14px;"
            )
            self.badge.setAlignment(Qt.AlignCenter)
            lay.addWidget(self.badge)
        else:
            self.badge = None

    # --- checkable behavior ---
    def setChecked(self, checked: bool) -> None:
        self._checked = checked
        self.setProperty("checked", "true" if checked else "false")
        # Refresh QSS by re-polishing unpolish/polish.
        self.style().unpolish(self)
        self.style().polish(self)
        if checked:
            self.label_lbl.setStyleSheet(
                f"color:{styles.THEME.sidebar_text_active}; font-size:10pt; "
                f"font-weight:700; padding:0; background:transparent; border:none;"
            )
        else:
            self.label_lbl.setStyleSheet(
                f"color:{styles.THEME.sidebar_text}; font-size:10pt; "
                f"font-weight:500; padding:0; background:transparent; border:none;"
            )

    def isChecked(self) -> bool:
        return self._checked

    # --- mouse handling ---
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.setProperty("checked", "true")
            self.style().polish(self)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class Sidebar(QFrame):
    """Fixed-width dark navigation panel."""

    page_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Logo block ---
        logo_block = QVBoxLayout()
        logo_block.setContentsMargins(20, 22, 20, 4)
        logo_block.setSpacing(2)
        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.setSpacing(10)
        self.logo_glyph = QLabel("◎")
        self.logo_glyph.setObjectName("SidebarLogoGlyph")
        logo_row.addWidget(self.logo_glyph)
        self.logo_text = QLabel("BEACONHUNT")
        self.logo_text.setObjectName("SidebarLogo")
        logo_row.addWidget(self.logo_text)
        logo_row.addStretch()
        logo_block.addLayout(logo_row)
        layout.addLayout(logo_block)

        layout.addSpacing(20)

        # --- Nav buttons ---
        self._rows: dict = {}
        for key, glyph, label, badge in NAV_ITEMS:
            row = _NavRow(glyph, label, badge)
            row.clicked.connect(lambda _checked=False, k=key: self._on_clicked(k))
            self._rows[key] = row
            layout.addWidget(row)

        layout.addStretch()

        # --- Threat Hunting promo card ---
        promo = QFrame()
        promo.setObjectName("ThreatHuntCard")
        promo_lay = QVBoxLayout(promo)
        promo_lay.setContentsMargins(14, 14, 14, 14)
        promo_lay.setSpacing(6)
        promo_head = QHBoxLayout()
        promo_head.setSpacing(8)
        self.promo_glyph = QLabel("🛡")
        self.promo_glyph.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:14pt; padding:0;"
        )
        promo_head.addWidget(self.promo_glyph)
        self.promo_title = QLabel("Threat Hunting")
        self.promo_title.setObjectName("ThreatHuntTitle")
        promo_head.addWidget(self.promo_title)
        promo_head.addStretch()
        promo_lay.addLayout(promo_head)
        self.promo_sub = QLabel(
            "Spotting C2-style beaconing in network traffic."
        )
        self.promo_sub.setObjectName("ThreatHuntSub")
        self.promo_sub.setWordWrap(True)
        promo_lay.addWidget(self.promo_sub)
        layout.addWidget(promo)

        layout.addSpacing(10)

        # --- Footer (Analyst / LAB ENVIRONMENT) ---
        footer = QFrame()
        footer_lay = QVBoxLayout(footer)
        footer_lay.setContentsMargins(20, 8, 20, 14)
        footer_lay.setSpacing(4)
        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(8)
        self.avatar = QLabel("●")
        self.avatar.setStyleSheet(
            f"background:{styles.THEME.green}; color:#061A0E; "
            f"border-radius:12px; padding:4px 7px; font-weight:800; "
            f"min-width:24px; min-height:24px;"
        )
        self.avatar.setAlignment(Qt.AlignCenter)
        avatar_row.addWidget(self.avatar)
        self.who = QLabel("Analyst")
        self.who.setObjectName("SidebarFooterUser")
        avatar_row.addWidget(self.who)
        avatar_row.addStretch()
        footer_lay.addLayout(avatar_row)
        self.env = QLabel("LAB ENVIRONMENT")
        self.env.setObjectName("SidebarFooterEnv")
        footer_lay.addWidget(self.env)
        layout.addWidget(footer)

    # ------------------------------------------------------------------ nav
    def _on_clicked(self, key: str) -> None:
        self.set_active(key)
        self.page_changed.emit(key)

    def set_active(self, key: str) -> None:
        for k, row in self._rows.items():
            row.setChecked(k == key)

    def set_alerts_badge(self, count: int) -> None:
        """Update the green count badge on the Alerts nav row.

        Pass ``count=0`` to hide the badge entirely (no open alerts).
        """
        row = self._rows.get("alerts")
        if row is None or row.badge is None:
            return
        if count <= 0:
            row.badge.setVisible(False)
        else:
            row.badge.setVisible(True)
            row.badge.setText(str(count))

    # Back-compat hooks (no-ops in the single-theme redesign).
    def set_theme(self, name: str) -> None:
        pass
