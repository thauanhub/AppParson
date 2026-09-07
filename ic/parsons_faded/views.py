import json

from django.shortcuts import get_object_or_404, redirect, render

from .models import ProblemPF, SolutionPF


def _parts_from_line(line):
    return [{'tipo': 'texto', 'texto': line}]


def _normalizar_blocos(problema):
    try:
        dados = json.loads(problema.options or '[]')
    except (TypeError, json.JSONDecodeError):
        dados = [line for line in problema.options.splitlines() if line.strip()]

    if isinstance(dados, dict):
        dados = dados.get('blocos', dados.get('options', []))

    solution = SolutionPF.objects.filter(problem=problema, ignore=False).first()
    indentacoes = []
    if solution:
        indentacoes = [
            (len(line) - len(line.lstrip())) // 4
            for line in solution.content.splitlines()
            if line.strip()
        ]

    blocos = []
    for index, bloco in enumerate(dados):
        if isinstance(bloco, str):
            bloco = {'id': index + 1, 'partes': _parts_from_line(bloco)}

        partes = bloco.get('partes', bloco.get('parts', []))
        if isinstance(partes, str):
            partes = _parts_from_line(partes)

        partes_normalizadas = []
        for parte in partes:
            if isinstance(parte, str):
                partes_normalizadas.append({'tipo': 'texto', 'texto': parte})
                continue
            tipo = parte.get('tipo', parte.get('type', 'texto'))
            partes_normalizadas.append({
                'tipo': tipo,
                'texto': parte.get('texto', parte.get('text', '')),
                'placeholder': parte.get('placeholder', 'Preencha o código'),
                'resposta': parte.get('resposta', parte.get('answer', '')),
                'linha_inteira': parte.get(
                    'linha_inteira', parte.get('whole_line', False)),
            })

        bloco_id = bloco.get('id', index + 1)
        blocos.append({
            'id': bloco_id,
            'indent': int(bloco.get('indent', indentacoes[index]
                                  if index < len(indentacoes) else 0)),
            'partes': partes_normalizadas,
        })

    return blocos


def _gabarito(blocos):
    return [
        {
            'id': bloco['id'],
            'indent': bloco['indent'],
            'respostas': [
                parte['resposta'] for parte in bloco['partes']
                if parte['tipo'] == 'input'
            ],
        }
        for bloco in blocos
    ]


def parsons_faded_home(request):
    """Raiz do protótipo: leva direto ao primeiro exemplo."""
    return redirect('parsons_faded_problem', problem_id=1)


def parsons_faded_problem(request, problem_id):
    problema = get_object_or_404(ProblemPF.objects.filter(question_type='F'), id=problem_id)
    blocos = _normalizar_blocos(problema)

    context = {
        'title': 'Parsons Faded',
        'problema': problema,
        'blocos_json': json.dumps(blocos),
        'gabarito_json': json.dumps(_gabarito(blocos)),
        'testes_json': json.dumps(problema.test_case_generator or ''),
        'problemas_disponiveis': ProblemPF.objects.filter(question_type='F').order_by('id'),
    }
    return render(request, 'parsons_faded.html', context)
