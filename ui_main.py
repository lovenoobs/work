from PySide6 import QtWidgets
from pathlib import Path
import pandas as pd

from config import AppConfig
from storage import init_db, clear_all, insert_bom_items, list_bom_items, insert_quote, list_quotes
from parser import parse_quote_text
from scraper import ICJYWScraper

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IC交易网询价助手 (本机版)")
        self.resize(1100, 700)

        init_db()

        self.cfg = AppConfig()
        self.scraper = ICJYWScraper(self.cfg)

        self.btn_load_bom = QtWidgets.QPushButton("导入BOM Excel")
        self.btn_clear = QtWidgets.QPushButton("清空数据")
        self.chk_headless = QtWidgets.QCheckBox("无头模式(不显示浏览器)")
        self.chk_headless.setChecked(False)

        self.bom_list = QtWidgets.QTableWidget(0, 4)
        self.bom_list.setHorizontalHeaderLabels(["ID", "型号", "数量", "年份(最低)"])
        self.bom_list.horizontalHeader().setStretchLastSection(True)
        self.bom_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.btn_start_browser = QtWidgets.QPushButton("启动浏览器")
        self.btn_stop_browser = QtWidgets.QPushButton("关闭浏览器")
        self.btn_open_search = QtWidgets.QPushButton("打开选中料号搜索页")
        self.btn_pick_and_qq = QtWidgets.QPushButton("筛选前10家并唤起QQ")

        self.txt_template = QtWidgets.QPlainTextEdit()
        self.txt_template.setPlainText("你好，这颗物料{型号}，数量{数量} 是否有货，烦请报价，谢谢！")
        self.btn_copy_msg = QtWidgets.QPushButton("复制询价话术(按选中料号)")
        self.lbl_status = QtWidgets.QLabel("状态：就绪")

        self.cmb_vendor = QtWidgets.QComboBox()
        self.cmb_vendor.setEditable(True)
        self.txt_quote = QtWidgets.QPlainTextEdit()
        self.btn_parse_save = QtWidgets.QPushButton("解析并保存报价(粘贴文本)")
        self.btn_export = QtWidgets.QPushButton("导出Excel(报价明细)")

        self.quotes_table = QtWidgets.QTableWidget(0, 8)
        self.quotes_table.setHorizontalHeaderLabels(["型号","数量","年份(最低)","供应商","RMB未税","RMB含税","USD","录入时间"])
        self.quotes_table.horizontalHeader().setStretchLastSection(True)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.btn_load_bom)
        top.addWidget(self.btn_clear)
        top.addStretch()
        top.addWidget(self.chk_headless)

        left = QtWidgets.QVBoxLayout()
        left.addLayout(top)
        left.addWidget(QtWidgets.QLabel("BOM列表："))
        left.addWidget(self.bom_list)

        actions = QtWidgets.QHBoxLayout()
        actions.addWidget(self.btn_start_browser)
        actions.addWidget(self.btn_stop_browser)
        actions.addWidget(self.btn_open_search)
        actions.addWidget(self.btn_pick_and_qq)
        left.addLayout(actions)

        left.addWidget(QtWidgets.QLabel("询价模板："))
        left.addWidget(self.txt_template)
        left.addWidget(self.btn_copy_msg)
        left.addWidget(self.lbl_status)

        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel("供应商(可选填)："))
        right.addWidget(self.cmb_vendor)
        right.addWidget(QtWidgets.QLabel("粘贴供应商报价文本："))
        right.addWidget(self.txt_quote)
        right.addWidget(self.btn_parse_save)
        right.addWidget(QtWidgets.QLabel("已保存报价："))
        right.addWidget(self.quotes_table)
        right.addWidget(self.btn_export)

        main = QtWidgets.QHBoxLayout()
        main.addLayout(left, 3)
        main.addLayout(right, 2)

        central = QtWidgets.QWidget()
        central.setLayout(main)
        self.setCentralWidget(central)

        self.btn_load_bom.clicked.connect(self.on_load_bom)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_start_browser.clicked.connect(self.on_start_browser)
        self.btn_stop_browser.clicked.connect(self.on_stop_browser)
        self.btn_open_search.clicked.connect(self.on_open_search)
        self.btn_pick_and_qq.clicked.connect(self.on_pick_and_qq)
        self.btn_copy_msg.clicked.connect(self.on_copy_msg)
        self.btn_parse_save.clicked.connect(self.on_parse_save)
        self.btn_export.clicked.connect(self.on_export)

        self.refresh_bom()
        self.refresh_quotes()

    def set_status(self, s: str):
        self.lbl_status.setText(f"状态：{s}")

    def refresh_bom(self):
        items = list_bom_items()
        self.bom_list.setRowCount(len(items))
        for r, it in enumerate(items):
            self.bom_list.setItem(r, 0, QtWidgets.QTableWidgetItem(str(it["id"])))
            self.bom_list.setItem(r, 1, QtWidgets.QTableWidgetItem(it["part_no"]))
            self.bom_list.setItem(r, 2, QtWidgets.QTableWidgetItem(str(it["qty"])))
            self.bom_list.setItem(r, 3, QtWidgets.QTableWidgetItem(it["min_year_text"]))

    def refresh_quotes(self):
        quotes = list_quotes()
        self.quotes_table.setRowCount(len(quotes))
        for r, q in enumerate(quotes):
            self.quotes_table.setItem(r, 0, QtWidgets.QTableWidgetItem(q["part_no"]))
            self.quotes_table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(q["qty"])))
            self.quotes_table.setItem(r, 2, QtWidgets.QTableWidgetItem(q["min_year_text"]))
            self.quotes_table.setItem(r, 3, QtWidgets.QTableWidgetItem(q.get("vendor_name") or ""))
            self.quotes_table.setItem(r, 4, QtWidgets.QTableWidgetItem("" if q["rmb_untaxed"] is None else str(q["rmb_untaxed"])))
            self.quotes_table.setItem(r, 5, QtWidgets.QTableWidgetItem("" if q["rmb_taxed"] is None else str(q["rmb_taxed"])))
            self.quotes_table.setItem(r, 6, QtWidgets.QTableWidgetItem("" if q["usd"] is None else str(q["usd"])))
            self.quotes_table.setItem(r, 7, QtWidgets.QTableWidgetItem(q["created_at"]))

    def get_selected_bom(self):
        sel = self.bom_list.selectionModel().selectedRows()
        if not sel:
            return None
        row = sel[0].row()
        bom_id = int(self.bom_list.item(row, 0).text())
        part_no = self.bom_list.item(row, 1).text()
        qty = int(self.bom_list.item(row, 2).text())
        min_year_text = self.bom_list.item(row, 3).text()
        return bom_id, part_no, qty, min_year_text

    def on_load_bom(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择BOM Excel", "", "Excel Files (*.xlsx *.xls)")
        if not path:
            return
        df = pd.read_excel(path)

        required = ["型号", "数量", "年份"]
        for c in required:
            if c not in df.columns:
                QtWidgets.QMessageBox.critical(self, "错误", f"Excel缺少列：{c}，当前列：{list(df.columns)}")
                return

        items = []
        for _, row in df.iterrows():
            pn = str(row["型号"]).strip()
            if not pn or pn.lower() == "nan":
                continue
            qty = int(row["数量"])
            year = str(row["年份"]).strip()
            items.append({"part_no": pn, "qty": qty, "min_year_text": year})

        insert_bom_items(items)
        self.refresh_bom()
        self.set_status(f"已导入 {len(items)} 条BOM")

    def on_clear(self):
        clear_all()
        self.refresh_bom()
        self.refresh_quotes()
        self.set_status("已清空数据")

    def on_start_browser(self):
        self.cfg.headless = self.chk_headless.isChecked()
        self.scraper = ICJYWScraper(self.cfg)
        try:
            self.scraper.start()
            self.set_status("浏览器已启动")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "启动失败", str(e))

    def on_stop_browser(self):
        try:
            self.scraper.stop()
            self.set_status("浏览器已关闭")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "关闭失败", str(e))

    def on_open_search(self):
        selected = self.get_selected_bom()
        if not selected:
            QtWidgets.QMessageBox.information(self, "提示", "请先选中一条BOM")
            return
        _, part_no, _, _ = selected
        try:
            self.scraper.open_search(part_no)
            self.set_status(f"已打开搜索页：{part_no}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "打开失败", str(e))

    def on_pick_and_qq(self):
        selected = self.get_selected_bom()
        if not selected:
            QtWidgets.QMessageBox.information(self, "提示", "请先选中一条BOM")
            return
        _, part_no, _, min_year_text = selected
        try:
            picked = self.scraper.pick_top_vendors(min_year_text, self.cfg.top_n)
            res = self.scraper.click_qq_for_rows(picked)
            ok = sum(1 for _, s in res if s == "OK")
            self.set_status(f"{part_no} 已尝试唤起QQ：成功 {ok}/{len(res)}")

            self.cmb_vendor.clear()
            for r, _ in res:
                self.cmb_vendor.addItem(r.vendor_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "执行失败", str(e))

    def on_copy_msg(self):
        selected = self.get_selected_bom()
        if not selected:
            QtWidgets.QMessageBox.information(self, "提示", "请先选中一条BOM")
            return
        _, part_no, qty, _ = selected
        tpl = self.txt_template.toPlainText()
        msg = tpl.replace("{型号}", part_no).replace("{数量}", str(qty))
        QtWidgets.QApplication.clipboard().setText(msg)
        self.set_status("询价话术已复制到剪贴板")

    def on_parse_save(self):
        selected = self.get_selected_bom()
        if not selected:
            QtWidgets.QMessageBox.information(self, "提示", "请先选中一条BOM（对应这条报价属于哪个料号）")
            return
        bom_id, _, _, _ = selected
        vendor = self.cmb_vendor.currentText().strip() or None
        text = self.txt_quote.toPlainText().strip()
        if not text:
            QtWidgets.QMessageBox.information(self, "提示", "请粘贴报价文本")
            return

        parsed = parse_quote_text(text)
        insert_quote(
            bom_item_id=bom_id,
            vendor_name=vendor,
            quote_text=text,
            rmb_untaxed=parsed.rmb_untaxed,
            rmb_taxed=parsed.rmb_taxed,
            usd=parsed.usd,
            dc_text=parsed.dc_text,
            lead_time=parsed.lead_time,
            quote_qty=parsed.quote_qty,
        )
        self.txt_quote.setPlainText("")
        self.refresh_quotes()
        self.set_status("报价已解析并保存")

    def on_export(self):
        out, _ = QtWidgets.QFileDialog.getSaveFileName(self, "导出Excel", "报价明细.xlsx", "Excel Files (*.xlsx)")
        if not out:
            return
        from exporter import export_quotes_xlsx
        quotes = list_quotes()
        export_quotes_xlsx(quotes, Path(out))
        self.set_status(f"已导出：{out}")