"""
MORTGAGE CALCULATOR
Calculates the monthly repayments of a fixed term mortgage over a period at a specific interest rate.

Inputs:
- Loan amount ($)
- Loan term (years)
- Interest rate (% p.a.)
- Repayment frequency - Monthly (default), fortnightly, or weekly
- Offset amount ($)
- Additional repayments ($)

Output:
- Monthly repayment ($)
- Amortisation schedule
- New loan term with offset and additional repayments

Author:     Tim Lu
Date:       16 April 2026
Version:    1.4.0
"""


# ── Import ───────────────────────────────────────
import math  # Required to round up


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
                amount = 0
                raise ValueError("Loan Amount cannot be negative!")
            elif 0 < amount < 30000:
                amount = 0
                raise ValueError("Loan amount must be at least $30,000!")
        except ValueError as e:
            if "invalid literal" in str(e):
                amount = 0
                print("Error: Interest Rate must be an integer!")
            else:
                print(f"Error: {e}")
        else:
            print(f"\r{CYAN}Loan Amount entered: ${RESET}{GREEN}{ITALIC}{amount:,.2f}{RESET}")  # Echo back with formatting
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
            if period < 0:
                period = 0
                raise ValueError("Loan Period cannot be negative!")
        except ValueError as e:
            if "invalid literal" in str(e):
                period = 0
                print("Error: Loan Period must be an integer!")
            else:
                print(f"Error: {e}")
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
            if interest < 0:
                interest = 0
                raise ValueError("Interest Rate cannot be negative!")
        except ValueError as e:
            if "could not convert" in str(e):
                interest = 0
                print("Error: Interest Rate must be floating point!")
            else:
                print(f"Error: {e}")
        else:
            return interest / 100  # Convert from %


def req_frequency():
    """Request user to select repayment frequency - Monthly (default), fortnightly, or weekly

    Returns:
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
    """
    frequency = 0  # Initialise variable to start while loop
    while frequency not in ['M','m','Monthly','monthly','','F', 'f', 'Fortnightly', 'fortnightly','W', 'w', 'Weekly', 'weekly']:
        try:
            frequency = input(f"{CYAN}Select Repayment Frequency (Monthly - M/Fortnightly - F/Weekly - W):{RESET} ")
            if frequency in ['M','m','Monthly','monthly','']:
                frequency = 'm'  # Pressing enter is equivalent to choosing default monthly
            elif frequency in ['F', 'f', 'Fortnightly', 'fortnightly']:
                frequency = 'f'
            elif frequency in ['W', 'w', 'Weekly', 'weekly']:
                frequency = 'w'
            else:
                raise Exception("Repayment Frequency must be 'M', 'F', or 'W'!")
        except Exception as e:
            print(f"Error: {e}")
        else:
            return frequency


def req_additional_repayments():
    """Request user to input the additional monthly/fortnightly/weekly (depending on selected interval) repayment amount, if any. Default is 0.

    Returns:
         extra (float): Additional repayment amount every repayment cycle in dollars
    """
    raw = "True"  # Initialise variable to start while loop
    while raw == "True":
        try:
            raw = input(f"{CYAN}Additional Repayment Amount (goes into offset): ${RESET} ")
            if raw == "":
                extra = 0.00  # Pressing enter is equivalent to zero
            else:
                extra = float(raw)
                if extra < 0:
                    raw = "True"
                    raise ValueError("Additional Repayment Amount cannot be negative!")
        except ValueError as e:
            if "could not convert" in str(e):
                raw = "True"
                print("Error: Additional Repayment Amount must be a integer/floating number!")
            else:
                print(f"Error: {e}")
        else:
            print(f"{CYAN}Additional Repayment Amount entered: ${RESET}{GREEN}{ITALIC}{extra:,.2f}{RESET}")  # Echo back with formatting
            return extra


def req_offset_amount():
    """Request user to input the amount in the offset account, if any

    Returns:
         offset (float): Offset amount in dollars
    """
    raw = "True"  # Initialise variable to start while loop
    while raw == "True":
        try:
            raw = input(f"{CYAN}Offset Amount: ${RESET} ")
            if raw == "":
                offset = 0.00  # Pressing enter is equivalent to zero
            else:
                offset = float(raw)
                if offset < 0:
                    raw = "True"
                    raise ValueError("Offset Amount cannot be negative!")
        except ValueError as e:
            if "could not convert" in str(e):
                raw = "True"
                print("Error: Offset Amount must be a integer/floating number!")
            else:
                print(f"Error: {e}")
        else:
            print(f"{CYAN}Offset Amount entered: ${RESET}{GREEN}{ITALIC}{offset:,.2f}{RESET}")  # Echo back with formatting
            return offset


