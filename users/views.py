from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .tokens import email_confirmation_token
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from django.db import transaction

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Деактивируем пользователя до подтверждения почты

            try:
                with transaction.atomic():
                    user.save()  # Сохраняем пользователя, чтобы получить pk

                    # Генерация и отправка письма
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = email_confirmation_token.make_token(user)
                    confirm_url = request.build_absolute_uri(
                        reverse('email_confirm', kwargs={'uidb64': uid, 'token': token})
                    )
                    email_html_message = render_to_string('users/emails/email_confirmation_sent.html', {
                        'user': user,
                        'confirm_url': confirm_url,
                        'domain': request.build_absolute_uri(reverse('home')).rstrip('/'),
                        'current_year': datetime.now().year,
                    })
                    email = EmailMessage(
                        subject='Подтверждение регистрации',
                        body=email_html_message,
                        from_email='"Dalv" <noreply@yourdomain.com>',
                        to=[user.email],
                    )
                    email.content_subtype = 'html'
                    email.send(fail_silently=False)

                return redirect('email_confirmation')
            except Exception as e:
                # Обработка ошибки отправки письма
                form.add_error(None, "Произошла ошибка при отправке письма. Пожалуйста, попробуйте снова.")
                # Опционально: удалить пользователя, если письмо не отправлено
                user.delete()
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def email_confirmation(request):
    return render(request, 'users/email_confirmation.html')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError, UnicodeDecodeError):
        user = None

    if user is not None and email_confirmation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Ваш аккаунт успешно активирован!')
        return redirect('home')
    else:
        messages.error(request, 'Ссылка активации недействительна или устарела!')
        return redirect('register')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Проверяем, активен ли пользователь
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Ваш аккаунт не активирован. Проверьте вашу почту.')
                return redirect('login')
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
