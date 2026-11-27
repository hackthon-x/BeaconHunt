"""Mock data for the redesigned BeaconHunt dashboard.

These values mirror the reference BEACONHUNT dashboard screenshot so the
redesign can be visually verified against the mockup:

  * Suspicious periodic connections table (5 rows with the exact IPs,
    intervals, jitter, confidence and severity from the reference).
  * Recent events (3 items with green/yellow/cyan dots).
  * Top beaconing destinations (3 IPs with hit counts).
  * Detection confidence: 87%.
  * Beacon investigation: source 10.0.1.23 → destination 192.0.2.10,
    interval 300 s, jitter ±4 s, 6 matches, confidence 92% High.
  * Network topology nodes: LAB-WS-01 (center), LAB-DC-01, WEB-01,
    LAB-WS-02, DB-01, INTERNET.

In the full BeaconHunt application these values would come from the
analysis engine (``beaconhunt.analysis.engine.AnalysisReport``); here we
ship a static snapshot so the redesigned UI is runnable standalone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SuspiciousRow:
    time_utc: str
    time_short: str          # shorter format for narrow table columns
    source: str
    destination: str
    interval: str
    jitter: str
    confidence: int
    severity: str          # "High" / "Medium" / "Low"
    status: str            # "Active" / "Resolved"


@dataclass(frozen=True)
class EventItem:
    color: str             # "green" / "yellow" / "cyan"
    title: str
    detail: str
    time: str


@dataclass(frozen=True)
class TopDest:
    ip: str
    count: int
    bar_pct: int           # 0..100


@dataclass(frozen=True)
class PatternDetail:
    source: str
    destination: str
    interval: str
    jitter: str
    first_seen: str
    last_seen: str
    confidence: int
    severity: str


@dataclass(frozen=True)
class EvidenceRow:
    icon: str
    label: str
    detail: str


@dataclass(frozen=True)
class RelatedHost:
    ip: str
    role: str              # "source" / "related"


@dataclass(frozen=True)
class TopologyNode:
    name: str
    ip: str
    icon: str              # emoji or glyph
    center: bool


# ---- Network Activity Overview data --------------------------------------

SUSPICIOUS_ROWS: List[SuspiciousRow] = [
    SuspiciousRow("2025-05-10 14:23", "05-10 14:23", "10.0.1.23",  "192.0.2.10",    "300s", "±4s",  92, "High",   "Active"),
    SuspiciousRow("2025-05-10 13:58", "05-10 13:58", "10.0.2.12",  "198.51.100.24", "600s", "±7s",  81, "Medium", "Active"),
    SuspiciousRow("2025-05-10 12:41", "05-10 12:41", "10.0.1.5",   "203.0.113.77",  "900s", "±12s", 76, "Medium", "Active"),
    SuspiciousRow("2025-05-10 11:32", "05-10 11:32", "10.0.3.8",   "192.0.2.10",    "300s", "±5s",  68, "Low",    "Resolved"),
    SuspiciousRow("2025-05-10 10:07", "05-10 10:07", "10.0.1.23",  "198.51.100.24", "600s", "±8s",  63, "Low",    "Resolved"),
]

RECENT_EVENTS: List[EventItem] = [
    EventItem("green",  "Periodic connection detected", "10.0.1.23 → 192.0.2.10 (300s)", "14:23"),
    EventItem("yellow", "New beacon pattern matched",   "10.0.2.12 → 198.51.100.24 (600s)", "13:58"),
    EventItem("cyan",   "Anomaly score increased",      "10.0.1.5 → 203.0.113.77 (900s)", "12:41"),
]

TOP_DESTINATIONS: List[TopDest] = [
    TopDest("192.0.2.10",    6, 100),
    TopDest("198.51.100.24", 4, 67),
    TopDest("203.0.113.77",  2, 33),
]

POTENTIAL_BEACONS_COUNT = 12
DETECTION_CONFIDENCE_PCT = 87

# Header bar live stats (top right).
HEADER_NETWORK_TRAFFIC = "12.4 MB/s"
HEADER_EVENTS_PER_MIN = "8,742"


# ---- Network topology ----------------------------------------------------

TOPOLOGY_NODES: List[TopologyNode] = [
    TopologyNode("LAB-DC-01", "10.0.1.5",  "🖥", False),  # top-left
    TopologyNode("WEB-01",    "10.0.2.12", "🌐", False),  # top-right
    TopologyNode("LAB-WS-02", "10.0.1.23", "👤", False),  # left
    TopologyNode("LAB-WS-01", "10.0.1.5",  "👤", True),   # center
    TopologyNode("DB-01",     "10.0.3.8",  "🗄", False),  # right
    TopologyNode("INTERNET",  "External",  "🌐", False),  # bottom
]


# ---- Beacon Investigation data -------------------------------------------

PATTERN = PatternDetail(
    source="10.0.1.23",
    destination="192.0.2.10",
    interval="300 seconds",
    jitter="±4 seconds",
    first_seen="2025-05-10 08:12",
    last_seen="2025-05-10 14:23",
    confidence=92,
    severity="High",
)


# ---- Beacon Analysis data ------------------------------------------------
#
# A richer cross-destination dataset for the Beacon Analysis page. Each
# row describes one detected beacon candidate with aggregate stats.

@dataclass(frozen=True)
class BeaconCandidate:
    source: str
    destination: str
    port: int
    protocol: str
    interval_sec: int
    jitter_sec: int
    confidence: int
    severity: str          # "High" / "Medium" / "Low"
    event_count: int
    bytes_total: int       # cumulative bytes transferred
    first_seen: str
    last_seen: str
    status: str            # "Active" / "Resolved"


BEACON_CANDIDATES: List[BeaconCandidate] = [
    BeaconCandidate("10.0.1.23",  "192.0.2.10",    443, "TCP",  300, 4,  92, "High",   6,  4_860,  "05-10 08:12", "05-10 14:23", "Active"),
    BeaconCandidate("10.0.2.12",  "198.51.100.24", 8080,"TCP",  600, 7,  81, "Medium", 4,  3_240,  "05-10 09:42", "05-10 13:58", "Active"),
    BeaconCandidate("10.0.1.5",   "203.0.113.77",  53,  "UDP",  900, 12, 76, "Medium", 3,  1_620,  "05-10 10:18", "05-10 12:41", "Active"),
    BeaconCandidate("10.0.3.8",   "192.0.2.10",    443, "TCP",  300, 5,  68, "Low",    6,  4_320,  "05-10 08:30", "05-10 11:32", "Resolved"),
    BeaconCandidate("10.0.1.23",  "198.51.100.24", 8080,"TCP",  600, 8,  63, "Low",    4,  2_560,  "05-10 09:15", "05-10 10:07", "Resolved"),
    BeaconCandidate("10.0.4.2",   "203.0.113.77",  53,  "UDP",  1200,15, 58, "Low",    2,    960,  "05-10 11:00", "05-10 12:50", "Active"),
    BeaconCandidate("10.0.1.17",  "192.0.2.10",    22,  "TCP",  180, 3,  88, "High",   8,  6_480,  "05-10 07:45", "05-10 13:20", "Active"),
    BeaconCandidate("10.0.2.99",  "198.51.100.24", 443, "TCP",  450, 9,  72, "Medium", 5,  3_750,  "05-10 09:00", "05-10 12:15", "Active"),
    BeaconCandidate("10.0.1.5",   "192.0.2.10",    443, "TCP",  300, 6,  79, "Medium", 6,  4_500,  "05-10 08:20", "05-10 11:45", "Resolved"),
    BeaconCandidate("10.0.3.8",   "203.0.113.77",  53,  "UDP",  900, 11, 65, "Low",    3,  1_440,  "05-10 10:30", "05-10 12:10", "Active"),
    BeaconCandidate("10.0.2.12",  "192.0.2.10",    443, "TCP",  300, 5,  74, "Medium", 6,  4_680,  "05-10 08:50", "05-10 11:30", "Active"),
    BeaconCandidate("10.0.4.2",   "198.51.100.24", 8080,"TCP",  600, 10, 60, "Low",    4,  2_880,  "05-10 09:30", "05-10 11:00", "Resolved"),
]


# ---- Alerts data ---------------------------------------------------------
#
# A consolidated alert queue for the Alerts page. The 7-badge on the
# sidebar "Alerts" nav item reflects the number of Open alerts.

@dataclass(frozen=True)
class Alert:
    id: int
    severity: str          # "High" / "Medium" / "Low"
    title: str
    source: str
    destination: str
    interval: str          # e.g. "300s" or "—"
    timestamp: str         # e.g. "14:23"
    age: str               # e.g. "2h ago"
    status: str            # "Open" / "Acknowledged" / "Resolved"
    detail: str


# Use a list (not tuple) of dicts so the Alerts page can mutate status
# at runtime when the user clicks Acknowledge / Resolve.
ALERTS: List[dict] = [
    {"id": 1,  "severity": "High",   "title": "Periodic connection detected",
     "source": "10.0.1.23",  "destination": "192.0.2.10",    "interval": "300s",
     "timestamp": "14:23", "age": "2h ago", "status": "Open",
     "detail": "C2-style beaconing pattern with 92% confidence."},
    {"id": 2,  "severity": "High",   "title": "Beacon pattern matched",
     "source": "10.0.1.17",  "destination": "192.0.2.10",    "interval": "180s",
     "timestamp": "13:20", "age": "3h ago", "status": "Open",
     "detail": "Rapid beaconing at 180s interval, 88% confidence."},
    {"id": 3,  "severity": "Medium", "title": "New beacon pattern matched",
     "source": "10.0.2.12",  "destination": "198.51.100.24", "interval": "600s",
     "timestamp": "13:58", "age": "2h ago", "status": "Open",
     "detail": "New destination exhibiting 600s periodicity."},
    {"id": 4,  "severity": "Medium", "title": "Anomaly score increased",
     "source": "10.0.1.5",   "destination": "203.0.113.77",  "interval": "900s",
     "timestamp": "12:41", "age": "4h ago", "status": "Open",
     "detail": "Anomaly score rose from 61% to 76%."},
    {"id": 5,  "severity": "Medium", "title": "Suspicious retry pattern",
     "source": "10.0.2.99",  "destination": "198.51.100.24", "interval": "450s",
     "timestamp": "12:15", "age": "4h ago", "status": "Open",
     "detail": "Repeated 450s interval connections observed."},
    {"id": 6,  "severity": "Medium", "title": "Periodic connection detected",
     "source": "10.0.2.12",  "destination": "192.0.2.10",    "interval": "300s",
     "timestamp": "11:30", "age": "5h ago", "status": "Open",
     "detail": "300s periodic beacon to known suspect destination."},
    {"id": 7,  "severity": "Medium", "title": "Unusual port observed",
     "source": "10.0.1.5",   "destination": "192.0.2.10",    "interval": "300s",
     "timestamp": "11:45", "age": "5h ago", "status": "Open",
     "detail": "Beaconing on port 443 to TEST-NET-1 address."},
    {"id": 8,  "severity": "High",   "title": "Beacon pattern matched",
     "source": "10.0.1.23",  "destination": "198.51.100.24", "interval": "600s",
     "timestamp": "10:07", "age": "6h ago", "status": "Acknowledged",
     "detail": "Analyst acknowledged — under investigation."},
    {"id": 9,  "severity": "Low",    "title": "New destination observed",
     "source": "10.0.4.2",   "destination": "203.0.113.77",  "interval": "1200s",
     "timestamp": "12:50", "age": "4h ago", "status": "Acknowledged",
     "detail": "First-seen destination, low confidence."},
    {"id": 10, "severity": "Low",    "title": "Periodic connection detected",
     "source": "10.0.3.8",   "destination": "192.0.2.10",    "interval": "300s",
     "timestamp": "11:32", "age": "5h ago", "status": "Acknowledged",
     "detail": "Resolved pattern from earlier shift, ack'd for tracking."},
    {"id": 11, "severity": "Low",    "title": "DNS query burst",
     "source": "10.0.4.2",   "destination": "203.0.113.77",  "interval": "900s",
     "timestamp": "12:10", "age": "4h ago", "status": "Acknowledged",
     "detail": "Periodic DNS queries to external resolver."},
    {"id": 12, "severity": "High",   "title": "Beacon pattern matched",
     "source": "10.0.1.17",  "destination": "192.0.2.10",    "interval": "180s",
     "timestamp": "10:30", "age": "6h ago", "status": "Resolved",
     "detail": "Confirmed authorized health-check endpoint."},
    {"id": 13, "severity": "Medium", "title": "Anomaly score increased",
     "source": "10.0.3.8",   "destination": "203.0.113.77",  "interval": "900s",
     "timestamp": "10:30", "age": "6h ago", "status": "Resolved",
     "detail": "Cleared after endpoint verification."},
    {"id": 14, "severity": "Low",    "title": "Periodic connection detected",
     "source": "10.0.1.23",  "destination": "198.51.100.24", "interval": "600s",
     "timestamp": "10:07", "age": "6h ago", "status": "Resolved",
     "detail": "Confirmed NTP synchronization traffic."},
    {"id": 15, "severity": "Low",    "title": "New destination observed",
     "source": "10.0.4.2",   "destination": "198.51.100.24", "interval": "600s",
     "timestamp": "11:00", "age": "5h ago", "status": "Resolved",
     "detail": "Whitelisted as authorized telemetry endpoint."},
]


# Sidebar alerts badge — reflects the number of Open alerts.
def open_alerts_count() -> int:
    return sum(1 for a in ALERTS if a["status"] == "Open")


# ---- Reports data --------------------------------------------------------
#
# A library of generated analysis reports for the Reports page. The
# original BeaconHunt project supports JSON, CSV, HTML, PDF, and Text
# exports — this dataset mirrors that set of formats.

@dataclass(frozen=True)
class ReportRecord:
    id: int
    name: str               # filename without extension
    format: str             # "JSON" / "CSV" / "HTML" / "PDF" / "Text"
    size_kb: int            # file size in KB
    generated: str          # generation timestamp (short)
    source: str             # input file the report was generated from
    destinations: int       # number of destinations analyzed
    flagged: int            # number of flagged destinations
    status: str             # "Ready" / "Archived"


# Format → icon glyph + color (used by the report list)
REPORT_FORMAT_META = {
    "JSON": ("📄", "#00D4FF"),
    "CSV":  ("▦", "#22C55E"),
    "HTML": ("🌐", "#FACC15"),
    "PDF":  ("📕", "#DC2626"),
    "Text": ("☰", "#8BA3BD"),
}


REPORTS: List[dict] = [
    {"id": 1, "name": "mixed_analysis",      "format": "JSON", "size_kb": 245,
     "generated": "05-10 14:30", "source": "mixed.csv",
     "destinations": 12, "flagged": 4, "status": "Ready"},
    {"id": 2, "name": "mixed_analysis",      "format": "CSV",  "size_kb": 89,
     "generated": "05-10 14:30", "source": "mixed.csv",
     "destinations": 12, "flagged": 4, "status": "Ready"},
    {"id": 3, "name": "mixed_analysis",      "format": "HTML", "size_kb": 412,
     "generated": "05-10 14:31", "source": "mixed.csv",
     "destinations": 12, "flagged": 4, "status": "Ready"},
    {"id": 4, "name": "mixed_analysis",      "format": "PDF",  "size_kb": 678,
     "generated": "05-10 14:31", "source": "mixed.csv",
     "destinations": 12, "flagged": 4, "status": "Ready"},
    {"id": 5, "name": "periodic_pcap",       "format": "JSON", "size_kb": 156,
     "generated": "05-10 13:15", "source": "periodic.pcap",
     "destinations": 8,  "flagged": 6, "status": "Ready"},
    {"id": 6, "name": "periodic_pcap",       "format": "PDF",  "size_kb": 534,
     "generated": "05-10 13:16", "source": "periodic.pcap",
     "destinations": 8,  "flagged": 6, "status": "Ready"},
    {"id": 7, "name": "jittered_periodic",   "format": "CSV",  "size_kb": 72,
     "generated": "05-10 11:42", "source": "jittered_periodic.csv",
     "destinations": 5,  "flagged": 2, "status": "Ready"},
    {"id": 8, "name": "firewall_log_export", "format": "Text", "size_kb": 34,
     "generated": "05-10 10:08", "source": "firewall.txt",
     "destinations": 14, "flagged": 3, "status": "Archived"},
    {"id": 9, "name": "ipv6_analysis",       "format": "HTML", "size_kb": 298,
     "generated": "05-09 18:22", "source": "ipv6.csv",
     "destinations": 6,  "flagged": 1, "status": "Archived"},
    {"id": 10, "name": "udp_periodic",       "format": "JSON", "size_kb": 188,
     "generated": "05-09 16:45", "source": "udp_periodic.pcap",
     "destinations": 4,  "flagged": 2, "status": "Archived"},
]


# Mock source files for the "Export new report" dropdown.
REPORT_SOURCES = [
    "mixed.csv",
    "periodic.pcap",
    "jittered_periodic.csv",
    "firewall.txt",
    "ipv6.csv",
    "udp_periodic.pcap",
    "strict_periodic.csv",
    "irregular_human.csv",
]

BEACON_SUMMARY = [
    ("Total Matches",        "6"),
    ("Unique Destinations",  "1"),
    ("Avg. Interval",        "300s"),
    ("Max. Jitter",          "±7s"),
]

RELATED_HOSTS: List[RelatedHost] = [
    RelatedHost("10.0.1.23", "source"),
    RelatedHost("10.0.1.5",  "related"),
    RelatedHost("10.0.2.12", "related"),
]

EVIDENCE_ROWS: List[EvidenceRow] = [
    EvidenceRow("📄", "Timestamps",        "6 matches"),
    EvidenceRow("📄", "Packet Size Pattern", "Consistent 64 B"),
    EvidenceRow("📋", "Connection Metadata", "TCP SYN, no ACK"),
    EvidenceRow("⚙",  "Associated Flows",  "3 flows"),
]


# ---- 24h beaconing activity sparkline ------------------------------------
# 48 half-hour buckets, roughly matching the noisy cyan baseline plus
# tall green spikes around beacon detection times.

import math as _math
import random as _r
_r.seed(42)

def _gen_24h_activity():
    """Return (hours, baseline_values, beacon_spike_indices, beacon_spike_heights)."""
    hours = list(range(0, 25))  # 0..24 inclusive
    baseline = []
    for h in hours:
        # Noisy baseline 10..55 with a daytime bump
        b = 12 + 22 * abs(_math.sin(h / 24.0 * 3.14)) + _r.uniform(-6, 6)
        baseline.append(max(5, min(60, b)))
    # Beacons detected around working hours.
    beacon_hours = [8, 9, 11, 12, 14, 16, 18, 20]
    beacon_heights = [130, 125, 138, 122, 140, 132, 128, 135]
    return hours, baseline, beacon_hours, beacon_heights


def _gen_timing_chart():
    """Return (timestamps, interval_seconds) for the beacon timing analysis."""
    # 6 detected beacon events spaced ~300s apart across 08:00..14:30.
    times = ["08:12", "09:42", "11:18", "12:53", "13:55", "14:23"]
    intervals = [300, 305, 296, 308, 294, 300]
    return times, intervals


def _gen_jitter_chart():
    """Return (sample_index, jitter_seconds) for the jitter waveform."""
    # Mostly flat ±4 with a spike to ±7 near the end.
    return list(range(12)), [3, 4, 4, 5, 4, 3, 4, 4, 5, 4, 7, 4]


def _gen_header_sparkline():
    """Return values for the small cyan traffic sparkline in the header."""
    return [8, 14, 11, 18, 12, 22, 17, 25, 19, 28, 22, 31, 26, 18, 14, 21]


def _gen_confidence_sparkline():
    """Return values for the green sparkline under the confidence donut."""
    return [3, 5, 4, 7, 6, 9, 8, 11, 10, 13, 11, 14]
