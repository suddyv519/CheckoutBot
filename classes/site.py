import threading
from json import load
from time import time, sleep

from classes.logger import Logger
from classes.product import Product

from webbot import Browser 

class Site(threading.Thread):
    def __init__(self, tid, config_filename, headless = False):
        threading.Thread.__init__(self)
        self.tid = tid
        self.start_time = time()
        self.log = Logger(tid).log
        self.web = Browser(showWindow=headless)
        with open(config_filename) as task_file:
            self.T = load(task_file)
        with open('config.json') as config_file:
            self.C = load(config_file)

    def wait(self, time):
        self.log('sleeping {} second(s)'.format(time))
        sleep(time)

    def login(self):
        self.web.go_to('https://catalog.usmint.gov/account-login')
        self.web.type(self.T["email"] , into='Login')
        self.web.type(self.T["password"] , into='Password')
        self.web.click('Sign In')

    def get_products(self):
        self.log('getting some products')
        self.web.go_to(self.T["link"])

    def add_to_cart(self):
        self.log('adding product to cart', 'blue')
        self.web.click('Add to Bag')
        # self.wait()

    def checkout(self):
        self.log('checking out')
        while not self.web.exists('Checkout', loose_match=False):
            self.wait(0.02)
        self.web.click('Checkout')
        self.web.click(id="shipping-method")
        self.web.click('Next Day')
        self.wait(0.1)

        # self.web.type(self.T["email"] , into='Login')
        # self.web.type(self.T["password"] , into='Password')
        # self.web.click('Checkout as Registered User')
        
        self.web.click(id="dwfrm_singleshipping_addressList")
        self.web.click(self.T["address"])
        self.wait(0.5)

        self.web.click(id="dwfrm_billing_paymentMethods_creditCardList")
        self.web.click(self.T["card"])
        self.web.type(self.T["cvv"] , id="dwfrm_billing_paymentMethods_creditCard_cvn")
        while not self.web.exists('Continue to Final Review', loose_match=False):
            self.wait(0.02)
        self.web.click('Continue to Final Review')
        # self.wait()

    def run(self):
        self.login()
        self.get_products()
        self.add_to_cart()
        self.checkout()
        self.wait(30)
        self.log('time to checkout: {} sec'.format(abs(self.start_time-time())), 'green')
