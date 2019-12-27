from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from MainApp.models import Employee, Office, User_Data, User_Type, Office_Employee
from django.contrib.auth.models import User

# Create your views here.

def index(request):
	return render(request, 'mainapp/index.html')

def login_page(request):
	return render(request, 'mainapp/login.html')

def create_user_page(request):
	return render(request, 'mainapp/create_user.html')

def create_user(request):
	
	if request.method == 'POST':

		all_users = User_Data.objects.all()

		employee_id = request.POST['employee_id']
		first_name = request.POST['first_name']
		middle_name = request.POST['middle_name']
		last_name = request.POST['last_name']
		email = request.POST['email']
		user_name = request.POST['user_name']
		password = request.POST['password']
		
		user_type_id = None

		if len(all_users) == 0:

			user_type = User_Type(type_name="Administrator", type_description="Administrative Level Access")
			user_type.save()
			user_type_id = user_type


		else:
			
			user_types = User_Type.objects.all()
			
			if len(user_types) == 1:
				
				user_type = User_Type(type_name="User", type_description="User Level Access")
				user_type.save()
				user_type_id = user_type
			
			else:

				user_type = User_Type.objects.get(type_name = "User")
				user_type_id  = user_type

		employee = Employee(id_code = employee_id, first_name = first_name, middle_name = middle_name, last_name = last_name, email = email)

		employee.save()
		employee_gen_id = employee

		user = User_Data(user_name = user_name, user_password = password, employee_id = employee_gen_id, user_type = user_type_id)

		user.save()

		django_user = User.objects.create_user(username = user_name, email = email, password = password)


	return HttpResponseRedirect('/login')

def login(request):

	if request.method == 'POST':

		username = request.POST['username']
		password = request.POST['password']

		user_log_in_fetch = None
		output = ''

		try:
			user_log_in_fetch = User_Data.objects.get(user_name = username, user_password = password)
			output = "Log in"
		
		except Exception as e:
			output = "Wrong Log in"

		return HttpResponse(output)


