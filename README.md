# project-mortgage-calculator
Calculate the monthly repayments of a fixed term mortgage over a period at a specific interest rate. Also shows the amortisation schedule, and the new loan term if there is an offset account/additional repayments.

Usage Instructions:
1. Download and run project-mortgage-calculator.py.
2. Enter the inputs as requested:

  Inputs:
  - Loan amount ($)
  - Loan period (years)
  - Repayment Type (Principal & Interest or Interest Only)
  - Interest rate (% p.a.) - P&I and IO
  - Repayment frequency - Monthly (default), fortnightly, or weekly
  - Additional repayment ($)
  - Offset amount ($)

<img width="940" height="287" alt="image" src="https://github.com/user-attachments/assets/ccba4fc6-5aaf-4970-8d4e-e85513c3e782" />

3. The outputs are as following:
   
  Outputs:
  - Amortisation schedule
    Yellow: Interest Only repayments
    White: Principal & Interest repayments
    Green: Final repayment with interest
  - Monthly repayment ($) - IO and P&I
  - Interest Only period (if applicable)
  - Updated loan term with offset and additional repayments

<img width="1642" height="407" alt="image" src="https://github.com/user-attachments/assets/c640a12a-f8a1-40cf-aafa-b2d27214abbc" />
<img width="1635" height="598" alt="image" src="https://github.com/user-attachments/assets/bbb3f854-9c27-4beb-9a6d-8a9858e94089" />
<img width="881" height="118" alt="image" src="https://github.com/user-attachments/assets/fcff0af1-b553-4ec4-bf4e-39c453371df2" />

Notes:
- Offset does NOT reduce the repayment amount, but decreases the loan term due to reduced payable interest
- Additional/extra repayments do not pay off the principal or interest directly, but sit in the offset account

Future Updates:
- Add customisation to extra repayments e.g. start and end date, varying amounts for different periods
