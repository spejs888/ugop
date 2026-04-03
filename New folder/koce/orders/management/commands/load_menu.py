from django.core.management.base import BaseCommand
from orders.models import Category, Product

class Command(BaseCommand):
    help = 'Load sample menu items into the database'

    def handle(self, *args, **options):
        menu = {
            'Пијалаци': [
                ('Еспресо', '80'),
                ('Макијато', '100'),
                ('Газирана вода (0.25л)', '90'),
                ('Природен сок (портокал)', '150'),
                ('Coca-Cola', '110'),
                ('Скопско пиво (0.33л)', '130'),
                ('Вино чаша (бело/црвено)', '180'),
                ('Ракија (лозова)', '120'),
                ('Лимунада со нане', '140'),
                ('Чај (планински)', '70'),
            ],
            'Салати': [
                ('Шопска салата', '180'),
                ('Цезар салата', '320'),
                ('Грчка салата', '240'),
                ('Македонска салата', '160'),
                ('Витаминска салата', '210'),
            ],
            'Главни Јадења': [
                ('Пилешки стек на скара', '350'),
                ('Плескавица со гарнир', '280'),
                ('Пастрмка на жар', '450'),
                ('Телешки мускул во сос', '550'),
                ('Рижото со зеленчук', '310'),
            ],
            'Пици': [
                ('Маргарита (кечап, кашкавал)', '320'),
                ('Капричиоза (шунка, печурки)', '380'),
                ('Кватро Формаџи (4 вида сирење)', '420'),
                ('Пеперони (кулен, лута пиперка)', '410'),
                ('Вегетаријана (свеж зеленчук)', '360'),
            ],
        }

        for cat_name, items in menu.items():
            cat, _ = Category.objects.get_or_create(name=cat_name)
            for name, price in items:
                Product.objects.get_or_create(name=name, category=cat, price=price)
        self.stdout.write(self.style.SUCCESS('Menu loaded'))
