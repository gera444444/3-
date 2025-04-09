from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)

# Модель автомобиля
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

# Создание бд и примеров авто
def create_db_and_add_examples():
    with app.app_context():
        db.create_all()
        
        
        if Car.query.count() == 0:
            
            example_cars = [
                Car(make='Toyota', model='Camry', year=2000),
                Car(make='Honda', model='Civic', year=2009),
                Car(make='Ford', model='Mustang', year=2011)
            ]
            db.session.bulk_save_objects(example_cars)
            db.session.commit()

create_db_and_add_examples()

# Валидация 
def validate_car_data(data):
    if not re.match(r'^[A-Za-zs]+$', data['make']):
        return "Invalid make"
    if not re.match(r'^[A-Za-z0-9s]+$', data['model']):
        return "Invalid model"
    if not isinstance(data['year'], int) or not (1886 <= data['year'] <= 2023):
        return "Invalid year"
    return None

# Создание авто
@app.route('/cars', methods=['POST'])
def add_car():
    data = request.json
    error = validate_car_data(data)
    if error:
        return jsonify({'error': error}), 400

    new_car = Car(make=data['make'], model=data['model'], year=data['year'])
    db.session.add(new_car)
    db.session.commit()
    
    return jsonify({'id': new_car.id, 'make': new_car.make, 'model': new_car.model, 'year': new_car.year}), 201

# список
@app.route('/cars', methods=['GET'])
def get_cars():
    query = Car.query

    # Фильтрация по марке
    make = request.args.get('make')
    if make:
        query = query.filter(Car.make.ilike(f'%{make}%'))

    # Фильтрация по модели
    model = request.args.get('model')
    if model:
        query = query.filter(Car.model.ilike(f'%{model}%'))

    # Фильтрация по году
    year = request.args.get('year')
    if year:
        query = query.filter(Car.year == int(year))

    # Поиск
    search = request.args.get('search')
    if search:
        query = query.filter((Car.make.ilike(f'%{search}%')) | (Car.model.ilike(f'%{search}%')))

    # Сортировка
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    if order == 'desc':
        query = query.order_by(getattr(Car, sort_by).desc())
    else:
        query = query.order_by(getattr(Car, sort_by))

    # Пагинация
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    cars_paginated = query.paginate(page=page, per_page=per_page)

    # Формирование ответа
    cars_list = [{
        'id': car.id,
        'make': car.make,
        'model': car.model,
        'year': car.year
    } for car in cars_paginated.items]

    return jsonify({
        'total': cars_paginated.total,
        'pages': cars_paginated.pages,
        'current_page': cars_paginated.page,
        'cars': cars_list
    })

# Получение авто по ID 
@app.route('/cars/<int:id>', methods=['GET'])
def get_car(id):
    car = Car.query.get_or_404(id)
    return jsonify({'id': car.id, 'make': car.make, 'model': car.model, 'year': car.year})

# Обновление 
@app.route('/cars/<int:id>', methods=['PUT'])
def update_car(id):
    car = Car.query.get_or_404(id)
    data = request.json
    error = validate_car_data(data)
    if error:
        return jsonify({'error': error}), 400

    car.make = data['make']
    car.model = data['model']
    car.year = data['year']
    
    db.session.commit()
    
    return jsonify({'id': car.id, 'make': car.make, 'model': car.model, 'year': car.year})


@app.route('/cars/<int:id>', methods=['DELETE'])
def delete_car(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    
    return jsonify({'message': 'Car deleted'}), 204


if __name__ == '__main__':
    app.run(debug=True)
