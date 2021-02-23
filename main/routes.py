from flask import request, jsonify, make_response,render_template,redirect,session,request
from main.models import User,Product,Transaction,TransactionDetail,Rating,ProductSchema,UserSchema,TransactionSchema,TransactionDetailSchema,RatingSchema
from main import app
import json
from main import AI
import pandas as pd
from main import db

@app.route("/")
def home():
    return 'home'

@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.json["username"]
        password = request.json["password"]
        
        login = User.query.filter_by(username=username, password=password).first()
        if login is not None:
            user_schema = UserSchema()
            users = user_schema.dump(login)
            return make_response(jsonify({"users": users}))
    return 'halaman login'

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.json['username']
        email = request.json['email']
        address = request.json['address']
        password = request.json['password']

        register = User(username = username, email = email, password = password,address = address)
        db.session.add(register)
        db.session.commit()

        return 'berhasil register,meunju ke page login'
    return 'render register page'

@app.route('/products', methods = ['GET'])
def index():
    get_products = Product.query.all()
    product_schema = ProductSchema(many=True)
    products = product_schema.dump(get_products)
    return make_response(jsonify({"product": products}))
@app.route('/products/<productId>', methods = ['GET'])
def get_product_by_id(productId):
    get_product = Product.query.get(productId)
    product_schema = ProductSchema()
    selectedProduct = product_schema.dump(get_product)
  
    get_ratings = Rating.query.all()
    rating_schema = RatingSchema(many=True)
    ratings = rating_schema.dump(get_ratings)
  
    df = pd.DataFrame(ratings)
    df = df.pivot_table(index='productId',columns='userId',values='rating')
    df = df.fillna(0)
    
    recommend_list = list()
    recommendation_return = AI.getRecommendation(productId,df)
    if len(recommendation_return) == 5 :
        for i in range(len(recommendation_return)):
            get_recommendation_product_id = Product.query.get(int(recommendation_return[i]))
            product_schema = ProductSchema()
            product = product_schema.dump( get_recommendation_product_id)
            if(product['productQuantity'] > 0 ):
                recommend_list.append(product)

        get_product_same_category = Product.query.filter_by(productCategory = get_product.productCategory).order_by(Product.productRating.desc())
        produk_schema = ProductSchema(many=True)
        get_product_rating = produk_schema.dump(get_product_same_category)
        i=0
        while(len(recommend_list) < 5):
            if get_product_rating[i]['productId'] == int(productId) :
                i+=1
            if(get_product_rating[i]['productQuantity'] > 0 ):
                flagDouble = False
                for j in range(len(recommend_list)):
                    if get_product_rating[i]['productId'] == recommend_list[j]['productId']:
                        flagDouble = True
                        break
                if flagDouble==False:
                    recommend_list.append(get_product_rating[i])
            i+=1
    else:
        get_product_same_category = Product.query.filter_by(productCategory = get_product.productCategory).order_by(Product.productRating.desc())
        produk_schema = ProductSchema(many=True)
        get_product_rating = produk_schema.dump(get_product_same_category)
        i = 0 
        while len(recommend_list) < 5:
            if get_product_rating[i]['productId'] == int(productId) :
                i+=1
            if(get_product_rating[i]['productQuantity'] > 0 ):
                recommend_list.append(get_product_rating[i])
            i+=1

    return make_response(jsonify({"product": selectedProduct,"recommendation":recommend_list}))
@app.route('/products/category/<productCategory>', methods = ['GET'])
def get_product_by_category(productCategory):
    get_product = Product.query.filter_by(productCategory=productCategory)
    product_schema = ProductSchema(many=True)
    product = product_schema.dump(get_product)
    return make_response(jsonify({"product": product}))

@app.route('/products/rating/<productRating>', methods = ['GET'])
def get_product_by_rating(productRating):
    get_product = Product.query.filter_by(productRating=productRating)
    product_schema = ProductSchema(many=True)
    product = product_schema.dump(get_product)
    return make_response(jsonify({"product": product}))

@app.route('/products/<productId>', methods = ['PUT'])
def update_product_by_id(productId):
    data = request.get_json()
    get_product = Product.query.get(productId)
    if data.get('productTitle'):
        get_product.productTitle = data['productTitle']
    if data.get('productCategory'):
        get_product.productCategory = data['productCategory']
    if data.get('productImg'):
        get_product.productImg = data['productImg']
    if data.get('productDesc'):
        get_product.productDesc = data['productDesc']
    if data.get('productPrice'):
        get_product.productPrice= data['productPrice']
    if data.get('productRating'):
        get_product.productRating= data['productRating']
    if data.get('productQuantity'):
        get_product.productQuantity= data['productQuantity']    
    db.session.add(get_product)
    db.session.commit()
    product_schema = ProductSchema(only=['productId', 'productTitle', 'productCategory','productImg','productDesc','productPrice','productRating','productQuantity'])
    product = product_schema.dump(get_product)
    return make_response(jsonify({"product": product}))

