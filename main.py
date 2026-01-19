# Import kivy libraries
import kivy
import kivymd
from kivy.app import App
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, CardTransition, WipeTransition
from kivymd.app import MDApp
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDDatePicker, MDColorPicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton, MDRoundFlatIconButton, MDRectangleFlatIconButton, \
    MDIconButton, MDFloatingActionButton
from kivymd.material_resources import dp
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.config import Config
from kivymd.uix.textfield import MDTextField
from kivymd.uix.tab import MDTabsBase
from kivy.clock import Clock

# Import other libraries
from plyer import notification
from datetime import datetime


# Set window configurations. Default (262.5, 555)
Config.set('graphics', 'resizable', False)
Window.size = (315, 640)

# Global variables
item_list = []  # Justification: Main list storing food items that must be accessed from many parts of the program
food_list = None  # Justification: ID containing the


# Main menu screen of the program with buttons leading to all the main screens.
class Menu(MDScreen):
    # Method changes widget's icon and colour depending on whether dark or light mode has been selected
    # Source: https://kivymd.readthedocs.io/en/1.1.1/themes/icon-definitions/index.html#module-kivymd.icon_definitions
    def on_mode_button_release(self, widget):
        # Execute while light mode is on
        if widget.icon == "weather-sunny":
            widget.icon = "weather-night"
            # widget.icon_color = "#ffffff"  # All white

        # Execute while dark mode is on
        else:
            widget.icon = "weather-sunny"
            # widget.icon_color = "#000000"  # All black

    # Store information in lists within text files upon clicking the close button
    def on_power_button_release(self):
        # Open "FoodList.txt" in write mode
        with open("FoodList.txt", "w") as outFile:
            # Loop through every item currently in the item_list
            for outLine in item_list:
                # Format the arrays to get rid of unnecessary brackets and spaces and write to the file
                print(",".join(str(e) for e in outLine) + "\n")
                outFile.write(",".join(str(e) for e in outLine) + "\n")

        # Open "SettingsFile.txt" in write mode
        with open("SettingsFile.txt", "w") as outFile:
            # Write the current theme colour on the first line of file
            print(str(App.get_running_app().theme_cls.primary_palette))
            outFile.write(str(App.get_running_app().theme_cls.primary_palette) + "\n")
            # Write the notifications settings on the second line of file
            outFile.write(str(App.get_running_app().notif_enabled) + "," + str(App.get_running_app().notif_limit))
            # Loop through every category and write the

        exit()

    # Changes the label beneath the option swiper depending on the option in focus
    def update_swiper_label(self):

        # Notifications option text
        if self.ids.menu_swiper.get_current_item().children[0].text == "Notifications":
            self.ids.swiper_label.text = "See pending notifications"
        # Settings option text
        elif self.ids.menu_swiper.get_current_item().children[0].text == "Settings":
            self.ids.swiper_label.text = "Customize user interface"
        # Catalog option text
        else:
            self.ids.swiper_label.text = "View, add, edit, or delete food items"


class Catalog(MDScreen):
    def on_pre_enter(self, *args):
        # Access the food_list widget using the ids dictionary
        global food_list
        food_list = self.ids.food_list

        # Set toggle buttons to off on entry into screen
        delete_button = self.ids.delete_button
        delete_button.state = "normal"
        edit_button = self.ids.edit_button
        edit_button.state = "normal"


# Screen that allows adjustment of notification options
class NotificationsScreen(MDScreen):
    pass


class SettingsScreen(MDScreen):
    pass


