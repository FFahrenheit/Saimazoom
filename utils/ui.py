import os
import keyboard
import time
import threading

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

    def get_simple_menu(self, options, prompt):
        valid = False

        while not valid:
            self.clear()
            print(prompt)
            for i, option in enumerate(options):
                print(f"\t[{i+1}] {option}")

            choice = input("\nSu eleccion: ")
            if not choice.isdigit():
                self.wait("Opcion invalida. Presione enter para continuar")
            else:
                selected = int(choice)
                if selected >= 1 and selected <= len(options):
                    valid = True

        self.clear()

        return selected - 1


    def get_option_menu(self, options: list, prompt="Seleccione una opcion del menu:", old_ui=True) -> int:   
        if old_ui:
            return self.get_simple_menu(options, prompt)
        
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

    def wait_queue(self, message="Enviando peticion..."):
        self.clear()
        print(message)

    def notify(self, message:str):
        print('\a')

        print(f"[{threading.current_thread().ident}] {message}")

    # Imprimir progreso
    """
        Llamar en loop para crear progreso en consola
        @params:
            iteration   - Required  : iteracion actual (Int)
            total       - Required  : total iteraciones (Int)
            prefix      - Optional  : mensaje inicio (Str)
            suffix      - Optional  : mensaje final (Str)
            decimals    - Optional  : decimales a usar (Int)
            length      - Optional  : longitud de barra (Int)
            fill        - Optional  : relleno de barra (Str)
            print_end    - Optional : fin de cadena (e.g. "\r", "\r\n") (Str)
            auto_clean   - Optional : limpiear en cada iteracion (bool)
    """
    def progress_bar(self, iteration: int, total: int, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r", auto_clean=True):
        if auto_clean:
            self.clear()
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = print_end)
        # Print New Line on Complete
        if iteration == total: 
            print()