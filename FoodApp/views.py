from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Products, Cart, Orders

# Dummy SMS function (replace with real integration like Twilio)
def send_sms(to_number, message):
    print(f"SMS to {to_number}: {message}")

def home(request):
    products = Products.objects.all()
    context = {'products': products}
    return render(request, "home.html", context)

def loginPage(request):
    
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            user = User.objects.filter(email = email).first()
            if not user:
                messages.warning(request, "Please enter valid Email !")
                return redirect("/login/")

            if not user.check_password(password):
                messages.warning(request, "Invalid Password !")
                return redirect("/login/")

            messages.success(request, "Login Successfully !")
            login(request, user)
            return redirect("/")

            

    except Exception as e:
        print(e)

    return render(request, "login.html")

def signup(request):
    try:
        if request.method == "POST":
            username = request.POST.get("uname")
            email = request.POST.get("email")
            password = request.POST.get("password")
            
            user = User.objects.filter(email = email)
            if user.exists():
                messages.warning(request, "Email already Exist, please your valid Email !")
                return redirect("/signup/")

            setUser = User(username = username , email = email)
            setUser.set_password(password)
            setUser.save()

            userData = User.objects.get(username = username)
            setProfile = Profile.objects.create(user = userData, id_user = userData.id)
            setProfile.save()

            send_mail(
                subject='Welcome to FastFood Express!',
                message=f'Hi {username}, thank you for signing up at FastFood Express!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, f"{username}, Signup Successfully !")
            
            return redirect("/login/")


    except Exception as e:
        print(e)
        messages.warning(request, "Something Wrong, Please try again later!",)

    return render(request, "signup.html")

@login_required(login_url="/login/")
def updateProfile(request, pk):
    user = User.objects.get(id=pk)
    profile, created = Profile.objects.get_or_create(id_user=pk, user=user)
    if request.method == "POST":
        data = request.POST

        name = data.get('uname')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zipcode')

        user.username = name
        profile.city = city
        profile.state = state
        profile.zip_code = zip_code
        user.save()
        profile.save()

        messages.success(request, f"{name}, Profile updated successfully !")
        return redirect('/')
    
    return render(request, "update.html", {'user': user, 'profile': profile})



@login_required(login_url="/login/")
def mycart(request, pk):

    cartItem = Cart.objects.filter(id_user = pk)
    product_ids = [item.product.id for item in cartItem]
    products = Products.objects.filter(id__in=product_ids)

    try:
        if request.method == 'POST':
            unit = request.POST.get('unit')
            productId = request.POST.get('productId')
            return redirect(reverse('orderNow', kwargs={'unit': unit, 'product_id': productId}))

    except Exception as e:
        print(e)

    context = {'products': products}

    return render(request, "mycart.html", context)

@login_required(login_url="/login/")
def orders(request, pk):
    user = User.objects.get(id = pk)
    order = Orders.objects.filter(user = user)
    context = {'orders': order}

    if request.method == "POST":
        rating = request.POST.get('rating')
        order_id = request.POST.get('orderId')

        if not rating:
            messages.info(request,'First, give a rating to products that were ordered before this product!')
            return render(request, "orders.html", context)

        order = Orders.objects.filter(id = order_id).order_by('-id').first()
        order.rating = rating
        order.save()
        try:
                
            userCount = Orders.objects.filter(product = order.product , rating__gt=0).count()
            total_rating = Orders.objects.filter(product = order.product).aggregate(Sum('rating'))['rating__sum']
            setProduct = Products.objects.get(product = order.product)
            if userCount > 0:
                setProduct.users = userCount
                # Calculate the new average rating
                setProduct.rating = round(total_rating / userCount, 1)
            else:
                setProduct.users = 0
                setProduct.rating = 0

            setProduct.save()

            

        except Exception as e:
            print("Ex >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ", e)
    
    

    return render(request, "orders.html", context)

@login_required(login_url="/login/")
def logoutPage(request):
    logout(request)
    messages.success(request, "Logout Successfully !")
    return redirect("/login/")

@login_required(login_url="/login/")
def addCart(request, pk , pid):

    product = Products.objects.get(id = pid)
    user = User.objects.get(id = pk)

    checkCart = Cart.objects.filter(id_user = user.id, id_product = product.id)
    if checkCart.exists():
        messages.info(request,f"{product} , Already present in Cart!")
        return redirect("/")


    setCart = Cart(product = product, user = user, id_user = user.id, id_product = product.id)
    setCart.save()

    messages.success(request,f"{product} Added to cart Successfully!")

    return redirect("/")

def removeCart(request, pk, pid):

    cart_item = Cart.objects.get(id_user = pk , id_product = pid)
    cart_item.delete()

    messages.success(request,f"Product removed from cart Successfully!")

    return redirect('/')


def orderNow(request, unit, product_id):
    try:
        if request.method == "POST":
            userId = request.POST.get('userId')
            number = request.POST.get('pnumber')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zipcode')

            user = User.objects.get(id = userId)
            product = Products.objects.get(id = product_id)
            total = (product.price * unit)

            setOrder = Orders(user = user, product = product, phone = number, city = city, state = state,
            zip_code = zip_code, item_count = unit, item_price = product.price, total_price = total)
            setOrder.save()

            cartProduct = Cart.objects.get(id_product = product_id, id_user = userId)
            cartProduct.delete()

            send_mail(
                subject='Order Confirmation',
                message=f'Hi {user.username}, your order for {product.name} has been placed successfully. Total: ₹{total}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            send_sms(
                to_number=number,  # Must include country code, e.g., +91XXXXXXXXXX
                message=f'Hi {user.username}, your order for {product.name} was placed. Total: ₹{total}'
            )

            messages.success(request,f"{product}, Ordered successfully!")
            return redirect('/')


            
    except Exception as e:
        print(e)
    return render(request, "orderForm.html", {'unit': unit, 'product_id': product_id})