# Allows for creation of custom categories. Future development.
class CategoryInputTab(MDBoxLayout):
    categoryList = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(20), dp(20), dp(20), 0]
        self.spacing = dp(10)

        add_button = MDFlatButton(text="Add Category",
                                  pos_hint={"center_x": 0.5},
                                  theme_text_color="Custom",
                                  text_color="white",
                                  md_bg_color=App.get_running_app().theme_cls.primary_color)
        add_button.bind(on_release=self.add_category)
        self.add_widget(add_button)

    # Adds category to the screen
    def add_category(self, *args):
        category_layout = MDBoxLayout(size_hint_y=None, height=dp(48))
        category_textfield = MDTextField(hint_text="Category")
        category_layout.add_widget(category_textfield)

        color_picker = MDIconButton(icon="palette")
        color_picker.bind(on_release=lambda *args: self.open_color_picker(category_textfield))
        category_layout.add_widget(color_picker)

        delete_button = MDIconButton(icon="trash-can")
        delete_button.bind(on_release=lambda *args: self.remove_category(category_layout))
        category_layout.add_widget(delete_button)

        self.add_widget(category_layout)

    def open_color_picker(self, textfield):
        color_picker = MDColorPicker()
        color_picker.bind(on_color=self.set_category_color)
        color_picker.open()

        # Store a reference to the textfield to update its color later
        self.color_picker_textfield = textfield

    def set_category_color(self, color):
        textfield = self.color_picker_textfield
        textfield.background_color = color
        self.color_picker_textfield = None

        # Update the categoryList with the new color
        for category in self.categoryList:
            if category[0] == textfield:
                category[1] = color

    def remove_category(self, category_layout):
        # Remove the category from the categoryList
        for category in self.categoryList:
            if category_layout.children[0] == category[0]:
                self.categoryList.remove(category)
                break

        self.remove_widget(category_layout)

    def on_categoryList(self, instance, value):
        # Clear the existing categories
        self.clear_widgets()

        # Add the categories from the categoryList
        for category, color in self.categoryList:
            category_layout = MDBoxLayout(size_hint_y=None, height=dp(48))

            category_textfield = MDTextField(hint_text="Category")
            category_textfield.text = category.text
            category_textfield.background_color = color
            category_layout.add_widget(category_textfield)

            color_picker = MDIconButton(icon="palette")
            color_picker.bind(on_release=lambda *args, textfield=category_textfield: self.open_color_picker(textfield))
            category_layout.add_widget(color_picker)

            delete_button = MDIconButton(icon="trash-can")
            delete_button.bind(on_release=lambda *args, layout=category_layout: self.remove_category(layout))
            category_layout.add_widget(delete_button)

            self.add_widget(category_layout)


class EditToggleButton(MDRoundFlatIconButton, MDToggleButton):
    edit_enabled = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_down = self.theme_cls.primary_color

    def on_toggle_button(self, widget):
        if EditToggleButton.edit_enabled is True:
            EditToggleButton.edit_enabled = False
        else:
            EditToggleButton.edit_enabled is False
            EditToggleButton.edit_enabled = True


class DeleteToggleButton(MDRoundFlatIconButton, MDToggleButton):
    del_enabled = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_down = "red"

    def on_pre_enter(self, *args):
        button = self.ids['delete']
        print(button)

    def on_toggle_button(self, widget):
        if DeleteToggleButton.del_enabled is True:
            DeleteToggleButton.del_enabled = False
        else:
            DeleteToggleButton.del_enabled is False
            DeleteToggleButton.del_enabled = True


