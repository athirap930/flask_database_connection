from database import db

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id, 
            'name': self.name, 
            'description': self.description
        }
    
    def __repr__(self):
        return f'<Item {self.name}>'