from rest_framework import serializers
from .models.riwayat_models import RiwayatRekomendasi, RiwayatPencarian

class RecommendRequestSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-11, max_value=6)
    lon = serializers.FloatField(min_value=95, max_value=141)
    
    nama_lokasi = serializers.CharField(
        max_length=100,
        min_length=1,
        required=True,
        allow_blank=False,
        
    )
    
    musim_target = serializers.ChoiceField(
        choices=["hujan", "kemarau"],
        required=False,
        allow_null=True,
    )
    
class RiwayatRekomendasiSerializer(serializers.ModelSerializer):
    nama_tanaman = serializers.CharField(source='crop.nama')
    nama_latin = serializers.CharField(source='crop.nama_latin')

    kesuburan_ideal = serializers.SerializerMethodField()
    ph_ideal = serializers.SerializerMethodField()
    elevasi_ideal = serializers.SerializerMethodField()

    class Meta:
        model = RiwayatRekomendasi
        fields = [
            'id', 'nama_tanaman', 'nama_latin',
            'kesuburan_ideal', 'ph_ideal', 'elevasi_ideal',
            'skor_kesesuaian', 'ranking',
        ]

    def get_kesuburan_ideal(self, obj):
        return obj.crop.syarat_tumbuh.get('kesuburan')

    def get_ph_ideal(self, obj):
        ph = obj.crop.syarat_tumbuh.get('ph', {})
        return f"{ph.get('min')} - {ph.get('max')}"

    def get_elevasi_ideal(self, obj):
        elevasi = obj.crop.syarat_tumbuh.get('elevasi', {})
        return f"{elevasi.get('min')} - {elevasi.get('max')} mdpl"

class RiwayatPencarianSerializer(serializers.ModelSerializer):
    rekomendasi = RiwayatRekomendasiSerializer(many=True, read_only=True)
    nama_tampilan = serializers.SerializerMethodField()

    class Meta:
        model = RiwayatPencarian
        fields = '__all__'
        
    def get_nama_tampilan(self, obj):
        if obj.nama_lokasi:
            return obj.nama_lokasi
        return f"Lokasi {obj.lat:.4f}, {obj.lon:.4f}"