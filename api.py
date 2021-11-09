from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
# from wtforms.fields.html5 import DateField
from wtforms import SubmitField, HiddenField, StringField,  FloatField, BooleanField, DateField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange

from datetime import datetime
from random import randint

# import requests
# from requests.exceptions import HTTPError

app = Flask(__name__)

# Flask-WTF enryption key 
app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'

# Flask-Bootstrap requires this line
Bootstrap(app)

# +++++++++++++++++++++++++++
# Business logic
# +++++++++++++++++++++++++++

def calculate_insurance(item_value, recipient_country): 
    #1. If package is being sent to the UK, insurance charge is 1% of the item
    if recipient_country == 'United Kingdom':
        insurance_charge = (item_value / 100) * 1  
    #2. If package is being sent to France, Germany, Netherlands or Belgium, insurance charge is 1.5% value of item
    elif recipient_country == 'France' or recipient_country == 'Germany' or recipient_country == 'Netherlands' or recipient_country == 'Belgium':
        insurance_charge = (item_value / 100) * 1.5  
    #3. If package is being sent anywhere else, insurance charge is 4% of the value of the item
    else: 
        insurance_charge = (item_value / 100) * 4  
    #4. If insurance charge is less than £9, insurance charge - £9 
    if insurance_charge < 9.00:
        insurance_charge = 9
    #5. Insurance premium tax calculate & round to two decimal places 
    insurance_premium_tax = (insurance_charge / 100) * 12.5
    final_insurance_charge = insurance_charge + insurance_premium_tax
    #6. Insurance charge is rounded to the nearest 0.01
    return round(final_insurance_charge,2)
   
def generate_tracking_reference(n): 
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

# Attempts at manual validation - ran out of time

# def validate_value(package_value, insurance, form):
#     print('entered validate_value')
#     if (float(package_value)) > 10000 and insurance == 'y':
#         flash("Error: We cannot insure packages worth more than £10,000".format(
#                 getattr(form1, field).label.text,
#                 error
#             ), 'error')
#         return render_template('order.html', form1=form1) 
#     else:
#         pass

# def validate_uniqueness(new_tracking_reference, form):
#     try:
#         print('entered validate_uniqueness')
#         order = Order.query.filter_by(tracking_reference=new_tracking_reference).first_or_404()
#         flash("Error: This order has already been submitted. Please search for your tracking reference.".format(
#                 getattr(form1, field).label.text,
#                 error
#             ), 'error')
#         print('tracking number has been used ')
#         return render_template('order.html', form1=form1) 
#     except HTTPError:
#         print('Tracking number has not been used yet')
#         pass

# def validate_allowed_despatch_date(despatch_date, form): 
#     print('entered validate_despatch_date')
#     today = datetime.datetime.now().date()
#     tomorrow = datetime.date.today() + datetime.timedelta(days=1)
#     if despatch_date != today or tomorrow:
#         flash("Error: This order has already been submitted. Please search for your tracking reference.".format(
#             getattr(form1, field).label.text,
#             error
#         ), 'error')
#         return render_template('order.html', form1=form1) 
#     else: 
#         pass




# ++++++++++++++++++++++
# Create DB and DB model
# ++++++++++++++++++++++

# the name of the database; add path if necessary
db_name = 'orders.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String)
    sender_address = db.Column(db.String)
    sender_city = db.Column(db.String)
    sender_country = db.Column(db.String)

    recipient_name = db.Column(db.String)
    recipient_address = db.Column(db.String)
    recipient_city = db.Column(db.String)
    recipient_country = db.Column(db.String)

    package_value = db.Column(db.Float)
    contents_declaration = db.Column(db.String)
    despatch_date = db.Column(db.String)
    insurance_charge = db.Column(db.Float)
    tracking_reference = db.Column(db.String)
    updated = db.Column(db.String)

    def __init__(self, 
                 sender_name, sender_address, sender_city, sender_country, 
                 recipient_name, recipient_address, recipient_city, recipient_country,
                 package_value, contents_declaration, despatch_date, insurance_charge,
                 tracking_reference, updated
                ):

        self.sender_name = sender_name
        self.sender_address = sender_address
        self.sender_city = sender_city
        self.sender_country = sender_country

        self.recipient_name = recipient_name
        self.recipient_address = recipient_address
        self.recipient_city = recipient_city
        self.recipient_country = recipient_country

        self.package_value = package_value
        self.contents_declaration = contents_declaration
        self.despatch_date = despatch_date
        self.insurance_charge = insurance_charge
        self.tracking_reference = tracking_reference
        self.updated = updated

# ++++++++++++++++++++
# Create Flask-WTF Form
# ++++++++++++++++++++

