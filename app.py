import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from faker import Faker


fake = Faker()

app = Flask(__name__)



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
       
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        year_of_study = int(request.form['year_of_study'])
        field_of_study = request.form['field_of_study']
        gpa = float(request.form['gpa'])

        
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

        
        return redirect(url_for('display_users'))

  
    return render_template('add.html')

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



@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    conn = connect_to_db()
    if request.method == 'POST':
        
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


def fetch_filtered_users(search=None, year_of_study=None, min_gpa=None):
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE 1=1"
        params = []

        
        if search:
            query += " AND (first_name ILIKE %s OR last_name ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        if year_of_study:
            query += " AND year_of_study = %s"
            params.append(year_of_study)
        if min_gpa:
            query += " AND gpa >= %s"
            params.append(min_gpa)

        cursor.execute(query, params)
        users = cursor.fetchall()
        return users
    except Exception as e:
        print("Error fetching filtered users:", e)
        return []
    finally:
        conn.close()

@app.route('/search', methods=['GET', 'POST'])
def search_users():
    if request.method == 'POST':
     
        search = request.form.get('search')
        year_of_study = request.form.get('year_of_study')
        min_gpa = request.form.get('min_gpa')

        
        year_of_study = int(year_of_study) if year_of_study else None
        min_gpa = float(min_gpa) if min_gpa else None

       
        users = fetch_filtered_users(search=search, year_of_study=year_of_study, min_gpa=min_gpa)
        return render_template('search.html', users=users)

    users = fetch_users()
    return render_template('search.html', users=users)



@app.route('/add_random', methods=['POST'])
def add_random_user():
   
    first_name = fake.first_name()
    last_name = fake.last_name()
    year_of_study = fake.random_int(1, 4)
    field_of_study = fake.job()
    gpa = round(fake.random.uniform(2.0, 4.0), 2)

   
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
            print(f"Random User {first_name} {last_name} added.")
        except Exception as e:
            print("Error adding random user:", e)
        finally:
            cursor.close()
            conn.close()

    
    return redirect(url_for('display_users'))

@app.route('/sort', methods=['GET'])
def sort_users():
    
    sort_by = request.args.get('sort_by', 'id')  
    order = request.args.get('order', 'asc')     

    
    valid_sort_fields = ['id', 'first_name', 'last_name', 'year_of_study', 'field_of_study', 'gpa']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'

    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = f"SELECT * FROM users ORDER BY {sort_by} {order};"
            cursor.execute(query)
            users = cursor.fetchall()
        except Exception as e:
            print("Error sorting users:", e)
            users = []
        finally:
            cursor.close()
            conn.close()
    else:
        users = []

    return render_template('users.html', users=users, sort_by=sort_by, order=order)



@app.route('/')
def display_users():
    users = fetch_users()
    return render_template('users.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)
