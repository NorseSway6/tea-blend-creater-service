from django.db import models

class UserRequest(models.Model): 
    theme = models.CharField(max_length=255)
    taste_type = models.CharField(max_length=255)
    tea_type = models.CharField(max_length=255)
    no_additives = models.BooleanField(default=False)
    price_range = models.IntegerField()

    class Meta:
        db_table = "users_requests"

class Taste(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tastes"

class BaseTea(models.Model):
    name = models.CharField(max_length=255) 
    tea_type = models.CharField(max_length=255)
    making_time = models.IntegerField()
    temperature = models.IntegerField()
    tastes = models.ManyToManyField(Taste, through='BaseTeaTaste')
    price = models.IntegerField()

    def get_tastes(self):
        return ", ".join([taste.name for taste in self.tastes.all()])
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "base_teas"

class BaseTeaTaste(models.Model):
    tea = models.ForeignKey(BaseTea, on_delete=models.CASCADE)
    taste = models.ForeignKey(Taste, on_delete=models.CASCADE)

    class Meta:
        db_table = "base_teas_tastes"
        constraints = [
            models.UniqueConstraint(fields=['tea', 'taste'], name='tea_taste_fk')
        ]

class Additive(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name 

    class Meta:
        db_table = "additives"

class BaseTaste(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "base_tastes"
    

class Subtaste(models.Model):
    name = models.CharField(max_length=255)
    base_taste = models.ForeignKey(BaseTaste, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "subtastes"
        constraints = [
            models.UniqueConstraint(fields=['name', 'base_taste'], name='subtastes_basetaste_fk')
        ]

class SubtasteAdditive(models.Model):
    subtaste = models.ForeignKey(Subtaste, on_delete=models.CASCADE)
    additive = models.ForeignKey(Additive, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "subtastes_tastes"
        constraints = [
            models.UniqueConstraint(fields=['subtaste', 'additive'], name='subtastes_additive_fk')
        ]

class TasteSubtaste(models.Model):
    taste = models.ForeignKey(Taste, on_delete=models.CASCADE)
    subtaste = models.ForeignKey(Subtaste, on_delete=models.CASCADE)

    class Meta:
        db_table = "tea_taste_mappings"
        constraints = [
            models.UniqueConstraint(fields=['taste', 'subtaste'], name='taste_subtaste_fk')
        ]

class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    additives = models.ManyToManyField('Additive', related_name='themes')
    subtastes = models.ManyToManyField('Subtaste', related_name='themes',)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "themes"

class Blend(models.Model):
    name = models.CharField(max_length=255)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    teas = models.ManyToManyField(BaseTea, related_name='blends')
    additives = models.ManyToManyField(Additive, blank=True, related_name='blends')
    subtaste = models.ForeignKey(Subtaste, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_saved = models.BooleanField(default=False)

    def get_price_estimate(self):
        teas_price = sum(tea.price for tea in self.teas.all()) / max(len(self.teas.all()), 1)
        additives_price = sum(50 for _ in self.additives.all())
        return round(teas_price + additives_price, 2)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "blends"


