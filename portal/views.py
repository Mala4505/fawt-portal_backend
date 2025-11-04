# from rest_framework import viewsets, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .models import User, Book, PageEntry, Group, GroupMembership
# from rest_framework.generics import RetrieveUpdateDestroyAPIView
# from .serializers import *

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# # class BookViewSet(viewsets.ModelViewSet):
# #     queryset = Book.objects.all()
# #     serializer_class = BookSerializer

# class BookListView(APIView):
#     def get(self, request):
#         books = Book.objects.all()
#         serializer = BookSerializer(books, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = BookSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

# class PageEntryView(APIView):
#     def get(self, request):
#         user_id = request.query_params.get('user')
#         if user_id:
#             entries = PageEntry.objects.filter(user__id=user_id)
#         else:
#             entries = PageEntry.objects.all()
#         serializer = PageEntrySerializer(entries, many=True)
#         print("Incoming data:", request.data)
#         return Response(serializer.data)

#     def post(self, request):
#         print("Incoming data:", request.data)
#         try:
#             user_id = request.data.get('user')
#             book_id = request.data.get('book')
#             from_page = request.data.get('from_page')
#             to_page = request.data.get('to_page')
#             revised = request.data.get('revised', False)

#             user = User.objects.get(id=user_id)
#             book = Book.objects.get(id=book_id)

#             entry = PageEntry.objects.create(
#                 user=user,
#                 book=book,
#                 from_page=from_page,
#                 to_page=to_page,
#                 revised=revised
#             )
#             serializer = PageEntrySerializer(entry)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except (User.DoesNotExist, Book.DoesNotExist):
#             return Response({'error': 'Invalid user or book ID'}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class TRLoginView(APIView):
#     def post(self, request):
#         tr_number = request.data.get('tr_number')
#         try:
#             user = User.objects.get(tr_number=tr_number)
#             return Response({
#                 'id': user.id,
#                 'name': user.name,
#                 'role': user.role
#             }, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             return Response({'error': 'Invalid TR number'}, status=status.HTTP_404_NOT_FOUND)

# class GroupListView(APIView):
#     def get(self, request):
#         groups = Group.objects.all()
#         data = []
#         for group in groups:
#             members = GroupMembership.objects.filter(group=group)
#             data.append({
#                 'id': group.id,
#                 'bookName': group.book.name,
#                 'sharedPages': group.shared_pages.split(','),
#                 'members': [{
#                     'trNumber': m.user.tr_number,
#                     'name': m.user.name
#                 } for m in members]
#             })
#         return Response(data)
    
    
# class EntryDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = PageEntry.objects.all()
#     serializer_class = PageEntrySerializer
    

# class GroupViewSet(viewsets.ModelViewSet):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer

# class GroupMembershipViewSet(viewsets.ModelViewSet):
#     queryset = GroupMembership.objects.all()
#     serializer_class = GroupMembershipSerializer

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .models import User, Book, PageEntry, Group, GroupMembership
from .serializers import *

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin

# ✅ User ViewSet (optional for admin use)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# ✅ Book List + Create
class BookListView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ PageEntry List + Create

class PageEntryView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        if user_id:
            entries = PageEntry.objects.filter(user__id=user_id)
        else:
            entries = PageEntry.objects.all()

        serializer = PageEntrySerializer(entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PageEntrySerializer(data=request.data)
        if serializer.is_valid():
            entry = serializer.save()
            # ✅ Re-serialize the saved entry for full response
            response_serializer = PageEntrySerializer(entry)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PageEntryView(CreateModelMixin, ListModelMixin, GenericAPIView):
#     queryset = PageEntry.objects.all()
#     serializer_class = PageEntrySerializer

#     def get_queryset(self):
#         user_id = self.request.query_params.get('user')
#         if user_id:
#             return PageEntry.objects.filter(user__id=user_id)
#         return PageEntry.objects.all()

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


class EntryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = PageEntry.objects.all()
    serializer_class = PageEntrySerializer
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        print(f"🔍 Looking for PageEntry with ID: {pk}")
        return super().get_object()


    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f"✅ Deleting entry ID {instance.id}")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ✅ TR Number Login
class TRLoginView(APIView):
    def post(self, request):
        tr_number = request.data.get('tr_number')
        try:
            user = User.objects.get(tr_number=tr_number)
            return Response({
                'id': user.id,
                'name': user.name,
                'role': user.role
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Invalid TR number'}, status=status.HTTP_404_NOT_FOUND)

# ✅ Group List View
class GroupListView(APIView):
    def get(self, request):
        groups = Group.objects.all()
        data = []
        for group in groups:
            members = GroupMembership.objects.filter(group=group)
            data.append({
                'id': group.id,
                'bookName': group.book.name,
                'sharedPages': group.shared_pages.split(','),
                'members': [{
                    'trNumber': m.user.tr_number,
                    'name': m.user.name
                } for m in members]
            })
        return Response(data)

# ✅ Optional: Admin ViewSets
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class GroupMembershipViewSet(viewsets.ModelViewSet):
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer
