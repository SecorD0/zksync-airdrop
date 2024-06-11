from pretty_utils.type_functions.classes import AutoRepr
from sqlalchemy import (Column, Integer, Text)
from sqlalchemy.orm import declarative_base

# --- Wallets
Base = declarative_base()


class EligibleAddress(Base, AutoRepr):
    __tablename__ = 'eligible_addresses'

    id = Column(Integer, primary_key=True)
    address = Column(Text, unique=True)
    amount = Column(Integer)

    def __init__(self, address: str, amount: int) -> None:
        self.address = address
        self.amount = amount


class Address(Base, AutoRepr):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    address = Column(Text, unique=True)
    amount = Column(Integer)

    def __init__(self, address: str, amount: int = 0) -> None:
        self.address = address
        self.amount = amount
