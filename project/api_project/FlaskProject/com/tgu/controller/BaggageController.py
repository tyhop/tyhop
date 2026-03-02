from flask import Blueprint, request, jsonify
from peewee import DoesNotExist
from com.tgu.mapper.Entitys import *
from com.tgu.controller.SysUserController import token_required
import logging
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

baggage = Blueprint('baggage', __name__)

# 行李状态定义
BAGGAGE_STATUS = {
    0: "待检验",
    1: "已通过",
    2: "未通过"
}


@baggage.route("/", methods=['POST'])
@token_required
def addBaggage(current_user):
    """
    添加行李信息（需要token认证）
    请求体示例:
    {
        "type": 1,  // 行李类型
        "traveller_id": "T123456",  // 旅客ID
        "flight_no": "CA1234",  // 航班号
        "travel_begin_time": "2023-12-01 10:00:00"  // 行程开始时间
    }
    """
    try:
        data = request.get_json()

        # 验证必需字段
        # required_fields = ['type', 'traveller_id', 'flight_no', 'travel_begin_time']
        # for field in required_fields:
        #     if field not in data:
        #         return jsonify({
        #             "code": 400,
        #             "message": f"缺少必需字段: {field}",
        #             "data": None
        #         }), 400

        # 检查旅客是否存在且属于当前用户
        # try:
        #     traveller = Traveller.get(
        #         (Traveller.travellerId == data['traveller_id']) &
        #         (Traveller.uid == current_user.uid) &
        #         (Traveller.isDeleted == False)
        #     )
        # except DoesNotExist:
        #     return jsonify({
        #         "code": 404,
        #         "message": "旅客不存在或不属于当前用户",
        #         "data": None
        #     }), 404

        # 检查航班是否存在
        # try:
        #     flight = FlightInfo.get(
        #         (FlightInfo.flightNo == data['flight_no']) &
        #         (FlightInfo.isDeleted == False)
        #     )
        # except DoesNotExist:
        #     return jsonify({
        #         "code": 404,
        #         "message": "航班不存在",
        #         "data": None
        #     }), 404

        # 解析时间字符串
        # try:
        #     travel_begin_time = datetime.strptime(data['travel_begin_time'], '%Y-%m-%d %H:%M:%S')
        # except ValueError:
        #     return jsonify({
        #         "code": 400,
        #         "message": "时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式",
        #         "data": None
        #     }), 400

        # 创建行李记录 - 初始状态为待检验(0)
        baggage = Baggage.create(
            type=data['type'],
            travellerId=data['traveller_id'],
            flightNo=data['flight_no'],
            status=0  # 待检验
            # travelBeginTime=travel_begin_time
        )

        return jsonify({
            "code": 201,
            "message": "行李添加成功",
            "data": {
                "type": baggage.type,
                "traveller_id": baggage.travellerId,
                "flight_no": baggage.flightNo,
                "status": baggage.status
            }
        }), 201

    except Exception as e:
        logger.error(f"添加行李失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"添加行李失败: {str(e)}",
            "data": None
        }), 500


