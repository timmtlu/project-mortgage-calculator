"""
Unit test for project_mortgage_calculator.py. Written by Claude and modified/corrected accordingly as I have zero experience in unit testing.

Author:     Tim Lu
Date:       14 May 2026
Version:    1.0.2
"""


# ── Imports ───────────────────────────────────────
import unittest  # Testing framework
from unittest.mock import patch  # To fake things like sys.stdout
from io import StringIO  # Capture printed output as a string instead of terminal
from project_mortgage_calculator import (
    calc_repayment,
    calc_amortisation,
    display_repayment,
    display_term,
    display_amortisation,
    req_loan_amount,
    req_loan_period,
    req_principal_interest,
    req_interest_rate,
    req_frequency,
    req_additional_repayments,
    req_offset_amount,
)


# ── Classes & Functions ───────────────────────────────────────
class TestCalcRepayment(unittest.TestCase):
    """Tests for calc_repayment()"""

    def test_monthly_pi_basic(self):
        """Standard P&I monthly repayment on a $500k loan at 6% over 30 years"""
        io_repayments, io_offset, io_period, pi_repayments, pi_period, pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=0, io_interest=0, offset=0
        )
        self.assertAlmostEqual(pi_repayments, 2997.75, places=2)
        self.assertEqual(pi_period, 360)
        self.assertAlmostEqual(pi_interest, 0.06 / 12)
        self.assertIsNone(io_repayments)
        self.assertIsNone(io_offset)

    def test_fortnightly_frequency(self):
        """Fortnightly repayments should use 26 periods per year, '_,' means do not care about this value"""
        _, _, _, pi_repayments, pi_period, pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='f', io_period=0, io_interest=0, offset=0
        )
        self.assertEqual(pi_period, 780)          # 30 * 26
        self.assertAlmostEqual(pi_interest, 0.06 / 26)

    def test_weekly_frequency(self):
        """Weekly repayments should use 52 periods per year"""
        _, _, _, pi_repayments, pi_period, pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='w', io_period=0, io_interest=0, offset=0
        )
        self.assertEqual(pi_period, 1560)         # 30 * 52
        self.assertAlmostEqual(pi_interest, 0.06 / 52)

    def test_interest_only_period(self):
        """IO repayment should be calculated when io_period > 0"""
        io_repayments, io_offset, io_period, pi_repayments, pi_period, _ = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=5, io_interest=0.055, offset=0
        )
        self.assertAlmostEqual(io_repayments, 500_000 * (0.055 / 12), places=2)
        self.assertEqual(io_period, 60)        # 5 * 12
        self.assertEqual(pi_period, 300)          # (30 - 5) * 12

    def test_offset_reduces_io_repayment(self):
        """Offset account should reduce the IO repayment amount"""
        _, io_offset_no_offset, _, _, _, _ = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=5, io_interest=0.055, offset=0
        )
        _, io_offset_with_offset, _, _, _, _ = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=5, io_interest=0.055, offset=50_000
        )
        self.assertLess(io_offset_with_offset, io_offset_no_offset)
        self.assertAlmostEqual(io_offset_with_offset, 450_000 * (0.055 / 12), places=2)


