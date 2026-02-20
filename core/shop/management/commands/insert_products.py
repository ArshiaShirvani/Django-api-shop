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
)


class Command(BaseCommand):
    help = "Generate 20 fake products with variants and images (bulk)"

    def handle(self, *args, **options):
        fake = Faker(locale="fa_IR")

        # ------------------------
        # مسیر پروژه و تصاویر
        # ------------------------
        # مسیر نسبی از فایل command تا manage.py
        PROJECT_ROOT = Path(__file__).resolve().parents[3]  # 4 سطح پایین → shop/management/commands
        images_dir = PROJECT_ROOT / "fake_data" / "images"
        images_list = list(images_dir.glob("*.*"))

        print("Looking for images in:", images_dir)

        if not images_list:
            self.stdout.write(self.style.ERROR(f"No images found in {images_dir}"))
            return

        # ------------------------
        # داده پایه
        # ------------------------
        self.create_base_data(fake)

        categories = list(ProductCategory.objects.all())
        sizes = list(ProductSize.objects.all())
        colors = list(ProductColor.objects.all())

        # ------------------------
        # ساخت محصولات
        # ------------------------
        products_to_create = []

        for _ in range(20):
            title = " ".join(fake.words(nb=random.randint(1, 3)))
            slug = self.generate_unique_slug(title)

            products_to_create.append(
                Product(
                    title=title,
                    slug=slug,
                    description=fake.text(max_nb_chars=200),
                    status=ProductStatus.PUBLISHED,
                )
            )

        created_products = Product.objects.bulk_create(products_to_create)

        # ------------------------
        # دسته‌بندی‌ها (M2M)
        # ------------------------
        for product in created_products:
            selected_categories = random.sample(
                categories, random.randint(1, min(3, len(categories)))
            )
            product.categories.set(selected_categories)

        # ------------------------
        # تصاویر محصولات
        # ------------------------
        images_to_create = []

        for product in created_products:
            selected_images = random.sample(images_list, random.randint(1, 4))

            for index, img_path in enumerate(selected_images):
                with open(img_path, "rb") as f:
                    data = f.read()
                images_to_create.append(
                    ProductImages(
                        product=product,
                        image=ContentFile(data, name=img_path.name),
                        is_main=(index == 0),
                    )
                )

        ProductImages.objects.bulk_create(images_to_create)

        # ------------------------
        # واریانت‌ها
        # ------------------------
        variants_to_create = []

        for product in created_products:
            combinations = [(s, c) for s in sizes for c in colors]
            random.shuffle(combinations)

            for size, color in combinations[: random.randint(1, 4)]:
                variants_to_create.append(
                    ProductVariant(
                        product=product,
                        size=size,
                        color=color,
                        price=random.randint(100_000, 5_000_000),
                        discount_percent=random.choice([0, 5, 10, 15, 20]),
                        stock=random.randint(0, 50),
                        sku=f"SKU-{random.randint(100000,999999)}",
                        is_active=True,
                    )
                )

        ProductVariant.objects.bulk_create(variants_to_create)

        self.stdout.write(
            self.style.SUCCESS("Successfully generated 20 fake products")
        )

    # ------------------------
    # Helper functions
    # ------------------------

    def generate_unique_slug(self, title):
        base_slug = slugify(title, allow_unicode=True)
        slug = base_slug
        counter = 1

        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def create_base_data(self, fake):
        # دسته‌بندی‌ها
        if not ProductCategory.objects.exists():
            for _ in range(8):
                title = fake.word()
                ProductCategory.objects.create(
                    title=title,
                    slug=slugify(title, allow_unicode=True),
                )

        # سایزها
        if not ProductSize.objects.exists():
            for size in ["S", "M", "L", "XL"]:
                ProductSize.objects.create(title=size)

        # رنگ‌ها
        if not ProductColor.objects.exists():
            colors = [
                ("قرمز", "#ff0000"),
                ("آبی", "#0000ff"),
                ("سبز", "#00ff00"),
                ("مشکی", "#000000"),
                ("سفید", "#ffffff"),
            ]
            for title, code in colors:
                ProductColor.objects.create(title=title, code=code)