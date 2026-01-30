from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
import os
from django.conf import settings
from .models import News, UserProfile

# ==================== صفحات اصلی ====================

def index_view(request):
    """صفحه اصلی"""
    return render(request, 'index.html')

def login_view(request):
    """صفحه ورود"""
    if request.user.is_authenticated:
        return redirect('config')
    return render(request, 'login.html')

def register_view(request):
    """صفحه ثبت‌نام"""
    if request.user.is_authenticated:
        return redirect('config')
    return render(request, 'login.html')

@login_required
def config_view(request):
    """صفحه پیکربندی"""
    return render(request, 'config.html')

@login_required
def news_view(request):
    """صفحه نمایش اخبار"""
    return render(request, 'news.html')

@login_required
def edit_news_view(request):
    """صفحه ویرایش اخبار"""
    return render(request, 'edit_news.html')

@login_required
def logout_view(request):
    """خروج از سیستم"""
    logout(request)
    return redirect('index')

# ==================== API ها ====================

@csrf_exempt
def api_login(request):
    """API برای ورود کاربر"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True, 
                    'username': user.username,
                    'message': 'ورود موفقیت‌آمیز بود'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'نام کاربری یا کلمه عبور اشتباه است'
                })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'متد غیرمجاز'})

@csrf_exempt
def api_register(request):
    """API برای ثبت‌نام کاربر"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            confirm_password = data.get('confirm')
            
            # اعتبارسنجی
            if not username or not password:
                return JsonResponse({
                    'success': False, 
                    'error': 'لطفاً تمام فیلدها را پر کنید'
                })
            
            if password != confirm_password:
                return JsonResponse({
                    'success': False, 
                    'error': 'کلمه‌های عبور یکسان نیستند'
                })
            
            # بررسی وجود کاربر
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'نام کاربری قبلاً استفاده شده است'
                })
            
            # ایجاد کاربر جدید
            user = User.objects.create_user(username=username, password=password)
            
            # ایجاد پروفایل
            UserProfile.objects.create(
                user=user,
                favorite_categories=['Technology']
            )
            
            # لاگین کردن کاربر
            login(request, user)
            
            return JsonResponse({
                'success': True, 
                'username': user.username,
                'message': 'ثبت‌نام موفقیت‌آمیز بود'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'خطا در ثبت‌نام: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'متد غیرمجاز'})

@login_required
@csrf_exempt
@require_POST
def api_save_config(request):
    """API برای ذخیره تنظیمات"""
    try:
        data = json.loads(request.body)
        categories = data.get('categories', [])
        
        # دریافت یا ایجاد پروفایل
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.favorite_categories = categories
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(
                user=request.user,
                favorite_categories=categories
            )
        
        return JsonResponse({
            'success': True, 
            'message': 'تنظیمات ذخیره شد'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_GET
def api_get_news(request):
    """API برای دریافت اخبار"""
    try:
        # بررسی اگر پارامتر all=true ارسال شده
        show_all = request.GET.get('all', 'false').lower() == 'true'
        
        if show_all:
            # نمایش همه اخبار بدون فیلتر
            news_items = News.objects.all()
        else:
            # دریافت دسته‌های مورد علاقه کاربر
            try:
                profile = UserProfile.objects.get(user=request.user)
                categories = profile.favorite_categories
            except UserProfile.DoesNotExist:
                categories = ['Technology']  # مقدار پیش‌فرض
            
            # اگر کاربر هیچ دسته‌ای انتخاب نکرده، همه دسته‌ها رو نشون بده
            if not categories or len(categories) == 0:
                categories = [choice[0] for choice in News.CATEGORY_CHOICES]
            
            # دریافت پارامترهای فیلتر از URL
            category_filter = request.GET.getlist('category', [])
            
            # فیلتر کردن اخبار
            news_items = News.objects.all()
            
            if category_filter:
                news_items = news_items.filter(category__in=category_filter)
            else:
                news_items = news_items.filter(category__in=categories)
        
        # مرتب‌سازی
        news_items = news_items.order_by('-view_counter', '-created_at')
        
        # تبدیل به لیست
        news_list = []
        for item in news_items:
            news_list.append({
                'NewsID': item.id,
                'NewsTitle': item.title,
                'NewsBody': item.body,
                'NewsClass': item.category,
                'ViewCounter': item.view_counter,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({'news': news_list})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_GET
def api_get_categories(request):
    """API برای دریافت دسته‌بندی‌ها"""
    categories = [choice[0] for choice in News.CATEGORY_CHOICES]
    return JsonResponse({'categories': categories})

@login_required
@csrf_exempt
@require_POST
def api_add_news(request):
    """API برای افزودن خبر جدید"""
    try:
        data = json.loads(request.body)
        
        news = News.objects.create(
            title=data.get('title', ''),
            body=data.get('body', ''),
            category=data.get('category', 'Technology'),
            view_counter=data.get('viewcounter', 0)
        )
        
        return JsonResponse({
            'success': True, 
            'news_id': news.id,
            'message': 'خبر با موفقیت اضافه شد'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@csrf_exempt
@require_POST
def api_edit_news(request):
    """API برای ویرایش خبر"""
    try:
        data = json.loads(request.body)
        news_id = data.get('id')
        
        news = get_object_or_404(News, id=news_id)
        
        news.title = data.get('title', news.title)
        news.body = data.get('body', news.body)
        news.category = data.get('category', news.category)
        
        if 'viewcounter' in data:
            news.view_counter = data['viewcounter']
        
        news.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'خبر با موفقیت ویرایش شد'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@csrf_exempt
@require_POST
def api_delete_news(request):
    """API برای حذف خبر"""
    try:
        data = json.loads(request.body)
        news_id = data.get('id')
        
        news = get_object_or_404(News, id=news_id)
        news.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'خبر با موفقیت حذف شد'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@csrf_exempt
@require_POST
def api_increment_view(request):
    """API برای افزایش تعداد بازدید"""
    try:
        data = json.loads(request.body)
        news_id = data.get('id')
        
        news = get_object_or_404(News, id=news_id)
        news.view_counter += 1
        news.save()
        
        return JsonResponse({
            'success': True, 
            'new_count': news.view_counter
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_GET
def api_check_auth(request):
    """API برای بررسی وضعیت احراز هویت"""
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            categories = profile.favorite_categories
        except UserProfile.DoesNotExist:
            # ایجاد پروفایل اگر وجود ندارد
            profile = UserProfile.objects.create(
                user=request.user,
                favorite_categories=['Technology']
            )
            categories = ['Technology']
            
        return JsonResponse({
            'authenticated': True, 
            'username': request.user.username,
            'categories': categories
        })
    return JsonResponse({'authenticated': False})

@login_required
@require_GET
def api_get_all_news(request):
    """API برای دریافت همه اخبار (بدون فیلتر)"""
    try:
        # دریافت همه اخبار بدون فیلتر
        news_items = News.objects.all().order_by('-view_counter', '-created_at')
        
        # تبدیل به لیست
        news_list = []
        for item in news_items:
            news_list.append({
                'NewsID': item.id,
                'NewsTitle': item.title,
                'NewsBody': item.body,
                'NewsClass': item.category,
                'ViewCounter': item.view_counter,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({'news': news_list})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})