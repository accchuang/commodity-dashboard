from tqsdk import TqApi, TqBacktest, TqAuth
from tqsdk.tafunc import ma
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, timedelta

# ==================== 配置参数（请根据实际情况修改） ====================
# 合约列表 — 支持同时回测多个合约
SYMBOLS = [
    "CZCE.OI609",
]

# 天勤账号
TQ_USERNAME = "15583300776"
TQ_PASSWORD = "Unfair4400"

DURATION = 60 * 5             # K线周期（秒），60=1分钟，300=5分钟
BACKTEST_DAYS = 30            # 回测天数（近N天）
DATA_LENGTH = 200            # 拉取K线数量
MA_FAST = 9                   # 快均线周期
MA_SLOW = 21                  # 慢均线周期
OVERLAP_THRESHOLD = 0.70      # 实体重叠阈值（70%）
LOOKBACK_HIGH = 5             # 前一根K线极值回溯周期
BODY_RATIO_THRESHOLD = 0.6    # 大实体判定阈值（实体/振幅）
RISK_REWARD_RATIO = 1.5       # 盈亏比


# ======================================================================

# -------------------- 数据结构 --------------------
@dataclass
class Trade:
    """单笔交易记录"""
    symbol: str
    direction: str          # "long" 或 "short"
    entry_time: str
    entry_price: float
    stop_loss: float
    take_profit: float
    exit_time: str = ""
    exit_price: float = 0.0
    exit_reason: str = ""   # "stop_loss" / "take_profit" / "close_out"
    pnl: float = 0.0
    pnl_pct: float = 0.0


@dataclass
class BacktestResult:
    """单合约回测结果汇总"""
    symbol: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_drawdown_pct: float = 0.0
    profit_factor: float = 0.0
    trades: List[Trade] = field(default_factory=list)


# -------------------- 基础辅助函数 --------------------
def is_big_candle(k, threshold=BODY_RATIO_THRESHOLD):
    """判断是否为"大实体"：实体长度占振幅的比例超过阈值"""
    amplitude = k.high - k.low
    if amplitude == 0:
        return False
    body = abs(k.close - k.open)
    return body / amplitude >= threshold


def is_bearish(k):
    """是否为阴线（下跌）"""
    return k.close < k.open


def is_bullish(k):
    """是否为阳线（上涨）"""
    return k.close > k.open


def calc_overlap_ratio(prev_k, curr_k):
    """
    计算当前K线实体 与 前一根K线实体的重叠比例
    返回: 重叠部分占前一根K线实体的百分比 (0~1)
    """
    prev_top = max(prev_k.open, prev_k.close)
    prev_bottom = min(prev_k.open, prev_k.close)
    curr_top = max(curr_k.open, curr_k.close)
    curr_bottom = min(curr_k.open, curr_k.close)

    overlap_top = min(prev_top, curr_top)
    overlap_bottom = max(prev_bottom, curr_bottom)

    if overlap_top <= overlap_bottom:
        return 0.0
    prev_body = prev_top - prev_bottom
    if prev_body == 0:
        return 0.0
    return (overlap_top - overlap_bottom) / prev_body


# -------------------- 形态判定函数 --------------------
def calc_body_ratio(prev_k, curr_k):
    """
    计算当前K线实体 与 前一根K线实体的比值
    返回: curr_body / prev_body
    """
    prev_body = abs(prev_k.open - prev_k.close)
    curr_body = abs(curr_k.open - curr_k.close)
    if prev_body == 0:
        return float("inf") if curr_body > 0 else 1.0
    return curr_body / prev_body


