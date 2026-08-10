from django.db import models


class Crop(models.Model):
    slug = models.SlugField(primary_key=True)

    nama = models.CharField(max_length=100)
    nama_latin = models.CharField(max_length=150)

    deskripsi = models.TextField()

    jenis_tanaman = models.CharField(max_length=100)

    umur_panen = models.CharField(max_length=100)

    potensi_hasil = models.CharField(max_length=100)

    manfaat = models.TextField()

    cara_budidaya = models.TextField()

    syarat_tumbuh = models.JSONField()

    def __str__(self):
        return self.nama