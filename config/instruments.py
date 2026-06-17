"""
Instrument and sector definitions.
Add / remove instruments by editing INSTRUMENTS below — no other file changes needed.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Sector definitions ──────────────────────────────────────────────

@dataclass
class Sector:
    id: str
    name: str
    icon: str
    order: int


SECTORS: List[Sector] = [
    Sector(id="ferrous",    name="黑色建材",     icon="🏗️", order=1),
    Sector(id="energy",     name="能源化工",     icon="⚡", order=2),
    Sector(id="nonferrous", name="有色金属",     icon="🪙", order=3),
    Sector(id="agri",       name="农产品/油脂", icon="🌾", order=4),
    Sector(id="newenergy",  name="新能源/其他", icon="🔋", order=5),
    Sector(id="financial",  name="金融期货",     icon="📈", order=6),
]

SECTOR_BY_ID = {s.id: s for s in SECTORS}


# ── Instrument definitions ──────────────────────────────────────────

@dataclass
class Instrument:
    """A single tradable instrument."""
    code: str            # Product code: "rb", "cu", etc.
    exchange: str        # Exchange: "SHFE", "DCE", "CZCE", "INE", "GFEX"
    name: str            # Chinese display name
    sector_id: str       # Must match a Sector.id above
    contract_suffix: Optional[str] = None  # Override global suffix; None = use global


INSTRUMENTS: List[Instrument] = [
    # ══════════════════════════════════════════════════════════════════
    # 黑色建材  ferrous
    # ══════════════════════════════════════════════════════════════════
    Instrument(code="rb", exchange="SHFE", name="螺纹钢",     sector_id="ferrous"),
    Instrument(code="hc", exchange="SHFE", name="热卷",       sector_id="ferrous"),
    # Instrument(code="wr", exchange="SHFE", name="线材",       sector_id="ferrous"),
    Instrument(code="ss", exchange="SHFE", name="不锈钢",     sector_id="ferrous"),
    Instrument(code="i",  exchange="DCE",  name="铁矿石",     sector_id="ferrous"),
    Instrument(code="jm", exchange="DCE",  name="焦煤",       sector_id="ferrous"),
    # Instrument(code="j",  exchange="DCE",  name="焦炭",       sector_id="ferrous"),
    Instrument(code="SM", exchange="CZCE", name="硅锰",       sector_id="ferrous"),
    # Instrument(code="SF", exchange="CZCE", name="硅铁",       sector_id="ferrous"),
    Instrument(code="FG", exchange="CZCE", name="玻璃",       sector_id="ferrous"),
    Instrument(code="SA", exchange="CZCE", name="纯碱",       sector_id="ferrous"),

    # ══════════════════════════════════════════════════════════════════
    # 能源化工  energy
    # ══════════════════════════════════════════════════════════════════
    # SHFE
    Instrument(code="ru", exchange="SHFE", name="天然橡胶",   sector_id="energy"),
    Instrument(code="br", exchange="SHFE", name="合成橡胶",   sector_id="energy"),
    Instrument(code="bu", exchange="SHFE", name="沥青",       sector_id="energy"),
    # Instrument(code="fu", exchange="SHFE", name="燃料油",     sector_id="energy"),
    Instrument(code="sp", exchange="SHFE", name="纸浆",       sector_id="energy"),
    # INE
    # Instrument(code="sc", exchange="INE",  name="原油",       sector_id="energy"),
    # Instrument(code="lu", exchange="INE",  name="低硫燃油",   sector_id="energy"),
    # DCE
    Instrument(code="l",  exchange="DCE",  name="塑料",       sector_id="energy"),
    Instrument(code="pp", exchange="DCE",  name="聚丙烯",     sector_id="energy"),
    Instrument(code="v",  exchange="DCE",  name="PVC",        sector_id="energy"),
    Instrument(code="eg", exchange="DCE",  name="乙二醇",     sector_id="energy"),
    Instrument(code="eb", exchange="DCE",  name="苯乙烯",     sector_id="energy"),
    Instrument(code="pg", exchange="DCE",  name="液化气",     sector_id="energy"),
    # CZCE
    Instrument(code="TA", exchange="CZCE", name="PTA",        sector_id="energy"),
    Instrument(code="MA", exchange="CZCE", name="甲醇",       sector_id="energy"),
    Instrument(code="UR", exchange="CZCE", name="尿素",       sector_id="energy"),
    Instrument(code="PF", exchange="CZCE", name="短纤",       sector_id="energy"),
    Instrument(code="SH", exchange="CZCE", name="烧碱",       sector_id="energy"),
    Instrument(code="PX", exchange="CZCE", name="对二甲苯",   sector_id="energy"),

    # ══════════════════════════════════════════════════════════════════
    # 有色金属  nonferrous
    # ══════════════════════════════════════════════════════════════════
    # Instrument(code="cu", exchange="SHFE", name="沪铜",       sector_id="nonferrous"),
    # Instrument(code="al", exchange="SHFE", name="沪铝",       sector_id="nonferrous"),
    # Instrument(code="zn", exchange="SHFE", name="沪锌",       sector_id="nonferrous"),
    # Instrument(code="pb", exchange="SHFE", name="沪铅",       sector_id="nonferrous"),
    # Instrument(code="ni", exchange="SHFE", name="沪镍",       sector_id="nonferrous"),
    # Instrument(code="sn", exchange="SHFE", name="沪锡",       sector_id="nonferrous"),
    Instrument(code="ao", exchange="SHFE", name="氧化铝",     sector_id="nonferrous"),
    # Instrument(code="au", exchange="SHFE", name="黄金",       sector_id="nonferrous"),
    # Instrument(code="ag", exchange="SHFE", name="白银",       sector_id="nonferrous"),
    # Instrument(code="bc", exchange="INE",  name="国际铜",     sector_id="nonferrous"),

    # ══════════════════════════════════════════════════════════════════
    # 农产品/油脂  agri
    # ══════════════════════════════════════════════════════════════════
    # DCE 油料油脂
    Instrument(code="m",  exchange="DCE",  name="豆粕",       sector_id="agri"),
    Instrument(code="a",  exchange="DCE",  name="豆一",       sector_id="agri"),
    Instrument(code="b",  exchange="DCE",  name="豆二",       sector_id="agri"),
    Instrument(code="y",  exchange="DCE",  name="豆油",       sector_id="agri"),
    Instrument(code="p",  exchange="DCE",  name="棕榈油",     sector_id="agri"),
    # DCE 谷物
    Instrument(code="c",  exchange="DCE",  name="玉米",       sector_id="agri"),
    Instrument(code="cs", exchange="DCE",  name="玉米淀粉",   sector_id="agri"),
    # Instrument(code="rr", exchange="DCE",  name="粳米",       sector_id="agri"),
    # DCE 畜牧
    Instrument(code="jd", exchange="DCE",  name="鸡蛋",       sector_id="agri"),
    Instrument(code="lh", exchange="DCE",  name="生猪",       sector_id="agri"),
    # DCE 木材
    # Instrument(code="fb", exchange="DCE",  name="纤维板",     sector_id="agri"),
    # Instrument(code="bb", exchange="DCE",  name="胶合板",     sector_id="agri"),
    # CZCE 油脂油料
    Instrument(code="RM", exchange="CZCE", name="菜粕",       sector_id="agri"),
    Instrument(code="OI", exchange="CZCE", name="菜油",       sector_id="agri"),
    # Instrument(code="RS", exchange="CZCE", name="菜籽",       sector_id="agri"),
    # Instrument(code="PK", exchange="CZCE", name="花生",       sector_id="agri"),
    # CZCE 软商品
    Instrument(code="SR", exchange="CZCE", name="白糖",       sector_id="agri"),
    Instrument(code="CF", exchange="CZCE", name="棉花",       sector_id="agri"),
    # Instrument(code="CY", exchange="CZCE", name="棉纱",       sector_id="agri"),
    # CZCE 水果
    Instrument(code="AP", exchange="CZCE", name="苹果",       sector_id="agri"),
    Instrument(code="CJ", exchange="CZCE", name="红枣",       sector_id="agri"),
    # CZCE 谷物 (低流动性)
    # Instrument(code="WH", exchange="CZCE", name="强麦",       sector_id="agri"),
    # Instrument(code="PM", exchange="CZCE", name="普麦",       sector_id="agri"),
    # Instrument(code="RI", exchange="CZCE", name="早籼稻",     sector_id="agri"),
    # Instrument(code="LR", exchange="CZCE", name="晚籼稻",     sector_id="agri"),
    # Instrument(code="JR", exchange="CZCE", name="粳稻",       sector_id="agri"),

    # ══════════════════════════════════════════════════════════════════
    # 新能源/其他  newenergy
    # ══════════════════════════════════════════════════════════════════
    Instrument(code="lc", exchange="GFEX", name="碳酸锂",     sector_id="newenergy"),
    Instrument(code="si", exchange="GFEX", name="工业硅",     sector_id="newenergy"),

    # ══════════════════════════════════════════════════════════════════
    # 金融期货  financial  (CFFEX)
    # ══════════════════════════════════════════════════════════════════
    Instrument(code="IF", exchange="CFFEX", name="沪深300股指",     sector_id="financial"),
    Instrument(code="IC", exchange="CFFEX", name="中证500股指",     sector_id="financial"),
    Instrument(code="IH", exchange="CFFEX", name="上证50股指",      sector_id="financial"),
    Instrument(code="IM", exchange="CFFEX", name="中证1000股指",    sector_id="financial"),
    # Instrument(code="TS", exchange="CFFEX", name="2年期国债",       sector_id="financial"),
    # Instrument(code="TF", exchange="CFFEX", name="5年期国债",       sector_id="financial"),
    # Instrument(code="T",  exchange="CFFEX", name="10年期国债",      sector_id="financial"),
    # Instrument(code="TL", exchange="CFFEX", name="30年期国债",      sector_id="financial"),
]


def get_contract_suffix(inst: "Instrument", global_suffix: str = "") -> str:
    """Resolve the effective contract suffix for an instrument.

    Priority (highest first):
    1. Instrument's own ``contract_suffix`` field
    2. Environment variable ``CD_CONTRACT_{CODE}`` (e.g. ``CD_CONTRACT_RB=2501``)
    3. Global suffix (from CLI ``--suffix`` or settings)
    """
    if inst.contract_suffix:
        return inst.contract_suffix
    env_val = os.environ.get(f"CD_CONTRACT_{inst.code.upper()}", "")
    if env_val:
        return env_val
    return global_suffix


def build_tqsdk_id(inst: "Instrument", effective_suffix: str = "") -> str:
    """Construct the tqsdk instrument id for quote subscription.

    Uses main-contract auto-resolution (``KQ.m@`` prefix) so tqsdk
    always returns the most actively traded contract month.
    Pass an *effective_suffix* to pin a specific month.
    """
    suffix = effective_suffix or inst.contract_suffix or ""
    if suffix:
        return f"{inst.exchange}.{inst.code}{suffix}"
    return f"KQ.m@{inst.exchange}.{inst.code}"


def get_sector(inst: Instrument) -> Sector:
    return SECTOR_BY_ID[inst.sector_id]
