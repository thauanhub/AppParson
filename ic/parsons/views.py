import random
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from parsons.models import Problem, Solution, Language
from parsons.get_problem import LOGGER, get_problem
from django.contrib.auth.decorators import login_required
from .forms import UserLogForm

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
        'problem': problema,
        'linhas_embaralhadas': linhas_embaralhadas,
        'gabarito_json': json.dumps(gabarito) # Envia o novo formato para o JS
    }
    return render(request, 'parsons.html', context)

# @login_required
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Faça login agora.')
            return redirect('login')
        else:
            messages.error(request, 'Erro no cadastro. Verifique os dados e tente novamente.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def parsons_home(request):
    problemas = Problem.objects.filter(question_type='P').order_by('id')
    return render(request, 'parsons_home.html', {
        'title': 'Parsons Home',
        'problemas': problemas,
    })


@login_required
def show_problem(request, problem_id):
     #try:
     problema = get_object_or_404(Problem, id=problem_id, question_type='P')
     context = get_problem(problem_id)

     if problema.question_type == 'P':
         return resolver_parsons(request, problem_id)
    
     #exercise_sets = ExerciseSet.objects.filter(problem=problem)
     #chapters = [es.chapter for es in exercise_sets]
     #links = []
     #for chapter in chapters:
         #links.extend(chapter.link.all())

     #context['links'] = links

     #except Problem.DoesNotExist:
         #raise Http404("Problem does not exist")
     return render(request, 'questions/show_problem.html', context)



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

@login_required
def save_user_log(request):
    # if request.POST['language'] not in supported_languages:
        # return JsonResponse({'status': 'failed', 'message': 'Language not supported'})
    request.POST = request.POST.copy()  #Criando uma cópia de request.POST, pois ele é imutável
    request.POST.pop('language', None)
    default_language, created = Language.objects.get_or_create(name='Unknown')
    if created:
        LOGGER.debug('Created default language Unknown with id %s', default_language.id)
    request.POST['language'] = str(default_language.id)
    form = UserLogForm(request.POST)
    LOGGER.debug("Log received for user %s with outcome %s: %s",
                 request.user,
                 request.POST.get('outcome'),
                 request.POST.get('solution'))
    if form.is_valid():
        log = form.save(commit=False)
        log.user = request.user
        log.user_class = None
        if hasattr(request.user, 'userprofile'):
            try:
                log.user_class = request.user.userprofile.user_class
            except Exception:
                pass
        log.save()
        return JsonResponse({'status': 'success'})
    LOGGER.debug("Log failed: %s", form.errors)
    return JsonResponse({'status': 'failed', 'errors': form.errors})