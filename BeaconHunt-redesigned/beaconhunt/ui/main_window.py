"""BeaconHunt main window — header bar + sidebar + stacked content.

Layout:
  * Top header bar (full width, ~58 px): logo glyph + "BEACONHUNT" wordmark,
    "LAB ENVIRONMENT" pill, green "MONITORING" indicator, mini cyan traffic
    sparkline, then two stat blocks ("Network Traffic 12.4 MB/s" and
    "Events (1m) 8,742") separated by a vertical divider.
  * Below the header: dark sidebar (left, fixed 210 px) + content stack
    (right).

Pages in the stack:
  0 = Network Activity Overview (dashboard.OverviewPage)
  1 = Beacon Investigation (investigation.InvestigationPage)
  2..4 = simple placeholders for Live Traffic / Alerts / Reports /
         Beacon Analysis so the sidebar nav works end-to-end.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QMenu,
    QMessageBox, QSizePolicy, QStackedWidget, QStatusBar, QToolButton,
    QVBoxLayout, QWidget,
)

from . import styles
from .dashboard import OverviewPage
from .investigation import InvestigationPage
from .live_traffic import LiveTrafficPage
from .beacon_analysis import BeaconAnalysisPage
from .alerts import AlertsPage
from .reports import ReportsPage
from .sidebar import Sidebar
from .widgets import Sparkline
from .mock_data import (
    HEADER_EVENTS_PER_MIN, HEADER_NETWORK_TRAFFIC, _gen_header_sparkline,
    open_alerts_count,
)


__version__ = "2.0.0"


class HeaderBar(QFrame):
    """Top application header with logo, monitoring status, and live stats."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(58)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(14)

        # Logo block: ring glyph + wordmark.
        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)
        self.logo_glyph = QLabel("◎")
        self.logo_glyph.setObjectName("HeaderLogoGlyph")
        logo_row.addWidget(self.logo_glyph)
        self.logo_text = QLabel("BEACONHUNT")
        self.logo_text.setObjectName("HeaderLogo")
        logo_row.addWidget(self.logo_text)
        lay.addLayout(logo_row)

        # LAB ENVIRONMENT pill.
        self.pill_lab = QLabel("LAB ENVIRONMENT")
        self.pill_lab.setObjectName("PillLabEnv")
        lay.addWidget(self.pill_lab)

        # Spacer to push the monitoring indicator right.
        lay.addStretch(10)

        # Monitoring indicator: green dot + label.
        self.mon_dot = QLabel("●")
        self.mon_dot.setStyleSheet(
            f"color:{styles.THEME.green}; font-size:11pt; padding-top:1px;"
        )
        lay.addWidget(self.mon_dot)
        self.mon_lbl = QLabel("MONITORING")
        self.mon_lbl.setObjectName("MonitoringLabel")
        lay.addWidget(self.mon_lbl)

        lay.addStretch(20)

        # Header sparkline (mini cyan traffic).
        self.spark = Sparkline(_gen_header_sparkline(),
                               color=styles.THEME.cyan,
                               height=30)
        self.spark.setFixedWidth(110)
        lay.addWidget(self.spark)

        # Stat block 1: Network Traffic.
        stat1 = QVBoxLayout()
        stat1.setSpacing(0)
        s1_label = QLabel("Network Traffic")
        s1_label.setObjectName("HeaderStatLabel")
        stat1.addWidget(s1_label)
        s1_value = QLabel(HEADER_NETWORK_TRAFFIC)
        s1_value.setObjectName("HeaderStatValue")
        stat1.addWidget(s1_value)
        lay.addLayout(stat1)

        # Vertical divider.
        divider = QFrame()
        divider.setObjectName("HeaderStatDivider")
        divider.setFixedHeight(28)
        divider.setFixedWidth(1)
        lay.addWidget(divider)

        # Stat block 2: Events (1m).
        stat2 = QVBoxLayout()
        stat2.setSpacing(0)
        s2_label = QLabel("Events (1m)")
        s2_label.setObjectName("HeaderStatLabel")
        stat2.addWidget(s2_label)
        s2_value = QLabel(HEADER_EVENTS_PER_MIN)
        s2_value.setObjectName("HeaderStatValue")
        stat2.addWidget(s2_value)
        lay.addLayout(stat2)


