from flask import Blueprint, request, jsonify
from peewee import DoesNotExist
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from com.tgu.mapper.Entitys import *
import logging

# 配置日志
logger = logging.getLogger(__name__)

sys_user = Blueprint('sys_user', __name__)

# JWT配置
JWT_SECRET_KEY = '12345678'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=24)


# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({
                'code': 401,
                'message': '访问令牌缺失',
                'data': None
            }), 401

        try:
            # 解码token
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            current_user = SysUser.get(SysUser.id == data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({
                'code': 401,
                'message': '访问令牌已过期',
                'data': None
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'code': 401,
                'message': '无效的访问令牌',
                'data': None
            }), 401
        except DoesNotExist:
            return jsonify({
                'code': 401,
                'message': '用户不存在',
                'data': None
            }), 401
        except Exception as e:
            logger.error(f"Token验证失败: {str(e)}")
            return jsonify({
                'code': 500,
                'message': '令牌验证失败',
                'data': None
            }), 500

        return f(current_user, *args, **kwargs)

    return decorated


# 生成JWT token
def generateToken(user):
    try:
        payload = {
            'user_id': user.id,
            'uid': user.uid,
            'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA,
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logger.error(f"生成Token失败: {str(e)}")
        raise e


@sys_user.route("/register", methods=['POST'])
def register():
    """
    用户注册
    请求体示例:
    {
        "uid": "user123",
        "pwd": "password123",
        "nick_name": "用户昵称"
    }
    """
    try:
        data = request.get_json()

        # 检查用户ID是否已存在
        if SysUser.select().where(SysUser.uid == data['uid']).exists():
            return jsonify({
                "code": 400,
                "message": "用户ID已存在",
                "data": None
            }), 400

        # 密码强度验证
        if len(data['pwd']) < 6:
            return jsonify({
                "code": 400,
                "message": "密码长度至少6位",
                "data": None
            }), 400

        # 创建用户 - 密码使用哈希加密
        user = SysUser.create(
            uid=data['uid'],
            pwd=generate_password_hash(data['pwd']),
            nickName=data.get('nick_name', data['uid'])  # 如果没有提供昵称，使用用户ID
        )

        # 生成JWT token
        token = generateToken(user)

        return jsonify({
            "code": 201,
            "message": "用户注册成功",
            "data": {
                "id": user.id,
                "uid": user.uid,
                "nick_name": user.nickName,
                "create_time": user.createTime,
                "token": token
            }
        }), 201

    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"用户注册失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/login", methods=['POST'])
def login():
    """
    用户登录
    请求体示例:
    {
        "uid": "user123",
        "pwd": "password123"
    }
    """
    try:
        data = request.get_json()

        # 查找用户
        try:
            user = SysUser.get(SysUser.uid == data['uid'])
        except DoesNotExist:
            return jsonify({
                "code": 401,
                "message": "用户名或密码错误",
                "data": None
            }), 401

        # 验证密码
        if not check_password_hash(user.pwd, data['pwd']):
            return jsonify({
                "code": 401,
                "message": "用户名或密码错误",
                "data": None
            }), 401

        # 检查用户是否被删除
        if user.isDeleted:
            return jsonify({
                "code": 401,
                "message": "用户已被删除",
                "data": None
            }), 401

        # 生成JWT token
        token = generateToken(user)

        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {
                "id": user.id,
                "uid": user.uid,
                "nick_name": user.nickName,
                "create_time": user.createTime.isoformat(),
                "token": token
            }
        })

    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"登录失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/profile", methods=['GET'])
@token_required
def getProfile(current_user):
    """
    获取当前用户信息（需要token认证）
    """
    try:
        return jsonify({
            "code": 200,
            "message": "获取用户信息成功",
            "data": {
                "id": current_user.id,
                "uid": current_user.uid,
                "nick_name": current_user.nickName,
                "create_time": current_user.createTime.isoformat(),
                "is_deleted": current_user.isDeleted
            }
        })

    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取用户信息失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/profile", methods=['POST'])
