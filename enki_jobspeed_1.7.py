''' JobSpeed: desktop application with locally stored database and subscription via server'''

import sys
import requests
import os
import shutil
from datetime import *
from dateutil.relativedelta import *
import collections
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from pathlib import Path
import sqlite3
import random
import enki_core
import enki_crud



# sqllite, microsoft azure for virtual comp, plan out and import modules, flask/ django and bootstrap
# examine 3 tier webapp. eg. 1. UI - html, css, javascript / bootstrap. 2. python/ flask/ django 3. database sqllite grow outwards
# deployment as final step
# mvp - minimal viable product

conn = sqlite3.connect('enki_sqlite_database.db')
c = conn.cursor()

def convert_to_integer(value):
    if value is True:
        value = 1
    else:
        value = 0
    return value

def move_file():
    '''move file operation that moves files in windows and unix'''
    source_path = Path(os.path.realpath(sys.argv[0]))  # requires absolute path /home/jaskaran/PycharmProjects/enki
    dst_path = Path(source_path.parent / "job_sheets")
    for files in source_path.parent.glob('*.pdf'):
        files.replace(dst_path / files.name)  # works to move the file

def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping): #WHAT IS THIS DOING?????
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def search_everywhere_function(required_item):
    '''search database everywhere not caps sensitve'''
    matches = []
    unique_matches = []
    if '#' in required_item:
        required_item = required_item.split('#')[1]
        required_item = int(required_item)
        c.execute("SELECT * FROM CustomerTable")
        customer_table = c.fetchall()

        for row, item in enumerate(customer_table):
            if item[0] == required_item:
                unique_matches.append(item[0])
                final_list = []
                for e in unique_matches:
                    c.execute("SELECT * FROM CustomerTable WHERE jobnumber=(?)", (e,))
                    cus_data = c.fetchall()
                    sub_list = []
                    sub_list.append(cus_data[0][0])
                    sub_list.append(cus_data[0][2])
                    sub_list.append(cus_data[0][7])
                    final_list.append(sub_list)
                    return final_list

    required_item = str(required_item)
    c.execute("SELECT * FROM SubJobTable")
    whole_subjob_table = c.fetchall()
    c.execute("SELECT * FROM CustomerTable")
    whole_customer_table = c.fetchall()
    for row, item in enumerate(whole_subjob_table):
        for i in item:
            try:
                if required_item.lower() in i:
                    matches.append(item[0])
                elif required_item.title() in i:
                    matches.append(item[0])
            except:
                if required_item == i:
                    matches.append(item[0])

    for row, item in enumerate(whole_customer_table):
        for i in item:
            try:
                if required_item.lower() in i:
                    matches.append(item[0])
                elif required_item.title() in i:
                    matches.append(item[0])
            except:
                if required_item == i:
                    matches.append(item[0])
    for i in matches:
        if i not in unique_matches:
            unique_matches.append(i)
    final_list = []
    for e in unique_matches:
        c.execute("SELECT * FROM CustomerTable WHERE jobnumber=(?)", (e,))
        cus_data = c.fetchall()
        sub_list = []
        sub_list.append(cus_data[0][0])
        sub_list.append(cus_data[0][2])
        sub_list.append(cus_data[0][7])
        final_list.append(sub_list)
    return final_list

def search_for_overall_status(required_item):
    matches = []
    unique_matches = []
    c.execute("SELECT * FROM CustomerTable")
    whole_customer_table = c.fetchall()
    for row, item in enumerate(whole_customer_table):
        for i in item:
            if required_item == i:
                matches.append(item[0])
    for i in matches:
        if i not in unique_matches:
            unique_matches.append(i)
    final_list = []
    for e in unique_matches:
        c.execute("SELECT * FROM CustomerTable WHERE jobnumber=(?)", (e,))
        cus_data = c.fetchall()
        sub_list = []
        sub_list.append(cus_data[0][0])
        sub_list.append(cus_data[0][2])
        sub_list.append(cus_data[0][7])
        final_list.append(sub_list)
    return final_list

def date_sorter(list_to_sort):
    '''sort dates by most recent descending'''
    s = sorted(list_to_sort, key=lambda x: x[2][0:3:])
    t = sorted(s, key=lambda x: x[2][3:5:])
    list_to_sort = sorted(t, key=lambda x: x[2][5::])
    return list_to_sort

