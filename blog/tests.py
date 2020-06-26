from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from .models import Post
from .serializers import PostSerializer


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_posts(title="", author=""):
        if title != "" and author != "":
            Post.objects.create(title=title, author=author)

    def setUp(self):
        # add test data
        self.create_posts("like glue", "sean paul")
        self.create_posts("simple song", "konshens")
        self.create_posts("love is wicked", "brick and lace")
        self.create_posts("jam rock", "damien marley")


class GetAllPostsTest(BaseViewTest):
    def test_get_all_posts(self):
        """
        This test ensures that all posts added in the setUp method
        exist when we make a GET request to the posts/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(reverse("posts-all"))
        # fetch the data from db
        expected = Post.objects.all()
        serialized = PostSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