@app.route('/products/<productId>', methods = ['DELETE'])
def delete_product_by_id(productId):
    get_product = Product.query.get(productId)
    db.session.delete(get_product)
    db.session.commit()
    return make_response("",204)

@app.route('/products', methods = ['POST'])
def create_product():
    data = request.get_json()
    product_schema = ProductSchema()
    product = product_schema.load(data)
    result = product_schema.dump(product.create())
    return make_response(jsonify({"product": result}),200)

@app.route('/transactions', methods = ['GET'])
def transaction():
    get_transactions = Transaction.query.all()
    transaction_schema = TransactionSchema(many=True)
    transactions = transaction_schema.dump(get_transactions)
    return make_response(jsonify({"transaction": transactions}))

@app.route('/transactions/<transactionId>', methods = ['GET'])
def get_transaction_by_id(transactionId):
    get_transaction = Transaction.query.get(transactionId)
    transaction_schema = TransactionSchema()
    transaction = transaction_schema.dump(get_transaction)
    return make_response(jsonify({"transaction": transaction}))
# BUAT UPDATE STATUS
@app.route('/transactions/<transactionId>', methods = ['PUT'])
def process_transaction_by_id(transactionId):
    get_transaction = Transaction.query.get(transactionId)
    if get_transaction.status == 'waiting':
        get_transaction.status ='delivering'
    else:
        get_transaction.status = 'delivered'
    db.session.add(get_transaction)
    db.session.commit()
    transaction_schema = TransactionSchema(only=['transactionId', 'status'])
    transaction = transaction_schema.dump(get_transaction)
    return transaction

@app.route('/transactions/<transactionId>', methods = ['DELETE'])
def delete_transaction_by_id(transactionId):
    transactionDetail_schema= TransactionDetailSchema(many=True)
    get_transactionDetail = TransactionDetail.query.filter_by(transactionId = transactionId)
    transactionDetails = transactionDetail_schema.dump(get_transactionDetail)
    for details in transactionDetails:
        transactionDetailToBeDelete = TransactionDetail.query.get(details['transactionDetailId'])
        db.session.delete(transactionDetailToBeDelete)
        print(details['transactionDetailId'])
    get_transaction = Transaction.query.get(transactionId)
    db.session.delete(get_transaction)
    db.session.commit()
    return make_response("",204)

@app.route('/transactions', methods = ['POST'])
def create_transaction():
    data = request.get_json()
    userId = data['userId']
    listProductId = data['listId']
    listQuantity = data['listQty']
    listPrice = data['listPrice']
    grandTotal = 0 
    for i in range(len(listPrice)):
        grandTotal+= (listQuantity[i]['qty'] * listPrice[i]['price'])
    transaction_dict = {
        'userId' : userId,
        'total':grandTotal,
        'status':'waiting'
    }
    transaction_schema = TransactionSchema()
    transaction = transaction_schema.load(transaction_dict)
    result = transaction_schema.dump(transaction.create())
    for i in range(len(listProductId)):
        transactionDetail_dict = {
        'transactionId' : int(result['transactionId']),
        'productId':listProductId[i]['productId'],
        'productQuantity':listQuantity[i]['qty']
        }
        get_product = Product.query.get(listProductId[i]['productId'])
        get_product.productQuantity = get_product.productQuantity - listQuantity[i]['qty']
        product_schema = ProductSchema()
        selectedProduct = product_schema.dump(get_product)
        db.session.add(get_product)
        db.session.commit()
        print(transactionDetail_dict)
        transactionDetail_schema = TransactionDetailSchema()
        transactionDetail = transactionDetail_schema.load(transactionDetail_dict)
        transactionDetailResult = transactionDetail_schema.dump(transactionDetail.create())

    return make_response(jsonify({"transaction": result}),200)