@baggage.route("/<baggage_id>/status", methods=['PUT'])
@token_required
def updateBaggageStatus(current_user):
    """
    更新行李检验状态（需要token认证）
    请求体示例:
    {
        "baggage_id": 1,  // 行李ID
        "status": 1,  // 状态: 0-待检验, 1-已通过, 2-未通过
        "remark": "检验通过"  // 备注信息（可选）
    }
    """
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['baggage_id', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"缺少必需字段: {field}",
                    "data": None
                }), 400

        # 验证状态值
        if data['status'] not in [0, 1, 2]:
            return jsonify({
                "code": 400,
                "message": "状态值无效，必须是 0(待检验), 1(已通过), 2(未通过)",
                "data": None
            }), 400

        # 查找行李记录
        try:
            baggage = Baggage.get(
                (Baggage.id == data['baggage_id']) &
                (Baggage.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "行李记录不存在",
                "data": None
            }), 404

        # 更新状态
        Baggage.update(
            status=data['status']
        ).where(
            (Baggage.id == data['baggage_id']) &
            (Baggage.isDeleted == False)
        ).execute()

        # 重新获取更新后的行李信息
        baggage = Baggage.get_by_id(data['baggage_id'])

        return jsonify({
            "code": 200,
            "message": "行李状态更新成功",
            "data": {
                "id": baggage.id,
                "traveller_id": baggage.travellerId,
                "flight_no": baggage.flightNo,
                "status": baggage.status,
                "status_text": BAGGAGE_STATUS[baggage.status],
                "update_time": datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"更新行李状态失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"更新行李状态失败: {str(e)}",
            "data": None
        }), 500


@baggage.route("/", methods=['GET'])
@token_required
def getBaggageList(current_user):
    """
    获取当前用户的行李列表（需要token认证）
    查询参数:
    - status: 按状态筛选 (0,1,2)
    - flight_no: 按航班号筛选
    """
    try:
        status_filter = request.args.get('status', type=int)
        flight_no_filter = request.args.get('flight_no')

        # 构建查询条件
        query = Baggage.select().where(Baggage.isDeleted == False)

        # 关联查询旅客信息，确保只返回当前用户的行李
        travellers = Traveller.select(Traveller.travellerId).where(
            (Traveller.uid == current_user.uid) &
            (Traveller.isDeleted == False)
        )
        traveller_ids = [t.travellerId for t in travellers]

        query = query.where(Baggage.travellerId.in_(traveller_ids))

        # 应用状态筛选
        if status_filter is not None and status_filter in [0, 1, 2]:
            query = query.where(Baggage.status == status_filter)

        # 应用航班号筛选
        if flight_no_filter:
            query = query.where(Baggage.flightNo == flight_no_filter)

        # 按创建时间倒序排列
        query = query.order_by(Baggage.createTime.desc())

        baggage_list = []
        for baggage in query:
            # 获取旅客信息
            try:
                traveller = Traveller.get(
                    (Traveller.travellerId == baggage.travellerId) &
                    (Traveller.isDeleted == False)
                )
                traveller_name = traveller.travellerName
            except DoesNotExist:
                traveller_name = "未知旅客"

            baggage_list.append({
                "id": baggage.id,
                "type": baggage.type,
                "traveller_id": baggage.travellerId,
                "traveller_name": traveller_name,
                "flight_no": baggage.flightNo,
                "status": baggage.status,
                "status_text": BAGGAGE_STATUS[baggage.status],
                "travel_begin_time": baggage.travelBeginTime.isoformat(),
                "create_time": baggage.createTime.isoformat()
            })

        return jsonify({
            "code": 200,
            "message": "成功获取行李列表",
            "data": baggage_list
        })

    except Exception as e:
        logger.error(f"获取行李列表失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取行李列表失败: {str(e)}",
            "data": None
        }), 500


@baggage.route("/<int:baggage_id>", methods=['GET'])
@token_required
def getBaggageDetail(current_user, baggage_id):
    """
    获取行李详细信息（需要token认证）
    """
    try:
        # 查找行李记录
        try:
            baggage = Baggage.get(
                (Baggage.id == baggage_id) &
                (Baggage.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "行李记录不存在",
                "data": None
            }), 404

        # 检查行李是否属于当前用户
        try:
            traveller = Traveller.get(
                (Traveller.travellerId == baggage.travellerId) &
                (Traveller.uid == current_user.uid) &
                (Traveller.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 403,
                "message": "无权访问该行李信息",
                "data": None
            }), 403

        # 获取航班信息
        try:
            flight = FlightInfo.get(
                (FlightInfo.flightNo == baggage.flightNo) &
                (FlightInfo.isDeleted == False)
            )
            flight_info = {
                "departure": flight.departure,
                "destination": flight.destination,
                "airline": flight.airline
            }
        except DoesNotExist:
            flight_info = None

        return jsonify({
            "code": 200,
            "message": "成功获取行李详情",
            "data": {
                "id": baggage.id,
                "type": baggage.type,
                "traveller_id": baggage.travellerId,
                "traveller_name": traveller.travellerName,
                "traveller_tel": traveller.travellerTel,
                "flight_no": baggage.flightNo,
                "flight_info": flight_info,
                "status": baggage.status,
                "status_text": BAGGAGE_STATUS[baggage.status],
                "travel_begin_time": baggage.travelBeginTime.isoformat(),
                "create_time": baggage.createTime.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"获取行李详情失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取行李详情失败: {str(e)}",
            "data": None
        }), 500


@baggage.route("/<int:baggage_id>/stats", methods=['GET'])
@token_required
def getBaggageStats(current_user):
    """
    获取行李统计信息（需要token认证）
    """
    try:
        # 获取当前用户的旅客ID列表
        travellers = Traveller.select(Traveller.travellerId).where(
            (Traveller.uid == current_user.uid) &
            (Traveller.isDeleted == False)
        )
        traveller_ids = [t.travellerId for t in travellers]

        # 统计各状态行李数量
        stats = {}
        for status in [0, 1, 2]:
            count = Baggage.select().where(
                (Baggage.travellerId.in_(traveller_ids)) &
                (Baggage.status == status) &
                (Baggage.isDeleted == False)
            ).count()
            stats[BAGGAGE_STATUS[status]] = count

        # 统计总数
        total = sum(stats.values())
        stats['总计'] = total

        return jsonify({
            "code": 200,
            "message": "成功获取行李统计信息",
            "data": stats
        })

    except Exception as e:
        logger.error(f"获取行李统计信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取行李统计信息失败: {str(e)}",
            "data": None
        }), 500


