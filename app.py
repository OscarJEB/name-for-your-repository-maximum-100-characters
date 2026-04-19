from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)

engine = create_engine('sqlite:///.database/cyberwatch.db') #link to the cyberwatch database here
connection = engine.connect()


#route for index.html
@app.route('/')
def home():
    
    with engine.connect() as connection:
        # This way of connecting to the database 
        # ensures that the connection is automatically closed as soon as the function finishes
        query = text('SELECT * FROM vulnerabilities ORDER BY owasp_rank;')
        result = connection.execute(query).fetchall()

    return render_template('index.html', vulnerabilities=result)

@app.route('/incidents/<vul_id>')
def incident_page(vul_id):
    # TASK 1: Connect to the database
    with engine.connect() as connection: #might need a change
    # TASK 2: Fetch the Vulnerability Name for the heading (JOIN or separate query)
        vulnamequery = text('SELECT vul_name FROM vulnerabilities WHERE id = {};'.format(vul_id))
        vulnameresult = connection.execute(vulnamequery).fetchall()
        print(vulnameresult)
    # TASK 3: Fetch all Incidents linked to this vul_id, return incidents list
        query = text('SELECT inc_name, inc_url, inc_year FROM incidents WHERE vul_id = {};'.format(vul_id))
        result = connection.execute(query, {"vul_id": vul_id}).fetchall()
        print(result)
    # print(vul_id) #this is a print statement to help you understand what data is being returned
    return render_template('incidents.html', vulnerability = vulnameresult[0][0], vul_list = result, vul_id = vul_id)

    # result = connection.execute(query).fetchall()
    # for r in result:
    #     print(r)

@app.route('/add-incident/<vul_id>', methods = ['GET'])
def incident_form(vul_id):
    return render_template('add-incident.html', vul_id = vul_id)

@app.route('/add-incident', methods=['POST'])
def add_review():
    vul_id = request.form['vul_id']
    print(vul_id)
    company = request.form['companyname']
    print(company)
    incidenturl = request.form['incidenturl']
    print(incidenturl)
    year = request.form['year']
    print(year)

    insert_statement = '''INSERT INTO incidents (vul_id, inc_name, inc_url, inc_year) VALUES ({}, '{}', '{}', {});
    '''.format(vul_id, company, incidenturl, year)

    connection.execute(text(insert_statement))
    connection.commit()

    #return render_template('add-incident.html')
    return redirect(url_for('incident_page', vul_id = vul_id))

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/filter', methods=['GET'])
def filter_incidents():
    vulnerability = request.args.get('vulnerability', )
    year = request.args.get('year', )
    limit = request.args.get('limit', )

    conditions = []
    if vulnerability:
        conditions.append("vulnerability={}".format(vulnerability))
    if year:
        conditions.append('year>={}'.format(year))

    condition_str = ' AND '.join(conditions)
    condition_str = condition_str + " LIMIT '{}'".format(limit)

    query = text('SELECT * FROM reviews WHERE {};'.format(condition_str, limit))
    result = connection.execute(query).fetchall()

    return render_template('filter.html', incidents=result)

app.run(debug=True, reloader_type='stat', port=5000)