from my_website import app,bcrypt,db
from flask import redirect,url_for,render_template,flash,request
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
from data_base import Authority
from flask_wtf import FlaskForm
from wtforms import EmailField,PasswordField,SubmitField,SelectField
from wtforms.validators import InputRequired, Length,Email


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




class Login_form(FlaskForm):
    user_id     = EmailField(validators=[InputRequired(),Length(min=9,max=30),Email()], render_kw={"placeholder":"User_email"})
    password    = PasswordField(validators=[InputRequired(),Length(min=8,max=20)], render_kw={"placeholder":"Password"})
    submit      = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return Authority.query.get(user_id)
    
@app.route('/login',methods = ['GET','POST'])
def login():
    form = Login_form()
    if form.validate_on_submit():
        with app.app_context():
            user = Authority.query.filter_by(user_id = form.user_id.data).first()
        if user:
            if bcrypt.check_password_hash(user.password.encode('utf-8'),form.password.data):
                login_user(user)
                return redirect(url_for('option',clicked_on = 'home'))
    return render_template('Admin/login.html',form = form)

@app.route('/dashboard',methods = ['GET','POST'])
@login_required
def dashboard():
    return redirect(url_for('option',clicked_on = 'home'))

@app.route('/logout',methods = ['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_required
def check_id(id):
    user = None
    with app.app_context():
        user = Authority.query.filter_by(user_id=id).first()
    if user:
        return False
    else:
        return True

@login_required
def pie_loader(district):
    mini_window = 'pie_loader'
    from data_base import Order_details,Review,Seller_partner,Delivery_partner
    import json
    from pandas import read_csv
    df = read_csv('pincode.csv')
    all_pins = df[df['District']==district.upper()]['Pincode'].to_list()
    from data_base import app,db,Order_details,Review
    with app.app_context():
        order_query = db.session.query(Order_details.order_id,Order_details.delivery_id).filter(Order_details.address_pin.in_(all_pins),
        Order_details.delivery_status == 'Delivered' ).all()
    order_data = {} 
    for row in order_query:
        order_data[row[0]] = row[1]
    with app.app_context():
        review_query = db.session.query(Review.deliver_review,Review.seller_review,Review.order_id).filter(Review.order_id.in_(order_data.keys())).all()
    delivery_chart = {}
    seller_chart = {}
    scale = {5:'EXELENT',4:'VERY GOOD',3:'GOOD',2:'NOT GOOD',1:'BAD'}
    for review in review_query:
        delivery_id = order_data[review.order_id]
        if delivery_chart.get(delivery_id) == None:
            delivery_chart[delivery_id] = {'EXELENT':0,'VERY GOOD':0,'GOOD':0,'NOT GOOD':0,'BAD':0}
        delivery_rating = review.deliver_review
        delivery_chart[delivery_id][scale[delivery_rating]] +=1

        sellers = json.loads(review.seller_review)
        for seller_review in sellers:
            try:
                seller_id = int(list(seller_review.keys())[0])
                if seller_chart.get(seller_id) == None:
                    seller_chart[seller_id]= {'EXELENT':0,'VERY GOOD':0,'GOOD':0,'NOT GOOD':0,'BAD':0}
                seller_rating = int(list(seller_review.values())[0])
                seller_chart[seller_id][scale[seller_rating]] +=1
            except Exception as e:
                app.logger.error("Cant handel seller id in admin views.")

    # print(delivery_chart,seller_chart)
    with app.app_context():
        seller_query = db.session.query(Seller_partner.seller_id,Seller_partner.seller_name).filter(Seller_partner.seller_id.in_(seller_chart.keys())).all()
        delivery_query = db.session.query(Delivery_partner.d_partner_id,Delivery_partner.d_partner_name).filter(Delivery_partner.d_partner_id.in_(delivery_chart.keys())).all()
    seller_details = {}
    for row in seller_query:
        seller_details[row.seller_id] = row.seller_name
    delivery_details = {}
    for row in delivery_query:
        delivery_details[row.d_partner_id] = row.d_partner_name
    # print(seller_details,delivery_details)

    #scaling review on scale of 100
    for key in delivery_chart:
        no_of_review = 0
        for child_key in delivery_chart[key]:
            no_of_review += delivery_chart[key][child_key]
        prev_value = 0 #keep track of previous occupied degree  in pie chart
        for child_key in delivery_chart[key]:
            #coverting to 360
            delivery_chart[key][child_key] = (delivery_chart[key][child_key]/no_of_review)*360 + prev_value
            prev_value = delivery_chart[key][child_key]
    for key in seller_chart:
        no_of_review = 0
        for child_key in seller_chart[key]:
            no_of_review += seller_chart[key][child_key]
        prev_value = 0
        for child_key in seller_chart[key]:
            seller_chart[key][child_key] = (seller_chart[key][child_key]/no_of_review)*360 + prev_value
            prev_value = seller_chart[key][child_key]
    print(seller_chart,delivery_chart,district)
    return {'d_chart':delivery_chart,'s_chart':seller_chart,'d_details':delivery_details,
            's_details':seller_details,'location' : district.capitalize()}
@app.route('/register',methods = ['POST'])
@login_required
def register_form():
    form = request.form
    data = {'user_email':None,'password':None,'role':None}
    for names in form:
        data[names] = form[names]
    if len(data['password']) < 8:
        flash("Please enter password of more then eight length.")
        return redirect(url_for('option',clicked_on='user'))
    if check_id(data['user_email']):    
            hashed_password = bcrypt.generate_password_hash(data['password'])
            new_user = Authority(user_id = data['user_email'],
                             password = hashed_password.decode('utf-8'),
                             role = data['role'])
            try:
                with app.app_context():
                    db.session.add(new_user)
                    db.session.commit()
                flash(f"User {data['user_email']} Added Successfully")
            except Exception as e:
                app.logger.error(f"Error while inserting user in Authority.-> {e}")
    else:
        flash(f"User with {data['user_email']} already Exist.")  
    return redirect(url_for('option',clicked_on='user'))

@app.route("/update",methods = ["POST"])
@login_required
def update_form():
    form = request.form
    data = {'user_email':None,'password':None,'role':None}
    for names in form:
        data[names] = form[names]
    if len(data['password']) < 8:
        flash("Please enter password of more then eight length.")
        return redirect(url_for('option',clicked_on='user'))
    try:
        hashed_password = bcrypt.generate_password_hash(data['password'])
        with app.app_context():
            user = Authority.query.filter_by(user_id = data['user_email']).first()
            if user is None:
                flash(f"User {data['user_email']} not found")
            else:
                user.role = data['role']
                user.password = hashed_password.decode('utf-8')
                db.session.commit()
                flash(f"User {data['user_email']} Updated sucessfully")
    except Exception as e:
        app.logger.error(f"Error while inserting user in Authority.-> {e}")
        flash(f"User with {data['user_email']} already Exist.")  
    return redirect(url_for('option',clicked_on='user'))

    
@app.route("/delete",methods = ["POST"])
@login_required
def delete_form():
    form = request.form
    data = {'user_email':None}
    for names in form:
        data[names] = form[names]
    if check_id(data['user_email']):
        flash(f"User with {data['user_email']} do not Exist.")  
    else:
        try:
            with app.app_context():
                user = Authority.query.filter_by(user_id = data['user_email']).delete()
                if user == 0:
                    flash(f"User {data['user_email']} not found")
                else:
                    db.session.commit()
                    flash(f"User {data['user_email']} Deleted Sucessfully.")
        except:
            flash(f"Facing error while Deleting {data['user_email']} User.")
            app.logger.error("Error while Deleting user data.")
    return redirect(url_for('option',clicked_on='user'))


@login_required
def get_all_delivery_partner():
    from data_base import Delivery_partner
    with app.app_context():
        entries = Delivery_partner.query.all()
    return entries
@login_required
def get_all_selling_partner():
    from data_base import Seller_partner
    with app.app_context():
        entries = Seller_partner.query.all()
    return entries

@app.route('/user/<partner_type>',methods =['POST'])
@login_required
def add_new_partner(partner_type):
    form = request.form
    data = {'id':None,'name':None}
    for names in form:
        data[names] = form[names]

    if partner_type.lower() == 'delivery':
        from data_base import Delivery_partner
        entry = Delivery_partner(d_partner_id=data['id'],d_partner_name = data['name'])
    elif partner_type.lower() == 'seller':
        from data_base import Seller_partner
        entry = Seller_partner(seller_id=data['id'],seller_name=data['name'])
    try:
        with app.app_context():
            db.session.add(entry)
            db.session.commit()
        flash(f"New Entry Added in {partner_type.upper()} with Id : {data['id']} and Name : {data['name']}.")
    except Exception as e:
        flash(f"Unable to add this user in {partner_type.upper()} with Id : {data['id']} and Name : {data['name']}.")
        app.logger.error(f"Unable to add entry in {partner_type.upper()} table, {e} occurs.")
    return redirect(url_for('option',clicked_on=partner_type))


@app.route("/<clicked_on>",methods = ["GET","POST"])
@login_required
def option(clicked_on):
    allowed = ('user','delivery','seller','home','pie_loader')
    mini_window = ""
    print(clicked_on)
    if clicked_on in allowed:
        #homepage code
        from pandas import read_csv
        df = read_csv('pincode.csv')
        all_district = df['District'].unique()
        from data_base import Review
        with app.app_context():
            neg_comment = Review.query.filter_by(comment_type=-1).count()
            pos_comment = Review.query.filter_by(comment_type=1).count()
            neutral_comment = Review.query.filter_by(comment_type=0).count()
        total_comment = neg_comment+pos_comment+neutral_comment
        if total_comment == 0:
            total_comment = 1
        all_comment = {'postive':(pos_comment/total_comment)*100,
                    'negative':(neg_comment/total_comment)*100,
                    'neutral':(neutral_comment/total_comment)*100}
        #till hear
        mini_window = clicked_on
        if clicked_on == 'user':
            return render_template('Admin/homepage.html',user_email =current_user.user_id,user_role = current_user.role,
                           mini_window_type = mini_window,districts = all_district,comment_count = all_comment,)
        elif clicked_on == 'delivery':
            all_partner = get_all_delivery_partner()
            return render_template('Admin/homepage.html',user_email =current_user.user_id,user_role = current_user.role,
                           mini_window_type = mini_window,delivery_partners = all_partner,districts = all_district,comment_count = all_comment,)
        elif clicked_on == 'seller':
            all_partner = get_all_selling_partner()
            return render_template('Admin/homepage.html',user_email =current_user.user_id,user_role = current_user.role,
                           mini_window_type = mini_window,delivery_partners = all_partner,districts = all_district,comment_count = all_comment,)
        elif clicked_on == 'home':
            return render_template('Admin/homepage.html',user_email =current_user.user_id,user_role = current_user.role,
                           districts = all_district,comment_count = all_comment,mini_window_type = mini_window)
        elif clicked_on == 'pie_loader':
            try:
                district = request.form['district']
            except Exception as e:
                flash("could not able to fetch form.")
                app.logger.error("could not able to fetch district from form.")
                return redirect(url_for('option',clicked_on = 'home'))
            render_data = pie_loader(district)
            return render_template('Admin/homepage.html',user_email =current_user.user_id,user_role = current_user.role,
                                mini_window_type = mini_window,d_chart = render_data['d_chart'],s_chart = render_data['s_chart'],
                                d_details = render_data['d_details'],s_details = render_data['s_details'],
                                location = render_data['location'],comment_count = all_comment,districts = all_district)
    return redirect(url_for('logout'))
        
 
    
