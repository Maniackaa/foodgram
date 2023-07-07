import csv

from django.core.management.base import BaseCommand, CommandError
from app.models import Ingredient
from foodgram.settings import BASE_DIR

PATH_FILE = BASE_DIR / 'data' / 'ingredients.csv'


def csv_serializer(csv_data):
    objects = []
    for row in csv_data:
        print(row)
        obj = Ingredient(**row)
        print(obj)
        objects.append(obj)
        print(f'Запись добавлена: \n{row}')

    Ingredient.objects.bulk_create(objects)


class Command(BaseCommand):
    help = 'Imports data from a CSV file to the database'

    def handle(self, *args, **kwargs):
        try:
            with open(f"{PATH_FILE}",
                      newline='',
                      encoding="utf-8-sig") as csv_file:
                csv_data = csv.DictReader(
                    csv_file,
                    fieldnames=['name', 'measurement_unit'])
                print(csv_data)
                csv_serializer(csv_data)
        except Exception as error:
            raise CommandError(error)
        self.stdout.write(self.style.SUCCESS('Successfully imported data.'))
