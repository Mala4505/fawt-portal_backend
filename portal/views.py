from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from collections import defaultdict
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


class BookDetailView(APIView):
    def put(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        book.delete()
        return Response({'message': 'Book deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
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
            response_serializer = PageEntrySerializer(entry)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


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
# class GroupListView(APIView):
#     def get(self, request):
#         entries = PageEntry.objects.select_related('user', 'book').all()
#         book_student_pages = defaultdict(lambda: defaultdict(set))  # book → student → pages

#         for entry in entries:
#             for page in range(entry.from_page, entry.to_page + 1):
#                 book_student_pages[entry.book.name][entry.user.name].add(page)

#         groups = []
#         pending = []

#         for book, student_pages in book_student_pages.items():
#             matched = set()
#             page_groups = defaultdict(list)  # frozen set of pages → list of students

#             for student, pages in student_pages.items():
#                 found = False
#                 for other, other_pages in student_pages.items():
#                     if student == other:
#                         continue
#                     shared = pages & other_pages
#                     if shared:
#                         key = frozenset(shared)
#                         page_groups[key].append(student)
#                         found = True
#                         break
#                 if not found:
#                     pending.append({
#                         "name": student,
#                         "book": book,
#                         "unmatchedPages": sorted(list(pages))
#                     })

#             for shared_pages, members in page_groups.items():
#                 groups.append({
#                     "book": book,
#                     "sharedPages": sorted(list(shared_pages)),
#                     "members": list(set(members))  # deduplicated
#                 })

#         return Response({
#             "groups": groups,
#             "pending": pending
#         })


class GroupListView(APIView):
    def get(self, request):
        entries = PageEntry.objects.select_related('user', 'book').all()
        book_student_pages = defaultdict(lambda: defaultdict(set))  # book → student → pages
        student_tr_map = {}  # student name → tr_number

        for entry in entries:
            name = entry.user.name
            tr = entry.user.tr_number
            student_tr_map[name] = tr
            for page in range(entry.from_page, entry.to_page + 1):
                book_student_pages[entry.book.name][name].add(page)

        groups = []
        pending = []

        for book, student_pages in book_student_pages.items():
            page_to_students = defaultdict(set)  # page → set of students
            for student, pages in student_pages.items():
                for page in pages:
                    page_to_students[page].add(student)

            grouped_pages = defaultdict(set)  # frozenset of students → set of shared pages

            for page, students in page_to_students.items():
                if len(students) > 1:
                    key = frozenset(students)
                    grouped_pages[key].add(page)

            # Build group list
            for members, shared_pages in grouped_pages.items():
                groups.append({
                    "book": book,
                    "sharedPages": sorted(shared_pages),
                    "members": sorted(members)
                })

            # Track matched pages per student
            matched_pages = defaultdict(set)
            for members, shared_pages in grouped_pages.items():
                for student in members:
                    matched_pages[student].update(shared_pages)

            # Compute unmatched pages per student
            for student, all_pages in student_pages.items():
                unmatched = all_pages - matched_pages.get(student, set())
                if unmatched:
                    pending.append({
                        "name": student,
                        "trNumber": student_tr_map.get(student),
                        "book": book,
                        "unmatchedPages": sorted(unmatched)
                    })

        return Response({
            "groups": groups,
            "pending": pending
        })



# ✅ Optional: Admin ViewSets
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class GroupMembershipViewSet(viewsets.ModelViewSet):
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer
