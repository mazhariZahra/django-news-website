from django.db import models
from django.contrib.auth.models import User

class News(models.Model):
    CATEGORY_CHOICES = [
        ('Technology', 'فناوری'),
        ('Sports', 'ورزشی'),
        ('Health', 'سلامتی'),
        ('Economics', 'اقتصادی'),
        ('Politics', 'سیاسی'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان خبر')
    body = models.TextField(verbose_name='متن خبر')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='دسته‌بندی')
    view_counter = models.IntegerField(default=0, verbose_name='تعداد بازدید')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'خبر'
        verbose_name_plural = 'اخبار'
        ordering = ['-view_counter']
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    favorite_categories = models.JSONField(default=list, verbose_name='دسته‌های مورد علاقه')
    
    def __str__(self):
        return f"پروفایل {self.user.username}"
    
    @classmethod
    def create_profile_for_user(cls, user):
        """ایجاد پروفایل برای کاربر - با بررسی تکراری نبودن"""
        # بررسی اگر پروفایل از قبل وجود دارد
        if not cls.objects.filter(user=user).exists():
            return cls.objects.create(
                user=user,
                favorite_categories=['Technology']
            )
        return cls.objects.get(user=user)

# **هیچ سیگنالی تعریف نکنید**