class FoodInputScreen(MDScreen):
    dialog = None  # Sets the initial popup dialogue to none which all the instances can access

    # Checks the validity of each of the input parameters
    def add_item(self, widget, name, category, date, quantity):
        name = name.strip()
        category = category.strip()
        quantity = quantity.strip()
        date = date.strip()

        # Checks that the food name is not empty nor a string of digits
        if name == "" or name.isdigit():
            self.show_alert_dialog("Check your food name again.")
            return
        elif len(name) > 12:
            self.show_alert_dialog("Food name is too long.")
            return
        # Checks that the category is not empty nor a string of digits
        elif category == "" or category.isdigit():
            self.show_alert_dialog("Check your category label again.")
            return
        elif len(category) > 12:
            self.show_alert_dialog("Category label is too long.")
            return
        # Checks that the quantity is an integer between 1 and 10, inclusive
        elif quantity.isdigit() is False or int(quantity) == 0:
            self.show_alert_dialog("Input quantity must be a positive integer 1 or greater.")
            return
        elif int(quantity) > 10:
            self.show_alert_dialog("Cannot add more than 10 items at any given time.")
            return

        # Checks whether a valid date is chosen
        try:
            datetime.strptime(date, "%m/%d/%Y")
        except ValueError:
            self.show_alert_dialog("Chosen date is invalid.")
            return

        global item_list
        new_item = [name, category, date]
        for i in range(int(quantity)):
            item_list.insert(0, new_item)
        food_list.display(item_list, 2)
        widget.parent.parent.parent.parent.parent.manager.return_to("catalog")

    # Display the alert dialog depending on the error
    def show_alert_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Improper Input",
                text=message,
                buttons=[MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss()
                )
                ],
            )

        else:
            self.dialog.text = message
            self.dialog.buttons = [MDFlatButton(
                text="OK",
                theme_text_color="Custom",
                text_color=App.get_running_app().theme_cls.primary_color,
                on_release=lambda x: self.dialog.dismiss()
            )]

        self.dialog.open()


# The food editing screen accessed through the EditToggleButton widget.
class EditScreen(MDScreen):
    box = None
    row = None

    def del_and_edit(self):
        self.food_list = food_list
        self.food_list.delete(EditScreen.box, EditScreen.row)


# Palette selection screen. Code in kv file.
class ThemeSelect(MDScreen):
    pass


