""" USSD Constants """
PENDING = 'pending'
CONFIRMED = 'confirmed'
CANCELLED = 'cancelled'
COMPLETED = 'completed'

STATUS_CHOICES = [
    (PENDING, 'Pending'),
    (CONFIRMED, 'Confirmed'),
    (CANCELLED, 'Cancelled'),
    (COMPLETED, 'Completed'),
]

TIME_SLOTS = [
    ('08:00', '08:00 AM - 10:00 AM'),
    ('11:00', '11:00 AM - 01:00 PM'),
    ('17:00', '05:00 PM - 07:00 PM'),
    ('20:00', '08:00 PM - 10:00 PM'),
]