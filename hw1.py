from abc import ABC, abstractmethod
from typing import Optional, override


class ITransfer(ABC):
    @abstractmethod
    def transfer(self, amount: float, to_account: "BankAccount") -> bool:
        pass


class IVerifyCreditCard(ABC):
    @abstractmethod
    def verify_credit_card(self, card_number: str) -> bool:
        pass

    @staticmethod
    def is_valid_card_format(card_number: str) -> bool:
        return card_number.isdigit() and len(card_number) == 16


class IVerifyPayPal(ABC):
    @abstractmethod
    def verify_paypal_email(self, email: str) -> bool:
        pass

    @staticmethod
    def is_valid_email_format(email: str) -> bool:
        return "@" in email and "." in email



class BankAccount(ITransfer, IVerifyCreditCard, IVerifyPayPal):
    ...

    def __init__(self, id: str, balance: float,
                 credit_card_number: Optional[str] = None,
                 paypal_email: Optional[str] = None):
        self._id = id
        self._balance = balance
        self._credit_card_number = credit_card_number
        self._paypal_email = paypal_email

    # === GETTERS ===
    @property
    def id(self):
        return self._id

    @property
    def balance(self):
        return self._balance

    # === SETTERS ===
    @balance.setter
    def balance(self, value: float):
        if value < 0:
            raise ValueError("A balance cannot be negative.")
        self._balance = value

    @property
    def credit_card_number(self):
        return self._credit_card_number

    @credit_card_number.setter
    def credit_card_number(self, number: str):
        if not IVerifyCreditCard.is_valid_card_format(number):
            raise ValueError("Invalid credit card format")
        self._credit_card_number = number

    @property
    def paypal_email(self):
        return self._paypal_email

    @paypal_email.setter
    def paypal_email(self, email: str):
        if not IVerifyPayPal.is_valid_email_format(email):
            raise ValueError("Invalid email format")
        self._paypal_email = email

    # === main action ===
    @override
    def transfer(self, amount: float, to_account: "BankAccount") -> bool:
        if self._balance >= amount:
            self._balance -= amount
            to_account._balance += amount
            print(f"A transfer was made of {amount} ₪ from-{self._id} ל-{to_account._id}")
            return True
        print(f"Failure: There is not enough money in the account {self._id}")
        return False

    @override
    def verify_credit_card(self, card_number: str) -> bool:
        return self._credit_card_number == card_number

    @override
    def verify_paypal_email(self, email: str) -> bool:
        return self._paypal_email == email

    @override
    def __str__(self):
        return f"Account: {self._id} | balance: {self._balance:.2f} ₪"

    @override
    def __repr__(self):
        return (f"BankAccount('{self._id}', {self._balance}, "
                f"'{self._credit_card_number}', '{self._paypal_email}')")



acc = BankAccount("A001", 1000.0, "1234567890123456", "user@example.com")
print(acc)        # use ־__str__
print(repr(acc))  # use ־__repr__

acc.balance = 800   # OK
# acc.balance = -5  # ValueError: Balance cannot be negative

acc.credit_card_number = "1111222233334444"  # OK
# acc.credit_card_number = "bad"             # ValueError: Invalid credit card format
