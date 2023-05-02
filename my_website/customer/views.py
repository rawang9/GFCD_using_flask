from my_website import app
from flask import render_template,request,send_file
from service import Customer_class

@app.route('/<int:order_id>',methods=["GET","POST"])
def feedback(order_id):
    helper = Customer_class(order_id)
    if Customer_class.fresh_review(order_id):
        if request.method == 'GET':
            helper.set_text('FRESH')
            return render_template('/customer/feedback.html',render_data = helper.get_order_detail(),
                                                             visible = helper.get_show(),
                                                             order_item = helper.get_order_item())
        elif request.method == 'POST':
            helper.set_text('SUBMIT')
            print(helper.get_show(),helper.get_order_detail(),)
            fetch_form =  request.form
            pic = request.files['img']
            if helper.review_entry(img = pic,form_data = fetch_form):
                app.logger.info("Review Sucessfully added to the Databse.")
            else:
                app.logger.error("Unable to Add Review in Database.")

            return render_template('/customer/feedback.html',render_message = helper.get_message(),
                                                             render_data = helper.get_order_detail(),
                                                             visible = helper.get_show())
    else:
        helper.set_text('ALREADY')
        return render_template('/customer/feedback.html',render_message = helper.get_message(),
                                                         visible = helper.get_show())


    
# @app.route("/",methods = ["GET","POST"])
def Upload():
    if request.method == 'POST':
        pic = request.files['image']
        if not pic:
            return "no_pic uploaded",400
        from data_base import Review
        from PIL import Image
        import io
        mimetype = pic.mimetype #check mimetype to verify its img image/jpeg
        # pic.seek(0)
        image = Image.open(io.BytesIO(pic.read()))
        max_width = 800#resize the image
        max_height = 600
        width,height = image.size
        if width > max_width or height > max_height:
            ratio = min(max_width/width,max_height/height)
            new_size = (int(ratio*width),int(ratio*height))
            image = image.resize(new_size)
        #convert image to bytes
        buffer = io.BytesIO()
        image.save(buffer,format=f'{mimetype[6:]}') #mimetype = image/jpeg
        pic = buffer.getvalue()

        entry = Review(order_id=1041,seller_review="99",deliver_review=3,comment="good",
                       image = pic,img_type = mimetype,comment_type=1)
        entry.add_row()
        return mimetype

    else:
        return render_template('/index.html'),400
# @app.route("/get/<int:id>")
def get_img(id):
    from data_base import Review
    with app.app_context:
        img = Review.query.filter_by(order_id = id).first()
    if not img:
        return 'no img with this id',404
    else:
        from io import BytesIO
        
        image_data = BytesIO(img.image)
        content_type = img.img_type
        return send_file(image_data, mimetype=content_type)
# @app.route("/check")
def check():
    return render_template('index2.html')

@app.route('/order_detail/post',methods = ['POST'])
def handle_order():
    data = request.json
    from data_base import Order_details,db
    respose = {'message':data}
    try:
        entry = Order_details(customer_email = data['customer_email'],address_pin = data['address_pin'],
                          order_items = data['order_items'],delivery_id = data['delivery_id'])
        with app.app_context():
            db.session.add(entry)
            db.session.commit()
        respose['message'] = "Data Added Successfully in Order_table with delivery status Pending."
        return respose,200
    except Exception as e:
        app.logger.info('Cant process POST request came for adding entry in Order table.')
        respose['message'] = f"Error while adding Entry {e}."
        return respose,400
    
@app.route('/<int:id>/<change_status>',methods = ['GET'])
def delivery_status(id,change_status):
    from data_base import Order_details,db
    from data_base import DELIVERY_STATE
    respose = {'message':None}
    if DELIVERY_STATE.get(change_status)==None:
        respose['message'] = f'plese proive status in {DELIVERY_STATE.keys()} type.'
        return respose,400
    try:
        with app.app_context():
            entry_query = Order_details.query.filter_by(order_id = id).first()
            if entry_query:
                entry_query.delivery_status = DELIVERY_STATE[change_status]
                db.session.commit()
                respose['message'] = "Data Updated Successfully in Order_table with delivery status Pending."
                return respose,200
            else:
                respose['message'] = f"No entry found with {id}."
                return respose,400
    except Exception as e:
        app.logger.info('Cant process GET request came for changing delivery state in Order table.')
        respose['message'] = "Error while changing delivery state"
        return respose,400






        