class TestCalcAmortisation(unittest.TestCase):
    """Tests for calc_amortisation()"""

    def setUp(self):
        """Shared loan parameters for amortisation tests"""
        _, _, _, self.pi_repayments, _, self.pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=0, io_interest=0, offset=0
        )

    def test_schedule_starts_at_zero(self):
        """First row in schedule should be index 0 with zero payments"""
        schedule, _, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=0
        )
        first = schedule[0]
        self.assertEqual(first['Month'], 0)
        self.assertEqual(first['Interest This Payment'], 0.0)
        self.assertEqual(first['Principal This Payment'], 0.0)
        self.assertEqual(first['Extra This Payment'], 0.0)
        self.assertEqual(first['Interest To Date'], 0.0)
        self.assertEqual(first['Principal To Date'], 0.0)
        self.assertEqual(first['Interest Payable Loan Balance'], 500_000)
        self.assertEqual(first['Total Loan Balance'], 500_000)

    def test_schedule_ends_at_zero_balance(self):
        """Final row should have zero remaining balance"""
        schedule, _, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=0
        )
        self.assertAlmostEqual(schedule[-1]['Total Loan Balance'], 0.0, places=2)

    def test_term_is_approximately_360_months(self):
        """A 30-year loan with no offset/extra should complete in ~360 months, delta=2 means "accept anything within ±2 months of 360" — this accounts for the fact that the final repayment might be a fractional amount that slightly shifts the count by 1 or 2 periods."""
        _, period_u, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=0
        )
        self.assertAlmostEqual(period_u, 360, delta=2)

    def test_extra_repayments_shorten_term(self):
        """Additional repayments should reduce the loan term"""
        _, term_standard, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=0
        )
        _, term_with_extra, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=500
        )
        self.assertLess(term_with_extra, term_standard)

    def test_offset_shortens_term(self):
        """Offset account should reduce the loan term"""
        _, term_no_offset, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=0
        )
        _, term_with_offset, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=50_000, frequency='m', extra=0
        )
        self.assertLess(term_with_offset, term_no_offset)

    def test_offset_exceeds_loan_is_clamped(self):
        """Offset greater than loan amount should be clamped to loan amount"""
        schedule, _, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=999_999, frequency='m', extra=0
        )
        # Interest on row 1 should be zero (fully offset)
        self.assertEqual(schedule[1]['Interest This Payment'], 0.0)

    def test_interest_decreases_over_time(self):
        """Interest component should generally decrease each period (P&I)"""
        schedule, _, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=0
        )
        interests = [row['Interest This Payment'] for row in schedule[1:11]]
        self.assertEqual(interests, sorted(interests, reverse=True))

    def test_final_interest_flag_is_set(self):
        """final_interest flag should be set when offset brings balance to zero"""
        _, _, final_interest = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=50_000, frequency='m', extra=0
        )
        self.assertNotEqual(final_interest, 'NO')


class TestDisplayFunctions(unittest.TestCase):
    """Tests for display output functions using stdout capture"""

    def test_display_repayment_pi_only(self, ):
        """Should print P&I repayment line"""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_repayment(
                io_repayment_n=None, io_repayment_offset=None,
                repayment_n=2997.75, frequency='m'
            )
            output = mock_out.getvalue()
        self.assertIn("2,997.75", output)
        self.assertIn("Monthly", output)

    def test_display_repayment_with_io(self):
        """Should print IO lines when io_repayment_n is provided"""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_repayment(
                io_repayment_n=2291.67, io_repayment_offset=2083.33,
                repayment_n=2997.75, frequency='m'
            )
            output = mock_out.getvalue()
        self.assertIn("IO Repayment", output)
        self.assertIn("2,291.67", output)

    def test_display_term_pi_without_offset(self):
        """Should print the P&I loan term without taking into account offset"""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_term(
                io_period=None, io_period_n=None,
                period_u=360, frequency='m'
            )
            output = mock_out.getvalue()
        self.assertIn("30 years & 0 months", output)
        self.assertIn("360 months", output)

    def test_display_term_pi_with_offset(self):
        """Should print the P&I loan term while taking into account offset"""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_term(
                io_period=None, io_period_n=None,
                period_u=296, frequency='m'
            )
            output = mock_out.getvalue()
        self.assertIn("24 years & 8 months", output)
        self.assertIn("296 months", output)

    def test_display_term_io(self):
        """Should print the P&I loan term without taking into account offset"""
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_term(
                io_period=5, io_period_n=60,
                period_u=300, frequency='m'
            )
            output = mock_out.getvalue()
        self.assertIn("5 years", output)
        self.assertIn("60 months", output)


