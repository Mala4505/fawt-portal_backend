from django.contrib import admin
from .models import User, Book, PageEntry, Group, GroupMembership

admin.site.register(User)
admin.site.register(Book)
admin.site.register(PageEntry)
admin.site.register(Group)
admin.site.register(GroupMembership)
