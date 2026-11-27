"""UI package — BeaconHunt PySide6 widgets (redesigned dark SOC dashboard)."""
from .main_window import MainWindow, HeaderBar
from .sidebar import Sidebar, NAV_ITEMS
from .dashboard import OverviewPage
from .investigation import InvestigationPage
from .live_traffic import LiveTrafficPage
from .beacon_analysis import BeaconAnalysisPage
from .alerts import AlertsPage
from .reports import ReportsPage
from . import styles
from .styles import QSS

__all__ = [
    "MainWindow",
    "HeaderBar",
    "Sidebar",
    "NAV_ITEMS",
    "OverviewPage",
    "InvestigationPage",
    "LiveTrafficPage",
    "BeaconAnalysisPage",
    "AlertsPage",
    "ReportsPage",
    "styles",
    "QSS",
]
