def calculate_checkout(price, tax):
    print("Calculating final price...")
    total = price + tax
    
    # This will crash the program: 'Total' is not defined!
    return Total 

if __name__ == "__main__":
    final_price = calculate_checkout(100, 5)
    print(f"Success: {final_price}")