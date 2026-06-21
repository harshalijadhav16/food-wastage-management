import streamlit as st
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("food_wastage.db")

st.title("🍱 Local Food Wastage Management System")

# Sidebar menu
menu = st.sidebar.selectbox("Menu", [
    "Home",
    "View Data",
    "SQL Queries",
    "Filter Food",
    "CRUD Operations"
])

if menu == "Home":
    st.header("Welcome!")
    st.write("This system helps reduce food wastage by connecting providers and receivers.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Providers", pd.read_sql("SELECT COUNT(*) as c FROM providers", conn).iloc[0,0])
    col2.metric("Total Receivers", pd.read_sql("SELECT COUNT(*) as c FROM receivers", conn).iloc[0,0])
    col3.metric("Total Food Listings", pd.read_sql("SELECT COUNT(*) as c FROM food_listings", conn).iloc[0,0])

elif menu == "View Data":
    st.header("View Data")
    table = st.selectbox("Select Table", ["providers", "receivers", "food_listings", "claims"])
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df)

elif menu == "SQL Queries":
    st.header("SQL Query Results")
    
    query_option = st.selectbox("Select Query", [
        "Q1 - Providers & Receivers per City",
        "Q2 - Provider Type Contributions",
        "Q3 - Provider Contact Info by City",
        "Q4 - Top Receivers by Claims",
        "Q5 - Total Food Available",
        "Q6 - City wise Food Listings",
        "Q7 - Most Common Food Types",
        "Q8 - Claims per Food Item",
        "Q9 - Top Providers by Successful Claims",
        "Q10 - Claim Status Percentage",
        "Q11 - Average Quantity per Receiver",
        "Q12 - Most Claimed Meal Type",
        "Q13 - Total Donation per Provider"
    ])

    queries = {
        "Q1 - Providers & Receivers per City": """
            SELECT p.City, COUNT(DISTINCT p.Provider_ID) as Total_Providers,
                   COUNT(DISTINCT r.Receiver_ID) as Total_Receivers
            FROM providers p LEFT JOIN receivers r ON p.City = r.City
            GROUP BY p.City ORDER BY Total_Providers DESC""",
        "Q2 - Provider Type Contributions": """
            SELECT Provider_Type, COUNT(*) as Total_Listings,
                   SUM(Quantity) as Total_Quantity
            FROM food_listings GROUP BY Provider_Type ORDER BY Total_Quantity DESC""",
        "Q3 - Provider Contact Info by City": """
            SELECT Name, Type, Address, City, Contact FROM providers LIMIT 20""",
        "Q4 - Top Receivers by Claims": """
            SELECT r.Name, r.Type, r.City, COUNT(c.Claim_ID) as Total_Claims
            FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Receiver_ID ORDER BY Total_Claims DESC LIMIT 10""",
        "Q5 - Total Food Available": """
            SELECT SUM(Quantity) as Total_Food_Available FROM food_listings""",
        "Q6 - City wise Food Listings": """
            SELECT Location as City, COUNT(*) as Total_Listings, SUM(Quantity) as Total_Quantity
            FROM food_listings GROUP BY Location ORDER BY Total_Listings DESC LIMIT 10""",
        "Q7 - Most Common Food Types": """
            SELECT Food_Type, COUNT(*) as Total_Listings, SUM(Quantity) as Total_Quantity
            FROM food_listings GROUP BY Food_Type ORDER BY Total_Listings DESC""",
        "Q8 - Claims per Food Item": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) as Total_Claims
            FROM food_listings f LEFT JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_Name ORDER BY Total_Claims DESC""",
        "Q9 - Top Providers by Successful Claims": """
            SELECT p.Name, p.Type, p.City, COUNT(c.Claim_ID) as Successful_Claims
            FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID ORDER BY Successful_Claims DESC LIMIT 10""",
        "Q10 - Claim Status Percentage": """
            SELECT Status, COUNT(*) as Total,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) as Percentage
            FROM claims GROUP BY Status""",
        "Q11 - Average Quantity per Receiver": """
            SELECT r.Name, AVG(f.Quantity) as Avg_Quantity_Claimed
            FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY r.Receiver_ID ORDER BY Avg_Quantity_Claimed DESC LIMIT 10""",
        "Q12 - Most Claimed Meal Type": """
            SELECT f.Meal_Type, COUNT(c.Claim_ID) as Total_Claims
            FROM food_listings f JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Meal_Type ORDER BY Total_Claims DESC""",
        "Q13 - Total Donation per Provider": """
            SELECT p.Name, p.Type, p.City, SUM(f.Quantity) as Total_Donated
            FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID ORDER BY Total_Donated DESC LIMIT 10"""
    }

    df = pd.read_sql(queries[query_option], conn)
    st.dataframe(df)
    st.bar_chart(df.set_index(df.columns[0])[df.columns[-1]])

elif menu == "Filter Food":
    st.header("Filter Food Listings")
    cities = pd.read_sql("SELECT DISTINCT Location FROM food_listings", conn)["Location"].tolist()
    food_types = pd.read_sql("SELECT DISTINCT Food_Type FROM food_listings", conn)["Food_Type"].tolist()
    meal_types = pd.read_sql("SELECT DISTINCT Meal_Type FROM food_listings", conn)["Meal_Type"].tolist()

    city = st.selectbox("Select City", ["All"] + cities)
    food_type = st.selectbox("Select Food Type", ["All"] + food_types)
    meal_type = st.selectbox("Select Meal Type", ["All"] + meal_types)

    query = "SELECT * FROM food_listings WHERE 1=1"
    if city != "All": query += f" AND Location = '{city}'"
    if food_type != "All": query += f" AND Food_Type = '{food_type}'"
    if meal_type != "All": query += f" AND Meal_Type = '{meal_type}'"

    df = pd.read_sql(query, conn)
    st.dataframe(df)

elif menu == "CRUD Operations":
    st.header("CRUD Operations")
    operation = st.selectbox("Select Operation", ["Add Food Listing", "Update Quantity", "Delete Listing"])

    if operation == "Add Food Listing":
        st.subheader("Add New Food Listing")
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", min_value=1)
        expiry = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1)
        location = st.text_input("Location")
        food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

        if st.button("Add"):
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO food_listings 
                (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (food_name, quantity, str(expiry), provider_id, location, food_type, meal_type))
            conn.commit()
            st.success("Food listing added! ✅")

    elif operation == "Update Quantity":
        st.subheader("Update Food Quantity")
        food_id = st.number_input("Food ID", min_value=1)
        new_qty = st.number_input("New Quantity", min_value=1)
        if st.button("Update"):
            conn.execute("UPDATE food_listings SET Quantity = ? WHERE Food_ID = ?", (new_qty, food_id))
            conn.commit()
            st.success("Quantity updated! ✅")

    elif operation == "Delete Listing":
        st.subheader("Delete Food Listing")
        food_id = st.number_input("Food ID to Delete", min_value=1)
        if st.button("Delete"):
            conn.execute("DELETE FROM food_listings WHERE Food_ID = ?", (food_id,))
            conn.commit()
            st.success("Listing deleted! ✅")
