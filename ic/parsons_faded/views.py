import json
import random

from django.shortcuts import redirect, render

# from .problems import PROBLEMAS, gabarito_de, get_problema_ou_404

from django.shortcuts import render, get_object_or_404, redirect

from .models import ProblemPF, SolutionPF


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
    problema = get_object_or_404(ProblemPF.objects.filter(question_type='F'), id=problem_id)

    linhas = []
    linhas_embaralhadas = []
    # linhas = problema['options']
    linhas = problema.options.splitlines()
    # random.shuffle(linhas_embaralhadas)

    for linha in linhas:
        if not linha.strip():  # Ignora linhas totalmente vazias
            continue
        
        texto_limpo = linha.strip()  
        linhas_embaralhadas.append(texto_limpo)

    context = {
        'title': 'Parsons Faded',
        'problema': problema,
        'linhas_embaralhadas': linhas_embaralhadas,
        # 'qtd_fades': sum(linha['tem_fade'] for linha in linhas),
        'gabarito_json': json.dumps(linhas),
        'problemas_disponiveis': ProblemPF.objects.filter(question_type='F').order_by('id'),
    }
    return render(request, 'parsons_faded.html', context)
