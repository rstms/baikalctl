# baikalctl client

import re

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

MIN_PASSWD_LEN = 8


class Client:
    def __init__(self):
        pass

    def startup(self, url, username, password, address, port, log_level):
        self.client = False
        self.url = url
        self.username = username
        self.password = password
        self.address = address
        self.port = port
        self.log_level = log_level
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=options)
        self.logged_in = False

    def shutdown(self):
        if self.logged_in:
            self._logout()
        self.driver.quit()

    def _login(self):
        if self.logged_in:
            return
        self.driver.get(self.url + "/admin/")
        username_text = self.driver.find_element(by=By.ID, value="login")
        password_text = self.driver.find_element(by=By.ID, value="password")
        authenticate_button = self.driver.find_element(by=By.TAG_NAME, value="button")
        if authenticate_button.text != "Authenticate":
            return dict(error="failed to find Authenticate button")
        username_text.clear()
        username_text.send_keys(self.username)
        password_text.clear()
        password_text.send_keys(self.password)
        authenticate_button.click()
        self.logged_in = True

    def _logout(self):
        if self.logged_in:
            self.driver.get(self.url + "/admin/")
            self.driver.find_element(by=By.LINK_TEXT, value="Logout").click()
            self.logged_in = False

    def _select_user_page(self):
        self.driver.get(self.url + "/admin/")
        users_menu = self.driver.find_element(by=By.LINK_TEXT, value="Users and resources")
        users_menu.click()

    def _parse_user_col(self, element):
        name, _, tail = element.text.partition("\n")
        display, _, email = tail.partition(" <")
        email = email.strip(">")
        return name, display, email

    def _parse_response(self, response):
        response.raise_for_status()
        return response.json()

    def list_users(self):
        if self.client:
            return self._parse_response(requests.get(f"{self.url}/users/"))
        self._login()
        self._select_user_page()
        users_cols = self.driver.find_elements(by=By.CLASS_NAME, value="col-username")
        ret = {}
        for col in users_cols:
            username, displayname, email = self._parse_user_col(col)
            ret[username] = dict(display_name=displayname, email=email)
        return ret

    def _set_text(self, by, value, text):
        element = self.driver.find_element(by=by, value=value)
        element.clear()
        element.send_keys(text)

    def _validate_name(self, text):
        if not re.match("^[a-zA-Z][a-zA-Z0-9@_-]*$", text):
            return dict(error=f"illegal characters in: '{text}'")
        return None

    def _validate_description(self, text):
        if not re.match("^[a-zA-Z][a-zA-Z0-9@_ -]*$", text):
            return dict(error=f"illegal characters in: '{text}'")
        return None

    def _validate_email(self, text):
        if not re.match("^[a-z][a-z0-9-]*@[a-z][a-z0-9\\.]*\\.[a-z][a-z]*$", text):
            return dict(error=f"illegal characters in: '{text}'")
        return None

    def _validate_password(self, text):
        if len(text) < MIN_PASSWD_LEN:
            return dict(error=f"password too short; minimum={MIN_PASSWD_LEN}")
        return None

    def add_user(self, username, displayname, password):
        err = self._validate_email(username)
        if err:
            return err
        err = self._validate_description(displayname)
        if err:
            return err
        err = self._validate_password(password)
        if err:
            return err
        if self.client:
            return self._parse_response(
                requests.post(
                    self.url + "/user/", data=dict(username=username, displayname=displayname, password=password)
                )
            )
        self._login()
        self._select_user_page()
        add_user_button = self.driver.find_element(by=By.LINK_TEXT, value="+ Add user")
        add_user_button.click()
        self._set_text(By.NAME, "data[username]", username)
        self._set_text(By.NAME, "data[displayname]", displayname)
        self._set_text(By.NAME, "data[email]", username)
        self._set_text(By.NAME, "data[password]", password)
        self._set_text(By.NAME, "data[passwordconfirm]", password)
        save_changes_button = [
            b for b in self.driver.find_elements(By.CLASS_NAME, "btn-primary") if b.text == "Save changes"
        ][0]
        save_changes_button.click()
        return dict(added_user=username)

    def _find_user_column(self, username):
        self._login()
        self._select_user_page()
        table = self.driver.find_element(By.CLASS_NAME, "users")
        users_cols = table.find_elements(by=By.CLASS_NAME, value="col-username")
        for i, col in enumerate(users_cols):
            name, display, email = self._parse_user_col(col)
            if name == username:
                return i, table, col, None
        return -1, None, None, dict(error=f"not found: '{username}'")

    def delete_user(self, username):
        if self.client:
            return self._parse_response(requests.delete(f"{self.url}/user/{username}/"))
        i, table, col, err = self._find_user_column(username)
        if err:
            return err
        table.find_elements(By.CLASS_NAME, "col-actions")[i].find_element(By.LINK_TEXT, "Delete").click()
        buttons = self.driver.find_elements(By.CLASS_NAME, "btn-danger")
        for button in buttons:
            if button.text == "Delete " + username:
                button.click()
                return dict(deleted_user=username)
        return dict(error="not found: '{username}'")

    def list_address_books(self, username):
        if self.client:
            return self._parse_response(requests.get(f"{self.url}/addressbooks/{username}/"))
        i, table, col, err = self._find_user_column(username)
        if err:
            return err
        table.find_elements(By.CLASS_NAME, "col-actions")[i].find_element(By.LINK_TEXT, "Address Books").click()
        names = self.driver.find_elements(By.CLASS_NAME, "col-displayname")
        contacts = self.driver.find_elements(By.CLASS_NAME, "col-contacts")
        descriptions = self.driver.find_elements(By.CLASS_NAME, "col-description")
        books = {}
        for i, name in enumerate(names):
            books[name.text] = dict(contacts=int(contacts[i].text), description=descriptions[i].text)
        return books

    def add_address_book(self, username, name, description):
        err = self._validate_email(username)
        if err:
            return err
        err = self._validate_description(name)
        if err:
            return err
        err = self._validate_description(description)
        if err:
            return err
        if self.client:
            return self._parse_response(
                requests.post(
                    self.url + "/addressbook/", data=dict(username=username, bookname=name, description=description)
                )
            )
        token = name + " " + description
        token = token.replace(" ", "-")
        i, table, col, err = self._find_user_column(username)
        if err:
            return err
        table.find_elements(By.CLASS_NAME, "col-actions")[i].find_element(By.LINK_TEXT, "Address Books").click()
        self.driver.find_element(by=By.LINK_TEXT, value="+ Add address book").click()
        self._set_text(By.NAME, "data[uri]", token)
        self._set_text(By.NAME, "data[displayname]", name)
        self._set_text(By.NAME, "data[description]", description)
        save_changes_button = [
            b for b in self.driver.find_elements(By.CLASS_NAME, "btn-primary") if b.text == "Save changes"
        ][0]
        save_changes_button.click()
        return dict(added_address_book=name)

    def delete_address_book(self, username, name):
        if self.client:
            return self._parse_response(requests.delete(f"{self.url}/addressbook/{username}/{name}/"))
        i, table, col, err = self._find_user_column(username)
        if err:
            return err
        table.find_elements(By.CLASS_NAME, "col-actions")[i].find_element(By.LINK_TEXT, "Address Books").click()
        names = self.driver.find_elements(By.CLASS_NAME, "col-displayname")
        buttons = self.driver.find_elements(By.CLASS_NAME, "btn-danger")
        for j, button in enumerate(buttons):
            if names[j].text == name:
                button.click()
                for b in self.driver.find_elements(By.CLASS_NAME, "btn-danger"):
                    if b.text == "Delete " + name:
                        b.click()
                        return dict(deleted_address_book=name)
        return dict(error=f"not found: '{name}'")

    def reset(self):
        if self.client:
            return self._parse_response(requests.post(f"{self.url}/reset/"))
        self.shutdown()
        self.startup(baikal.url, baikal.username, baikal.password, baikal.address, baikal.port, baikal.log_level)
        return dict(message="server reset")


baikal = Client()
