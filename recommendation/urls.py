from django.urls import path
from .views import recommend, detail_tanaman, RiwayatListView, RiwayatDeleteView, RiwayatDetailView

urlpatterns = [
    path('recommend/', recommend),
    path('rekomendasi/<int:rekomendasi_id>/detail/', detail_tanaman),
    path('riwayat/', RiwayatListView.as_view()),
    path('riwayat/<int:pk>/', RiwayatDeleteView.as_view()),
    path('riwayat/<int:pk>/detail/', RiwayatDetailView.as_view()),
]