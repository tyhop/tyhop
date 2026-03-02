from flask import Blueprint, request, jsonify
from peewee import DoesNotExist
from com.tgu.mapper.Entitys import *
from com.tgu.controller.SysUserController import token_required
import logging
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

flight_info = Blueprint('flight_info', __name__)


@flight_info.route("/", methods=['GET'])
@token_required
def addFlightInfo(current_user):
    """
    添加航班信息（需要token认证）
    请求体示例:
    {
        "flight_no": "CA1234",
        "departure": "北京",
        "destination": "上海",
        "period": "每日",
        "airline": "中国国际航空"
    }
    """
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['flight_no', 'departure', 'destination', 'period', 'airline']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"缺少必需字段: {field}",
                    "data": None
                }), 400

        # 检查航班号是否已存在
        if FlightInfo.select().where(
                (FlightInfo.flightNo == data['flight_no']) &
                (FlightInfo.isDeleted == False)
        ).exists():
            return jsonify({
                "code": 400,
                "message": "航班号已存在",
                "data": None
            }), 400

        # 创建航班信息
        flight = FlightInfo.create(
            flightNo=data['flight_no'],
            departure=data['departure'],
            destination=data['destination'],
            period=data['period'],
            airline=data['airline']
        )

        return jsonify({
            "code": 201,
            "message": "航班信息添加成功",
            "data": {
                "id": flight.id,
                "flight_no": flight.flightNo,
                "departure": flight.departure,
                "destination": flight.destination,
                "period": flight.period,
                "airline": flight.airline,
                "create_time": flight.createTime.isoformat()
            }
        }), 201

    except Exception as e:
        logger.error(f"添加航班信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"添加航班信息失败: {str(e)}",
            "data": None
        }), 500


@flight_info.route("/", methods=['POST'])
@token_required
def getFlightList(current_user):
    """
    获取航班列表（需要token认证）
    查询参数:
    - airline: 航空公司，为空时选取所有航空公司
    - departure: 出发地
    - destination: 目的地
    - departure_date: 出发日期
    """
    try:

        data = request.get_json()

        airline = data['airline']
        departure = data['departure']
        destination = data['destination']
        departure_date = data['departure_date']

        # 基础查询，排除已删除的记录
        query = FlightInfo.select().where(FlightInfo.isDeleted == False)

        # 航空公司筛选（如果提供且不为空）
        if airline:
            query = query.where(FlightInfo.airline == airline)
        # 如果airline为空或None，不添加条件（选取所有航空公司）

        # 出发地筛选
        if departure:
            query = query.where(FlightInfo.departure == departure)

        # 目的地筛选
        if destination:
            query = query.where(FlightInfo.destination == destination)

        # 起飞日期筛选（匹配到日）
        if departure_date:
            # 将日期转换为星期几的中文名称
            target_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            target_weekday = weekdays[target_date.weekday()]

            # 构建匹配模式：时间部分可以任意，但星期几必须匹配
            # period格式如："10:30:00/12:30:00/星期三"
            pattern = f'%/%/{target_weekday}'

            query = query.where(FlightInfo.period ** (f'%{pattern}'))

        # 按创建时间倒序排列
        query = query.order_by(FlightInfo.createTime.desc())


        flight_list = []
        for flight in query:
            flight_list.append({
                "flight_no": flight.flightNo,
                "departure": flight.departure,
                "destination": flight.destination,
                "period": flight.period,
                "airline": flight.airline,
            })

        return jsonify({
            "code": 200,
            "message": "成功获取航班列表",
            "data": flight_list
        })

    except Exception as e:
        logger.error(f"获取航班列表失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取航班列表失败: {str(e)}",
            "data": None
        }), 500


