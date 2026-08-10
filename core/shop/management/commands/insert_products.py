import random
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from faker import Faker

from shop.models import (
    Product,
    ProductCategory,
    ProductColor,
    ProductImages,
    ProductSize,
    ProductStatus,
    ProductVariant,
    Feature,
    FeatureValue,
)


class Command(BaseCommand):

    help = "Generate random fake shop data"

    def handle(self, *args, **options):

        fake = Faker("fa_IR")

        # ==========================================
        # Project root / Images
        # ==========================================

        PROJECT_ROOT = Path(__file__).resolve().parents[3]

        images_dir = PROJECT_ROOT / "fake_data" / "images"

        # تصاویر عمومی سایت که نباید برای محصولات استفاده شوند
        excluded_images = {
            "banner1.png",
            "banner2.png",
            "banner3.png",
            "banner4.png",
            "banner5.png",
            "secendery_pic.png",
        }

        images_list = [
            image
            for image in images_dir.glob("*.*")
            if (
                image.suffix.lower()
                in [".jpg", ".jpeg", ".png", ".webp"]
                and image.name.lower()
                not in {
                    name.lower()
                    for name in excluded_images
                }
            )
        ]

        self.stdout.write(
            f"Looking for product images in: {images_dir}"
        )

        self.stdout.write(
            f"Product images found: {len(images_list)}"
        )

        if not images_list:

            self.stdout.write(
                self.style.ERROR(
                    f"No product images found in {images_dir}"
                )
            )

            return

        # ==========================================
        # Base data
        # ==========================================

        self.create_base_data()

        categories = list(
            ProductCategory.objects.all()
        )

        sizes = list(
            ProductSize.objects.all()
        )

        colors = list(
            ProductColor.objects.all()
        )

        features = list(
            Feature.objects.all()
        )

        # ==========================================
        # Products
        # ==========================================

        products = []

        for _ in range(20):

            title = self.generate_product_title(
                fake
            )

            slug = self.generate_unique_slug(
                title
            )

            products.append(
                Product(
                    title=title,
                    slug=slug,

                    brief_description=fake.sentence(
                        nb_words=random.randint(
                            5,
                            10
                        )
                    ),

                    description=fake.paragraph(
                        nb_sentences=random.randint(
                            3,
                            7
                        )
                    ),

                    status=random.choice([
                        ProductStatus.PUBLISHED,
                        ProductStatus.PUBLISHED,
                        ProductStatus.PUBLISHED,
                        ProductStatus.DRAFT,
                    ]),
                )
            )

        created_products = Product.objects.bulk_create(
            products
        )

        # ==========================================
        # Categories
        # ==========================================

        for product in created_products:

            count = random.randint(
                1,
                min(
                    3,
                    len(categories)
                )
            )

            selected_categories = random.sample(
                categories,
                count
            )

            product.categories.set(
                selected_categories
            )

        # ==========================================
        # Images
        # ==========================================

        images_to_create = []

        for product in created_products:

            number_of_images = random.randint(
                1,
                min(
                    4,
                    len(images_list)
                )
            )

            selected_images = random.sample(
                images_list,
                number_of_images
            )

            for index, image_path in enumerate(
                selected_images
            ):

                with open(
                    image_path,
                    "rb"
                ) as image_file:

                    image_data = image_file.read()

                images_to_create.append(
                    ProductImages(
                        product=product,

                        image=ContentFile(
                            image_data,
                            name=image_path.name
                        ),

                        is_main=(
                            index == 0
                        ),
                    )
                )

        ProductImages.objects.bulk_create(
            images_to_create
        )

        # ==========================================
        # Variants
        # ==========================================

        variants_to_create = []

        for product in created_products:

            combinations = [
                (size, color)
                for size in sizes
                for color in colors
            ]

            random.shuffle(
                combinations
            )

            number_of_variants = random.randint(
                1,
                min(
                    6,
                    len(combinations)
                )
            )

            selected_combinations = combinations[
                :number_of_variants
            ]

            for size, color in selected_combinations:

                price = random.randrange(
                    300_000,
                    8_000_000,
                    50_000
                )

                discount = random.choice([
                    0,
                    0,
                    0,
                    5,
                    10,
                    15,
                    20,
                    25,
                    30,
                ])

                stock = random.randint(
                    0,
                    50
                )

                variants_to_create.append(
                    ProductVariant(
                        product=product,
                        size=size,
                        color=color,

                        price=price,

                        discount_percent=discount,

                        stock=stock,

                        sku=self.generate_unique_sku(),

                        is_active=random.choice([
                            True,
                            True,
                            True,
                            False,
                        ]),
                    )
                )

        ProductVariant.objects.bulk_create(
            variants_to_create
        )

        # ==========================================
        # Feature Values
        # ==========================================

        feature_values = []

        for product in created_products:

            selected_features = random.sample(
                features,
                random.randint(
                    2,
                    min(
                        5,
                        len(features)
                    )
                )
            )

            for feature in selected_features:

                value = self.generate_feature_value(
                    feature.title
                )

                feature_values.append(
                    FeatureValue(
                        product=product,
                        feature=feature,
                        value=value,
                    )
                )

        FeatureValue.objects.bulk_create(
            feature_values
        )

        # ==========================================
        # Result
        # ==========================================

        self.stdout.write(
            self.style.SUCCESS(
                "\nSuccessfully generated fake data!"
            )
        )

        self.stdout.write(
            f"Products: {len(created_products)}"
        )

        self.stdout.write(
            f"Images: {len(images_to_create)}"
        )

        self.stdout.write(
            f"Variants: {len(variants_to_create)}"
        )

        self.stdout.write(
            f"Features: {len(feature_values)}"
        )

    # ==============================================
    # Product title
    # ==============================================

    def generate_product_title(self, fake):

        prefixes = [
            "پیراهن",
            "شومیز",
            "مانتو",
            "کت",
            "شلوار",
            "دامن",
            "بلوز",
            "تاپ",
            "هودی",
            "ست",
            "لباس",
        ]

        adjectives = [
            "مجلسی",
            "شیک",
            "جدید",
            "خاص",
            "لاکچری",
            "تابستانی",
            "پاییزی",
            "اسپرت",
            "کلاسیک",
            "مدرن",
            "مینیمال",
            "زنانه",
        ]

        materials = [
            "ساتن",
            "لینن",
            "کرپ",
            "نخی",
            "مخمل",
            "ابریشم",
            "بافت",
        ]

        return (
            f"{random.choice(adjectives)} "
            f"{random.choice(materials)} "
            f"{random.choice(prefixes)}"
        )

    # ==============================================
    # Unique slug
    # ==============================================

    def generate_unique_slug(self, title):

        base_slug = slugify(
            title,
            allow_unicode=True
        )

        if not base_slug:

            base_slug = "product"

        slug = base_slug

        counter = 1

        while Product.objects.filter(
            slug=slug
        ).exists():

            slug = (
                f"{base_slug}-{counter}"
            )

            counter += 1

        return slug

    # ==============================================
    # Unique SKU
    # ==============================================

    def generate_unique_sku(self):

        while True:

            sku = (
                f"SKU-"
                f"{random.randint(100000, 999999)}"
            )

            if not ProductVariant.objects.filter(
                sku=sku
            ).exists():

                return sku

    # ==============================================
    # Base data
    # ==============================================

    def create_base_data(self):

        # ------------------------------------------
        # Categories
        # ------------------------------------------

        categories = [
            "لباس زنانه",
            "مانتو",
            "شومیز",
            "پیراهن",
            "شلوار",
            "دامن",
            "تاپ",
            "کت و ژاکت",
            "هودی",
            "اکسسوری",
        ]

        for title in categories:

            ProductCategory.objects.get_or_create(
                title=title,

                defaults={
                    "slug": slugify(
                        title,
                        allow_unicode=True
                    )
                }
            )

        # ------------------------------------------
        # Sizes
        # ------------------------------------------

        sizes = [
            "XS",
            "S",
            "M",
            "L",
            "XL",
            "XXL",
        ]

        for size in sizes:

            ProductSize.objects.get_or_create(
                title=size
            )

        # ------------------------------------------
        # Colors
        # ------------------------------------------

        colors = [
            ("مشکی", "#000000"),
            ("سفید", "#FFFFFF"),
            ("قرمز", "#FF0000"),
            ("آبی", "#0000FF"),
            ("سبز", "#008000"),
            ("زرد", "#FFD700"),
            ("صورتی", "#FFC0CB"),
            ("بنفش", "#800080"),
            ("نارنجی", "#FFA500"),
            ("طوسی", "#808080"),
            ("کرم", "#F5F5DC"),
            ("قهوه‌ای", "#8B4513"),
        ]

        for title, code in colors:

            ProductColor.objects.get_or_create(
                title=title,

                defaults={
                    "code": code
                }
            )

        # ------------------------------------------
        # Features
        # ------------------------------------------

        features = [
            "جنس",
            "مناسب برای",
            "فصل",
            "نوع استایل",
            "کشسانی",
            "نحوه شستشو",
            "کشور تولید کننده",
            "نوع پارچه",
            "طرح",
            "فرم لباس",
        ]

        for title in features:

            Feature.objects.get_or_create(
                title=title
            )

    # ==============================================
    # Feature values
    # ==============================================

    def generate_feature_value(self, feature):

        values = {

            "جنس": [
                "نخ پنبه",
                "کرپ",
                "ساتن",
                "لینن",
                "مخمل",
                "ابریشم",
                "پلی استر",
            ],

            "مناسب برای": [
                "خانم‌ها",
                "بانوان",
                "استفاده روزمره",
                "مهمانی",
            ],

            "فصل": [
                "بهار",
                "تابستان",
                "پاییز",
                "زمستان",
                "چهارفصل",
            ],

            "نوع استایل": [
                "کژوال",
                "رسمی",
                "مینیمال",
                "اسپرت",
                "مجلسی",
                "کلاسیک",
            ],

            "کشسانی": [
                "بدون کشسانی",
                "کشسانی کم",
                "کشسانی متوسط",
                "کشسانی زیاد",
            ],

            "نحوه شستشو": [
                "شستشو با دست",
                "شستشو با ماشین لباسشویی",
                "خشکشویی",
            ],

            "کشور تولید کننده": [
                "ایران",
                "ترکیه",
                "چین",
            ],

            "نوع پارچه": [
                "لطیف",
                "سبک",
                "ضخیم",
                "نرم",
                "خنک",
            ],

            "طرح": [
                "ساده",
                "گل‌دار",
                "راه‌راه",
                "چهارخانه",
                "چاپی",
            ],

            "فرم لباس": [
                "آزاد",
                "راسته",
                "اسلیم",
                "اورسایز",
            ],
        }

        return random.choice(
            values.get(
                feature,
                ["مقدار تصادفی"]
            )
        )
