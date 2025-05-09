#handlers/login_handler.py

class LoginHandler:
    def __init__(self, facade):
        self.facade = facade

    def handle(self, text, user_state):
        chat_id = self.facade.chat_id
        auth = self.facade.auth_service
        bot = self.facade.bot_service
    

        if text == "🔐 Login":
            self.facade.ask_for_email()
            auth.set_user_state("waiting_for_login_email")

        elif user_state == "waiting_for_login_email":
            auth.set_session_data("email", text.strip())
            auth.set_user_state("waiting_for_login_password")
            bot.send_message(chat_id, "🔑 Please enter your password:")

        elif user_state == "waiting_for_login_password":
            email = auth.get_session_data("email")
            password = text.strip()
            response = auth.send_login_request(email, password)

            if response.get("status") == "success":
                self.facade.send_login_success()
                print('response is',response)
                if response.get('user_type')=='customer':
                    auth.set_user_state("customer_menu")
                    print('loged in user state here is',auth.get_user_state())
                    self.facade.send_customer_menu()
                elif response.get('user_type')=='professional':
                    auth.set_user_state("professional_menu")
                    self.facade.send_professional_menu()
            else:
                self.facade.send_login_failure(error=response.get('error'))
                self.facade.send_main_menu(message='please try to login again!')

            # auth.clear_session()
