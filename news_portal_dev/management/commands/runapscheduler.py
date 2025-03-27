import logging
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from news_portal_dev.models import Post, Category, Subscriber


logger = logging.getLogger(__name__)


def my_job():
    cur_time = datetime.datetime.now()
    last_week = cur_time - datetime.timedelta(days=7)
    posts = Post.objects.filter(timestamp__gte=last_week).order_by('timestamp')

    if not posts.exists():
        logger.info("Нет новых постов за неделю.")
        return

    categories = set(posts.values_list('category', flat=True))

    subscribers = set(
        Subscriber.objects.filter(category__in=categories)
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


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week='thu', hour="04", minute="01"),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'delete_old_job_executions'.")

        try:
            logger.info("Запуск планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен.")