@flight_info.route("/<flight_no>", methods=['GET'])
@token_required
def getFlightDetail(current_user, flight_no):
    """
    获取航班详细信息（需要token认证）
    """
    try:
        # 查找航班记录
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

        # 获取该航班的行李统计信息
        baggage_stats = {
            "total": 0,
            "pending": 0,
            "passed": 0,
            "failed": 0
        }

        try:
            # 统计各状态行李数量
            baggage_stats['total'] = Baggage.select().where(
                (Baggage.flightNo == flight_no) &
                (Baggage.isDeleted == False)
            ).count()

            baggage_stats['pending'] = Baggage.select().where(
                (Baggage.flightNo == flight_no) &
                (Baggage.status == 0) &
                (Baggage.isDeleted == False)
            ).count()

            baggage_stats['passed'] = Baggage.select().where(
                (Baggage.flightNo == flight_no) &
                (Baggage.status == 1) &
                (Baggage.isDeleted == False)
            ).count()

            baggage_stats['failed'] = Baggage.select().where(
                (Baggage.flightNo == flight_no) &
                (Baggage.status == 2) &
                (Baggage.isDeleted == False)
            ).count()
        except Exception as e:
            logger.warning(f"获取航班行李统计失败: {str(e)}")

        return jsonify({
            "code": 200,
            "message": "成功获取航班详情",
            "data": {
                "id": flight.id,
                "flight_no": flight.flightNo,
                "departure": flight.departure,
                "destination": flight.destination,
                "period": flight.period,
                "airline": flight.airline,
                "create_time": flight.createTime.isoformat(),
                "baggage_stats": baggage_stats
            }
        })

    except Exception as e:
        logger.error(f"获取航班详情失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取航班详情失败: {str(e)}",
            "data": None
        }), 500


@flight_info.route("/<flight_no>", methods=['PUT'])
@token_required
def updateFlightInfo(current_user):
    """
    更新航班信息（需要token认证）
    请求体示例:
    {
        "flight_no": "CA1234",
        "departure": "北京首都",
        "destination": "上海浦东",
        "period": "每周一、三、五",
        "airline": "中国国际航空公司"
    }
    """
    try:
        data = request.get_json()

        if 'flight_no' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少航班号",
                "data": None
            }), 400

        # 查找航班记录
        try:
            flight = FlightInfo.get(
                (FlightInfo.flightNo == data['flight_no']) &
                (FlightInfo.isDeleted == False)
            )
        except DoesNotExist:
            return jsonify({
                "code": 404,
                "message": "航班不存在",
                "data": None
            }), 404

        # 更新字段
        update_fields = {}
        if 'departure' in data:
            update_fields[FlightInfo.departure] = data['departure']
        if 'destination' in data:
            update_fields[FlightInfo.destination] = data['destination']
        if 'period' in data:
            update_fields[FlightInfo.period] = data['period']
        if 'airline' in data:
            update_fields[FlightInfo.airline] = data['airline']

        if update_fields:
            FlightInfo.update(**update_fields).where(
                (FlightInfo.flightNo == data['flight_no']) &
                (FlightInfo.isDeleted == False)
            ).execute()
            # 重新获取更新后的航班信息
            flight = FlightInfo.get(
                (FlightInfo.flightNo == data['flight_no']) &
                (FlightInfo.isDeleted == False)
            )

        return jsonify({
            "code": 200,
            "message": "航班信息更新成功",
            "data": {
                "id": flight.id,
                "flight_no": flight.flightNo,
                "departure": flight.departure,
                "destination": flight.destination,
                "period": flight.period,
                "airline": flight.airline
            }
        })

    except Exception as e:
        logger.error(f"更新航班信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"更新航班信息失败: {str(e)}",
            "data": None
        }), 500


@flight_info.route("/<flight_no>", methods=['DELETE'])
@token_required
def deleteFlightInfo(current_user, flight_no):
    """
    删除航班信息（逻辑删除，需要token认证）
    """
    try:
        # 查找航班记录
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

        # 检查是否有关联的行李记录
        baggage_count = Baggage.select().where(
            (Baggage.flightNo == flight_no) &
            (Baggage.isDeleted == False)
        ).count()

        if baggage_count > 0:
            return jsonify({
                "code": 400,
                "message": f"该航班有 {baggage_count} 件关联行李，无法删除",
                "data": None
            }), 400

        # 执行逻辑删除
        updated_count = FlightInfo.update(
            isDeleted=True
        ).where(
            (FlightInfo.flightNo == flight_no) &
            (FlightInfo.isDeleted == False)
        ).execute()

        if updated_count > 0:
            return jsonify({
                "code": 200,
                "message": "航班删除成功",
                "data": None
            })
        else:
            return jsonify({
                "code": 500,
                "message": "航班删除失败",
                "data": None
            }), 500

    except Exception as e:
        logger.error(f"删除航班失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"删除航班失败: {str(e)}",
            "data": None
        }), 500


