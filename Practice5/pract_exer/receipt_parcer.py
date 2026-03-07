#(1) Extract all prices from the receipt
import re
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
prices = re.findall(r'\d[\d ]*,\d{2}', text)
print(prices)

#(2) Find all product names
import re
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
product_names = re.findall(r'(?m)^\d+\.\n(.+)\n\d+,\d{3} x \d[\d ]*,\d{2}$', text)
print(product_names)

#(3) Calculate total amount
import re
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
match = re.search(r'ИТОГО:\n(\d[\d ]*,\d{2})', text)
if match:
    total = match.group(1)
    print(total)

#OR another method for (3)
import re
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
totals = re.findall(r'(?m)^\d+,\d{3} x \d[\d ]*,\d{2}\n(\d[\d ]*,\d{2})$', text)
def to_float(x):
    return float(x.replace(" ", "").replace(",", "."))
sum_total = sum(to_float(x) for x in totals)
print(sum_total)

#(4) Extract date and time information
import re
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})', text)
if match:
    date = match.group(1)
    time = match.group(2)
    print("Date:", date)
    print("Time:", time)

#(5) Find payment method
import re
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
match = re.search(r'(Банковская карта|Наличные|Карта):', text)
if match:
    payment_method = match.group(1)
    print(payment_method)

#(6) Create a structured output
import re
import json
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
def to_float(x):
    return float(x.replace(" ", "").replace(",", "."))
prices = re.findall(r'\d[\d ]*,\d{2}', text)
product_names = re.findall(r'(?m)^\d+\.\n(.+)\n\d+,\d{3} x \d[\d ]*,\d{2}$', text)
item_totals = re.findall(r'(?m)^\d+,\d{3} x \d[\d ]*,\d{2}\n(\d[\d ]*,\d{2})$', text)
calculated_total = sum(to_float(x) for x in item_totals)
datetime_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})', text)
date = datetime_match.group(1) if datetime_match else None
time = datetime_match.group(2) if datetime_match else None
payment_match = re.search(r'(Банковская карта|Наличные|Карта):', text)
payment_method = payment_match.group(1) if payment_match else None
result = {
    "prices": prices,
    "product_names": product_names,
    "total_amount": calculated_total,
    "date": date,
    "time": time,
    "payment_method": payment_method
}
print(json.dumps(result, ensure_ascii=False, indent=4))