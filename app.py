import psycopg2
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)


# Connect to Render PostgreSQL database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="pythondatabase",
            user="kiko",
            password="VQmmSpJ1PTqMRggjx6wAQuFqV91CkDLN",
            host="dpg-ctqs4q0gph6c73cotva0-a.frankfurt-postgres.render.com",
            port="5432"
        )
        return conn
    except Exception as e:
        print("Error connecting to the Render database:", e)
        return None


# Fetch all users
def fetch_users():
    conn = connect_to_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM users;"
        cursor.execute(query)
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print("Error fetching users:", e)
        return []

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        year_of_study = int(request.form['year_of_study'])
        field_of_study = request.form['field_of_study']
        gpa = float(request.form['gpa'])

        # Insert into the database
        conn = connect_to_db()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                INSERT INTO users (first_name, last_name, year_of_study, field_of_study, gpa)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(query, (first_name, last_name, year_of_study, field_of_study, gpa))
                conn.commit()
                print(f"User {first_name} {last_name} added.")
            except Exception as e:
                print("Error adding user:", e)
            finally:
                cursor.close()
                conn.close()

        # Redirect to the main page
        return redirect(url_for('display_users'))

    # Render the add user form
    return render_template('add.html')
# Delete a user by ID
@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM users WHERE id = %s;"
            cursor.execute(query, (user_id,))
            conn.commit()
            print(f"User with ID {user_id} deleted.")
        except Exception as e:
            print("Error deleting user:", e)
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('display_users'))


# Update a user
@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    conn = connect_to_db()
    if request.method == 'POST':
        # Get updated data from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        year_of_study = int(request.form['year_of_study'])
        field_of_study = request.form['field_of_study']
        gpa = float(request.form['gpa'])

        if conn:
            try:
                cursor = conn.cursor()
                query = """
                UPDATE users
                SET first_name = %s, last_name = %s, year_of_study = %s, field_of_study = %s, gpa = %s
                WHERE id = %s;
                """
                cursor.execute(query, (first_name, last_name, year_of_study, field_of_study, gpa, user_id))
                conn.commit()
                print(f"User with ID {user_id} updated.")
            except Exception as e:
                print("Error updating user:", e)
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for('display_users'))
    else:
        # Fetch user details to pre-fill the form
        user = None
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT * FROM users WHERE id = %s;"
                cursor.execute(query, (user_id,))
                user = cursor.fetchone()
            except Exception as e:
                print("Error fetching user for update:", e)
            finally:
                cursor.close()
                conn.close()
        return render_template('update.html', user=user)


# Route to display users
@app.route('/')
def display_users():
    users = fetch_users()
    return render_template('users.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)
