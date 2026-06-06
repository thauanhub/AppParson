import random
import json
from django.shortcuts import render, get_object_or_404
from parsons.models import Problem

def resolver_parsons(request, problem_id):
    problema = get_object_or_404(Problem, id=problem_id, question_type='P')
    
    linhas_originais = problema.options.splitlines()
    gabarito = []
    linhas_embaralhadas = []

    for linha in linhas_originais:
        if not linha.strip():  # Ignora linhas totalmente vazias
            continue
        
        # Conta os espaços em branco no início da linha
        espacos_iniciais = len(linha) - len(linha.lstrip())
        
        # Define o nível de indentação (Assumindo 4 espaços = 1 tab/nível)
        nivel_indentacao = espacos_iniciais // 4 
        
        # Limpa o texto para exibir na tela sem os espaços
        texto_limpo = linha.strip()
        
        # Salva o gabarito (Texto + Nível correto)
        gabarito.append({
            'codigo': texto_limpo,
            'indent': nivel_indentacao
        })
        
        linhas_embaralhadas.append(texto_limpo)

    # Embaralha as linhas para o aluno
    random.shuffle(linhas_embaralhadas)

    context = {
        'problema': problema,
        'linhas_embaralhadas': linhas_embaralhadas,
        'gabarito_json': json.dumps(gabarito) # Envia o novo formato para o JS
    }
    return render(request, 'parsons.html', context)