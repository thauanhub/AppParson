"""Problemas Parsons Faded estáticos (protótipo, sem banco de dados).

Cada problema é um dict espelhando os campos do model Problem:
- id: inteiro usado na URL (/parsons_faded/<id>/);
- title/content: enunciado exibido no template;
- options: linhas na ORDEM CORRETA (o gabarito é derivado delas),
  correspondente ao campo Problem.options.
"""

from django.http import Http404


def _linha(linha_id, indent, partes):
    return {
        'id': linha_id,
        'indent': indent,
        'partes': partes,
        'tem_fade': any(p['tipo'] == 'input' for p in partes),
    }


def gabarito_de(linhas):
    """Gabarito esperado (ordem/indent/respostas) derivado das linhas."""
    return [
        {
            'id': linha['id'],
            'indent': linha['indent'],
            'respostas': [p['resposta'] for p in linha['partes']
                          if p['tipo'] == 'input'],
        }
        for linha in linhas
    ]


def _problema(problema_id, title, content, linhas):
    return {'id': problema_id, 'title': title,
            'content': content, 'options': linhas}


PROBLEMAS = [
    # Exemplo 1
    _problema(
        1, 'Maior número da lista',
        ('Complete a função maior_numero(numeros), que recebe uma lista de '
         'números e devolve o maior valor presente nela. Os blocos com '
         'destaque laranja têm trechos apagados: preencha o código que '
         'falta e depois arraste os blocos na ordem correta.'),
        [
            _linha(1, 0, [
                {'tipo': 'texto', 'texto': 'def maior_numero(numeros):'},
            ]),
            _linha(2, 1, [
                {'tipo': 'texto', 'texto': 'maior = numeros[0]'},
            ]),
            _linha(3, 1, [
                {'tipo': 'texto', 'texto': 'for n in numeros:'},
            ]),
            _linha(4, 2, [
                {'tipo': 'texto', 'texto': 'if '},
                {'tipo': 'input', 'placeholder': 'condição',
                 'resposta': 'n > maior'},
                {'tipo': 'texto', 'texto': ':'},
            ]),
            _linha(5, 3, [
                {'tipo': 'input', 'linha_inteira': True,
                 'placeholder': 'Digite o comando dentro do if',
                 'resposta': 'maior = n'},
            ]),
            _linha(6, 1, [
                {'tipo': 'texto', 'texto': 'return maior'},
            ]),
        ],
    ),
    # Exemplo 2
    _problema(
        2, 'Fatorial de um número',
        ('Complete a função fatorial(n), que devolve n! (o produto de todos '
         'os inteiros de 1 a n). Os blocos com destaque laranja têm trechos '
         'apagados: preencha a condição de parada, o retorno do caso base e '
         'a chamada recursiva, e depois arraste os blocos na ordem correta.'),
        [
            _linha(1, 0, [
                {'tipo': 'texto', 'texto': 'def fatorial(n):'},
            ]),
            _linha(2, 1, [
                {'tipo': 'texto', 'texto': 'if '},
                {'tipo': 'input', 'placeholder': 'condição de parada',
                 'resposta': 'n <= 1'},
                {'tipo': 'texto', 'texto': ':'},
            ]),
            _linha(3, 2, [
                {'tipo': 'input', 'linha_inteira': True,
                 'placeholder': 'Digite o retorno do caso base',
                 'resposta': 'return 1'},
            ]),
            _linha(4, 1, [
                {'tipo': 'texto', 'texto': 'return n * fatorial('},
                {'tipo': 'input', 'placeholder': 'chamada recursiva',
                 'resposta': 'n - 1'},
                {'tipo': 'texto', 'texto': ')'},
            ]),
        ],
    ),
]


def get_problema_ou_404(problem_id):
    for problema in PROBLEMAS:
        if problema['id'] == problem_id:
            return problema
    raise Http404('Problema Parsons Faded não encontrado.')