@flight_info.route("/search", methods=['GET'])
@token_required
def searchFlights(current_user):
    """
    搜索航班信息（需要token认证）
    查询参数:
    - keyword: 搜索关键词（航班号、出发地、目的地、航空公司）
    """
    try:
        keyword = request.args.get('keyword')

        if not keyword:
            return jsonify({
                "code": 400,
                "message": "请输入搜索关键词",
                "data": None
            }), 400

        # 构建搜索查询
        query = FlightInfo.select().where(
            (FlightInfo.isDeleted == False) &
            (
                    (FlightInfo.flightNo.contains(keyword)) |
                    (FlightInfo.departure.contains(keyword)) |
                    (FlightInfo.destination.contains(keyword)) |
                    (FlightInfo.airline.contains(keyword))
            )
        ).order_by(FlightInfo.createTime.desc())

        flight_list = []
        for flight in query:
            flight_list.append({
                "id": flight.id,
                "flight_no": flight.flightNo,
                "departure": flight.departure,
                "destination": flight.destination,
                "period": flight.period,
                "airline": flight.airline,
                "create_time": flight.createTime.isoformat()
            })

        return jsonify({
            "code": 200,
            "message": f"找到 {len(flight_list)} 条匹配的航班信息",
            "data": flight_list
        })

    except Exception as e:
        logger.error(f"搜索航班失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"搜索航班失败: {str(e)}",
            "data": None
        }), 500


@flight_info.route("/stats", methods=['GET'])
@token_required
def getFlightStats(current_user):
    """
    获取航班统计信息（需要token认证）
    """
    try:
        # 统计航班总数
        total_flights = FlightInfo.select().where(FlightInfo.isDeleted == False).count()

        # 统计各航空公司航班数量
        airline_stats = {}
        airlines = FlightInfo.select(FlightInfo.airline).where(FlightInfo.isDeleted == False).distinct()

        for airline in airlines:
            count = FlightInfo.select().where(
                (FlightInfo.airline == airline.airline) &
                (FlightInfo.isDeleted == False)
            ).count()
            airline_stats[airline.airline] = count

        # 统计热门出发地
        departure_stats = {}
        departures = FlightInfo.select(FlightInfo.departure).where(FlightInfo.isDeleted == False).distinct()

        for departure in departures:
            count = FlightInfo.select().where(
                (FlightInfo.departure == departure.departure) &
                (FlightInfo.isDeleted == False)
            ).count()
            departure_stats[departure.departure] = count

        # 统计热门目的地
        destination_stats = {}
        destinations = FlightInfo.select(FlightInfo.destination).where(FlightInfo.isDeleted == False).distinct()

        for destination in destinations:
            count = FlightInfo.select().where(
                (FlightInfo.destination == destination.destination) &
                (FlightInfo.isDeleted == False)
            ).count()
            destination_stats[destination.destination] = count

        return jsonify({
            "code": 200,
            "message": "成功获取航班统计信息",
            "data": {
                "total_flights": total_flights,
                "airline_stats": airline_stats,
                "departure_stats": departure_stats,
                "destination_stats": destination_stats
            }
        })

    except Exception as e:
        logger.error(f"获取航班统计信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取航班统计信息失败: {str(e)}",
            "data": None
        }), 500


@flight_info.route("/<flight_no>/baggage", methods=['GET'])
@token_required
def getFlightBaggage(current_user, flight_no):
    """
    获取航班行李详情（需要token认证）
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

        # 获取该航班的所有行李
        baggage_list = Baggage.select().where(
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
                traveller_info = {
                    "name": traveller.travellerName,
                    "tel": traveller.travellerTel
                }
            except DoesNotExist:
                traveller_info = {"name": "未知旅客", "tel": "未知"}

            # 行李状态文本
            status_text = {
                0: "待检验",
                1: "已通过",
                2: "未通过"
            }.get(baggage.status, "未知状态")

            result.append({
                "id": baggage.id,
                "type": baggage.type,
                "traveller_id": baggage.travellerId,
                "traveller_info": traveller_info,
                "status": baggage.status,
                "status_text": status_text,
                "travel_begin_time": baggage.travelBeginTime.isoformat(),
                "create_time": baggage.createTime.isoformat()
            })

        return jsonify({
            "code": 200,
            "message": f"成功获取航班 {flight_no} 的行李信息",
            "data": {
                "flight_info": {
                    "flight_no": flight.flightNo,
                    "departure": flight.departure,
                    "destination": flight.destination,
                    "airline": flight.airline
                },
                "baggage_list": result,
                "total_count": len(result)
            }
        })

    except Exception as e:
        logger.error(f"获取航班行李信息失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"获取航班行李信息失败: {str(e)}",
            "data": None
        }), 500
