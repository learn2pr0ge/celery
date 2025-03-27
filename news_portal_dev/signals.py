from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import PostCategory


@receiver(m2m_changed, sender=PostCategory)
def create_post(instance, **kwargs):
    if not kwargs['action'] == 'post_add':
         return

    category = instance.category.all()
    emails = User.objects.filter(subscriber__category__in=category).values_list('email', flat=True).distinct()

    subject = f'Вышла новая новость в категории: {instance.category}'

    text_content = (
        f'{instance.content}\n\n'
        f'Ссылка: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )

    html_content = (
        f'<h3>{instance.title}</h3>'
        f'<p>{instance.content}</p>'
        f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">Читать далее</a>'
    )

    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
