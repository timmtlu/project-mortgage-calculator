"""
MORTGAGE CALCULATOR
Calculates the monthly repayments of a fixed term mortgage over a period at a specific interest rate.

Inputs:
- Loan amount ($)
- Loan term (years)
- Interest rate (% p.a.)
- Offset amount ($)

Output:
- Monthly repayment ($)
- Amortisation schedule
- Loan term with offset (years + months)

Author:     Tim Lu
Date:       02 April 2026
Version:    1.2.1
"""


# ── Import ───────────────────────────────────────
import math


# ── Constants ───────────────────────────────────────
# Define font styling constants
BOLD       = "\033[1m"
ITALIC     = "\033[3m"
RED        = "\033[31m"
GREEN      = "\033[32m"
CYAN       = "\033[36m"
RESET      = "\033[0m"


# ── Functions ───────────────────────────────────────
def req_loan_amount():
    """Request user to input the loan amount.

    Returns:
        amount (int): Loan amount in dollars
    """
    amount = 0  # Initialise variable to be used in while loop
    while amount == 0:

        try:
            raw_amount = input(f"{CYAN}Loan Amount: ${RESET}")
            amount = int(raw_amount.replace(",", ""))  # Strip commas before converting

            # Raise error if not positive
            if amount <= 0:
                raise ValueError
        except ValueError:
            print("Error: Loan Amount must be a positive integer!")
        else:
            print(f"{CYAN}Loan Amount entered: ${RESET}{GREEN}{ITALIC}{amount:,.2f}{RESET}")  # Echo back with formatting
            return amount


def req_loan_period():
    """Request user to input the loan period.

    Returns:
        period (int): Loan term in years
    """
    period = 0  # Initialise variable to start while loop
    while period == 0:
        try:
            period = int(input(f"{CYAN}Loan Period (years):{RESET} "))
        except ValueError:
            print("Error: Loan Period must be an integer!")
        else:
            return period


def req_interest_rate():
    """Request user to input the annual interest rate.

    Returns:
        interest / 100 (float): Annual interest rate in decimal (not percentage)
    """
    interest = 0  # Initialise variable to start while loop
    while interest == 0:
        try:
            interest = float(input(f"{CYAN}Interest Rate (% p.a.):{RESET} "))
        except ValueError:
            print("Error: Interest Rate must be floating point!")
        else:
            return interest / 100  # Convert from %


def req_offset_amount():
    """Request user to input the amount in the offset account, if any

    Returns:
         offset (float): Offset amount in dollars
    """
    offset = 0  # Initialise variable to start while loop
    while offset == 0:
        try:
            offset = float(input(f"{CYAN}Offset Amount: ${RESET} "))
        except ValueError:
            print("Error: Offset Amount must be floating point!")
        else:
            print(f"{CYAN}Offset Amount entered: ${RESET}{GREEN}{ITALIC}{offset:,.2f}{RESET}")  # Echo back with formatting
            return offset

def calc_repayments(amount,period_y,interest_y):
    """Calculate the monthly repayments.

    Args:
        amount (int): Loan amount in dollars
        period_y (int): Loan term in years
        interest_y (float): Annual interest rate in decimal (not percentage)

    Returns:
        repayment_m (float): Monthly repayments in dollars (rounded to 2 decimal points)
        period_m (int): Loan term in months
        interest_m (float): Monthly interest rate in decimal (not percentage)
    """
    # Normalise the values from annually to monthly
    period_m = period_y * 12
    interest_m = interest_y / 12

    # Formula for monthly repayments
    repayment_m = round((amount * interest_m * (1 + interest_m) ** period_m) / ((1 + interest_m) ** period_m - 1),2)
    return repayment_m, period_m, interest_m


def calc_offset(amount,repayment_m,interest_m,offset):
    """Calculate the new loan term when offset is considered, monthly repayments are the same.

    Args:
        amount (int): Loan amount in dollars
        repayment_m (float): Monthly repayments in dollars (rounded to 2 decimal points)
        interest_m (float): Monthly interest rate in decimal (not percentage)
        offset (float): Offset amount in dollars

    Returns:
        offset_period_m (int): Loan term in months when taking into account offset
    """

    # Formula for loan term in months with offset
    offset_period_m = math.log(repayment_m / (repayment_m - (amount - offset) * interest_m)) / math.log(1 + interest_m)
    offset_period_m = math.ceil(offset_period_m)  # round up to the closest integer
    return offset_period_m


