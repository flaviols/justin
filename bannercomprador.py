from botoes import LabelButton, ImageButton
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
import requests
from kivy.app import App
from functools import partial


class Bannercomprador(FloatLayout):
    def __init__(self, **kwargs):
        # kwargs = {"cliente": "Mundial", "foto_cliente": "mundial.png", "produto": "arroz", ...}
        # todos os dados de uma compra
        # self.rows = 1
        super().__init__()

        with self.canvas:
            Color(rgb=(0, 0, 0, 1))
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.atualizar_rec, size=self.atualizar_rec)

        id_comprador = kwargs["id_comprador"]
        link = f'https://justin-default-rtdb.firebaseio.com/.json?orderBy="id_comprador"&equalTo="{id_comprador}"'
        listar_compradores = requests.get(link)
        listar_compradores_dic = listar_compradores.json()
        dados_comprador = list(listar_compradores_dic.values())[0]
        avatar = dados_comprador["avatar"]
        total_compras = dados_comprador["total_compras"]

        main_app = App.get_running_app()

        imagem = ImageButton(source=f"icones/fotos_perfil/{avatar}",
                             pos_hint={"right": 0.4, "top": 0.9}, size_hint=(0.3, 0.8),
                             on_release=partial(main_app.carregar_compras_comprador, dados_comprador))

        label_id = LabelButton(text=f"ID comprador: {id_comprador}",
                               pos_hint={"right": 0.9, "top": 0.9}, size_hint=(0.5, 0.5),
                               on_release=partial(main_app.carregar_compras_comprador, dados_comprador))
        label_total = LabelButton(text=f"Total de compras: R${total_compras}",
                                  pos_hint={"right": 0.9, "top": 0.6}, size_hint=(0.5, 0.5),
                                  on_release=partial(main_app.carregar_compras_comprador, dados_comprador))

        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_total)

    def atualizar_rec(self, *args):
        self.rec.pos = self.pos
        self.rec.size = self.size
