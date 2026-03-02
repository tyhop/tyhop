from flask import Blueprint, request, jsonify
from peewee import DoesNotExist
from com.tgu.controller.SysUserController import token_required
from com.tgu.mapper.Entitys import *

import logging

# 配置日志
logger = logging.getLogger(__name__)

traveller = Blueprint('traveller', __name__)


@traveller.route("/", methods=['GET'])
@token_required
def getAllTravellers():
    """
    获取所有旅客信息
    """
    try:
        travellers = list(Traveller.select().where(Traveller.isDeleted == False).dicts())
        return jsonify({
            "code": 200,
            "message": "成功获取所有旅客信息",
            "data": travellers
        })
    except Exception as e:
        logger.error(f"获取所有旅客信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取旅客信息失败: {str(e)}",
            "data": None
        }), 500


@traveller.route("/", methods=['POST'])
@token_required
def addTraveller(current_user):
    """
    添加新旅客
    请求体示例:
    {
        "traveller_name": "张三",
        "traveller_id": "123456789",
        "traveller_tel": "13800138000",
        "uid": "T1001"
    }
    """
    try:
        data = request.get_json()

        # # 验证必需字段
        # required_fields = ['traveller_name', 'traveller_id', 'traveller_tel', 'uid']
        # for field in required_fields:
        #     if field not in data:
        #         return jsonify({
        #             "code": 400,
        #             "message": f"缺少必需字段: {field}",
        #             "data": None
        #         }), 400

        # 检查旅客ID是否已存在
        if Traveller.select().where(Traveller.travellerId == data['traveller_id']).exists():
            return jsonify({
                "code": 400,
                "message": "旅客ID已存在",
                "data": None
            }), 400

        # 检查用户是否存在
        try:
            user = SysUser.get(SysUser.uid == data['uid'])
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "关联的用户不存在",
                "data": None
            }), 404

        # 创建旅客
        traveller = Traveller.create(
            travellerName=data['traveller_name'],
            travellerId=data['traveller_id'],
            travellerTel=data['traveller_tel'],
            uid=user.uid
        )

        return jsonify({
            "code": 201,
            "message": "旅客添加成功",
            "data": {
                "id": traveller.id,
                "traveller_name": traveller.travellerName,
                "traveller_id": traveller.travellerId,
                "traveller_tel": traveller.travellerTel,
                "uid": traveller.uid
            }
        }), 201

    except Exception as e:
        logger.error(f"添加旅客失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"添加旅客失败: {str(e)}",
            "data": None
        }), 500


