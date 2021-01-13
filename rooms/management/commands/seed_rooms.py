import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms import models as room_models
from users import models as user_models


class Command(BaseCommand):

    help = "This command creates many rooms."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            default=2,
            type=int,
            help="How many rooms do you want to create?",
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        room_types = room_models.RoomType.objects.all()
        seeder.add_entity(
            room_models.Room,
            number,
            {
                "name": lambda x: seeder.faker.address(),
                "host": lambda x: random.choice(all_users),
                "room_type": lambda x: random.choice(room_types),
                "guests": lambda x: random.randint(1, 8),
                "price": lambda x: random.randint(50, 300),
                "beds": lambda x: random.randint(1, 5),
                "bedrooms": lambda x: random.randint(1, 5),
                "baths": lambda x: random.randint(1, 5),
            },
        )
        created_room = seeder.execute()
        created_room_list = flatten(list(created_room.values()))
        amenities = room_models.Amenity.objects.all()
        house_rules = room_models.HouseRule.objects.all()
        for pk in created_room_list:
            room = room_models.Room.objects.get(pk=pk)
            for i in range(3, random.randint(10, 30)):
                room_models.Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    room=room,
                    file=f"room_photos/{random.randint(1,31)}.webp",
                )
            for a in amenities:
                random_num = random.randint(0, 15)
                if random_num % 2 == 0:
                    room.amenities.add(a)
            for r in house_rules:
                random_num = random.randint(0, 15)
                if random_num % 2 == 0:
                    room.house_rule.add(r)

        self.stdout.write(self.style.SUCCESS(f"{number} rooms are created!"))