@baggage.route("/<int:baggage_id>", methods=['DELETE'])
@token_required
def deleteBaggage(current_user, baggage_id):
    """
    删除行李记录（逻辑删除，需要token认证）
    """
    try:
        # 查找行李记录
        try:
            baggage = Baggage.get(
                (Baggage.id == baggage_id) &
                (Baggage.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "行李记录不存在",
                "data": None
            }), 404

        # 检查行李是否属于当前用户
        try:
            traveller = Traveller.get(
                (Traveller.travellerId == baggage.travellerId) &
                (Traveller.uid == current_user.uid) &
                (Traveller.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 403,
                "message": "无权删除该行李记录",
                "data": None
            }), 403

        # 执行逻辑删除
        updated_count = Baggage.update(
            isDeleted=True
        ).where(
            (Baggage.id == baggage_id) &
            (Baggage.isDeleted == False)
        ).execute()

        if updated_count > 0:
            return jsonify({
                "code": 200,
                "message": "行李删除成功",
                "data": None
            })
        else:
            return jsonify({
                "code": 500,
                "message": "行李删除失败",
                "data": None
            }), 500

    except Exception as e:
        logger.error(f"删除行李失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"删除行李失败: {str(e)}",
            "data": None
        }), 500


@baggage.route("/flight/<flight_no>", methods=['GET'])
@token_required
def getBaggageByFlight(current_user, flight_no):
    """
    按航班号查询行李信息（需要token认证）
    """
    try:
        # 检查航班是否存在
        try:
            flight = FlightInfo.get(
                (FlightInfo.flightNo == flight_no) &
                (FlightInfo.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "航班不存在",
                "data": None
            }), 404

        # 获取当前用户在该航班的行李
        travellers = Traveller.select(Traveller.travellerId).where(
            (Traveller.uid == current_user.uid) &
            (Traveller.isDeleted == False)
        )
        traveller_ids = [t.travellerId for t in travellers]

        baggage_list = Baggage.select().where(
            (Baggage.travellerId.in_(traveller_ids)) &
            (Baggage.flightNo == flight_no) &
            (Baggage.isDeleted == False)
        ).order_by(Baggage.createTime.desc())

        result = []
        for baggage in baggage_list:
            # 获取旅客信息
            try:
                traveller = Traveller.get(
                    (Traveller.travellerId == baggage.travellerId) &
                    (Traveller.isDeleted == False)
                )
                traveller_name = traveller.travellerName
            except DoesNotExist:
                traveller_name = "未知旅客"

            result.append({
                "id": baggage.id,
                "type": baggage.type,
                "traveller_id": baggage.travellerId,
                "traveller_name": traveller_name,
                "status": baggage.status,
                "status_text": BAGGAGE_STATUS[baggage.status],
                "travel_begin_time": baggage.travelBeginTime.isoformat()
            })

        return jsonify({
            "code": 200,
            "message": f"成功获取航班 {flight_no} 的行李信息",
            "data": {
                "flight_no": flight_no,
                "departure": flight.departure,
                "destination": flight.destination,
                "baggage_list": result
            }
        })

    except Exception as e:
        logger.error(f"按航班查询行李失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"按航班查询行李失败: {str(e)}",
            "data": None
        }), 500

@baggage.route("/status", methods=['POST'])
@token_required
def getBaggageStatus(current_user):
    """
    更新行李检验状态（需要token认证）
    请求体示例:
    {
        "traveller_id": "213"
    }
    """
    try:

        data = request.get_json()

        baggage = list(Baggage.select().where(
            (Baggage.travellerId == data['traveller_id']) &
            (Baggage.isDeleted == False)
        ).dicts())
    except DoesNotExist:
        return jsonify({
            "code": 404,
            "message": "行李记录不存在",
            "data": None
        }), 404
    return jsonify({
        "code": 200,
        "message": "行李状态更新成功",
        "data": baggage
    })