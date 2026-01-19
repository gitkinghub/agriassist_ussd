""" ussd utility functions"""

import datetime
from agriassist.USSD.constants import TIME_SLOTS
from agriassist.USSD.models import UssdBooking


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
            tuple: (response_text, is_end)
        """
                
        is_registered = bool(self.user.first_name)
        
        if not is_registered:
            return self.registration_menu()
        
        # for registered users
        menu_method = getattr(self, f"{self.state.current_menu}")
        
        if not callable(menu_method):
            self.current_menu = 'main_menu'
            self.state.save()
            menu_method = self.main_menu
        
        return menu_method()
            
        
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
            return self.view_menu()
        elif self.user_input == '2':
            self.state.current_menu = 'book_table_menu'
            self.state.save()
            return self.book_table_menu()
        elif self.user_input == '3':
            self.state.current_menu = 'my_bookings'
            self.state.save()
            return self.my_bookings_menu()
        elif self.user_input == '4':
            self.state.current_menu = 'contact_us'
            self.state.save()
            return self.view_menu() 
        elif self.user_input == '0':
            return(
                "Operation cancelled.\n",
                True
            )
        else:
            return (
                "Invalid option. Please try again.",
                False
            )
            
    def view_menu(self):
        """
        Handle view menu

        USER STORY: Display menu
        Acceptance Criteria:
        - Display "View Menu"
        - List menu options
        """
        # Check if we just entered this menu
        if 'view_menu_shown' not in self.state.temp_data:
            self.state.temp_data['view_menu_shown'] = True
            self.state.save()
            return (
                "Menu categories:\n"
                "1. Breakfast\n"
                "2. Appetizers\n"
                "3. Drinks\n"
                "4. Main Dishes\n"
                "0. Back",
                False
            )

        # Clear the flag and handle selection
        del self.state.temp_data['view_menu_shown']
        self.state.save()

        if self.user_input == '1':
            self.state.current_menu = 'breakfast_menu'
            self.state.save()
            return self.breakfast_menu()
        elif self.user_input == '2':
            self.state.current_menu = 'appetizers_menu'
            self.state.save()
            return self.appetizers_menu()
        elif self.user_input == '3':
            self.state.current_menu = 'drinks_menu'
            self.state.save()
            return self.drinks_menu()
        elif self.user_input == '4':
            self.state.current_menu = 'main_dishes_menu'
            self.state.save()
            return self.main_dishes_menu()
        elif self.user_input == '0':
            self.state.current_menu = 'main_menu'
            self.state.save()
            return self.main_menu()
        else:
            return (
                "Invalid option. Please try again.",
                False
            )
        
        
        
    def book_table_menu(self):
        """
        Handle book table
        
        USER STORY: Book table
        Acceptance Criteria:
        - Display "Book Table"
        - Prompt for date and time
        """
        if 'book_table_menu' not in self.state.temp_data:
            self.state.temp_data['book_table_menu'] = True
            self.state.save()
            return(
                "Booking Information:\n"
                "Enter booking date (YYYY-MM-DD):",
                False
            )
        
        if 'booking_date' not in self.state.temp_data:
            booking_date = self.user_input.strip()
            self.state.temp_data['booking_date'] = booking_date
            self.state.save()
            
            slots = [f"{time}. {display}" for time, (_, display) in enumerate(TIME_SLOTS, start=1)]
            return(
                "Available time slots:\n\n" + "\n".join(slots) + "\n\nEnter booking time slot:",
                False
            )
        
        if 'time_slot' not in self.state.temp_data:
            time_mapping = {str(time): time_value for time, (time_value, _) in enumerate(TIME_SLOTS, start=1)}
            if self.user_input not in time_mapping:
                return(
                    "Invalid time slot. Please try again.",
                    False
                )
            time_slot = time_mapping[self.user_input]
            self.state.temp_data['time_slot'] = time_slot
            self.state.save()
            return(
                "Enter number of people:",
                False
            )
        
        if 'party_size' not in self.state.temp_data:
            party_size = self.user_input.strip()
            self.state.temp_data['party_size'] = party_size
            self.state.save()
            return(
                "Write any special requests:",
                False
            )
            
        if 'special_requests' not in self.state.temp_data:
            special_requests = self.user_input.strip()
            self.state.temp_data['special_requests'] = special_requests
            self.state.save()
            return(
                "Confirm booking:\n"
                f"Name: {self.user.first_name} {self.user.last_name}\n"
                f"Booking Date: {self.state.temp_data['booking_date']}\n"
                "1. Confirm\n"
                "2. Edit\n"
                "0. Cancel",
                False
            )
            
        if self.user_input == '1':
            booking = UssdBooking.objects.create(
                user = self.user,
                booking_date = self.state.temp_data['booking_date'],
                time_slot = self.state.temp_data['time_slot'],
                party_size = self.state.temp_data['party_size'],
                special_requests = self.state.temp_data['special_requests']
            )
            
            # Clear temp data and update menu
            self.state.temp_data = {}
            self.state.current_menu = 'main_menu'
            self.state.save()
            
            return(
                "Booking successful!\n"
                "Thank you for booking with us.",
                True
            )
            
        elif self.user_input == '2':
            self.state.temp_data = {}
            self.state.save()
            return self.book_table_menu()
        
        else:            
            return(
                "Booking cancelled.\n",
                True
            )
            
    
    def my_bookings_menu(self):
        """
        Handle my bookings
        
        USER STORY: View bookings
        Acceptance Criteria:
        - Display "My Bookings"
        - List bookings
        """
        bookings = UssdBooking.objects.filter(user=self.user, booking_date__gte=datetime.now())
        
        if not bookings:
            return (
                "You have no bookings.\n",
                True
            )
            
        response = "Your Upcoming Bookings:\n\n"
        for booking in bookings:
            time_display = dict(TIME_SLOTS).get(booking.time_slot, booking.time_slot)
            
            response += (
                f" {booking.booking_date}\n"
                f" {time_display}\n"
                f" {booking.party_size} guests\n"
                f"Ref No: {booking.reference_number}\n\n"
            )
        
        response += "For changes call:\n+88-123-123456"
        
        return (
            response,
            True
        )
        
        
    def breakfast_menu(self):
        """
        Handle breakfast menu
        
        USER STORY: Display breakfast menu
        Acceptance Criteria:
        - Display "Breakfast Menu"
        - List breakfast options
        """
        if 'breakfast_menu_shown' not in self.state.temp_data:
            self.state.temp_data['breakfast_menu_shown'] = True
            self.state.save()
            return (
                "Breakfast Menu:\n"
                "1. Eggs Benedict - Ksh 500\n"
                "2. Pancakes - Ksh 400\n"
                "3. French Toast - Ksh 300\n"
                "0. Back",
                False
            )
        
        # Clear the flag and handle selection
        del self.state.temp_data['breakfast_menu_shown']
        self.state.save()
            
        if self.user_input == '1':
            self.state.current_menu = 'eggs_benedict'
            self.state.save()
            return self.eggs_benedict()
        if self.user_input == '2':
            self.state.current_menu = 'pancakes'
            self.state.save()
            return self.pancakes()
        if self.user_input == '3':
            self.state.current_menu = 'french_toast'
            self.state.save()
            return self.french_toast()
        if self.user_input == '0':
            self.state.current_menu = 'view_menu'
            self.state.save()
            return self.view_menu()
        else:
            return (
                "Invalid option. Please try again.",
                False
            )
        