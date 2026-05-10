import smtplib
from email.message import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import UserProfile,EmailHistory,Contact
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required(login_url='login')
def profile_view(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)

    password_form = PasswordChangeForm(user)

    if request.method == "POST":

        # Update App Password
        if "update_app_password" in request.POST:
            new_app_password = request.POST.get("app_password")

            if new_app_password:
                profile.app_password = new_app_password
                profile.save()

                return render(request, "profile.html", {
                    "success": "App password updated successfully!",
                    "password_form": password_form
                })

        # Change Login Password
        if "change_password" in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)

                return render(request, "profile.html", {
                    "success": "Login password changed successfully!",
                    "password_form": PasswordChangeForm(user)
                })

    return render(request, "profile.html", {
        "password_form": password_form
    })

# Home
def home(request):
    return render(request, "home.html")


# Register
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            app_password = form.cleaned_data.get("app_password")

            UserProfile.objects.create(
                user=user,
                app_password=app_password
            )

            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# Login (Username OR Gmail)
def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=identifier)
            username = user_obj.username
        except User.DoesNotExist:
            username = identifier

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


# Logout
def logout_view(request):
    logout(request)
    return redirect("home")


# Dashboard (Protected)
@login_required(login_url='login')
def dashboard(request):
    total_emails = EmailHistory.objects.filter(user=request.user).count()
    total_contacts = Contact.objects.filter(user=request.user).count()
    last_email = EmailHistory.objects.filter(user=request.user).order_by('-sent_at').first()

    return render(request, "dashboard.html", {
        "total_emails": total_emails,
        "total_contacts": total_contacts,
        "last_email": last_email,
    })


@login_required(login_url='login')
def compose_mail(request):
    contacts = Contact.objects.filter(user=request.user)
    prefill_email = request.GET.get("to")

    if request.method == "POST":
        recipient = request.POST.get("recipient")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not recipient or not subject or not message:
            return render(request, "compose.html", {
                "error": "All fields are required.",
                "contacts": contacts,
                "prefill_email": recipient
            })

        try:
            profile = UserProfile.objects.get(user=request.user)
            sender_email = request.user.email
            app_password = profile.app_password

            email = EmailMessage()
            email["From"] = sender_email
            email["To"] = recipient
            email["Subject"] = subject
            email.set_content(message)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(email)
            server.quit()

            # Save history
            EmailHistory.objects.create(
                user=request.user,
                recipient=recipient,
                subject=subject,
                message=message
            )

            return render(request, "compose.html", {
                "success": "Email sent successfully!",
                "contacts": contacts
            })

        except Exception as e:
            return render(request, "compose.html", {
                "error": f"Error: {str(e)}",
                "contacts": contacts,
                "prefill_email": recipient
            })

    return render(request, "compose.html", {
        "contacts": contacts,
        "prefill_email": prefill_email
    })


@login_required(login_url='login')
def email_history(request):
    emails = EmailHistory.objects.filter(user=request.user).order_by('-sent_at')
    contacts = Contact.objects.filter(user=request.user)

    contact_dict = {c.email: c.name for c in contacts}

    # Attach contact_name to each email object
    for email in emails:
        email.contact_name = contact_dict.get(email.recipient)

    return render(request, "history.html", {
        "emails": emails,
    })


@login_required(login_url='login')
def contacts_view(request):
    contacts = Contact.objects.filter(user=request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")

        Contact.objects.create(
            user=request.user,
            name=name,
            email=email
        )
        return redirect("contacts")

    return render(request, "contacts.html", {"contacts": contacts})


@login_required(login_url='login')
def delete_contact(request, contact_id):
    contact = Contact.objects.get(id=contact_id, user=request.user)
    contact.delete()
    return redirect("contacts")


@login_required(login_url='login')
def view_email(request, id):
    email = EmailHistory.objects.get(id=id, user=request.user)
    return render(request, "view_email.html", {"email": email})