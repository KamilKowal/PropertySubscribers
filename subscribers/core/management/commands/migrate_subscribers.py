import csv
from django.core.management.base import BaseCommand

from core.models import Subscriber, SubscriberSMS, Client, User

CONFLICTS_FILE = 'subscriber_conflicts.csv'
SMS_CONFLICTS_FILE = 'subscriber_conflicts_SMS.csv'


class Command(BaseCommand):
    help = "Migracja rekordów Subscriber i SubscriberSMS do User"

    def handle(self, *args, **options):
        self.migrate_subscribers()
        self.migrate_subscribers_sms()

    def migrate_subscribers(self):
        with open(CONFLICTS_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["subscriber_id", "email"])

            for sub in Subscriber.objects.all():
                self._process_subscriber(sub, writer)

        self.stdout.write(
            self.style.SUCCESS(f"Migracja Subscriber zakończona. Konflikty zapisane w {CONFLICTS_FILE}")
        )

    def _process_subscriber(self, sub, writer):
        email = sub.email

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            self._handle_existing_user(sub, existing_user, writer)
            return

        client = Client.objects.filter(email=email).first()
        if client and User.objects.filter(phone=client.phone).exists():
            writer.writerow([sub.id, email])
            print(f"Subscriber {sub.id} ({email}) ➡ konflikt (telefon zajęty) – zapisany do CSV")
            return

        if client:
            User.objects.create(
                email=email,
                phone=client.phone,
                gdpr_consent=sub.gdpr_consent,
            )
            print(f"Subscriber {sub.id} ({email}) ➡ utworzono Usera na podstawie Clienta")
            return

        User.objects.create(
            email=email,
            phone="",
            gdpr_consent=sub.gdpr_consent,
        )
        print(f"Subscriber {sub.id} ({email}) ➡ utworzono Usera bez Clienta (telefon pusty)")

    def _handle_existing_user(self, sub, existing_user, writer):
        email = sub.email
        client = Client.objects.filter(email=email).first()
        if client and client.phone != existing_user.phone:
            writer.writerow([sub.id, email])
            print(f"Subscriber {sub.id} ({email}) ➡ konflikt (User ma inny telefon) – zapisany do CSV")
        else:
            print(f"Subscriber {sub.id} ({email}) ➡ pominięty (User już istnieje)")

    def migrate_subscribers_sms(self):
        """
        Migracja SubscriberSMS -> User
        Zasady:
        - jeśli istnieje User z tym phone:
            - jeśli istnieje Client z tym samym phone i email inny niż User → CSV
            - w przeciwnym razie pomiń
        - jeśli istnieje Client z tym phone:
            - jeśli email zajęty przez innego Usera → CSV
            - w przeciwnym razie twórz User
        - jeśli brak Clienta -> twórz User z pustym emailem
        """
        SMS_CONFLICTS_FILE = "subscriber_conflicts_SMS.csv"

        with open(SMS_CONFLICTS_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["subscriber_sms_id", "phone"])

            for sub in SubscriberSMS.objects.all():
                phone = sub.phone
                existing_user = User.objects.filter(phone=phone).first()
                client = Client.objects.filter(phone=phone).first()

                if existing_user and client and client.email != existing_user.email:
                    writer.writerow([sub.id, phone])
                    print(f"SubscriberSMS {sub.id} ({phone}) ➡ konflikt (User ma inny email) – zapisany do CSV")
                    continue

                if client and not User.objects.filter(email=client.email).exists():
                    User.objects.create(
                        email=client.email,
                        phone=phone,
                        gdpr_consent=sub.gdpr_consent,
                    )
                    print(f"SubscriberSMS {sub.id} ({phone}) ➡ utworzono Usera na podstawie Clienta")
                    continue

                if client:
                    writer.writerow([sub.id, phone])
                    print(f"SubscriberSMS {sub.id} ({phone}) ➡ konflikt (email zajęty) – zapisany do CSV")
                    continue

                User.objects.create(
                    email="",
                    phone=phone,
                    gdpr_consent=sub.gdpr_consent,
                )
                print(f"SubscriberSMS {sub.id} ({phone}) ➡ utworzono Usera bez Clienta (email pusty)")

        self.stdout.write(
            self.style.SUCCESS(
                f"Migracja SubscriberSMS zakończona. Konflikty zapisane w {SMS_CONFLICTS_FILE}"
            )
        )