# -------------------- 核心信号检测函数 --------------------
def check_bearish_signal(klines, idx):
    """
    做空信号检测
    条件：MA9<MA21 + 高重叠 + 前高阻力 + 前大阳线 + 当前阴线 + 实体比70%-120%
    """
    if idx < LOOKBACK_HIGH + 1:
        return False

    curr = klines.iloc[idx]
    prev = klines.iloc[idx - 1]

    # 1. 均线空头排列
    ma9_series = ma(klines.close, MA_FAST)
    ma21_series = ma(klines.close, MA_SLOW)
    if ma9_series.iloc[idx] >= ma21_series.iloc[idx]:
        return False

    # 2. 实体重叠 ≥ 70%
    if calc_overlap_ratio(prev, curr) < OVERLAP_THRESHOLD:
        return False

    # 3. 前一根K线收盘价是近N周期最高点
    recent_high = klines.high.iloc[idx - LOOKBACK_HIGH:idx].max()
    if prev.close < recent_high:
        return False

    # 4. 前一根K线是大实体
    if not is_big_candle(prev):
        return False

    # 5. 当前K线是阴线
    if not is_bearish(curr):
        return False

    # 6. 实体重叠 70%-120%（前一根K线实体与当前K线实体大小相近且有重叠）
    body_ratio = calc_body_ratio(prev, curr)
    if body_ratio < 0.70 or body_ratio > 1.20:
        return False

    return True


def check_bullish_signal(klines, idx):
    """
    做多信号检测（镜像反转）
    条件：MA9>MA21 + 高重叠 + 前低支撑 + 前大阴线 + 当前阳线 + 实体比70%-120%
    """
    if idx < LOOKBACK_HIGH + 1:
        return False

    curr = klines.iloc[idx]
    prev = klines.iloc[idx - 1]

    # 1. 均线多头排列
    ma9_series = ma(klines.close, MA_FAST)
    ma21_series = ma(klines.close, MA_SLOW)
    if ma9_series.iloc[idx] <= ma21_series.iloc[idx]:
        return False

    # 2. 实体重叠 ≥ 70%
    if calc_overlap_ratio(prev, curr) < OVERLAP_THRESHOLD:
        return False

    # 3. 前一根K线收盘价是近N周期最低点
    recent_low = klines.low.iloc[idx - LOOKBACK_HIGH:idx].min()
    if prev.close > recent_low:
        return False

    # 4. 前一根K线是大实体
    if not is_big_candle(prev):
        return False

    # 5. 当前K线是阳线
    if not is_bullish(curr):
        return False

    # 6. 实体重叠 70%-120%（前一根K线实体与当前K线实体大小相近且有重叠）
    body_ratio = calc_body_ratio(prev, curr)
    if body_ratio < 0.70 or body_ratio > 1.20:
        return False

    return True


# -------------------- tqsdk 回测引擎 --------------------
def _order_is_filled(order) -> bool:
    """判断订单是否已成交。"""
    if order is None:
        return False
    try:
        return str(order.status) == "FINISHED"
    except Exception:
        return False


def _cancel_if_alive(api: TqApi, order) -> None:
    """取消未成交的订单。"""
    if order is None:
        return
    try:
        if str(order.status) == "ALIVE":
            api.cancel_order(order)
    except Exception:
        pass


