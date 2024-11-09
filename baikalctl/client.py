# baikalctl client

import re

from selenium import webdriver
from selenium.webdriver.common.by import By

MIN_PASSWD_LEN = 8


class Client:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=options)
        #self.driver.implicitly_wait(1)
        self.logged_in = False

    def close(self):
        if self.logged_in:
            self.logout()
        self.driver.quit()

    def login(self):
        if self.logged_in:
            return
        self.driver.get(self.url + "/admin/")
        username_text = self.driver.find_element(by=By.ID, value="login")
        password_text = self.driver.find_element(by=By.ID, value="password")
        authenticate_button = self.driver.find_element(by=By.TAG_NAME, value="button")
        if authenticate_button.text != "Authenticate":
            raise RuntimeError("failed to find Authenticate button")
        username_text.clear()
        username_text.send_keys(self.username)
        password_text.clear()
        password_text.send_keys(self.password)
        authenticate_button.click()
        self.logged_in = True

    def logout(self):
        if self.logged_in:
            self.driver.get(self.url + "/admin/")
            self.driver.find_element(by=By.LINK_TEXT, value="Logout").click()
            self.logged_in = False

    def select_user_page(self):
        users_menu = self.driver.find_element(by=By.LINK_TEXT, value="Users and resources")
        users_menu.click()

    def _parse_user_col(self, element):
        name, _, tail = element.text.partition("\n")
        display, _, email = tail.partition(" <")
        email = email.strip(">")
        return name, display, email

    def list_users(self):
        self.login()
        self.select_user_page()
        users_cols = self.driver.find_elements(by=By.CLASS_NAME, value="col-username")
        ret = []
        for col in users_cols:
            username, displayname, email = self._parse_user_col(col)
            ret.append(dict(name=username, display_name=displayname, email=email))
        return ret

    def _set_text(self, by, value, text):
        element = self.driver.find_element(by=by, value=value)
        element.clear()
        element.send_keys(text)

    def _validate_name(self, text):
        if not re.match("^[a-zA-Z][a-zA-Z0-9@_-]*$", text):
            raise RuntimeError(f"illegal characters in: '{text}'")

    def _validate_description(self, text):
        if not re.match("^[a-zA-Z][a-zA-Z0-9@_ -]*$", text):
            raise RuntimeError(f"illegal characters in: '{text}'")

    def _validate_email(self, text):
        if not re.match("^[a-z][a-z0-9-]*@[a-z][a-z0-9\\.]*\\.[a-z][a-z]*$", text):
            raise RuntimeError(f"illegal characters in: '{text}'")

    def _validate_password(self, text):
        if len(text) < MIN_PASSWD_LEN:
            raise RuntimeError(f"password too short; minimum={MIN_PASSWD_LEN}")

    def add_user(self, username, displayname, password):
        self._validate_email(username)
        self._validate_description(displayname)
        self._validate_password(password)
        self.login()
        self.select_user_page()
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
        self.login()
        self.select_user_page()
        table = self.driver.find_element(By.CLASS_NAME, "users")
        users_cols = table.find_elements(by=By.CLASS_NAME, value="col-username")
        for i, col in enumerate(users_cols):
            name, display, email = self._parse_user_col(col)
            if name == username:
                print(f"found user {username} index={i}")
                return i, table, col
        raise RuntimeError(f"not found: '{username}'")

    def delete_user(self, username):
        print(f"deleting user: {username}")
        i, table, col = self._find_user_column(username)
        table.find_elements(By.CLASS_NAME, "col-actions")[i].find_element(By.LINK_TEXT, "Delete").click()
        buttons = self.driver.find_elements(By.CLASS_NAME, "btn-danger")
        for button in buttons:
            if button.text == "Delete " + username:
                button.click()
                return dict(deleted_user=username)
        raise RuntimeError("not found: '{username}'")

    def list_address_books(self, username):
        i, table, col = self._find_user_column(username)
        table.find_elements(By.CLASS_NAME, "col-actions")[i].find_element(By.LINK_TEXT, "Address Books").click()
        names = self.driver.find_elements(By.CLASS_NAME, "col-displayname")
        contacts = self.driver.find_elements(By.CLASS_NAME, "col-contacts")
        descriptions = self.driver.find_elements(By.CLASS_NAME, "col-description")
        books = []
        for i, name in enumerate(names):
            books.append(dict(name=name.text, contacts=int(contacts[i].text), description=descriptions[i].text))
        return books


    def add_address_book(self, username, name, description):
        self._validate_email(username)
        self._validate_description(name)
        self._validate_description(description)
        token = name + " " + description
        token = token.replace(" ", "-")
        i, table, col = self._find_user_column(username)
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
        i, table, col = self._find_user_column(username)
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
        raise RuntimeError(f"not found: '{name}'")
