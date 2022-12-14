import requests
from kivy.app import App


class AccountManager:
    API_KEY = "AIzaSyCy1TUrBafJ_D5kL9k6ITilD1QZbG_nn2U"

    def criar_conta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        signup_post = requests.post(link, data=info)
        signup_post_dic = signup_post.json()

        if signup_post.ok:
            # signup_post_dic["idToken"]         -> autenticação
            # signup_post_dic["refreshToken"]    -> token que mantém o usuário logado
            # signup_post_dic["localId"]         -> id_usuario
            refresh_token = signup_post_dic["refreshToken"]
            id_token = signup_post_dic["idToken"]
            local_id = signup_post_dic["localId"]
            # Quem é o aplicativo principal ?
            main_app = App.get_running_app()
            # Armazenando as informações do usuario no aplicativo principal(App):
            main_app.local_id = local_id
            main_app.id_token = id_token
            # guardando o refresh_token para utilizaćão em um novo login("Lembrar")

            try:
                with open("refresh_token.txt", "w") as arquivo:
                    arquivo.write(refresh_token)
            except:
                pass

            # Busca o próximo ID comprador

            proximo_id = requests.get(f"https://justin-55643-default-rtdb.firebaseio.com/"
                                      f"proximo_id_comprador.json?auth={id_token}")
            id_comprador = proximo_id.json()
            # Atualiza / Cria Usuario
            link = f"https://justin-55643-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
            info_usuario = f'{{"id_comprador": "{id_comprador}", "avatar": "foto3.png", ' \
                           f'"equipe": "", "total_compras": "0", "compras": ""}}'

            # O PATCH É para criar um usuário com a chave(local_Id) que queremos. O Post cria com uma chave
            # inédita para o firebase
            atualiza_ou_cria_usuario = requests.patch(link, data=info_usuario)

            # Atualizar o valor do "proximo_id_comprador"
            link = f"https://justin-55643-default-rtdb.firebaseio.com/.json?auth={id_token}"
            proximo_id = int(id_comprador) + 1
            proximo_id_dic = f'{{"proximo_id_comprador": "{proximo_id}"}}'
            atualiza_id_proximo_comprador = requests.patch(link, data=proximo_id_dic)
            # Indo para a HOMEPAGE
            main_app.carregar_infos_usuario()
            main_app.trocar_tela("homepage")
        else:
            mensagem_erro = signup_post_dic["error"]["message"]
            main_app = App.get_running_app()
            login_page = main_app.root.ids["loginpage"]
            login_page.ids["mensagem_login"].text = mensagem_erro
            login_page.ids["mensagem_login"].color = (1, 0, 0, 1)

    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email, "password": senha, "returnSecureToken": True}

        signin_post = requests.post(link, data=info)
        signin_post_dic = signin_post.json()

        if signin_post.ok:
            refresh_token = signin_post_dic["refreshToken"]
            id_token = signin_post_dic["idToken"]
            local_id = signin_post_dic["localId"]
            # Quem é o aplicativo principal ?
            main_app = App.get_running_app()
            # Armazenando as informações do usuario no aplicativo principal(App):
            main_app.local_id = local_id
            main_app.id_token = id_token
            # guardando o refresh_token para utilizaćão em um novo login("Lembrar")
            with open("refresh_token.txt", "w") as arquivo:
                arquivo.write(refresh_token)
            # Indo para a HOMEPAGE
            main_app.carregar_infos_usuario()
            main_app.trocar_tela("homepage")

        else:
            mensagem_erro = signin_post_dic["error"]["message"]
            main_app = App.get_running_app()
            login_page = main_app.root.ids["loginpage"]
            login_page.ids["mensagem_login"].text = mensagem_erro
            login_page.ids["mensagem_login"].color = (1, 0, 0, 1)

    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        # trocar_token --> change_token ?
        change_token = requests.post(link, data=info)
        change_token_dic = change_token.json()
        local_id = change_token_dic["user_id"]
        id_token = change_token_dic["id_token"]
        return local_id, id_token