def run_backtest(symbol: str) -> BacktestResult:
    """使用 tqsdk TqBacktest 对单个合约执行回测，返回 BacktestResult。

    止损止盈采用逐K线手动检查（tqsdk insert_order 不支持 STOP 单）。
    """

    end_dt = date.today()
    start_dt = end_dt - timedelta(days=BACKTEST_DAYS)

    print(f"  [{symbol}] 回测区间: {start_dt} ~ {end_dt}")

    # ---- 创建回测 API ----
    bt = TqBacktest(start_dt=start_dt, end_dt=end_dt)
    api = TqApi(auth=TqAuth(TQ_USERNAME, TQ_PASSWORD), backtest=bt)

    # ---- 订阅行情 ----
    klines = api.get_kline_serial(symbol, DURATION, data_length=DATA_LENGTH)
    quote = api.get_quote(symbol)

    # ---- 预热：等待足够K线数据 ----
    print(f"  [{symbol}] 正在加载K线数据...", end=" ", flush=True)
    min_bars = MA_SLOW + LOOKBACK_HIGH + 3
    while len(klines) < min_bars:
        try:
            api.wait_update()
        except Exception:
            break
    print(f"共 {len(klines)} 根K线", flush=True)
    if len(klines) > 0:
        print(f"  时间范围: {klines.iloc[0].datetime} ~ {klines.iloc[-1].datetime}")

    if len(klines) < min_bars:
        print(f"  [{symbol}] ⚠️ 数据不足（需≥{min_bars}），跳过回测")
        api.close()
        return BacktestResult(symbol=symbol)

    # ---- 回测主循环 ----
    trades: List[Trade] = []

    # 状态机: IDLE → WAITING_ENTRY → IN_POSITION → IDLE
    state = "IDLE"
    entry_order = None
    # 持仓信息
    position: dict = {}     # {direction, entry_time, entry_price, sl, tp}

    # 去重：防止同一根K线重复触发
    last_bar_id = None

    while True:
        try:
            api.wait_update()
        except Exception:
            break

        # 用 is_changing 检测K线更新（与原实时监控代码一致）
        if not api.is_changing(klines.iloc[-1]):
            continue

        n = len(klines)
        if n < min_bars:
            continue

        # 去重：同一根K线只处理一次
        bar_id = klines.iloc[-1].id
        if bar_id == last_bar_id:
            continue
        last_bar_id = bar_id

        # 最新完成K线 = n-2（iloc[-1] 是正在形成的K线）
        idx = n - 2
        curr = klines.iloc[idx]
        next_k = klines.iloc[idx + 1] if idx + 1 < n else curr

        # ============================================================
        # 状态: WAITING_ENTRY — 检查入场单是否成交
        # ============================================================
        if state == "WAITING_ENTRY":
            if _order_is_filled(entry_order):
                # 入场成交，用实际成交价更新（SL/TP 已在信号检测时设定）
                fill_price = float(getattr(entry_order, 'trade_price', 0) or position["entry_price"])
                position["entry_price"] = fill_price
                state = "IN_POSITION"
                entry_order = None

        # ============================================================
        # 状态: IN_POSITION — 逐K线手动检查止损/止盈
        # ============================================================
        elif state == "IN_POSITION":
            pos_dir = position["direction"]
            sl = position["sl"]
            tp = position["tp"]

            exit_now = False
            exit_price = 0.0
            exit_reason = ""

            if pos_dir == "long":
                # 做多：优先止损（同一K线保守处理）
                if next_k.low <= sl:
                    exit_price = sl
                    exit_reason = "stop_loss"
                    exit_now = True
                elif next_k.high >= tp:
                    exit_price = tp
                    exit_reason = "take_profit"
                    exit_now = True
            else:  # short
                if next_k.high >= sl:
                    exit_price = sl
                    exit_reason = "stop_loss"
                    exit_now = True
                elif next_k.low <= tp:
                    exit_price = tp
                    exit_reason = "take_profit"
                    exit_now = True

            if exit_now:
                entry_px = position["entry_price"]
                if pos_dir == "long":
                    pnl = exit_price - entry_px
                else:
                    pnl = entry_px - exit_price

                trade = Trade(
                    symbol=symbol,
                    direction=pos_dir,
                    entry_time=position["entry_time"],
                    entry_price=entry_px,
                    stop_loss=sl,
                    take_profit=tp,
                    exit_time=str(next_k.datetime),
                    exit_price=exit_price,
                    exit_reason=exit_reason,
                    pnl=pnl,
                    pnl_pct=(pnl / entry_px) * 100,
                )
                trades.append(trade)
                state = "IDLE"
                position = {}

        # ============================================================
        # 状态: IDLE — 检测信号，下单入场
        # ============================================================
        if state == "IDLE":
            if check_bullish_signal(klines, idx):
                entry_price = curr.close
                sl_price = curr.low              # 做多止损 = 信号K线最低点
                risk = entry_price - sl_price
                if risk > 0:
                    tp_price = entry_price + RISK_REWARD_RATIO * risk
                    entry_order = api.insert_order(
                        symbol=symbol, direction="BUY", offset="OPEN",
                        volume=1, limit_price=entry_price,
                    )
                    position = {
                        "direction": "long",
                        "entry_time": str(curr.datetime),
                        "entry_price": entry_price,
                        "sl": sl_price,
                        "tp": tp_price,
                    }
                    state = "WAITING_ENTRY"

            elif check_bearish_signal(klines, idx):
                entry_price = curr.close
                sl_price = curr.high             # 做空止损 = 信号K线最高点
                risk = sl_price - entry_price
                if risk > 0:
                    tp_price = entry_price - RISK_REWARD_RATIO * risk
                    entry_order = api.insert_order(
                        symbol=symbol, direction="SELL", offset="OPEN",
                        volume=1, limit_price=entry_price,
                    )
                    position = {
                        "direction": "short",
                        "entry_time": str(curr.datetime),
                        "entry_price": entry_price,
                        "sl": sl_price,
                        "tp": tp_price,
                    }
                    state = "WAITING_ENTRY"

    # ---- 回测结束：清理未平仓 ----
    if state == "IN_POSITION":
        last_k = klines.iloc[-1] if len(klines) > 0 else None
        exit_price = float(last_k.close) if last_k is not None else position.get("entry_price", 0)
        exit_time = str(last_k.datetime) if last_k is not None else ""

        entry_px = position["entry_price"]
        pos_dir = position["direction"]
        if pos_dir == "long":
            pnl = exit_price - entry_px
        else:
            pnl = entry_px - exit_price

        trade = Trade(
            symbol=symbol,
            direction=pos_dir,
            entry_time=position["entry_time"],
            entry_price=entry_px,
            stop_loss=position["sl"],
            take_profit=position["tp"],
            exit_time=exit_time,
            exit_price=exit_price,
            exit_reason="close_out",
            pnl=pnl,
            pnl_pct=(pnl / entry_px) * 100,
        )
        trades.append(trade)
    elif state == "WAITING_ENTRY":
        _cancel_if_alive(api, entry_order)

    api.close()

    # ---- 汇总统计 ----
    result = BacktestResult(symbol=symbol)
    result.total_trades = len(trades)
    result.trades = trades

    if result.total_trades > 0:
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]
        result.winning_trades = len(wins)
        result.losing_trades = len(losses)
        result.win_rate = result.winning_trades / result.total_trades * 100
        result.total_pnl = sum(t.pnl for t in trades)
        result.total_pnl_pct = sum(t.pnl_pct for t in trades)
        result.avg_win = sum(t.pnl_pct for t in wins) / len(wins) if wins else 0.0
        result.avg_loss = sum(t.pnl_pct for t in losses) / len(losses) if losses else 0.0

        total_profit = sum(t.pnl for t in wins) if wins else 0.0
        total_loss = abs(sum(t.pnl for t in losses)) if losses else 0.0
        result.profit_factor = total_profit / total_loss if total_loss > 0 else (float("inf") if total_profit > 0 else 0.0)

        # 最大回撤
        cumulative = 0.0
        peak = 0.0
        max_dd = 0.0
        for t in trades:
            cumulative += t.pnl_pct
            if cumulative > peak:
                peak = cumulative
            dd = peak - cumulative
            if dd > max_dd:
                max_dd = dd
        result.max_drawdown_pct = max_dd

    return result