def calc_repayment(amount,period_y,interest_y,frequency):
    """Calculate the monthly/fortnightly/weekly repayments.

    Args:
        amount (int): Loan amount in dollars
        period_y (int): Loan term in years
        interest_y (float): Annual interest rate in decimal (not percentage)
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly

    Returns:
        repayment_n (float): Monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        period_n (int): Loan term in months/fortnights/weeks
        interest_n (float): Monthly/fortnightly/weekly interest rate in decimal (not percentage)
    """
    # For monthly repayments
    if frequency == 'm':
        # Normalise the values from annually to monthly
        period_n = period_y * 12
        interest_n = interest_y / 12

        # Formula for monthly repayments
        repayment_n = round((amount * interest_n * (1 + interest_n) ** period_n) / ((1 + interest_n) ** period_n - 1),2)

        return repayment_n, period_n, interest_n

    # For fortnightly repayments
    if frequency == 'f':
        # Normalise the values from annually to fortnightly
        period_n = period_y * 26
        interest_n = interest_y / 26

        # Formula for fortnightly repayments
        repayment_n = round((amount * interest_n * (1 + interest_n) ** period_n) / ((1 + interest_n) ** period_n - 1),2)

        return repayment_n, period_n, interest_n

    # For weekly repayments
    if frequency == 'w':
        # Normalise the values from annually to weekly
        period_n = period_y * 52
        interest_n = interest_y / 52

        # Formula for weekly repayments
        repayment_n = round((amount * interest_n * (1 + interest_n) ** period_n) / ((1 + interest_n) ** period_n - 1),2)

        return repayment_n, period_n, interest_n


def display_repayment(repayment_n,frequency):
    """Display the monthly/fortnightly/weekly repayments.

    Args:
        repayment_n (float): Monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
    """
    # Convert frequency flag to string
    interval = ""
    if frequency == 'm':
        interval = "Monthly"
    elif frequency == 'f':
        interval = "Fortnightly"
    elif frequency == 'w':
        interval = "Weekly"
    print(f"{CYAN}{interval} Repayment (exc. additional repayment): ${GREEN}{ITALIC}{repayment_n:,.2f}{RESET}")


def calc_loan_term(amount,repayment_n,period_n,interest_n,offset):
    """Calculate the new loan term when offset is considered, monthly repayments are the same.

    Args:
        amount (int): Loan amount in dollars
        repayment_n (float): Monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        period_n (int): Loan term in months/fortnights/weeks
        interest_n (float): Monthly/fortnightly/weekly interest rate in decimal (not percentage)
        offset (float): Offset amount in dollars

    Returns:
        new_period_n (int): Loan term in months when taking into account offset
    """
    # Offset amount equal to loan amount reduces interest to zero, therefore any additional offset beyond loan amount is meaningless
    if offset > amount:
        offset = amount

    # Formula for loan term in months with offset
    new_period_n = math.log(repayment_n / (repayment_n - (amount - offset) * interest_n)) / math.log(1 + interest_n)
    new_period_n = min(math.ceil(new_period_n),period_n)  # round up to the closest integer or use original loan term, whichever is smaller

    return new_period_n


def display_term(period_n,frequency):
    """Display the updated loan term after taking into account the offset amount and additional repayments.

    Args:
        period_n (int): Loan term in months/fortnights/weeks
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
    """
    # Display messages for different repayment frequencies
    if frequency == 'm':
        print(f"{CYAN}Loan term with offset and additional repayments: {GREEN}{ITALIC}{period_n // 12} years & {period_n % 12} months ({period_n} months){RESET}")
    elif frequency == 'f':
        print(f"{CYAN}Loan term with offset and additional repayments: {GREEN}{ITALIC}{period_n // 26} years & {period_n % 26} fortnights ({period_n} fortnights){RESET}")
    elif frequency == 'w':
        print(f"{CYAN}Loan term with offset and additional repayments: {GREEN}{ITALIC}{period_n // 52} years & {period_n % 52} weeks ({period_n} weeks){RESET}")


