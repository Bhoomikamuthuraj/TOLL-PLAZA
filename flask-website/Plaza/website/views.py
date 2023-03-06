from flask import Blueprint, render_template

views = Blueprint("views",__name__)

name = 'User'

@views.route("/user")
def user_homepage():
    return render_template("user.html", name=name)

@views.route("/prebook")
def user_prebook():
    return render_template("prebook.html")

@views.route("/addtowallet")
def user_addtowallet():
    return render_template("addtowallet.html")

@views.route("/payment")
def user_payment():
    return render_template("payment.html")

@views.route("/profile")
def user_profile():
    return render_template("profile.html", name=name)

@views.route("/admin")
def admin_homepage():
    return render_template("admin.html")

@views.route("/acc_rej_users")
def admin_acc_rej_users():
    return render_template("acc_rej_users.html")

@views.route("/view_reg_users")
def admin_view_reg_users():
    return render_template("view_reg_users.html")

@views.route("/rej_users")
def admin_rej_users():
    return render_template("rej_users.html")

@views.route("/add_del_tollplaza")
def admin_add_del_tollplaza():
    return render_template("add_del_tollplaza.html")

@views.route("/tollplaza")
def tollplaza_homepage():
    return render_template("tollplaza.html")