"""
Clase base de la que parten nuestros modelos
"""
class BaseModel:
    def get_body(self) -> dict:
        """Traduce las propiedades de un objeto a un diccionario

        Returns:
            dict: diccionario con las propiedades y valores del objeto
        """
        return vars(self)
    
    def from_dict(self, d):
        """Asigna las propiedades de un objeto basado en un diccionario

        Args:
            d (_type_): diccionario de donde se obtienen las propiedades en cuestión
        """
        for key, value in d.items():
            setattr(self, key, value)