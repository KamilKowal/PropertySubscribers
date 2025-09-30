

from django.core.management.base import BaseCommand

from core.models import Subscriber, SubscriberSMS, Client, User


class Command(BaseCommand):
    "Skrypt czyszczacy i dodający nowe testowe rekordy do bazy"

    def handle(self, *args, **options):
        self.clean_database()
        self.add_subscribers()

    def clean_database(self):
        SubscriberSMS.objects.all().delete()
        Subscriber.objects.all().delete()
        User.objects.all().delete()
        Client.objects.all().delete()

    def add_subscribers(self):
        # zwykły istniejący user
        User.objects.create(email="existing_user@example.com", phone="+48111111111", gdpr_consent=True)

        # user z telefonem, który wejdzie w konflikt w migrate_subscribers
        User.objects.create(email="conflict_user@example.com", phone="+48555555555", gdpr_consent=True)

        # user z innym telefonem, który pokryje się emailem z Clientem
        User.objects.create(email="client_match_conflict@example.com", phone="+48000000001", gdpr_consent=True)

        # --- Subscribers (email-driven) ---
        Subscriber.objects.create(email="existing_user@example.com", gdpr_consent=True)  # case: user exists
        Subscriber.objects.create(email="client_match_no_conflict@example.com",
                                  gdpr_consent=True)  # dopasowanie client bez konfliktu
        Subscriber.objects.create(email="client_match_conflict@example.com", gdpr_consent=False)  # konflikt phone
        Subscriber.objects.create(email="no_client@example.com",
                                  gdpr_consent=True)  # brak clienta -> user z pustym phone

        # --- Clients ---
        Client.objects.create(email="client_match_no_conflict@example.com", phone="+48666666666")  # no conflict
        Client.objects.create(email="client_match_conflict@example.com", phone="+48555555555")  # konflikt phone

        # --- SubscriberSMS (phone-driven) ---
        # 1. Istniejący user z tym samym phone i client z innym emailem -> konflikt
        SubscriberSMS.objects.create(phone="+48111111111", gdpr_consent=True)

        # 2. Client o tym phone, ale email już zajęty przez innego usera -> konflikt
        Client.objects.create(email="taken_email@example.com", phone="+48777777777")
        User.objects.create(email="taken_email@example.com", phone="+48999999999", gdpr_consent=True)
        SubscriberSMS.objects.create(phone="+48777777777", gdpr_consent=True)

        # 3. Client o tym phone, brak konfliktu -> nowy user
        Client.objects.create(email="fresh_client@example.com", phone="+48888888888")
        SubscriberSMS.objects.create(phone="+48888888888", gdpr_consent=False)

        # 4. Brak clienta -> user z pustym emailem
        SubscriberSMS.objects.create(phone="+48900000000", gdpr_consent=True)