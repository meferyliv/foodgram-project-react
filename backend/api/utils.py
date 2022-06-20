from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
        'attachment;filename=shopping_cart.pdf'
    )
    pdfmetrics.registerFont(
        TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8')
    )
    page = Canvas(filename=response)
    page.setFont('DejaVuSerif', 24)
    page.drawString(210, 800, 'Список покупок')
    page.setFont('DejaVuSerif', 16)
    height = 760
    for i, (name, data) in enumerate(ingredients_dict.items(), 1):
        page.drawString(
            70, height, (
                f'{i}.{name} -{data["amount"]}, {data["measurement_unit"]}.'
            )
        )
        height -= 30
    page.showPage()
    page.save()
    return response
