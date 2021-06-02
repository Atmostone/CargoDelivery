from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from CargoDelivery import settings
from apps.company.models import Company, WorkerProfile
from apps.main.tasks import send_email_celery, send_many_email_celery


class Country(models.Model):
    """
    Model of country
    """
    name = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return self.name


class City(models.Model):
    """
    Model of city in country
    """
    name = models.CharField(max_length=100, verbose_name='Название')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Страна')

    def __str__(self):
        return f'{self.name} ({self.country.name})'


class Warehouse(models.Model):
    """
    Model of warehouse in city
    """
    address = models.CharField(max_length=250, verbose_name='Адрес')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')

    def __str__(self):
        return f'{self.address} ({self.city.name}, {self.city.country.name})'


class Order(models.Model):
    """
    Model of order
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    departure_city = models.ForeignKey(City, on_delete=models.CASCADE,
                                       related_name='order_departure_city', verbose_name='Город отправления')
    arrival_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='order_arrival_city',
                                     verbose_name='Город получения')

    sender_fullname = models.CharField(max_length=100, verbose_name='ФИО отправителя')
    recipient_fullname = models.CharField(max_length=100, verbose_name='ФИО получателя')

    direct_take = models.BooleanField(verbose_name='Нужно ли забрать от отправителя?')
    direct_take_address = models.CharField(max_length=250, blank=True, verbose_name='Адрес отправителя')

    direct_deliver = models.BooleanField(verbose_name='Нужно ли доставить получателю?')
    direct_deliver_address = models.CharField(max_length=250, blank=True, verbose_name='Адрес получателя')

    departure_date = models.DateField(verbose_name='Дата отправления')

    CARGO_TYPE_SET = (
        ('PACK', 'Упаковка'),
        ('BARE', 'Без упаковки'),
    )

    cargo_type = models.CharField(max_length=4, choices=CARGO_TYPE_SET, verbose_name='Тип груза')

    cargo_len = models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Длина груза (см)')
    cargo_width = models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Ширина груза (см)')
    cargo_depth = models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Глубина груза (см)')

    cargo_weight = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Вес груза (кг)')

    insurance_price = models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Стоимость страховки (руб)')

    additional_info = models.TextField(max_length=5000, blank=True, verbose_name='Дополнительная информация')

    @property
    def cargo_volume(self):
        """
        :return: volume of cargo in m^3
        """
        return round(self.cargo_len * self.cargo_width * self.cargo_depth, 2) / 1000000

    def __str__(self):
        return f'Заказ №{self.id}. ({self.sender_fullname}.' \
               f' {self.departure_city} -> {self.arrival_city}. {self.recipient_fullname}) . {self.departure_date}'

    cargo_volume.fget.short_description = 'Объём груза (м^3)'


class Transport(models.Model):
    """
    Model of transport
    """
    TRANSPORT_TYPE_SET = (
        ('CAR', 'Грузовик'),
        ('TRAIN', 'Поезд'),
        ('PLANE', 'Самолёт'),
        ('SHIP', 'Корабль'),
    )
    transport_type = models.CharField(max_length=5, choices=TRANSPORT_TYPE_SET, verbose_name='Тип транспорта')
    number = models.CharField(max_length=20, blank=True, verbose_name='Название или номер транспорта')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')

    def __str__(self):
        return f'{self.company}. {self.get_transport_type_display()} ({self.number})'


class Sending(models.Model):
    """
    Model of sending
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания')

    departure_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE,
                                            related_name='sending_departure_warehouse',
                                            verbose_name='Склад отправления')
    departure_date = models.DateField(verbose_name='Дата отправления')

    arrival_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='sending_arrival_warehouse',
                                          verbose_name='Склад получения')

    arrival_date = models.DateField(verbose_name='Дата получения')

    total_volume = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Общий объём в м^3')

    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, verbose_name='Транспорт')

    orders = models.ManyToManyField(Order, blank=True, verbose_name='Заказы')

    price_for_m3 = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за кубометр')

    @property
    def free_volume(self):
        """
        :return: difference between total volume and sum of all orders volume in m^3
        """
        summ = sum([order.cargo_volume for order in self.orders.all()])
        return self.total_volume - round(summ, 2)

    @property
    def days(self):
        """
        Calculate number of days between departure and arrival
        """
        days_list = ['день', 'дня', 'дней']
        num_days = (self.arrival_date - self.departure_date).days
        if num_days % 10 == 1 and num_days % 100 != 11:
            p = 0
        elif 2 <= num_days % 10 <= 4 and (num_days % 100 < 10 or num_days % 100 >= 20):
            p = 1
        else:
            p = 2
        return f'{num_days} {days_list[p]}'

    def __str__(self):
        return f'Отправление №{self.id}. {self.company}. {self.departure_warehouse} -> {self.arrival_warehouse}.' \
               f' {self.departure_date} -> {self.arrival_date} '

    free_volume.fget.short_description = 'Свободное место (м^3)'


