# login
# ===========================================================
from flask import Blueprint, redirect, request, session, jsonify
from dotenv import load_dotenv
from src.helpers.utils import generate_random_string
from src.helpers.jwt_utils import create_jwt, validate_jwt
from urllib.parse import urlencode

import os
import urllib.parse
import urllib.request
import json

auth = Blueprint('auth', __name__)

# Konfigurasi
client_id = os.environ.get('IDPRO_CLIENT_ID')
client_secret = os.environ.get('IDPRO_CLIENT_SECRET')
base_url = os.environ.get('IDPRO_BASE_URL')
redirect_uri = os.environ.get('IDPRO_REDIRECT_URL')
scope = os.environ.get('IDPRO_SCOPE')
state = generate_random_string(length=10, use_digits=True, use_uppercase=True, use_lowercase=True, use_special=False)

# URL untuk authorization
@auth.route('/login')
def login():
    return 'tes'
    auth_url = f"{base_url}/authorize"
    query_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scope,
        'state': state
    }
    auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(query_params)}"
    return redirect(auth_url_with_params)

# callback
# ===========================================================
@auth.route('/callback')
def callback():
    
    code = request.args.get('code')
    
    if not code:
        return "Authorization code not found", 400
        
    token_url = f"{base_url}/token"
    try:
        data = urllib.parse.urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'code': code,
            'grant_type': 'authorization_code'
        }).encode()

        req = urllib.request.Request(token_url, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        req.add_header('Accept-Language', 'en-US,en;q=0.5')

        with urllib.request.urlopen(req) as response:
            token_json = json.loads(response.read())

    except urllib.error.HTTPError as e:
        return f"Error during token request: {str(e)}", 500
    except ValueError:
        return "Failed to parse token response", 500

    access_token_sso = token_json.get('access_token')
    if not access_token_sso:
        return "Access token not found in the response", 500

    # Mendapatkan informasi pengguna dari SSO
    userinfo_url = f"{base_url}/userinfo"
    try:
        userinfo_req = urllib.request.Request(userinfo_url)
        userinfo_req.add_header('Authorization', f'Bearer {access_token_sso}')
        userinfo_req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        userinfo_req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
        userinfo_req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        userinfo_req.add_header('Accept-Language', 'en-US,en;q=0.5')
        
        with urllib.request.urlopen(userinfo_req) as response:
            user_info = json.loads(response.read())
    except urllib.error.HTTPError as e:
        return f"Error during user info request: {str(e)}", 500
    
    # Buat access token dan refresh token
    # jwt_payload = {
    #     "user_id": user_info.get("employee_id"),
    #     "roles": user_info.get("roles", ["user"]),
    #     "name": user_info.get("display_name"),
    #     "email": user_info.get("email"),
    #     "client_name": user_info.get("client_name"),
    #     "state": user_info.get("state"),
    #     "company_code": user_info.get("company_code"),
    #     "upn": user_info.get("upn"),
    #     "primary_sid": user_info.get("PrimarySid"),
    #     "nip": user_info["info"].get("NIP"),
    #     "nip_baru": user_info["info"].get("NIPBaru"),
    #     "nama_pegawai": user_info["info"].get("NamaPegawai"),
    #     "kode_unit_kerja": user_info["info"].get("KodeUnitKerja"),
    #     "nama_unit_kerja": user_info["info"].get("NamaUnitKerja"),
    #     "kode_eselon": user_info["info"].get("KodeEselon"),
    #     "nama_eselon": user_info["info"].get("NamaEselon"),
    #     "kode_unit_kerja_asli": user_info["info"].get("KodeUnitKerjaAsli"),
    #     "nama_unit_kerja_asli": user_info["info"].get("NamaUnitKerjaAsli"),
    #     "kode_eselon_asli": user_info["info"].get("KodeEselonAsli"),
    #     "nama_eselon_asli": user_info["info"].get("NamaEselonAsli"),
    #     "nama_jabatan": user_info["info"].get("NamaJabatan"),
    #     "nama_lengkap": user_info["info"].get("NamaLengkap"),
    #     "nomor_handphone": user_info["info"].get("NomorHandphone"),
    #     "nomor_handphone2": user_info["info"].get("NomorHandphone2"),
    #     "nik": user_info["info"].get("NIK"),
    #     "jenis_kelamin": user_info["info"].get("JenisKelamin"),
    #     "is_aktif": user_info["info"].get("isAktif"),
    #     "keterangan": user_info["info"].get("Keterangan"),
    #     "jenis_jabatan_cur": user_info["info"].get("JnsJabatanCur")
    # }

    # access_token = create_jwt(jwt_payload)
    # refresh_token = create_jwt({"user_id": user_info.get("employee_id")}, 
    #                             exp_minutes=int(os.environ.get("JWT_REFRESH_EXPIRATION_MINUTES")))    

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,   
        "refresh_token": refresh_token,
        "access_token_sso": access_token_sso,
        "code_sso": code,
        "id_token": token_json.get('id_token'),
    })
    
    # session['access_token_sso'] = access_token_sso
    # session['access_token'] = access_token
    # session['refresh_token'] = refresh_token
    # session['id_token'] = token_json.get('id_token')
    
    # frontend_url = os.environ.get('FRONTEND_HOST_URL', 'http://localhost:5173')
    # return redirect(
    #     f"{frontend_url}/#/auth/callback?"
    #     f"access_token={access_token}&"
    #     f"access_token_sso={access_token_sso}&"
    #     f"refresh_token={refresh_token}&"
    #     f"session_id={session.sid}"  # Tambahkan session ID ke query parameter
    # )
    
    
# logout
# ===========================================================
def get_logout_url(base_url: str, redirect_uri: str, id_token_hint: str = None, **additional_parameters) -> str:
    logout_url = f"{base_url}/endsession"
    params = {
        'post_logout_redirect_uri': redirect_uri,
        'id_token_hint': id_token_hint
    }
    params.update(additional_parameters)

    return f"{logout_url}?{urlencode(params)}"

@auth.route('/logout', methods=['POST'])
def logout():
    print("Headers:", request.headers)
    print("Cookies:", request.cookies)
    print("Session Data:", session)
    id_token = session.get('id_token')

    redirect_uri = 'http://0.0.0.0:5000'

    logout_url = get_logout_url(
        base_url=base_url,
        redirect_uri=redirect_uri,
        id_token_hint=id_token,
        client_id=client_id
    )
    
    session.clear()

    return jsonify({"logout_url": logout_url})





