export function formatCurrency(value: string | number, currency: string = "₹", decimals: number = 2): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return `${currency}0.00`;
  return `${currency}${num.toLocaleString("en-IN", { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
}

export function formatPercent(value: string | number, decimals: number = 2): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "0.00%";
  return `${num >= 0 ? "+" : ""}${num.toFixed(decimals)}%`;
}

export function formatNumber(value: string | number, decimals: number = 0): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "0";
  return num.toLocaleString("en-IN", { maximumFractionDigits: decimals });
}
