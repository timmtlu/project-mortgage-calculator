"""
MORTGAGE CALCULATOR
Calculates the monthly repayments of a fixed term mortgage over a period at a specific interest rate.

Inputs:
- Loan amount ($)
- Loan period (years)
- Interest rate (% p.a.)

Output:
- Monthly repayment

Author:     Tim Lu
Date:       24 March 2026
Version:    1.0.2
"""

"""
Define font styling constants
"""
BOLD       = "\033[1m"
ITALIC     = "\033[3m"
RED        = "\033[31m"
GREEN      = "\033[32m"
CYAN       = "\033[36m"
RESET      = "\033[0m"


"""
Function to request the loan amount and returns the same value
"""
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
def req_loan_amount():
    amount = 0  # Initialise variable to be used in while loop
    while amount == 0:
        try:
            raw_amount = input(f"{CYAN}Loan Amount: ${RESET}")
            amount = int(raw_amount.replace(",", ""))  # Strip commas before converting
            if amount <= 0:
                raise ValueError
        except ValueError:
            print("Error: Loan Amount must be a positive integer!")
        else:
            print(f"{CYAN}Loan Amount entered: ${RESET}{GREEN}{ITALIC}{amount:,}{RESET}")  # Echo back with formatting
            return amount

"""
Function to request the loan period and returns the same value
"""
def req_loan_period():
    period = 0  # Initialise variable to start while loop
    while period == 0:
        try:
            period = int(input(f"{CYAN}Loan Period (years):{RESET} "))
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
            interest = float(input(f"{CYAN}Interest Rate (% p.a.):{RESET} "))
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
    print(f"\n{BOLD}USER INPUT{RESET}")
    loan_amount = req_loan_amount()
    loan_period = req_loan_period()
    interest_rate = req_interest_rate()
    monthly_repayments = calc_repayments(loan_amount,loan_period,interest_rate)
    print(f"\n{BOLD}{CYAN}Monthly repayment: ${GREEN}{ITALIC}{monthly_repayments:,}{RESET}")

if __name__ == "__main__":
    main()