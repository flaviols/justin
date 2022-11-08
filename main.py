import requests
import certifi
from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
from bannercompra import Bannercompra
import os
from functools import partial
from accountmanager import AccountManager
from bannercomprador import Bannercomprador
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
        incluircomprapage = self.root.ids["incluircomprapage"]
        lista_clientes = incluircomprapage.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}", on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png", "").capitalize(), on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        # carregar as fotos dos produtos
        arquivos = os.listdir("icones/fotos_produtos")
        incluircomprapage = self.root.ids["incluircomprapage"]
        lista_produtos = incluircomprapage.ids["lista_produtos"]
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}", on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(), on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        # carregar a data
        incluircomprapage = self.root.ids["incluircomprapage"]
        data_compra = incluircomprapage.ids["data_compra"]
        data_compra.text = f"Data: {date.today().strftime('%d/%m/%Y')}"

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
            usuario = requests.get(f"https://justin-default-rtdb.firebaseio.com/{self.local_id}.json?auth={id_token}")
            usuario_dic = usuario.json()
            # preencher foto de perfil
            self.avatar = usuario_dic["avatar"]
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"
            self.equipe = usuario_dic["equipe"]

            #   preencher o id Único do Usuário
            id_comprador = usuario_dic["id_comprador"]
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids["id_comprador"].text = f"ID: {id_comprador}"
            #   preencher o total de compras
            total_compras = usuario_dic["total_compras"]
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_compras"].text = f"[color=#000000] Todas as compras: [/color] [b]R$ {total_compras}[/b]"
            # preencher lista de compras
            try:
                compras = usuario_dic["compras"]
                homepage = self.root.ids["homepage"]
                lista_compras = homepage.ids["lista_compras"]
                for id_compra in compras:
                    compra = compras[id_compra]
                    banner = Bannercompra(cliente=compra["cliente"], foto_cliente=compra["foto_cliente"], data=compra["data"],
                                         produto=compra["produto"], foto_produto=compra["foto_produto"],
                                         unidade=compra["unidade"], preco=compra["preco"],
                                         quantidade=compra["quantidade"])
                    lista_compras.add_widget(banner)
            except:
                pass
                # pass def carregar_infos_usuario(self):

            #  Preencher equipe do usuário(compradores)
            equipe = usuario_dic["equipe"]
            listarcompradorespage = self.root.ids["listarcompradorespage"]
            listarcompradores = listarcompradorespage.ids["lista_compradores"]

            lista_equipe = equipe.split(",")
            for id_comprador_equipe in lista_equipe:
                if id_comprador_equipe != "":
                    banner_comprador = Bannercomprador(id_comprador=id_comprador_equipe)
                    listarcompradores.add_widget(banner_comprador)

            # listarcompradorespage.ids["equipe"].text = f"[color=#000000] Todas as compras: [/color] [b]R$ {total_compras}[/b]"
            self.trocar_tela("homepage")
        except:
            pass


    def trocar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"

        parm_foto = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f"https://justin-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                                    data=parm_foto)

        self.trocar_tela("ajustespage")

    def trocar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def selecionar_cliente(self, foto, *args):
        # pintar de branco todas as outras letras
        incluircomprapage = self.root.ids["incluircomprapage"]
        self.cliente = foto.replace(".png", "")
        lista_clientes = incluircomprapage.ids["lista_clientes"]
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
        incluircomprapage = self.root.ids["incluircomprapage"]
        self.produto = foto.replace(".png", "")
        lista_produtos = incluircomprapage.ids["lista_produtos"]
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
        incluircomprapage = self.root.ids["incluircomprapage"]
        self.unidade = id_label.replace("unidade_", "")
        # pintar todo mundo de branco
        incluircomprapage.ids["unidade_kg"].color = (1, 1, 1, 1)
        incluircomprapage.ids["unidade_unidades"].color = (1,1,1,1)
        incluircomprapage.ids["unidade_litros"].color = (1,1,1,1)
        # pintar a unidade  selecionada de azul
        incluircomprapage.ids[id_label].color = (0, 207/255, 219/255, 1)


    def incluir_compras(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade

        incluircomprapage = self.root.ids["incluircomprapage"]
        data = incluircomprapage.ids["data_compra"].text.replace("Data: ", "")
        preco = incluircomprapage.ids["preco_total"].text
        quantidade = incluircomprapage.ids["quantidade"].text


        # Se não tem cliente preenchido
        if not cliente:
            incluircomprapage.ids["selecionar_cliente"].color = (1, 0, 0, 1)
        else: # gambiarra para evitar pintar de vermelho
            incluircomprapage.ids["selecionar_cliente"].color = (1, 1, 1, 1)

        # Se não tem produto preenchido
        if not produto:
            incluircomprapage.ids["selecionar_produto"].color = (1, 0, 0, 1)
        else: # gambiarra para evitar pintar de vermelho
            incluircomprapage.ids["selecionar_produto"].color = (1, 1, 1, 1)

        # Se não tem cliente preenchido
        if not unidade:
            incluircomprapage.ids["unidade_kg"].color = (1, 0, 0, 1)
            incluircomprapage.ids["unidade_unidades"].color = (1, 0, 0, 1)
            incluircomprapage.ids["unidade_litros"].color = (1, 0, 0, 1)

        if not preco:
            incluircomprapage.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                incluircomprapage.ids["label_preco"].color = (1, 0, 0, 1)

        if not quantidade:
            incluircomprapage.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                incluircomprapage.ids["label_quantidade"].color = (1, 0, 0, 1)

        # garantindo que os dados existam
        # Se está tudo OK entao incluir no BD.
        if cliente and produto and unidade and preco and quantidade and (type(preco == float) and type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}", "quantidade": "{quantidade}"}}'
            requests.post(f"https://justin-default-rtdb.firebaseio.com/{self.local_id}/compras.json?auth={self.id_token}", data=info)

            # criar o banner  de compra para a hpmepage
            banner = Bannercompra(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto, data=data, preco=preco, quantidade=quantidade, unidade=unidade)
            homepage = self.root.ids["homepage"]
            lista_compras = homepage.ids["lista_compras"]
            lista_compras.add_widget(banner)

            # adiciona preco da compra efetuada no total das compras
            total_compras = requests.get(f"https://justin-default-rtdb.firebaseio.com/{self.local_id}/total_compras.json?auth={self.id_token}")
            total_compras = float(total_compras.json())
            total_compras += float(preco)
            info = f'{{"total_compras": "{total_compras}"}}'
            requests.patch(f"https://justin-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)

            homepage.ids["label_total_compras"].text = f"[color=#000000] Todas as compras: [/color] [b]R$ {total_compras}[/b]"

            # Redireciona para a homepage
            self.trocar_tela("homepage")

        # limpando os dados de cliente, produto e unidade
        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_compras(self):
        # Limpando os banner preexistentes em todascompraspage
        todascompraspage = self.root.ids["todascompraspage"]
        lista_compras = todascompraspage.ids["lista_compras"]

       # Para evitar duplicidade(recarregamento do mesmo item,
       # limpar a lista_compras no início de cada carregamento.
        for item in list(lista_compras.children):
            lista_compras.remove_widget(item)

        # preencher a página todascompraspage
        # criar o banner  de compra para a hpmepage

        # pegar informações de toda a empresa
        empresa_dic = requests.get(f'https://justin-default-rtdb.firebaseio.com/.json?orderBy="id_comprador"')
        empresa = empresa_dic.json()
        # preencher foto de perfil
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/inovati.png"

        total_compras = 0
        try:
            for id_usuario in empresa:
                try:
                    compras = empresa[id_usuario]["compras"]
                    # todascompraspage = self.root.ids["todascompraspage"]
                    lista_compras = todascompraspage.ids["lista_compras"]
                    # compras = usuario["compras"]
                    for id_compra in compras:
                        compra = compras[id_compra]
                        banner = Bannercompra(cliente=compra["cliente"], foto_cliente=compra["foto_cliente"],
                                             data=compra["data"],
                                             produto=compra["produto"], foto_produto=compra["foto_produto"],
                                             unidade=compra["unidade"], preco=compra["preco"],
                                             quantidade=compra["quantidade"])
                        lista_compras.add_widget(banner)
                        total_compras += float(compra["preco"])
                    #   preencher o total de compras
                    todascompraspage.ids[
                        "label_total_compras"].text = f"[color=#000000] Todas as compras: [/color] [b]R$ {total_compras}[/b]"
                except Exception as excecao:
                    print(excecao)

        except Exception as excecao:
            print(excecao)

        # Redireciinar para a pagina todascompraspage
        self.trocar_tela("todascompraspage")

    def sair_todas_compras(self):
        # voltar com a foto de perfil do usuario
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"

        self.trocar_tela("ajustespage")

    def adicionar_comprador(self, id_comprador_adicionado):
        link = f'https://justin-default-rtdb.firebaseio.com/.json?orderBy="id_comprador"&equalTo="{id_comprador_adicionado}"'
        comprador = requests.get(link)
        comprador_dic = comprador.json()

        adicionarcompradorpage = self.root.ids["adicionarcompradorpage"]
        mensagem_texto = adicionarcompradorpage.ids["mensagem_outrocomprador"]

        if comprador_dic == {}:
            mensagem_texto.text = "comprador não encontrado"
        else:
            equipe = self.equipe.split(",")
            if id_comprador_adicionado in equipe:
                mensagem_texto.text = "comprador já está na equipe"
            else:
                self.equipe = self.equipe + f",{id_comprador_adicionado}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://justin-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                               data=info)
                mensagem_texto.text = "comprador adicionado com sucesso !"
                # adicionar um novo banner na lista de compradores
                listarcompradorespage = self.root.ids["listarcompradorespage"]
                listarcompradores = listarcompradorespage.ids["lista_compradores"]
                banner_comprador = Bannercomprador(id_comprador=id_comprador_adicionado)
                listarcompradores.add_widget(banner_comprador)


    def carregar_compras_comprador(self, dados_comprador_dic, *args):
        total_compras = dados_comprador_dic["total_compras"]
        # Para evitar duplicidade(recarregamento do mesmo item,
        try:
            compras = dados_comprador_dic["compras"]
            comprascompradorpage = self.root.ids["comprascompradorpage"]
            lista_compras = comprascompradorpage.ids["lista_compras"]

            # limpar a lista_compras no início de cada carregamento.
            for item in list(lista_compras.children):
                lista_compras.remove_widget(item)

            # Carregar Lista compras
            for id_compra in compras:
                compra = compras[id_compra]
                banner = Bannercompra(cliente=compra["cliente"], foto_cliente=compra["foto_cliente"],
                                     data=compra["data"],
                                     produto=compra["produto"], foto_produto=compra["foto_produto"],
                                     unidade=compra["unidade"], preco=compra["preco"],
                                     quantidade=compra["quantidade"])
                lista_compras.add_widget(banner)
                # total_compras += float(compra["preco"])

            #   preencher o total de compras
            comprascompradorpage.ids["label_total_compras"].text = \
                f"[color=#000000] Todas as compras: [/color] [b]R$ {total_compras}[/b]"

        except Exception as excecao:
            print(excecao)

        # preencher foto de perfil
        foto_perfil = self.root.ids["foto_perfil"]
        avatar = dados_comprador_dic["avatar"]
        foto_perfil.source = f"icones/fotos_perfil/{avatar}"

        self.trocar_tela("comprascompradorpage")


MainApp().run()