@app.route('/transactions-history', methods = ['POST'])
def transactionHistory():
    data = request.get_json()
    get_transaction = Transaction.query.filter_by(userId = data['userId'])
    transaction_schema = TransactionSchema(many=True)
    transactions = transaction_schema.dump(get_transaction)

    transactionhistory_dict = dict()
    trans_dict = list()
    transactionsDetail_Schema = TransactionDetailSchema(many=True)
    for i in range(len(transactions)):
        temp_dict = dict()
        temp_dict['transactionId'] = transactions[i]['transactionId']
        temp_dict['total'] = transactions[i]['total']
        temp_dict['status'] = transactions[i]['status']
        transactionDetailHistory = list()
        for x in  range(len(transactions[i]['transactionDetail'])):
            get_transactionDetail = TransactionDetail.query.filter_by(transactionDetailId = transactions[i]['transactionDetail'][x])
            transaction_detail = transactionsDetail_Schema.dump(get_transactionDetail)
            get_product = Product.query.get(transaction_detail[0]['productId'])
            get_rating = Rating.query.filter_by(productId = transaction_detail[0]['productId'],userId = data['userId']).first()
            rating_schema = RatingSchema()
            rating = rating_schema.dump(get_rating) 
            product_schema = ProductSchema()
            product = product_schema.dump(get_product)
            
            
            merge = dict()
            merge['transactionDetail'] = transaction_detail
            merge['productDetail'] = product
            merge['ratingDetail'] = rating
            

            transactionDetailHistory.append(merge)
        temp_dict['items'] = transactionDetailHistory
        trans_dict.append(temp_dict)
        
    transactionhistory_dict['history'] = trans_dict
    
    return  make_response(jsonify({"transaction_history": transactionhistory_dict}),200)

@app.route('/transactions-history', methods = ['GET'])
def transactionHistoryAdmin():
    get_transaction = Transaction.query.all()
    transaction_schema = TransactionSchema(many=True)
    transactions = transaction_schema.dump(get_transaction)
    transactionhistory_dict = dict()
    trans_dict = list()
    transactionsDetail_Schema = TransactionDetailSchema(many=True)
    for i in range(len(transactions)):
        temp_dict = dict()
        temp_dict['transactionId'] = transactions[i]['transactionId']
        temp_dict['total'] = transactions[i]['total']
        temp_dict['status']=transactions[i]['status']
        temp_dict['userId']=transactions[i]['userId']
        transactionDetailHistory = list()
        for x in  range(len(transactions[i]['transactionDetail'])):
            get_transactionDetail = TransactionDetail.query.filter_by(transactionDetailId = transactions[i]['transactionDetail'][x])
            transaction_detail = transactionsDetail_Schema.dump(get_transactionDetail)
            get_product = Product.query.get(transaction_detail[0]['productId'])
            product_schema = ProductSchema()
            product = product_schema.dump(get_product)
              
            merge = dict()
            merge['transactionDetail'] = transaction_detail
            merge['productDetail'] = product
            
            transactionDetailHistory.append(merge)
        temp_dict['items'] = transactionDetailHistory
        trans_dict.append(temp_dict)
        
    transactionhistory_dict['history'] = trans_dict
    
    return  make_response(jsonify({"transaction_history": transactionhistory_dict}),200)

@app.route('/ratings', methods = ['POST'])
def create_ratings():
    data = request.get_json()

    get_rating = Rating.query.filter_by(productId = data['productId'],userId = data['userId']).first()
    rating_schema = RatingSchema()
    rating = rating_schema.dump(get_rating)

    if not rating:
        new_rating = Rating(data['productId'], data['userId'], data['rating'])
        db.session.add(new_rating)
            
        getAll_ratings = Rating.query.filter_by(productId = data['productId']).all()
        ratings_schema = RatingSchema(many=True)
        product_ratings = ratings_schema.dump(getAll_ratings)
        
        tot = 0
        for i in range(len(product_ratings)):
            tot += product_ratings[i]['rating']
        
        
        get_product = Product.query.filter_by(productId = data['productId']).first()
        get_product.productRating = float(tot / len(product_ratings))
        
        db.session.commit()
    else:
        get_rating.rating = data['rating']
        
        getAll_ratings = Rating.query.filter_by(productId = data['productId']).all()
        ratings_schema = RatingSchema(many=True)
        product_ratings = ratings_schema.dump(getAll_ratings)
  
        tot = 0
        for i in range(len(product_ratings)):
            tot += product_ratings[i]['rating']
          
        get_product = Product.query.filter_by(productId = data['productId']).first()
        print(get_product.productRating)
        get_product.productRating = float(tot / len(product_ratings))
        print(get_product.productRating)
        db.session.commit()

        
    return "pass"