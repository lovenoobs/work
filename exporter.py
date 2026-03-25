from typing import List, Dict, Any
from pathlib import Path
import pandas as pd

def export_quotes_xlsx(quotes: List[Dict[str, Any]], out_path: Path):
    df = pd.DataFrame(quotes)

    rename = {
        "part_no": "型号",
        "qty": "数量",
        "min_year_text": "年份(最低)",
        "vendor_name": "供应商",
        "dc_text": "报价年份/DC",
        "lead_time": "交期",
        "quote_qty": "报价数量",
        "rmb_untaxed": "RMB未税",
        "rmb_taxed": "RMB含税",
        "usd": "USD",
        "quote_text": "报价原文",
        "created_at": "录入时间",
    }
    for k, v in rename.items():
        if k in df.columns:
            df = df.rename(columns={k: v})

    preferred = ["型号","数量","年份(最低)","供应商","报价年份/DC","RMB未税","RMB含税","USD","交期","报价数量","报价原文","录入时间"]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    df = df[cols]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="报价明细")