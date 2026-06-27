import random
import json
from django.shortcuts import render, get_object_or_404
from parsons.models import Problem, Solution

def verifica_indentacao(linha):
   
    # Conta os espaços em branco no início da linha
    espacos_iniciais = len(linha) - len(linha.lstrip())
    
    # Define o nível de indentação (Assumindo 4 espaços = 1 tab/nível)
    nivel_indentacao = espacos_iniciais // 4 
    
    # Limpa o texto para exibir na tela sem os espaços
    texto_limpo = linha.strip()
    
    return nivel_indentacao, texto_limpo


def resolver_parsons(request, problem_id):
    problema = get_object_or_404(Problem, id=problem_id, question_type='P')
    
    linhas_originais = problema.options.splitlines()
    linhas_embaralhadas = []
    
    solution = Solution.objects.filter(problem__id=problem_id).first()
    linhas_solucao = []
    gabarito = []
    if solution:
        linhas_solucao = solution.content.splitlines()
    
    for linha_original in linhas_originais:
        if not linha_original.strip():  # Ignora linhas totalmente vazias
            continue
        
        texto_limpo = linha_original.strip()  
        linhas_embaralhadas.append(texto_limpo)
        
    for linha_solucao in linhas_solucao:
        
        if not linha_solucao.strip():  # Ignora linhas totalmente vazias
            continue
        
        nivel_indentacao, texto_limpo = verifica_indentacao(linha_solucao)
        
        # Salva o gabarito (Texto + Nível correto)
        gabarito.append({
            'codigo': texto_limpo,
            'indent': nivel_indentacao
        })

    # Embaralha as linhas para o aluno
    random.shuffle(linhas_embaralhadas)

    context = {
        'problema': problema,
        'linhas_embaralhadas': linhas_embaralhadas,
        'gabarito_json': json.dumps(gabarito) # Envia o novo formato para o JS
    }
    return render(request, 'parsons.html', context)





# @login_required
# def show_problem(request, problem_id):
#     #try:
#     context = get_problem(problem_id)
    
#     problem = problem_id
#     exercise_sets = ExerciseSet.objects.filter(problem=problem)
#     chapters = [es.chapter for es in exercise_sets]
#     links = []
#     for chapter in chapters:
#         links.extend(chapter.link.all())

#     context['links'] = links

#     #except Problem.DoesNotExist:
#         #raise Http404("Problem does not exist")
#     return render(request, 'questions/show_problem.html', context)
# Chamar a view show_Problem e tratar no método auxiliar, pode retornar um html diferente (show_problem_parson.html)
# Fazer teste automatizado com playwright
# Fazer teste de backend testcase