import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedQuote:
    rmb_untaxed: Optional[float] = None
    rmb_taxed: Optional[float] = None
    usd: Optional[float] = None
    dc_text: Optional[str] = None
    lead_time: Optional[str] = None
    quote_qty: Optional[int] = None

_DC_RE = re.compile(r"\b(\d{2}|\d{4})\+\b")
_NUM_RE = re.compile(r"(?<!\d)(\d+(?:\.\d+)?)(?!\d)")
_QTY_RE = re.compile(r"(?<!\d)(\d{2,})(?:\s*)(pcs|pc|片|只|颗|K|k)?\b", re.IGNORECASE)

def parse_min_year_text(min_year_text: str) -> int:
    m = re.match(r"^\s*(\d{2})\+\s*$", min_year_text)
    if not m:
        raise ValueError(f"最低年份格式不正确: {min_year_text}，应为如 '22+'")
    return 2000 + int(m.group(1))

def parse_dc_year(dc_text: str) -> Optional[int]:
    if not dc_text:
        return None
    m = _DC_RE.search(dc_text)
    if not m:
        return None
    s = m.group(1)
    if len(s) == 2:
        return 2000 + int(s)
    if len(s) == 4:
        return 2000 + int(s[:2])
    return None

def meets_year(dc_text: str, min_year: int) -> bool:
    y = parse_dc_year(dc_text)
    if y is None:
        return False
    return y >= min_year

def parse_quote_text(text: str) -> ParsedQuote:
    t = (text or "").strip()
    out = ParsedQuote()

    m = _DC_RE.search(t)
    if m:
        out.dc_text = m.group(0)

    for kw in ["现货", "当天", "即发"]:
        if kw in t:
            out.lead_time = kw
            break
    mlt = re.search(r"(\d+)\s*(天|周)", t)
    if mlt:
        out.lead_time = f"{mlt.group(1)}{mlt.group(2)}"

    mq = _QTY_RE.search(t)
    if mq:
        try:
            out.quote_qty = int(mq.group(1))
        except:
            pass

    is_usd = bool(re.search(r"\bUSD\b|US\$|\bU\b", t, re.IGNORECASE))
    is_taxed = bool(re.search(r"含税|含票|含点|含13|含增值税", t))

    nums = [float(x) for x in _NUM_RE.findall(t)]
    price = nums[0] if nums else None

    if price is not None:
        if is_usd:
            out.usd = price
        elif is_taxed:
            out.rmb_taxed = price
        else:
            out.rmb_untaxed = price

    return out