def set_search_customer_fields():
    ''' send the correct data to the search screen when a job is selected in rv'''
    app = App.get_running_app()
    subjob_dict = {}
    subjob_dict.clear()  # just in case there is another variable pointing to this
    app.search_subjob_dict.clear()
    subjob_dict = enki_crud.DBMethods(int(app.job)).build_dict_from_subjob()
    app.search_subjob_dict = {}
    update_dict(app.search_subjob_dict, subjob_dict)

    c.execute("SELECT customername FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    customer_name = c.fetchone()[0]
    app.search_customer_name = str(customer_name)
    c.execute("SELECT contactnumber FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    contact_number = c.fetchone()[0]
    app.search_contact_number = str(contact_number)
    c.execute("SELECT email FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    email_add = c.fetchone()[0]
    app.search_email_add = str(email_add)
    c.execute("SELECT dateoforder FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    date_of_order = c.fetchone()[0]
    app.search_date_of_order = str(date_of_order)
    c.execute("SELECT deposit FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    customer_deposit = c.fetchone()[0]
    app.search_customer_deposit = str(customer_deposit)
    c.execute("SELECT totalmoneyowed FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    customer_money_owed = c.fetchone()[0]
    app.search_customer_money_owed = str(customer_money_owed)
    c.execute("SELECT deadline FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    customer_deadline = c.fetchone()[0]
    app.search_customer_deadline = str(customer_deadline)
    c.execute("SELECT overallstatus FROM CustomerTable WHERE jobnumber=(?)", (int(app.job),))
    overall_status = c.fetchone()[0]
    app.search_overall_status = str(overall_status)
    app.search_subjob_rows = enki_crud.DBMethods(int(app.job)).subjob_length()
    return

import kivy
kivy.require("1.10.0")
from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'borderless', '0')
Config.set('graphics', 'show_cursor', '1')
Config.set('kivy', 'exit_on_escape', '0')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.scatter import Scatter
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.bubble import Bubble
from kivy.uix.spinner import Spinner
from kivy.uix.spinner import SpinnerOption
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BoundedNumericProperty
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from validate_email import validate_email
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from PIL import Image as I
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from functools import partial
import glob

s = requests.session()
enki_crud.DBMethods(0).donut_plot()
enki_crud.DBMethods(0).delete_duplicate_subjobs()

class Todo(FloatLayout):
    app = App.get_running_app()

    glayout = ObjectProperty(None)
    todo_list = search_for_overall_status("Work In Progress")
    todo_list_rv_root = date_sorter(todo_list)

    waiting_for_collection_list = search_for_overall_status("Waiting for Collection")
    waiting_for_collection = date_sorter(waiting_for_collection_list)

    returned_list_5 = search_for_overall_status("Returned")
    returned = date_sorter(returned_list_5[:20])

    matched_items = []

    logout_cookie_exist = False
    logout_cookie_user = ''


    def __init__(self, **kwargs):
        super(Todo, self).__init__(**kwargs)
        self.glayout.bind(minimum_height=self.glayout.setter('height'))
        Window.bind(mouse_pos=self.mouse_pos)
        self.mouse_icon = Image(id='mouse', source='enki_icon.ico', size_hint_x=None, size_hint_y=None, size=(40, 40))
        self.add_widget(self.mouse_icon)

    def mouse_pos(self, window, pos):
        self.mouse_icon.pos = (pos[0] - 5, pos[1] - 5)

    def compile_add_subjob(self, job_number):
        '''gather data from added job and send it to the relevant job being editted - UPDATE (need function to unpack
        a dictionary and update it to the correct job_number and subjob)'''
        app = App.get_running_app()
        try:
            e = enki_crud.DBMethods(job_number)
            e.take_dict_update_job_in_db(app.edit_subjob_dict)
        except:
            print("ALREADY INSERTED - NEED TO UPDATE")
            pass

    def wrap_update_table(self, job_number, field, new_info, subjob_num):
        '''redirect to original update table function'''
        e = enki_crud.DBMethods(job_number)
        if field == "Actual Cost" or field == "Estimated Cost":
            e.update_table(field, self.edit_add_subjob_format_currency(subjob_num, field, new_info), subjob_num)
        else:
            e.update_table(field, new_info, subjob_num)

    def add_subjob(self):
        '''adds new subjob but nothing changes in database'''
        app = App.get_running_app()
        app.glayout2_rows = app.glayout2_rows + 1
        subjob_num = int(len(self.ids.glayout2.children) + 1)
        self.ids.glayout2.add_widget(EditAddSubJobTable(id=str(subjob_num)))
        # create the relevant dictionary entry here
        app.edit_subjob_dict[subjob_num] = {'Repair/ Commission': '', 'Job Description': '', 'Metal': '', 'Stones': '',
                              'Estimated Cost': '', 'Actual Cost': '',
                              'Status': 'Work In Progress'}
        self.compile_add_subjob(int(app.job))
        self.compile_overall_status(int(app.job))

        app.subjob_tracker = subjob_num
        app.subjob_dict[subjob_num] = {'Repair/ Commission': '', 'Job Description': '', 'Metal': '', 'Stones': '',
                              'Estimated Cost': '', 'Actual Cost': '',
                              'Status': 'Work In Progress'}

    def delete_subjob(self):
        '''delete subjob'''
        app = App.get_running_app()
        subjob_num = len(self.ids.glayout2.children)
        self.ids.glayout2.remove_widget(self.ids.glayout2.children[0]) # subjobtable
        # remove relevant subjob from the dict
        del app.edit_subjob_dict[app.subjob_tracker]
        app.subjob_tracker = app.subjob_tracker -1
        e = enki_crud.DBMethods(int(app.job))
        e.delete_subjob_row(subjob_num)
        self.compile_overall_status(int(app.job))
        app.glayout2_rows = app.glayout2_rows - 1
        # delete last entry in app.subjob_dict
        delete_subjob = len(app.subjob_dict)
        del app.subjob_dict[delete_subjob]
        self.calculate_total_money_owed()

    def create_add_subjob(self):
        '''add subjob but not compiled yet'''
        app = App.get_running_app()
        app.create_num_rows = app.create_num_rows + 1

        subjob_num = len(self.ids.create_subjob.children) + 1
        app.current_subjob = subjob_num
        app.create_subjob_dict[subjob_num] = {'Repair/ Commission': '', 'Job Description': '', 'Metal': '', 'Stones': '',
                               'Estimated Cost': '', 'Actual Cost': '',
                              'Status': 'Work In Progress'}
        self.ids.create_subjob.add_widget(CreateSubJobTable(id=str(subjob_num)))

    def create_delete_subjob(self):
        '''delete subjob'''

        app = App.get_running_app()
        if len(app.create_subjob_dict) > 1:
            del app.create_subjob_dict[len(app.create_subjob_dict)]
        subjob_num = str(len(self.ids.create_subjob.children))
        self.ids.create_subjob.remove_widget(self.ids.create_subjob.children[0])
        app.create_num_rows = app.create_num_rows - 1

    def open_ready(self):
        app = App.get_running_app()
        if app.overall_status == "Waiting for Collection":
            app.ready_email = "Yes"
            return
        else:
            app.ready_email = "No"
            return

    def email_or_not_to_email(self):
        '''SELECT and UPDATE'''
        app = App.get_running_app()
        counter = 1
        e = enki_crud.DBMethods(int(app.job))
        subjob_num = e.subjob_length()
        while counter < subjob_num + 1: # can subjobs for any no charges
            c.execute("SELECT actualcost FROM SubJobTable Where jobnumber=(?) AND subjob=(?)", (int(app.job), counter))
            actual_cost_entry = c.fetchone()[0]
            if actual_cost_entry == "Pending" or "Pending" in app.subjob_dict[counter]['Actual Cost']:
                PendingPop().open()
                return
            elif actual_cost_entry == "£" or app.subjob_dict[counter]['Actual Cost'] == "£":
                ChargeZeroPop().open()
                return
            elif actual_cost_entry == "" or app.subjob_dict[counter]['Actual Cost'] == "":
                ChargeZeroPop().open()
                return
            elif actual_cost_entry == "0" or app.subjob_dict[counter]['Actual Cost'] == "0":
                ChargeZeroPop().open()
                return
            elif actual_cost_entry == "£0" or app.subjob_dict[counter]['Actual Cost'] == "£0":
                ChargeZeroPop().open()
                return
            elif actual_cost_entry == "£.00" or app.subjob_dict[counter]['Actual Cost'] == "£.00":
                ChargeZeroPop().open()
                return
            elif actual_cost_entry == "£0.00" or app.subjob_dict[counter]['Actual Cost'] == "£0.00":
                ChargeZeroPop().open()
                return
            else:
                counter = counter + 1

        app.overall_status = "Waiting for Collection"
        counter2 = 1
        subjob_num = e.subjob_length()
        while counter2 < subjob_num + 1: # following checks assert that all values are now waiting for collection
            app.subjob_dict[counter2]['Status'] = "Waiting for Collection"
            with conn:
                c.execute("UPDATE SubJobTable SET status=(?) WHERE jobnumber=(?) AND subjob=(?)",
                          ("Waiting for Collection", int(app.job), counter2))
            counter2 = counter2 + 1

        Todo.unload_grid(self)
        Todo.reload_data(self)
        self.compile_add_subjob(int(app.job))
        e = enki_core.Enki(int(app.job))
        subjob_list = enki_crud.DBMethods(int(app.job)).subjob_into_list()
        e.generate_pdf(app.customer_name, app.contact_number, app.email_add, date.today().strftime("%d/%m/%y"),
                 app.customer_deposit, app.customer_money_owed, app.customer_deadline, app.overall_status, subjob_list)
        e.delete_pdf()
        move_file()
        cus_name = app.customer_name.split(' ')
        body = "Dear " + str(cus_name[0].title()) + ",\n\n" + "Your order is now ready for collection, please find " + \
            "your invoice attached. This is a no-reply email address, if you have any queries or would like to arrange " + \
            "for someone else to collect your item/s, please contact us:\n\nfaith@enkionline.com" + \
            "\n0121 4444 453\nThanks for your custom.\nEnki."
        subject = "ENKI -- Ready for Collection -- (no reply)"
        if app.email_checked is True:
            e.email(app.email_add, body, subject)
        if app.phone_checked is True:
            phone_body = "Dear " + str(cus_name[0].title()) + ",\n\nYour Enki order is now ready for collection." \
                                                                    "The balance due is: " + app.customer_money_owed +\
                                                                      "\n\nDO NOT reply to this number." \
                                                                      "\nContact us on:" \
                                                                      "\n\n0121 4444 453\n" +"Tues to Sat 10am - 5pm" \
                                                                      "\nThanks for your custom.\nEnki."
            numb = '+44' + app.contact_number[1:]
            try:
                e.send_sms(numb, phone_body)
            except:
                CannotSMS().open()
        self.ids._screen_manager.current = 'main'
        return

    def load_customer_info(self):
        ''' load customer info and behaviours for 'main' button on the edit screen and checks email valid'''
        self.ids.customer_info_layout.add_widget(CustomerLayout(id="custgrid"))
        #clear the appropriate gridlayout
        self.ids.edit_customer_grid_buttons.clear_widgets()
        # create the gridlayout
        app = App.get_running_app()
        app.ready_email = "No"
        Todo.calculate_total_money_owed(self)
        edit_main = BackToMain(
                           size_hint_x=0.5,
                           size_hint_y=None,
                           height=50)
        job_num_lab = Label(size_hint_x=0.5,
                           size_hint_y=None,
                           height=50, text="[b]# " + app.job + "[/b]", text_size=self.size, valign='middle',
                            halign='center', font_size=25, markup=True)

        box1 = BoxLayout(size_hint_x=0.3)
        box2 = BoxLayout()

        overall_stat_lab = Label(size_hint_x=0.5,
                           size_hint_y=None,
                           height=50, text="[b] " + app.overall_status + "[/b]", text_size=self.size, valign='middle',
                            halign='center', font_size=25, markup=True)
        print_but = Print()
        resend_but = ResendNotification()

        #create the button
        # bind it to the button
        self.ids.edit_customer_grid_buttons.add_widget(job_num_lab)
        self.ids.edit_customer_grid_buttons.add_widget(overall_stat_lab)
        box2.add_widget(print_but)
        box2.add_widget(resend_but)
        box2.add_widget(edit_main)
        self.ids.edit_customer_grid_buttons.add_widget(box1)
        self.ids.edit_customer_grid_buttons.add_widget(box2)
        #add the button to the gridlayout
        return

    def load_create_customer_info(self):
        ''' load blank customer form for the create new job screen '''
        app = App.get_running_app()
        self.ids.create_customer_info_layout.clear_widgets()
        self.ids.create_subjob.clear_widgets()
        #edits should already write back to database so don't edit anything to prevent headache

        app.create_repair_commission = "[b] --- select here --- [/b]"
        u = date.today() + timedelta(days=14)
        app.create_deadline = str(u.strftime("%d/%m/%y"))

        c.execute("SELECT jobnumber FROM CustomerTable")
        data = c.fetchall()
        try:
            app.next_job_number = str(max(data)[0] + 1)
        except:
            # the data is empty because there are no jobs
            app.next_job_number = str(1)

        # Whatever is in textInput for the subjob must be written to database, a function to copy all that back

        # have a discard/delete job button to return to main screen without writting any changes back
        self.required_field_validation()
        self.ids.create_customer_info_layout.add_widget(CreateCustomerLayout(id="create_customer"))
        self.ids.create_subjob.add_widget(CreateSubJobTable(id=str(1)))
        #with finalised data send reload the relevant rv.data list and then send it via email

    def compile_create_job(self):
        '''gather all new input and write it all back into a new job, sending it to the correct list also!
        SELECT and UPDATE'''
        app = App.get_running_app()
        job_number = app.next_job_number
        job_number = int(job_number)

        #need to account for multiple subjob a loop for the above as at the minute its only capturing the first subjob
        def treat_create_subjob():
            ''' fill in the blanks for the subjobs that have not been completed'''
            counter = 1
            while counter < len(app.create_subjob_dict) + 1:
                formatted = self.create_subjob_format_currency(counter,
                                                               app.create_subjob_dict[counter]['Estimated Cost'])
                app.create_subjob_dict[counter]['Estimated Cost'] = formatted
                app.create_subjob_dict[counter]['Actual Cost'] = 'Pending'

                with conn:
                    c.execute("""INSERT INTO SubJobTable VALUES((?), (?), (?), (?), (?), (?), (?),
                                        (?), (?))""", (job_number, counter,
                                                       app.create_subjob_dict[counter]['Repair/ Commission'],
                                                       app.create_subjob_dict[counter]['Job Description'],
                                                       app.create_subjob_dict[counter]['Metal'],
                                                       app.create_subjob_dict[counter]['Stones'],
                                                       app.create_subjob_dict[counter]['Estimated Cost'],
                                                       app.create_subjob_dict[counter]['Actual Cost'],
                                                       "Work In Progress"))

                counter = counter + 1

        treat_create_subjob()
        deposit = self.create_customer_format_currency_deposit(app.create_deposit)
        phone_checked = convert_to_integer(app.phone_checked)
        email_checked = convert_to_integer(app.email_checked)

        with conn:
            c.execute("""INSERT INTO CustomerTable VALUES((?), (?), (?), (?),
            (?), (?), (?), (?), (?), (?), (?))""", (job_number, date.today().strftime("%d/%m/%y"), app.create_customer_name,
                                         app.create_contact_number, app.create_email, deposit,
                                         app.create_money_owed, app.create_deadline, "Work In Progress", phone_checked,
                                                    email_checked))

    def create_customer_format_currency_deposit(self, user_edit):

        app = App.get_running_app()

        if '.' in user_edit:
            user_edit = re.sub('£', '', user_edit)
            user_edit = user_edit.split('.', 1)
            format_curren = "£{}.{}".format(user_edit[0], user_edit[1])
            app.create_deposit = format_curren
            return app.create_deposit
        else:

            if user_edit == '':
                format_curren = "£0.00"
                app.create_deposit = format_curren
                return app.create_deposit
            elif user_edit[0] == '£':
                format_currency = re.sub('£', '', user_edit)
                format_curren = "£{}.00".format(format_currency)
                app.create_deposit = format_curren
                return app.create_deposit
            else:
                app.create_deposit = "£{}.00".format(user_edit)
                return app.create_deposit

    def create_subjob_format_currency(self, subjob_num, user_edit):
        app = App.get_running_app()
        if '.' in user_edit:
            user_edit = re.sub('£', '', user_edit)
            user_edit = user_edit.split('.', 1)
            format_curren = "£{}.{}".format(user_edit[0], user_edit[1])
            app.create_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
            return app.create_subjob_dict[subjob_num]['Estimated Cost']

        else:
            if user_edit == '':
                format_curren = "No quote given"
                app.create_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
                return app.create_subjob_dict[subjob_num]['Estimated Cost']
            elif user_edit[0] == '£':
                format_currency = re.sub('£', '', user_edit)
                format_curren = "£{}.00".format(format_currency)
                app.create_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
                return app.create_subjob_dict[subjob_num]['Estimated Cost']
            else:
                format_curren = "£{}.00".format(user_edit)
                app.create_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
                return app.create_subjob_dict[subjob_num]['Estimated Cost']

    def edit_add_subjob_format_currency(self, subjob_num, subjob_field, user_edit):
        app = App.get_running_app()

        if '.' in user_edit:  # if dot
            user_edit = re.sub('£', '', user_edit)
            user_edit = user_edit.split('.', 1)
            format_curren = "£{}.{}".format(user_edit[0], user_edit[1])
            if subjob_field == 'Actual Cost':
                app.edit_subjob_dict[subjob_num]['Actual Cost'] = format_curren
                return app.edit_subjob_dict[subjob_num]['Actual Cost']
            elif subjob_field == 'Estimated Cost':
                app.edit_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
                return app.edit_subjob_dict[subjob_num]['Estimated Cost']

        else:

            if user_edit == '':
                if subjob_field == 'Actual Cost':
                    format_curren  = '£'
                    app.edit_subjob_dict[subjob_num]['Actual Cost'] = format_curren
                    return app.edit_subjob_dict[subjob_num]['Actual Cost']
                elif subjob_field == 'Estimated Cost':
                    format_curren = "No quote given"
                    app.edit_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
                    return app.edit_subjob_dict[subjob_num]['Estimated Cost']

            elif user_edit[0] == '£':
                format_currency = re.sub('£', '', user_edit)
                format_curren = "£{}.00".format(format_currency)
                if subjob_field == 'Actual Cost':
                    app.edit_subjob_dict[subjob_num]['Actual Cost'] = format_curren
                    return app.edit_subjob_dict[subjob_num]['Actual Cost']
                elif subjob_field == 'Estimated Cost':
                    app.edit_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
                    return app.edit_subjob_dict[subjob_num]['Estimated Cost']
            else:
                format_curren = "£{}.00".format(user_edit)
                if subjob_field == 'Actual Cost':
                    app.edit_subjob_dict[subjob_num]['Actual Cost'] = format_curren
                    return app.edit_subjob_dict[subjob_num]['Actual Cost']
                elif subjob_field == 'Estimated Cost':
                    app.edit_subjob_dict[subjob_num]['Estimated Cost'] = format_curren
                    return app.edit_subjob_dict[subjob_num]['Estimated Cost']

    def load_grid(self, sj_num):

        app = App.get_running_app()
        counter = 1
        app.subjob_num = 1
        self.ids.glayout2.add_widget(FirstSubJobTable())

        for n in range(1, sj_num):
            app.glayout2_rows = app.glayout2_rows + 1
            #app.edit_num_rows = app.edit_num_rows + 1
            counter = counter + 1
            app.subjob_num = counter
            self.ids.glayout2.add_widget(SubJobTable(id=str(counter)))
        return counter

    def unload_grid(self):
        app = App.get_running_app()
        self.ids.glayout2.clear_widgets()
        self.ids.customer_info_layout.clear_widgets()
        app.subjob_num = 0
        return

    def compile_temp_dict_entry(self, job_number, subjob_num, subjob_field, user_edit):
        ''' gather all data (user edits in subjobs) and compile the entry to be written to the database
        SELECT and UPDATE'''
        if subjob_field == 'Actual Cost' or subjob_field == 'Estimated Cost':
            if '.' in user_edit:
                user_edit = re.sub('£', '', user_edit)
                user_edit = user_edit.split('.', 1)
                format_curren = "£{}.{}".format(user_edit[0], user_edit[1])
                if subjob_field == 'Actual Cost':
                    with conn:
                        c.execute("UPDATE SubJobTable SET actualcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                  (format_curren, job_number, subjob_num))
                elif subjob_field == 'Estimated Cost':
                    with conn:
                        c.execute("UPDATE SubJobTable SET estimatedcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                  (format_curren, job_number, subjob_num))
            else:
                c.execute("SELECT estimatedcost FROM SubJobTable Where jobnumber=(?) AND subjob=(?)",
                          (job_number, subjob_num))
                estim_cost = c.fetchone()[0]
                c.execute("SELECT actualcost FROM SubJobTable Where jobnumber=(?) AND subjob=(?)",
                          (job_number, subjob_num))
                actual_cost = c.fetchone()[0]

                if estim_cost == '' or actual_cost == '' or user_edit == '':
                    format_curren = "£"

                    if subjob_field == 'Actual Cost':
                        with conn:
                            c.execute("UPDATE SubJobTable SET actualcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                      (format_curren, job_number, subjob_num))
                    elif subjob_field == 'Estimated Cost':
                        with conn:
                            c.execute("UPDATE SubJobTable SET estimatedcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                      (format_curren, job_number, subjob_num))

                elif estim_cost[0] == '£' or actual_cost[0] == "£":
                    format_curren = "£0.00"
                    if subjob_field == 'Actual Cost' and len(actual_cost) == 1:
                        with conn:
                            c.execute("UPDATE SubJobTable SET actualcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                      (format_curren, job_number, subjob_num))
                    elif subjob_field == 'Estimated Cost' and len(estim_cost) == 1:
                        with conn:
                            c.execute("UPDATE SubJobTable SET estimatedcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                      (format_curren, job_number, subjob_num))
                    else:
                        format_currency = re.sub('£', '', user_edit)
                        format_curren = "£{}.00".format(format_currency)
                        if subjob_field == 'Actual Cost':
                            with conn:
                                c.execute("UPDATE SubJobTable SET actualcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                          (format_curren, job_number, subjob_num))
                        elif subjob_field == 'Estimated Cost':
                            with conn:
                                c.execute("UPDATE SubJobTable SET estimatedcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                                          (format_curren, job_number, subjob_num))
        else:
            e = enki_crud.DBMethods(job_number)
            e.update_table(subjob_field, user_edit, subjob_num=subjob_num)
            return

    def compile_customer_info(self, job_number, field, user_edit):
        ''' customer info to be written to the database & treat currency correctly SELECT and UPDATE'''
        if field == 'Deposit':
            if '.' in user_edit:
                user_edit = re.sub('£', '', user_edit)
                user_edit = user_edit.split('.', 1)
                format_curren = "£{}.{}".format(user_edit[0], user_edit[1])
                with conn:
                    c.execute("UPDATE CustomerTable SET deposit=(?) WHERE jobnumber=(?)",
                              (format_curren, job_number))
            else:
                c.execute("SELECT deposit FROM CustomerTable WHERE jobnumber=(?)", (job_number,))
                database_deposit = c.fetchone()[0]
                if database_deposit == '' or user_edit == '':
                    format_curren = "£"
                    with conn:
                        c.execute("UPDATE CustomerTable SET deposit=(?) WHERE jobnumber=(?)",
                                  (format_curren, job_number))

                elif database_deposit[0][0] == '£':
                    format_currency = re.sub('£', '', user_edit)
                    format_curren = "£{}.00".format(format_currency)
                    with conn:
                        c.execute("UPDATE CustomerTable SET deposit=(?) WHERE jobnumber=(?)",
                                  (format_curren, job_number))
        else:
            e = enki_crud.DBMethods(job_number)
            e.update_table(field, user_edit)
            return

    def compile_overall_status(self, job_number):
        ''' compile the overall status every time the status of a subjob changes SELECT and UPDATE'''
        app = App.get_running_app()
        subjob_num = enki_crud.DBMethods(job_number).subjob_length()
        statuses = []
        n = 1
        while n < subjob_num + 1:
            c.execute("SELECT status FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)", (job_number, n))
            subjob_status = c.fetchone()[0]
            statuses.append(subjob_status)
            n = n + 1

        if "Work In Progress" in statuses:
            with conn:
                c.execute("UPDATE CustomerTable SET overallstatus=(?) WHERE jobnumber=(?)", ("Work In Progress",
                                                                                             job_number))
            app.overall_status = "Work In Progress"
            app.ready_email = "No"
            return

        elif "Work In Progress" not in statuses:
            if "Waiting for Collection" in statuses:
                # pop up informs when "main" is hit the customer will be emailed "Ready for Collection"
                # Do you wish to proceed
                with conn:
                    c.execute("UPDATE CustomerTable SET overallstatus=(?) WHERE jobnumber=(?)",
                              ("Waiting for Collection", job_number))
                app.overall_status = "Waiting for Collection"
                app.ready_email = "Yes"
                return
            elif "Waiting for Collection" not in statuses:
                with conn:
                    c.execute("UPDATE CustomerTable SET overallstatus=(?) WHERE jobnumber=(?)",
                              ("Returned", job_number))
                app.overall_status = "Returned"
                app.ready_email = "No"
                return

    def reload_data(self):
        ''' reload the rvs so they display the most up to date lists NEW SEARCH FUNCTION!'''
        Todo.todo_list.clear()
        Todo.todo_list_rv_root.clear()
        Todo.waiting_for_collection_list.clear()
        Todo.waiting_for_collection.clear()
        Todo.returned_list_5.clear()
        Todo.returned.clear()

        Todo.todo_list = search_for_overall_status("Work In Progress")
        Todo.todo_list_rv_root = date_sorter(Todo.todo_list)
        len_todo = len(search_for_overall_status("Work In Progress"))
        self.ids.todo_label_num.text = "[b]" + "To do:      " + str(len_todo) +"[/b]"

        Todo.waiting_for_collection_list = search_for_overall_status("Waiting for Collection")
        Todo.waiting_for_collection = date_sorter(Todo.waiting_for_collection_list)

        Todo.returned_list_5 = search_for_overall_status("Returned")
        Todo.returned = date_sorter(Todo.returned_list_5[:20])

        self.ids.waitingrv.data = [
            {'text': " {} | #{}   {:>20}".format( x[1], x[0], x[2]), 'text_size': self.ids.waitingrv.size,
             'halign': 'center', 'valign': 'center',
             'font_size': self.ids.waitingrv.width * 0.09, 'height': self.ids.waitingrv.height * 0.16} for x in
            Todo.waiting_for_collection]
        self.ids.todorv.data = [
            {'text': " {} | #{}   {:>20}".format( x[1], x[0], x[2]), 'text_size': self.ids.todorv.size, 'halign': 'center',
             'valign': 'center',
             'font_size': self.ids.todorv.width * 0.09, 'height': self.ids.todorv.height * 0.16} for x in
            Todo.todo_list_rv_root]
        self.ids.returnedrv.data = [
            {'text': " {} | #{}   {:>20}".format( x[1], x[0], x[2]), 'text_size': self.ids.returnedrv.size,
             'halign': 'center', 'valign': 'center',
             'font_size': self.ids.returnedrv.width * 0.09, 'height': self.ids.returnedrv.height * 0.16} for x in
            Todo.returned]

        return

    def required_field_validation(self):
        '''ensure a new job cannot be created without the required fields being filled in'''
        app = App.get_running_app()

        create_job_button = create_button(source='create.ico',
                                   size_hint_x=0.5,
                                   size_hint_y=None,
                                   height=50)
        discard_changes = discard_button(source='return.ico', # source='discard_white.ico',
                                 size_hint_x=0.5,
                                 size_hint_y=None,
                                 height=50)

        job_num_lab = Label(size_hint_x=0.5,
                            size_hint_y=None,
                            height=50, text="[b]# " + app.next_job_number + "[/b]", text_size=self.size, valign='middle',
                            halign='center', font_size=25, markup=True)

        box1 = BoxLayout(size_hint_x=0.5)
        box2 = BoxLayout(size_hint_x=0.5)
        box3 = BoxLayout(size_hint_x=0.5)
        box4 = BoxLayout(size_hint_x=0.5)

        overall_stat_lab = Label(size_hint_x=0.5,
                                 size_hint_y=None,
                                 height=50, text="[b]Work in Progress[/b]", text_size=self.size,
                                 valign='middle',
                                 halign='center', font_size=25, markup=True)
        box2.add_widget(job_num_lab)
        box2.add_widget(overall_stat_lab)
        box1.add_widget(create_job_button)
        box1.add_widget(discard_changes)
        box3.add_widget(box4)
        box3.add_widget(box1)
        self.ids.create_customer_grid_buttons.add_widget(box2)
        self.ids.create_customer_grid_buttons.add_widget(box3)
        return

    def create_prompt_confirm(self):
        ''' bahviour to follow create job prompt confirmation'''
        app = App.get_running_app()
        app.what_screen = 'main'
        Todo.compile_create_job(self)  # writing back to file
        Todo.reload_data(self)  # for the rvs
        self.ids.create_customer_grid_buttons.clear_widgets()
        E = enki_core.Enki(int(app.next_job_number))
        subjob_list = enki_crud.DBMethods(int(app.next_job_number)).subjob_into_list()
        E.generate_pdf(app.create_customer_name, app.create_contact_number,
                 app.create_email,
                 date.today().strftime("%d/%m/%y"),
                 app.create_deposit, app.create_money_owed, app.create_deadline, "Work In Progress",
                 subjob_list)
        move_file()
        cus_name = app.create_customer_name.split(' ')
        body = "Dear " + str(cus_name[0].title()) + ",\n\n" + """Attached is your Enki order details.
        This is a no-reply email address, if you have any queries, please contact us:\n\n\n
        \nThanks for your custom.\nEnki.
                                       """
        subject = 'ENKI Order: Job Number: ' + str(app.next_job_number) + " (no reply)"

        if app.email_checked is True:
            E.email(app.create_email, body, subject)
        if app.phone_checked is True:
            phone_body = "Dear " + str(cus_name[0].title()) + ",\n\n" + "Confirmation of your Enki Order. Due for " \
                        "completion " + str(app.create_deadline) + ".\n\nDO NOT REPLY to this number, " \
                        "if you have any queries, please contact us:\n\n\nTues to Sat 10am - 5pm" \
                                                                   "\nThank you for your custom.\nEnki."
            numb = '+44' + app.create_contact_number[1:]
            try:
                E.send_sms(numb, phone_body)
            except:
                CannotSMS().open()

        self.ids._screen_manager.current = 'main'
        app.create_subjob_dict.clear()
        app.create_subjob_dict = {
            1: {'Repair/ Commission': '', 'Job Description': '', 'Metal': '', 'Stones': '',
                'Estimated Cost': '', 'Actual Cost': '',
                'Status': 'Work In Progress'}}
        return

    def calculate_total_money_owed(self):
        ''' add 'actual cost' values from all subjobs and minus 'deposit' '''

        app = App.get_running_app()
        num_subjob = len(app.subjob_dict)
        # str(len(self.ids.glayout2.children)) works out total widgets
        sum_list = []
        counter = 1

        while counter <= num_subjob:
            # loop asserts that no pending or empty strings
            if app.subjob_dict[counter]['Actual Cost'] == 'Pending':
                app.subjob_dict[counter]['Actual Cost'] = re.sub("Pending", '', app.subjob_dict[counter]['Actual Cost'])
            no_pound = re.sub('£', '', app.subjob_dict[counter]['Actual Cost'])
            if no_pound == '':
                no_pound = 00.00
            no_pound = float(no_pound)
            sum_list.append(no_pound) # appends sum to the list without £ sign
            counter = counter + 1

        if app.customer_deposit == 'Pending':
            app.customer_deposit = re.sub("Pending", '', app.customer_deposit)
        no_pound_deposit = re.sub('£', '', app.customer_deposit)
        if no_pound_deposit == '':
            no_pound_deposit = 00.00
        no_pound_deposit = float(no_pound_deposit)
        rounded_total = sum(sum_list)
        rounded_total = "{:.2f}".format(rounded_total - no_pound_deposit)
        app.customer_money_owed = "£" + rounded_total
        return app.customer_money_owed

    def search_all(self, required_item):
        '''return every entry which matches the required item NEW SEARCH FUNCTION and SELECT'''
        if '#' in required_item:
            try:
                unique_items = []
                Todo.matched_items.clear()
                Todo.matched_items = search_everywhere_function(required_item)
                for i in Todo.matched_items:
                    if i not in unique_items:
                        unique_items.append(i)
                self.ids.search_rv.data = [
                    {'text': "{} | #{} {:>20}".format(x[1], x[0], x[2]), 'text_size': self.ids.returnedrv.size,
                     'halign': 'left', 'valign': 'center',
                     'font_size': self.ids.returnedrv.width * 0.09, 'height': self.ids.returnedrv.height * 0.16} for x
                    in
                    unique_items]
            except:

                unique_items = []
                Todo.matched_items.clear()
                self.ids.search_rv.data = [
                    {'text': "{} | #{} {:>20}".format(x[1], x[0], x[2]), 'text_size': self.ids.returnedrv.size,
                     'halign': 'left', 'valign': 'center',
                     'font_size': self.ids.returnedrv.width * 0.09, 'height': self.ids.returnedrv.height * 0.16} for x
                    in
                    unique_items]
        else:

            unique_items = []
            Todo.matched_items.clear()
            Todo.matched_items = search_everywhere_function(required_item.lower())
            Todo.matched_items = search_everywhere_function(required_item.title())

            for i in Todo.matched_items:
                if i not in unique_items:
                    unique_items.append(i)

            self.ids.search_rv.data = [
                {'text': "{} | #{} {:>20}".format(x[1], x[0], x[2]), 'text_size': self.ids.returnedrv.size,
                 'halign': 'left', 'valign': 'center',
                 'font_size': self.ids.returnedrv.width * 0.09, 'height': self.ids.returnedrv.height * 0.16} for x in
                unique_items]

    def add_search_subjobs(self):
        ''' clear then add all the relevant subjob widgets'''
        app = App.get_running_app()
        app.search_subjob_rows = enki_crud.DBMethods(int(app.job)).subjob_length()
        counter = 1
        while counter < app.search_subjob_rows + 1:
            self.ids.search_subjob_grid.add_widget(SearchSubJobTable(id=str(counter)))
            counter = counter + 1

    def clear_search_subjobs(self):
        '''clear all widgets in search subjobs grid'''
        self.ids.search_subjob_grid.clear_widgets()

    def yes_but_charge_zero(self):
        ''' behaviour for charge zero pop up yes button'''
        app = App.get_running_app()
        app.overall_status = "Waiting for Collection"
        counter2 = 1
        e_crud = enki_crud.DBMethods(int(app.job))
        subjob_num = e_crud.subjob_length()
        e = enki_core.Enki(int(app.job))

        while counter2 < subjob_num + 1:
            app.subjob_dict[counter2]['Status'] = "Waiting for Collection"
            with conn:
                c.execute("UPDATE SubJobTable SET status=(?) WHERE jobnumber=(?) AND subjob=(?)",
                          ("Waiting for Collection", int(app.job), counter2))
            counter2 = counter2 + 1
        Todo.unload_grid(self)
        Todo.reload_data(self)
        self.compile_add_subjob(int(app.job))
        subjob_list = enki_crud.DBMethods(int(app.job)).subjob_into_list()
        e.generate_pdf(app.customer_name, app.contact_number, app.email_add, date.today().strftime("%d/%m/%y"),
                 app.customer_deposit, app.customer_money_owed, app.customer_deadline, app.overall_status, subjob_list)
        e.delete_pdf()
        move_file()
        cus_name = app.customer_name.split(' ')
        body = "Dear " + str(cus_name[0].title()) + ",\n\n" + """Your order is now ready for collection,
         please find your invoice attached. This is a no-reply email address, if you have any queries or would like to
         arrange for someone else to collect your item/s, please contact us:\n\n\n
         Thanks for your custom.\nEnki.
                        """
        subject = "ENKI -- Ready for Collection -- (no reply)"
        if app.email_checked is True:
            e.email(app.email_add, body, subject)
        if app.phone_checked is True:
            phone_body = "Dear " + str(cus_name[0].title()) + ",\n\nYour Enki order is now ready for collection." \
                                                                    "The balance due is: " + app.customer_money_owed +\
                                                                      "\n\nDO NOT reply to this number." \
                                                                      "\nContact us on:" \
                                                                      "\n\\n" +"Tues to Sat 10am - 5pm" \
                                                                      "\nThanks for your custom\nEnki."
            numb = '+44' + app.contact_number[1:]
            try:
                e.send_sms(numb, phone_body)
            except:
                CannotSMS().open()
        self.ids._screen_manager.current = 'main'
        return

    def get_email_adds(self):
        ''' grab all the email addresses'''
        app = App.get_running_app()
        c.execute("SELECT email FROM CustomerTable")
        all_emails = c.fetchall()
        email_list = []
        for i in all_emails:
            email_list.append(str(i[0]))
        unique_email_list = []

        for i in email_list:
            if i not in unique_email_list:
                unique_email_list.append(i)

        email_string = ",".join(unique_email_list)
        email_string = re.sub(",", "; ", email_string)
        app.email_string = email_string
        self.ids.text_email_adds.select_all()
        self.ids.text_email_adds.copy(data=app.email_string)
        return app.email_string

    def clean_and_polish_1_year_old(self):
        '''create a date range one year ago and the current month, then match these possible dates with customer
        deadlines - specifically only for commissions '''
        what_day = str(datetime.today().strftime("%A"))
        if what_day == 'Tuesday':
            last_year_today = datetime.today() - relativedelta(years=1)
            last_year_today = last_year_today.strftime("%d/%m/%y").split("/", 1)
            date_matches = search_everywhere_function(str(last_year_today))
            job_matches = []
            for e in date_matches:
                job_matches.append(e[0])
            deadline_matches = []
            commission_matches = []
            for e in job_matches:
                c.execute("SELECT deadline FROM CustomerTable WHERE jobnumber=(?)", (e,))
                cust_deadline = c.fetchone()[0]
                if last_year_today == cust_deadline:
                    deadline_matches.append(e)
                    num_subjob = enki_crud.DBMethods(e).subjob_length()
                    while num_subjob > 0:
                        c.execute("SELECT repaircommission FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)",
                                  (e, num_subjob))
                        is_it_commission = c.fetchone()[0]
                        if is_it_commission == 'Commission':
                            c.execute("SELECT overallstatus FROM CustomerTable WHERE jobnumber=(?)", (e,))
                            commiss_overall_status = c.fetchone()[0]
                            if commiss_overall_status == "Returned":
                                commission_matches.append(e)
                                num_subjob = num_subjob - 1
                            else:
                                num_subjob = num_subjob - 1
                        else:
                            num_subjob = num_subjob - 1

            if len(commission_matches) > 0:
                body_string = ""
                for e in commission_matches:
                    c.execute("SELECT customername FROM CustomerTable WHERE jobnumber=(?)", (e,))
                    cust_name = c.fetchone()[0]
                    body_sub_string = "#" + str(e) + " " + str(cust_name) + "\n"
                    body_string = body_string + body_sub_string
                gmail_user = GMAIL_USER
                gmail_pass = GMAIL_PASSWORD
                clean_and_pol_subj = "CLEAN AND POLISHES DUE: " + str(datetime.today().strftime("%A %d/%m/%y"))
                body = "Hi Faith,\n\nHere are your clean and polishes due this month:\n\n" + body_string
                msg = MIMEMultipart()
                msg['From'] = formataddr(('Enki', GMAIL_USER'))  
                msg['To'] = GMAIL_USER
                msg['Subject'] = clean_and_pol_subj
                msg.attach(MIMEText(body, 'plain'))

                for e in commission_matches:
                    source_path = Path(os.path.realpath(sys.argv[0]))
                    job_sheets_path = Path(source_path.parent / 'job_sheets')
                    file_name = str(e) + '.pdf'
                    filename = Path(job_sheets_path / file_name)
                    attachment = open(filename, 'rb')
                    part = MIMEApplication(attachment.read())
                    part.add_header('Content-Disposition', 'attachment', filename=str(e) + ".pdf")
                    msg.attach(part)
                text = msg.as_string()
                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(gmail_user, gmail_pass)

                    server.sendmail(gmail_user, GMAIL_USER, text)
                    server.quit()
                    print("Email Sent!")
                except:
                    print("Something went wrong...")
            else:
                pass

    def delete_job_number(self):
        '''delete a job and it's related subjobs'''
        app = App.get_running_app()
        with conn:
            c.execute("DELETE FROM CustomerTable WHERE jobnumber=(?)", (app.delete_job_num,))
            c.execute("DELETE FROM SubJobTable WHERE jobnumber=(?)", (app.delete_job_num,))
        self.reload_data()
        try:
            self.ids._screen_manager.current = 'main'
            app.what_screen = 'main'
        except:
            pass

    def logging_in(self):
        ''' POST login data to my API'''
        app = App.get_running_app()
        payload = {'username': app.username, 'passwurd_attempt': app.passwurd_attempt}
        api_url = API_URL
        r = s.post(api_url, data=payload)
        cookies = r.cookies
        try:
            user_payload = {'user_active_sesh': app.username}
            s.post(api_url + 'is_session_active/', user_payload)
            if cookies:
                if Todo.logout_cookie_exist is True and app.username == Todo.logout_cookie_user:
                    self.ids.username_text.text = ''
                    self.ids.passwurd_attempt_text.text = ''
                    self.ids._screen_manager.current = 'login'
                    SessionInvalid().open()
                    rand_wait = random.randrange(1800, 3600)  # wait lasts 30 - 60 mins
                    return Clock.schedule_once(lambda dt: login_wait(), rand_wait)
                for cook in cookies:
                    if cook.name == 'blacklisted':
                        self.ids.username_text.text = ''
                        self.ids.passwurd_attempt_text.text = ''
                        self.ids._screen_manager.current = 'login'
                        return BlackListed().open()
                self.ids._screen_manager.current = 'main'
                Clock.schedule_interval(lambda dt: is_sesh_active(), 300)
            else:
                self.ids.username_text.text = ''
                self.ids.passwurd_attempt_text.text = ''
                self.ids._screen_manager.current = 'login'
                IncorrectCredentials().open()
        except:
            self.ids.username_text.text = ''
            self.ids.passwurd_attempt_text.text = ''
            self.ids._screen_manager.current = 'login'
            CannotConnect().open()

        def is_sesh_active():
            '''run repeatedly every 5 mins to check that sesh is active '''
            api_url_active = 'is_session_active/'
            try:
                logoout_cookie = s.post(api_url + api_url_active, user_payload)
                l_cookie = logoout_cookie.cookies
                if l_cookie:
                    Todo.logout_cookie_exist = True
                    Todo.logout_cookie_user = app.username
                    self.ids.username_text.text = ''
                    self.ids.passwurd_attempt_text.text = ''
                    self.ids._screen_manager.current = 'login'
                    SessionInvalid().open()
                elif cookies:
                    print(cookies)
                else:
                    self.ids.username_text.text = ''
                    self.ids.passwurd_attempt_text.text = ''
                    self.ids._screen_manager.current = 'login'
                    SessionInvalid().open()

            except:
                self.ids.username_text.text = ''
                self.ids.passwurd_attempt_text.text = ''
                self.ids._screen_manager.current = 'login'
                SessionInvalid().open()
            return

        def login_wait():
            '''wait and then log in'''
            Todo.logout_cookie_exist = False
            Todo.logout_cookie_user = ''
            return
        return

    def auto_fill(self, required_item):
        app = App.get_running_app()
        matches = []
        c.execute("SELECT customername FROM CustomerTable")
        all_customers = c.fetchall()

        for cust in all_customers:
            if re.search(required_item, str(cust[0])):
                matches.append(cust[0])
            else:
                app.suggestion_contact_number = ''
                app.suggestion_email = ''
        try:
            c.execute("SELECT jobnumber FROM CustomerTable WHERE customername=(?)", (matches[0],))
            job_number = c.fetchone()[0]
            c.execute("SELECT contactnumber, email FROM CustomerTable WHERE jobnumber=(?)", (job_number,))
            suggestions = c.fetchall()
            app.suggestion_contact_number = suggestions[0][0]
            app.suggestion_email = suggestions[0][1]
        except:
            pass
        try:
            if matches:
                app.suggestion_name = matches[0][len(required_item):]
            else:
                app.suggestion_name = ''
        except:
            pass
        return

    def auto_fill_email(self, required_item):
        app = App.get_running_app()
        matches = []
        c.execute("SELECT email FROM CustomerTable")
        all_email = c.fetchall()

        for cust in all_email:
            if re.search(required_item, str(cust[0])):
                matches.append(cust[0])
            else:
                app.suggestion_contact_number = ''
        try:
            c.execute("SELECT jobnumber FROM CustomerTable WHERE email=(?)", (matches[0],))
            job_number = c.fetchone()[0]
            c.execute("SELECT contactnumber FROM CustomerTable WHERE jobnumber=(?)", (job_number,))
            suggestions = c.fetchall()
            app.suggestion_contact_number = suggestions[0][0]
        except:
            pass
        try:
            if matches:
                app.suggestion_suggestion_email = matches[0][len(required_item):]
            else:
                app.suggestion_suggestion_email = ''
        except:
            pass
        return

    def format_selected_files(self, list):
        formatted_list = list[-3:]
        app = App.get_running_app()
        App.get_running_app().upload_paths.clear()
        App.get_running_app().upload_paths = formatted_list
        def grab_file(dir):
            if os.name == 'nt':
                return str(dir).rsplit("\\", 1)[1]
            else:
                return str(dir).rsplit('/', 1)[1]
        try:
            newest = "[b]Files to upload ({}/3): [/b][i]{}[/i]".format(app.num_existing_img + len(formatted_list),
                                                                       (grab_file(formatted_list[-1])))
            if len(newest) > 60:
                newest = newest[:-28] + "[/i][..]"
        except:
            UploadLimit().open()
            return

        try:
            second = newest + ',[i] ' + str(grab_file(formatted_list[-2])) + "[/i]"
            if len(second) > 90:
               second = second[:-28] + "[/i][..]"
            try:
                final = second + '[i], \n' + str(grab_file(formatted_list[-3])) + "[/i]"
                if len(final) > 120:
                    final = final[:-28] + "[/i][..]"
                return final
            except:
                return second
        except:
            return newest

    def resend_note(self):
        if App.get_running_app().overall_status == "Waiting for Collection":
            resend_notification_collection()
        elif App.get_running_app().overall_status == "Work In Progress":
            resend_notification_todo()
        else:
            pass

    def bubble_behaviour(self):
        self.bub = DeleteBubble(pos=(Window.mouse_pos[0], Window.mouse_pos[1]),
                                arrow_pos='bottom_left')
        self.remove_bubble()

        self.add_widget(self.bub)

    def remove_bubble(self):
        if len(App.get_running_app().root.children) > 1:
            for child in App.get_running_app().root.children:
                #App.get_running_app().root.remove_widget(child)
                pass
        else:
            pass

class RV_Todo(RecycleView): # controller in model-view-controller architechture
    def __init__(self, **kwargs):
        super(RV_Todo, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in Todo.todo_list_rv_root]

class RV_Waiting_For_Collection(RecycleView): # controller in model-view-controller architechture
    def __init__(self, **kwargs):
        super(RV_Waiting_For_Collection, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in Todo.waiting_for_collection]

class RV_Returned(RecycleView): # controller in model-view-controller architechture
    def __init__(self, **kwargs):
        super(RV_Returned, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in Todo.returned]

def discard_create_job(*args):
    app = App.get_running_app()
    app.root.ids.create_customer_grid_buttons.clear_widgets()
    app.root.ids._screen_manager.current = 'main'
    app.what_screen = 'main'
    app.create_subjob_dict.clear()
    app.create_subjob_dict = {1: {'Repair/ Commission': '', 'Job Description': '', 'Metal': '', 'Stones': '',
             'Estimated Due Date': '', 'Deadline': '', 'Estimated Cost': '', 'Actual Cost': '',
             'Status': 'Work In Progress'}}
    app.suggestion_email = ''
    app.suggestion_contact_number = ''
    return

def switchscreen_or_popup(*args):
    # add behaviour to button
    app = App.get_running_app()
    is_valid = validate_email(app.create_email)
    print(is_valid)

    if app.create_customer_name == '':
        MyPopUp().open()
        return
    elif is_valid is None and app.create_email != '':
        EmailInvalid().open()
        return
    elif app.create_repair_commission == "[b] --- select here --- [/b]":
        MyPopUp().open()
        return
    else:
        CreatePrompt().open()
        return

def edit_main_behaviour(*args):
    app = App.get_running_app()
    is_valid = validate_email(app.email_add)

    if is_valid is True and not None or app.email_add == '':
        if len(app.customer_deadline) != 8:
            DateInvalid().open()
        else:
            day, month, year = app.customer_deadline.split('/')
            isValidDate = True

            try:
                date(int(year), int(month), int(year))
            except ValueError:
                isValidDate = False

            if (isValidDate):
                if app.ready_email == "Yes":
                    ReadyForCollection().open()
                    return

                else:
                    app.root.unload_grid()
                    app.root.reload_data()
                    e = enki_core.Enki(int(app.job))
                    subjob_list = enki_crud.DBMethods(int(app.job)).subjob_into_list()
                    e.generate_pdf(app.customer_name, app.contact_number, app.email_add,
                             date.today().strftime("%d/%m/%y"), app.customer_deposit, app.customer_money_owed,
                             app.customer_deadline, app.overall_status, subjob_list)
                    e.delete_pdf()
                    move_file()
                    app.overall_status = "Work In Progress"

                    app.root.ids._screen_manager.current = 'main'
                    app.what_screen = 'main'
                    return
            else:
                DateInvalid().open()
    else:
        EmailInvalid().open()

def resend_notification_collection(*args):
    app = App.get_running_app()
    e = enki_core.Enki(int(app.job))
    cus_name = app.customer_name.split(' ')
    body = "Dear " + str(cus_name[0].title()) + ",\n\n" + "Your order is now ready for collection, please find " + \
           "your invoice attached. This is a no-reply email address, if you have any queries or would like to arrange " + \
           "for someone else to collect your item/s, please contact us:\n\n" + \
           "\\nThanks for your custom.\nEnki."
    subject = "ENKI -- Ready for Collection -- (no reply)"
    if app.email_checked is True:
        e.email(app.email_add, body, subject)
    if app.phone_checked is True:
        phone_body = "Dear " + str(cus_name[0].title()) + ",\n\nYour Enki order is now ready for collection." \
                                                          "The balance due is: " + app.customer_money_owed + \
                     "\n\nDO NOT reply to this number." \
                     "\nContact us on:" \
                     "\n\n\n" + "Tues to Sat 10am - 5pm" \
                                             "\nThanks for your custom.\nEnki."
        numb = '+44' + app.contact_number[1:]
        try:
            e.send_sms(numb, phone_body)
        except:
            CannotSMS().open()

    app.root.unload_grid()
    app.root.reload_data()
    app.root.ids._screen_manager.current = 'main'
    return

def resend_notification_todo(*args):
    app = App.get_running_app()
    E = enki_core.Enki(int(app.job))
    cus_name = app.customer_name.split(' ')
    body = "Dear " + str(cus_name[0].title()) + ",\n\n" + """Attached is your Enki order details.
            This is a no-reply email address, if you have any queries, please contact us:\n\n\n
            Thanks for your custom.\nEnki.
                                           """
    subject = 'ENKI Order: Job Number: ' + str(app.job) + " (no reply)"

    if app.email_checked is True:
        E.email(app.email_add, body, subject)
    if app.phone_checked is True:
        phone_body = "Dear " + str(cus_name[0].title()) + ",\n\n" + "Confirmation of your Enki Order. Due for " \
                                                                    "completion " + str(
            app.customer_deadline) + ".\n\nDO NOT REPLY to this number, " \
                                   "if you have any queries, please contact us:\n\n\nTues to Sat 10am - 5pm" \
                                   "\nThank you for your custom.\nEnki."
        numb = '+44' + app.contact_number[1:]
        try:
            E.send_sms(numb, phone_body)
        except:
            CannotSMS().open()
    app.root.unload_grid()
    app.root.reload_data()
    app.root.ids._screen_manager.current = 'main'
    return

class BackgroundLabel(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(44, 154, 132, 0.25)
            Rectangle(pos=self.pos, size=self.size)

class BackgroundCheckBox(CheckBox):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(44, 154, 132, 0.25)
            Rectangle(pos=self.pos, size=self.size)


class CreateCheckBox(CheckBox):

    def __init__(self, **kwargs):
        super(CreateCheckBox, self).__init__(**kwargs)
        self.active = True

class DeleteButton(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)


    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    App.get_running_app().root.ids._screen_manager.current = 'delete_job'

class AddressButton(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    App.get_running_app().root.ids._screen_manager.current = 'get_email'
                    App.get_running_app().root.get_email_adds()

class CreateButton(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    App.get_running_app().root.ids._screen_manager.current = 'create'
                    App.get_running_app().root.load_create_customer_info()

class AddSubjob(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    App.get_running_app().root.add_subjob()

class DeleteSubjob(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    App.get_running_app().root.delete_subjob()


class CreateDeleteSubjob(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    App.get_running_app().root.create_delete_subjob()

class CreateAddSubjob(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    App.get_running_app().root.create_add_subjob()


class BackToMain(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)


    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    if App.get_running_app().what_screen == "edit":
                        edit_main_behaviour()
                    else:
                        App.get_running_app().what_screen = 'main'
                        App.get_running_app().root.ids._screen_manager.current = 'main'

class ResendNotePopup(Popup):
    pass

class ResendNotification(ButtonBehavior, Image):
    #need a flag to see if collection or creation
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    ResendNotePopup().open()


class Upload(ButtonBehavior, Image):
    SubJob = NumericProperty(0)
    num_existing_images = NumericProperty(0)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)
                    App.get_running_app().current_subjob = self.SubJob
                    App.get_running_app().num_existing_img = self.num_existing_images

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    app = App.get_running_app()
                    if os.name == 'nt':
                        app.home_dir = os.environ["HOMEPATH"]
                    else:
                        app.home_dir = os.environ["HOME"]
                    FileChooser().open()
                    app.touch_flag = False

class Print(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    app = App.get_running_app()
                    enki_core.Enki(app.job).print_pdf()

class discard_button(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    discard_create_job()

class create_button(ButtonBehavior, Image):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    switchscreen_or_popup()

class UploadCancel(Upload):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    App.get_running_app().touch_flag = True
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)
        else:
            App.get_running_app().touch_flag = False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)

class UploadRemove(Upload):
    file_to_remove = StringProperty('')
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    file_name = self.file_to_remove
                    source_path = Path(os.path.realpath(sys.argv[0]))
                    # requires absolute path /home/jaskaran/PycharmProjects/enki
                    dst_path = Path(source_path.parent / "images" / file_name)
                    dst_path.unlink()
                    app = App.get_running_app()
                    if app.what_screen == 'create':
                        app.current_job = int(app.current_job)
                        subjob_num = len(app.create_subjob_dict)
                        n = 1
                        app.root.ids['create_subjob'].clear_widgets()
                        while n <= subjob_num:
                            app.root.ids['create_subjob'].add_widget(CreateSubJobTable(id=str(n)))
                            n += 1
                    else:
                        app.root.unload_grid()
                        e = enki_crud.DBMethods(app.job)
                        app.root.load_grid(e.subjob_length())
                        app.root.load_customer_info()

class UploadPopup(Upload):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x + (self.center_x * 0.005)
                    self.center_y = self.center_y - (self.center_y * 0.005)
                    App.get_running_app().touch_flag = True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                if touch.button == 'left':
                    self.center_x = self.center_x - (self.center_x * 0.005)
                    self.center_y = self.center_y + (self.center_y * 0.005)
                    counter = 0
                    app = App.get_running_app()
                    source_path = Path(os.path.realpath(sys.argv[0]))
                    file_name = str(int(app.current_job)) + '_' + str(app.current_subjob)  # matches any file ending eg .jpg or .png
                    dst_folder = Path(source_path.parent / "images")
                    file_options = ['a', 'b', 'c']
                    if app.num_existing_img > 0:
                        if app.num_existing_img + len(app.upload_paths) > 3:
                            return UploadLimit().open()
                        if app.num_existing_img == 1:
                            #only add 2 images
                            for suffix in file_options:
                                file_suffix = file_name + suffix
                                target = Path(dst_folder / file_suffix)
                                if target.exists():
                                    if suffix == 'a':
                                        counter = 1
                                    elif suffix == 'b':
                                        counter = 2
                                    elif suffix == 'c':
                                        counter = 0

                        elif app.num_existing_img == 2:
                            for suffix in file_options:
                                file_suffix = file_name + suffix
                                target = Path(dst_folder / file_suffix)
                                if target.exists():
                                    if suffix == 'a':
                                        for s in file_options:
                                            file_s = file_name + s
                                            target = Path(dst_folder / file_s)
                                            if target.exists() and s == 'b':
                                                counter = 2
                                            if target.exists() and s == 'c':
                                                counter = 1
                                    elif suffix == 'b':
                                        for s in file_options:
                                            file_s = file_name + s
                                            target = Path(dst_folder / file_s)
                                            if target.exists() and s == 'c':
                                                counter = 0
                            # only add one image
                        elif app.num_existing_img == 3:
                            UploadLimit().open()
                            return
                    for file in app.upload_paths:
                        source_path = Path(os.path.realpath(sys.argv[0]))
                        #requires absolute path /home/jaskaran/PycharmProjects/enki
                        image_to_upload = Path(file)
                        if counter == 0:
                            filename = file_name + 'a'
                            dest_dir = Path(source_path.parent / 'images' / filename)
                            shutil.copy(str(image_to_upload), str(dest_dir))
                            counter += 1
                        elif counter == 1:
                            filename = file_name + 'b'
                            dest_dir = Path(source_path.parent / 'images' / filename)
                            shutil.copy(str(image_to_upload), str(dest_dir))
                            counter += 1
                        elif counter == 2:
                            filename = file_name + 'c'
                            dest_dir = Path(source_path.parent / 'images' / filename)
                            shutil.copy(str(image_to_upload), str(dest_dir))
                            counter = 0
                        else:
                            return
                    app = App.get_running_app()
                    if app.what_screen == 'create':
                        app.current_job = int(app.current_job)
                        subjob_num = len(app.create_subjob_dict)
                        n = 1
                        app.root.ids['create_subjob'].clear_widgets()
                        while n <= subjob_num:
                            app.root.ids['create_subjob'].add_widget(CreateSubJobTable(id=str(n)))
                            n += 1
                    else:
                        app.root.unload_grid()
                        e = enki_crud.DBMethods(app.job)
                        app.root.load_grid(e.subjob_length())
                        app.root.load_customer_info()
                    return

class MyLabel(Label):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            file_name = self.text[9:]
            file_name = file_name.split("[/u][/i][/b]")[0]
            source_path = Path(os.path.realpath(sys.argv[0]))
            dst_folder = Path(source_path.parent / "images")
            target = Path(dst_folder / file_name)
            I.open(target).show() # convert this to windows compatible dir w/ source path etc

class Image_Gallery(GridLayout):

    def __init__(self, **kwargs):
        super(Image_Gallery, self).__init__(**kwargs)
        app = App.get_running_app()
        try:
            app.temp_subjob = app.temp_subjob + 1
            self.cols = 4
            source_path = Path(os.path.realpath(sys.argv[0]))
            file_name = str(int(app.current_job)) + '_' + str(app.temp_subjob) + '*' # matches any file ending eg .jpg or .png
            dst_folder = Path(source_path.parent / "images")
            images = dst_folder.glob(file_name)
            counter = 0
            self.add_widget(Upload(size_hint_x=0.3, size_hint_y=1, SubJob=app.temp_subjob,
                                   num_existing_images=len(list(dst_folder.glob(file_name)))))
            for img in images:
                if os.name == 'nt':
                    img = str(img).rsplit("\\", 1)[1]
                else:
                    img = str(img).rsplit('/', 1)[1]
                box = BoxLayout(orientation='horizontal')
                box.add_widget(MyLabel(text="[b][i][u]" + str(img) + "[/u][/i][/b]", font_size=20, markup=True))
                box.add_widget(UploadRemove(source='cancel.ico', size_hint_x=0.4, size_hint_y=0.4, file_to_remove=img))
                if os.name == 'nt':
                    self.add_widget(box)
                else:
                    self.add_widget(box, index=counter)
                counter += 1
        except:
            print("not trying Image_Gallery...")

class PhoneInput(TextInput):
    ''' numbers and an 11 digit limit'''
    pat = re.compile('([^0-9])') # pattern DO NOT match these characters gets rid of all the rest with re.sub

    def insert_text(self, substring, from_undo=False):
        if len(self.text) == 10:
            self.focus = False
        pat = self.pat
        self.text = self.text[:10]
        s = re.sub(pat, '', substring)
        return super(PhoneInput, self).insert_text(s, from_undo=from_undo)

class MoneyInput(TextInput):
    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)

        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])

        dot = self.text.split('.', 1)  # put into list
        if len(dot) > 1:
            if len(dot[1]) > 0:
                self.focus = False # stop listening to keyboard strokes when 2 decimal places reached
        return super(MoneyInput, self).insert_text(s, from_undo=from_undo)

class AlphabetInput(TextInput):
    pat = re.compile('([^a-zA-Z\s])')

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """ Add support for tab as an 'autocomplete' using the suggestion text.
        """
        app = App.get_running_app()

        if self.suggestion_text and keycode[1] == 'tab' and app.suggestion_name != '':
            self.insert_text(app.suggestion_name)
            self.on_text_validate()
            return True
        if self.suggestion_text and keycode[1] == 'enter' and app.suggestion_name != '':
            self.insert_text(app.suggestion_name)
            self.on_text_validate()
            return True
        return super(AlphabetInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

    def insert_text(self, substring, from_undo=False):
        self.foreground_color = [1, 1, 1, 1]
        pat = self.pat
        s = re.sub(pat, '', substring)
        return super(AlphabetInput, self).insert_text(s, from_undo=from_undo)


    def on_suggestion_text(self, instance, value):
        from kivy.core.text.markup import MarkupLabel
        global MarkupLabel
        cursor_row = self.cursor_row
        if cursor_row >= len(self._lines) or self.canvas is None:
            return

        cursor_pos = self.cursor_pos
        txt = self._lines[cursor_row]

        kw = self._get_line_options()
        rct = self._lines_rects[cursor_row]

        lbl = text = None
        if value:
            app = App.get_running_app()
            lbl = MarkupLabel(
                text=txt + "[b]{}[/b]".format(app.suggestion_name), **kw)
        else:
            lbl = Label(**kw)
            text = txt

        lbl.refresh()

        self._lines_labels[cursor_row] = lbl.texture
        rct.size = lbl.size
        self._update_graphics()
        return super(AlphabetInput, self).on_selection_text(instance, value)


class EmailInput(TextInput):
    ''' Must be one @ symbol followed by some characters a . and some more characters'''
    pat = re.compile('[^\w\.@-_+]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        s = re.sub(pat, '', substring)
        return super(EmailInput, self).insert_text(s, from_undo=from_undo)

    def on_suggestion_text(self, instance, value):
        from kivy.core.text.markup import MarkupLabel
        global MarkupLabel

        cursor_row = self.cursor_row
        if cursor_row >= len(self._lines) or self.canvas is None:
            return

        cursor_pos = self.cursor_pos
        txt = self._lines[cursor_row]

        kw = self._get_line_options()
        rct = self._lines_rects[cursor_row]

        lbl = text = None
        if value:
            app = App.get_running_app()
            lbl = MarkupLabel(
                text=txt + "[b]{}[/b]".format(app.suggestion_suggestion_email), **kw)
        else:
            lbl = Label(**kw)
            text = txt

        lbl.refresh()

        self._lines_labels[cursor_row] = lbl.texture
        rct.size = lbl.size
        self._update_graphics()
        return super(EmailInput, self).on_selection_text(instance, value)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """ Add support for tab as an 'autocomplete' using the suggestion text.
        """
        app = App.get_running_app()
        self.foreground_color = [1, 1, 1, 1]
        if self.suggestion_text and keycode[1] == 'tab' and app.suggestion_suggestion_email != '':
            self.insert_text(app.suggestion_suggestion_email)
            self.on_text_validate()
            return True
        if self.suggestion_text and keycode[1] == 'enter' and app.suggestion_suggestion_email != '':
            self.insert_text(app.suggestion_suggestion_email)
            self.on_text_validate()
            return True
        return super(EmailInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

class DateInput(TextInput):
    ''' add date rules eg. not possible to enter over 31 for relevant months and must enter proper
     date eg. dd/mm/yy'''
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        s = re.sub(pat, '', substring)
        if len(self.text) == 2:
            self.text = self.text + '/'
        if len(self.text) == 5:
            self.text = self.text + '/'
        if len(self.text) == 7:
            self.focus = False

        return super(DateInput, self).insert_text(s, from_undo=from_undo)

class JobDescInput(TextInput):

    def insert_text(self, substring, from_undo=False):
        if len(self.text) == 94:
            self.focus = False
        s = substring[:94]
        return super(JobDescInput, self).insert_text(s, from_undo=from_undo)

class CannotSMS(Popup):
    pass

class PleaseWait(Popup):
    def __init__(self, **kwargs):
        super(PleaseWait, self).__init__(**kwargs)
        self.title = "Please wait, verifying the email address exists..."
        self.size_hint_x = 0.5
        self.size_hint_y = 0.15
        self.title_align = 'center'
        # call dismiss_popup in 10seconds
        Clock.schedule_once(self.dismiss_popup, 8)

    def dismiss_popup(self, dt):
        self.dismiss()

class CannotConnect(Popup):
    pass

class UploadLimit(Popup):
    pass

class FileChooser(Popup):
    def select(self, *args):
        try:
            print(args)
        except:
            pass

class BlackListed(Popup):
    pass

class IncorrectCredentials(Popup):
    pass

class SessionInvalid(Popup):
    pass

class AreYouSure(Popup):
    pass

class ChargeZeroPop(Popup):
    pass

class PendingPop(Popup):
    pass

class CreatePrompt(Popup):
    pass

class DateInvalid(Popup):
    pass

class EmailInvalid(Popup):
    pass

class ReadyForCollection(Popup):
    pass

class MyPopUp(Popup):
    pass

class CustomerLayout(GridLayout):
    pass

class FirstSubJobTable(GridLayout):
    pass

class EditAddSubJobTable(GridLayout):
    pass

class CreateCustomerLayout(GridLayout):
    pass

class CreateSubJobTable(GridLayout):
    pass

class SearchSubJobTable(GridLayout):
    pass

class SubJobTable(GridLayout):
    pass

class Login(Screen):
    pass

class Delete_Job(Screen):
    pass

class Get_email(Screen):
    pass

class Search(Screen):
    pass

class Edit(Screen):
    pass

class Create(Screen):
    pass

class Main(Screen):
    pass

class MyScreenManager(ScreenManager):
    pass

class DeleteBubble(Bubble):
    pass

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout): # view in model-view-controller architechture
    ''' Adds selection and focus behaviour to the view. '''

class SelectableLabel(RecycleDataViewBehavior, Label): # optional base class for data views (RecycleView.viewclass)
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            app = App.get_running_app()
            y = rv.data[index]['text']
            regex_job_number = y.split('#', 1)
            regex_job_number = str(regex_job_number[1])
            regex_job_number = re.sub('\d\d/\d\d/\d\d', '', regex_job_number)
            regex_job_number = re.sub('\s*\D*', '', regex_job_number)
            app.job = regex_job_number
            if app.what_screen == 'search':
                set_search_customer_fields()
            regex_job_number = int(regex_job_number)
            self.e = enki_crud.DBMethods(regex_job_number)
        else:
            print("selection removed for {0}".format(rv.data[index]))

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''

        if super(SelectableLabel, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos) and self.selectable:
            if touch.is_double_tap and touch.button == 'left':
                Clock.schedule_once(self.switch_it, 0.1) # 0.1 second wait
                self.e.edit()
                # self.double is being returned as true here good. which also means it is
                # checking self.double  before "false_it" method has time to change self.double back to
                # false
                return True
            if touch.button == 'right':
                App.get_running_app().root.bubble_behaviour()
            if touch.button == 'left':
                if len(App.get_running_app().root.children) > 1:
                    for child in App.get_running_app().root.children:
                        App.get_running_app().root.remove_widget(child)

            return self.parent.select_with_touch(self.index, touch)

    def switch_it(self, *args):
        app = App.get_running_app()
        app.root.ids._screen_manager.current = 'edit'
        app.what_screen = 'edit'
        return

class EnkiBox_1_7App(App):
    title = "JobSpeed -- Enki"
    icon = "enki_icon.ico"

    username = StringProperty('')
    passwurd_attempt = StringProperty('')
    session_cookie = StringProperty('')

    num_todo = str(len(Todo.todo_list))

    delete_job_num = NumericProperty

    create_repair_commission = StringProperty("[b] --- select here --- [/b]")
    create_customer_name = StringProperty('')
    create_contact_number = StringProperty('')
    create_email = StringProperty('')
    create_deposit = StringProperty('')
    create_deadline = StringProperty('')
    create_money_owed = StringProperty('Pending')

    create_subjob_dict = {1: {'Repair/ Commission': '', 'Job Description': '', 'Metal': '', 'Stones': '',
                     'Estimated Cost': '', 'Actual Cost': '',
                     'Status': 'Work In Progress'}}
    suggestion_name = StringProperty('')
    suggestion_contact_number = StringProperty('')
    suggestion_email = StringProperty('')
    suggestion_suggestion_email = StringProperty('')


    edit_subjob_dict = {}
    subjob_tracker = 0

    job = StringProperty('')
    next_job_number = StringProperty('')
    customer_name = StringProperty('')
    contact_number = StringProperty('')
    email_add = StringProperty('')
    date_of_order = StringProperty('')
    customer_deposit = StringProperty('')
    customer_money_owed = StringProperty('')
    customer_deadline = StringProperty('')
    overall_status = StringProperty('')
    email_checked = BooleanProperty(True)
    phone_checked = BooleanProperty(False)

    search_date_of_order = StringProperty('')
    search_customer_name = StringProperty('')
    search_contact_number = StringProperty('')
    search_email_add = StringProperty('')
    search_customer_deposit = StringProperty('')
    search_customer_money_owed = StringProperty('')
    search_customer_deadline = StringProperty('')
    search_overall_status = StringProperty('')
    search_subjob_rows = NumericProperty(1)
    search_subjob_dict = {1: {'Repair/ Commission': '', 'Job Description': '', 'Metal': '', 'Stones': '',
                     'Estimated Cost': '', 'Actual Cost': '',
                     'Status': 'Work In Progress'}}


    subjob_dict = {}
    subjob_num = NumericProperty
    glayout2_rows = NumericProperty(1)
    num_rows = BoundedNumericProperty(1, min=1)
    create_num_rows = BoundedNumericProperty(1)
    create_main_rows = NumericProperty(4)
    edit_num_rows = BoundedNumericProperty(4)

    ready_email = StringProperty('No')
    what_screen = StringProperty('main')
    email_string = StringProperty('')
    home_dir = StringProperty('')
    touch_flag = BooleanProperty(False)
    upload_paths = []
    current_subjob = NumericProperty(0)
    num_existing_img = NumericProperty(0)
    current_job = NumericProperty(0)

    temp_subjob = BoundedNumericProperty(0, min=0)

    def load_mouse_icon(*args):
        print(args) #(<__main__.EnkiBox_1_7App object at 0x7f414a117388>,)
        mouse_icon = Image(id='mouse', source='enki_icon.ico', size_hint_x=None, size_hint_y=None,
                           size=(40, 40))

        def mouse_pos(window, pos):
            mouse_icon.pos = (pos[0] - 5, pos[1] - 5)

        Window.bind(mouse_pos=mouse_pos)

        App.get_running_app().root.add_widget(mouse_icon)

    def build(self):
        enki_core.Enki(0).daily_backup()
        Todo.clean_and_polish_1_year_old(self)
        return Todo()

EnkiBox_1_7App().run()
conn.commit()
c.close()
conn.close()

# white lines seperating tray
# new fonts
# change background
# get rid of black selectable label.... work on how it behaves
# make cursor into feather (just hide it and display a kivy image to the cursor position
# look at the cursor module for how to do that, and at the config for how to hide the native cursor)
# figure out how to have cursor over popups and spinners
# check out the glitch with adding and removing subjobs in the CREATE
# add feather icon over selectable labels
# add icon to widgets....
# make remove_bubble remove the bubble again
# enki_icon not being added to the Windows window.... revert back to the old way of inserting the icon....
# matplotlib doesn't seem to work when compiling with PyInstaller on Windows look into this
