from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from apps.users.models.withdrawal import Withdrawal  # 실제 경로에 맞춰 import

class AdminAnalysisReasonService:
    @staticmethod
    def get_monthly_withdrawal_stats(reason: str):
        # 1. 날짜 범위 설정 (올해 1월 1일부터 현재까지)
        now = timezone.now()
        from_date = now.replace(month=1, day=1).strftime('%Y-%m-%d')
        to_date = now.strftime('%Y-%m-%d')

        # 2. 특정 사유에 대한 월별 통계 쿼리 (TimeStampModel의 created_at 활용)
        stats_query = (
            Withdrawal.objects.filter(reason=reason)
            .annotate(period=TruncMonth('created_at'))
            .values('period')
            .annotate(count=Count('id'))
            .order_by('period')
        )

        # 3. 데이터 포맷팅
        items = [
            {
                "period": item['period'].strftime('%Y-%m'),
                "count": item['count']
            }
            for item in stats_query
        ]

        total = sum(item['count'] for item in items)

        # 모델의 Reason 클래스에서 label 가져오기
        reason_label = dict(Withdrawal.Reason.choices).get(reason, "기타")

        return {
            "reason": reason,
            "reason_label": reason_label,
            "from_date": from_date,
            "to_date": to_date,
            "total": total,
            "items": items
        }