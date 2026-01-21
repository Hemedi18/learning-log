from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Topic(models.Model):
    """A topic the user is learning about."""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True) 
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the model."""
        return self.text
    
class Entry(models.Model):
    """Something specific learned about a topic."""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name_plural = 'entries'
        
    def __str__(self):
        """Return a string representation of the model."""
        return f"{self.text[:50]}..."

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

    def __str__(self):
        return f"{self.title} ({self.frequency}) - {self.amount}"