# Controls the connections between program screens
class WindowManager(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = FadeTransition()

    def return_to(self, screen):
        self.current = screen
        self.transition.direction = "right"


# The top header of the food list. Includes "Name", "Category", and "Expiry Date" buttons with sorting capabilities
class CategoryColumns(MDBoxLayout):
    pass


# The display of the food list inside the Catalog screen
class FoodList(MDBoxLayout):
    # Load stored data in file
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        # Open "FoodList.txt" in read mode
        with open("FoodList.txt") as itemFile:
            # Read and separate the lines
            global item_list
            item_list = itemFile.readlines()
            for i in range(len(item_list)):
                # Split the string into elements of list at commas
                item_list[i] = item_list[i].strip().split(",")
            # self.update(item_list, 1)

    # Displays elements from list onto table
    def display(self, list, test):
        global item_list
        print(test)
        print("list to be displayed" + str(list))
        self.clear_widgets()
        today = datetime.now().date()

        # Loop through every item and create a label for it
        for index, i in enumerate(list):
            item_row = MDBoxLayout(orientation='horizontal',
                                   size_hint=(1, None),
                                   height=dp(60))
            for z in i:

                # For the expiration dates, create a boxlayout showing both the expiry date and the number of days left
                if z == i[-1]:
                    # Calculate the number of days left until the expiry date
                    expiry_date = datetime.strptime(z, '%m/%d/%Y').date()
                    days_left = (expiry_date - today).days

                    # Create the vertical box layout
                    vbox = MDBoxLayout(orientation='vertical', size_hint=(1, 0.6))
                    expiry_label = MDLabel(text=z,
                                           size_hint=(1, 0.5),
                                           halign="center",
                                           valign="bottom",
                                           font_style="Body2",
                                           font_size=(dp(4)),
                                           )

                    # If the number of days left is 0 or greater, display it on the table
                    if days_left >= 0:
                        days_left_label = MDLabel(text=f"{days_left} days left",
                                                  size_hint=(1, 0.5),
                                                  halign="center",
                                                  valign="top",
                                                  font_style="Body2",
                                                  font_size=(dp(4))
                                                  )
                        days_left_label.color = App.get_running_app().theme_cls.primary_color

                    # If the number of days left is less than 0, display it as expired
                    else:
                        days_left_label = MDLabel(text="Expired",
                                                  size_hint=(1, 0.5),
                                                  halign="center",
                                                  valign="top",
                                                  font_style="Body2",
                                                  font_size=(dp(4))
                                                  )
                        # Change the label to red to make it stand out
                        days_left_label.color = "red"

                    # Add the labels to the boxlayout
                    vbox.add_widget(expiry_label)
                    vbox.add_widget(days_left_label)
                    label = vbox

                # For name and catalog, create a simple label
                else:
                    label = MDFlatButton(text=z,
                                         size_hint=(1, 1),
                                         # When the label is pressed while delete is enabled, remove the item
                                         on_release=lambda x, row=i, name=i[0], category=i[1], expiry=i[2],
                                                           box=item_row, parent=self: (
                                             self.confirm_delete(name, box, row)
                                             if DeleteToggleButton.del_enabled is True else None,
                                             self.edit(name, category, expiry, box, row)
                                             if EditToggleButton.edit_enabled is True else None)

                                         )
                    label.color = App.get_running_app().theme_cls.primary_color

                # Add the label to the item row
                item_row.add_widget(label)

            # Add the item row to the table
            item_row.opacity = 0
            self.add_widget(item_row)

            # Create the animation for this row, and add a delay based on the row index
            anim = Animation(opacity=1, d=1.0 + index * 0.2)
            anim &= Animation(d=1.0 + index * 0.4)
            anim.start(item_row)

    # Opens up a pop-up asking the user to confirm whether they want to delete their food item
    def confirm_delete(self, item_name, box, row):
        self.dialog = MDDialog(
            title=str("Delete " + item_name),
            text="Are you sure you want to delete this food item?",
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(
                    text="Delete",
                    theme_text_color="Custom",
                    text_color="white",
                    md_bg_color="red",
                    on_release=lambda x: (self.delete(box, row), self.dialog.dismiss())
                )
            ],
        )
        self.dialog.open()

    # Removes the widget from the box layout and removes the item from the itemList
    def delete(self, box, row):
        anim = Animation(
            opacity=0,  # fade out the widget
            size=(0, 0),  # shrink the widget down to nothing
            d=0.5  # duration of the animation
        )
        anim.bind(on_complete=lambda *args: FoodList.remove_widget(self, box))
        anim.start(box)
        try:
            item_list.remove(row)
        except:
            pass

    # Performs the edit on the select item
    def edit(self, name, category, expiry, box, row):
        self.app.root.current = "edit_screen"
        self.app.root.transition.direction = "left"
        print(name, category, expiry)
        screen = self.app.root.get_screen("edit_screen")
        screen.ids.name_field.text = name
        screen.ids.category_field.text = category
        screen.ids.expiry_date_field.text = expiry
        EditScreen.box = box
        EditScreen.row = row


# Grid Layout displaying all the default themes available in KivyMD
class Themes(MDGridLayout):

    # Initialization of layout properties
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.spacing = 10
        self.padding = [20, 20, 20, 20]

        # List of all KivyMD themes. Source: https://kivymd.readthedocs.io/en/1.1.1/themes/color-definitions/index.html
        themes = ['LightBlue', 'LightGreen', 'Red', 'Pink', 'Purple', 'DeepPurple',
                  'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen',
                  'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray']

        # Loop through all the themes and create corresponding widgets
        for theme in themes:
            button = MDFlatButton(text=theme,
                                  font_size='15sp',
                                  size_hint=[1, None],
                                  height=60,
                                  # When widget is clicked, change the theme
                                  on_press=lambda x, t=theme: self.change_theme(t))
            self.add_widget(button)

    # Change the theme colour of the app
    def change_theme(self, theme_name):
        App.get_running_app().theme_cls.primary_palette = theme_name


class Tab(MDBoxLayout, MDTabsBase):
    pass


# Displays dynamic date and time
class DynamicTime(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)
        self.color = App.get_running_app().theme_cls.primary_color

    # Uses datetime to get the current clock tim. Returns the formatted time.
    def update(self, dt):
        self.text = datetime.now().strftime("%B %d, %Y - %H:%M:%S")