@token_required
def updateProfile(current_user):
    """
    更新用户信息（需要token认证）
    请求体示例:
    {
        "nick_name": "新的昵称",
        "old_pwd": "旧密码",  // 修改密码时需要
        "new_pwd": "新密码"   // 修改密码时需要
    }
    """
    try:
        data = request.get_json()

        update_fields = {}

        # 更新昵称
        if 'nick_name' in data:
            update_fields[SysUser.nickName] = data['nick_name']

        # 更新密码（需要验证旧密码）
        if 'new_pwd' in data:
            if 'old_pwd' not in data:
                return jsonify({
                    "code": 400,
                    "message": "修改密码需要提供旧密码",
                    "data": None
                }), 400

            # 验证旧密码
            if not check_password_hash(current_user.pwd, data['old_pwd']):
                return jsonify({
                    "code": 400,
                    "message": "旧密码错误",
                    "data": None
                }), 400

            # 验证新密码强度
            if len(data['new_pwd']) < 6:
                return jsonify({
                    "code": 400,
                    "message": "新密码长度至少6位",
                    "data": None
                }), 400

            update_fields[SysUser.pwd] = generate_password_hash(data['new_pwd'])

        if update_fields:
            SysUser.update(**update_fields).where(SysUser.id == current_user.id).execute()
            # 重新获取更新后的用户信息
            current_user = SysUser.get_by_id(current_user.id)

        return jsonify({
            "code": 200,
            "message": "用户信息更新成功",
            "data": {
                "id": current_user.id,
                "uid": current_user.uid,
                "nick_name": current_user.nickName,
            }
        })

    except Exception as e:
        logger.error(f"更新用户信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"更新用户信息失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/", methods=['GET'])
@token_required
def getAllUsers(current_user):
    """
    获取所有用户信息（需要token认证，管理员功能）
    """
    try:
        users = list(SysUser.select().where(SysUser.isDeleted == False).dicts())

        # 从结果中移除密码字段
        for user in users:
            user.pop('pwd', None)

        return jsonify({
            "code": 200,
            "message": "成功获取所有用户信息",
            "data": users
        })

    except Exception as e:
        logger.error(f"获取所有用户信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取用户信息失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/<uid>  ", methods=['DELETE'])
@token_required
def deleteUser(current_user):
    """
    请求体示例:
    {
        "uid": "要删除的用户ID"  // 如果是管理员删除其他用户
    }
    """
    try:
        data = request.get_json()
        target_uid = data.get('uid', current_user.uid)  # 默认删除当前用户

        # 检查是否尝试删除自己
        if target_uid == current_user.uid:
            # 用户删除自己
            # 检查是否有未完成的业务（如未处理的行李等）
            traveller_count = Traveller.select().where(
                (Traveller.uid == current_user.uid) &
                (Traveller.isDeleted == False)
            ).count()

            if traveller_count > 0:
                return jsonify({
                    "code": 400,
                    "message": f"您有 {traveller_count} 个关联旅客，无法删除账户",
                    "data": None
                }), 400

            # 执行逻辑删除
            updated_count = SysUser.update(
                isDeleted=True
            ).where(
                (SysUser.id == current_user.id) &
                (SysUser.isDeleted == False)
            ).execute()

            if updated_count > 0:
                return jsonify({
                    "code": 200,
                    "message": "用户删除成功",
                    "data": None
                })
            else:
                return jsonify({
                    "code": 500,
                    "message": "用户删除失败",
                    "data": None
                }), 500
        else:
            # 管理员删除其他用户（这里可以添加管理员权限检查）
            # 暂时只允许用户删除自己
            return jsonify({
                "code": 403,
                "message": "无权删除其他用户",
                "data": None
            }), 403

    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"删除用户失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/refresh", methods=['POST'])
@token_required
def refreshToken(current_user):
    """
    刷新JWT token（需要token认证）
    """
    try:
        # 生成新的token
        new_token = generateToken(current_user)

        return jsonify({
            "code": 200,
            "message": "Token刷新成功",
            "data": {
                "token": new_token,
                "uid": current_user.uid,
                "nick_name": current_user.nickName
            }
        })

    except Exception as e:
        logger.error(f"刷新Token失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"刷新Token失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/verify", methods=['POST'])
def verifyToken():
    """
    验证token有效性
    请求体示例:
    {
        "token": "jwt_token_string"
    }
    """
    try:
        data = request.get_json()

        if 'token' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少token参数",
                "data": None
            }), 400

        token = data['token']

        try:
            # 解码token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = SysUser.get(SysUser.id == payload['user_id'])

            return jsonify({
                "code": 200,
                "message": "Token有效",
                "data": {
                    "valid": True,
                    "uid": user.uid,
                    "nick_name": user.nickName,
                    "expires_at": datetime.datetime.fromtimestamp(payload['exp']).isoformat()
                }
            })

        except jwt.ExpiredSignatureError:
            return jsonify({
                "code": 401,
                "message": "Token已过期",
                "data": {"valid": False}
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "code": 401,
                "message": "无效Token",
                "data": {"valid": False}
            }), 401

    except Exception as e:
        logger.error(f"验证Token失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"验证Token失败: {str(e)}",
            "data": None
        }), 500


@sys_user.route("/flights", methods=['GET'])
@token_required
def getFlights(current_user):
    """
    获取当前用户信息（需要token认证）
    """
    try:
        travellers = list(Traveller.select().where(
            (Traveller.uid == current_user.uid) &
            (Traveller.flightNo != None) &
            (Traveller.isDeleted == False)
        ).dicts())

        return jsonify({
            "code": 200,
            "message": "成功获取旅客信息",
            "data": travellers
        })

    except Exception as e:
        logger.error(f"根据用户ID查询旅客失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"查询旅客失败: {str(e)}",
            "data": None
        }), 500
