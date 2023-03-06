from flask import Blueprint, render_template, redirect, url_for, request #wherever there is form tag u have to use request

auth = Blueprint("auth",__name__)

@auth.route("/", methods = ['GET','POST']) #whereever there is form tag
def index():
    admin_login_email = request.form.get("admin_login_email")
    admin_login_password = request.form.get("admin_login_password")

    print(admin_login_email, admin_login_password)

    tollplaza_login_email = request.form.get("tollplaza_login_email")
    tollplaza_login_password = request.form.get("tollplaza_login_password")

    print(tollplaza_login_email, tollplaza_login_password)

    user_login_email = request.form.get("user_login_email")
    user_login_password = request.form.get("user_login_password")

    print(user_login_email, user_login_password)

    return render_template("index.html")

@auth.route("/signin", methods = ['GET','POST'])
def user_signin():
    signin_dl_id = request.form.get("signin_dl_id")
    signin_name = request.form.get("signin_name")
    signin_vehicle_no = request.form.get("signin_vehicle_no")
    signin_vehicletype = request.form.get("signin_vehicletype")
    signin_city = request.form.get("signin_city")
    signin_state = request.form.get("signin_state")
    signin_ph_no = request.form.get("signin_ph_no")
    signin_email = request.form.get("signin_email")
    signin_password = request.form.get("signin_password")
    signin_re_password = request.form.get("signin_re_password")

    print(signin_dl_id, signin_name, signin_vehicle_no, signin_vehicletype, signin_city, signin_state, signin_ph_no, signin_email, signin_password, signin_re_password)

    return render_template("signin.html")

@auth.route("/logout")
def logout():
    return redirect(url_for("auth.index"))