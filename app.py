# Importação
from flask import Flask, request, jsonify, render_template, redirect, url_for  # adicionei render_template para templates
from flask_sqlalchemy import SQLAlchemy  # botar no docs, caso esqueça o que é tem no caderno
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user  # guarda muitos códigos dentro que ajuda no login do usuario, da uma pesquisada LoginManager faz o gerenciamento de quem tá logado e quem não tá, login_required é uma proteção que obriga o usuario a estar autenticado como adm pra mudar alguma coisa nas rotas em que o login_required for aplicado

# Criando uma variável que vai receber uma instância (É um objeto específico criado a partir de uma classe)
app = Flask(__name__)  # O nome (name) da variável (Flask) é (app)
app.config['SECRET_KEY'] = "minha_chave_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # avisando o computador então de que ele vai usar o banco de dados SQL num arquivo chamado ecommerce?

login_manager = LoginManager()
db = SQLAlchemy(app)  # O objeto db representa o banco de dados e conecta o SQLA ao app Flask, permitindo que o aplicativo gerencie o banco usando as configurações definidas.
login_manager.init_app(app)  # Aqui você tá usando o loggin manager pra receber a aplicação init app
login_manager.login_view = 'login_page'
CORS(app)

# Login e Logout do usuário (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)  # Aqui eu disse que o nome de usuario tem no máximo 80 caracteres, é obrigatório o usuario ter nome e unique diz que os nomes são unicos não pode ter dois com o mesmo nome de usuario
    password = db.Column(db.String(80), nullable=True)  # unique por padrão é falso
    cart = db.relationship('CartItem', backref='user', lazy=True)  # cria uma relaçao para os itens dentro do carrinho do usuário

# Modelagem ou Model pra ser criado precisamos antes criar uma class, no ex abaixo Product é o Model
# Todo Produto Cadastrado aqui deve ter (id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Cria uma coluna inteira chamada id, que serve como identificador único da tabela (chave primária)
    name = db.Column(db.String(120), nullable=False)  # Cria uma coluna de texto chamada name, com no máximo 120 caracteres, e que é obrigatória 
    price = db.Column(db.Float, nullable=False)  # Float permite ter centavos  nullable=False significa que é obrigatório a regra apresentada atrás
    description = db.Column(db.Text, nullable=True)  # Aqui eu falei que eu posso ter produtos sem a descrição

class CartItem(db.Model):  # Criei o modelo do carrinho de compras
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ele vai criar uma chave estrangeira, uma referencia que vai ligar a class user ao carrinho
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # ele vai criar uma chave estrangeira, uma referencia que vai ligar a class product ao carrinho

# Autenticacao
@login_manager.user_loader
def load_user(user_id):  # corrigido o nome da função (era load_use)
    return User.query.get(int(user_id))  # pesquisar pra que serve isso tudo depois

@app.route('/')
def home():  # def é definição a função
    # return 'Hello World'  # removido, vamos renderizar o template HTML
    return render_template('login.html')  # renderiza o template HTML da página inicial

@app.route('/store')
@login_required
def store_page():
    return render_template('store.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=["POST"])  # Metodo POST passa uma informação
def login():
    data = request.json
    # data.get("username") recomendado esse jeito de recuperar o username
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    # Tenta buscar o usuário no banco
    user = User.query.filter_by(username=username).first()

    if user:
        # Usuário existe, aceita qualquer senha (ou você pode deixar a checagem)
        # Se quiser aceitar qualquer senha, não precisa verificar password
        login_user(user)
        return jsonify({"message": "Logged in successfully"})
    else:
        # Se não existe, cria um novo usuário com essa senha e já loga
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({"message": "User created and logged in successfully"})

@app.route('/logout', methods=["POST"])
@login_required
def logout():  # Pesquisar depois o que significa tudo isso
    logout_user()
    return jsonify({"message": "Logout successfully"})

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()  # Notasse que o product está no plural com S no final, pois é mais de uma lista. Esse Product.query.all tá dizendo que vai recuperar (GET) todos os produtos cadastrados como uma lista
    product_list = []
    for product in products:  # for Faz um loop, uma interação, a cada interação ele vai recuperar um produto, ai eu dei o nome que vai ser product (único disponivel pois só tem product) e falei que ele vai ficar em products
        product_data = {
            "id": product.id,  # recuperei a informação do product.id
            "name": product.name,  # recuperei a informação do product.name
            "price": product.price,  # recuperei a informação do product.price
            "description": product.description  # recuperei a informação do product.description
        }
        product_list.append(product_data)  # aqui vai receber algum valor que eu por nessa lista

    return jsonify(product_list)

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # Usuário
    user = User.query.get(int(current_user.id))
    # Produto
    product = Product.query.get(product_id)

    if user and product:  # Tem que ter os dois se um for falso não vai funcionar
        cart_item = CartItem(user_id=user.id, product_id=product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item added to the cart successfully'})
    return jsonify({'message': 'Failed to add item to the cart'}), 400

@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    # Usuario
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_content = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        cart_content.append({
            "id": cart_item.id,
            "user_id": cart_item.user_id,
            "product_id": cart_item.product_id,
            "product_name": product.name,
            "product_price": product.price
        })
    return jsonify(cart_content)

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@login_required
def remove_from_cart(product_id):  # removendo o produto do carrinho
    # Produto, Usuario = Item no carrinho
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()  # pede pro chat explicar essa linha depois
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from the cart successfully'})
    return jsonify({'message': 'Failed to remove item from the cart'}), 400

@app.route('/api/cart/checkout', methods=["POST"])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Checkout successfully. Cart has been cleared'})

if __name__ == "__main__":  # Se o conteúdo da variável name for igual a main, ele será rodado com debug=True
    with app.app_context():
        db.create_all()  # Cria as tabelas automaticamente ao iniciar o app
    app.run(debug=True)

# (debug=True) ativa o modo depuração, isso vai ajudar a ter mais visibilidade do que acontece no servidor

# Pra ver a requisição, aperte o triângulo virado pra direita no canto superior direito do Vscode depois, abra o postman e cole o link que você vai copiar do terminal, depois coloque a rota (no caso do projeto a rota é /teste)
# O que é app.run?
# Na API se você rodou a informação em json e no postman aparecer como html, tá errado, geralmente tem que ser em json também, abaixo um exemplo de retorno em json:
# return jsonify ({"message": "Product added successfully"}) "Product added successfully" return jsonify({"message": "Invalid product data"}), 400
