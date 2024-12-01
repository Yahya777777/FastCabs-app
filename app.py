from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DATABASE = "fastcabs.db"

def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enables dict-like access to rows
    return conn

@app.route('/')
def index():
    """Render the homepage."""
    return render_template("index.html")

@app.route('/query/managers', methods=['GET'])
def get_managers():
    """Query and display managers' details."""
    conn = get_db_connection()
    query = "SELECT fName, lName, phone FROM Employee WHERE position = 'Manager';"
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Managers' Details", results=results)

@app.route('/query/female-drivers-glasgow', methods=['GET'])
def get_female_drivers_glasgow():
    """Query and display female drivers in Glasgow."""
    conn = get_db_connection()
    query = """
    SELECT Driver.fName, Driver.lName
    FROM Driver
    JOIN Office ON Driver.officeID = Office.OfficeID
    WHERE Office.location LIKE '%Glasgow%' AND Driver.gender = 'Female';
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Female Drivers in Glasgow", results=results)

@app.route('/query/staff-count', methods=['GET'])
def get_staff_count_per_office():
    """Query and display the total number of staff at each office."""
    conn = get_db_connection()
    query = "SELECT officeID, COUNT(*) AS total_staff FROM Employee GROUP BY officeID;"
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Staff Count Per Office", results=results)

@app.route('/query/taxis-in-glasgow', methods=['GET'])
def get_taxis_in_glasgow():
    """Query and display details of all taxis at the Glasgow office."""
    conn = get_db_connection()
    query = """
    SELECT Taxi.*
    FROM Taxi
    JOIN Office ON Taxi.officeID = Office.OfficeID
    WHERE Office.location LIKE '%Glasgow%';
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Taxis in Glasgow", results=results)

@app.route('/query/w-registered-taxis', methods=['GET'])
def get_w_registered_taxis():
    """Query and display the total number of W-registered taxis."""
    conn = get_db_connection()
    query = "SELECT COUNT(*) AS total_w_registered_taxis FROM Taxi WHERE registrationNO LIKE 'W%';"
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="W-Registered Taxis", results=results)

@app.route('/query/driver-allocation', methods=['GET'])
def get_driver_allocation_per_taxi():
    """Query and display the number of drivers allocated to each taxi."""
    conn = get_db_connection()
    query = "SELECT taxiID, COUNT(*) AS total_drivers FROM Driver GROUP BY taxiID;"
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Driver Allocation Per Taxi", results=results)

@app.route('/query/multi-taxi-owners', methods=['GET'])
def get_multi_taxi_owners():
    """Query and display owners with more than one taxi."""
    conn = get_db_connection()
    query = """
    SELECT TaxiOwner.fName, TaxiOwner.lName, COUNT(*) AS total_taxis
    FROM TaxiOwner
    JOIN Taxi ON TaxiOwner.ownerID = Taxi.ownerID
    GROUP BY TaxiOwner.fName, TaxiOwner.lName
    HAVING COUNT(*) > 1;
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Owners with More Than One Taxi", results=results)

@app.route('/query/business-clients-glasgow', methods=['GET'])
def get_business_clients_glasgow():
    """Query and display the full addresses of business clients in Glasgow."""
    conn = get_db_connection()
    query = "SELECT address FROM Client WHERE address LIKE '%Glasgow%';"
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Business Clients in Glasgow", results=results)

@app.route('/query/current-contracts-glasgow', methods=['GET'])
def get_current_contracts_glasgow():
    """Query and display details of current contracts with Glasgow clients."""
    conn = get_db_connection()
    query = """
    SELECT Service.*, Client.address
    FROM Service
    JOIN Client ON Service.clientID = Client.clientID
    WHERE Client.address LIKE '%Glasgow%' AND Service.paymentStatus = 'Paid';
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Current Contracts in Glasgow", results=results)

@app.route('/query/private-clients-by-city', methods=['GET'])
def get_private_clients_by_city():
    """Query and display the total number of private clients in each city."""
    conn = get_db_connection()
    query = """
    SELECT SUBSTR(address, INSTR(address, ',') + 2) AS city, COUNT(*) AS total_private_clients
    FROM Client
    GROUP BY SUBSTR(address, INSTR(address, ',') + 2);
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Private Clients by City", results=results)

@app.route('/query/jobs-by-driver', methods=['GET', 'POST'])
def get_jobs_by_driver():
    """Query and display details of jobs by a specific driver on a given day."""
    if request.method == 'POST':
        driver_id = request.form.get('driver_id')
        date = request.form.get('date')
        conn = get_db_connection()
        query = """
        SELECT * 
        FROM Jobs
        WHERE DriverID = ? AND JobDate = ?;
        """
        results = conn.execute(query, (driver_id, date)).fetchall()
        conn.close()
        return render_template("query_results.html", title="Jobs by Driver", results=results)
    return render_template("driver_query.html")

@app.route('/query/drivers-over-55', methods=['GET'])
def get_drivers_over_55():
    """Query and display names of drivers who are over 55 years old."""
    conn = get_db_connection()
    query = """
    SELECT DriverName 
    FROM Drivers 
    WHERE (julianday('now') - julianday(DateOfBirth)) / 365 > 55;
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Drivers Over 55", results=results)

@app.route('/query/private-clients-november-2000', methods=['GET'])
def get_private_clients_november_2000():
    """Query and display private clients who hired taxis in November 2000."""
    conn = get_db_connection()
    query = """
    SELECT DISTINCT c.fName, c.lName
    FROM Client c
    JOIN Service s ON c.clientID = s.clientID
    JOIN Trip t ON s.tripID = t.tripID
    WHERE strftime('%Y-%m', t.pickupTime) = '2000-11';
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Private Clients in November 2000", results=results)

@app.route('/query/average-miles', methods=['GET'])
def get_average_miles():
    """Query and display the average number of miles driven during a job."""
    conn = get_db_connection()
    query = "SELECT AVG(MilesDriven) AS AverageMiles FROM Jobs;"
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template("query_results.html", title="Average Miles Per Job", results=results)

@app.route('/query/jobs-and-miles', methods=['GET'])
def get_jobs_and_miles():
    """Query and display total number of jobs and miles driven for a specific contract."""
    contract_id = request.args.get('contract_id', 'CON001')  # Default contract ID
    conn = get_db_connection()
    query = """
    SELECT contractID, COUNT(t.tripID) AS total_jobs, SUM(t.mileage) AS total_miles
    FROM Trip t
    WHERE t.contractID = ?
    GROUP BY contractID;
    """
    results = conn.execute(query, (contract_id,)).fetchall()
    conn.close()
    return render_template("query_results.html", title="Jobs and Miles by Contract", results=results)

if __name__ == "__main__":
    app.run(debug=True)