def calc_amortisation(amount,repayment_m,period_m,interest_m):
    """Calculate the amortisation schedule which is a table showing each payment including the principal and interest.

    Args:
        amount (int): Loan amount in dollars
        repayment_m (float): Monthly repayments in dollars (rounded to 2 decimal points)
        period_m (int): Loan term in months
        interest_m (float): Monthly interest rate in decimal (not percentage)

    Returns:
        schedule (list[dict]): Amortisation schedule consisting of Interest this payment, Principal this payment, Interest to date, Principal to date, Principal remaining for each month
    """
    schedule = []  # Initialise list for amortisation schedule
    balance = amount  # Current balance of principal
    total_interest = 0  # Total interest paid to date
    total_principal = 0  # Total principal paid to date

    # Append dictionary into list before payment starts (month 0)
    schedule.append({
        "Month": 0,
        "Interest This Payment": 0.00,
        "Principal This Payment": 0.00,
        "Interest To Date": 0.00,
        "Principal To Date": 0.00,
        "Principal Remaining": round(balance, 2)
    })

    # Calculate for each month - Interest this payment, Principal this payment, Interest to date, Principal to date, Principal remaining
    for month in range(1,period_m+1):
        interest_payment = balance * interest_m
        principal_payment = repayment_m - interest_payment
        total_interest += interest_payment
        total_principal += principal_payment
        balance -= principal_payment

        # Append dictionary into list for each month
        schedule.append({
            "Month": month,
            "Interest This Payment": round(interest_payment,2),
            "Principal This Payment": round(principal_payment,2),
            "Interest To Date": round(total_interest,2),
            "Principal To Date": min(round(total_principal,2), amount),  # To account for rounding errors for the last month
            "Principal Remaining": max(round(balance,2), 0.00)  # To account for rounding errors for the last month
        })

    return schedule


def display_amortisation(schedule):
    """Display the amortisation schedule in a table

    Args:
        schedule (list[dict]): Amortisation schedule consisting of Interest this payment, Principal this payment, Interest to date, Principal to date, Principal remaining for each month
    """
    # Print the labels and separation line, Labels are left-aligned which is standard for financial tables
    print(f"\n{'MONTH':<8} {'INTEREST THIS PAYMENT ($)':<28} {'PRINCIPAL THIS PAYMENT ($)':<29} {'INTEREST TO DATE ($)':<23} {'PRINCIPAL TO DATE ($)':<24} {'PRINCIPAL REMAINING ($)':<23}")
    print("-" * 140)

    # Numbers are right-aligned which is standard for financial tables
    for row in schedule:
        print(f"{row['Month']:<5}   {row['Interest This Payment']:>26,.2f}   {row['Principal This Payment']:>27,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Principal Remaining']:>24,.2f}")


def main():
    """Main function - only runs when executed directly and not when imported"""
    print(f"\n{BOLD}USER INPUTS:{RESET}")
    loan_amount = req_loan_amount()
    loan_period = req_loan_period()
    annual_rate = req_interest_rate()
    offset_amount = req_offset_amount()
    monthly_repayments, monthly_period, monthly_interest = calc_repayments(loan_amount,loan_period,annual_rate)
    offset_period = calc_offset(loan_amount, monthly_repayments, monthly_interest, offset_amount)
    amor_schedule = calc_amortisation(loan_amount, monthly_repayments, offset_period, monthly_interest)
    print(f"\n{BOLD}OUTPUTS:{RESET}")
    print(f"{CYAN}Monthly repayment: ${GREEN}{ITALIC}{monthly_repayments:,.2f}{RESET}")
    print(f"{CYAN}Loan term with offset: {GREEN}{ITALIC}{offset_period // 12} years & {offset_period % 12} months{RESET}")
    display_amortisation(amor_schedule)


# ── Main ───────────────────────────────────────
if __name__ == "__main__":
    main()