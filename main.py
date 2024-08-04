from flask import Flask, request, jsonify, render_template, url_for, redirect
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import razorpay

app = Flask(__name__)

try:
    uri = "mongodb+srv://Sneakycks:sneakycks@cluster0.8eefhmf.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.get_database('Sneakycks')
    print('Connected')
except Exception as e:
    print(e)

razorpay_key_id = "rzp_test_vhgAEO30FLnHFv"
razorpay_key_secret = "tS1LiFcRctTIHnUrsWafj1vm"
razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

browsed_items = {} # stores art items against their ids (artnames for now)
cart_items = {} # stores ites added to the cart

@app.template_filter('zip')
def _zip(a,b):
    return zip(a,b)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginn')
def loginn():
    return render_template('login.html')



@app.route('/cartt',methods=['GET','POST'])
def cartt():
    parameter_value = int(request.args.get('price'))
    return render_template('cart.html',price = parameter_value+5)
    # if request.method == 'POST':
    #     price = request.form['itemprice']
    #     return render_template('cart.html',price=price)

@app.route('/paymentt',methods=['POST'] )
def paymentt():
    if request.method == 'POST':
        amount = request.form['finalamount']
        return render_template('firstpay.html', amt=amount)

@app.route('/signup',methods=['POST','GET'])
def signup():
    login_collection = db.get_collection('login')
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            contactno = request.form['contactno']
            password = request.form['password']
            document = {
                "name": name,
                "email": email,
                "contactno": contactno,
                "password": password
            }
            login_collection.insert_one(document)
            print('Success')
            return redirect(url_for('loginn'))
        except Exception as e:
            print(e)
            print('error')
            return render_template('index.html')
        
@app.route('/login',methods=['POST','GET'])
def login():
    login_collection = db.get_collection('login')
    if request.method == 'POST':
        try:
            print("login")
            email = request.form['email']
            password = request.form['password']
            rs = login_collection.find_one({'email': email})
            if rs:
                if rs['password'] == password:
                    return render_template('home.html')
                else:
                    print('password or username incorrect')
                    return render_template('index.html')
            else:
                print('user not found')
                return render_template('index.html')
        except Exception as e:
            print(e)
            print('error login')
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/charge', methods=['POST'])
def charge():
    if request.method == 'POST':
        amount = request.form['amount']
        #amount = int(request.form['amount']) * 100  # Razorpay accepts amount in paise
        amount_float = float(amount)
        amount_int = int(amount_float) * 100
        currency = 'INR' 
        order_data = {
        'amount': amount_int,
        'currency': currency
        }
        # Create a Razorpay Order
        order = razorpay_client.order.create(data=order_data)
        return render_template('payment.html', order=order)
    

# Call this to add an item to the cart dictionary
# Later when you open up cart page, use this dictionary (cart_items) along with browsed_items to populate the page
@app.route('/cartadd',methods=['POST'])
def AddToCart(id):
    if id in cart_items.keys():
        cart_items[id] += 1
    else:
        cart_items[id] = 1
    
    

if __name__ == '__main__':
    app.run()

