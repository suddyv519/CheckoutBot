import threading
from json import load
from time import time, sleep

from classes.logger import Logger
from classes.product import Product

from webbot import Browser 
import pause, datetime

class Site(threading.Thread):
    def __init__(self, tid, config_filename, headless = False):
        threading.Thread.__init__(self)
        self.tid = tid
        self.start_time = time()
        self.log = Logger(tid).log
        self.web = Browser(showWindow=not headless, incognito=True)
        self.gold_link = 'https://catalog.usmint.gov/basketball-hall-of-fame-2020-uncirculated-silver-dollar-20CD.html?cgid=silver-dollars#start=1'
        self.silver_link = ''

        with open(config_filename) as task_file:
            self.T = load(task_file)


    def wait(self, time):
        self.log('sleeping {} second(s)'.format(time))
        sleep(time)

    def login(self):
        self.web.go_to('https://catalog.usmint.gov/account-login')
        self.web.type(self.T["email"] , into='Login')
        self.web.type(self.T["password"] , into='Password')
        self.web.click(id="login")

    def get_products(self):
        self.log('getting some products')
        self.web.go_to(self.gold_link)
        day = 4
        hour = 20
        minute = 0
        dt = datetime.datetime(2020, 11, day, hour, minute, 0)
        self.log(f'waiting until {hour}:{minute}')
        pause.until(dt)

    def add_to_cart(self):
        # while self.web.exists(classname="acsClassicInner"):
        #     self.log('survey pop up detected')
        #     self.web.refresh()
        self.log('adding product to cart', 'blue')
        while not self.web.exists('Add to Bag', loose_match=False):
            self.log('waiting for add to bag button to appear')
            self.refresh()
        self.web.click('Add to Bag')

    def checkout(self):
        self.log('checking out')
        self.web.click(classname="mini-cart-link")
        self.web.click(id="shipping-method")
        self.web.click('Next Day')
        self.wait(0.1)
        
        # self.wait(300)
        self.web.click(id="dwfrm_singleshipping_addressList")
        self.web.click(self.T["address"])
        self.wait(0.8) #

        self.web.click(id="dwfrm_billing_paymentMethods_creditCardList")
        self.web.click(self.T["card"])
        self.web.type(self.T["cvv"] , id="dwfrm_billing_paymentMethods_creditCard_cvn")
        while not self.web.exists(id="checkoutContinuePaymentDelegator", loose_match=False):
            self.log('waiting for checkout button')
            self.wait(0.01)
        self.web.click(id="checkoutContinuePaymentDelegator")
       
        ############# self.web.click(id="submitOrderButton") # UNCOMMENT TO PURCHASE 

    def run(self):
        self.login()
        self.get_products()
        self.add_to_cart()
        self.checkout()
        # self.wait(3000) 
        self.log('time to checkout: {} sec'.format(abs(self.start_time-time())), 'green')
