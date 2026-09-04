import json
import random

from django.shortcuts import redirect, render

from .problems import PROBLEMAS, gabarito_de, get_problema_ou_404


def parsons_faded_home(request):
    """Raiz do protótipo: leva direto ao primeiro exemplo."""
    return redirect('parsons_faded_problem', problem_id=1)


def parsons_faded_problem(request, problem_id):
    """
    Protótipo visual de Parsons Faded com problemas estáticos.

    A modelagem (novo question_type "PF" etc.) ainda não foi definida, então
    os problemas ficam hardcoded em problems.py, sem banco de dados. Cada
    linha (option) tem um id, a indentação esperada e partes (texto fixo ou
    trecho apagado a ser preenchido).
    """
    problema = get_problema_ou_404(problem_id)

    linhas = problema['options']
    linhas_embaralhadas = linhas[:]
    random.shuffle(linhas_embaralhadas)

    context = {
        'title': 'Parsons Faded',
        'problema': problema,
        'linhas_embaralhadas': linhas_embaralhadas,
        'qtd_fades': sum(linha['tem_fade'] for linha in linhas),
        'gabarito_json': json.dumps(gabarito_de(linhas)),
        'problemas_disponiveis': PROBLEMAS,
    }
    return render(request, 'parsons_faded.html', context)
