import json  
import sys  
from datetime import datetime  

# Class to represent each resident in the system.
class Resident:
    def __init__(self, name, house_number, zone, waste_added=0, recycling_discount=0, final_payment=0, waste_log=None):
        self.name = name
        self.house_number = house_number
        self.zone = zone
        self.waste_added = waste_added  
        self.recycling_discount = recycling_discount  
        self.final_payment = final_payment
        self.waste_log = waste_log if waste_log is not None else []  

# Main class
class BinIttoWinIt:
    def __init__(self):
        self.residents = []  # List of registered residents.
        
        # Dictionary mapping zone numbers to collection days.
        self.zones = {
            1: ["Monday", "Wednesday"],
            2: ["Monday", "Wednesday"],
            3: ["Thursday", "Saturday"],
            4: ["Thursday", "Saturday"],
            5: ["Tuesday", "Friday"],
            6: ["Tuesday", "Friday"]
        }
        
        #Load resident data from JSON file
        self.load_residents()

    #Method to load resident data from a JSON file.
    def load_residents(self):
        try:
            with open("residents.json", "r") as file:
                data = json.load(file)  
                for resident_data in data:
                    resident = Resident(
                        name=resident_data["name"],
                        house_number=resident_data["house_number"],
                        zone=resident_data["zone"],
                        waste_added=resident_data.get("waste_added", 0),
                        recycling_discount=resident_data.get("recycling_discount", 0),
                        final_payment=resident_data.get("final_payment", 0),
                        waste_log=resident_data.get("waste_log", [])
                    )
                    self.residents.append(resident)
        except FileNotFoundError:
            print("No resident data found.r")
        except json.JSONDecodeError:
            print("Error decoding the residents file. Please check the file format.")

    #Method to save resident data to a JSON file.
    def save_residents(self):
        with open("residents.json", "w") as file:
            json.dump([
                {
                    "name": resident.name,
                    "house_number": resident.house_number,
                    "zone": resident.zone,
                    "waste_added": resident.waste_added,
                    "recycling_discount": resident.recycling_discount,
                    "final_payment": resident.final_payment,
                    "waste_log": resident.waste_log
                }
                for resident in self.residents
            ], file, indent=4)

    #Method to register a new resident.
    def register_resident(self):
        name = input("Enter name: ")
        house_number = input("Enter house number: ")
        while True:
            try:
                zone = int(input("Enter zone (1-6): "))
                if zone in self.zones:
                    break
                else:
                    print("Invalid zone. Please enter a number between 1 and 6.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        #Create a new Resident object and add it to the list.
        new_resident = Resident(name, house_number, zone)
        self.residents.append(new_resident)
        print("Resident registered successfully!")
        self.save_residents()

    #Method to log in an existing resident.
    def login(self):
        house_number = input("Enter your house number to login: ")
        for resident in self.residents:
            if resident.house_number == house_number:
                print(f"Welcome back, {resident.name}!")
                return resident
        print("Resident not found.")
        return None

    #Method to display collection days for a resident's zone.
    def show_collection_day(self, resident):
        print(f"Your collection days are: {', '.join(self.zones[resident.zone])}")

    #Method to display waste sorting instructions and reduction tips.
    def show_instructions_and_tips(self):
        print("\nWASTE SORTING INSTRUCTIONS")
        print("\nRECYCLABLE WASTE (use recycling bin)")
        print("      Plastic: Clean plastic bottles and containers.")
        print("      Paper: Newspapers, magazines, cardboard, and office paper.")
        print("      Metal: Tin cans and aluminum cans.")
        print("      Glass: Glass bottles and jars.")
        print("  Preparation:")
        print("      Remove food residue, flatten items when possible, and avoid including contaminated materials.\n")
        
        print("GENERAL WASTE (use general waste bin)")
        print("      Food Waste: All food scraps, peelings, and leftovers.")
        print("      Non-recyclables: Soiled paper, certain plastics, ceramics, and broken household items.")
        print("      Electronics: Old phones, batteries, and small electronic devices.")
        print("  Preparation:")
        print("      Secure in bags to avoid spillage, especially for food waste and sharp objects.\n")
        
        print("WASTE REDUCTION TIPS:")
        print("Use reusable bags instead of plastic bags.")
        print("Compost food waste to reduce landfill impact.")
        print("Opt for items with minimal packaging.")
        print("Use glass containers instead of single-use plastic.\n")

    #Method to select a recyclable waste item.
    def select_waste_item(self):
        recyclable_items = ["Plastic", "Paper", "Metal", "Glass"]
        print("Select a recyclable item:")
        for i, item in enumerate(recyclable_items, 1):
            print(f"{i}. {item}")
        while True:
            try:
                item_index = int(input("Choose an item number: ")) - 1
                if 0 <= item_index < len(recyclable_items):
                    return recyclable_items[item_index]
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    #Method to input the amount of waste for a selected item.
    def input_waste_amount(self, waste_item):
        while True:
            try:
                waste_amount = float(input(f"Enter the amount of {waste_item} added (in kg): "))
                if waste_amount >= 0:
                    return waste_amount
                print("Invalid amount. Please enter a non-negative number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    #Method to add waste entries for a resident.
    def add_waste(self, resident):
        print("\n=======================")
        print("\tBIN IT")
        print("=======================")
        while True:
            waste_item = self.select_waste_item()
            waste_amount = self.input_waste_amount(waste_item)
            resident.waste_added += waste_amount  # Update total waste added.
            resident.waste_log.append({"type": "Recyclable", "item": waste_item, "amount": waste_amount}) 
            print(f"{waste_item} of {waste_amount} kg added successfully.")
            if input("\nWould you like to add more waste? (yes/no): ").strip().lower() != 'yes':
                break
        self.save_residents()  # Save data after adding waste

    #Method to calculate recycling discount based on waste added.
    def calculate_discount(self, resident):
        while True:
            try:
                initial_payment = float(input("\nEnter total payment (before discount): "))
                if initial_payment >= 0:
                    break
                else:
                    print("Please enter a valid payment amount.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        #Calculate the base discount based on total recyclable waste added
        base_discount = max(0, 20 - resident.waste_added)
        
        #Additional discount based on type and frequency of recyclable items
        extra_discount = 0
        for entry in resident.waste_log:
            item = entry["item"]
            amount = entry["amount"]
            
            if item == "Plastic":
                extra_discount += 0.5 * min(amount, 10)  
            elif item == "Paper":
                extra_discount += 0.3 * min(amount, 10)  
            elif item == "Metal":
                extra_discount += 0.4 * min(amount, 10)  
            elif item == "Glass":
                extra_discount += 0.7 * min(amount, 10)  
        
        extra_discount = min(extra_discount, 10)
        
        #Calculate the total discount, limiting it to a maximum of 20 pesos
        resident.recycling_discount = min(base_discount + extra_discount, 20)
        
        #Calculate final payment after discount
        resident.final_payment = max(0, initial_payment - resident.recycling_discount)
        print(f"Recycling discount: ₱ {resident.recycling_discount:.2f}")
        print(f"Final payment after discount: ₱ {resident.final_payment:.2f}")
        self.save_residents()  # Save data after calculating discount

    #Method to display a summary of the resident's waste data and final payment.
    def display_summary(self, resident):
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S") 
        print("\n=================================")
        print("            WIN IT")
        print("---------------------------------")
        print("     Waste Management Summary")
        print("=================================")
        print(f"Name: {resident.name}")
        print(f"House Number: {resident.house_number}")
        print(f"Zone: {resident.zone}")
        print(f"Collection Days: {', '.join(self.zones[resident.zone])}")
        print(f"Total Recyclable Waste Added: {resident.waste_added:.2f} kg")
        print(f"Recycling Discount: ₱ {resident.recycling_discount:.2f}")
        print(f"Final Payment After Discount: ₱ {resident.final_payment:.2f}")
        print(f"\n{current_time}")
        print("\nWaste Log:")
        for entry in resident.waste_log:
            print(f"  - {entry['amount']} kg of {entry['item']} ({entry['type']}).")

    #Main menu for the system
    def main_menu(self):
        while True:
            print("\n===============================")
            print("\tBIN IT TO WIN IT")
            print("===============================")
            print("1. Register Resident")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose an option: ")
            
            if choice == "1":
                self.register_resident()
            elif choice == "2":
                resident = self.login()
                if resident:
                    self.resident_menu(resident)
            elif choice == "3":
                print("Exiting the system. Goodbye!")
                self.save_residents()
                sys.exit()
            else:
                print("Invalid choice. Please try again.")

    #Menu for a logged-in resident, allowing various actions.
    def resident_menu(self, resident):
        while True:
            print("\n=================================")
            print("\tResident Options")
            print("=================================")
            print("1. Show Collection Days")
            print("2. Show Instructions and Reduction Tips")
            print("3. Add Waste")
            print("4. Calculate Recycling Discount")
            print("5. Display Summary")
            print("6. Logout")
            choice = input("Choose an option: ")

            if choice == "1":
                self.show_collection_day(resident)
            elif choice == "2":
                self.show_instructions_and_tips()
            elif choice == "3":
                self.add_waste(resident)
            elif choice == "4":
                self.calculate_discount(resident)
            elif choice == "5":
                self.display_summary(resident)
            elif choice == "6":
                print("Logging out.")
                break
            else:
                print("Invalid choice. Please try again.")

#Entry point to start the program.
if __name__ == "__main__":
    system = BinIttoWinIt()
    system.main_menu()
