from django.contrib import admin
from .models import Post, PostCategory, Comment

class ProductAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('title', 'content', 'author','post_type', 'timestamp')  # генерируем список имён всех полей для более красивого отображения
    list_filter = ('post_type', 'category')
    search_fields = ('title', 'content')


admin.site.register(Post, ProductAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment)
# Register your models here.
