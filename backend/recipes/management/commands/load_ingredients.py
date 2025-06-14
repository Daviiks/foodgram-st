﻿import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Путь к файлу")

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, options["path"])
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                name_csv = 0
                measurement_unit_csv = 1
                try:
                    obj, created = Ingredient.objects.get_or_create(
                        name=row[name_csv],
                        measurement_unit=row[measurement_unit_csv],
                    )
                    if not created:
                        print(f"Ингредиент {obj} уже есть в базе данных.")
                except Exception as err:
                    print(f"Ошибка в строке {row}: {err}")

        print("Данные загружены!")
