from django.core.management.base import BaseCommand
from core.models import AircraftModel, Team, PartType

class Command(BaseCommand):
    help = 'Veritabanına başlangıç verilerini ekler (uçak modelleri, takımlar, parça tipleri).'

    def handle(self, *args, **options):
        # Uçak modelleri
        for name in ["TB2", "TB3", "Akıncı"]:
            model, created = AircraftModel.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"AircraftModel eklendi: {name}"))

        # Takımlar
        team_data = [
            ("Gövde Takımı", "gövde"),
            ("Kanat Takımı", "kanat"),
            ("Aviyonik Takımı", "aviyonik"),
            ("Motor Takımı", "motor"),
            ("Montaj Takımı", "montaj"),
            ("Kuyruk Takımı", "kuyruk"),
        ]
        teams = {}
        for name, resp in team_data:
            team, _ = Team.objects.get_or_create(name=name, responsibility=resp)
            teams[resp] = team
            self.stdout.write(self.style.SUCCESS(f"Team eklendi: {name}"))

        # Parça tipleri
        for part in ["gövde", "kanat", "aviyonik", "motor"]:
            if part in teams:
                pt, created = PartType.objects.get_or_create(name=part, allowed_team=teams[part])
                if created:
                    self.stdout.write(self.style.SUCCESS(f"PartType eklendi: {part}"))
