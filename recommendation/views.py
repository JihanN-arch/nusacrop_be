from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import DestroyAPIView, RetrieveAPIView
from rest_framework import generics

from .serializers import RecommendRequestSerializer, RiwayatPencarianSerializer
from .services.recommendation_services import get_recommendation
from .services.detail_crop import get_crop_detail
from .models.riwayat_models import RiwayatPencarian

from .utils.pagination import RiwayatPagination

# Create your views here.
@api_view(["POST"])
def recommend(request):
    serializer = RecommendRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    anonymous_id = request.data.get("anonymous_id")
    if not anonymous_id:
        return Response({"status": "error", "message": "anonymous_id wajib dikirim"}, status=400)
    
    result = get_recommendation(serializer.validated_data, anonymous_id)
        
    if result["status"] != "success":
        return Response(result, status=503)

    return Response(result)

@api_view(['GET'])
def detail_tanaman(request, rekomendasi_id):
    result = get_crop_detail(rekomendasi_id)
    if result is None:
        return Response(
            {"error":"Tanaman tidak ditemukan"},
            status=404
        )

    return Response(result)


# for riwayat
class RiwayatListView(generics.ListAPIView):
    serializer_class = RiwayatPencarianSerializer
    pagination_class = RiwayatPagination

    def get_queryset(self):
        anonymous_id = self.request.query_params.get('anonymous_id')
        if not anonymous_id: # kalo ga ada anonymous id
            return RiwayatPencarian.objects.none()
        return RiwayatPencarian.objects.filter(anonymous_id=anonymous_id)


class RiwayatDeleteView(DestroyAPIView):
    serializer_class = RiwayatPencarianSerializer

    def get_queryset(self):
        anonymous_id = self.request.query_params.get('anonymous_id')
        return RiwayatPencarian.objects.filter(anonymous_id=anonymous_id)

# lihat 1 user     
class RiwayatDetailView(RetrieveAPIView):
    serializer_class = RiwayatPencarianSerializer

    def get_queryset(self):
        anonymous_id = self.request.query_params.get('anonymous_id')
        return RiwayatPencarian.objects.filter(anonymous_id=anonymous_id)