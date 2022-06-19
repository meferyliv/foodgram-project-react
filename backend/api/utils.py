from django.http import HttpResponse

from recipes.models import IngredientAmount


def generate_shopping_list(request):
    ingredients = IngredientAmount.objects.filter(
        recipe__carts__user=request.user.id).values_list(
        'ingredient__name', 'ingredient__measurement_unit', 'amount'
    )
    ingredients_dict = {}
    for item in ingredients:
        name = item[0]
        if name not in ingredients_dict:
            ingredients_dict[name] = {
                'measurement_unit': item[1],
                'amount': item[2]
            }
        else:
            ingredients_dict[name]['amount'] += item[2]
    shopping_cart = ['Список покупок:']
    for i, (name, data) in enumerate(ingredients_dict.items(), 1):
        shopping_cart.append(
            f'\n {i}.{name} -{data["amount"]}, {data["measurement_unit"]}.'
        )
    response = HttpResponse(shopping_cart, content_type='text')
    response['Content-Disposition'] = (
        'attachment;filename=shopping_cart.pdf'
    )
    return response
