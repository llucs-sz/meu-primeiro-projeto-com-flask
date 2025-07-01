# Importação
from flask import Flask, request, jsonify #esses dois ao lado do Flask são uma atualização de uma trequisição lá de baixo
from flask_sqlalchemy import SQLAlchemy #botar no docs, caso esqueça o que é tem no caderno
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user #guarda muitos códigos dentro que ajuda no login do usuario, da uma pesquisada LoginManager faz o gerenciamento de quem tá logado e quem não tá, login_required é uma proteção que obriga o usuario a estar autenticado como adm pra mudar alguma coisa nas rotas em que o login_required for aplicado

# Criando uma variável que vai receber uma instância (É um objeto específico criado a partir de uma classe)
app = Flask(__name__)    # O nome (name) da variável (Flask) é (app)
app.config['SECRET_KEY'] = "minha_chave_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'    #avisando o computador então de que ele vai usar o banco de dados SQL num arquivo chamadoo ecommerce?

login_manager = LoginManager()
db = SQLAlchemy (app) #O objeto db representa o banco de dados e conecta o SQLA ao app Flask, permitindo que o aplicativo gerencie o banco usando as configurações definidas.
login_manager.init_app(app) #Aqui você tá usando o loggin manager pra receber a aplicação init app
login_manager.login_view = 'login'
CORS(app)


#Login e Logout do usuário (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True) #Aqui eu disse que o nome de usuario tem no máximo 80 caracteres, é obrigatório o usuario ter nome e unique diz que os nomes são unicos não pode ter dois com o mesmo nome de usuario
    password = db.Column(db.String(80), nullable=True) #unique por padrão é falso
    cart = db.relationship('CartItem', backref='user', lazy=True)#cria uma relaçao para os itens dentro do carrinho do usuário

# Modelagem ou Model pra ser criado precisamos antes criar uma class, no ex abaixo Product é o Model
# Todo Produto Cadastrado aqui deve ter (id, name, price, description)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)      #Cria uma coluna inteira chamada id, que serve como identificador único da tabela (chave primária)
    name = db.Column(db.String(120), nullable=False)  #Cria uma coluna de texto chamada name, com no máximo 120 caracteres, e que é obrigatória 
    price = db.Column(db.Float, nullable=False)       #Float permite ter centavos  nullable=False significa que é obrigatório a regra apresentada atrás
    description = db.Column(db.Text, nullable=True)   #Aqui eu falei que eu posso ter produtos sem a descrição

class CartItem(db.Model): #Criei o modelo do carrinho de compras
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #ele vai criar uma chave estrangeira, uma referencia que vai ligar a class user ao carrinho
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) #ele vai criar uma chave estrangeira, uma referencia que vai ligar a class product ao carrinho




#  Autenticacao
@login_manager.user_loader
def load_use(user_id):
    return User.query.get(int(user_id)) #pesquisar pra que serve isso tudo dps

@app.route('/login', methods=["POST"]) #Metodo POST passa uma informação
def login():
    data = request.json
# data.get("username") recomendado esse jeito de recuperar o username
    user = User.query.filter_by(username=data.get("username")).first()#quando você quer filtrar o produto, ele vai retornar todo usuario com o username
    if user and data.get("password") == user.password:
           login_user(user) #apartir daqui já estamos autenticado
           return jsonify({"message": "Logged in sucessfully"})
        
    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401

@app.route('/logout', methods=["POST"])
@login_required
def logout(): #Pesquisar dps oq significa tudo isso
    logout_user()
    return jsonify({"message": "Logout sucessfully"})

@app.route('/api/products/add', methods=["POST"])    #à uma rota da API/Estamos trabalhando no modelo de products/A operação add é de adicionar eu também disse que o unico metodo aceito é o POST
@login_required  #pra usar alterar rota precisa de permição
def add_product(): #aqui eu criei a função adicionar produto
    data = request.json #variável data vai receber os dados da requisição.json
    if 'name' in data and 'price' in data: #Verificando se tem o nome e o texto antes de realizar o cadastro, se não tiver um dos dois o software não funciona
      product = Product(name=data["name"], price=data["price"],description=data.get("description", "")) #pra os valores serem a mesma coisa que no body do baseUrl no postman. Com o data[xxx] ele pega de lá o atributo mas se não achar da error / o data.get("xxx", "") ele faz a mesma coisa só que se ele não achar da pra você por no"" o que voce queria
      db.session.add(product)
      db.session.commit() #Vai mandar os comandos pro banco de dados
      return jsonify({"message": 'Product added sucessfully'})  #o retorno do código acima em json vai ser "Product added sucessfully"
    return jsonify({"message": 'Invalid product data'}), 400 #Se não tiver todos os atributos exigidos, vai aparecer essa mensagem de retorno, o 400 significa erro

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])    #à uma rota da API/Estamos trabalhando no modelo de products/A operação delete é de deletar/ Espere um número inteiro na URL e salve ele na variável product_id. methods eu também disse que o unico metodo aceito é o DELETE
@login_required
def delete_product(product_id): #isso é uma implementação
    # Recuperar o produto da base de dados
    # Verificar se o produto existe
    # Se existe, apagar da base de dados
    # Se não existe, retornar 404 not found
    product = Product.query.get(product_id) 
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": 'Product deleted successfully'})
    return jsonify({"message": 'Product not found'}), 404 #400 é erro de quando não manda com o dado esperado, e 404 quando o dado não é encontrado

