"""
Course    : CSE 351
Assignment: 02
Student   : <your name here>

Instructions:
    - review instructions in the course
"""

# Don't import any other packages for this assignment
import os
import random
import threading
from money import *
from cse351 import *

# ---------------------------------------------------------------------------
def main(): 

    print('\nATM Processing Program:')
    print('=======================\n')

    create_data_files_if_needed()

    # Load ATM data files
    data_files = get_filenames('data_files')
    print(data_files)
    threads = []
    
    log = Log(show_terminal=True)
    log.start_timer()

    bank = Bank()

    deposit_withdrawal_lock = threading.Lock()

    for file in data_files:
        #figure out how to get the ATM_Reader to work with the three pieces of data
        t = ATM_Reader(file, bank, deposit_withdrawal_lock)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    test_balances(bank)

    log.stop_timer('Total time')

        


# ===========================================================================
class Account():
    def __init__(self, account_number: int):
        self.account_number = account_number
        self.balance = Money("0")
    
    def deposit(self, amount: str):
        self.balance.add(Money(amount))

    def withdraw(self, amount: str):
        self.balance.sub(Money(amount))

    def get_balance(self) -> Money:
        return self.balance


# ===========================================================================
class Bank():
    def __init__(self):
        self.accounts = {}

    def deposit(self, account: Account, amount: str):
        account.deposit(amount)

    def withdraw(self, account: Account, amount: str):
        account.withdraw(amount)

    def get_balance(self, account_num: int):
        return self.accounts[account_num].get_balance()



# ===========================================================================
class ATM_Reader(threading.Thread):
    def __init__(self, file, bank: Bank, transaction_lock: threading.Lock):
        super().__init__()
        self.file = file
        self.bank = bank
        self.transaction_lock = transaction_lock

    def run(self):
        lines = open(self.file, "r")
        #DONT uncomment ~.~
        # for line in lines:
        #     print(line)
        for line in lines:
            if not line.startswith("#"):
                data_pieces = line.strip().split(",")
                #print(data_pieces) --> DONT uncomment this either -_-
                self.process_transaction(data_pieces)
        
    #need to process what is being given for each line of the file
    def process_transaction(self, data):

        account_num = int(data[0])

        #adding account to the Bank if it doesn't exist
        if account_num not in self.bank.accounts:
            self.bank.accounts[account_num] = Account(account_num)

        #performing withdrawal for associated account
        if data[1] == "w":
            with self.transaction_lock:
                self.bank.withdraw(self.bank.accounts[account_num], data[2])
            #MAN troubleshooting this is hard when you can't print anything
            #print(bank.accounts[account_num].get_balance())

        #deposit for associated account
        if data[1] == "d":
            with self.transaction_lock:
                self.bank.deposit(self.bank.accounts[account_num], data[2])



# ---------------------------------------------------------------------------

def get_filenames(folder):
    """ Don't Change """
    filenames = []
    for filename in os.listdir(folder):
        if filename.endswith(".dat"):
            filenames.append(os.path.join(folder, filename))
    return filenames

# ---------------------------------------------------------------------------
def create_data_files_if_needed():
    """ Don't Change """
    ATMS = 10
    ACCOUNTS = 20
    TRANSACTIONS = 250000

    sub_dir = 'data_files'
    if os.path.exists(sub_dir):
        return

    print('Creating Data Files: (Only runs once)')
    os.makedirs(sub_dir)

    random.seed(102030)
    mean = 100.00
    std_dev = 50.00

    for atm in range(1, ATMS + 1):
        filename = f'{sub_dir}/atm-{atm:02d}.dat'
        print(f'- {filename}')
        with open(filename, 'w') as f:
            f.write(f'# Atm transactions from machine {atm:02d}\n')
            f.write('# format: account number, type, amount\n')

            # create random transactions
            for i in range(TRANSACTIONS):
                account = random.randint(1, ACCOUNTS)
                trans_type = 'd' if random.randint(0, 1) == 0 else 'w'
                amount = f'{(random.gauss(mean, std_dev)):0.2f}'
                f.write(f'{account},{trans_type},{amount}\n')

    print()

# ---------------------------------------------------------------------------
def test_balances(bank):
    """ Don't Change """

    # Verify balances for each account
    correct_results = (
        (1, '59362.93'),
        (2, '11988.60'),
        (3, '35982.34'),
        (4, '-22474.29'),
        (5, '11998.99'),
        (6, '-42110.72'),
        (7, '-3038.78'),
        (8, '18118.83'),
        (9, '35529.50'),
        (10, '2722.01'),
        (11, '11194.88'),
        (12, '-37512.97'),
        (13, '-21252.47'),
        (14, '41287.06'),
        (15, '7766.52'),
        (16, '-26820.11'),
        (17, '15792.78'),
        (18, '-12626.83'),
        (19, '-59303.54'),
        (20, '-47460.38'),
    )

    wrong = False
    for account_number, balance in correct_results:
        bal = bank.get_balance(account_number)
        print(f'{account_number:02d}: balance = {bal}')
        if Money(balance) != bal:
            wrong = True
            print(f'Wrong Balance: account = {account_number}, expected = {balance}, actual = {bal}')

    if not wrong:
        print('\nAll account balances are correct')



if __name__ == "__main__":
    main()

