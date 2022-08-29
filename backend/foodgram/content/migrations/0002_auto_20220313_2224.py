import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name'], 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-id'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='favourite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourite', to='content.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favourite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourite', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название ингредиента'),
        ),
        migrations.AlterField(
            model_name='ingredientsrecipe',
            name='amount',
            field=models.IntegerField(default=1, verbose_name='Количество ингредиентор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(default=1, verbose_name='Время приготовленмя'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(max_length=1000, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='shopping',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppings', to='content.recipe', verbose_name='Рецепт'),
        ),
    ]