# -------------------- 输出函数 --------------------
DIR_MAP = {"long": "做多", "short": "做空"}
REASON_MAP = {"stop_loss": "止损", "take_profit": "止盈", "close_out": "收盘平仓"}


def print_trade_detail(t: Trade, i: int):
    """打印单笔交易明细"""
    tag = "✅" if t.pnl > 0 else "❌"
    print(f"  {tag} #{i} {DIR_MAP.get(t.direction, t.direction)} | "
          f"入场: {t.entry_time} @ {t.entry_price:.2f} | "
          f"离场: {t.exit_time} @ {t.exit_price:.2f} | "
          f"原因: {REASON_MAP.get(t.exit_reason, t.exit_reason)} | "
          f"盈亏: {t.pnl:+.2f} ({t.pnl_pct:+.2f}%)")


def print_result(result: BacktestResult):
    """打印单合约回测结果"""
    print()
    print("=" * 80)
    print(f"  📊 {result.symbol} 回测报告")
    print("=" * 80)
    print(f"  总交易次数: {result.total_trades}")
    if result.total_trades == 0:
        print("  无交易信号，跳过详细统计")
        return

    print(f"  盈利次数:   {result.winning_trades}  |  亏损次数: {result.losing_trades}")
    print(f"  胜率:       {result.win_rate:.1f}%")
    print(f"  总盈亏:      {result.total_pnl:+.2f}  ({result.total_pnl_pct:+.2f}%)")
    print(f"  平均盈利:    {result.avg_win:+.2f}%  |  平均亏损: {result.avg_loss:+.2f}%")
    if result.avg_loss != 0:
        print(f"  盈亏比(实际): {abs(result.avg_win / result.avg_loss):.2f}")
    print(f"  盈亏因子:    {result.profit_factor:.2f}")
    print(f"  最大回撤:    {result.max_drawdown_pct:.2f}%")
    print("-" * 80)
    print(f"  交易明细:")
    for i, t in enumerate(result.trades, 1):
        print_trade_detail(t, i)
    print("-" * 80)


