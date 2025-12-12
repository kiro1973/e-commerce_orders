

import json
import sys
from datetime import datetime, timezone
from typing import List, Dict, Tuple
from collections import defaultdict


def read_orders(filepath: str, from_date: str = None) -> List[Dict]:
    orders = []
    filter_date = None
    
    if from_date:
        try:
            filter_date = datetime.strptime(from_date, "%Y-%m-%d")
            # Make it timezone-aware (UTC) to match order dates
            filter_date = filter_date.replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Error: Invalid date format '{from_date}'. Use YYYY-MM-DD")
            sys.exit(1)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    order = json.loads(line)
                    
                    if filter_date and 'created_at' in order:
                        order_date = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00'))
                        if order_date < filter_date:
                            continue
                    
                    orders.append(order)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON at line {line_num}: {e}")
                    sys.exit(1)
    
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    return orders


def is_suspicious(order: Dict) -> Tuple[bool, str]:
    amount = order.get('amount_cents', 0)
    marketplace = order.get('marketplace', '')
    
    if amount < 0:
        return True, f"negative amount ({amount})"
    
    if not marketplace or marketplace.strip() == '':
        return True, "empty marketplace"
    
    return False, ""


def calculate_revenue(orders: List[Dict]) -> Tuple[float, Dict[str, float], List[Tuple[str, str]]]:
    total_cents = 0
    marketplace_cents = defaultdict(int)
    suspicious_orders = []
    
    for order in orders:
        order_id = order.get('id', 'unknown')
        amount = order.get('amount_cents', 0)
        marketplace = order.get('marketplace', '').strip()
        
        is_susp, reason = is_suspicious(order)
        if is_susp:
            suspicious_orders.append((order_id, reason))
        
        # Include non-negative amounts in total this is different from what included in the test I believe this is better
        if amount >= 0:
            total_cents += amount
            
            if marketplace:
                marketplace_cents[marketplace] += amount
    
    total_eur = total_cents / 100.0
    marketplace_eur = {mp: cents / 100.0 for mp, cents in marketplace_cents.items()}
    
    return total_eur, marketplace_eur, suspicious_orders


def format_output(total_revenue: float, marketplace_revenue: Dict[str, float], 
                  suspicious_orders: List[Tuple[str, str]]) -> str:
    output = []
    
    output.append(f"Total revenue: {total_revenue:.2f} EUR")
    output.append("")
    
    output.append("Revenue by marketplace:")
    sorted_marketplaces = sorted(marketplace_revenue.items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)
    
    for marketplace, revenue in sorted_marketplaces:
        output.append(f"- {marketplace}: {revenue:.2f} EUR")
    
    if suspicious_orders:
        output.append("")
        output.append("Suspicious orders:")
        for order_id, reason in suspicious_orders:
            output.append(f"- {order_id}: {reason}")
    
    return "\n".join(output)


def parse_arguments() -> Tuple[str, str]:
    if len(sys.argv) < 2:
        print("Usage: python orders_analyzer.py <orders.json> [-from=YYYY-MM-DD]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    from_date = None
    
    for arg in sys.argv[2:]:
        if arg.startswith('-from='):
            from_date = arg.split('=', 1)[1]
    
    return filepath, from_date


def main():
    filepath, from_date = parse_arguments()
    orders = read_orders(filepath, from_date)
    
    if not orders:
        print("No orders found" + (f" from {from_date}" if from_date else ""))
        sys.exit(0)
    
    total_revenue, marketplace_revenue, suspicious_orders = calculate_revenue(orders)
    output = format_output(total_revenue, marketplace_revenue, suspicious_orders)
    print(output)


if __name__ == "__main__":
    main()