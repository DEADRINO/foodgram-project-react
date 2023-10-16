from users.models import User
from django.contrib.auth.hashers import check_password
from djoser.serializers import (PasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Subscribe, Tag)
from rest_framework import serializers, status


class UserListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return (self.context.get('request').user.is_authenticated
                and Subscribe.objects.filter(
                    user=self.context.get('request').user,
                    author=obj
        ).exists())


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        required_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class IngrediendAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = IngrediendAmountSerializer(
        many=True,
        source='recipe',
        required=True,
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = UserListSerializer(
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        return (self.context.get('request').user.is_authenticated
                and FavoriteRecipe.objects.filter(
                    user=self.context.get('request').user,
                    favorite_recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())


class IngredientsEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeEditSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True)
    ingredients = IngredientsEditSerializer(
        many=True)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True)

    def validate(self, data):
        self.validate_name(data)
        self.validate_ingredients(data)
        self.validate_tags(data)
        self.validate_amounts(data)
        self.validate_cooking_time(data)
        self.validate_image(data)
        return data

    def validate_name(self, data):
        name = data.get('name')
        if len(name) < 4:
            raise serializers.ValidationError(
                {'name':
                 'Название рецепта должно содержать не менее 4 символов'}
            )

    def validate_ingredients(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Загрузите ингредиенты'}
            )
        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError({
                    'ingredients':
                    f'Ингредиента с id - {ingredient["id"]} не существует'
                })
        if len(ingredients) != len(set([item['id'] for item in ingredients])):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!')

    def validate_tags(self, data):
        tags = data.get('tags')
        if len(tags) != len(set([item for item in tags])):
            raise serializers.ValidationError({
                'tags': 'Тэги не должны повторяться!'})

    def validate_amounts(self, data):
        amounts = data.get('ingredients')
        if [item for item in amounts if item['amount'] < 1]:
            raise serializers.ValidationError(
                {'amount': 'Минимальное количество ингредиента - 1'}
            )

    def validate_cooking_time(self, data):
        cooking_time = data.get('cooking_time')
        if cooking_time is None:
            raise serializers.ValidationError(
                {'cooking_time': 'Поле cooking_time является обязательным'}
            )
        if cooking_time > 300 or cooking_time < 1:
            raise serializers.ValidationError(
                {'cooking_time':
                 'Время приготовления блюда должно быть от 1 до 300 минут'}
            )

    def validate_image(self, data):
        image = data.get('image')
        if image is None:
            raise serializers.ValidationError(
                {'image': 'Загрузите изображение'}
            )

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.bulk_create([
                IngredientAmount(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),)
            ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                {'ingredients': 'Поле "ingredients" обязательно'},
                status=status.HTTP_400_BAD_REQUEST)
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                {'tags': 'Поле "tags" обязательно'},
                status=status.HTTP_400_BAD_REQUEST)

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                {'tags': 'Поле "tags" обязательно'},
                status=status.HTTP_400_BAD_REQUEST)

        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                {'ingredients': 'Поле "ingredients" обязательно'},
                status=status.HTTP_400_BAD_REQUEST)

        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)

        instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data
        if data.get('image') is None:
            data['image'] = ''
        return data

    class Meta:
        model = Recipe
        fields = '__all__'
        extra_kwargs = {
            'tags':
            {"error_messages":
                {"does_not_exist": "Ошибка в Тэге"}}}


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class SetPasswordSerializer(PasswordSerializer):
    current_password = serializers.CharField(
        required=True,
        label='Текущий пароль'
    )

    def validate(self, data):
        user = self.context.get('request').user
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                "new_password": "Пароли не должны совпадать"})
        check_current = check_password(data['current_password'], user.password)
        if check_current is False:
            raise serializers.ValidationError({
                "current_password": "Введен неверный пароль"})
        return data


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        source='author.email',
        read_only=True)
    id = serializers.IntegerField(
        source='author.id',
        read_only=True)
    username = serializers.CharField(
        source='author.username',
        read_only=True)
    first_name = serializers.CharField(
        source='author.first_name',
        read_only=True)
    last_name = serializers.CharField(
        source='author.last_name',
        read_only=True)
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='author.recipe.count')

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count',)

    def validate(self, data):
        user = self.context.get('request').user
        author = self.context.get('author_id')
        if user.id == int(author):
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'})
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на данного пользователя'})
        return data

    def get_recipes(self, obj):
        recipes = obj.author.recipe.all()
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data

    def get_is_subscribed(self, obj):
        subscribe = Subscribe.objects.filter(
            user=self.context.get('request').user,
            author=obj.author
        )
        if subscribe:
            return True
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='favorite_recipe.id',
    )
    name = serializers.ReadOnlyField(
        source='favorite_recipe.name',
    )
    image = serializers.CharField(
        source='favorite_recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='favorite_recipe.cooking_time',
    )

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if FavoriteRecipe.objects.filter(user=user,
                                         favorite_recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в избранном'})
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='recipe.id',
    )
    name = serializers.ReadOnlyField(
        source='recipe.name',
    )
    image = serializers.CharField(
        source='recipe.image',
        read_only=True,
    )
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time',
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if ShoppingCart.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в список покупок'})
        return data
