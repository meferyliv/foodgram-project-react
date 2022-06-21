from django.http import HttpResponse
from reportlab.pdfgen.canvas import Canvas

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
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.pdf"'
    )
    page = Canvas(response)
    page.setFont('Courier', size=16)
    page.drawString(200, 800, 'Список ингредиентов')
    page.setFont('Courier', size=12)
    height = 750
    for i, (name, data) in enumerate(ingredients_dict.items(), 1):
        page.drawString(75, height, (
            f'<{i}> {name} - {data["amount"]}, {data["measurement_unit"]}'
        ))
        height -= 25
    page.showPage()
    page.save()
    return response
