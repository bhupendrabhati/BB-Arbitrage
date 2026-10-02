class ArbitrageError(Exception):
    pass


class InsufficientLiquidityError(ArbitrageError):
    pass


class StaleMarketDataError(ArbitrageError):
    pass


class RiskLimitExceededError(ArbitrageError):
    pass


class ExchangeUnavailableError(ArbitrageError):
    pass


class OrderExecutionError(ArbitrageError):
    pass


class KillSwitchActiveError(ArbitrageError):
    pass


class UnknownOrderStateError(ArbitrageError):
    pass
