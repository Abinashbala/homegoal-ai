export function formatCurrency(amount: number, currency: 'INR' | 'AED' = 'INR'): string {
  if (currency === 'INR') {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)} Cr`;
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(2)} Lakh`;
    }
    return `₹${amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  } else {
    return `AED ${amount.toLocaleString('en-AE', { maximumFractionDigits: 0 })}`;
  }
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}
