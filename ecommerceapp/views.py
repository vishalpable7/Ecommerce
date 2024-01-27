from django.shortcuts import render, redirect
from .models import Contact, Product, Order, OrderUpdates
from django.contrib import messages
from math import ceil
from ecommerceapp import keys
from django.views.decorators.csrf import  csrf_exempt
from PayTm import Checksum
MERCHANT_KEY=keys.MK
# Create your views here.
def index(request):
    return render(request,"index.html" )

# Create your views here.
def index(request):

    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)

def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        desc = request.POST['desc']
        phone_num = request.POST['pnumber']
        obj = Contact(name=name, email=email, desc=desc, phone_nubmer=phone_num)
        obj.save()
        messages.success(request,"We will look into your query, Thanks for contact us")

    return render(request,"contactus.html" )

def about(request):
    return render(request,"about.html" )

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Order(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone)
        order.save()
        # update = OrderUpdates(order_id=order.order_id,update_desc="the order has been placed")
        update_data = {'orders': order,'order_id': order.order_id,'update_desc':'the order has been placed'}
        updated = OrderUpdates.objects.create(**update_data)
        updated.save()
        thank = True
# # PAYMENT INTEGRATION

        id = Order.order_id
        oid=str(id)+"NexuKart"
        param_dict = {

            'MID':keys.MID,
            'ORDER_ID': oid,
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict': param_dict})

    return render(request, 'checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            a=response_dict['ORDERID']
            b=response_dict['TXNAMOUNT']
            rid=a.replace("NexuKart","")
            filter2= Order.objects.filter(order_id=rid)

            for post1 in filter2:
                post1.oid=a
                post1.amountpaid=b
                post1.paymentstatus="PAID"
                post1.save()

        else:
            a=response_dict['ORDERID']
            b=response_dict['TXNAMOUNT']
            rid=a.replace("NexuKart","")
            filter2= Order.objects.filter(order_id=rid)
            for post1 in filter2:
                post1.oid=a
                post1.amountpaid=b
                post1.paymentstatus="UNPAID"
                post1.save()
    return render(request, 'paymentstatus.html', {'response': response_dict})

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    # import ipdb;ipdb.set_trace()
    currentuser=request.user.email
    items=Order.objects.filter(email=currentuser)
    rid=""
    for i in items:
        myid=i.oid
        rid=myid.replace("NexuKart","")
        status=OrderUpdates.objects.filter(order_id=int(rid))
   
    context ={"items":items,"status":status}

    return render(request,"profile.html",context)