@traveller.route("/user/", methods=['GET'])
@token_required
def findTravellerByUserId(current_user):
    """
    根据用户ID获取旅客信息（排除已删除的）
    """
    try:
        # 检查用户是否存在
        # try:
        #     user = SysUser.get(SysUser.uid == uid)
        # except DoesNotExist:
        #     return jsonify({
        #         "code": 404,
        #         "message": "用户不存在",
        #         "data": None
        #     }), 404

        # 获取该用户下的所有未删除旅客
        travellers = list(Traveller.select().where(
            # (Traveller.uid == user.uid) &
            (Traveller.uid == current_user.uid) &
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


@traveller.route("/user/<flight_no>", methods=['GET'])
@token_required
def findTravellerByUserIdAndFN(current_user, flight_no):
    """
    根据用户ID获取旅客信息（排除已删除的）
    """
    try:
        # 获取该用户下的所有未删除旅客
        travellers = list(Traveller.select().where(
            # (Traveller.uid == user.uid) &
            (Traveller.uid == current_user.uid) &
            (Traveller.flightNo == flight_no) &
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


@traveller.route("/<traveller_id>", methods=['GET'])
@token_required
def findTravellerById(traveller_id):
    """
    根据旅客ID获取旅客信息（排除已删除的）
    """
    try:
        traveller = Traveller.select().where(
            (Traveller.travellerId == traveller_id) &
            (Traveller.isDeleted == False)
        ).first()

        if not traveller:
            return jsonify({
                "code": 404,
                "message": "旅客不存在或已被删除",
                "data": None
            }), 404

        return jsonify({
            "code": 200,
            "message": "成功获取旅客信息",
            "data": {
                "id": traveller.id,
                "traveller_name": traveller.travellerName,
                "traveller_id": traveller.travellerId,
                "traveller_tel": traveller.travellerTel,
                "uid": traveller.uid,
                "create_time": traveller.createTime.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"根据旅客ID查询失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"查询旅客失败: {str(e)}",
            "data": None
        }), 500


@traveller.route("/", methods=['PUT'])
@token_required
def updateTraveller(current_user):
    """
    更新旅客信息（只能更新未删除的旅客）
    请求体示例:
    {
        "traveller_id": "ID123456789",
        "flight_no":"123"
    }
    """
    try:
        data = request.get_json()

        # if 'traveller_id' not in data:
        #     return jsonify({
        #         "code": 400,
        #         "message": "缺少旅客ID",
        #         "data": None
        #     }), 400

        # 查找未删除的旅客
        try:
            traveller = Traveller.get(
                (Traveller.travellerId == data['traveller_id']) &
                (Traveller.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "旅客不存在或已被删除",
                "data": None
            }), 404

        # 更新字段
        update_fields = {}
        if 'traveller_name' in data:
            update_fields[Traveller.travellerName] = data['traveller_name']
        if 'traveller_tel' in data:
            update_fields[Traveller.travellerTel] = data['traveller_tel']
        if 'flight_no' in data:
            update_fields[Traveller.flightNo] = data['flight_no']

        print(update_fields)
        if update_fields:
            Traveller.update(update_fields).where(
                (Traveller.travellerId == data['traveller_id']) &
                (Traveller.isDeleted == False)
            ).execute()
            # 重新获取更新后的旅客信息
            traveller = Traveller.get(
                (Traveller.travellerId == data['traveller_id']) &
                (Traveller.isDeleted == False)
            )

        return jsonify({
            "code": 200,
            "message": "旅客信息更新成功",
            "data": {
                "id": traveller.id,
                "traveller_name": traveller.travellerName,
                "traveller_id": traveller.travellerId,
                "traveller_tel": traveller.travellerTel,
                "flight_no": traveller.flightNo,
                "uid": traveller.uid
            }
        })

    except Exception as e:
        logger.error(f"更新旅客信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"更新旅客失败: {str(e)}",
            "data": None
        }), 500


@traveller.route("/<traveller_id>", methods=['DELETE'])
@token_required
def deleteTraveller():
    """
    请求体示例:
    {
        "traveller_id": "ID123456789"
    }
    """
    try:
        data = request.get_json()

        if 'traveller_id' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少旅客ID",
                "data": None
            }), 400

        # 检查旅客是否存在
        try:
            traveller = Traveller.get(
                (Traveller.travellerId == data['traveller_id']) &
                (Traveller.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "旅客不存在或已被删除",
                "data": None
            }), 404

        # 检查旅客是否有关联的未删除行李
        baggage_count = Baggage.select().where(
            (Baggage.travellerId == data['traveller_id']) &
            (Baggage.isDeleted == False)
        ).count()

        if baggage_count > 0:
            return jsonify({
                "code": 400,
                "message": f"该旅客有 {baggage_count} 件关联行李，无法删除",
                "data": None
            }), 400

        # 执行逻辑删除
        updated_count = Traveller.update(
            isDeleted=True
        ).where(
            (Traveller.travellerId == data['traveller_id']) &
            (Traveller.isDeleted == False)
        ).execute()

        if updated_count > 0:
            return jsonify({
                "code": 200,
                "message": "旅客删除成功",
                "data": None
            })
        else:
            return jsonify({
                "code": 500,
                "message": "旅客删除失败",
                "data": None
            }), 500

    except Exception as e:
        logger.error(f"删除旅客失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"删除旅客失败: {str(e)}",
            "data": None
        }), 500
