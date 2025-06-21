from abc import ABC, abstractmethod
from typing import Optional

# === INTERFACES ===

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


# === BANK ACCOUNT ===

class BankAccount(ITransfer, IVerifyCreditCard, IVerifyPayPal):
    def __init__(self, id: str, balance: float,
                 credit_card_number: Optional[str] = None,
                 paypal_email: Optional[str] = None):
        self._id = id
        self._balance = balance
        self._credit_card_number = credit_card_number
        self._paypal_email = paypal_email
        self._history = []

    @property
    def id(self):
        return self._id

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if value < 0:
            raise ValueError("balance cannot be negative")
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

    def add_history(self, desc: str):
        self._history.append(desc)

    def print_history(self):
        print(f"\n== account history {self._id} ==")
        for line in self._history:
            print(line)

    def transfer(self, amount: float, to_account: "BankAccount") -> bool:
        if self._id == to_account._id:
            print("Cannot transfer to yourself")
            return False
        if self._balance >= amount:
            self._balance -= amount
            to_account._balance += amount
            self.add_history(f"send {amount} ₪ to-{to_account._id}")
            to_account.add_history(f"reciev {amount} ₪ from-{self._id}")
            print(f"The transfer amounting to {amount} ₪ from-{self._id} ל-{to_account._id}")
            return True
        print(f"Failure: There is not enough money in the account {self._id}")
        return False

    def verify_credit_card(self, card_number: str) -> bool:
        return self._credit_card_number == card_number

    def verify_paypal_email(self, email: str) -> bool:
        return self._paypal_email == email

    def __str__(self):
        return f"Account: {self._id} | balance: {self._balance:.2f} ₪"

    def __repr__(self):
        return f"BankAccount('{self._id}', {self._balance}, '{self._credit_card_number}', '{self._paypal_email}')"

    def __del__(self):
        print(f"\n🗑️ Account {self._id} deleted from system.")


# === PAYMENT (ABSTRACT) ===

class Payment(ABC):
    _total_payments = 0

    def __init__(self, amount: float, from_account_id: str, to_account_id: str):
        self.amount = amount
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        Payment._total_payments += 1

    @staticmethod
    def get_total_payments():
        return Payment._total_payments

    @abstractmethod
    def process(self, accounts: dict[str, BankAccount]) -> bool:
        pass


# === CREDIT CARD PAYMENT ===

class CreditCardPayment(Payment):
    def __init__(self, amount, from_id, to_id, card_number):
        super().__init__(amount, from_id, to_id)
        self.card_number = card_number

    def process(self, accounts):
        from_acc = accounts.get(self.from_account_id)
        to_acc = accounts.get(self.to_account_id)

        if not IVerifyCreditCard.is_valid_card_format(self.card_number):
            print("Invalid credit card format")
            return False

        if not from_acc.verify_credit_card(self.card_number):
            print("Failure: The card does not match the account.")
            return False

        return from_acc.transfer(self.amount, to_acc)


# === PAYPAL PAYMENT ===

class PayPalPayment(Payment):
    def __init__(self, amount, from_id, to_id, email):
        super().__init__(amount, from_id, to_id)
        self.email = email

    def process(self, accounts):
        from_acc = accounts.get(self.from_account_id)
        to_acc = accounts.get(self.to_account_id)

        if not IVerifyPayPal.is_valid_email_format(self.email):
            print("Incorrect email format")
            return False

        if not from_acc.verify_paypal_email(self.email):
            print("Failure: The email does not match the account")
            return False

        return from_acc.transfer(self.amount, to_acc)


# === HELPER FUNCTION ===

def log_payment(payment: Payment, success: bool):
    status = " Success" if success else " failure"
    print(f"{status} | {payment.__class__.__name__} של {payment.amount} ₪ מ-{payment.from_account_id} ל-{payment.to_account_id}")


# === MAIN ===

def main():
    accounts = {
        "A001": BankAccount("A001", 1000.0, "1234567890123456", "user1@example.com"),
        "A002": BankAccount("A002", 500.0, "1111222233334444", "user2@example.com")
    }

    payments = [
        CreditCardPayment(200.0, "A001", "A002", "1234567890123456"),
        PayPalPayment(300.0, "A001", "A002", "wrong@example.com"),
        CreditCardPayment(900.0, "A002", "A001", "1111222233334444"),
        CreditCardPayment(100.0, "A001", "A001", "1234567890123456"),
        PayPalPayment(50.0, "A001", "A002", "invalid")
    ]

    for payment in payments:
        success = payment.process(accounts)
        log_payment(payment, success)
        print("-" * 40)

    for acc in accounts.values():
        print(acc)
        acc.print_history()

    print(f"\n Total payments made: {Payment.get_total_payments()}")


if __name__ == "__main__":
    main()
