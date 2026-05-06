"""
MORTGAGE CALCULATOR
Calculate the monthly repayments of a fixed term mortgage over a period at a specific interest rate. Also shows the amortisation schedule, and the new loan term if there is an offset account/additional repayments.

Inputs:
- Loan amount ($)
- Loan period (years)
- Repayment Type (Principal & Interest or Interest Only)
- Interest rate (% p.a.) - P&I and IO
- Repayment frequency - Monthly (default), fortnightly, or weekly
- Additional repayment ($)
- Offset amount ($)

Outputs:
- Amortisation schedule
- Monthly repayment ($) - IO and P&I
- Interest Only period (if applicable)
- Updated loan term with offset and additional repayments

Author:     Tim Lu
Date:       06 May 2026
Version:    1.5.2
"""


# ── Constants ───────────────────────────────────────
# Define font styling constants
BOLD       = "\033[1m"
ITALIC     = "\033[3m"
RED        = "\033[31m"
GREEN      = "\033[32m"
YELLOW     = "\033[33m"
CYAN       = "\033[36m"
RESET      = "\033[0m"
CLEAR      = "\033[A\033[2K"  # Moves the cursor up one line and clears the entire line


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
                print("Error: Loan amount must be an integer!")
            else:
                print(f"Error: {e}")
        else:
            print(f"{CLEAR}", end="")  # clear previous line
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
            raw = input(f"{CYAN}Loan Period (years, default 30 years):{RESET} ")
            if raw == "":
                period = 30  # Pressing enter is equivalent to 30 years
                print(f"\033[A\033[39G {GREEN}{ITALIC}30{RESET}")  # Move cursor up one line and to the end of line and print default value
            else:
                period = int(raw)
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


def req_principal_interest():
    """Request user to select repayment type - Principal & Interest (default), or Interest only

    Returns:
        io_period (int): Interest only period in years
    """
    io = 0  # Initialise variable to start while loop
    io_period = 0
    while io == 0:
        try:
            io = input(f"{CYAN}Select Repayment Type (Principal & Interest - P (default) / Interest only - I):{RESET} ")
            if io in ['P', 'p', 'P&I', 'p&i', 'Principal & Interest', 'principal & interest']:
                io = False
            elif io == '':
                print(f"\033[A\033[80G {GREEN}{ITALIC}P&I{RESET}")  # Move cursor up one line and to the end of line and print default value
                io = False  # Pressing enter is equivalent to choosing default P&I
            elif io in ['I', 'i', 'IO', 'io', 'Interest only', 'interest only']:
                io = True

                while io_period == 0:
                    try:
                        raw = input(f"{CYAN}Enter Interest Only Period (years, default 5 years):{RESET} ")
                        if raw == "":
                            io_period = 5  # Pressing enter is equivalent to 5 years
                            print(
                                f"\033[A\033[53G {GREEN}{ITALIC}5{RESET}")  # Move cursor up one line and to the end of line and print default value
                        else:
                            io_period = int(raw)
                            if io_period < 0:
                                io_period = 0
                                raise ValueError("Interest Only Period cannot be negative!")
                    except ValueError as e:
                        if "invalid literal" in str(e):
                            io_period = 0
                            print("Error: Interest Only Period must be an integer!")
                        else:
                            print(f"Error: {e}")
                    else:
                        return io_period
            else:
                io = 0
                raise Exception("Repayment Type must be 'p' or 'i'!")
        except Exception as e:
            print(f"Error: {e}")
        else:
            return io_period


