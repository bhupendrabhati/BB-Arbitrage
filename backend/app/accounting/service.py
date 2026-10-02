from decimal import Decimal
from datetime import datetime, timezone
from app.core.logging import get_logger
from app.utils.helpers import export_trades_csv, export_trades_json

logger = get_logger("accounting")


class AccountingService:
    def __init__(self):
        self.tax_records: list[dict] = []

    def record_trade(self, trade: dict) -> None:
        record = {
            "trade_id": trade.get("id", ""),
            "timestamp": trade.get("created_at", datetime.now(timezone.utc).isoformat()),
            "asset": trade.get("symbol", "").split("/")[0] if "/" in trade.get("symbol", "") else "",
            "quantity": trade.get("quantity", "0"),
            "buy_price": trade.get("buy_price", "0"),
            "sell_price": trade.get("sell_price", "0"),
            "fees": str(Decimal(trade.get("buy_fee", "0")) + Decimal(trade.get("sell_fee", "0"))),
            "gross_profit": trade.get("gross_profit", "0"),
            "net_profit": trade.get("net_profit", "0"),
            "exchange": f"{trade.get('buy_exchange', '')}/{trade.get('sell_exchange', '')}",
            "mode": trade.get("mode", "paper"),
        }
        self.tax_records.append(record)
        logger.info("tax_record_created", trade_id=record["trade_id"])

    def export_csv(self) -> str:
        return export_trades_csv(self.tax_records)

    def export_json(self) -> str:
        return export_trades_json(self.tax_records)

    def get_records(self, limit: int = 100) -> list[dict]:
        return self.tax_records[-limit:]

    def get_summary(self) -> dict:
        total_pnl = sum(Decimal(r.get("net_profit", "0")) for r in self.tax_records)
        total_fees = sum(Decimal(r.get("fees", "0")) for r in self.tax_records)
        return {
            "total_trades": len(self.tax_records),
            "total_pnl": str(total_pnl),
            "total_fees": str(total_fees),
        }


accounting_service = AccountingService()
