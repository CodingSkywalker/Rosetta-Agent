def calculate_checkout(price, tax_rate):
    tax_amount = price * (tax_rate / 100)
    total = price + tax_amount
    return total # Changed from 'Total' to 'total'

print("Calculating final price...")
final_price = calculate_checkout(100, 5)
print(f"Final price: ${final_price:.2f}")