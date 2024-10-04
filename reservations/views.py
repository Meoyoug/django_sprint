from rest_framework.generics import CreateAPIView
from reservations.models import Reservation
from reservations import serializers

# 1. 예약하기(가게, 인원, 예약자)
# 2. 입장(식당 오너가 처리)
# orderby('reserved_at') -> 가장 오래된 예약이 맨위
# objects.count 전체 길이를 구함
# count 번째를 제일 마지막 예약에 부여.
# 나머지는 -1 씩하면서 가장 오래된 예약이 1번이 되도록 부여
# serializer의 to_representation 메서드를 통해서 처리
# 3. 취소(예약의 상태를 Canceled 로 변경)


class ReservationCreateView(CreateAPIView):
    serializer_class = serializers.ReservationSerializer
    queryset = Reservation.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

