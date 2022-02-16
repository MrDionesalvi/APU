import sqlalchemy as master
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import String


Base = declarative_base()
engine = master.create_engine('sqlite:////home/dionesalvi/public_html/APU/data.db?check_same_thread=False')
Session = sessionmaker(bind=engine)


class Database:
    def __init__(self):
        self.session = Session()
        Base.metadata.create_all(bind=engine)

    class user(Base):
        __tablename__ = 'user'

        id = master.Column(master.Integer, primary_key=True)
        username = master.Column(master.Text, default="")
        member = master.Column(master.Integer, default=0)
        admin = master.Column(master.Integer, default=0)

        def __repr__(self):
            return f'<User #{self.id}>'

    class beehives(Base):
        __tablename__ = 'beehives'

        id = master.Column(master.Integer, primary_key=True)
        owner = master.Column(master.Text, default="")
        name = master.Column(master.Text, default="")
        
        x_coords = master.Column(master.Integer, default=0)
        z_coords = master.Column(master.Integer, default=0)
        doc = master.Column(master.Text, default="")

        def __repr__(self):
            return f'<Beehives #{self.id}>'

    class apiarys(Base):
        __tablename__ = 'apiarys'

        id = master.Column(master.Integer, primary_key=True)
        owner = master.Column(master.Text, default="")

        idBeehive = master.Column(master.Integer, default=0)
        typeBee = master.Column(master.Text, default="")

        def __repr__(self):
            return f'<Apiary #{self.id}>'
    
    class invoices(Base):
        __tablename__ = 'invoices'

        id = master.Column(master.Integer, primary_key=True)
        user = master.Column(master.Text, default="")
        date = master.Column(master.Text, default="")
        ammount = master.Column(master.Integer, default=0)
        paid = master.Column(master.Boolean, default=False)

        #description = master.Column(master.Text, default="no")

        def __repr__(self):
            return f'<Invoice #{self.id}>'

