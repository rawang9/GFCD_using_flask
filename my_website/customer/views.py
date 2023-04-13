from my_website import app
from flask import render_template,request


@app.route('/<order_id>')
def feedback(order_id):
    #check whether  its a valid id or not 3 case fresh,already,wrong_id. 
    #if valid
    order_data = {'item_name':"Roadster_Tshirt",
                  'size':"M",'order_id':order_id,
                  'delivery_date':'17-01-2023',
                  'u_name':"Chirag kumar",
                  'email':'aki299@gmail.com'}
    # try:
    #     print(order_data.get('u_name'))
    # except Exception as e:
    #     pass
    if order_id== "fresh":
        return render_template('/customer/feedback.html',render_data = order_data)
    elif order_id == "Already":
        message = {'head':"You have already submited your feedback.",
                   'body':"Your feedback really help use in improving Our service for our Customers."}
        return render_template('/customer/submited.html',render_message = message)
    else:
        message = {'head':"Either you have already submited your feedback or clicked on wrong link.",
                   'body':"Your feedback really help use in improving Our service for our Customers."}
        return render_template('/customer/submited.html',render_message = message)
        


@app.route("/submited",methods=["GET","POST"])
def submit():
    if request.method == 'POST':
        delivery_rating = request.form['rating1']
        product_quality = request.form['rating2']
        comment = request.form['commentText']
        print(delivery_rating,product_quality,comment)
        message = {'head':"Thank you for you valuable feedback.",
                   'body':"Your feedback really help use in improving Our service for our Customers."}
        return render_template('/customer/submited.html',render_message = message)
    else:
        message = {'head':"Invalid attempt.",
                   'body':"try contacting us using 1900 1223 1234"}
        return render_template('/customer/submited.html',render_message = message)
        





