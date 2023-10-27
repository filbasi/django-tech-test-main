import json

from django.test import TestCase
from django.urls import reverse

from techtest.articles.models import Article, Author
from techtest.regions.models import Region


class ArticleListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("articles-list")
        self.article_1 = Article.objects.create(title="Fake Article 1")
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article_2 = Article.objects.create(
            title="Fake Article 2", content="Lorem Ipsum"
        )
        self.article_2.regions.set([self.region_1, self.region_2])
        self.author = Author.objects.create(first_name="Test First Name", last_name="Test Last Name")
        self.article_3 = Article.objects.create(
            title="Fake Article 3", content="Fake Content", author=self.author)

    def test_serializes_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "id": self.article_1.id,
                    "title": "Fake Article 1",
                    "content": "",
                    "regions": [],
                    "author": None,
                },
                {
                    "id": self.article_2.id,
                    "title": "Fake Article 2",
                    "content": "Lorem Ipsum",
                    "regions": [
                        {
                            "id": self.region_1.id,
                            "code": "AL",
                            "name": "Albania",
                        },
                        {
                            "id": self.region_2.id,
                            "code": "UK",
                            "name": "United Kingdom",
                        },
                    ],
                    "author": None,
                },
                {
                    "id": self.article_3.id,
                    "title": "Fake Article 3",
                    "content": "Fake Content",
                    "regions": [],
                    "author": 
                        {   "id": self.author.id,
                            "first_name": "Test First Name",
                            "last_name": "Test Last Name",
                        }
                },
            ],
        )

    def test_creates_new_article_with_regions_and_author(self):
        payload = {
            "title": "Fake Article 3",
            "content": "To be or not to be",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"code": "AU", "name": "Austria"},
            ],
            "author": 
                {   
                    "first_name": "Test First Name1",
                    "last_name": "Test Last Name1",
                }
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        author = Author.objects.filter(authors__id=article.id)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 3",
                "content": "To be or not to be",
                "regions": [
                    {
                        "id": regions.all()[0].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                    {"id": regions.all()[1].id, "code": "AU", "name": "Austria"},
                ],
                "author": 
                    {   
                        "id": author.all()[0].id,
                        "first_name": "Test First Name1",
                        "last_name": "Test Last Name1",
                    },
            },
            response.json(),
        )


class ArticleViewTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="Test First Name", last_name="Test Last Name")
        self.article = Article.objects.create(title="Fake Article 1", author=self.author)
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article.regions.set([self.region_1, self.region_2])
        self.url = reverse("article", kwargs={"article_id": self.article.id})

    def test_serializes_single_record_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.article.id,
                "title": "Fake Article 1",
                "content": "",
                "regions": [
                    {
                        "id": self.region_1.id,
                        "code": "AL",
                        "name": "Albania",
                    },
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                ],
                "author": 
                    {   
                        "id": self.author.id,
                        "first_name": "Test First Name",
                        "last_name": "Test Last Name",
                    },
            },
        )

    def test_updates_article_and_regions_and_author(self):
        # Change regions and author
        payload = {
            "title": "Fake Article 1 (Modified)",
            "content": "To be or not to be here",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"id": self.region_2.id},
            ],
            "author": 
                {   
                    "id": self.author.id,
                    "first_name": "Updated Test First Name",
                    "last_name": "Updated Test Last Name",
                },
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.first()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertEqual(Article.objects.count(), 1)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "regions": [
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                    {
                        "id": regions.all()[1].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                ],
                "author": 
                {   
                    "id": self.author.id,
                    "first_name": "Updated Test First Name",
                    "last_name": "Updated Test Last Name",
                },
            },
            response.json(),
        )
        # Remove regions and author
        payload["regions"] = []
        payload["author"] = None
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "regions": [],
                "author": None
            },
            response.json(),
        )

    def test_removes_article(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 0)

class AuthorListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('authors-list')
        self.author_1 = Author.objects.create(first_name="Test First Name", last_name="Test Last Name")
        self.author_2 = Author.objects.create(first_name="Test First Name1", last_name="Test Last Name1")

    def test_serializes_shape_with_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [{
                "id": self.author_1.id,
                "first_name": "Test First Name",
                "last_name": "Test Last Name"
            },
            {
               "id": self.author_2.id,
                "first_name": "Test First Name1",
                "last_name": "Test Last Name1" 
            }])

    def test_create_new_author(self):
        body = {
            "first_name": "Test First Name2",
            "last_name": "Test Last Name2"
        }
        response = self.client.post(self.url, data=json.dumps(body), content_type="application/json")
        author = Author.objects.last()
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(author)
        self.assertDictEqual(
            {   
                "id": author.id,
                "first_name": "Test First Name2",
                "last_name": "Test Last Name2",
            }, response.json()
        )

class AuthorViewTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="Test First Name", last_name="Test Last Name")
        self.url = reverse("author", kwargs = {"author_id": self.author.id})

    def test_single_record_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.author.id,
                "first_name": "Test First Name",
                "last_name": "Test Last Name"
            }
        )
    def test_update_author(self):
        body = {
            "id": self.author.id,
            "first_name": "Updated Test First Name",
            "last_name": "Updated Test Last Name"
        }
        response = self.client.put(self.url, data=json.dumps(body), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        author = Author.objects.last()
        self.assertIsNotNone(author)
        self.assertDictEqual(
            response.json(),
            {
                "id": self.author.id,
                "first_name": "Updated Test First Name",
                "last_name": "Updated Test Last Name"
            }
        )
    def test_delete_author(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 0)