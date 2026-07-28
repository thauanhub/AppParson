import os
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright, expect

from parsons.models import Problem, Solution

# Executar teste: python ic/manage.py test parsons.tests.ParsonsProblemUITest
class ParsonsProblemUITest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False, slow_mo=300)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.page = self.browser.new_page()

        # Options com distrator incluído.
        self.options_texto = "a = 1\nb = 2\nprint(a + b)\nc = 3  # distrator"
        self.problema = Problem.objects.create(
            title="Teste",
            content="Organize o código.",
            question_type="P",
            options=self.options_texto,
        )
        Solution.objects.create(
            problem=self.problema,
            content="a = 1\nb = 2\nprint(a + b)",
        )

    def tearDown(self):
        self.page.close()

    def _url(self):
        return self.live_server_url + reverse('show_problem', args=[self.problema.id])

    # ---------- Testes ----------

    def test_pagina_carrega_com_todos_os_blocos(self):
        self.page.goto(self._url())

        quantidade_esperada = len(
            [l for l in self.options_texto.splitlines() if l.strip()]
        )
        blocos = self.page.locator("#blocos-disponiveis .linha-codigo")
        
        expect(blocos).to_have_count(quantidade_esperada)

    def test_verificar_sem_arrastar_da_erro(self):
        self.page.goto(self._url())

        self.page.click("button:has-text('Verificar Código')")

        mensagem = self.page.locator("#mensagem")
        # expect() espera automaticamente o setTimeout(50ms) do JS terminar
        expect(mensagem).to_have_class("feedback erro show")
        expect(mensagem).to_contain_text("Estrutura incorreta")

    def test_montar_solucao_correta_ignorando_distrator(self):
        self.page.goto(self._url())

        area_solucao = self.page.locator("#area-solucao")

        for codigo in ["a = 1", "b = 2", "print(a + b)"]:  # sem o distrator
            origem = self.page.locator(f'.linha-codigo[data-codigo="{codigo}"]').first
            self._arrastar_para_o_final(origem, area_solucao)

        self.page.click("button:has-text('Verificar Código')")

        mensagem = self.page.locator("#mensagem")
        expect(mensagem).to_have_class("feedback sucesso show")
        expect(mensagem).to_contain_text("Perfeito")

    def test_distrator_impede_solucao_correta(self):
        self.page.goto(self._url())

        area_solucao = self.page.locator("#area-solucao")

        for codigo in ["a = 1", "b = 2", "print(a + b)", "c = 3  # distrator"]:
            origem = self.page.locator(f'.linha-codigo[data-codigo="{codigo}"]').first
            self._arrastar_para_o_final(origem, area_solucao)

        self.page.click("button:has-text('Verificar Código')")

        mensagem = self.page.locator("#mensagem")
        expect(mensagem).to_have_class("feedback erro show")

    def test_indentar_via_botao(self):
        """
        Testa o controle de indentação por botão.
        """
        self.page.goto(self._url())

        area_solucao = self.page.locator("#area-solucao")
        origem = self.page.locator('.linha-codigo[data-codigo="a = 1"]').first
        self._arrastar(origem, area_solucao)

        linha_na_solucao = area_solucao.locator('.linha-codigo[data-codigo="a = 1"]')
        botao_aumentar = linha_na_solucao.locator('button[title="Aumentar indentação"]')

        botao_aumentar.click()
        botao_aumentar.click()

        expect(linha_na_solucao).to_have_attribute("data-indent", "2")

    def test_ordem_errada_da_erro(self):
        """
        Monta os blocos corretos, mas fora da ordem esperada da solução.
        """
        self.page.goto(self._url())

        area_solucao = self.page.locator("#area-solucao")

        # Ordem trocada: "print(a + b)" antes de "a = 1" e "b = 2"
        for codigo in ["print(a + b)", "a = 1", "b = 2"]:
            origem = self.page.locator(f'.linha-codigo[data-codigo="{codigo}"]').first
            self._arrastar_para_o_final(origem, area_solucao)

        self.page.click("button:has-text('Verificar Código')")

        mensagem = self.page.locator("#mensagem")
        expect(mensagem).to_have_class("feedback erro show")
        expect(mensagem).to_contain_text("Estrutura incorreta")

    def test_indentacao_errada_da_erro(self):
        """
        Monta os blocos na ordem correta, mas com indentação incorreta
        em uma das linhas (usando o botão de aumentar indentação).
        """
        self.page.goto(self._url())

        area_solucao = self.page.locator("#area-solucao")

        for codigo in ["a = 1", "b = 2", "print(a + b)"]:
            origem = self.page.locator(f'.linha-codigo[data-codigo="{codigo}"]').first
            self._arrastar_para_o_final(origem, area_solucao)

        # Indenta incorretamente a linha "b = 2", que deveria ficar no nível 0
        linha_b = area_solucao.locator('.linha-codigo[data-codigo="b = 2"]')
        botao_aumentar = linha_b.locator('button[title="Aumentar indentação"]')
        botao_aumentar.click()

        self.page.click("button:has-text('Verificar Código')")

        mensagem = self.page.locator("#mensagem")
        expect(mensagem).to_have_class("feedback erro show")
        expect(mensagem).to_contain_text("Estrutura incorreta")
        
        
    # ---------- Helper de drag-and-drop ----------

    def _arrastar_para_o_final(self, origem, area_solucao):
        """
        Solta o bloco sempre abaixo do último item já colocado em #area-solucao.
        """
        origem_box = origem.bounding_box()
        itens_atuais = area_solucao.locator(".linha-codigo")
        quantidade = itens_atuais.count()

        if quantidade == 0:
            destino_box = area_solucao.bounding_box()
            alvo_x = destino_box["x"] + 20
            alvo_y = destino_box["y"] + 20
        else:
            ultimo_item = itens_atuais.nth(quantidade - 1)
            ultimo_box = ultimo_item.bounding_box()
            alvo_x = ultimo_box["x"] + 20
            alvo_y = ultimo_box["y"] + ultimo_box["height"] + 10

        self.page.mouse.move(
            origem_box["x"] + origem_box["width"] / 2,
            origem_box["y"] + origem_box["height"] / 2,
        )
        self.page.mouse.down()
        self.page.mouse.move(alvo_x, alvo_y, steps=10)
        self.page.mouse.up()

    def _arrastar(self, origem, destino, offset_x=15, offset_y=20):
        """
        Simula o arrasto de um elemento para outro.
        """
        origem_box = origem.bounding_box()
        destino_box = destino.bounding_box()

        self.page.mouse.move(
            origem_box["x"] + origem_box["width"] / 2,
            origem_box["y"] + origem_box["height"] / 2,
        )
        self.page.mouse.down()
        self.page.mouse.move(
            destino_box["x"] + offset_x,
            destino_box["y"] + offset_y,
            steps=10,
        )
        self.page.mouse.up()