from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///animals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Animal(db.Model):
    __tablename__ = 'animals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Animal {self.name}, Species: {self.species}, Age: {self.age}>"

# Создание базы данных и таблицы
def create_db():
    with app.app_context():
        db.create_all()
        
        if Animal.query.count() == 0:  
            examples = [
                Animal(name="Leo", species="Lion", age=5),
                Animal(name="Milo", species="Cat", age=3),
                Animal(name="Buddy", species="Dog", age=4),
                Animal(name="Coco", species="Parrot", age=2),
                Animal(name="Max", species="Rabbit", age=1)
            ]
            db.session.bulk_save_objects(examples)
            db.session.commit()

create_db()


@app.route('/animals', methods=['POST'])
def create_animal():
    data = request.get_json()
    

#валидация 
def validate_animal_data(data):
    
    if not re.match(r'^[A-Za-zs]+$', data['name']):
        return "Invalid name"
    
   
    if not re.match(r'^[A-Za-zs]+$', data['species']):
        return "Invalid species"
    
    
    if not isinstance(data['age'], int) or data['age'] < 0:
        return "Invalid age"
    
    return None


@app.route('/animals', methods=['GET'])
def get_animals():
    query = Animal.query

    # Фильтрация
    species = request.args.get('species')
    if species:
        query = query.filter(Animal.species == species)

    # Поиск
    name = request.args.get('name')
    if name:
        query = query.filter(Animal.name.ilike(f'%{name}%'))

    # Сортировка
    sort_by = request.args.get('sort_by', 'id')
    if sort_by not in ['id', 'name', 'species', 'age']:
        return jsonify({"error": "Invalid sort parameter."}), 400
    query = query.order_by(getattr(Animal, sort_by))

    # Пагинация
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    animals = query.paginate(page, per_page, error_out=False)

    return jsonify({
        "animals": [{"id": a.id, "name": a.name, "species": a.species, "age": a.age} for a in animals.items],
        "total": animals.total,
        "pages": animals.pages,
        "current_page": animals.page,
        "next_page": animals.next_num,
        "prev_page": animals.prev_num,
    })

@app.route('/animals/<int:id>', methods=['GET'])
def get_animal(id):
    animal = Animal.query.get_or_404(id)
    return jsonify({"id": animal.id, "name": animal.name, "species": animal.species, "age": animal.age})

@app.route('/animals/<int:id>', methods=['PUT'])
def update_animal(id):
    data = request.get_json()
    animal = Animal.query.get_or_404(id)
    
    
if __name__ == '__main__':
    app.run(debug=True)