class TestDisplayAmortisation(unittest.TestCase):

    def setUp(self):
        """Build a small, real schedule to pass into the display function"""
        _, _, _, self.pi_repayments, _, self.pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=0, io_interest=0, offset=0
        )
        self.schedule, self.final_interest, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=self.pi_repayments, interest_n=self.pi_interest,
            offset=0, frequency='m', extra=0
        )

    # ✅ Test 1: Column headers appear in output
    def test_monthly_headers_present(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_amortisation(self.schedule, self.final_interest, 'm', None)
            output = mock_out.getvalue()
        self.assertIn("MONTH", output)
        self.assertIn("INTEREST ($)", output)
        self.assertIn("TOTAL LOAN BALANCE ($)", output)

    # ✅ Test 2: First data row (month 0) appears in output
    def test_first_row_present(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_amortisation(self.schedule, self.final_interest, 'm', None)
            output = mock_out.getvalue()
        self.assertIn("500,000.00", output)  # Opening balance should appear

    # ✅ Test 3: Fortnightly uses "FORTNIGHT" header, not "MONTH"
    def test_fortnightly_header(self):
        _, _, _, pi_repayments, _, pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='f', io_period=0, io_interest=0, offset=0
        )
        schedule, final_interest, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=pi_repayments, interest_n=pi_interest,
            offset=0, frequency='f', extra=0
        )
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_amortisation(schedule, final_interest, 'f', None)
            output = mock_out.getvalue()
        self.assertIn("FORTNIGHT", output)
        self.assertNotIn("MONTH", output)

    # ✅ Test 4: IO period rows appear (yellow rows exist in output)
    def test_io_period_rows_present(self):
        _, io_offset, io_period_n, pi_repayments, _, pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=5, io_interest=0.055, offset=0
        )
        schedule, final_interest, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=io_offset, io_period_n=io_period_n,
            repayment_n=pi_repayments, interest_n=pi_interest,
            offset=0, frequency='m', extra=0
        )
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_amortisation(schedule, final_interest, 'm', io_period_n)
            output = mock_out.getvalue()
        # YELLOW ANSI code \033[33m should appear for IO rows
        self.assertIn("\033[33m", output)

    # ✅ Test 5: Final interest row is highlighted (green)
    def test_final_interest_row_highlighted(self):
        _, _, _, pi_repayments, _, pi_interest = calc_repayment(
            amount=500_000, period_y=30, interest_y=0.06,
            frequency='m', io_period=0, io_interest=0, offset=0
        )
        schedule, final_interest, _ = calc_amortisation(
            amount=500_000, io_repayment_offset=None, io_period_n=None,
            repayment_n=pi_repayments, interest_n=pi_interest,
            offset=50_000, frequency='m', extra=0  # Offset triggers final_interest flag
        )
        with patch('sys.stdout', new_callable=StringIO) as mock_out:
            display_amortisation(schedule, final_interest, 'm', None)
            output = mock_out.getvalue()
        # GREEN ANSI code \033[32m should appear for the final interest row
        self.assertIn("\033[32m", output)


class TestReqLoanAmount(unittest.TestCase):

    # ✅ Happy path
    def test_valid_amount(self):
        with patch('builtins.input', return_value='500000'):
            result = req_loan_amount()
        self.assertEqual(result, 500000)

    # ✅ Commas should be stripped before converting
    def test_valid_amount_with_commas(self):
        with patch('builtins.input', return_value='500,000'):
            result = req_loan_amount()
        self.assertEqual(result, 500000)

    # ❌ Amount below $30,000 minimum — then valid input
    def test_amount_below_minimum_retries(self):
        with patch('builtins.input', side_effect=['10000', '500000']):
            result = req_loan_amount()
        self.assertEqual(result, 500000)

    # ❌ Negative amount — then valid input
    def test_negative_amount_retries(self):
        with patch('builtins.input', side_effect=['-100000', '500000']):
            result = req_loan_amount()
        self.assertEqual(result, 500000)

    # ❌ Non-integer input — then valid input
    def test_non_integer_retries(self):
        with patch('builtins.input', side_effect=['abc', '500000']):
            result = req_loan_amount()
        self.assertEqual(result, 500000)

    # ❌ Float input — then valid input (your code uses int(), so floats fail)
    def test_float_input_retries(self):
        with patch('builtins.input', side_effect=['500000.50', '500000']):
            result = req_loan_amount()
        self.assertEqual(result, 500000)


class TestReqLoanPeriod(unittest.TestCase):

    # ✅ Standard period
    def test_valid_period(self):
        with patch('builtins.input', return_value='25'):
            result = req_loan_period()
        self.assertEqual(result, 25)

    # ✅ Empty input defaults to 30 years
    def test_default_period_on_enter(self):
        with patch('builtins.input', return_value=''):
            result = req_loan_period()
        self.assertEqual(result, 30)

    # ❌ Negative period — then valid
    def test_negative_period_retries(self):
        with patch('builtins.input', side_effect=['-5', '25']):
            result = req_loan_period()
        self.assertEqual(result, 25)

    # ❌ Non-integer — then valid
    def test_non_integer_retries(self):
        with patch('builtins.input', side_effect=['abc', '25']):
            result = req_loan_period()
        self.assertEqual(result, 25)


