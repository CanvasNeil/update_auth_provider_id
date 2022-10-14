import config
import csv
import logging
import os
import time
import pandas as pd
import requests
import sys
import teams
from datetime import datetime


def create_log():
    if os.path.isdir('logs') is False:
        os.mkdir('logs')
    logfile = os.path.join('logs', f'{TASK_ID}.log')
    logging.basicConfig(
        filename=logfile,
        filemode='w',
        encoding='utf-8',
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s',
    )
    logging.info(f'TASK_ID: {TASK_ID}\n')


def create_output_file():
    logging.info(f'{"="*9} CREATE OUTPUT STATUS FILE {"="*9}')
    try:
        header = [
            'user_id',
            'email',
            'created_at',
            'sis_user_id',
            'login_id',
            'authentication_provider_id',
            'update_status'
        ]
        if os.path.isdir('user_provisioning_reports') is False:
            os.mkdir('user_provisioning_reports')
        output_filename = os.path.join('user_provisioning_reports', f'{TASK_ID}.csv')
        with open(output_filename, 'w', newline ='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        logging.info(f'File {output_filename} created with headers\n')
        return output_filename
    except Exception as e:
        logging.exception(f'Error creating output file: {e}')
        sys.exit(1)


def update_output_file(data):
    try:
        with open(SUMMARY_FILE, 'a', newline ='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    except Exception as e:
        logging.info(f'Unexpected error updating status file. Data: {data}')
        logging.exception(f'{e}')
        sys.exit(1)


def generate_user_provisioning_report():
    logging.info(f'{"="*9} GENERATE USER PROVISIONING REPORT {"="*9}')
    url = f'{BASE_URL}/api/v1/accounts/1/reports/provisioning_csv'
    payload = {
        'parameters': {
            'enrollment_term_id': '',
            'users': '1'
        }
    }
    attempt = 0
    while True:
        attempt += 1
        res = requests.post(url, json=payload, headers=TOKEN)
        if res.status_code == 200:
            report_id = res.json()['id']
            logging.info(f'Report ID: {report_id}')
            return report_id
        else:
            if MAX_RETRY > attempt:
                time.sleep(1)
            else:
                raise RuntimeError('Maximum number of attempts exceeded, aborting.')


def is_report_running(report_id):
    logging.info(f'Check report status')
    url = f'{BASE_URL}/api/v1/accounts/1/reports/provisioning_csv/{report_id}'
    attempt = 0
    while True:
        attempt += 1
        res = requests.get(url, headers=TOKEN)
        if res.status_code == 200:
            progress = res.json()['progress']
            if progress == 100:
                logging.info(f'Progress: {progress}%')
                return False
            else:
                logging.info(f'Progress: {progress}%')
                return True
        else:
            if MAX_RETRY > attempt:
                time.sleep(1)
            else:
                raise RuntimeError('Maximum number of attempts exceeded, aborting.')


def download_report(report_id):
    logging.info(f'Download report')
    url = f'{BASE_URL}/api/v1/accounts/1/reports/provisioning_csv/{report_id}'
    attempt = 0
    while True:
        # Get report url and name
        attempt += 1
        res = requests.get(url, headers=TOKEN)
        if res.status_code == 200:
            file_url = res.json()['attachment']['url']
            filename = res.json()['attachment']['filename']

            # Download report
            while True:
                res = requests.get(file_url)
                if res.status_code == 200:
                    filename = os.path.join('user_provisioning_reports', 'canvas_users.csv')
                    with open(filename, 'wb') as f:
                        f.write(res.content)
                    logging.info(f'Filename: {filename}\n')
                    return filename
        else:
            if MAX_RETRY > attempt:
                time.sleep(1)
            else:
                raise RuntimeError('Maximum number of attempts exceeded, aborting.')


def get_null_auth_users(file):
    logging.info(f'{"="*9} UPDATE NULL AUTH PROVIDER ID {"="*9}')
    logging.info('Filter users with null authentication provider ID')
    df = pd.read_csv(file)
    df = df.query('authentication_provider_id.isnull()', engine='python')
    users = df['canvas_user_id'].to_list()
    users = list(set(users))
    logging.info(f'Users: {users}')
    return users


def update_null_auth(login_id):
    global UPDATED_USER_LOGINS
    url = f'{BASE_URL}/api/v1/accounts/1/logins/{login_id}'
    data = {
        'login': {
            'authentication_provider_id': CANVAS_AUTH_ID
        }
    }
    res = requests.put(url, json=data, headers=TOKEN)
    status_code = res.status_code
    if status_code == 200:
        UPDATED_USER_LOGINS += 1
    logging.info(f'Auth ID update status: {status_code}')
    return status_code


def get_logins(user_id):
    url = f'{BASE_URL}/api/v1/users/{user_id}/logins'
    attempt = 0
    while True:
        attempt += 1
        res = requests.get(url, headers=TOKEN)
        if res.status_code == 200:
            logins = res.json()
            for login in logins:
                login_id = login['id']
                email = login.get('unique_id', '')
                created_at = login.get('created_at', '')
                sis_user_id = login.get('sis_user_id', '')
                auth_id = login['authentication_provider_id']

                if auth_id is None:
                    logging.info(f'Null Auth ID Found: {user_id}, Login ID: {login_id}')
                    res_status = update_null_auth(login_id)
                    data = [user_id, email, created_at, sis_user_id, login_id, auth_id, res_status]
                    update_output_file(data)
            break
        else:
            if MAX_RETRY > attempt:
                time.sleep(1)
            else:
                raise RuntimeError('Maximum number of attempts exceeded, aborting.')


def main():
    start = time.time()
    try:
        report_id = generate_user_provisioning_report()

        # Exit loop when report complete
        while is_report_running(report_id=report_id):
            time.sleep(5)

        filename = download_report(report_id=report_id)
        users = get_null_auth_users(file=filename)
        print(len(users))


        for user_id in users:
            get_logins(user_id)

    except Exception as e:
        logging.exception(e)
        runtime = time.time() - start
        teams.error_alert(ERROR_HOOK, runtime, f'{TASK_ID}.csv', f'{TASK_ID}.log')

    else:
        runtime = time.time() - start
        if UPDATED_USER_LOGINS > 0:
            teams.success_alert(SUCCESS_HOOK, runtime, UPDATED_USER_LOGINS, f'{TASK_ID}.csv', f'{TASK_ID}.log')


if __name__ == '__main__':
    TASK_ID = 'fix_null_id_'+datetime.now().strftime('%d-%m-%y_%S')
    create_log()

    MAX_RETRY = config.MAX_RETRY
    TOKEN = {'Authorization': f'Bearer {config.CANVAS_TOKEN}'}
    BASE_URL = config.BASE_URL
    CANVAS_AUTH_ID = config.CANVAS_AUTH_ID

    ERROR_HOOK = config.ERROR_HOOK
    SUCCESS_HOOK = config.SUCCESS_HOOK

    SUMMARY_FILE = create_output_file()
    UPDATED_USER_LOGINS = 0

    main()