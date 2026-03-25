from dataclasses import dataclass
from typing import List, Optional, Tuple
from playwright.sync_api import sync_playwright, Page
from config import AppConfig
from parser import parse_min_year_text, meets_year

@dataclass
class VendorRow:
    vendor_name: str
    dc_text: str
    has_sscp: bool
    row_index: int

class ICJYWScraper:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self._pw = None
        self._browser = None
        self._context = None
        self.page: Optional[Page] = None

    def start(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self.cfg.headless)
        self._context = self._browser.new_context()
        self.page = self._context.new_page()

    def stop(self):
        try:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
        finally:
            self._pw = None
            self._browser = None
            self._context = None
            self.page = None

    def open_search(self, part_no: str):
        assert self.page is not None
        url = self.cfg.search_url_template.format(pn=part_no)
        self.page.goto(url, wait_until="domcontentloaded")

    def _read_rows(self, min_year_text: str) -> List[VendorRow]:
        assert self.page is not None
        min_year = parse_min_year_text(min_year_text)

        rows = self.page.locator(self.cfg.result_row_selector)
        count = rows.count()
        out: List[VendorRow] = []

        for i in range(count):
            row = rows.nth(i)

            vendor = ""
            if row.locator(self.cfg.vendor_cell_selector).count():
                vendor = row.locator(self.cfg.vendor_cell_selector).inner_text().strip()

            dc = ""
            if row.locator(self.cfg.dc_cell_selector).count():
                dc = row.locator(self.cfg.dc_cell_selector).inner_text().strip()

            has_sscp = row.locator(self.cfg.sscp_clickable_selector).count() > 0

            if not vendor and not dc:
                continue

            if meets_year(dc, min_year):
                out.append(VendorRow(vendor_name=vendor, dc_text=dc, has_sscp=has_sscp, row_index=i))

        return out

    def pick_top_vendors(self, min_year_text: str, top_n: int) -> List[VendorRow]:
        rows = self._read_rows(min_year_text)

        selected: List[VendorRow] = []
        used_idx = set()

        for r in rows:
            if r.has_sscp and r.row_index not in used_idx:
                selected.append(r)
                used_idx.add(r.row_index)
            if len(selected) >= top_n:
                return selected

        for r in rows:
            if r.row_index in used_idx:
                continue
            selected.append(r)
            used_idx.add(r.row_index)
            if len(selected) >= top_n:
                break

        return selected

    def click_qq_for_rows(self, rows: List[VendorRow]) -> List[Tuple[VendorRow, str]]:
        assert self.page is not None
        results: List[Tuple[VendorRow, str]] = []

        for r in rows:
            try:
                row = self.page.locator(self.cfg.result_row_selector).nth(r.row_index)
                qq_btn = row.locator(self.cfg.qq_button_selector).first
                qq_btn.click()

                try:
                    self.page.locator(self.cfg.continue_wakeup_selector).click(timeout=5000)
                except Exception:
                    try:
                        self.page.locator(self.cfg.continue_wakeup_selector).click(timeout=10000)
                    except Exception:
                        pass

                results.append((r, "OK"))
            except Exception as e:
                results.append((r, f"FAIL: {e}"))
        return results