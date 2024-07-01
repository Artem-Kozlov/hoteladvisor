from django.contrib import admin
from .models import *


admin.site.register(Article)
admin.site.register(Hotel)
admin.site.register(HotelImage)
admin.site.register(Review)
admin.site.register(Booking)

# @admin.register(Hotel)
# class HotelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'location', 'rating', 'price_per_night', 'created_at')

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1