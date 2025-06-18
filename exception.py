from schemas.base_response import BaseResponse

EXCEPTION_CODE = {
100001 : 'User not found!',
100002 : "Wrong password!",
100003 : 'Username already exist!',
100004 : 'Register Failed',
100005 : 'Update Password Failed',
100006: 'Flower not found!',
100007: 'Not enough flower!',
100008:'Only for user',
100009:'Invalid date',
100010:'Only for admin!',
100011:'Bill not found!',
100012: 'Rank already exist!',
100013 : 'Rank not found',
100014: 'Quantity should be greater than 0!',

}

def raise_error(error_code: int) -> BaseResponse:
    return BaseResponse(
        message=EXCEPTION_CODE.get(error_code),
        status='error',
    )