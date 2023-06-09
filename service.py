from my_website import app,db
from data_base import Review,Order_details,Bad_review,Pending_feedback
from pandas import read_csv
import json
import os
import smtplib as sm
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
#used for sentiment analysis of text
from textblob import TextBlob
#pillow library for editing image
from PIL import Image
#convert img into bytecode
import io
class Customer_class:
    def __init__(self,id):
        self.__MESSAGE      = {'head':None,'body':None}
        self.__ORDER_DETAIL = {'order_id':None,'customer_email':None,'address':None,'delivery_status':None}
        self.__ORDER_ITEM   = [{'item_id':None,'qty':None,'seller_id':None,'item_type':None},]
        self.__SHOW         = {'c_detail':False,'feedback_form':False}
        self.__order_id     = id 
    @staticmethod
    def fresh_review(id):
        with app.app_context():
            match = Review.query.filter_by(order_id=id).first()
        if match==None:
            return True
        else:
            return False
    def set_text(self,state):
        if state == 'FRESH':
            self.__SHOW.update({'c_detail':True,'feedback_form':True})
            try:
                with app.app_context():
                    order_record = Order_details.query.filter_by(order_id = self.__order_id).first()
            except Exception as e:
                app.logger.error(f"Error {e} occured while fetching detail from Order_details in service.py")
            df = read_csv('pincode.csv')
            result = df.loc[df['Pincode'] == order_record.address_pin]
            post_office = result.OfficeName.iloc[0]
            self.__ORDER_DETAIL.update({'order_id':order_record.order_id,'customer_email':order_record.customer_email,
                                        'address':post_office,'delivery_status':order_record.delivery_status})
            try:
                items = order_record.order_items
                print("items-> ",items)
                self.__ORDER_ITEM = json.loads(items)
                print(self.__ORDER_ITEM)
            except Exception as e:
                app.logger.error(f"Error {e} occur, while converting String to JSON in services.")
                #always add data in '[{"item_id":9221,"qty":1,"seller_id":433,"item_type":"Tshirt"},]' this formate
                # '"' double quote inside single quotes
        elif state == 'SUBMIT':
            #---|
            self.__SHOW.update({'c_detail':False,'feedback_form':False})
            self.__MESSAGE.update({'head':"Thank you for you valuable feedback.",
                                   'body':"Your feedback really help use in improving Our service for our Customers."})
        else:
            self.__SHOW.update({'c_detail':False,'feedback_form':False})
            self.__MESSAGE.update({'head':"Either you have already submited your feedback or clicked on wrong link.",
                                   'body':"Your feedback really help use in improving Our service for our Customers."})
    
    def get_message(self):
        return self.__MESSAGE
    def get_order_detail(self):
        return self.__ORDER_DETAIL
    def get_show(self):
        return self.__SHOW
    def get_order_item(self):
        return self.__ORDER_ITEM

    def image_to_byte(self,pic):
        #check mimetype to verify its img image/jpeg
        mimetype = pic.mimetype 
        pic.seek(0)
        image = Image.open(io.BytesIO(pic.read()))
        #resize the image
        max_width = 800
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
        return [pic,mimetype]

    def review_entry(self,**kwargs):
        entry_data = {'order_id':self.__order_id,'seller_review':None,'delivery_review' : None,
                      'comment':None,'comment_type':None,'image':None}
        try:
            form_data = kwargs['form_data']
            seller_data = []
            for key in form_data:
                if key == 'd_rating':
                    entry_data['delivery_review'] = form_data[key]
                elif key == 'comment':
                    entry_data['comment'] = form_data[key]
                else:
                    s_id = key[:len(key)-1]
                    seller_data.append({s_id:form_data[key]})
            entry_data['seller_review'] = json.dumps(seller_data) 
            blob1 = TextBlob(entry_data['comment'])
            #blob1.sentiment.polarity can return three values -1 means negative,0 means neutral and 1 means postive
            sentiment_value = blob1.sentiment.polarity
            result = 0
            if sentiment_value > 0:
                result = 1
            elif sentiment_value < 0:
                result = -1
            entry_data['comment_type'] = result
            #check mimetype to verify its img image/jpeg image type
            mimetype = None
            pic = kwargs['img']
            if not pic:
                pic = None
            else:
                pic,mimetype = self.image_to_byte(pic)
            entry_data['image'] = pic
        except Exception as e:
            app.logger.error(f"Encounter error {e} while formating data in services.")    
        #inserting row into Review table.
        try:
            entry =  Review(order_id = entry_data['order_id'], seller_review = entry_data['seller_review'],
                            deliver_review = entry_data['delivery_review'], comment = entry_data['comment'],
                            image = entry_data['image'],img_type = mimetype, comment_type = entry_data['comment_type'])
            with app.app_context():
                db.session.add(entry)
                db.session.commit()
            return True
        except Exception as e:
            app.logger.error(f"Cant insert value in database {e} error occured in Service.")
            return False


class Schedule:
    @staticmethod
    def send_mail():
        #need_to_send = [{"email_id":"abc@gmail.com","order_id":1234}]
        need_to_send = []
        try:
            with app.app_context():
                pending_query = Pending_feedback.query.all()
                for row in pending_query:
                    if row.days_left-1 == 0:
                        email_data = {"email_id":row.email_id,"order_id":row.order_id}
                        need_to_send.append(email_data)
                        db.session.delete(row)
                    else:
                        row.days_left -=1
                db.session.commit()
            app.logger.info("Provided lsit of mail to once_a_dat file.")
        except:
            app.logger.error("Unable to perform fetch email on Pending_feedback")
        if len(need_to_send) > 0:
            try:
                with sm.SMTP("smtp.gmail.com") as connnection:
                    connnection.starttls()
                    connnection.login(user= os.environ.get('COMPANY_EMAIL'),
                                    password=os.environ.get('EMAIL_PASS'))    
                    for user_data in need_to_send:
                        CUSTOMER_EMAIL = user_data['email_id']
                        LINK           = f"https://customer-feedback-dashboard.onrender.com/{user_data['order_id']}"
                        MESSAGE        = "Hey ,\n\nThanks for shopping from fynd. We would appreciate it if you can spare a little " \
                                        f"of your time and provide us your valuable feedback by clicking  on  {LINK} " \
                                        "\n\nthank you."
                        msg = MIMEMultipart()
                        msg['From']    = os.environ.get('COMPANY_EMAIL')
                        msg['To'] = CUSTOMER_EMAIL
                        msg['Subject'] = "Fynd feedback regarding your recent order"
                        msg.attach(MIMEText(MESSAGE))
                        connnection.sendmail(from_addr=os.environ.get('COMPANY_EMAIL'),to_addrs=CUSTOMER_EMAIL,
                                             msg = msg.as_string())
                app.logger.info("All mail Send Sucessfully.")
            except Exception as e:
                app.logger.error(f"Error {e} orrcur while Sending mail to the customers.")



        
        