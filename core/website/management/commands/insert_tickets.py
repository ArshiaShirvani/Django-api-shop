import random

from faker import Faker
from django.core.management.base import BaseCommand

from website.models import ContactMessage


class Command(BaseCommand):

    help = "Create fake contact messages"

    def handle(self, *args, **options):

        fake = Faker("fa_IR")

        subjects = [
            "پیگیری سفارش",
            "مشکل در ثبت سفارش",
            "سوال درباره محصول",
            "مشکل در پرداخت",
            "درخواست راهنمایی",
            "استعلام قیمت",
            "مشکل در ورود به حساب",
            "پیشنهاد برای سایت",
            "گزارش مشکل",
            "سوال درباره ارسال",
        ]

        messages = [
            "سلام، میخواستم درباره وضعیت سفارش خودم اطلاعات بیشتری دریافت کنم.",
            "سلام، هنگام ثبت سفارش با مشکل مواجه شدم. لطفاً راهنمایی کنید.",
            "سلام، آیا این محصول موجود هست و امکان ارسال آن وجود دارد؟",
            "سلام، هنگام پرداخت مبلغ سفارش با خطا مواجه شدم.",
            "سلام، میخواستم اطلاعات بیشتری درباره این محصول دریافت کنم.",
            "سلام، لطفاً درباره نحوه ارسال سفارش و زمان تحویل راهنمایی کنید.",
            "سلام، آیا امکان تغییر آدرس ارسال بعد از ثبت سفارش وجود دارد؟",
            "سلام، پیشنهاد دارم بخش محصولات سایت کمی کامل‌تر شود.",
            "سلام، در هنگام استفاده از سایت با یک مشکل مواجه شدم.",
            "سلام، میخواستم درباره شرایط خرید و ارسال سفارش سوال کنم.",
        ]

        created_count = 0

        for i in range(10):

            message = ContactMessage.objects.create(

                name=fake.name(),

                subject=random.choice(
                    subjects
                ),

                phone=fake.phone_number(),

                email=(
                    fake.email()
                    if random.choice([True, False])
                    else ""
                ),

                message=random.choice(
                    messages
                ),

                seen=random.choice(
                    [True, False]
                ),

            )

            created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {message.name} - "
                    f"{message.subject}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created "
                f"{created_count} contact messages."
            )
        )