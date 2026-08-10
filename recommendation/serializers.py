from rest_framework import serializers
from .riwayat_models import RiwayatRekomendasi, RiwayatPencarian

class RecommendRequestSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-11, max_value=6)
    lon = serializers.FloatField(min_value=95, max_value=141)
    luas_lahan = serializers.FloatField(
        min_value=0,
        required=False,
        allow_null=True,
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

    class Meta:
        model = RiwayatPencarian
        fields = '__all__'