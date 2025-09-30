1️⃣ clean_and_init_all

python manage.py clean_and_init_all

Czyści bazę danych z istniejących rekordów.
Inicjalizuje wymagane obiekty w bazie, np. przykładowych User, Subscriber, SubscriberSMS i Client.

2️⃣ show_all_data

python manage.py show_all_data

Wyświetla aktualne dane w bazie.
Lista wszystkich User, Subscriber, SubscriberSMS oraz Client.


3️⃣ migrate_subscribers

python manage.py migrate_subscribers

Migruje dane z modeli Subscriber i SubscriberSMS do User.
