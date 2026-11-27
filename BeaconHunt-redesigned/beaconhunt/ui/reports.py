"""Reports page — generated analysis report library with export actions.

Layout:
  * Page title + subtitle.
  * Filter bar: format dropdown, search box, "Export New Report" button.
  * Four summary stat cards: Total Reports, Total Size, Flagged Items,
    Storage Used.
  * Two-column body:
      - Left (wider): Reports list — vertical cards, one per report.
        Each card shows format icon + name, format pill, size,
        generated timestamp, source file, destinations/flagged counts,
        and a status pill (Ready / Archived). Selecting a card updates
        the details panel on the right.
      - Right: Report Details panel for the selected report — shows
        every metadata field, plus **Open**, **Delete**, and
        **Re-export** action buttons that actually update the list.
  * Bottom: Export New Report section — a source dropdown, format
    dropdown, and an Export button that creates a new mock report and
    prepends it to the list.

All data comes from ``beaconhunt.ui.mock_data.REPORTS`` (a list of
dicts so the page can add/delete entries at runtime).
"""
from __future__ import annotations

import random
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from . import styles
from .mock_data import REPORTS, REPORT_FORMAT_META, REPORT_SOURCES


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


# ---- Report list row ------------------------------------------------------

class _ReportRow(QFrame):
    """One report entry in the list."""

    selected = Signal(int)    # report id

    def __init__(self, report: dict, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._report = report
        self.setObjectName("ReportRow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self._checked = False
        self._refresh_style()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(4)

        # Row 1: icon + name + format pill + size.
        top = QHBoxLayout()
        top.setSpacing(10)
        glyph, color = REPORT_FORMAT_META.get(report["format"], ("📄", styles.THEME.text_muted))
        icon = QLabel(glyph)
        icon.setStyleSheet(f"color:{color}; font-size:14pt; padding:0;")
        icon.setFixedWidth(20)
        icon.setAlignment(Qt.AlignCenter)
        top.addWidget(icon)
        name = QLabel(f"{report['name']}.{report['format'].lower()}")
        name.setStyleSheet(
            f"color:{styles.THEME.text_primary}; font-size:10pt; font-weight:700;"
        )
        top.addWidget(name, 1)
        fmt_pill = QLabel(report["format"])
        fmt_pill.setStyleSheet(
            f"background:{color}; color:#061018; border:none; border-radius:8px; "
            f"padding:2px 8px; font-size:8pt; font-weight:800; letter-spacing:0.5px;"
        )
        fmt_pill.setAlignment(Qt.AlignCenter)
        top.addWidget(fmt_pill)
        size = QLabel(self._fmt_size(report["size_kb"]))
        size.setStyleSheet(
            f"color:{styles.THEME.text_muted}; font-size:9pt; font-weight:600;"
        )
        top.addWidget(size)
        lay.addLayout(top)

        # Row 2: generated + source + dests/flagged.
        meta = QLabel(
            f"Generated {report['generated']}  ·  Source: {report['source']}  "
            f"·  {report['destinations']} dests  ·  {report['flagged']} flagged"
        )
        meta.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:8.5pt;"
        )
        lay.addWidget(meta)

        # Row 3: status pill (compact, left-aligned).
        status_row = QHBoxLayout()
        status_row.setSpacing(0)
        status_row.setContentsMargins(0, 0, 0, 0)
        status_pill = QLabel(report["status"])
        if report["status"] == "Ready":
            status_pill.setStyleSheet(
                f"background:{styles.THEME.green_tint}; color:{styles.THEME.green}; "
                f"border:1px solid {styles.THEME.green}; border-radius:8px; "
                f"padding:2px 8px; font-size:8pt; font-weight:700;"
            )
        else:
            status_pill.setStyleSheet(
                f"background:{styles.THEME.card_alt_bg}; color:{styles.THEME.text_muted}; "
                f"border:1px solid {styles.THEME.card_border}; border-radius:8px; "
                f"padding:2px 8px; font-size:8pt; font-weight:700;"
            )
        status_pill.setAlignment(Qt.AlignCenter)
        status_pill.setFixedHeight(18)
        status_row.addWidget(status_pill)
        status_row.addStretch()
        lay.addLayout(status_row)

    @staticmethod
    def _fmt_size(kb: int) -> str:
        if kb < 1024:
            return f"{kb} KB"
        return f"{kb / 1024:.1f} MB"

    def setChecked(self, checked: bool) -> None:
        self._checked = checked
        self._refresh_style()

    def isChecked(self) -> bool:
        return self._checked

    def _refresh_style(self) -> None:
        if self._checked:
            self.setStyleSheet(
                f"QFrame#ReportRow {{"
                f"  background:{styles.THEME.sidebar_active_bg};"
                f"  border: 1px solid {styles.THEME.cyan};"
                f"  border-radius: 8px;"
                f"}}"
            )
        else:
            self.setStyleSheet(
                f"QFrame#ReportRow {{"
                f"  background:{styles.THEME.card_bg};"
                f"  border: 1px solid {styles.THEME.card_border};"
                f"  border-radius: 8px;"
                f"}}"
                f"QFrame#ReportRow:hover {{"
                f"  background:{styles.THEME.card_hover_bg};"
                f"  border-color: {styles.THEME.scrollbar_handle};"
                f"}}"
            )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.selected.emit(self._report["id"])
        super().mousePressEvent(event)


# ---- Reports page ---------------------------------------------------------

class ReportsPage(QWidget):
    """Report library with search/filter, stat cards, details, export."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Content")
        # Take a shallow copy so we can add/delete at runtime.
        self._reports: List[dict] = [dict(r) for r in REPORTS]
        self._next_id = max(r["id"] for r in self._reports) + 1
        self._selected_id: Optional[int] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(14)

        # --- Title ---
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Reports")
        title.setObjectName("PageTitle")
        title_block.addWidget(title)
        sub = QLabel("Generated analysis reports and exports.")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(sub)
        outer.addLayout(title_block)

        # --- Filter bar ---
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        fmt_label = QLabel("Format:")
        fmt_label.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:600;"
        )
        filter_row.addWidget(fmt_label)
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["All", "JSON", "CSV", "HTML", "PDF", "Text"])
        self.fmt_combo.setFixedWidth(120)
        self.fmt_combo.currentTextChanged.connect(self._refresh)
        filter_row.addWidget(self.fmt_combo)
        filter_row.addSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search report name or source…")
        self.search.setFixedWidth(280)
        self.search.textChanged.connect(self._refresh)
        filter_row.addWidget(self.search)
        filter_row.addStretch()
        self.btn_export_new = QPushButton("＋  Export New Report")
        self.btn_export_new.setCursor(Qt.PointingHandCursor)
        self.btn_export_new.clicked.connect(self._scroll_to_export)
        filter_row.addWidget(self.btn_export_new)
        outer.addLayout(filter_row)

        # --- Stat cards row ---
        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)
        self.card_total = _StatCard(
            "TOTAL REPORTS", "0", "Across all formats",
            color=styles.THEME.cyan,
        )
        self.card_size = _StatCard(
            "TOTAL SIZE", "0", "Cumulative file size",
        )
        self.card_flagged = _StatCard(
            "FLAGGED ITEMS", "0", "Across all reports",
            color=styles.THEME.sev_high_fg,
        )
        self.card_storage = _StatCard(
            "STORAGE USED", "0%", "Of allocated 50 MB",
            color=styles.THEME.green,
        )
        for c in (self.card_total, self.card_size,
                  self.card_flagged, self.card_storage):
            stat_row.addWidget(c, 1)
        outer.addLayout(stat_row)

        # --- Body: report list (left) + details (right) ---
        body = QHBoxLayout()
        body.setSpacing(14)

        # Left: scrollable report list.
        list_card = _Card("Reports Library",
                          "Select a report to inspect details")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea {{ background:transparent; border:none; }}"
            f"QScrollBar:vertical {{ background:transparent; width:8px; }}"
        )
        self._list_container = QWidget()
        self._list_lay = QVBoxLayout(self._list_container)
        self._list_lay.setContentsMargins(0, 0, 8, 0)
        self._list_lay.setSpacing(8)
        self._list_lay.addStretch()
        scroll.setWidget(self._list_container)
        list_card.body.addWidget(scroll)
        body.addWidget(list_card, 62)

        # Right: report details panel.
        details_card = _Card("Report Details", "Metadata and actions")
        self._details_container = QWidget()
        details_lay = QVBoxLayout(self._details_container)
        details_lay.setContentsMargins(0, 0, 0, 0)
        details_lay.setSpacing(8)
        self._details_rows: dict = {}
        for field in ["Filename", "Format", "Size", "Generated",
                      "Source", "Destinations", "Flagged", "Status"]:
            row = QHBoxLayout()
            key_lbl = QLabel(field)
            key_lbl.setStyleSheet(
                f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:500;"
            )
            row.addWidget(key_lbl)
            row.addStretch()
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet(
                f"color:{styles.THEME.text_primary}; font-size:9.5pt; font-weight:600;"
            )
            row.addWidget(val_lbl)
            details_lay.addLayout(row)
            self._details_rows[field] = val_lbl
        # Spacer + action buttons.
        details_lay.addStretch()
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_open = QPushButton("Open")
        self.btn_open.setProperty("secondary", True)
        self.btn_open.setCursor(Qt.PointingHandCursor)
        self.btn_open.clicked.connect(self._on_open)
        btn_row.addWidget(self.btn_open)
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setProperty("outline", True)
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.clicked.connect(self._on_delete)
        btn_row.addWidget(self.btn_delete)
        self.btn_reexport = QPushButton("Re-export")
        self.btn_reexport.setProperty("outline", True)
        self.btn_reexport.setCursor(Qt.PointingHandCursor)
        self.btn_reexport.clicked.connect(self._on_reexport)
        btn_row.addWidget(self.btn_reexport)
        details_lay.addLayout(btn_row)
        details_card.body.addWidget(self._details_container)
        body.addWidget(details_card, 38)

        outer.addLayout(body, 1)

        # --- Export New Report section (bottom) ---
        export_card = _Card("Export New Report",
                            "Generate a fresh report from a source file")
        exp_row = QHBoxLayout()
        exp_row.setSpacing(10)
        src_label = QLabel("Source file:")
        src_label.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:600;"
        )
        exp_row.addWidget(src_label)
        self.src_combo = QComboBox()
        self.src_combo.addItems(REPORT_SOURCES)
        self.src_combo.setFixedWidth(220)
        exp_row.addWidget(self.src_combo)
        exp_row.addSpacing(10)
        fmt_label2 = QLabel("Format:")
        fmt_label2.setStyleSheet(
            f"color:{styles.THEME.text_secondary}; font-size:9pt; font-weight:600;"
        )
        exp_row.addWidget(fmt_label2)
        self.exp_fmt_combo = QComboBox()
        self.exp_fmt_combo.addItems(["JSON", "CSV", "HTML", "PDF", "Text"])
        self.exp_fmt_combo.setFixedWidth(120)
        exp_row.addWidget(self.exp_fmt_combo)
        exp_row.addStretch()
        self.btn_do_export = QPushButton("⤴  Export Now")
        self.btn_do_export.setCursor(Qt.PointingHandCursor)
        self.btn_do_export.clicked.connect(self._on_export_now)
        exp_row.addWidget(self.btn_do_export)
        export_card.body.addLayout(exp_row)
        outer.addWidget(export_card)

        # Initial population.
        self._refresh()
        # Auto-select the first visible report so the details panel
        # isn't empty on first render.
        visible = self._filtered()
        if visible:
            self._on_row_selected(visible[0]["id"])

    # ------------------------------------------------------------------ helpers
    def _filtered(self) -> List[dict]:
        fmt = self.fmt_combo.currentText()
        needle = self.search.text().strip().lower()
        out = []
        for r in self._reports:
            if fmt != "All" and r["format"] != fmt:
                continue
            if needle and needle not in r["name"].lower() \
                      and needle not in r["source"].lower():
                continue
            out.append(r)
        return out

    def _refresh(self) -> None:
        visible = self._filtered()
        # Update stat cards.
        self.card_total.set_value(str(len(self._reports)))
        total_kb = sum(r["size_kb"] for r in self._reports)
        self.card_size.set_value(
            f"{total_kb / 1024:.1f} MB" if total_kb >= 1024 else f"{total_kb} KB"
        )
        total_flagged = sum(r["flagged"] for r in self._reports)
        self.card_flagged.set_value(str(total_flagged))
        storage_pct = min(100, int(total_kb / 50_000 * 100))  # 50 MB budget
        self.card_storage.set_value(f"{storage_pct}%")
        # Rebuild the list.
        self._rebuild_list(visible)
        # Refresh details panel.
        self._refresh_details()

    def _rebuild_list(self, visible: List[dict]) -> None:
        # Remove all existing rows (keep the trailing stretch).
        while self._list_lay.count() > 1:
            item = self._list_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        # Insert new rows before the trailing stretch.
        for r in visible:
            row = _ReportRow(r)
            row.selected.connect(self._on_row_selected)
            if r["id"] == self._selected_id:
                row.setChecked(True)
            self._list_lay.insertWidget(self._list_lay.count() - 1, row)

    def _refresh_details(self) -> None:
        r = next((x for x in self._reports if x["id"] == self._selected_id), None)
        if r is None:
            for lbl in self._details_rows.values():
                lbl.setText("—")
            self.btn_open.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_reexport.setEnabled(False)
            return
        self._details_rows["Filename"].setText(f"{r['name']}.{r['format'].lower()}")
        self._details_rows["Format"].setText(r["format"])
        self._details_rows["Size"].setText(_ReportRow._fmt_size(r["size_kb"]))
        self._details_rows["Generated"].setText(r["generated"])
        self._details_rows["Source"].setText(r["source"])
        self._details_rows["Destinations"].setText(str(r["destinations"]))
        self._details_rows["Flagged"].setText(str(r["flagged"]))
        self._details_rows["Status"].setText(r["status"])
        self.btn_open.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.btn_reexport.setEnabled(True)

    # ------------------------------------------------------------------ actions
    def _on_row_selected(self, report_id: int) -> None:
        self._selected_id = report_id
        # Update the checked state of each row.
        for i in range(self._list_lay.count() - 1):
            item = self._list_lay.itemAt(i)
            w = item.widget() if item is not None else None
            if isinstance(w, _ReportRow):
                w.setChecked(w._report["id"] == report_id)
        self._refresh_details()

    def _on_open(self) -> None:
        r = next((x for x in self._reports if x["id"] == self._selected_id), None)
        if r is None:
            return
        # In the full app this would launch the system file opener. In the
        # demo we just emit a status message via the parent's status bar.
        win = self.window()
        if hasattr(win, "statusBar"):
            win.statusBar().showMessage(
                f"Would open: {r['name']}.{r['format'].lower()}  "
                f"(in the full BeaconHunt app this launches the system viewer)"
            )

    def _on_delete(self) -> None:
        if self._selected_id is None:
            return
        self._reports = [r for r in self._reports if r["id"] != self._selected_id]
        self._selected_id = None
        self._refresh()

    def _on_reexport(self) -> None:
        r = next((x for x in self._reports if x["id"] == self._selected_id), None)
        if r is None:
            return
        # Bump the size slightly to simulate a re-export with new data.
        r["size_kb"] = max(8, int(r["size_kb"] * random.uniform(0.95, 1.05)))
        r["generated"] = "just now"
        self._refresh()

    def _on_export_now(self) -> None:
        src = self.src_combo.currentText()
        fmt = self.exp_fmt_combo.currentText()
        # Derive a name from the source filename (without extension).
        base = src.rsplit(".", 1)[0] if "." in src else src
        # Pick plausible random stats for the new report.
        new_report = {
            "id": self._next_id,
            "name": base,
            "format": fmt,
            "size_kb": random.randint(40, 600),
            "generated": "just now",
            "source": src,
            "destinations": random.randint(3, 16),
            "flagged": random.randint(0, 6),
            "status": "Ready",
        }
        self._next_id += 1
        self._reports.insert(0, new_report)
        self._selected_id = new_report["id"]
        # Reset the filter so the new report shows.
        self.fmt_combo.blockSignals(True)
        self.fmt_combo.setCurrentText("All")
        self.fmt_combo.blockSignals(False)
        self.search.clear()
        self._refresh()

    def _scroll_to_export(self) -> None:
        # Just focus the source combo — the export section is at the bottom
        # of the page and always visible.
        self.src_combo.setFocus()
