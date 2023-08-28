from django.utils import timezone

from ...models import DailyChallenge


def get_current_daily_challenge() -> DailyChallenge:
    today = timezone.now().date()
    today_str = today.strftime("%Y-%m-%d")

    try:
        return DailyChallenge.objects.get(id=today_str)
    except DailyChallenge.DoesNotExist:
        # TODO: implement multiple fallback daily challenges (and use a modulo to select one)
        return DailyChallenge.objects.get(id="fallback")