class TestReqPrincipalInterest(unittest.TestCase):

    # ✅ P&I selected — should return 0 (no IO period)
    def test_pi_selected(self):
        with patch('builtins.input', return_value='P'):
            result = req_principal_interest()
        self.assertEqual(result, 0)

    # ✅ Default (Enter) — treated as P&I
    def test_default_is_pi(self):
        with patch('builtins.input', return_value=''):
            result = req_principal_interest()
        self.assertEqual(result, 0)

    # ✅ IO selected with default 5-year period
    def test_io_selected_default_period(self):
        # First input selects IO, second input (Enter) defaults to 5 years
        with patch('builtins.input', side_effect=['I', '']):
            result = req_principal_interest()
        self.assertEqual(result, 5)

    # ✅ IO selected with custom period
    def test_io_selected_custom_period(self):
        with patch('builtins.input', side_effect=['I', '3']):
            result = req_principal_interest()
        self.assertEqual(result, 3)

    # ❌ Invalid option — then valid P selection
    def test_invalid_option_retries(self):
        with patch('builtins.input', side_effect=['X', 'P']):
            result = req_principal_interest()
        self.assertEqual(result, 0)


class TestReqInterestRate(unittest.TestCase):

    # ✅ P&I only (no IO period)
    def test_pi_rate_only(self):
        with patch('builtins.input', return_value='6.0'):
            interest, io_interest = req_interest_rate(io_period=0)
        self.assertAlmostEqual(interest, 0.06, places=4)
        self.assertEqual(io_interest, 0)

    # ✅ Both IO and P&I rates (when IO period exists)
    def test_both_rates_with_io_period(self):
        # First input is IO rate, second is P&I rate
        with patch('builtins.input', side_effect=['5.5', '6.0']):
            interest, io_interest = req_interest_rate(io_period=5)
        self.assertAlmostEqual(interest, 0.06, places=4)
        self.assertAlmostEqual(io_interest, 0.055, places=4)

    # ❌ Non-float input — then valid
    def test_non_float_retries(self):
        with patch('builtins.input', side_effect=['abc', '6.0']):
            interest, io_interest = req_interest_rate(io_period=0)
        self.assertAlmostEqual(interest, 0.06, places=4)


class TestReqFrequency(unittest.TestCase):

    # ✅ Monthly selected
    def test_monthly_selected(self):
        with patch('builtins.input', return_value='M'):
            result = req_frequency()
        self.assertEqual(result, 'm')

    # ✅ Default (Enter) — treated as monthly
    def test_default_is_monthly(self):
        with patch('builtins.input', return_value=''):
            result = req_frequency()
        self.assertEqual(result, 'm')

    # ✅ Fortnightly
    def test_fortnightly_selected(self):
        with patch('builtins.input', return_value='F'):
            result = req_frequency()
        self.assertEqual(result, 'f')

    # ✅ Weekly
    def test_weekly_selected(self):
        with patch('builtins.input', return_value='W'):
            result = req_frequency()
        self.assertEqual(result, 'w')

    # ❌ Invalid — then valid
    def test_invalid_retries(self):
        with patch('builtins.input', side_effect=['X', 'M']):
            result = req_frequency()
        self.assertEqual(result, 'm')


class TestReqAdditionalRepayments(unittest.TestCase):

    # ✅ Valid extra repayment
    def test_valid_extra_repayment(self):
        with patch('builtins.input', return_value='500'):
            result = req_additional_repayments()
        self.assertAlmostEqual(result, 500.0, places=2)

    # ✅ Default (Enter) — treated as 0
    def test_default_is_zero(self):
        with patch('builtins.input', return_value=''):
            result = req_additional_repayments()
        self.assertEqual(result, 0.0)

    # ❌ Negative — then valid
    def test_negative_retries(self):
        with patch('builtins.input', side_effect=['-100', '500']):
            result = req_additional_repayments()
        self.assertAlmostEqual(result, 500.0, places=2)


class TestReqOffsetAmount(unittest.TestCase):

    # ✅ Valid offset amount
    def test_valid_offset(self):
        with patch('builtins.input', return_value='50000'):
            result = req_offset_amount()
        self.assertAlmostEqual(result, 50000.0, places=2)

    # ✅ Default (Enter) — treated as 0
    def test_default_is_zero(self):
        with patch('builtins.input', return_value=''):
            result = req_offset_amount()
        self.assertEqual(result, 0.0)

    # ❌ Negative — then valid
    def test_negative_offset_retries(self):
        with patch('builtins.input', side_effect=['-50000', '50000']):
            result = req_offset_amount()
        self.assertAlmostEqual(result, 50000.0, places=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)