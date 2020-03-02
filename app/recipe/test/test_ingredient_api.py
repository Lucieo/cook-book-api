from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@lucieo.com',
            'testpassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Tomato')
        Ingredient.objects.create(user=self.user, name='Pepper')
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Retrieve all ingredients / serialize them / compare to response
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients linked to user are returned"""
        user2 = get_user_model().objects.create_user(
            'test2@lucieo.com',
            'testpassword2'
        )
        created_ingredient = Ingredient.objects.create(
            user=self.user,
            name='Garlic')
        Ingredient.objects.create(user=user2, name='Watermelon')
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], created_ingredient.name)

    def test_create_ingredients_successful(self):
        """Test ingredient created successfully"""
        payload = {'name': 'Cucumber'}
        res = self.client.post(INGREDIENT_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']).exists()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test ingredient is not created if invalid payload"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test retrieving only ingredients assigned to recipe"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Pear')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Carrots')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Chocolate and Pear cake',
            price=15.50,
            time_minutes=20,
            description="pears are so good"
        )
        recipe1.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test retrieving ingredients assigned unique"""
        ingredient = Ingredient.objects.create(user=self.user, name="egg")
        Ingredient.objects.create(user=self.user, name="carrot")
        recipe = Recipe.objects.create(
            user=self.user,
            title="Omlette",
            time_minutes=10,
            price=20.50,
            description="nice Omlette"
        )
        recipe.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="Cream caramel",
            time_minutes=20,
            price=10.00,
            description="miam"
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data), 1)
