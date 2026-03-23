"""
Function to request the loan amount and returns the same value
"""
def req_loan_amount():
    amount = 0  # Initialise variable to start while loop
    while amount == 0:
        try:
            amount = int(input("Loan Amount: $"))
        except ValueError:
            print("Error: Loan Amount must be an integer!")
        else:
            return amount

"""
Function to request the loan period and returns the same value
"""
def req_loan_period():
    period = 0  # Initialise variable to start while loop
    while period == 0:
        try:
            period = int(input("Loan period (years): "))
        except ValueError:
            print("Error: Loan Period must be an integer!")
        else:
            return period

"""
Function to request the interest rate and returns the same value
"""
def req_interest_rate():
    interest = 0  # Initialise variable to start while loop
    while interest == 0:
        try:
            interest = float(input("Interest Rate (% p.a.): "))
        except ValueError:
            print("Error: Interest Rate must be a floating point!")
        else:
            return interest / 100   # Convert from %

"""
Function to calculate the monthly repayments
"""
def calc_repayments(principal,period_y,interest_y):
    # normalise the values from annually to monthly
    period_m = period_y * 12
    interest_m = interest_y / 12

    # Formula for monthly replayments
    repayment_m = round((principal * interest_m * (1 + interest_m) ** period_m) / ((1 + interest_m) ** period_m - 1),2)
    return repayment_m

"""
Main function - only runs when executed directly and not when imported
"""
def main():
    loan_amount = req_loan_amount()
    loan_period = req_loan_period()
    interest_rate = req_interest_rate()
    monthly_repayments = calc_repayments(loan_amount,loan_period,interest_rate)
    print(f"Monthly repayment: ${monthly_repayments}")

if __name__ == "__main__":
    main()