def req_interest_rate(io_period):
    """Request user to input the annual interest rate.

    Args:
        io_period (int): Interest only period in years

    Returns:
        interest (float): Annual interest rate in decimal (not percentage)
        io_interest (float): Annual interest only interest rate in decimal (not percentage)
    """
    interest = 0  # Initialise variable to start while loop
    io_interest = 0

    # If there is interest only period
    if io_period > 0:
        while io_interest == 0:
            try:
                io_interest = float(input(f"{CYAN}Interest Only Interest Rate (% p.a.):{RESET} "))
                io_interest = io_interest / 100  # Convert from %
                if io_interest < 0:
                    io_interest = 0
                    raise ValueError("Interest Only Interest Rate cannot be negative!")
            except ValueError as e:
                if "could not convert" in str(e):
                    io_interest = 0
                    print("Error: Interest Only Interest Rate must be floating point!")
                else:
                    print(f"Error: {e}")
            else:
                pass

    while interest == 0:
        try:
            interest = float(input(f"{CYAN}P&I Interest Rate (% p.a.):{RESET} "))
            interest = interest / 100  # Convert from %
            if interest < 0:
                interest = 0
                raise ValueError("P&I Interest Rate cannot be negative!")
        except ValueError as e:
            if "could not convert" in str(e):
                interest = 0
                print("Error: P&I Interest Rate must be floating point!")
            else:
                print(f"Error: {e}")
        else:
            return interest, io_interest


def req_frequency():
    """Request user to select repayment frequency - Monthly (default), fortnightly, or weekly

    Returns:
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
    """
    frequency = 0  # Initialise variable to start while loop
    while frequency not in ['M', 'm', 'Monthly', 'monthly', '', 'F', 'f', 'Fortnightly', 'fortnightly', 'W', 'w', 'Weekly', 'weekly']:
        try:
            frequency = input(f"{CYAN}Select Repayment Frequency (Monthly - M (default) / Fortnightly - F / Weekly - W):{RESET} ")
            if frequency in ['M', 'm', 'Monthly', 'monthly']:
                frequency = 'm'
            elif frequency == '':
                print(f"\033[A\033[83G {GREEN}{ITALIC}Monthly{RESET}")  # Move cursor up one line and to the end of line and print default value
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
            raw = input(f"{CYAN}Additional Repayment Amount (default $0): ${RESET} ")
            if raw == "":
                extra = 0.00  # Pressing enter is equivalent to zero
                print(
                    f"\033[A\033[44G {GREEN}{ITALIC}0{RESET}")  # Move cursor up one line and to the end of line and print default value
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
            print(f"{CLEAR}", end="")  # clear previous line
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
            raw = input(f"{CYAN}Offset Amount (default $0): ${RESET} ")
            if raw == "":
                offset = 0.00  # Pressing enter is equivalent to zero
                print(
                    f"\033[A\033[30G {GREEN}{ITALIC}0{RESET}")  # Move cursor up one line and to the end of line and print default value
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
            print(f"{CLEAR}", end="")  # clear previous line
            print(f"{CYAN}Offset Amount entered: ${RESET}{GREEN}{ITALIC}{offset:,.2f}{RESET}")  # Echo back with formatting
            return offset


def calc_repayment(amount, period_y, interest_y, frequency, io_period, io_interest, offset):
    """Calculate the monthly/fortnightly/weekly repayments.

    Args:
        amount (int): Loan amount in dollars
        period_y (int): Loan term in years
        interest_y (float): Annual interest rate in decimal (not percentage)
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
        io_period (int): Interest only period in years
        io_interest (float): Annual interest only interest rate in decimal (not percentage)
        offset (float): Offset amount in dollars

    Returns:
        io_repayment_n (float): Interest Only monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        io_repayment_offset (float): Interest Only monthly/fortnightly/weekly repayments when taking into account offset amount in dollars (rounded to 2 decimal points)
        io_period_n (int): Interest only period in months/fortnights/weeks
        repayment_n (float): P&I monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        period_n (int): P&I loan term in months/fortnights/weeks
        interest_n (float): P&I monthly/fortnightly/weekly interest rate in decimal (not percentage)
    """
    # Map frequency to its annual multiplier
    multipliers = {'m': 12, 'f': 26, 'w': 52}
    n = multipliers[frequency]

    # Calculation for the standard P&I repayment
    period_n = (period_y - io_period) * n  # P&I period is reduced due to IO period
    interest_n = interest_y / n
    repayment_n = (amount * interest_n * (1 + interest_n) ** period_n) / ((1 + interest_n) ** period_n - 1)

    # Calculation for IO repayment if true, otherwise set to None
    if io_period > 0:
        io_period_n = io_period * n
        io_interest_n = io_interest / n
        io_repayment_n = amount * io_interest_n
        io_repayment_offset = (amount - offset) * io_interest_n
    else:
        io_repayment_n, io_repayment_offset, io_period_n, io_interest_n = None, None, None, None

    return io_repayment_n, io_repayment_offset, io_period_n, repayment_n, period_n, interest_n