def print_summary(results: List[BacktestResult]):
    """打印所有合约汇总"""
    if len(results) <= 1:
        return

    print()
    print("=" * 80)
    print("  📋 多合约汇总")
    print("=" * 80)
    print(f"  {'合约':<22} {'交易':>4} {'胜率':>7} {'总盈亏%':>9} {'盈亏因子':>8} {'最大回撤%':>9}")
    print("  " + "-" * 65)
    total_trades = 0
    total_wins = 0
    total_pnl = 0.0
    for r in results:
        if r.total_trades == 0:
            print(f"  {r.symbol:<22} {'—':>4} {'—':>7} {'—':>9} {'—':>8} {'—':>9}")
        else:
            print(f"  {r.symbol:<22} {r.total_trades:>4} {r.win_rate:>6.1f}% {r.total_pnl_pct:>+8.2f}% {r.profit_factor:>8.2f} {r.max_drawdown_pct:>8.2f}%")
            total_trades += r.total_trades
            total_wins += r.winning_trades
            total_pnl += r.total_pnl
    print("  " + "-" * 65)
    overall_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
    print(f"  {'合计':<22} {total_trades:>4} {overall_wr:>6.1f}% {total_pnl:>+9.2f}")
    print("=" * 80)


# -------------------- 主程序 --------------------
def main():
    end_dt = date.today()
    start_dt = end_dt - timedelta(days=BACKTEST_DAYS)

    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║       商品期货 K线形态回测系统 (tqsdk TqBacktest)          ║")
    print(f"╠══════════════════════════════════════════════════════════════╣")
    print(f"║  回测区间: {start_dt} ~ {end_dt}                     ║")
    print(f"║  K线周期: {DURATION}秒  |  盈亏比: 1:{RISK_REWARD_RATIO:.1f}  "
         f"|  回测天数: {BACKTEST_DAYS}天               ║")
    print(f"║  快均线: MA{MA_FAST}  |  慢均线: MA{MA_SLOW}  |  回溯: {LOOKBACK_HIGH}周期  "
         f"|  重叠阈值: {OVERLAP_THRESHOLD*100:.0f}%        ║")
    print(f"║  合约数量: {len(SYMBOLS)}                                           ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")

    results: List[BacktestResult] = []

    for symbol in SYMBOLS:
        try:
            result = run_backtest(symbol)
            results.append(result)
            print_result(result)
        except Exception as e:
            print(f"\n  [{symbol}] ❌ 回测异常: {e}")
            import traceback
            traceback.print_exc()

    print_summary(results)
    print("\n回测完成。")


if __name__ == "__main__":
    main()
