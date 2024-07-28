import random
import math
from fpdf import FPDF

def equal_split(total_bill, num_friends):
    amount_per_person = total_bill / num_friends
    return [round(amount_per_person, 2) for _ in range(num_friends)]

def diff_split(total_bill, num_friends):
    if num_friends <= 0:
        raise ValueError("Number of people must be greater than zero")
    if total_bill <= 0:
        raise ValueError("Total amount must be greater than zero")

    # Generate random weights
    weights = [random.uniform(0.35, 1) for _ in range(num_friends)]
    total_weight = sum(weights)

    # Calculate the amounts based on weights
    amounts = [round(total_bill * (weight / total_weight), 2) for weight in weights]
    summat, n = 0, len(amounts)
    for i in range(n-1):
        fractional_part, integer_part = math.modf(amounts[i])
        if fractional_part < 0.5:
            amounts[i] = math.floor(amounts[i])
        else:
            amounts[i] = math.ceil(amounts[i])
        summat += amounts[i]
    amounts[n-1] = total_bill - summat
    return amounts

def percent_split(total_bill, num_friends):
    weights = [random.uniform(0.30, 1) for _ in range(num_friends)]
    total_weight = sum(weights)
    amounts = [round((weight / total_weight) * 100, 2) for weight in weights]
    summat, n = 0, len(amounts)
    for i in range(n-1):
        fractional_part, integer_part = math.modf(amounts[i])
        if fractional_part <= 0.5:
            amounts[i] = math.floor(amounts[i])
        else:
            amounts[i] = math.ceil(amounts[i])
        summat += amounts[i]
    amounts[n-1] = 100 - summat
    return amounts

def generate_report(total_bill, num_friends, amounts, split_method):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 16)
    
    # Title
    pdf.cell(200, 20, txt = "Expense Split Report", ln = True, align = 'C')
    
    # Basic information
    pdf.set_font("Arial", size = 12)
    pdf.cell(200, 10, txt = f"Total Bill: {total_bill}", ln = True)
    pdf.cell(200, 10, txt = f"Number of Friends: {num_friends}", ln = True)
    pdf.cell(200, 10, txt = f"Split Method: {split_method}", ln = True)
    
    # Amounts per person
    if split_method == "Percentage":
        pdf.cell(200, 10, txt = "Percentage per person:", ln = True)
    else:
        pdf.cell(200, 10, txt = "Amount per person:", ln = True)
    for i, amount in enumerate(amounts):
        pdf.cell(200, 10, txt = f"Person {i+1}: {amount}", ln = True)
    
    # Save the PDF to a file
    pdf_file = "expense_split_report.pdf"
    pdf.output(pdf_file)
    return pdf_file
