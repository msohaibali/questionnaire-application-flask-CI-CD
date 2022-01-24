from flask import Blueprint, jsonify, render_template,send_from_directory, make_response
import os
from flask_login import login_required, current_user
from werkzeug.utils import redirect

pdf = Blueprint('pdf', __name__)

@pdf.route('/pdf')
def pdf_viewer():
    file_name = 'sample'
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '\\docs\\'
    filepath = filepath + file_name + '.pdf'

    with open(filepath, "rb") as binary_pdf:
        # binary_pdf = fl.read()

        response = make_response(binary_pdf)

        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
            'inline; filename=%s.pdf' % file_name
    return response

    # return redirect(filepath)

# @pdf.route('/profile')
# @login_required
# def get_profile():
#     return render_template('profile.html', username=current_user.username)
