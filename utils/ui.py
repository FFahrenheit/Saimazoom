import os
import keyboard
import time
import threading

class UIConsole:
    def __init__(self, debounce_time=0.15, allow_clear=True):
        """
        Inicializa la clase y define un tiempo de debounce predeterminado.

        Parámetros:
        debounce_time (float): tiempo de debounce en segundos. Valor por defecto es 0.15 segundos.
        """
        self.debouce_time = debounce_time
        self.allow_clear = allow_clear

    def clear(self):
        """
        Limpia la consola.
        """
        if self.allow_clear:
            os.system('cls' if os.name=='nt' else 'clear')
    
    def print_menu(self, options: list, selected = 0):
        """
        Imprime un menú en la consola con las opciones proporcionadas. La opción seleccionada se marca con un ">".

        Parámetros:
        options (list): lista de opciones a mostrar en el menú.
        selected (int): índice de la opción seleccionada. Valor por defecto es 0.
        """
        self.clear()
        print("Selecciona una opcion: \n")

        for i, option in enumerate(options):
            prefix = ">" if i == selected else " "
            print(f" {prefix} {option}")
        print(end='\n')

    def get_simple_menu(self, options, prompt):
        """
        Imprime un menú en la consola y devuelve la opción seleccionada por el usuario.

        Parámetros:
        options (list): lista de opciones a mostrar en el menú.
        prompt (str): mensaje a mostrar al usuario antes de imprimir el menú.

        Retorna:
        int: índice de la opción seleccionada.
        """
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
        """
        Imprime un menú en la consola y devuelve la opción seleccionada por el usuario.

        Parámetros:
        options (list): lista de opciones a mostrar en el menú.
        prompt (str): mensaje a mostrar al usuario antes de imprimir el menú. Valor por defecto es "Seleccione una opcion del menu:".
        old_ui (bool): determina si se utiliza una interfaz de usuario antigua o no. Valor por defecto es True.

        Retorna:
        int: índice de la opción seleccionada.
        """
        if old_ui:
            return self.get_simple_menu(options, prompt)
        
        selected = 0
        self.print_menu(options, selected)
        last = time.time()
        try:
            while True:
                # Debounce
                if time.time() - last < self.debouce_time:
                    continue
                
                if keyboard.is_pressed('up'):
                    # Selección hacia arriba
                    last = time.time()
                    if selected == 0:
                        selected = len(options) - 1
                    else:
                        selected -= 1
                    self.print_menu(options, selected)
                elif keyboard.is_pressed('down'):
                    # Selección hacia abajo
                    last = time.time()
                    if selected == len(options) - 1:
                        selected = 0
                    else:
                        selected += 1
                    self.print_menu(options, selected)
                elif keyboard.is_pressed('enter'):
                    # Confirmar selección
                    input()
                    self.clear()
                    return selected

        except:
            # Salir en caso de excepción
            input()
            self.clear()
            return selected
        
    def print_success(self, message):
        """
        Imprime un mensaje de éxito y espera a que el usuario presione enter para continuar.

        :param message: El mensaje a imprimir.
        """
        print("")
        print(message)
        input("Presione enter para continuar...")
        self.clear()

    def wait(self, message="Presione enter para continuar...", auto_clean=True):
        """
        Espera a que el usuario presione enter.

        :param message: El mensaje a imprimir antes de esperar la entrada del usuario.
        :param auto_clean: Si es True, se llama a self.clear() después de recibir la entrada del usuario.
        """
        input(message)
        if auto_clean:
            self.clear()

    def wait_queue(self, message="Enviando peticion..."):
        """
        Imprime un mensaje mientras espera que una petición se complete.

        :param message: El mensaje a imprimir mientras se espera.
        """
        self.clear()
        print(message)

    def notify(self, message:str):
        """
        Emite una notificación sonora y muestra un mensaje en la consola.

        :param message: El mensaje a mostrar en la consola.
        """
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
        if not self.allow_clear:
            if iteration == 0:
                print(f"{prefix} ... empezando")
            elif iteration == total:
                print(f"{prefix} terminado.")
            return
        
        if auto_clean:
            self.clear()
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = print_end)
        # Print New Line on Complete
        if iteration == total: 
            print()