# Main application class that builds the program and controls all the general functions
class FoodApp(MDApp):

    # Set notification settings from stored file
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with open("SettingsFile.txt") as settingsFile:
            # Read the file lines twice to retrive the second line
            notifSettings = settingsFile.readline()
            notifSettings = settingsFile.readline().strip().split(",")
            print(notifSettings)
            self.notif_enabled = bool(notifSettings[0])
            self.notif_limit = int(notifSettings[1])

    # Set the graphical configurations of the app using the stored settings within the SettingsFile
    def build(self):
        with open("SettingsFile.txt") as settingsFile:
            palette = settingsFile.readline().strip()
            # Check to see if the stored theme colour configuration is valid.
            try:
                self.theme_cls.primary_palette = palette
            # If error occurs, change theme colour to blue
            except:
                self.theme_cls.primary_palette = "Blue"

        # Build theme configurations
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"

    # Perform the notifications method once opening the application
    def on_start(self):
        self.notify()

    # Changes the theme style of the entire app
    def change_mode(self):
        # If theme is already light, switch to dark mode
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
        # If theme is already dark, switch to light mode
        else:
            self.theme_cls.theme_style = "Light"

    ascending_order = True

    # Performs selection sort on item_list based on the category passed in argument
    @classmethod
    def selection_sort(cls, category):
        list = item_list

        length = len(list)
        for i in range(length - 1):
            maximum = 0

            # Loop through every element in item_list to find the largest value
            for z in range(length - i):

                def convert_date(date_str):
                    date = datetime.strptime(date_str, '%m/%d/%Y').date()
                    # today = datetime.today().date()
                    return date

                if category == 2:
                    if convert_date(list[z][category]) >= convert_date(list[maximum][category]):
                        maximum = z
                else:
                    if list[z][category] >= list[maximum][category]:
                        maximum = z

            # Perform exchange of values
            list[z], list[maximum] = list[maximum], list[z]

        # Reverse the list if it was previously sorted in ascending order
        if cls.ascending_order:
            list.reverse()
        cls.ascending_order = not cls.ascending_order  # Toggle the order for next sort

        # Display the new sorted list
        food_list.display(list, 3)
        return

    # Opens MDDatePicker to select date
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_expiry_date)
        date_dialog.open()

    # Sets expiry date text to the date selected in the MDDatePicker
    def set_expiry_date(self, instance, value, date_range):
        screen = self.root.get_screen("input_screen")
        screen.ids.expiry_date_field.text = value.strftime('%m/%d/%Y')
        screenEdit = self.root.get_screen("edit_screen")
        screenEdit.ids.expiry_date_field.text = value.strftime('%m/%d/%Y')

    # Get the current date from datetime and then return it in the format mm/dd/yyyy
    def get_current_date(self):
        now = datetime.now()
        return now.strftime("%m/%d/%Y")

    # Checks to see any upcoming expiration dates. Sends notifications as required.
    def notify(self):
        today = datetime.today().date()

        # Check every item in the itemList
        for item in item_list:

            # Specific embedded function created for converting expiration date into a usable form
            def convert_date(date_str):
                date = datetime.strptime(date_str, '%m/%d/%Y').date()
                return date

            # Compares the expiration date of the item to the current date
            time_left = (convert_date(item[2]) - today).days

            # If there are less than three days left, send a notification from the operating system
            if 1 <= time_left <= self.notif_limit:
                notification.notify(
                    title='Expiration',
                    message=f"Hurry! Your {item[0]} expires in {time_left} days.",
                )

            # If the expiration date is today, send a unique notification
            if time_left == 0:
                notification.notify(
                    title='Expiration',
                    message=f"Hurry! Your {item[0]} expires tonight.",
                )


# Run the application
if __name__ == "__main__":
    print(FoodList.__dict__)
    FoodApp().run()
