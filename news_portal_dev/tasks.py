from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from .models import Post, Subscriber
import datetime
import logging
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timezone

logger = logging.getLogger(__name__)
@shared_task
def send_new_post():

    instance = Post.objects.order_by('-id').first()
    category = instance.category.all()
    emails = User.objects.filter(subscriber__category__id__in=category).values_list('email', flat=True).distinct()

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

@shared_task
def send_post_1week():
    cur_time = datetime.datetime.now()
    last_week = cur_time - datetime.timedelta(days=7)
    posts = Post.objects.filter(timestamp__gte=last_week).order_by('timestamp')

    if not posts.exists():
        logger.info("Нет новых постов за неделю.")
        return

    categories = set(posts.values_list('category', flat=True))

    subscribers = set(
        Subscriber.objects.filter(category__id__in=categories)
        .values_list('user__email', flat=True)
    )

    if not subscribers:
        logger.info("Нет подписчиков для отправки.")
        return

    html_content = render_to_string(
        'weekly_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )

    msg = EmailMultiAlternatives(
        subject='Публикации за неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    logger.info(f"Рассылка отправлена {len(subscribers)} подписчикам.")