class Application(models.Model):
    """
    Model of order application
    """
    order = models.OneToOneField(to=Order, on_delete=models.CASCADE, verbose_name='Заказ')
    sending = models.ForeignKey(Sending, on_delete=models.CASCADE, verbose_name='Отправление')

    STATUS_SET = (
        ('WAIT', 'Ожидается подтверждение'),
        ('CONF', 'Подтверждено'),
        ('DECL', 'Отклонено'),

    )
    status = models.CharField(max_length=4, choices=STATUS_SET, default='WAIT', verbose_name='Статус')

    info = models.CharField(max_length=1000, blank=True, verbose_name='Информация по заявке')

    @property
    def price(self):
        """
        :return: calculated price, according to order volume and price of sending
        """
        return round(float(self.order.cargo_volume) * float(self.sending.price_for_m3), 2)

    def __str__(self):
        return f'{self.get_status_display()}. {self.order}. {self.sending}'


class TransitPoint(models.Model):
    sending = models.ForeignKey(Sending, on_delete=models.CASCADE,
                                verbose_name='Отправление')
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE,
                                  verbose_name='Транспорт (до следующего пункта маршрута)')
    arrival_date = models.DateField(verbose_name='Дата прибытия (в данный пункт)')

    arrival_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE,
                                     verbose_name='Транзитный склад')

    def __str__(self):
        return f'Транзитный пункт. {self.sending}, {self.transport}, {self.arrival_date}, {self.arrival_warehouse}'


@receiver(post_save, sender=Sending)
def new_sendings_email(sender, instance, created, **kwargs):
    """
    Signal for sending emails with new sendings (for users)
    """
    if created:

        for order in Order.objects.filter(departure_city=instance.departure_warehouse.city,
                                          arrival_city=instance.arrival_warehouse.city,
                                          departure_date=instance.departure_date):

            need_send = False
            try:
                # Check for application doesn't exists
                if order.application:
                    pass
            except ObjectDoesNotExist:
                need_send = True
            else:
                # Check for application doesn't confirmed
                if order.application.status != 'CONF':
                    need_send = True

            if need_send:
                user_email = order.user.email
                subject = 'Для вашего заказа доступно новое отправление'
                html_message = render_to_string('emails/new_sending.html',
                                                {'order': order, 'sending': instance, 'SITE_URL': settings.SITE_URL})
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                send_email_celery.delay(subject, plain_message, from_email, user_email, html_message)


@receiver(post_save, sender=Application)
def application_status_email(sender, instance, created, **kwargs):
    """
    Signal for sending emails when manager change its status (for users)
    """
    status = ''
    if instance.status == 'CONF':
        status = 'Подтверждено'
    elif instance.status == 'DECL':
        status = 'Отклонено'

    if status:
        user_email = instance.order.user.email
        order = Order.objects.get(application=instance)
        sending = Sending.objects.get(application=instance)
        subject = 'Обновлён статус заявки'
        html_message = render_to_string('emails/application_status.html',
                                        {'status': status, 'order': order, 'sending': sending,
                                         'SITE_URL': settings.SITE_URL})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        send_email_celery.delay(subject, plain_message, from_email, user_email, html_message)


@receiver(post_save, sender=Application)
def application_created_email(sender, instance, created, **kwargs):
    """
    Signal for sending emails when new application created (for workers)
    """
    if created:
        emails = []
        workers_list = WorkerProfile.objects.filter(company__sending__application=instance)
        for worker in workers_list:
            emails.append(worker.user.email)

        order = Order.objects.get(application=instance)
        sending = Sending.objects.get(application=instance)
        subject = 'Появилась новая заявка для вашей компании'
        html_message = render_to_string('emails/application_created.html',
                                        {'order': order, 'sending': sending, 'application': instance,
                                         'SITE_URL': settings.SITE_URL})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        send_many_email_celery.delay(subject, plain_message, from_email, emails, html_message)