#Rota pra recuperar os detalhes do produto
@app.route('/api/products/<int:product_id>', methods=['GET']) #Método Get recupera as informações
def get_product_details(product_id): #essa função recupera os detalhes do produto
    product = Product.query.get(product_id)  #esse product_id é o produto que o usuário requisitou, vem no Id do produto
    if product:
        return jsonify({
            "id": product.id, #recuperei a informação do product.id
            "name": product.name,  #recuperei a informação do product.name
            "price": product.price,   #recuperei a informação do product.price
            "description": product.description   #recuperei a informação do product.description
        })
    return jsonify({"message": 'Product not found'}), 404

#Rota pra atualização de produto
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product: #Se não existir o produto (false) ele vai negar com esse comando e torna-lo verdadeiro, diferente dos if acima que se a variavel product tem (true) ele permite
      return jsonify({"message": 'Product not found'}), 404

    data = request.json
    if 'name' in data: #Aqui verificou se tem name nos dados acima
        product.name = data['name']

    if 'price' in data: #verifiquei se o preço existe nos dados
        product.price = data['price']

    if 'description' in data: #Verifiquei se tem descrição nos dados
        product.description = data['description']
    
    db.session.commit() #sem o commit não vai funcionar as atualizações, ou delete, ou adição, qualquer coisa, vai precisar do commit
    return jsonify({'message': 'Product updated successfuly'})

#Rota pra retornar a lista de produtos
@app.route('/api/products', methods= ['GET'])
def get_products():
    products = Product.query.all() # Notasse que i product está no plurall com S no final, pois  é mais de uma lista. Esse Product.query.all tá dizendo que vai recuperar (GET) todos os produtos cadastrados como uma lista
    product_list = []
    for product in products: #for Faz um lopin, uma interação, a cada interação ele vai recuperar um produto, ai eu dei o nome que vai ser product(unico disponivel pois só tem product) e falei que ele vai ficar em products
        product_data = {
             "id": product.id, #recuperei a informação do product.id
            "name": product.name,  #recuperei a informação do product.name
            "price": product.price,   #recuperei a informação do product.price
            "description": product.description   #recuperei a informação do product.description
        }
        product_list.append(product_data)#aqui vai receber algum valor que eu por nessa lista

    return jsonify(product_list)

# Checkout
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required 
def add_to_cart(product_id):
    # Usuário
    user = User.query.get(int(current_user.id))
    #Produto
    product = Product.query.get(product_id)

    if user and product: #Tem que ter os dois se um for falso não vai funcionar
        cart_item = CartItem(user_id=user.id, product_id= product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item added to the cart sucessfully'})
    return jsonify({'message': 'Failed to add item to the cart'}), 400



#depois de fazer a requisição no postman, nota-se que product 1 e 2 estão em lista, graças a essa rota Get criada acima


# Definir uma rota raiz @app.route('/teste') (página inicial) e a função que será executada quando o usuário requisitar
@app.route('/')
def hello_world():       #def é definição a função
    return 'Hello World' 
#Quando o usuário requisitar (pedir) uma rota, o sistema vai definir (def) a rota (hello_world) ele vai retornar com a requisição ('Hello World)


@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@login_required
def remove_from_cart(product_id): #removendo o produto do carrinho
    # Produto, Usuario = Item no carrinho
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()#pede pro chat explicar essa linha dps
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from the cart sucessfully'})
    return jsonify({'message': 'Failed to romeve item from the cart'}), 400

@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    #Usuario
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

@app.route('/api/cart/checkout', methods=["POST"])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Checkout sucessfuly. Cart has been clared'})


if  __name__ == "__main__":      #Se o conteúdo da variável name for igual a main, ele será rodado com debug=True
    with app.app_context():
        db.create_all()  # Cria as tabelas
    app.run(debug=True)

 
#(debug=True) ativa o modo depuração, isso vai ajudar a ter mais visibilidade do que acontece no servidor









#Pra ver a requisição, aperte o triangulo virado pra direita no canto superior direito do Vscode depois, abra o posteman e cole o link que você vai copiar do terminal, depois coloque a rota (no caso do projeto a rota é /teste)
#O que é app.run?
#Na API se você rodou a informação em json e no postman aparecer como html, tá errado, geralmente tem que ser em json também, abaixo um exemplo de retorno em json:
#return jsonify ({"message": "Product added sucessfully"}) "Product added sucessfully" return jsonify({"message": "Invalid product data"}), 400 