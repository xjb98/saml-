from flask import Flask, request, redirect, session, url_for, render_template
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=os.path.join(os.path.dirname(__file__), 'saml'))
    return auth

def prepare_flask_request(request):
    url_data = request.url.split('?')
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        'query_string': request.query_string.decode('utf-8')
    }

@app.route('/')
def index():
    if 'samlUserdata' in session:
        return render_template('index.html', user=session['samlUserdata'])
    return render_template('login.html')

@app.route('/login')
def login():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    return redirect(auth.login())

@app.route('/saml/acs', methods=['POST'])
def acs():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    auth.process_response()
    errors = auth.get_errors()
    
    if not errors:
        if auth.is_authenticated():
            session['samlUserdata'] = auth.get_attributes()
            session['nameId'] = auth.get_nameid()
            session['sessionIndex'] = auth.get_session_index()
            return redirect(url_for('index'))
    
    return 'Error: ' + ', '.join(errors)

@app.route('/logout')
def logout():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    name_id = session.get('nameId')
    session_index = session.get('sessionIndex')
    session.clear()
    
    if name_id and session_index:
        return redirect(auth.logout(name_id=name_id, session_index=session_index))
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 确保 'saml/sp.cer' 和 'saml/sp.key' 文件存在
    # 可能需要安装 pyOpenSSL: pip install pyOpenSSL
    app.run(debug=True, ssl_context=('saml/sp.cer', 'saml/sp.key'))