import re
from .models import User, AuthSMS

def check_auth(user_hp:str, user_auth:str)->bool:
    '''
    휴대폰번호를 쿼리로 인증번호가 매치되는지 찾는 함수
    '''
    c_auth = AuthSMS.objects.get(hp=user_hp).auth
    c_auth = str(c_auth)

    if c_auth == user_auth:
        return True
    elif c_auth != user_auth:
        return False


def register_errors(form)->dict:
    errors = {}
    fcd = form.cleaned_data
    print(fcd)

     # 입력하지 않았을때 에러메세지
    if 'user_id' not in fcd:
        errors['user_id'] = '아이디를 입력하세요.'
    else:
        # if fcd['user_id'][0].isalpha() != True:
        #     errors['user_id'] = '아이디는 숫자로 시작할 수 없습니다.'
        if re.sub('[^A-Za-z0-9_]', '', fcd['user_id']) != fcd['user_id']:
            errors['user_id'] = '아이디는 4~15자의 영문, 숫자, 아래첨자(_) 로 이루어져야 합니다.'
        if len(fcd['user_id']) > 15:
            errors['user_id'] = '아이디는 4~15자의 영문, 숫자, 아래첨자(_) 로 이루어져야 합니다.'
        if len(fcd['user_id']) < 4:
            errors['user_id'] = '아이디는 4~15자의 영문, 숫자, 아래첨자(_) 로 이루어져야 합니다.'

    
    if 'password2' not in fcd:
        errors['password2'] = '비밀번호를 입력하세요.'
    if 'password1' not in fcd:
        errors['password1'] = '비밀번호를 입력하세요.'
        
    if 'hp' not in fcd:
        errors['hp'] = '휴대폰번호를 입력하세요.'
    else:
        if len(fcd['hp']) != 11:
            errors['hp'] = '휴대폰번호 형식을 확인해주세요.'

    if 'auth' not in fcd:
        errors['auth'] = '인증번호를 입력하세요.'
    else:
        if len(fcd['auth']) != 6:
            errors['auth'] = '인증번호를 확인해주세요.'

        else:
            if AuthSMS.check_timer(fcd['hp'], fcd['auth']) == False:
                errors['auth'] = '인증번호 시간 초과'

            if (check_auth(fcd['hp'], fcd['auth']))==False:
                errors['auth'] = '인증번호를 확인해주세요.'

    return errors
