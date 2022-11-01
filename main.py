import requests
import certifi
from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
from bannervenda import BannerVenda
import os
from functools import partial
from accountmanager import AccountManager
from bannervendedor import BannerVendedor
from datetime import date

# Criando a variável de ambiente que usa o certifi nas requests
os.environ["SSL_CERT_FILE"] = certifi.where()

GUI = Builder.load_file("main.kv")

class MainApp(App):
    # forçando a existencia de cliente, produto e unidade, caso não existam
    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.accountmanager = AccountManager()
        return GUI

    def on_start(self):
        # carregar as fotos de perfil
        fotos = os.listdir("icones/fotos_perfil")
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]
        for foto in fotos:
            image = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.trocar_foto_perfil, foto))
            lista_fotos.add_widget(image)

        # carregar as fotos dos clientes
        arquivos = os.listdir("icones/fotos_clientes")
        incluirvendapage = self.root.ids["incluirvendapage"]
        lista_clientes = incluirvendapage.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}", on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png", "").capitalize(), on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        # carregar as fotos dos produtos
        arquivos = os.listdir("icones/fotos_produtos")
        incluirvendapage = self.root.ids["incluirvendapage"]
        lista_produtos = incluirvendapage.ids["lista_produtos"]
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}", on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(), on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        # carregar a data
        incluirvendapage = self.root.ids["incluirvendapage"]
        data_venda = incluirvendapage.ids["data_venda"]
        data_venda.text = f"Data: {date.today().strftime('%d/%m/%Y')}"

        # carregar as infos do usuário
        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            with open("refresh_token.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.accountmanager.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token
            # pegar informaćões do usuário
            usuario = requests.get(f"https://aplicativovendasint-default-rtdb.firebaseio.com/{self.local_id}.json?auth={id_token}")
            usuario_dic = usuario.json()
            # preencher foto de perfil
            self.avatar = usuario_dic["avatar"]
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"

            self.equipe = usuario_dic["equipe"]

            #   preencher o id Único do Usuário
            id_vendedor = usuario_dic["id_vendedor"]
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids["id_vendedor"].text = f"ID: {id_vendedor}"

            #   preencher o total de vendas
            total_vendas = usuario_dic["total_vendas"]
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f"[color=#000000] Todas as Vendas: [/color] [b]R$ {total_vendas}[/b]"

            # preencher lista de vendas
            try:
                vendas = usuario_dic["vendas"]
                homepage = self.root.ids["homepage"]
                lista_vendas = homepage.ids["lista_vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"], data=venda["data"],
                                         produto=venda["produto"], foto_produto=venda["foto_produto"],
                                         unidade=venda["unidade"], preco=venda["preco"],
                                         quantidade=venda["quantidade"])
                    lista_vendas.add_widget(banner)
            except Exception as excecao:
                print(excecao)
                # pass def carregar_infos_usuario(self):

            #  Preencher equipe do usuário(vendedores)
            equipe = usuario_dic["equipe"]
            listarvendedorespage = self.root.ids["listarvendedorespage"]
            listarvendedores = listarvendedorespage.ids["lista_vendedores"]

            lista_equipe = equipe.split(",")
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    listarvendedores.add_widget(banner_vendedor)

            # listarvendedorespage.ids["equipe"].text = f"[color=#000000] Todas as Vendas: [/color] [b]R$ {total_vendas}[/b]"

            self.trocar_tela("homepage")
        except Exception as excecao:
            print("Exceção: ", excecao)
            # pass def carregar_infos_usuario(self):


    def trocar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"

        parm_foto = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f"https://aplicativovendasint-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                                    data=parm_foto)

        self.trocar_tela("ajustespage")

    def trocar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def selecionar_cliente(self, foto, *args):
        # pintar de branco todas as outras letras
        incluirvendapage = self.root.ids["incluirvendapage"]
        self.cliente = foto.replace(".png", "")
        lista_clientes = incluirvendapage.ids["lista_clientes"]
        for cliente in list(lista_clientes.children):
            cliente.color = (1,1,1,1)
            # pintar de azul as letras do Cliente selecionado.
            try:
                texto = cliente.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    cliente.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        # pintar de branco todas as outras letras
        incluirvendapage = self.root.ids["incluirvendapage"]
        self.produto = foto.replace(".png", "")
        lista_produtos = incluirvendapage.ids["lista_produtos"]
        for produto in list(lista_produtos.children):
            produto.color = (1,1,1,1)
            # pintar de azul as letras do produto selecionado.
            try:
                texto = produto.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    produto.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        incluirvendapage = self.root.ids["incluirvendapage"]
        self.unidade = id_label.replace("unidade_", "")
        # pintar todo mundo de branco
        incluirvendapage.ids["unidade_kg"].color = (1, 1, 1, 1)
        incluirvendapage.ids["unidade_unidades"].color = (1,1,1,1)
        incluirvendapage.ids["unidade_litros"].color = (1,1,1,1)
        # pintar a unidade  selecionada de azul
        incluirvendapage.ids[id_label].color = (0, 207/255, 219/255, 1)


    def incluir_vendas(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade

        incluirvendapage = self.root.ids["incluirvendapage"]
        data = incluirvendapage.ids["data_venda"].text.replace("Data: ", "")
        preco = incluirvendapage.ids["preco_total"].text
        quantidade = incluirvendapage.ids["quantidade"].text


        # Se não tem cliente preenchido
        if not cliente:
            incluirvendapage.ids["selecionar_cliente"].color = (1, 0, 0, 1)
        else: # gambiarra para evitar pintar de vermelho
            incluirvendapage.ids["selecionar_cliente"].color = (1, 1, 1, 1)

        # Se não tem produto preenchido
        if not produto:
            incluirvendapage.ids["selecionar_produto"].color = (1, 0, 0, 1)
        else: # gambiarra para evitar pintar de vermelho
            incluirvendapage.ids["selecionar_produto"].color = (1, 1, 1, 1)

        # Se não tem cliente preenchido
        if not unidade:
            incluirvendapage.ids["unidade_kg"].color = (1, 0, 0, 1)
            incluirvendapage.ids["unidade_unidades"].color = (1, 0, 0, 1)
            incluirvendapage.ids["unidade_litros"].color = (1, 0, 0, 1)

        if not preco:
            incluirvendapage.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                incluirvendapage.ids["label_preco"].color = (1, 0, 0, 1)

        if not quantidade:
            incluirvendapage.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                incluirvendapage.ids["label_quantidade"].color = (1, 0, 0, 1)

        # garantindo que os dados existam
        # Se está tudo OK entao incluir no BD.
        if cliente and produto and unidade and preco and quantidade and (type(preco == float) and type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}", "quantidade": "{quantidade}"}}'
            requests.post(f"https://aplicativovendasint-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}", data=info)

            # criar o banner  de venda para a hpmepage
            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto, data=data, preco=preco, quantidade=quantidade, unidade=unidade)
            homepage = self.root.ids["homepage"]
            lista_vendas = homepage.ids["lista_vendas"]
            lista_vendas.add_widget(banner)

            # adiciona preco da venda efetuada no total das vendas
            total_vendas = requests.get(f"https://aplicativovendasint-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
            total_vendas = float(total_vendas.json())
            total_vendas += float(preco)
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://aplicativovendasint-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)

            homepage.ids["label_total_vendas"].text = f"[color=#000000] Todas as Vendas: [/color] [b]R$ {total_vendas}[/b]"

            # Redireciona para a homepage
            self.trocar_tela("homepage")

        # limpando os dados de cliente, produto e unidade
        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        # Limpando os banner preexistentes em todasvendaspage
        todasvendaspage = self.root.ids["todasvendaspage"]
        lista_vendas = todasvendaspage.ids["lista_vendas"]

       # Para evitar duplicidade(recarregamento do mesmo item,
       # limpar a lista_vendas no início de cada carregamento.
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        # preencher a página todasvendaspage
        # criar o banner  de venda para a hpmepage

        # pegar informações de toda a empresa
        empresa_dic = requests.get(f'https://aplicativovendasint-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        empresa = empresa_dic.json()
        # preencher foto de perfil
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/inovati.png"

        total_vendas = 0
        try:
            for id_usuario in empresa:
                try:
                    vendas = empresa[id_usuario]["vendas"]
                    # todasvendaspage = self.root.ids["todasvendaspage"]
                    lista_vendas = todasvendaspage.ids["lista_vendas"]
                    # vendas = usuario["vendas"]
                    for id_venda in vendas:
                        venda = vendas[id_venda]
                        banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],
                                             data=venda["data"],
                                             produto=venda["produto"], foto_produto=venda["foto_produto"],
                                             unidade=venda["unidade"], preco=venda["preco"],
                                             quantidade=venda["quantidade"])
                        lista_vendas.add_widget(banner)
                        total_vendas += float(venda["preco"])
                    #   preencher o total de vendas
                    todasvendaspage.ids[
                        "label_total_vendas"].text = f"[color=#000000] Todas as Vendas: [/color] [b]R$ {total_vendas}[/b]"
                except Exception as excecao:
                    print(excecao)

        except Exception as excecao:
            print(excecao)

        # Redireciinar para a pagina todasvendaspage
        self.trocar_tela("todasvendaspage")

    def sair_todas_vendas(self):
        # voltar com a foto de perfil do usuario
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"

        self.trocar_tela("ajustespage")

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativovendasint-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        vendedor = requests.get(link)
        vendedor_dic = vendedor.json()

        adicionarvendedorpage = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = adicionarvendedorpage.ids["mensagem_outrovendedor"]

        if vendedor_dic == {}:
            mensagem_texto.text = "Vendedor não encontrado"
        else:
            equipe = self.equipe.split(",")
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor já está na equipe"
            else:
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://aplicativovendasint-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                               data=info)
                mensagem_texto.text = "Vendedor adicionado com sucesso !"
                # adicionar um novo banner na lista de vendedores
                listarvendedorespage = self.root.ids["listarvendedorespage"]
                listarvendedores = listarvendedorespage.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                listarvendedores.add_widget(banner_vendedor)


    def carregar_vendas_vendedor(self, dados_vendedor_dic, *args):
        total_vendas = dados_vendedor_dic["total_vendas"]
        # Para evitar duplicidade(recarregamento do mesmo item,
        try:
            vendas = dados_vendedor_dic["vendas"]
            vendasvendedorpage = self.root.ids["vendasvendedorpage"]
            lista_vendas = vendasvendedorpage.ids["lista_vendas"]

            # limpar a lista_vendas no início de cada carregamento.
            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)

            # Carregar Lista Vendas
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda["cliente"], foto_cliente=venda["foto_cliente"],
                                     data=venda["data"],
                                     produto=venda["produto"], foto_produto=venda["foto_produto"],
                                     unidade=venda["unidade"], preco=venda["preco"],
                                     quantidade=venda["quantidade"])
                lista_vendas.add_widget(banner)
                # total_vendas += float(venda["preco"])

            #   preencher o total de vendas
            vendasvendedorpage.ids["label_total_vendas"].text = \
                f"[color=#000000] Todas as Vendas: [/color] [b]R$ {total_vendas}[/b]"

        except Exception as excecao:
            print(excecao)

        # preencher foto de perfil
        foto_perfil = self.root.ids["foto_perfil"]
        avatar = dados_vendedor_dic["avatar"]
        foto_perfil.source = f"icones/fotos_perfil/{avatar}"

        self.trocar_tela("vendasvendedorpage")


MainApp().run()
