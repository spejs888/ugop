from functools import reduce
from decimal import Decimal

def calculate_subtotal(order_items):
    """Користи sum со Decimal почетна вредност за да не дојде до TypeError при додавање Decimal и int."""
    totals = (item.product.price * item.quantity for item in order_items)
    return sum(totals, Decimal('0.00'))

def calculate_tax(amount, tax_rate=Decimal('0.18')):
    """Пресметува ДДВ користејќи Decimal. Враќа износ на данок за дадена сума."""
    if not isinstance(tax_rate, Decimal):
        tax_rate = Decimal(str(tax_rate))
    return (amount * tax_rate).quantize(Decimal('0.01'))

def apply_discount(amount, discount_percentage):
    """Ја намалува сумата за одреден процент. Работи со Decimal."""
    if not discount_percentage:
        return amount
    discount = Decimal(discount_percentage)
    return (amount * (Decimal('1') - (discount / Decimal('100')))).quantize(Decimal('0.01'))

def get_full_bill_data(order):
    """Главна функција која ги спојува пресметките во речник.

    Важно: final_total е сумата која гостинoт ја плаќа (без ДДВ). ДДВ се пресметува
    и вклучена како `tax_amount`, но не се додава на final_total — газдата го плаќа ДДВ-то.
    """
    TAX_RATE = Decimal('0.18')  # 18% стандардна стапка во Македонија

    items = list(order.items.all())
    subtotal = calculate_subtotal(items)
    with_discount = apply_discount(subtotal, order.discount_percent)
    tax_amount = calculate_tax(with_discount, TAX_RATE)
    final_total = with_discount  # Гостите плаќаат нето (без ДДВ)
    
    return {
        'subtotal': subtotal,
        'discount_applied': (subtotal - with_discount).quantize(Decimal('0.01')),
        'tax_amount': tax_amount,
        'final_total': final_total,
        'tax_percent': int((TAX_RATE * Decimal('100')).to_integral_value()),
    }