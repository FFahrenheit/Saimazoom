class BaseModel:
    def get_body(self) -> dict:
        return vars(self)
    
    def from_dict(self, d):
        for key, value in d.items():
            setattr(self, key, value)