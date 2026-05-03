# from abc import ABC, abstractmethod
# from application.controllers.user_controller import UserController


# class Command(ABC):
#     @abstractmethod
#     def execute(self) -> None:
#         pass


# class RegisterUserCommand(Command):
#     def __init__(self, user_controller: UserController) -> None:
#         self._user_controller = user_controller

#     def execute(self) -> None:
#         username = input("username: ")
#         print(self._user_controller.register_user(username))
