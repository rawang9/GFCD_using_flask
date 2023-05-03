# from data_base import Delivery_partner,Order_details,app,db

# # entry  = Delivery_partner(2,"Clint")
# # entry.add_row()

# # entry = Order_details(customer_email = "email",address_pin=273015,
# #                       order_items = "order",delivery_id = 2)
# # entry.add_row()
# with app.app_context():
#     # db.create_all()
#     detail = Order_details.query.filter_by(order_id=1041).first()
#     # # print(detail) #handel None then oid not forund
#     detail.delivery_status = "Delivered"
#     db.session.commit()
# from textblob import TextBlob
# comment1 = "it meet my expectation"
# comment2 = "None soo good"
# blob1 = TextBlob(comment1)
# blob2 = TextBlob(comment2)
# print(blob1.sentiment.polarity)
# print(blob2.sentiment.polarity)
# from data_base import Review,app,Order_details
# import json
# def fresh_review(id):
#         with app.app_context(): 
#             match = order_detail = Order_details.query.filter_by(order_id = id).first()
#         return match
# record = fresh_review(1041).order_items
# jsn = json.loads(record)
# print(type(jsn),type(jsn[0]))
# import json
# order = '[{"item_id":9221,"qty":1,"seller_id":433,"item_type":"Tshirt"},{"item_id":8382,"qty":3,"seller_id":1234,"item_type":"Jeans"}]'
# res = json.loads(order)
# print(type(res))
# class Heel:
#     def __init__(self):
#         self.__name = "king"
#     def get(self):
#         print(self.__name)
# h1 = Heel()
# _Heel__name = "amam"
# h1.get()
# import json
# a = [{'912':2},{'231':2}]
# res = json.dumps(a)
# print(type(res))
# from data_base import app,db,Order_details,Review,Seller_partner,Delivery_partner
# import json
# from pandas import read_csv
# df = read_csv('pincode.csv')
# all_pins = df[df['District']=='GORAKHPUR']['Pincode'].to_list()
# with app.app_context():
#     order_query = db.session.query(Order_details.order_id,Order_details.delivery_id).filter(Order_details.address_pin.in_(all_pins),
#     Order_details.delivery_status == 'Delivered' ).all()
# order_data = {} 
# for row in order_query:
#     order_data[row[0]] = row[1]
# with app.app_context():
#     review_query = db.session.query(Review.deliver_review,Review.seller_review,Review.order_id).filter(Review.order_id.in_(order_data.keys())).all()
# all_detail = []
# delivery_chart = {}
# seller_chart = {}
# scale = {5:'EXELENT',4:'VERY GOOD',3:'GOOD',2:'NOT GOOD',1:'BAD'}
# for review in review_query:
#     delivery_id = order_data[review.order_id]
#     if delivery_chart.get(delivery_id) == None:
#         delivery_chart[delivery_id] = {'EXELENT':0,'VERY GOOD':0,'GOOD':0,'NOT GOOD':0,'BAD':0}
#     delivery_rating = review.deliver_review
#     delivery_chart[delivery_id][scale[delivery_rating]] +=1

#     sellers = json.loads(review.seller_review)
#     for seller_review in sellers:
#         if list(seller_review.keys())[0] != None:
#             pass
#         else:
#             seller_id = int(list(seller_review.keys())[0])
#         if seller_chart.get(seller_id) == None:
#             seller_chart[seller_id]= {'EXELENT':0,'VERY GOOD':0,'GOOD':0,'NOT GOOD':0,'BAD':0}
#         seller_rating = int(list(seller_review.values())[0])
#         seller_chart[seller_id][scale[seller_rating]] +=1

# print(delivery_chart,seller_chart)
# with app.app_context():
#     seller_query = db.session.query(Seller_partner.seller_id,Seller_partner.seller_name).filter(Seller_partner.seller_id.in_(seller_chart.keys())).all()
#     delivery_query = db.session.query(Delivery_partner.d_partner_id,Delivery_partner.d_partner_name).filter(Delivery_partner.d_partner_id.in_(delivery_chart.keys())).all()
# seller_details = {}
# for row in seller_query:
#     seller_details[row.seller_id] = row.seller_name
# delivery_details = {}
# for row in delivery_query:
#     delivery_details[row.d_partner_id] = row.d_partner_name
# print(seller_details,delivery_details)

# #scaling review on scale of 100
# for key in delivery_chart:
#     no_of_review = 0
#     for child_key in delivery_chart[key]:
#         no_of_review += delivery_chart[key][child_key]
#     for child_key in delivery_chart[key]:
#         delivery_chart[key][child_key] = (delivery_chart[key][child_key]/no_of_review)*100
# for key in seller_chart:
#     no_of_review = 0
#     for child_key in seller_chart[key]:
#         no_of_review += seller_chart[key][child_key]
#     for child_key in seller_chart[key]:
#         seller_chart[key][child_key] = (seller_chart[key][child_key]/no_of_review)*100
# print(delivery_chart,seller_chart)


# import requests
# import json
# #add order details
# # Define the data to be sent in JSON format
# data =  {  
#             "customer_email":"akarshitg9@gmail.com",
#             "address_pin":273015,
#             "order_items":'[{"item_id":11311,"qty":1,"seller_id":1022,"item_type":"tshirt"}]',
#             "delivery_id":12938,
#         }

# # Convert the data to JSON format
# json_data = json.dumps(data)
# print(json_data)
# # Set the headers to indicate that the data is in JSON format
# headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# # Set the URL of the Flask POST API endpoint
# url = 'http://localhost:5000/order_detail/post'

# # Send the POST request to the Flask API endpoint with the JSON data and headers
# response = requests.post(url, data=json_data, headers=headers)

# # Print the response from the Flask API endpoint
# print(response.text)
from my_website import db
try:
    db.engine.execute("CREATE TABLE DEPARTMENT( ID INT PRIMARY KEY NOT NULL,DEPT CHAR(50) NOT NULL,\
   EMP_ID INT NOT NULL);")
    db.session.commit()
except Exception:
    pass
print("done")

    




