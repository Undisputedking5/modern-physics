from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from teacher.models import Lesson

class LessonViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testteacher', password='password123')
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            form="1",
            topic="Test Topic",
            description="Test Description",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            is_published=True,
            author=self.user
        )

    def test_lesson_list_view(self):
        response = self.client.get(reverse('dashboard:lesson_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Lesson")
        self.assertTemplateUsed(response, 'dashboard/lesson_list.html')

    def test_lesson_detail_view(self):
        response = self.client.get(reverse('dashboard:lesson_detail', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Lesson")
        self.assertContains(response, "https://www.youtube.com/embed/dQw4w9WgXcQ")
        self.assertTemplateUsed(response, 'dashboard/lesson_detail.html')

    def test_lesson_embed_url_conversion(self):
        # Test watch?v= format
        self.assertEqual(self.lesson.get_embed_url, "https://www.youtube.com/embed/dQw4w9WgXcQ")
        
        # Test youtu.be/ format
        self.lesson.video_url = "https://youtu.be/dQw4w9WgXcQ"
        self.lesson.save()
        self.assertEqual(self.lesson.get_embed_url, "https://www.youtube.com/embed/dQw4w9WgXcQ")

    def test_unpublished_lesson_not_visible(self):
        self.lesson.is_published = False
        self.lesson.save()
        
        # Should not be in list
        response = self.client.get(reverse('dashboard:lesson_list'))
        self.assertNotContains(response, "Test Lesson")
        
        # Detail should return 404
        response = self.client.get(reverse('dashboard:lesson_detail', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 404)
