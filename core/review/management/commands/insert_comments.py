import random

from django.core.management.base import BaseCommand

from accounts.models import User
from shop.models import Product
from review.models import Review


class Command(BaseCommand):
    help = "Create fake reviews for random users and products"

    COMMENTS = [
        "محصول خیلی خوبی بود و از خریدم راضی هستم.",
        "کیفیت محصول واقعاً خوب بود.",
        "محصول دقیقاً مطابق توضیحات بود.",
        "بسته بندی خوب و ارسال هم سریع بود.",
        "نسبت به قیمت، کیفیت مناسبی داره.",
        "از خرید این محصول راضی بودم.",
        "کیفیت پارچه خیلی خوبه.",
        "رنگ محصول خیلی قشنگ‌تر از چیزی بود که انتظار داشتم.",
        "سایز کاملاً مناسب بود.",
        "محصول با عکس سایت مطابقت داشت.",
        "کیفیت دوخت خیلی خوبه.",
        "در کل محصول خوب و باکیفیتی بود.",
        "انتظار کیفیت بیشتری داشتم.",
        "محصول بدی نیست ولی می‌توانست بهتر باشد.",
        "برای این قیمت انتخاب مناسبیه.",
        "خیلی خوشم اومد و دوباره خرید می‌کنم.",
        "کیفیتش عالی بود.",
        "محصول به موقع به دستم رسید.",
        "ظاهر محصول خیلی شیکه.",
        "از کیفیت و طراحی محصول راضی هستم.",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=100,
            help="Number of fake reviews to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        users = list(
            User.objects.all()
        )

        products = list(
            Product.objects.filter(
                status=1
            )
        )

        if not users:
            self.stdout.write(
                self.style.ERROR(
                    "No users found."
                )
            )
            return

        if not products:
            self.stdout.write(
                self.style.ERROR(
                    "No published products found."
                )
            )
            return

        existing_reviews = set(
            Review.objects.values_list(
                "user_id",
                "product_id"
            )
        )

        available_pairs = [
            (user.id, product.id)
            for user in users
            for product in products
            if (user.id, product.id) not in existing_reviews
        ]

        if not available_pairs:
            self.stdout.write(
                self.style.WARNING(
                    "No available user/product pairs."
                )
            )
            return

        random.shuffle(available_pairs)

        count = min(
            count,
            len(available_pairs)
        )

        reviews = []

        for user_id, product_id in available_pairs[:count]:

            reviews.append(
                Review(
                    user_id=user_id,
                    product_id=product_id,
                    rating=random.randint(1, 5),
                    comment=random.choice(
                        self.COMMENTS
                    ),
                )
            )

        Review.objects.bulk_create(
            reviews
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} fake reviews created successfully."
            )
        )