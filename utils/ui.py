import os
import keyboard
import time

class UIConsole:
    def __init__(self, debounce_time = 0.15):
        self.debouce_time = debounce_time

    def clear(self):
        os.system('cls' if os.name=='nt' else 'clear')
    
    def print_menu(self, options : list, selected = 0):
        self.clear()
        print("Selecciona una opcion: \n")

        for i, option in enumerate(options):
            prefix = ">" if i == selected else " "
            print(f" {prefix} {option}")
        print(end='\n')

    def get_option_menu(self, options : list) -> int:
        selected = 0
        self.print_menu(options, selected)
        last = time.time()
        try:
            while True:
                if time.time() - last < self.debouce_time:
                    continue
                
                if keyboard.is_pressed('up'):
                    last = time.time()
                    if selected == 0:
                        selected = len(options) - 1
                    else:
                        selected -= 1
                    self.print_menu(options, selected)
                elif keyboard.is_pressed('down'):
                    last = time.time()
                    if selected == len(options) - 1:
                        selected = 0
                    else:
                        selected += 1
                    self.print_menu(options, selected)
                elif keyboard.is_pressed('enter'):
                    input()
                    self.clear()
                    return selected

        except:
            input()
            self.clear()
            return selected
        
    def print_success(self, message):
        print("")
        print(message)
        input("Presione enter para continuar...")
        self.clear()

    def wait(self, message="Presione enter para continuar...", auto_clean=True):
        input(message)
        if auto_clean:
            self.clear()
