from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Topic(models.Model):
    """A topic the user is learning about."""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True) 
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the model."""
        return self.text

class Tag(models.Model):
    """Global Thought Taxonomy."""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Entry(models.Model):
    """A specific diary entry (DiaryEntry)."""
    MOOD_CHOICES = [
        ('Happy', 'Happy'),
        ('Sad', 'Sad'),
        ('Neutral', 'Neutral'),
        ('Excited', 'Excited'),
        ('Anxious', 'Anxious'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=False, blank=True, max_length=250, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False, null=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    event_date = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES, blank=True)
    
    # Geolocation
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Taxonomy
    tags = models.ManyToManyField(Tag, blank=True)
 
    class Meta:
        verbose_name_plural = 'entries'
        ordering = ['-date_created']

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.uuid}")
        super().save(*args, **kwargs)
        
    def __str__(self):
        """Return a string representation of the model."""
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('learning_logs:entry_detail', kwargs={'pk': self.pk})

class MoodHealthMatrix(models.Model):
    """Tracks physiological and psychological metrics."""
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE, related_name='health_matrix')
    heart_rate_avg = models.IntegerField(null=True, blank=True)
    sleep_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    water_intake_liters = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    mood_intensity = models.IntegerField(default=5) # 1-10 scale

class MediaVault(models.Model):
    """Secure storage for entry attachments."""
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='diary_vault/%Y/%m/')
    file_type = models.CharField(max_length=20, choices=[('image', 'Image'), ('audio', 'Audio'), ('pdf', 'PDF')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AccessLog(models.Model):
    """Security audit trail."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

@receiver(post_save, sender=Entry)
def check_milestones(sender, instance, created, **kwargs):
    """Trigger notification on milestone entries."""
    if created:
        count = Entry.objects.filter(owner=instance.owner).count()
        if count % 100 == 0:
            # In a real app, trigger email task here
            print(f"Milestone reached: {count} entries for {instance.owner.username}")

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Chakula', 'Chakula'),
        ('Usafiri', 'Usafiri'),
        ('Mawasiliano', 'Mawasiliano'),
        ('Burudani', 'Burudani'),
        ('Dharura', 'Dharura'),
        ('Mengineyo', 'Mengineyo'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Mengineyo')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Income(models.Model):
    """Mapato yanayoingia (Mshahara, Biashara, n.k)."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.amount}"

class FinancialGoal(models.Model):
    """Malengo ya fedha na mipangilio ya bajeti ya mtumiaji."""
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    daily_income_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_goal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    daily_spending_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Malengo ya {self.owner.username}"

class RecurringExpense(models.Model):
    FREQUENCY_CHOICES = [
        ('Daily', 'Kila Siku'),
        ('Weekly', 'Kila Wiki'),
        ('Monthly', 'Kila Mwezi'),
        ('Yearly', 'Kila Mwaka'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=Expense.CATEGORY_CHOICES, default='Mengineyo')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='Monthly')
    next_due_date = models.DateField()
    reminder_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.frequency}) - {self.amount}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'