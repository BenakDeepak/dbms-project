import streamlit as st
import mysql.connector
import pandas as pd

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="benak@2010",
        database="farm_management"
    )

def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return pd.DataFrame(data, columns=columns)

def run_action(query, values):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def authenticate(username, password, role):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Users WHERE username = %s AND password = %s AND role = %s", 
        (username, password, role)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def login():
    st.title("Login Page")
    
    role = st.selectbox("Select User Type", ["Admin", "Farmer", "Worker"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate(username, password, role.lower())
        if user:
            st.session_state.user_id = user['user_id']
            st.session_state.role = role
            st.experimental_rerun()
        else:
            st.error("Invalid username, password, or user type")

def render_admin_page():
    st.sidebar.title("Admin Dashboard")
    page = st.sidebar.radio("Select Page", ["Users", "Farmers", "Farms", "Workers", "Equipment", "Crops", "Crop Inventory"])

    if page == "Users":
        render_users_page()
    elif page == "Farmers":
        render_farmers_page()
    elif page == "Farms":
        render_farms_page()
    elif page == "Workers":
        render_workers_page()
    elif page == "Equipment":
        render_equipment_page()
    elif page == "Crops":
        render_crops_page()
    elif page == "Crop Inventory":
        render_crop_inventory_page()
def render_users_page():
    st.header("Users")
    action = st.selectbox("Choose action", ["View", "Add", "Delete"])

    if action == "View":
        df = run_query("SELECT * FROM Users")
        st.write(df)

    elif action == "Add":
        with st.form("Add User"):
            username = st.text_input("Username")
            password = st.text_input("Password")
            role = st.selectbox("Role", ["Admin", "Farmer", "Worker"])
            submitted = st.form_submit_button("Add User")
            if submitted:
                run_action("INSERT INTO Users (username,password, role) VALUES (%s, %s, %s)", (username, password, role))
                st.success("User added successfully")
    elif action == "Delete":
        users = run_query("SELECT user_id, username FROM Users")
        user_dict = {row['username']: row['user_id'] for index, row in users.iterrows()}
        username = st.selectbox("Choose a user to delete", list(user_dict.keys()))
        user_id = user_dict[username]

        # Check if there are workers associated with this user
        workers = run_query(f"SELECT * FROM Worker WHERE user_id = {user_id}")
        if not workers.empty:
            st.warning("This user has associated workers. Please handle those workers before deleting.")
        else:
            if st.button("Delete User"):
                run_action("DELETE FROM Users WHERE user_id = %s", (user_id,))
                st.success("User deleted successfully")

def render_farmers_page():
    st.header("Farmers")
    action = st.selectbox("Choose action", ["View", "Add", "Edit", "Delete"])

    if action == "View":
        df = run_query("SELECT * FROM Farmer")
        st.write(df)

    elif action == "Add":
        with st.form("Add Farmer"):
            name = st.text_input("Name")
            address = st.text_input("Address")
            submitted = st.form_submit_button("Add Farmer")
            if submitted:
                run_action("INSERT INTO Farmer (name, address) VALUES (%s, %s)", (name, address))
                st.success("Farmer added successfully")

    elif action == "Edit":
        farmers = run_query("SELECT farmer_id, name FROM Farmer")
        farmer_dict = {row['name']: row['farmer_id'] for index, row in farmers.iterrows()}
        farmer_name = st.selectbox("Choose a farmer to edit", list(farmer_dict.keys()))
        farmer_id = farmer_dict[farmer_name]
        farmer = run_query(f"SELECT * FROM Farmer WHERE farmer_id = {farmer_id}").iloc[0]

        with st.form("Edit Farmer"):
            name = st.text_input("Name", value=farmer['name'])
            address = st.text_input("Address", value=farmer['address'])
            submitted = st.form_submit_button("Update Farmer")
            if submitted:
                run_action("UPDATE Farmer SET name = %s, address = %s WHERE farmer_id = %s", (name, address, farmer_id))
                st.success("Farmer updated successfully")

    elif action == "Delete":
        farmers = run_query("SELECT farmer_id, name FROM Farmer")
        farmer_dict = {row['name']: row['farmer_id'] for index, row in farmers.iterrows()}
        farmer_name = st.selectbox("Choose a farmer to delete", list(farmer_dict.keys()))
        farmer_id = farmer_dict[farmer_name]

        # Check if there are farms associated with this farmer
        farms = run_query(f"SELECT * FROM Farm WHERE farmer_id = {farmer_id}")
        if not farms.empty:
            st.warning("This farmer has associated farms. Please handle those farms before deleting.")
        else:
            if st.button("Delete Farmer"):
                run_action("DELETE FROM Farmer WHERE farmer_id = %s", (farmer_id,))
                st.success("Farmer deleted successfully")

def render_farms_page():
    st.header("Farms")
    action = st.selectbox("Choose action", ["View", "Add", "Delete"])

    if action == "View":
        df = run_query("SELECT * FROM Farm")
        st.write(df)

    elif action == "Add":
        farmers = run_query("SELECT farmer_id, name FROM Farmer")
        farmer_dict = {row['name']: row['farmer_id'] for index, row in farmers.iterrows()}
        with st.form("Add Farm"):
            location = st.text_input("Location")
            size = st.number_input("Size", min_value=0.0, step=0.01)
            farmer_name = st.selectbox("Farmer", list(farmer_dict.keys()))
            submitted = st.form_submit_button("Add Farm")
            if submitted:
                farmer_id = farmer_dict[farmer_name]
                run_action("INSERT INTO Farm (location, size, farmer_id) VALUES (%s, %s, %s)", (location, size, farmer_id))
                st.success("Farm added successfully")
    elif action == "Delete":
        farms = run_query("SELECT farm_id, location FROM Farm")
        farm_dict = {row['location']: row['farm_id'] for index, row in farms.iterrows()}
        farm_location = st.selectbox("Choose a farm to delete", list(farm_dict.keys()))
        farm_id = farm_dict[farm_location]

        if st.button("Delete Farm"):
            run_action("DELETE FROM Farm WHERE farm_id = %s", (farm_id,))
            st.success("Farm deleted successfully")

def render_workers_page():
    st.header("Workers")
    action = st.selectbox("Choose action", ["View", "Add", "Edit", "Delete"])

    if action == "View":
        df = run_query("SELECT * FROM Worker")
        st.write(df)

    elif action == "Add":
        with st.form("Add Worker"):
            name = st.text_input("Name")
            contact_info = st.text_input("Contact Info")
            submitted = st.form_submit_button("Add Worker")
            if submitted:
                run_action("INSERT INTO Worker (name, contact_info) VALUES (%s, %s)", (name, contact_info))
                st.success("Worker added successfully")

    elif action == "Edit":
        workers = run_query("SELECT worker_id, name FROM Worker")
        worker_dict = {row['name']: row['worker_id'] for index, row in workers.iterrows()}
        worker_name = st.selectbox("Choose a worker to edit", list(worker_dict.keys()))
        worker_id = worker_dict[worker_name]
        worker = run_query(f"SELECT * FROM Worker WHERE worker_id = {worker_id}").iloc[0]

        with st.form("Edit Worker"):
            name = st.text_input("Name", value=worker['name'])
            contact_info = st.text_input("Contact Info", value=worker['contact_info'])
            submitted = st.form_submit_button("Update Worker")
            if submitted:
                run_action("UPDATE Worker SET name = %s, contact_info = %s WHERE worker_id = %s", (name, contact_info, worker_id))
                st.success("Worker updated successfully")

    elif action == "Delete":
        workers = run_query("SELECT worker_id, name FROM Worker")
        worker_dict = {row['name']: row['worker_id'] for index, row in workers.iterrows()}
        worker_name = st.selectbox("Choose a worker to delete", list(worker_dict.keys()))
        worker_id = worker_dict[worker_name]

        if st.button("Delete Worker"):
            run_action("DELETE FROM Worker WHERE worker_id = %s", (worker_id,))
            st.success("Worker deleted successfully")

def render_equipment_page():
    st.header("Equipment")
    action = st.selectbox("Choose action", ["View", "Add", "Edit", "Delete"])

    if action == "View":
        df = run_query("SELECT * FROM Equipment")
        st.write(df)

    elif action == "Add":
        with st.form("Add Equipment"):
            name = st.text_input("Name")
            quantity = st.text_input("description")
            submitted = st.form_submit_button("Add Equipment")
            if submitted:
                run_action("INSERT INTO Equipment (equipment_name, description) VALUES (%s, %s)", (name, quantity))
                st.success("Equipment added successfully")

    elif action == "Edit":
        equipment = run_query("SELECT equipment_id, equipment_name FROM Equipment")
        equipment_dict = {row['equipment_name']: row['equipment_id'] for index, row in equipment.iterrows()}
        equipment_name = st.selectbox("Choose equipment to edit", list(equipment_dict.keys()))
        equipment_id = equipment_dict[equipment_name]
        equipment_item = run_query(f"SELECT * FROM Equipment WHERE equipment_id = {equipment_id}").iloc[0]

        with st.form("Edit Equipment"):
            name = st.text_input("Name", value=equipment_item['equipment_name'])
            quantity = st.text_input("Quantity", value=equipment_item['description'])
            submitted = st.form_submit_button("Update Equipment")
            if submitted:
                run_action("UPDATE Equipment SET equipment_name = %s, description = %s WHERE equipment_id = %s", (name, quantity, equipment_id))
                st.success("Equipment updated successfully")

    elif action == "Delete":
        equipment = run_query("SELECT equipment_id, equipment_name FROM Equipment")
        equipment_dict = {row['equipment_name']: row['equipment_id'] for index, row in equipment.iterrows()}
        equipment_name = st.selectbox("Choose equipment to delete", list(equipment_dict.keys()))
        equipment_id = equipment_dict[equipment_name]

        if st.button("Delete Equipment"):
            run_action("DELETE FROM Equipment WHERE equipment_id = %s", (equipment_id,))
            st.success("Equipment deleted successfully")

def render_crops_page():

    st.title("Crops Management")

    st.sidebar.title("Crops Operations")
    operation = st.sidebar.selectbox("Select Operation", ["Add Crop", "View Crops", "Edit Crop", "Delete Crop"])

    if operation == "Add Crop":
        st.header("Add New Crop")
        crop_name = st.text_input("Crop Name")
        variety = st.text_input("Variety")
        planting_date = st.date_input("Planting Date")
        expected_harvest_date = st.date_input("Expected Harvest Date")
        description = st.text_area("Description")
        part_of_country = st.text_input("Part of Country")
        soil_type = st.text_input("Soil Type")
        images = st.text_input("Image URL")
        farm_id = st.number_input("Farm ID", min_value=1, step=1)

        if st.button("Add Crop"):
            run_query("""
                INSERT INTO Crop (crop_name, variety, planting_date, expected_harvest_date, description, part_of_country, soil_type, images, farm_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (crop_name, variety, planting_date, expected_harvest_date, description, part_of_country, soil_type, images, farm_id))
            run_query("commit()")
            st.success("Crop added successfully!")

    elif operation == "View Crops":
        st.header("View All Crops")
        df=run_query("SELECT * FROM Crop")
        st.write(df)
    elif operation == "Edit Crop":
        st.header("Edit Crop")
        crop_id = st.number_input("Enter Crop ID to edit", min_value=1, step=1)
        run_query("SELECT * FROM Crop WHERE crop_id=%s", (crop_id,))
        crop = run_query("fetchone()")
        if crop:
            crop_name = st.text_input("Crop Name", crop[1])
            variety = st.text_input("Variety", crop[2])
            planting_date = st.date_input("Planting Date", crop[3])
            expected_harvest_date = st.date_input("Expected Harvest Date", crop[4])
            description = st.text_area("Description", crop[5])
            part_of_country = st.text_input("Part of Country", crop[6])
            soil_type = st.text_input("Soil Type", crop[7])
            images = st.text_input("Image URL", crop[8])
            farm_id = st.number_input("Farm ID", min_value=1, step=1, value=crop[9])

            if st.button("Update Crop"):
                run_query("""
                    UPDATE Crop SET crop_name=%s, variety=%s, planting_date=%s, expected_harvest_date=%s, description=%s, part_of_country=%s, soil_type=%s, images=%s, farm_id=%s
                    WHERE crop_id=%s
                """, (crop_name, variety, planting_date, expected_harvest_date, description, part_of_country, soil_type, images, farm_id, crop_id))
                run_query("commit()")
                st.success("Crop updated successfully!")
        else:
            st.error("Crop ID not found")

    elif operation == "Delete Crop":
        st.header("Delete Crop")
        crop_id = st.number_input("Enter Crop ID to delete", min_value=1, step=1)
        if st.button("Delete Crop"):
            run_query("DELETE FROM Crop WHERE crop_id=%s", (crop_id,))
            run_query("commit()")
            st.success("Crop deleted successfully!")
def render_crop_inventory_page():
    st.header("Crop Inventory")
    action = st.selectbox("Choose action", ["View", "Add", "Edit", "Delete"])

    if action == "View":
        df = run_query("SELECT * FROM crop_inventory")
        st.write(df)

    elif action == "Add":
        crops = run_query("SELECT crop_id FROM Crop")
        crop_dict = {row['crop_id'] for index, row in crops.iterrows()}
        with st.form("Add Crop Inventory"):
            crop_name = st.selectbox("Crop", list(crop_dict.keys()))
            quantity = st.number_input("Quantity", min_value=0)
            submitted = st.form_submit_button("Add Crop Inventory")
            if submitted:
                crop_id = crop_dict[crop_name]
                run_action("INSERT INTO crop_inventory (crop_id, quantity) VALUES (%s, %s)", (crop_id, quantity))
                st.success("Crop Inventory added successfully")

    elif action == "Edit":
        inventory = run_query("SELECT inventory_id, crop_id FROM crop_inventory")
        inventory_dict = {f"Crop ID: {row['crop_id']}, Inventory ID: {row['inventory_id']}": row['inventory_id'] for index, row in inventory.iterrows()}
        inventory_choice = st.selectbox("Choose inventory to edit", list(inventory_dict.keys()))
        inventory_id = inventory_dict[inventory_choice]
        inventory_item = run_query(f"SELECT * FROM crop_inventory WHERE inventory_id = {inventory_id}").iloc[0]

        crops = run_query("SELECT crop_id FROM Crop")
        crop_dict = {row['crop_id']: row['crop_id'] for index, row in crops.iterrows()}

        with st.form("Edit Crop Inventory"):
            crop_id = st.selectbox("Crop ID", list(crop_dict.keys()), index=list(crop_dict.keys()).index(inventory_item['crop_id']))
            quantity = st.number_input("Quantity", value=inventory_item['quantity'], min_value=0)
            submitted = st.form_submit_button("Update Crop Inventory")
            if submitted:
                run_action("UPDATE crop_inventory SET crop_id = %s, quantity = %s WHERE inventory_id = %s", (crop_id, quantity, inventory_id))
                st.success("Crop Inventory updated successfully")

    elif action == "Delete":
        inventory = run_query("SELECT inventory_id, crop_id FROM crop_inventory")
        inventory_dict = {f"Crop ID: {row['crop_id']}, Inventory ID: {row['inventory_id']}": row['inventory_id'] for index, row in inventory.iterrows()}
        inventory_choice = st.selectbox("Choose inventory to delete", list(inventory_dict.keys()))
        inventory_id = inventory_dict[inventory_choice]

        if st.button("Delete Crop Inventory"):
            run_action("DELETE FROM crop_inventory WHERE inventory_id = %s", (inventory_id,))
            st.success("Crop Inventory deleted successfully")
def send_message(worker_id, worker_name, farmer_name, money, message):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO messages (worker_id, worker_name, farmer_name, money, message)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (worker_id, worker_name, farmer_name, money, message))
        conn.commit()
        st.success("Message sent successfully!")
        st.error(f"Error sending message: {e}")
        cursor.close()
        conn.close()
    else:
        st.error("Unable to connect to the database.")

def render_worker_page(conn):
    st.title("Worker Dashboard")

    # Display Farmer Information
    st.subheader("View Farmer Details")
    farmer_query = "SELECT name FROM farmer"
    farmers_df = pd.read_sql(farmer_query, conn)
    st.dataframe(farmers_df)
    st.subheader("Send Message to Farmer")
    worker_id = st.text_input("Worker ID")
    worker_name = st.text_input("Worker Name")
    farmer_name = st.text_input("Farmer Name")
    money = st.number_input("Money", min_value=0.0)
    message = st.text_area("Message")
    if st.button("Send Message"):
        send_message(worker_id, worker_name, farmer_name, money, message)
    # Sending Message to Farmer
def reply_to_worker_messages(farmer_name):
    st.subheader("Reply to Worker Messages")
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Fetch messages for the farmer
        cursor.execute("SELECT * FROM messages WHERE farmer_name = %s AND status = 'pending'", (farmer_name,))
        messages = cursor.fetchall()
        cursor.close()
        
        if messages:
            for message in messages:
                st.write(f"Worker: {message['worker_name']}")
                st.write(f"Message: {message['message']}")
                st.write(f"Money: {message['money']}")
                
                response = st.text_area(f"Reply to message ID {message['id']}", key=f"reply_{message['id']}")
                
                if st.button(f"Send Response for Message ID {message['id']}", key=f"send_{message['id']}"):
                    cursor = conn.cursor()
                    insert_reply_query = """
                    INSERT INTO message_replies (message_id, farmer_reply) 
                    VALUES (%s, %s)
                    """
                    update_message_status_query = """
                    UPDATE messages
                    SET status = 'replied'
                    WHERE id = %s
                    """
                    cursor.execute(insert_reply_query, (message['id'], response))
                    cursor.execute(update_message_status_query, (message['id'],))
                    conn.commit()
                    st.success("Response sent successfully!")
                    st.error(f"Error sending response: {e}")
        else:
            st.write("No messages to respond to.")
    else:
        st.error("Unable to connect to the database.")

    # Input worker's details
        
def render_farmer_page(conn, farmer_id):
    # Add custom CSS styles
    st.markdown("""
    <style>
    .title {
        color: #4CAF50;
        font-size: 2em;
    }
    .subheader {
        color: #FF5722;
    }
    .form-label {
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Farmer Dashboard")

    # Dropdown for Selecting Table
    table_options = [
        "View Farmer Details", "Add New Farmer", "Delete Farmer", "Edit Farmer Details",
        "Place Equipment Order", "Reply to Worker Messages", "View Crops", "View Crop Inventory"
    ]
    selected_table = st.selectbox("Select Table to Manage", table_options)

    if selected_table == "View Farmer Details":
        st.subheader("View Farmer Details")
        farmer_query = "SELECT * FROM farmer WHERE farmer_id = %s"
        farmer_df = pd.read_sql(farmer_query, conn, params=(farmer_id,))
        st.dataframe(farmer_df)

    elif selected_table == "Add New Farmer":
        st.subheader("Add New Farmer")
        with st.form(key='add_farmer_form'):
            new_farm_name = st.text_input("Farmer Name")
            address = st.text_input("Farm address")
            contact_info=st.text_input("Contact Number")

            add_button = st.form_submit_button("Add Farmer")
            if add_button:
                cursor = conn.cursor()
                add_farmer_query = """
                INSERT INTO farmer (name, address,contact_info)
                VALUES (%s, %s, %s)
                """
                try:
                    cursor.execute(add_farmer_query, (new_farm_name, address,contact_info))
                    conn.commit()
                    st.success("Farmer added successfully!")
                except Exception as e:
                    st.error(f"Error adding farmer: {e}")
                finally:
                    cursor.close()

    elif selected_table == "Edit Farmer Details":
        st.subheader("Edit Farmer Details")
        with st.form(key='edit_farmer_form'):
            new_farm_name = st.text_input("Farm Name")
            address = st.text_input("Farm Owner")
            contact_info=st.text_input("Contact Number")
            edit_button = st.form_submit_button("Edit Farmer")
            if edit_button:
                cursor = conn.cursor()
                edit_farmer_query = """
                UPDATE farmer
                SET location = %s, owner = %s
                WHERE farmer_id = %s
                """
                try:
                    cursor.execute(edit_farmer_query, (new_farm_name, address, contact_info))
                    conn.commit()
                    st.success("Farmer details updated successfully!")
                except Exception as e:
                    st.error(f"Error updating farmer details: {e}")
                finally:
                    cursor.close()

    elif selected_table == "Place Equipment Order":
        from datetime import date

        st.subheader("Place Equipment Order")
    
    # Fetch available equipment
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT equipment_id, equipment_name FROM equipment")
        equipment_list = cursor.fetchall()
        cursor.close()

        equipment_dict = {item['equipment_name']: item['equipment_id'] for item in equipment_list}
    
    # Select equipment from dropdown
        equipment_name = st.selectbox("Equipment Name", list(equipment_dict.keys()))
        equipment_id = equipment_dict[equipment_name]
        equipment_quantity = st.number_input("Quantity", min_value=1)
    
        order_button = st.button("Place Order")
    
        if order_button:
            cursor = conn.cursor()
            place_order_query = """
            INSERT INTO equipment_order (equipment_id, farmer_id, quantity, order_date, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            farmer_name = st.session_state.get('farmer_name')  # assuming farmer_id is stored in session state
            farmer_id = st.session_state.get('farmer_id')  # assuming farmer_id is stored in session state
            try:
                cursor.execute(place_order_query, (equipment_id, farmer_id, equipment_quantity, date.today(), "Pending"))
                conn.commit()
                st.success("Equipment order placed successfully!")
            except Exception as e:
                st.error(f"Error placing equipment order: {e}")
            finally:
                cursor.close()

    elif selected_table == "Reply to Worker Messages":
        reply_to_worker_messages(farmer_id)
    elif selected_table == "View Crops":
        st.subheader("View Crops")
        df = run_query("SELECT * FROM crop")
        st.dataframe(df)

    elif selected_table == "View Crop Inventory":
        st.subheader("View Crop Inventory")

        df = run_query("SELECT * FROM crop_inventory")
        st.dataframe(df)
def reply_to_worker_messages1(farmer_name):
    st.subheader("Reply to Worker Messages")
    conn = get_connection()
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Fetch messages for the farmer
        cursor.execute("SELECT * FROM messages WHERE farmer_name = %s AND status = 'pending'", (farmer_name,))
        messages = cursor.fetchall()
        cursor.close()
        
        if messages:
            for message in messages:
                st.write(f"Worker: {message['worker_name']}")
                st.write(f"Message: {message['message']}")
                st.write(f"Money: {message['money']}")
                
                response = st.text_area(f"Reply to message ID {message['id']}", key=f"reply_{message['id']}")
                
                if st.button(f"Send Response for Message ID {message['id']}", key=f"send_{message['id']}"):
                    cursor = conn.cursor()
                    insert_reply_query = """
                    INSERT INTO message_replies (message_id, farmer_reply) 
                    VALUES (%s, %s)
                    """
                    update_message_status_query = """
                    UPDATE messages
                    SET status = 'replied'
                    WHERE id = %s
                    """
                    
                    cursor.execute(insert_reply_query, (message['id'], response))
                    cursor.execute(update_message_status_query, (message['id'],))
                    conn.commit()
                    st.success("Response sent successfully!")
                   
        else:
            st.write("No messages to respond to.")
    else:
        st.error("Unable to connect to the database.")

def reply_to_worker_messages(farmer_id):
    st.subheader("Reply to Messages from Workers")
    farmer_name = st.text_input("Farmer Name")
    if st.button("Load Messages"):
        reply_to_worker_messages1(farmer_name)
def main():
    if 'role' not in st.session_state:
        login()
    else:
        if st.session_state.role == "Admin":
            render_admin_page()
        elif st.session_state.role == "Farmer":
            conn=get_connection()
            farmer_id = st.text_input("Enter Farmer ID")
            if farmer_id:
                render_farmer_page(conn, farmer_id)
            conn.close()        
        elif st.session_state.role == "Worker":
            conn=get_connection()
            st.sidebar.header("Worker Selection")
            # Fetch worker names and IDs for the selector
            workers_query = "SELECT worker_id, name FROM Worker"
            workers_df = pd.read_sql(workers_query, conn)
    
            worker_options = workers_df.set_index('worker_id')['name'].to_dict()
    
                # Render the Worker Page based on selected worker
            render_worker_page(conn)
            conn.close()
if __name__ == "__main__":
    main()
