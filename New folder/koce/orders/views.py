from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse
from .models import Order, Product, OrderItem
from .logic import get_full_bill_data
from decimal import Decimal
from django.core import serializers

@login_required
def dashboard(request):
    """Преглед на сите активни нарачки за сите корисници (Конкурентност)."""
    active_orders = Order.objects.exclude(status='PAID').order_by('-created_at')
    return render(request, 'orders/dashboard.html', {'orders': active_orders})

@login_required
def create_order(request):
    """Креирање нова нарачка од келнер."""
    if request.method == "POST":
        table = request.POST.get('table_number')
        try:
            table_number = int(table)
        except (TypeError, ValueError):
            table_number = 0
        order = Order.objects.create(table_number=table_number, waiter=request.user)
        return redirect('order_detail', order_id=order.id)
    return render(request, 'orders/create_order.html')

@login_required
def order_detail(request, order_id):
    """Детален приказ со пресметки во реално време."""
    order = get_object_or_404(Order, pk=order_id)
    bill_data = get_full_bill_data(order)
    products = Product.objects.all()
    
    context = {
        'order': order,
        'items': order.items.all(),
        'products': products,
        **bill_data # Ги додава subtotal, tax_amount и final_total во контекстот
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def add_item(request, order_id):
    """Додавање ставка во нарачка (поддржува и AJAX)."""
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        qty = request.POST.get('quantity', 1)
        try:
            product = Product.objects.get(pk=int(product_id))
            quantity = int(qty)
            if quantity < 1:
                quantity = 1
        except (Product.DoesNotExist, ValueError, TypeError):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False}, status=400)
        item, created = OrderItem.objects.get_or_create(order=order, product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()

        # Ideally trigger printing to the correct station here (out of scope)
    return redirect('order_detail', order_id=order.id)

@login_required
def remove_item(request, order_id, item_id):
    """Отстранување ставка од нарачка. Само staff (газда) може да брише ставки."""
    if not request.user.is_staff:
        return HttpResponseForbidden('Немаш права за оваа операција')
    order = get_object_or_404(Order, pk=order_id)
    try:
        item = OrderItem.objects.get(pk=item_id, order=order)
        item.delete()
    except OrderItem.DoesNotExist:
        pass
    return redirect('order_detail', order_id=order.id)

@login_required
def print_fiscal(request, order_id):
    """Печатење на фискална сметка (вклучува пресметано ДДВ како информација)."""
    order = get_object_or_404(Order, pk=order_id)
    bill = get_full_bill_data(order)
    return render(request, 'orders/print_fiscal.html', {'order': order, **bill})

@login_required
def print_cash(request, order_id):
    """Печатење на готовинска сметка каде ДДВ е означено како 0% (приказ за плаќање готовина)."""
    order = get_object_or_404(Order, pk=order_id)
    bill = get_full_bill_data(order)
    # show tax as 0% on cash receipt (display only) — guest pays final_total, tax shown 0
    cash_total = bill['final_total']
    cash_tax = Decimal('0.00')
    return render(request, 'orders/print_cash.html', {'order': order, **bill, 'cash_total': cash_total, 'cash_tax': cash_tax})

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """Страница за газдата/админ кој може да ги следи активностите на келнерите и да брише ставки."""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/admin_dashboard.html', {'orders': orders})

@login_required
def pici_queue(request):
    """Печатење/приказ за пици (станица на пици)."""
    items = OrderItem.objects.filter(product__category__name='Пици').order_by('order__created_at')
    return render(request, 'orders/kitchen_pici.html', {'items': items})

@login_required
def kitchen_queue(request):
    """Приказ за салати и главни јадења (кујна)."""
    items = OrderItem.objects.filter(product__category__name__in=['Салати','Главни Јадења']).order_by('order__created_at')
    return render(request, 'orders/kitchen_kitchen.html', {'items': items})

def bar_queue(request):
    """Приказ за пијалаци (бар). Барот може да ја користи оваа страница, нема потреба од акаунт за печатење на маркчиња."""
    items = OrderItem.objects.filter(product__category__name='Пијалаци').order_by('order__created_at')
    return render(request, 'orders/kitchen_bar.html', {'items': items})

@login_required
def api_pici(request):
    """API endpoint: враќа JSON со небараните/активните ставки за категоријата 'Пици'."""
    items = OrderItem.objects.filter(product__category__name='Пици').order_by('order__created_at')
    data = []
    for it in items:
        data.append({
            'order_id': it.order.id,
            'product': it.product.name,
            'quantity': it.quantity,
            'created': it.order.created_at.isoformat(),
        })
    return JsonResponse({'items': data})

@login_required
def api_kitchen(request):
    """API endpoint for salads and main dishes."""
    items = OrderItem.objects.filter(product__category__name__in=['Салати','Главни Јадења']).order_by('order__created_at')
    data = []
    for it in items:
        data.append({
            'order_id': it.order.id,
            'product': it.product.name,
            'quantity': it.quantity,
            'created': it.order.created_at.isoformat(),
        })
    return JsonResponse({'items': data})

def api_bar(request):
    """API endpoint for drinks (no auth) so bar devices can poll."""
    items = OrderItem.objects.filter(product__category__name='Пијалаци').order_by('order__created_at')
    data = []
    for it in items:
        data.append({
            'order_id': it.order.id,
            'product': it.product.name,
            'quantity': it.quantity,
            'created': it.order.created_at.isoformat(),
        })
    return JsonResponse({'items': data})

@login_required
def kitchen_realtime(request):
    return render(request, 'orders/kitchen_realtime.html')

@login_required
def table_view(request, table_number):
    """Прикажува сите нарачки за дадена маса и вкупна цена за сите нив."""
    orders_qs = Order.objects.filter(table_number=table_number).order_by('-created_at')
    orders_data = []
    total_for_table = Decimal('0.00')
    total_items = 0
    for o in orders_qs:
        bill = get_full_bill_data(o)
        orders_data.append({'order': o, **bill})
        # final_total е без ДДВ (гостин плаќа), но ќе сумираме таа вредност
        total_for_table += bill.get('final_total', Decimal('0.00'))
        total_items += sum(item.quantity for item in o.items.all())

    context = {
        'table_number': table_number,
        'orders_data': orders_data,
        'total_for_table': total_for_table,
        'total_items': total_items,
    }
    return render(request, 'orders/table_view.html', context)

@user_passes_test(lambda u: u.is_staff)
def manager_report(request):
    """Приказ достапен само за администратори (менаџмент)."""
    total_revenue = sum((get_full_bill_data(o)['final_total'] for o in Order.objects.filter(status='PAID')), Decimal('0.00'))
    paid_orders = Order.objects.filter(status='PAID').order_by('-updated_at')
    return render(request, 'orders/report.html', {'revenue': total_revenue, 'paid_orders': paid_orders})