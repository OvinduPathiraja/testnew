from flask import Flask, render_template, request, redirect, flash
from boto3.dynamodb.conditions import Key, Attr
import config
import boto3


app = Flask(__name__, static_url_path='/static')

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=config.ACCESS_KEY,
    aws_secret_access_key=config.SECRET_ACCESS_KEY,
    region_name=config.REGION
)



@app.route('/')
def index():
    return render_template('home.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('full-name')
        registration_number = request.form.get('registration-number')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        degree_program = request.form.get('degree-program')
        contact_number = request.form.get('contact-number')
        introduction = request.form.get('introduction')
        current_gpa = request.form.get('current-gpa')
        skills = request.form.get('skills')

        table = dynamodb.Table('signup_db')

        table.put_item(
            Item={
                'name': name,
                'registration_number': registration_number,
                'email': email,
                'password': password,
                'degree_program': degree_program,
                'contact_number': contact_number,
                'introduction': introduction,
                'current_gpa': current_gpa,
                'skills': skills
            }
        )
     
        msg = "Registration Complete. Please Login to your account!"
        return render_template('login.html', msg=msg)

    # Handle the GET method here
    return render_template('signup.html')




from flask import url_for

@app.route('/login', methods=['POST', 'GET'])
def check():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        table = dynamodb.Table('signup_db')  # Update with the correct table name
        response = table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']

        if items and password == items[0]['password']:
            user_data = items[0]  # Get user data from DynamoDB
            return redirect(url_for('profile_edit', **user_data))  # Pass user data as URL parameters
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template("login.html")


@app.route('/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    if request.method == 'POST':
        name = request.form['full-name']
        registration_number = request.form['registration-number']
        password = request.form['password']
        degree_program = request.form['degree-program']
        contact_number = request.form['contact-number']
        introduction = request.form['introduction']
        current_gpa = request.form['current-gpa']
        skills = request.form['skills']
        email = request.form['email']

        table = dynamodb.Table('signup_db')
        table.update_item(
            Key={'email': email},
            UpdateExpression='SET #n = :name, #rn = :registration_number, #p = :password, '
                             '#dp = :degree_program, #cn = :contact_number, #i = :introduction, '
                             '#cg = :current_gpa, #s = :skills',
            ExpressionAttributeNames={
                '#n': 'name',
                '#rn': 'registration_number',
                '#p': 'password',
                '#dp': 'degree_program',
                '#cn': 'contact_number',
                '#i': 'introduction',
                '#cg': 'current_gpa',
                '#s': 'skills'
            },
            ExpressionAttributeValues={
                ':name': name,
                ':registration_number': registration_number,
                ':password': password,
                ':degree_program': degree_program,
                ':contact_number': contact_number,
                ':introduction': introduction,
                ':current_gpa': current_gpa,
                ':skills': skills
            }
        )

        msg = "Profile Updated Successfully!"
        return render_template("profile.edit.html", msg=msg, user_data=request.form)

    user_data = request.args.to_dict()  # Get user data from URL parameters
    return render_template('profile.edit.html', user_data=user_data)


@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        email = request.form['email']

        table = dynamodb.Table('signup_db')
        response = table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']

        if items:
            user_data = items[0]
            return redirect(url_for('profile_edit', **user_data))
        else:
            flash('User not found.', 'error')

    return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/profile-view', methods=['GET'])
def public_profile():
    registration_number = request.args.get('registration_number')
    if registration_number:
        table = dynamodb.Table('signup_db')
        response = table.scan(
            FilterExpression=Attr('registration_number').eq(registration_number)
        )
        items = response['Items']
        
        if items:
            user_profile = items[0]
            user_profile.pop('password', None)  # Remove the 'password' field from the profile
            
            return render_template('profile-view.html', user_profile=user_profile)
        else:
            flash('User not found.', 'error')
    else:
        flash('Invalid registration number.', 'error')
    
    return redirect('home')

@app.route('/home')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
