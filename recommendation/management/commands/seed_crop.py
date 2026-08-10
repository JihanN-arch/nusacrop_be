from django.core.management.base import BaseCommand
from ...crop_models import Crop
from recommendation.data import TANAMAN_DATA

class Command(BaseCommand):
    def handle(self, *args, **options):
        for slug, crop in TANAMAN_DATA.items():
            Crop.objects.update_or_create(
                slug = slug,
                defaults={
                    "nama": crop["nama"],
                    "nama_latin": crop["nama_latin"],
                    "deskripsi": crop["deskripsi"],
                    "jenis_tanaman": crop["jenis_tanaman"],
                    "umur_panen": crop["umur_panen"],
                    "potensi_hasil": crop["potensi_hasil"],
                    "cara_budidaya": crop["cara_budidaya"],
                    "manfaat": crop["manfaat"],
                    "syarat_tumbuh": crop["syarat_tumbuh"]
                }
            )
            
        self.stdout.write("Seed selesai.")