from django.db import models
from .crop_models import Crop

class RiwayatPencarian(models.Model):

    anonymous_id = models.CharField(max_length=100,db_index=True)

    nama_lokasi = models.CharField(max_length=100, null=True, blank=True)
    
    lat = models.FloatField()
    lon = models.FloatField()

    luas_lahan = models.FloatField(null=True,blank=True)

    musim_target = models.CharField(max_length=50,null=True,blank=True)

    curah_hujan = models.FloatField(null=True,blank=True)

    ph_tanah = models.FloatField(null=True, blank=True)

    elevasi = models.FloatField(null = True,blank=True)
    
    ndvi = models.FloatField(null=True, blank=True)
    
    suhu = models.FloatField(null=True,blank=True)
    et0 = models.FloatField(null=True,blank=True)


    nitrogen = models.FloatField(null=True,blank=True)
    organic_carbon = models.FloatField(null=True,blank=True)
    tekstur_tanah = models.JSONField(default=dict)
    kesuburan_tanah = models.FloatField(null=True,blank=True)

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-dibuat_pada"]
        
    def __str__(self):
        return f"Riwayat {self.id} ({self.lat},{self.lon})"

class RiwayatRekomendasi(models.Model):

    riwayat = models.ForeignKey(
        RiwayatPencarian,
        related_name="rekomendasi",
        on_delete=models.CASCADE
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.PROTECT
    )

    skor_kesesuaian = models.FloatField()

    ranking = models.PositiveSmallIntegerField()

    tingkat_kepercayaan = models.CharField(
        max_length=50,
        default="Sedang"
    )

    alasan_rekomendasi = models.JSONField(
        default=list
    )


    class Meta:
        ordering = ["ranking"]

        constraints = [
            models.UniqueConstraint(
                fields=["riwayat", "crop"],
                name="unique_crop_history"
            )
        ]