# form for add_record and edit_or_delete
# each field includes validation requirements and messages
class AddRecord(FlaskForm):
    # id used only by update/edit
    id_field = HiddenField()

    #  Sender information
    sender_name = StringField('Sender Name', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Sender Name"),
        Length(min=3, max=25, message="Invalid Sender name length")
        ])
    sender_address = StringField('Sender Address', [ InputRequired(),
        # Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Sender Address"),
        Length(min=3, max=250, message="Invalid Sender Address length")
        ])
    sender_city = StringField('Sender City', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Sender City"),
        Length(min=3, max=25, message="Invalid Sender City length")
        ])
    sender_country = StringField('Sender Country', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Sender Country"),
        Length(min=3, max=25, message="Invalid Sender Country length")
        ])

    #  Recipient Information 
    recipient_name = StringField('Recipient Name', [ InputRequired(),
        # Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Recipient Name"),
        Length(min=3, max=25, message="Invalid Recipient name length")
        ])
    recipient_address = StringField('Recipient Address', [ InputRequired(),
        # Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Recipient Address"),
        Length(min=3, max=250, message="Invalid Recipient Address length")
        ])
    recipient_city = StringField('Recipient City', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Recipient City"),
        Length(min=3, max=25, message="Invalid Recipient City length")
        ])
    recipient_country = StringField('Recipient Country', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Recipient Country"),
        Length(min=3, max=25, message="Invalid Recipient Country length")
        ])

    #  Other Information
    package_value = FloatField('Package Value', [ InputRequired(),
        NumberRange(min=1.00, max=1000000, message="Invalid range")
        ]) #  If value > 10,000 && insurance = true then.... Error 
    contents_declaration = StringField('Contents Declaration', [ InputRequired(),
        Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Contents Declaration"),
        Length(min=3, max=250, message="Invalid Contents Declaration length")
        ])
    despatch_date = DateField('Despatch Date') #  If date != today or tomorrow && insurance = true then... Error
    insurance = BooleanField('I would like insurance') 
    tracking_reference = HiddenField() 
    updated = HiddenField()  # updated = date - handled in the route function
    submit = SubmitField('Submit Order')

class SearchRecord(FlaskForm):
    #  Order reference number
    tracking_reference = StringField('Tracking Reference', [ InputRequired(),
        # Regexp(r'^[A-Za-z\s\-\']+$', message="Invalid Sender Name"), #Should change regex so it only accepts numbers
        Length(min=3, max=25, message="Invalid Tracking Reference")
        ])
    submit = SubmitField('Search')

# +++++++++++++
# Create Routes
# +++++++++++++

#  View home page
@app.route("/")
def index():
    return render_template('index.html')

#  Add a new order to the database
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    form1 = AddRecord()
    if form1.validate_on_submit(): #IF form is valid
        #1. Define fields - below are fields for use without JSON
        #Sender
        sender_name = request.form['sender_name']
        sender_address = request.form['sender_address']
        sender_city = request.form['sender_city']
        sender_country = request.form['sender_country']
        #Recipiant
        recipiant_name = request.form['recipient_name']
        recipiant_address = request.form['recipient_address']
        recipiant_city = request.form['recipient_city']
        recipiant_country = request.form['recipient_country']
        #Other
        package_value = request.form['package_value']
        contents_declaration = request.form['contents_declaration']
        despatch_date = request.form['despatch_date']
        # tracking_reference = request.form['tracking_reference']
        insurance = request.form['insurance']
        updated = datetime.now() # get today's date and time  
        tracking_reference = generate_tracking_reference(8) 

        # #Fields for JSON - I did not have enough time to implement JSON for request and response
        #I imagine that I would have had to deserialize and then validate the JSON
        # json_data = request.json
        # #Sender
        # sender_name = json_data['sender_name']
        # sender_address = json_data['sender_address']
        # sender_city = json_data['sender_city']
        # sender_country = json_data['sender_country']
        # #Recipiant
        # recipiant_name = json_data['recipient_name']
        # recipiant_address = json_data['recipient_address']
        # recipiant_city = json_data['recipient_city']
        # recipiant_country = json_data['recipient_country']
        # #Other
        # package_value = json_data['package_value']
        # contents_declaration = json_data['contents_declaration']
        # despatch_date = json_data['despatch_date']
        # tracking_reference = json_data['tracking_reference']
        # insurance = json_data['insurance']
        # updated = datetime.now() # get today's date and time 

        # req = request.get_json() 
      
        #2. Validate (using the validators which I created above - not working yet)
        # validate_value(package_value, insurance, form1)
        # validate_uniqueness(tracking_reference, form1)
        # validate_allowed_despatch_date(despatch_date, form1)



        #2. Run functions to calculate - should move the below if statement into the insurance calculate function so that it is better encapsulated
        if insurance == 'y':
            insurance_charge = calculate_insurance(float(package_value), recipiant_country)
            print('CHARGEEEE',insurance_charge)
        else: 
            print('insuranceeeeeeee',insurance)
            insurance_charge = 0 #  Or 0 
            print('Insurance Charge: 0')

        #3. save to DB 

        # The data to be inserted into Order model
        record = Order(sender_name, sender_address, sender_city, sender_country, 
                       recipiant_name, recipiant_address, recipiant_city, recipiant_country,
                       package_value, contents_declaration, despatch_date, insurance_charge, 
                       tracking_reference, updated 
                      ) #Insurance_charge
                
        # Flask-SQLAlchemy adds record to database
        db.session.add(record)
        db.session.commit()

        # create a message to send to the template
        message = f"The data for your order to {recipiant_address} has been submitted. The Insurance charge for this order will be {insurance_charge}. The tracking reference for this order is {tracking_reference}"
        return render_template('order.html', message=message)
    else: #  If form is not valid
        # Show validaton errors
        # see https://pythonprogramming.net/flash-flask-tutorial/
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('order.html', form1=form1)

#Search for orders
@app.route("/search", methods=["GET", "POST"])
def search():
    form1 = SearchRecord()
    if request.method == "POST":
        tracking_reference = request.form['tracking_reference']
        print(tracking_reference) #Order 15 = 47433635 
        order = Order.query.filter_by(tracking_reference=tracking_reference).first_or_404()
        return render_template('order_details.html', tracking_reference=tracking_reference, order=order)
    else:
        return render_template('search_order.html', form1=form1)

# +++++++++++++++++++++++

if __name__ == '__main__':
    app.run(debug=True)