def calc_amortisation(amount,repayment_n,period_n,interest_n,offset,frequency,extra):
    """Calculate the amortisation schedule which is a table showing each payment including the principal and interest.

    Args:
        amount (int): Loan amount in dollars
        repayment_n (float): Monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        period_n (int): Loan term in months/fortnights/weeks
        interest_n (float): Monthly/fortnightly/weekly interest rate in decimal (not percentage)
        offset (float): Offset amount in dollars
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
        extra (float): Additional repayment amount every repayment cycle in dollars

    Returns:
        schedule (list[dict]): Amortisation schedule consisting of Interest this payment, Principal this payment, Interest to date, Principal to date, Principal remaining for each month
        period_n (int): Updated loan term (including paying off principal in offset) in months
        final_interest (int): Final month paying interest, this row will be highlighted
    """
    # Offset amount equal to loan amount reduces interest to zero, therefore any additional offset beyond loan amount is meaningless
    if offset > amount:
        offset = amount

    schedule = []  # Initialise list for amortisation schedule
    payable_balance = amount - offset  # Current balance of principal owing interest
    total_balance = amount  # Current balance of principal including amount in offset
    total_interest = 0  # Total interest paid to date
    total_principal = 0  # Total principal paid to date
    index = 0  # Loan term index
    final_interest = 0  # Flag for final index paying interest
    label = 0  # Index label for repayment frequency

    # Different index label for different repayment frequencies
    if frequency == 'm':
        label = "Month"
    elif frequency == 'f':
        label = "Fortnight"
    elif frequency == 'w':
        label = "Week"

    # Append dictionary into list before payment starts (index 0)
    schedule.append({
        label: index,
        "Interest This Payment": 0.00,
        "Principal This Payment": 0.00,
        "Extra This Payment": 0.00,
        "Interest To Date": 0.00,
        "Principal To Date": 0.00,
        "Interest Payable Loan Balance": round(payable_balance, 2),
        "Total Loan Balance": round(amount, 2)
    })

    index += 1

    # Note that additional repayments will sit in the offset account and therefore contributes only to the principal and not the interest
    # Calculate for each repayment frequency - Interest this payment, Principal this payment, Interest to date, Principal to date, Interest Payable Loan Balance, Total Loan Balance
    while repayment_n + extra <= (payable_balance + payable_balance * interest_n):
        interest_payment = payable_balance * interest_n
        principal_payment = repayment_n - interest_payment
        total_interest += interest_payment
        total_principal += principal_payment + extra
        payable_balance -= principal_payment + extra
        total_balance -= principal_payment + extra

        # Append dictionary into list for each repayment frequency
        schedule.append({
            label: index,
            "Interest This Payment": round(interest_payment,2),
            "Principal This Payment": round(principal_payment,2),
            "Extra This Payment": round(extra,2),
            "Interest To Date": round(total_interest,2),
            "Principal To Date": round(total_principal,2),
            "Interest Payable Loan Balance": round(payable_balance,2),
            "Total Loan Balance": round(total_balance,2)
        })

        index += 1

    # Calculation for the final repayment frequency with interest
    while repayment_n + extra > payable_balance > 0:
        interest_payment = payable_balance * interest_n
        principal_payment = repayment_n - interest_payment
        total_interest += interest_payment
        total_principal += principal_payment + extra
        total_balance -= principal_payment + extra  # First (partial) payment on principal in offset
        payable_balance = 0  # Paid off all principal that charges interest
        final_interest = index  # Flag the final repayment frequency paying interest

        schedule.append({
            label: index,
            "Interest This Payment": round(interest_payment,2),
            "Principal This Payment": round(principal_payment,2),
            "Extra This Payment": round(extra, 2),
            "Interest To Date": round(total_interest,2),
            "Principal To Date": round(total_principal,2),
            "Interest Payable Loan Balance": round(payable_balance,2),  # To account for rounding errors for the last repayment frequency
            "Total Loan Balance": round(total_balance,2)
        })

        index += 1

    # Calculation for the repayment frequencies with no interest
    while payable_balance == 0 and repayment_n + extra < total_balance:
        principal_payment = repayment_n
        total_principal += principal_payment + extra
        payable_balance = 0  # Paid off all principal that charges interest
        total_balance -= principal_payment + extra  # Entire repayment goes to pay the principal in offset

        schedule.append({
            label: index,
            "Interest This Payment": 0.00,
            "Principal This Payment": round(principal_payment,2),
            "Extra This Payment": round(extra, 2),
            "Interest To Date": round(total_interest,2),
            "Principal To Date": round(total_principal,2),
            "Interest Payable Loan Balance": 0.00,
            "Total Loan Balance": round(total_balance,2)
        })

        index += 1

    # Calculation for final repayment frequency with no interest
    if payable_balance == 0 and repayment_n + extra > total_balance:

        if repayment_n + extra > total_balance > repayment_n:
            principal_payment = repayment_n  # Final payment is the remaining loan balance
            total_principal += total_balance

            schedule.append({
                label: index,
                "Interest This Payment": 0.00,
                "Principal This Payment": round(principal_payment, 2),
                "Extra This Payment": round(total_balance - repayment_n, 2),
                "Interest To Date": round(total_interest, 2),
                "Principal To Date": round(total_principal, 2),
                "Interest Payable Loan Balance": 0.00,
                "Total Loan Balance": 0.00
            })

        elif total_balance < repayment_n:
            principal_payment = total_balance  # Final payment is the remaining loan balance
            total_principal += principal_payment
            total_balance = 0  # Paid off all principal including offset

            schedule.append({
                label: index,
                "Interest This Payment": 0.00,
                "Principal This Payment": round(principal_payment, 2),
                "Extra This Payment": 0.00,
                "Interest To Date": round(total_interest, 2),
                "Principal To Date": round(total_principal, 2),
                "Interest Payable Loan Balance": 0.00,
                "Total Loan Balance": round(total_balance, 2)
            })

        period_n = index  # Update loan term with offset

    return schedule, period_n, final_interest


