import config
from sqlalchemy import create_engine, Integer, Column, Text, Table, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker, joinedload

engine = create_engine(config.sql_login)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False)
    ref = Column(Integer, nullable=False)
    balance = Column(Integer, default=0, nullable=False)
    count_game = Column(Integer, default=0, nullable=False)
    deposit = Column(Integer, default=0, nullable=False)
    out = Column(Integer, default=0, nullable=False)

    def __init__(self, user_id, ref, balance, count_game=0, deposit=0, out=0):
        self.user_id = user_id
        self.ref = ref
        self.balance = balance
        self.count_game = count_game
        self.deposit = deposit
        self.out = out

    def __repr__(self):
        return "<User(user_id=%s, ref=%s, balance=%s, count_game=%s, deposit=%s, out0%s)>" % (
            self.user_id, self.ref, self.balance, self.count_game, self.deposit, self.out)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def get_session():
    session = Session()
    try:
        return session
    finally:
        session.close()


def add_new_user(user_id, ref, balance=0):
    session: Session = get_session()
    s_user = User(user_id=user_id, ref=ref, balance=balance)
    session.add(s_user)
    session.commit()
    return True


def get_all_users():
    session: Session = get_session()
    s = session.query(User).all()
    return [(i.id, i.user_id, i.ref, i.balance, i.count_game) for i in s]


def exist_user(user_id):
    session: Session = get_session()
    s = session.query(User).filter_by(user_id=user_id).all()
    return bool(len(s))


def count_refs(user_id):
    session: Session = get_session()
    s = session.query(User).filter_by(ref=user_id).all()
    return len(s)


def get_user_info(user_id):
    session: Session = get_session()
    if not exist_user(user_id):
        return [0, 0, 0]
    user = session.query(User).filter_by(user_id=user_id).first()
    return [user.balance, count_refs(user_id), user.count_game]


def update_balance(user_id, count):
    session: Session = get_session()
    s = session.query(User).filter_by(user_id=user_id).first()
    count_balance = s.balance
    u = update(User).where(User.user_id == user_id).values(balance=count_balance + count).\
        execution_options(synchronize_session="fetch")
    session.execute(u)
    session.commit()
    return True


def update_count_game(user_id):
    session: Session = get_session()
    s = session.query(User).filter_by(user_id=user_id).first()
    count_game = s.count_game
    u = update(User).where(User.user_id == user_id).values(count_game=count_game + 1).\
        execution_options(synchronize_session="fetch")
    session.execute(u)
    session.commit()
    return True


def get_user_balance(user_id):
    session: Session = get_session()
    user = session.query(User).filter_by(user_id=user_id).first()
    balance = user.balance
    return balance


def add_dep(user_id, cash):
    session: Session = get_session()
    s = session.query(User).filter_by(user_id=user_id).first()
    old_balance = s.balance
    old_deposit = s.deposit
    user_ref = s.ref
    if int(user_ref) != 0:
        sel = session.query(User).filter_by(user_id=user_ref).first()
        ref_old_balance = sel.balance
        upd = update(User).where(User.user_id == user_ref).values(balance=ref_old_balance + cash // 10)\
            .execution_options(synchronize_session="fetch")
        session.execute(upd)
    u = update(User).where(User.user_id == user_id).values(balance=old_balance + cash,
                                                           deposit=old_deposit + cash). \
        execution_options(synchronize_session="fetch")
    session.execute(u)
    session.commit()
    return True