def display_repayment(io_repayment_n, io_repayment_offset, repayment_n, frequency):
    """Display the monthly/fortnightly/weekly repayments.

    Args:
        io_repayment_n (float): Interest Only monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        io_repayment_offset (float): Interest Only monthly/fortnightly/weekly repayments when taking into account offset amount in dollars (rounded to 2 decimal points)
        repayment_n (float): P&I monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
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
    if io_repayment_n is not None:
        print(f"{CYAN}{interval} IO Repayment: ${GREEN}{ITALIC}{io_repayment_n:,.2f}{RESET}")
        print(f"{CYAN}{interval} IO Repayment with offset: ${GREEN}{ITALIC}{io_repayment_offset:,.2f}{RESET}")
    print(f"{CYAN}{interval} P&I Repayment: ${GREEN}{ITALIC}{repayment_n:,.2f}{RESET}")


def display_term(io_period, io_period_n, period_u, frequency):
    """Display the updated loan term after taking into account the offset amount and additional repayments.

    Args:
        io_period (int): Interest only period in years
        io_period_n (int): Interest only period in months/fortnights/weeks
        period_u (int): Updated loan term (including paying off principal in offset and extra repayments) in months/fortnights/weeks
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
    """
    # Display IO period if true
    if io_period:
        if frequency == 'm':
            print(f"{CYAN}Interest Only period: {GREEN}{ITALIC}{io_period} years ({io_period_n} months){RESET}")
        elif frequency == 'f':
            print(f"{CYAN}Interest Only period: {GREEN}{ITALIC}{io_period} years ({io_period_n} fortnights){RESET}")
        elif frequency == 'w':
            print(f"{CYAN}Interest Only period: {GREEN}{ITALIC}{io_period} years ({io_period_n} weeks){RESET}")
    # Display messages for different repayment frequencies
    if frequency == 'm':
        print(f"{CYAN}P&I Loan term with offset and additional repayments: {GREEN}{ITALIC}{period_u // 12} years & {period_u % 12} months ({period_u} months){RESET}")
    elif frequency == 'f':
        print(f"{CYAN}P&I Loan term with offset and additional repayments: {GREEN}{ITALIC}{period_u // 26} years & {period_u % 26} fortnights ({period_u} fortnights){RESET}")
    elif frequency == 'w':
        print(f"{CYAN}P&I Loan term with offset and additional repayments: {GREEN}{ITALIC}{period_u // 52} years & {period_u % 52} weeks ({period_u} weeks){RESET}")


def calc_amortisation(amount, io_repayment_offset, io_period_n, repayment_n, interest_n, offset, frequency, extra):
    """Calculate the amortisation schedule which is a table showing each payment including the principal and interest.

    Args:
        amount (int): Loan amount in dollars
        io_repayment_offset (float): Interest Only monthly/fortnightly/weekly repayments when taking into account offset amount in dollars (rounded to 2 decimal points)
        io_period_n (int): Interest only period in months/fortnights/weeks
        repayment_n (float): P&I monthly/fortnightly/weekly repayments in dollars (rounded to 2 decimal points)
        interest_n (float): P&I monthly/fortnightly/weekly interest rate in decimal (not percentage)
        offset (float): Offset amount in dollars
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
        extra (float): Additional repayment amount every repayment cycle in dollars

    Returns:
        schedule (list[dict]): Amortisation schedule consisting of Month/Fortnight/Week, Interest this payment, Principal this payment, Extra repayment, Interest to date, Principal to date, Effective balance, and Principal remaining
        period_u (int): Updated loan term (including paying off principal in offset and extra repayments) in months/fortnights/weeks
        final_interest (int): Final month/fortnight/week paying interest, this row will be highlighted
    """
    # Pre-rounding all floating numbers to 2 decimal points for consistency
    # amount = round(amount, 4)
    # offset = round(offset, 4)
    # extra = round(extra, 4)

    # Offset amount equal to loan amount reduces interest to zero, therefore any additional offset beyond loan amount is meaningless
    if offset > amount:
        offset = amount

    schedule = []  # Initialise list for amortisation schedule
    payable_balance = amount - offset  # Current balance of principal owing interest
    total_balance = amount  # Current balance of principal including amount in offset
    total_interest = 0  # Total interest paid to date
    total_principal = 0  # Total principal paid to date
    index = 0  # Loan term index
    final_interest = 'NO'  # Flag for final index paying interest
    label = 0  # Index label for repayment frequency
    period_u = 0  # To-be-updated loan term (including paying off principal in offset) in months/fortnights/weeks

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
        "Interest Payable Loan Balance": payable_balance,
        "Total Loan Balance": amount
    })

    index += 1

    # Interest Only calculation for each month/fortnight/week if provided
    if io_period_n is not None:
        while index <= io_period_n:
            interest_payment = io_repayment_offset
            total_interest += interest_payment

            # Append dictionary into list for each repayment frequency
            schedule.append({
                label: index,
                "Interest This Payment": interest_payment,
                "Principal This Payment": 0.00,
                "Extra This Payment": 0.00,
                "Interest To Date": total_interest,
                "Principal To Date": 0.00,
                "Interest Payable Loan Balance": payable_balance,
                "Total Loan Balance": total_balance
            })

            index += 1

    # Note that additional repayments will sit in the offset account and therefore contributes only to the principal and not the interest
    # Calculate for each month/fortnight/week - Interest this payment, Principal this payment, Interest to date, Principal to date, Interest Payable Loan Balance, Total Loan Balance
    while repayment_n <= payable_balance:

        # Repayment + extra is still less than effective balance
        if repayment_n + extra <= payable_balance:
            interest_payment = payable_balance * interest_n
            principal_payment = repayment_n - interest_payment
            total_interest += interest_payment
            total_principal += principal_payment + extra
            payable_balance -= principal_payment + extra
            total_balance -= principal_payment + extra

            # Append dictionary into list for each repayment frequency
            schedule.append({
                label: index,
                "Interest This Payment": interest_payment,
                "Principal This Payment": principal_payment,
                "Extra This Payment": extra,
                "Interest To Date": total_interest,
                "Principal To Date": total_principal,
                "Interest Payable Loan Balance": payable_balance,
                "Total Loan Balance": total_balance
            })

            index += 1

        # Repayment alone is less than effective balance but repayment+extra exceeds effective balance
        else:
            interest_payment = payable_balance * interest_n
            principal_payment = repayment_n - interest_payment
            total_interest += interest_payment
            total_principal += principal_payment + extra
            payable_balance = 0.00
            total_balance -= principal_payment + extra
            final_interest = index  # Flag the final repayment frequency paying interest

            # Append dictionary into list for each repayment frequency
            schedule.append({
                label: index,
                "Interest This Payment": interest_payment,
                "Principal This Payment": principal_payment,
                "Extra This Payment": extra,
                "Interest To Date": total_interest,
                "Principal To Date": total_principal,
                "Interest Payable Loan Balance": payable_balance,
                "Total Loan Balance": total_balance
            })

            index += 1

    # Calculation for the final repayment month/fortnight/week with interest
    while repayment_n > round(payable_balance, 2) > 0:

        # Offset is zero, then this is the final repayment
        if payable_balance == total_balance:

            # Repayment alone is not enough to cover p+i
            if total_balance + payable_balance * interest_n > repayment_n:

                # If extra is 0 then this is not the final repayment
                if extra == 0:
                    interest_payment = payable_balance * interest_n
                    principal_payment = repayment_n - interest_payment
                    total_interest += interest_payment
                    total_principal += principal_payment + extra
                    payable_balance -= principal_payment + extra
                    total_balance -= principal_payment + extra

                    # Append dictionary into list for each repayment frequency
                    schedule.append({
                        label: index,
                        "Interest This Payment": interest_payment,
                        "Principal This Payment": principal_payment,
                        "Extra This Payment": extra,
                        "Interest To Date": total_interest,
                        "Principal To Date": total_principal,
                        "Interest Payable Loan Balance": payable_balance,
                        "Total Loan Balance": total_balance
                    })

                    # If principal remaining > 0 then keep iterating, otherwise this is the final repayment
                    if round(total_balance, 2) > 0:
                        index += 1

                # Repayment alone is not enough to cover p+i but repayment+extra is enough
                else:
                    interest_payment = payable_balance * interest_n
                    principal_payment = repayment_n - interest_payment
                    total_interest += interest_payment
                    total_principal += total_balance
                    payable_balance = total_balance = 0  # Paid off all principal

                    schedule.append({
                        label: index,
                        "Interest This Payment": interest_payment,
                        "Principal This Payment": principal_payment,
                        "Extra This Payment": total_balance - repayment_n,
                        "Interest To Date": total_interest,
                        "Principal To Date": total_principal,
                        "Interest Payable Loan Balance": 0.00,
                        "Total Loan Balance": 0.00
                    })

            # Repayment alone is enough to cover p+i
            else:
                interest_payment = payable_balance * interest_n
                principal_payment = total_balance  # Final payment is the remaining loan balance
                total_interest += interest_payment
                total_principal += principal_payment
                payable_balance = total_balance = 0  # Paid off all principal

                schedule.append({
                    label: index,
                    "Interest This Payment": interest_payment,
                    "Principal This Payment": principal_payment,
                    "Extra This Payment": 0.00,
                    "Interest To Date": total_interest,
                    "Principal To Date": total_principal,
                    "Interest Payable Loan Balance": 0.00,
                    "Total Loan Balance": 0.00
                })

            # Update final loan term with offset
            if io_period_n:
                period_u = index - io_period_n
            else:
                period_u = index

        # Offset is non-zero
        else:
            # Repayment is more than effective balance but not enough to cover interest
            if payable_balance + payable_balance * interest_n > repayment_n:
                interest_payment = payable_balance * interest_n
                principal_payment = repayment_n - interest_payment
                total_interest += interest_payment
                total_principal += principal_payment + extra
                payable_balance = 0.00
                total_balance -= principal_payment + extra

                # Append dictionary into list for each repayment frequency
                schedule.append({
                    label: index,
                    "Interest This Payment": interest_payment,
                    "Principal This Payment": principal_payment,
                    "Extra This Payment": extra,
                    "Interest To Date": total_interest,
                    "Principal To Date": total_principal,
                    "Interest Payable Loan Balance": payable_balance,
                    "Total Loan Balance": total_balance
                })

                index += 1

            # Repayment is more than effective balance + interest
            else:
                interest_payment = payable_balance * interest_n
                principal_payment = repayment_n - interest_payment
                total_interest += interest_payment
                total_principal += principal_payment + extra
                total_balance -= principal_payment + extra  # First (partial) payment on principal in offset
                payable_balance = 0  # Paid off all principal that charges interest
                final_interest = index  # Flag the final repayment frequency paying interest

                schedule.append({
                    label: index,
                    "Interest This Payment": interest_payment,
                    "Principal This Payment": principal_payment,
                    "Extra This Payment": extra,
                    "Interest To Date": total_interest,
                    "Principal To Date": total_principal,
                    "Interest Payable Loan Balance": payable_balance,
                    "Total Loan Balance": total_balance
                })

                index += 1

    # Calculation for the repayment frequencies with no interest (offset is non-zero)
    while payable_balance == 0 and repayment_n < total_balance:

        # Repayment alone is less than total balance but repayment + extra is more than total balance then this is final repayment
        if repayment_n + extra > total_balance > repayment_n:
            principal_payment = repayment_n  # Final payment is the remaining loan balance
            total_principal += total_balance

            schedule.append({
                label: index,
                "Interest This Payment": 0.00,
                "Principal This Payment": principal_payment,
                "Extra This Payment": total_balance - repayment_n,
                "Interest To Date": total_interest,
                "Principal To Date": total_principal,
                "Interest Payable Loan Balance": 0.00,
                "Total Loan Balance": 0.00
            })

            # Update final loan term with offset
            if io_period_n:
                period_u = index - io_period_n
            else:
                period_u = index

        # Repayment + extra is less than total balance
        else:
            principal_payment = repayment_n
            total_principal += principal_payment + extra
            payable_balance = 0  # Paid off all principal that charges interest
            total_balance -= principal_payment + extra  # Entire repayment goes to pay the principal in offset

            schedule.append({
                label: index,
                "Interest This Payment": 0.00,
                "Principal This Payment": principal_payment,
                "Extra This Payment": extra,
                "Interest To Date": total_interest,
                "Principal To Date": total_principal,
                "Interest Payable Loan Balance": 0.00,
                "Total Loan Balance": total_balance
            })

            index += 1

    # Calculation for final repayment (offset is non-zero, no interest payment)
    if payable_balance == 0 and repayment_n >= total_balance > 0:
        principal_payment = total_balance  # Final payment is the remaining loan balance
        total_principal += principal_payment

        schedule.append({
            label: index,
            "Interest This Payment": 0.00,
            "Principal This Payment": principal_payment,
            "Extra This Payment": 0.00,
            "Interest To Date": total_interest,
            "Principal To Date": total_principal,
            "Interest Payable Loan Balance": 0.00,
            "Total Loan Balance": 0.00
        })

        # Update final loan term with offset
        if io_period_n:
            period_u = index - io_period_n
        else:
            period_u = index

    return schedule, period_u, final_interest


def display_amortisation(schedule, final_interest, frequency, io_period_n):
    """Display the amortisation schedule in a table

    Args:
        schedule (list[dict]): Amortisation schedule consisting of Month/Fortnight/Week, Interest this payment, Principal this payment, Extra repayment, Interest to date, Principal to date, Effective balance, and Principal remaining
        final_interest (int): Final month/fortnight/week paying interest, this row will be highlighted
        frequency (str): Repayment frequency:
            - 'm': Monthly (default)
            - 'f': Fortnightly
            - 'w': Weekly
        io_period_n (int): Interest only period in months/fortnights/weeks
    """
    # Display schedules for different repayment frequencies
    # Monthly
    if frequency == 'm':
        # Print the labels and separation line, Labels are left-aligned which is standard for financial tables
        print(f"\n{BOLD}{'MONTH':<8} {'INTEREST ($)':<15} {'PRINCIPAL ($)':<16} {'EXTRA REPAYMENT ($)':<22} {'INTEREST TO DATE ($)':<23} {'PRINCIPAL TO DATE ($)':<24} {'EFFECTIVE BALANCE ($)':<24} {'TOTAL LOAN BALANCE ($)':<22}{RESET}")
        print("-" * 161)

        # Numbers are right-aligned which is standard for financial tables
        for row in schedule:
            # Highlight the month of final interest
            if row['Month'] == final_interest:
                print(f"{GREEN}{ITALIC}{row['Month']:<5}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            # Interest Only period if provided
            elif io_period_n is not None and row['Month'] <= io_period_n:
                print(f"{YELLOW}{row['Month']:<5}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            else:
                print(f"{row['Month']:<5}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}")

    # Fornightly
    elif frequency == 'f':
        print(f"\n{BOLD}{'FORTNIGHT':<12} {'INTEREST ($)':<15} {'PRINCIPAL ($)':<16} {'EXTRA REPAYMENT ($)':<22} {'INTEREST TO DATE ($)':<23} {'PRINCIPAL TO DATE ($)':<24} {'EFFECTIVE BALANCE ($)':<24} {'TOTAL LOAN BALANCE ($)':<22}{RESET}")
        print("-" * 165)

        for row in schedule:
            if row['Fortnight'] == final_interest:
                print(f"{GREEN}{ITALIC}{row['Fortnight']:<9}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            # Interest Only period if provided
            elif io_period_n is not None and row['Fortnight'] <= io_period_n:
                print(f"{YELLOW}{row['Fortnight']:<9}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            else:
                print(f"{row['Fortnight']:<9}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}")

    # Weekly
    elif frequency == 'w':
        print(f"\n{BOLD}{'WEEK':<7} {'INTEREST ($)':<15} {'PRINCIPAL ($)':<16} {'EXTRA REPAYMENT ($)':<22} {'INTEREST TO DATE ($)':<23} {'PRINCIPAL TO DATE ($)':<24} {'EFFECTIVE BALANCE ($)':<24} {'TOTAL LOAN BALANCE ($)':<22}{RESET}")
        print("-" * 160)

        for row in schedule:
            if row['Week'] == final_interest:
                print(f"{GREEN}{ITALIC}{row['Week']:<4}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            # Interest Only period if provided
            elif io_period_n is not None and row['Week'] <= io_period_n:
                print(f"{YELLOW}{row['Week']:<4}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}{RESET}")
            else:
                print(f"{row['Week']:<4}   {row['Interest This Payment']:>13,.2f}   {row['Principal This Payment']:>14,.2f}   {row['Extra This Payment']:>20,.2f}   {row['Interest To Date']:>21,.2f}   {row['Principal To Date']:>22,.2f}   {row['Interest Payable Loan Balance']:>22,.2f}   {row['Total Loan Balance']:>23,.2f}")

    # Display a blank line after table
    print("\n")


def main():
    """Main function - only runs when executed directly and not when imported"""
    print(f"\n{BOLD}USER INPUTS:{RESET}")
    loan_amount = req_loan_amount()
    loan_period = req_loan_period()
    interest_period = req_principal_interest()
    annual_rate, io_rate = req_interest_rate(interest_period)
    repayment_frequency = req_frequency()
    extra_repayments = req_additional_repayments()
    offset_amount = req_offset_amount()
    io_repayments, io_offset, io_period, pi_repayments, pi_period, pi_interest = calc_repayment(loan_amount, loan_period, annual_rate, repayment_frequency, interest_period, io_rate, offset_amount)
    amor_schedule, new_term, final_interest = calc_amortisation(loan_amount, io_offset, io_period, pi_repayments, pi_interest, offset_amount, repayment_frequency, extra_repayments)
    print(f"\n{BOLD}OUTPUTS:{RESET}")
    display_amortisation(amor_schedule, final_interest, repayment_frequency, io_period)
    display_repayment(io_repayments, io_offset, pi_repayments, repayment_frequency)
    display_term(interest_period, io_period, new_term, repayment_frequency)


# ── Main ───────────────────────────────────────
if __name__ == "__main__":
    main()