def display_amortisation(schedule,final_interest,frequency):
    """Display the amortisation schedule in a table

    Args:
        schedule (list[dict]): Amortisation schedule consisting of Interest this payment, Principal this payment, Interest to date, Principal to date, Principal remaining for each month
        final_interest (int): Final month paying interest, this row will be highlighted
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
    """
    # Display schedules for different repayment frequencies
    # Monthly
    if frequency == 'm':
        # Print the labels and separation line, Labels are left-aligned which is standard for financial tables
        print(
            f"\n{BOLD}{'MONTH':<8} {'INTEREST ($)':<15} {'PRINCIPAL ($)':<16} {'EXTRA REPAYMENT ($)':<22} {'INTEREST TO DATE ($)':<23} {'PRINCIPAL TO DATE ($)':<24} {'EFFECTIVE BALANCE ($)':<24} {'TOTAL LOAN BALANCE ($)':<22}{RESET}")
        print("-" * 161)

        # Numbers are right-aligned which is standard for financial tables
        for row in schedule:
            # Highlight the month of final interest
            if row['Month'] == final_interest:
                print(
                    f"{GREEN}{ITALIC}{row['Month']:<5}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            else:
                print(
                    f"{row['Month']:<5}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}")

    # Fornightly
    elif frequency == 'f':
        print(
            f"\n{BOLD}{'FORTNIGHT':<12} {'INTEREST ($)':<15} {'PRINCIPAL ($)':<16} {'EXTRA REPAYMENT ($)':<22} {'INTEREST TO DATE ($)':<23} {'PRINCIPAL TO DATE ($)':<24} {'EFFECTIVE BALANCE ($)':<24} {'TOTAL LOAN BALANCE ($)':<22}{RESET}")
        print("-" * 165)

        for row in schedule:
            if row['Fortnight'] == final_interest:
                print(
                    f"{GREEN}{ITALIC}{row['Fortnight']:<9}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            else:
                print(
                    f"{row['Fortnight']:<9}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}")

    # Weekly
    elif frequency == 'w':
        print(
            f"\n{BOLD}{'WEEK':<7} {'INTEREST ($)':<15} {'PRINCIPAL ($)':<16} {'EXTRA REPAYMENT ($)':<22} {'INTEREST TO DATE ($)':<23} {'PRINCIPAL TO DATE ($)':<24} {'EFFECTIVE BALANCE ($)':<24} {'TOTAL LOAN BALANCE ($)':<22}{RESET}")
        print("-" * 160)

        for row in schedule:
            if row['Week'] == final_interest:
                print(
                    f"{GREEN}{ITALIC}{row['Week']:<4}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            else:
                print(
                    f"{row['Week']:<4}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}")


def main():
    """Main function - only runs when executed directly and not when imported"""
    print(f"\n{BOLD}USER INPUTS:{RESET}")
    loan_amount = req_loan_amount()
    loan_period = req_loan_period()
    annual_rate = req_interest_rate()
    repayment_frequency = req_frequency()
    extra_repayments = req_additional_repayments()
    offset_amount = req_offset_amount()
    frq_repayments, frq_period, frq_interest = calc_repayment(loan_amount,loan_period,annual_rate,repayment_frequency)
    offset_term = calc_loan_term(loan_amount,frq_repayments,frq_period,frq_interest,offset_amount)
    amor_schedule, new_term, final_interest = calc_amortisation(loan_amount,frq_repayments,offset_term,frq_interest,offset_amount,repayment_frequency,extra_repayments)
    print(f"\n{BOLD}OUTPUTS:{RESET}")
    display_repayment(frq_repayments,repayment_frequency)
    display_term(new_term,repayment_frequency)
    display_amortisation(amor_schedule,final_interest,repayment_frequency)


# ── Main ───────────────────────────────────────
if __name__ == "__main__":
    main()