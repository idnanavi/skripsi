from main import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    password = db.Column(db.String(80))
    transactions = db.relationship('Transaction', backref='users', lazy=True)

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self

    def __init__(self,username,email,address,password):
        self.username = username
        self.email = email
        self.address = address
        self.password = password
        
       
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.address}','{self.password}')"

class Product(db.Model):
    __tablename__ = "products"
    productId = db.Column(db.Integer, primary_key=True)
    productTitle = db.Column(db.String(255))
    productCategory = db.Column(db.String(255))
    productImg = db.Column(db.String(255))
    productDesc = db.Column(db.String(255))
    productPrice = db.Column(db.Float)
    productRating = db.Column(db.Float)
    productQuantity = db.Column(db.Integer)
    transactionDetail = db.relationship('TransactionDetail', backref='products', lazy=True)

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,productTitle,productCategory,productImg,productDesc,productPrice,productRating,productQuantity):
        self.productTitle = productTitle
        self.productCategory = productCategory
        self.productImg = productImg
        self.productDesc = productDesc
        self.productPrice = productPrice
        self.productRating = productRating
        self.productQuantity = productQuantity
       

    def __repr__(self):
        return f"Product('{self.productTitle}','{self.productCategory}','{self.productImg}','{self.productDesc}','{self.productPrice}','{self.productRating}','{self.productQuantity}')"

class Transaction(db.Model):
    __tablename__ = "transactions"
    transactionId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    total = db.Column(db.Float)
    status=db.Column(db.String(225))
    transactionDetail = db.relationship('TransactionDetail', backref='transactions', lazy=True)

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,userId,total,status):
        self.userId = userId
        self.total = total
        self.status= status

    def __repr__(self):
        return f"Transaction('{self.userId}','{self.total}','{self.status}')"

class TransactionDetail(db.Model):
    __tablename__ = "transaction_detail"
    transactionDetailId = db.Column(db.Integer, primary_key=True)
    transactionId = db.Column(db.Integer,db.ForeignKey('transactions.transactionId'),nullable=False)
    productId = db.Column(db.Integer,db.ForeignKey('products.productId'),nullable=False)
    productQuantity = db.Column(db.Integer)

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,transactionId,productId,productQuantity):
        self.transactionId = transactionId
        self.productId = productId
        self.productQuantity = productQuantity

    def __repr__(self):
        return f"TransactionDetail('{self.transactionId}','{self.productId}','{self.productQuantity}')"

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer)
    userId = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,productId,userId,rating):
        self.productId = productId
        self.userId = userId
        self.rating = rating

    def __repr__(self):
        return f"Rating('{self.productId}','{self.userId}','{self.rating}')"

class ProductSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Product
        sqla_session = db.session
    productId = fields.Integer(dump_only=True)
    productTitle = fields.String(required=True)
    productCategory = fields.String(required=True)
    productImg = fields.String(required=True)
    productDesc = fields.String(required=True)
    productPrice = fields.Float(required=True)
    productRating = fields.Float(required=True)
    productQuantity = fields.Integer(required=True)

class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User
        sqla_session = db.session
    Id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    email = fields.String(required=True)
    address = fields.String(required=True)
    password = fields.String(required=True)

class TransactionSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Transaction
        sqla_session = db.session
    transactionId = fields.Integer(dump_only=True)
    status = fields.String(required=True)
    userId = fields.Number(required=True)
    total = fields.Float(required=True)

class TransactionDetailSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = TransactionDetail
        sqla_session = db.session
    transactionDetailId = fields.Integer(dump_only=True)
    transactionId = fields.Integer(required=True)
    productId = fields.Integer(required=True)
    productQuantity = fields.Integer(required=True)

class RatingSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Rating
        sqla_session = db.session
    id = fields.Integer(dump_only=True)
    productId = fields.Integer(required=True)
    userId = fields.Integer(required=True)
    rating = fields.Integer(required=True)

db.create_all()