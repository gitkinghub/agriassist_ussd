""" ussd utility functions"""

class USSDMenuHandler:
    def __init__(self, user, session, session_state, text):
        """
        Initialize menu handler
        
        Args:
            user: UssdUser instance
            session: UssdSession instance
            session_state: UssdSessionState instance
            text: Full navigation path from AfricasTalking (e.g., "1*2*3")
        """
        self.user = user
        self.session = session
        self.state = session_state
        self.text = text
        
        # Extract latest user input (last segment after splitting by *)
        # Examples: "" -> "", "1" -> "1", "1*2*3" -> "3"
        self.user_input = text.split('*')[-1] if text else ''
        
        
    def process(self):
        """
        Process user input and return appropriate response menu
        
        Returns:
            str: Response text to be sent back to user
        """
        
        registered_user = ['254112130020']
        
        is_registered = self.user.phone_number in registered_user
        
        if not is_registered:
            return self.registration_menu()
        
        # for registered users
        menu_method = getattr(self, f"{self.state.current_menu}_menu", None)
        
        if menu_method and callable(menu_method):
            return menu_method()
        else:
            # Fallback to main menu if method doesn't exist
            return self.main_menu()
        
    def registration_menu(self):
        """
        Handle user registration flow
        
        USER STORY: Display registration welcome message
        Acceptance Criteria:
        - Display "Welcome to Curbside Kitchen! You need to register first."
        - Prompt for first name
        """
        
        if not self.text:
            self.state.current_menu = 'registration'
            self.state.save()
            
            return (
                "Welcome to AgriAssist!\n"
                "You need to register first.\n\n"
                "Enter your first name:",
                False
                )
            
        
        # handling registration
        if 'first_name' not in self.state.temp_data:
            first_name = self.user_input.strip()
            
            if not first_name or not first_name.isalpha():
                return (
                    "Invalid input. Please enter a valid first name.",
                    False
                    )
                
            self.state.temp_data['first_name'] = first_name.title()
            self.state.save()
            
            return (
                "Enter your last name:",
                False
                )
            
        if 'last_name' not in self.state.temp_data:
            last_name = self.user_input.strip()
            
            if not last_name or not last_name.isalpha():
                return (
                    "Invalid input. Please enter a valid first name.",
                    False
                    )
                
            self.state.temp_data['last_name'] = last_name.title()
            self.state.save()
            
            full_name = f"{self.state.temp_data['first_name']} {self.state.temp_data['last_name']}"
            
            return (
                f"Confirm registration:\n"
                f"Name: {full_name}\n"
                f"Phone: {self.user.phone_number}\n\n"
                f"1. Confirm\n"
                f"2. Start Over\n"
                f"0. Cancel",
                False
            )

        if self.user_input == '1':
            self.user.first_name = self.state.temp_data['first_name']
            self.user.last_name = self.state.temp_data['last_name']
            self.user.save()
            
            # Clear temp data and update menu
            self.state.temp_data = {}
            self.state.current_menu = 'main_menu'
            self.state.save()
            
            return (
                f"Registration successful!\n"
                f"Welcome {self.user.first_name}!\n\n"
                f"Dial again to access our services.",
                True  # End session
            )
            
        elif self.user_input == '2':
            self.state.temp_data = {}
            self.state.save()
            return self.registration_menu()
        
        else:
            # Cancel registration
            self.state.temp_data = {}
            self.state.current_menu = 'main_menu'
            self.state.save()
            
            return (
                "Registration cancelled.\n"
                "You need to register to use our services.",
                True
            )
            
    def main_menu(self):
        """
        Handle main menu
        
        USER STORY: Display main menu
        Acceptance Criteria:
        - Display "Welcome to Curbside Kitchen!"
        - List main menu options
        """
        if not self.text or self.text == '':
            return (
                f"Welcome {self.user.first_name}!\n\n"
                f"1. View Menu\n"
                f"2. Book Table\n"
                f"3. My Bookings\n"
                f"4. Contact Us\n"
                f"0. Exit",
                False
            )
            
        if self.user_input == '1':
            self.state.current_menu = 'view_menu'
            self.state.save()
            return self.view_menu_menu()
        elif self.user_input == '2':
            self.state.current_menu = 'book_table'
            self.state.save()
            return self.view_menu_menu()
        elif self.user_input == '3':
            self.state.current_menu = 'my_bookings'
            self.state.save()
            return self.view_menu_menu()
        elif self.user_input == '4':
            self.state.current_menu = 'contact_us'
            self.state.save()
            return self.view_menu_menu() 
        else:
            return(
                "Ivalid option.\n",
                True
            )
            
    def view_menu_menu(self):
        """
        Handle view menu
        
        USER STORY: Display menu
        Acceptance Criteria:
        - Display "View Menu"
        - List menu options
        """
        return (
            "Menu categories:\n"
            "1. Breakfast\n"
            "2. Appetizers\n"
            "3. Drinks\n"
            "4. Main Dishes\n"
            "0. Back",
            False
        )
        