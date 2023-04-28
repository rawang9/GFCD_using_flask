try:
    from my_website import db,app
    from sqlalchemy import DDL,event,func,Sequence,text
    from flask_login import UserMixin
except Exception as e:
    app.logger.error("Could not import module in data_base.py.")

DAY_LEFT        = 2
DELIVERY_STATE  = {'Initial'    : "Pending",
                   'Fail'       : "Cancelled",
                   'Pass'       : "Delivered"}
TODAY           = func.now()
CONFIRM         = "Delivered"
DEFAULT_ROLE    = "VIEWER"

class Seller_partner(db.Model):
    seller_id       = db.Column(db.Integer(), primary_key = True)
    seller_name     = db.Column(db.String(50), nullable = False)


class Delivery_partner(db.Model):
    d_partner_id    = db.Column(db.Integer(), primary_key = True)
    d_partner_name  = db.Column(db.String(50), nullable = False)

class Order_details(db.Model):
    # __tablename__   = 'order_data' this is used to give table name
    order_id        = db.Column(db.Integer(), Sequence('order_id_seq'), primary_key = True)
    customer_email  = db.Column(db.String(20), nullable = False) 
    address_pin     = db.Column(db.Integer(), nullable = False) 
    order_items     = db.Column(db.String(250), nullable = False)
    delivery_id     = db.Column(db.Integer(), db.ForeignKey('delivery_partner.d_partner_id'))
    delivery_status = db.Column(db.String(10), nullable = False,default = DELIVERY_STATE['Initial'])

    # def add_row(self):
    #     try:
    #         with app.app_context():
    #             # create a SQLAlchemy engine object
    #             engine = db.engine
    #             # create a database connection
    #             conn = engine.connect()
    #             db.session.add(self)
    #             db.session.commit()
    #     except Exception as e:
    #         sequence_name = 'order_id_seq'
    #         # execute a query to check if the sequence exists
    #         query = text(f"SELECT COUNT(*) FROM all_sequences WHERE sequence_name = '{sequence_name}'")
    #         result = conn.execute(query)
    #         # extract the count from the query result
    #         count = result.fetchone()[0]
            
    #         if count > 0:
    #             app.logger.error("Some problem occure in data_base file while inserting values in order_details.")
    #         else:
    #             try:
    #                 query = text("CREATE SEQUENCE order_id_seq START WITH 1001 INCREMENT BY 1")
    #                 conn.execute(query)
    #                 with app.app_context():
    #                     db.session.add(self)
    #                     db.session.commit()
    #             except Exception as e:
    #                 app.logger.error("Unable to create Sequence or psuh the row in Order_details.")
    #     finally:
    #         conn.close()





class Pending_feedback(db.Model):
    order_id        = db.Column(db.Integer(), db.ForeignKey('order_details.order_id'),primary_key = True) 
    email_id        = db.Column(db.String(20), nullable = False)
    days_left       = db.Column(db.Integer(), default = DAY_LEFT,nullable = False)

class Review(db.Model):
    order_id        = db.Column(db.Integer(), db.ForeignKey('order_details.order_id'),primary_key = True)
    seller_review   = db.Column(db.String(250), nullable = False)
    deliver_review  = db.Column(db.Integer(), nullable = False)
    comment         = db.Column(db.String(50), nullable = True)
    image           = db.Column(db.LargeBinary(), nullable = True)
    img_type        = db.Column(db.String(20),nullable=True)
    review_date     = db.Column(db.Date(), default = TODAY)
    comment_type    = db.Column(db.Integer(), nullable = True)
 
#The NEW keyword refers to the updated row details. In this case,
# we use NEW.order_id and NEW.customer_email to insert the updated values into the pending_feedback table.
pending_trigger = DDL(f"""
    CREATE OR REPLACE TRIGGER o_one
    AFTER UPDATE ON order_details
    FOR EACH ROW
    BEGIN
        IF :NEW.delivery_status = '{DELIVERY_STATE['Pass']}' AND :OLD.delivery_status = '{DELIVERY_STATE['Initial']}' THEN
            INSERT INTO pending_feedback (order_id, email_id,days_left)
            VALUES (:NEW.order_id, :NEW.customer_email,{DAY_LEFT});
        END IF;
    END;
""")
event.listen(Order_details.__table__,'after_create',pending_trigger)

class Bad_review(db.Model):
    order_id        = db.Column(db.Integer(), db.ForeignKey('order_details.order_id'),primary_key = True)


class Authority(db.Model,UserMixin):
    user_id     = db.Column(db.String(30), primary_key = True)
    password    = db.Column(db.String(250), nullable = False)
    role        = db.Column(db.String(15), nullable = False, default = DEFAULT_ROLE)
    #overriging get_id of UserMixin becaues by default it relturn self.id and hear i need to return user_id
    def get_id(self):
        return self.user_id















