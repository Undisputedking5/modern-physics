from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Order, OrderItem, MpesaTransaction
from cart.models import CartItem
from .utils import initiate_stk_push
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:view_cart')
    
    total = sum(item.total_price for item in cart_items)
    return render(request, 'payments/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def process_payment(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            messages.error(request, "Phone number is required.")
            return redirect('payments:checkout')

        # Clean phone number (convert 07... or +254... to 254...)
        phone_number = ''.join(filter(str.isdigit, str(phone_number)))
        
        if phone_number.startswith('07'):
            phone_number = '2547' + phone_number[2:]
        elif phone_number.startswith('01'):
            phone_number = '2541' + phone_number[2:]
        elif phone_number.startswith('7'):
            phone_number = '2547' + phone_number[1:]
        elif phone_number.startswith('1'):
            phone_number = '2541' + phone_number[1:]
        elif phone_number.startswith('254'):
            pass # Already in correct format
        
        # Ensure it's 12 digits (Safaricom requirement)
        if len(phone_number) != 12:
            messages.error(request, f"Invalid phone number format: {phone_number}. Please use 07XXXXXXXX or 2547XXXXXXXX.")
            return redirect('payments:checkout')
        
        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.total_price for item in cart_items)

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status='pending'
        )

        # Create OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                resource=item.resource,
                title=item.resource.title,
                price=item.resource.price,
                quantity=item.quantity
            )

        # Initiate STK Push — M-Pesa requires a public HTTPS callback (not localhost).
        public_base = getattr(settings, "PUBLIC_SITE_URL", "") or ""
        if public_base:
            callback_url = public_base.rstrip("/") + reverse("payments:mpesa_callback")
        else:
            callback_url = request.build_absolute_uri(reverse("payments:mpesa_callback"))

        if "127.0.0.1" in callback_url or "localhost" in callback_url:
            messages.error(
                request,
                "M-Pesa cannot reach localhost. Deploy the app and set PUBLIC_SITE_URL to your "
                "HTTPS site (e.g. https://your-app.vercel.app), or use a tunnel URL while testing.",
            )
            order.delete()
            return redirect("payments:checkout")

        response = initiate_stk_push(phone_number, total, callback_url, order.id)

        if response is None:
            order.status = "failed"
            order.save()
            messages.error(
                request,
                "Payment service is unavailable. Check M-Pesa credentials in the environment or admin, "
                "and server logs for details.",
            )
            return redirect("payments:checkout")

        rc = response.get("ResponseCode")
        if rc == "0" or rc == 0:
            MpesaTransaction.objects.create(
                order=order,
                merchant_request_id=response.get('MerchantRequestID'),
                checkout_request_id=response.get('CheckoutRequestID'),
                amount=total,
                phone_number=phone_number,
                status='Sent'
            )
            # Clear cart? No, wait for successful payment.
            return redirect('payments:payment_status', order_id=order.id)
        else:
            order.status = "failed"
            order.save()
            err_msg = "Failed to initiate payment. Please try again."
            if response:
                err_msg = response.get("CustomerMessage") or response.get("errorMessage") or err_msg
            messages.error(request, err_msg)
            return redirect("payments:checkout")

    return redirect('cart:view_cart')

@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return HttpResponse("OK")

    try:
        data = json.loads(request.body.decode("utf-8") if request.body else "{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.exception("M-Pesa callback invalid JSON: %s", e)
        return HttpResponse("Bad Request", status=400)

    logger.info("M-Pesa Callback Data: %s", data)

    stk_callback = data.get("Body", {}).get("stkCallback", {})
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")

    if not checkout_request_id:
        logger.error("M-Pesa callback missing CheckoutRequestID")
        return HttpResponse("OK")

    try:
        transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
    except MpesaTransaction.DoesNotExist:
        logger.error("Transaction not found for CheckoutRequestID: %s", checkout_request_id)
        return HttpResponse("OK")

    transaction.result_code = result_code
    transaction.result_desc = result_desc

    if result_code in (0, "0"):
        transaction.status = "Success"
        callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        for item in callback_metadata:
            if item.get("Name") == "MpesaReceiptNumber":
                transaction.mpesa_receipt_number = item.get("Value")
                break

        order = transaction.order
        order.status = "completed"
        order.save()

        CartItem.objects.filter(user=order.user).delete()
    else:
        transaction.status = "Failed"
        transaction.order.status = "failed"
        transaction.order.save()

    transaction.save()

    return HttpResponse("OK")

@login_required
def payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/payment_status.html', {'order': order})