class MainWindow(QMainWindow):
    """Top-level window: header + sidebar + stacked pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"BeaconHunt v{__version__}")
        self.resize(1600, 1000)
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(styles.QSS)
        self.setAcceptDrops(True)

        # Central widget: vertical header + horizontal (sidebar + stack).
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header = HeaderBar()
        root.addWidget(self.header)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._on_page_changed)
        body.addWidget(self.sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("Content")
        body.addWidget(self._stack, 1)
        root.addLayout(body)

        # Pages.
        self._overview = OverviewPage()
        self._stack.addWidget(self._overview)

        self._investigation = InvestigationPage()
        self._stack.addWidget(self._investigation)

        # Live Traffic — animated page with rolling chart + live events.
        self._live_traffic = LiveTrafficPage()
        self._stack.addWidget(self._live_traffic)

        # Beacon Analysis — cross-destination comparison view.
        self._beacon_analysis = BeaconAnalysisPage()
        self._stack.addWidget(self._beacon_analysis)

        # Alerts — consolidated alert queue with Acknowledge/Resolve.
        self._alerts = AlertsPage()
        self._alerts.alerts_changed.connect(self._on_alerts_changed)
        self._stack.addWidget(self._alerts)

        # Reports — generated report library with export/delete actions.
        self._reports = ReportsPage()
        self._stack.addWidget(self._reports)

        self.setCentralWidget(central)

        # Status bar.
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(
            f"BeaconHunt v{__version__}  ·  passive · offline  ·  "
            f"LAB ENVIRONMENT  ·  MONITORING"
        )

        # Initial page = overview.
        self._go_to_page("overview")
        self.sidebar.set_active("overview")

    # ------------------------------------------------------------------ helpers
    def _make_placeholder(self, title: str, body: str) -> QWidget:
        page = QWidget()
        page.setObjectName("Content")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(12)
        t = QLabel(title)
        t.setObjectName("PageTitle")
        lay.addWidget(t)
        b = QLabel(body)
        b.setObjectName("PageSubtitle"
                        if False else "Muted")  # use Muted style (gray)
        b.setWordWrap(True)
        lay.addWidget(b)
        lay.addStretch()
        return page

    def _go_to_page(self, key: str) -> None:
        idx = {
            "overview": 0,
            "investigation": 1,
            "live": 2,
            "beacon": 3,
            "alerts": 4,
            "reports": 5,
        }.get(key, 0)
        # Map sidebar keys to the right page. The sidebar uses
        # "overview", "live", "beacon", "alerts", "reports". We also expose
        # "investigation" internally.
        # Start/stop the live-traffic timer so it only runs when visible.
        if key == "live":
            self._live_traffic.start()
        else:
            self._live_traffic.stop()
        self._stack.setCurrentIndex(idx)
        self.sidebar.set_active(key)

    def _on_page_changed(self, key: str) -> None:
        self._go_to_page(key)

    def _on_alerts_changed(self) -> None:
        """The Alerts page updated an alert's status — refresh the badge."""
        try:
            self.sidebar.set_alerts_badge(self._alerts.open_count())
        except Exception:
            pass

    # ------------------------------------------------------------ drag-drop
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        # Kept for back-compat with the original app; in the redesign it
        # just acknowledges the drop.
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path:
                self.statusBar().showMessage(f"File dropped: {path}")

    # ------------------------------------------------------------ close
    def closeEvent(self, event) -> None:
        # Stop the live-traffic timer so it doesn't keep firing after the
        # window is closed.
        try:
            self._live_traffic.stop()
        except Exception:
            pass
        event.accept()
