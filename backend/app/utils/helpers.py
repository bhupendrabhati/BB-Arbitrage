import csv
import io
import json
from decimal import Decimal
from datetime import datetime, timezone
from typing import Any


def decimal_to_str(value: Decimal) -> str:
    return str(value)


def str_to_decimal(value: str) -> Decimal:
    return Decimal(value)


def format_timestamp(dt: datetime) -> str:
    return dt.isoformat()


def parse_timestamp(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def export_trades_csv(trades: list[dict]) -> str:
    if not trades:
        return ""

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=trades[0].keys())
    writer.writeheader()
    writer.writerows(trades)
    return output.getvalue()


def export_trades_json(trades: list[dict]) -> str:
    return json.dumps(trades, indent=2, default=str)


def calculate_win_rate(winning: int, total: int) -> Decimal:
    if total == 0:
        return Decimal("0")
    return (Decimal(str(winning)) / Decimal(str(total))) * 100


def calculate_drawdown(current: Decimal, peak: Decimal) -> Decimal:
    if peak == 0:
        return Decimal("0")
    return ((peak - current) / peak) * 100


def sanitize_for_log(data: dict) -> dict:
    sensitive_keys = {"api_key", "api_secret", "password", "token", "secret"}
    return {k: "***" if any(s in k.lower() for s in sensitive_keys) else v for k, v in data.items()}
