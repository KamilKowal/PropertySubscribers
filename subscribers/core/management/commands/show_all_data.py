from django.core.management.base import BaseCommand
from core.models import Subscriber, SubscriberSMS, Client, User


class Command(BaseCommand):
    help = "Wyświetla wszystkie rekordy z modeli Subscriber, SubscriberSMS, Client i User"

    def handle(self, *args, **options):
        self.stdout.write("=== Subscribers ===")
        for sub in Subscriber.objects.all():
            self.stdout.write(f"id={sub.id}, email={sub.email}, gdpr_consent={sub.gdpr_consent}")

        self.stdout.write("\n=== SubscriberSMS ===")
        for sub_sms in SubscriberSMS.objects.all():
            self.stdout.write(f"id={sub_sms.id}, phone={sub_sms.phone}, gdpr_consent={sub_sms.gdpr_consent}")

        self.stdout.write("\n=== Clients ===")
        for client in Client.objects.all():
            self.stdout.write(f"id={client.id}, email={client.email}, phone={client.phone}")

        self.stdout.write("\n=== Users ===")
        for user in User.objects.all():
            self.stdout.write(f"id={user.id}, email={user.email}, phone={user.phone}, gdpr_consent={user.gdpr_consent}")