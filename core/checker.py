import re
import random
from datetime import datetime

def luhn_check(card_number: str) -> bool:
    digits = re.sub(r'\D', '', card_number)
    if len(digits) < 13 or len(digits) > 19:
        return False
    total = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        num = int(d)
        if i % 2 == 1:
            num *= 2
            if num > 9:
                num -= 9
        total += num
    return total % 10 == 0

def get_card_brand(number: str) -> str:
    patterns = {
        'VISA': r'^4',
        'MASTERCARD': r'^5[1-5]',
        'AMEX': r'^3[47]',
        'DISCOVER': r'^6(?:011|5)',
        'DINERS': r'^3(?:0[0-5]|[68])',
        'JCB': r'^(?:2131|1800|35)'
    }
    for brand, pattern in patterns.items():
        if re.match(pattern, number):
            return brand
    return 'UNKNOWN'

def generate_luhn_number(bin_prefix: str, length: int = 16) -> str:
    if len(bin_prefix) >= length:
        return bin_prefix[:length]
    number = bin_prefix
    while len(number) < length - 1:
        number += str(random.randint(0, 9))
    digits = list(number)
    total = 0
    for i, d in enumerate(digits):
        num = int(d)
        if (len(digits) - i) % 2 == 0:
            num *= 2
            if num > 9:
                num -= 9
        total += num
    check_digit = (10 - (total % 10)) % 10
    return number + str(check_digit)

def parse_cc_line(line: str):
    line = line.strip()
    if not line:
        return None
    parts = re.split(r'[|,\s]+', line)
    number = re.sub(r'\D', '', parts[0])
    if len(number) < 13:
        return None
    return {
        'number': number,
        'month': parts[1] if len(parts) > 1 else '',
        'year': parts[2] if len(parts) > 2 else '',
        'cvv': parts[3] if len(parts) > 3 else '',
        'raw': line
    }

def validate_cc_local(card: dict) -> str:
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    if card['month'] and card['year']:
        try:
            exp_month = int(card['month'])
            exp_year = int(card['year'])
            if exp_year < 100:
                exp_year += 2000
            if exp_year < current_year:
                return 'die'
            if exp_year == current_year and exp_month < current_month:
                return 'die'
        except ValueError:
            pass
    return 'live' if random.random() < 0.15 else 'die'
