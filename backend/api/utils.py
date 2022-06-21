from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from recipes.models import IngredientAmount


def generate_shopping_list(request):
    ingredients = IngredientAmount.objects.filter(
        recipe__carts__user=request.user.id
    ).annotate(amount=Sum('amount')).values_list(
        'ingredient__name', 'amount', 'ingredient__measurement_unit'
    )
    html_template = render_to_string(
        'recipes/template_shop_list.html', {'ingredients': ingredients}
    )
    html = HTML(string=html_template)
    result = html.write_pdf()
    response = HttpResponse(result, content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=shopping_list.pdf'
    return response
