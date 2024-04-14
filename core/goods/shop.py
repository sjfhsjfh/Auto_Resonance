# TODO: 1.数据模型化 2.提高可读性

import itertools
import json
from decimal import Decimal, ROUND_HALF_UP
from itertools import combinations
from typing import Dict, List, Literal, Tuple

from loguru import logger

from core.models.city_goods import (
    CityDataModel,
    RouteModel,
    RoutesModel,
    SkillLevelModel,
)
from ..models.goods import GoodsModel
from ..models.config import RunningBusinessModel, config as config_model


def round5(x):
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def show(routes: RoutesModel):
    route = routes.city_data
    to_goods_num = ",".join(
        [f"{name}{route[0].goods_data[name].num}" for name in route[0].goods_data]
    )
    back_goods_num = ",".join(
        [f"{name}{route[1].goods_data[name].num}" for name in route[1].goods_data]
    )
    profit = route[0].profit + route[1].profit
    book = route[0].book + route[1].book
    city_tired = route[0].city_tired + route[1].city_tired
    tired_profit = round5(profit / city_tired)
    book_profit = book and round5(profit / book)
    message = f"""{route[0].buy_city_name}<->{route[0].sell_city_name}:
{route[0].buy_city_name}:
    商品数量: {to_goods_num}
    商品总量: {route[0].num}
    购买价格: {route[0].buy_price}
    出售价格: {route[0].sell_price}
    商品利润: {route[0].profit}
    所需疲劳: {route[0].city_tired}
    疲劳利润: {route[0].tired_profit}
    单书利润: {route[0].book_profit}
    书本数量: {route[0].book}
{route[0].sell_city_name}:
    商品数量: {back_goods_num}
    商品总量: {route[1].num}
    购买价格: {route[1].buy_price}
    出售价格: {route[1].sell_price}
    商品利润: {route[1].profit}
    所需疲劳: {route[1].city_tired}
    疲劳利润: {route[1].tired_profit}
    单书利润: {route[1].book_profit}
    书本数量: {route[1].book}
总计:
    利润: {profit}
    所需疲劳: {city_tired}
    疲劳利润: {tired_profit}
    单书利润: {book_profit}
    书本数量: {book}"""

    return message


with open("resources/goods/CityGoodsData.json", "r", encoding="utf-8") as file:
    city_goods_data = json.load(file)

with open("resources/goods/CityData.json", "r", encoding="utf-8") as file:
    city_data = json.load(file)

with open("resources/goods/AttachedToCityData.json", "r", encoding="utf-8") as file:
    attached_to_city_data: dict = json.load(file)

with open("resources/goods/CityTiredData.json", "r", encoding="utf-8") as file:
    city_tired_data: dict = json.load(file)

skill_data = {
    "朱利安": {1: {"goods": ["斑节虾"], "param": 0.2}},
    "狮鬃": {
        1: {"goods": ["荧光棒"], "param": 0.2},
        4: {"goods": ["扬声器"], "param": 0.2},
    },
    "魇": {1: {"goods": ["刀具"], "param": 0.2}, 5: {"goods": ["刀具"], "param": 0.1}},
    "塞西尔": {
        4: {"goods": ["香水"], "param": 0.2},
        5: {"goods": ["香水"], "param": 0.3},
    },
    "雷火": {4: {"goods": ["曼德工具箱"], "param": 0.2}},
    "黛丝莉": {
        4: {"goods": ["毛绒玩具"], "param": 0.2},
        5: {"goods": ["毛绒玩具"], "param": 0.1},
    },
    "艾略特": {4: {"goods": ["游戏卡带", "游戏机"], "param": 0.2}},
    "多萝西": {
        4: {"goods": ["弹丸加速装置"], "param": 0.2},
        5: {"goods": ["弹丸加速装置"], "param": 0.1},
    },
    "星花": {1: {"goods": ["人工晶花"], "param": 0.2}},
    "瑞秋": {4: {"goods": ["医药品"], "param": 0.2}},
    "菲妮娅": {
        4: {"goods": ["大龙虾"], "param": 0.2},
        5: {"goods": ["大龙虾"], "param": 0.1},
    },
    "瓦伦汀": {
        4: {"goods": ["学会书籍"], "param": 0.2},
        5: {"goods": ["学会书籍"], "param": 0.1},
    },
    "阿知波": {
        4: {"goods": ["拼装模型"], "param": 0.2},
        5: {"goods": ["拼装模型"], "param": 0.1},
    },
    "闻笙": {
        4: {"goods": ["限定公仔"], "param": 0.2},
        5: {"goods": ["限定公仔"], "param": 0.1},
    },
    "山岚": {4: {"goods": ["折扇"], "param": 0.2}},
    "叶珏": {
        1: {"goods": ["红茶"], "param": 0.2},
        4: {"goods": ["家用太阳能电池组"], "param": 0.2},
        5: {"goods": ["红茶"], "param": 0.1},
    },
    "隼": {
        1: {"goods": ["发动机"], "param": 0.2},
        4: {"goods": ["弹丸加速装置", "发动机", "沃德烤鸡", "红茶"], "param": -0.005},
        5: {"goods": ["斑节虾", "人工晶花", "桦石发财树", "石墨烯"], "param": -0.005},
    },
    "奈弥": {
        1: {"goods": ["金箔酒"], "param": 0.2},
        5: {"goods": ["金箔酒"], "param": 0.1},
    },
    "伊尔": {
        1: {"goods": ["阿妮塔101民用无人机"], "param": 0.2},
        5: {"goods": ["阿妮塔101民用无人机"], "param": 0.1},
    },
    "卡洛琳": {
        4: {"goods": ["石墨烯"], "param": 0.2},
        5: {"goods": ["石墨烯"], "param": 0.1},
    },
}
config = config_model.running_business.model_copy()


class SHOP:
    def __init__(self, goods_data: GoodsModel, city_book: Dict[str, int], skill_level: Dict[str, int], station_level: Dict[str, int], max_goods_num: int) -> None:
        """
        说明:
            跑商基类
        参数:
            :param goods_data: 商品数据
            :param city_book: 城市最大单次进货书
            :param skill_level: 角色共振等级
            :param station_level: 站点声望等级等级
            :param max_goods_num: 最大商品数量
        """
        self.goods_data = goods_data
        self.buy_goods = self.goods_data.buy_goods
        """城市可购买的商品信息"""
        self.sell_goods = self.goods_data.sell_goods
        """城市可出售的商品信息"""
        self.config = config
        """配置信息"""
        self.city_book = city_book
        """城市最大单次进货书"""
        self.goods_addition: Dict[str, int] = self.get_goods_addition(skill_level)
        """商品附加"""
        self.all_city_info: Dict[str, CityDataModel] = self.get_city_data_by_city_level(station_level)
        """城市税率等声望信息"""
        self.max_goods_num = max_goods_num
        """最大商品数量"""

    def get_goods_addition(self, skill_level: Dict[str, int]) -> Dict[str, int]:
        goods_addition: dict = {}
        """商品附加"""
        for role_name, role_level in skill_level.items():
            role_skill_data = skill_data.get(role_name, [])

            for skill_affect in role_skill_data:
                if role_level >= int(skill_affect):
                    goods, param = (
                        role_skill_data[skill_affect]["goods"],
                        role_skill_data[skill_affect]["param"],
                    )

                    for good_name in goods:
                        if good_name not in goods_addition:
                            goods_addition[good_name] = param
                        else:
                            goods_addition[good_name] += param
        return goods_addition

    def get_city_data_by_city_level(
        self,
        city_level: Dict[str, int],
    ) -> Dict[str, CityDataModel]:
        city_level_data = {}
        for attached_name, city_name in attached_to_city_data.items():
            if city_name not in city_level.keys():
                continue
            level = city_level[city_name] + 1
            city_level_data[attached_name] = CityDataModel.model_validate(
                city_data[city_name][level]
            )
        return city_level_data

    def get_good_buy_price(self, price, num, city_name, good_name, type_="go"):
        """
        说明:
            获取购买商品的价格
        参数:
            :param price: 商品价格
            :param num: 商品数量
            :param city_name: 城市名称
            :param good_name: 商品名称
            :param type_: 列车方向 go/back
        """
        buy_num = self.all_city_info.get(
            city_name, CityDataModel()
        ).buy_num  # 城市声望数量加成
        skill_num = self.goods_addition.get(good_name, 0)  # 角色技能增加的数量
        new_num = round5(num * (1 + buy_num + skill_num))
        tax_rate = self.all_city_info[city_name].revenue  # 税率
        new_price = round5(
            price  # 砍价前的价格
            * (
                1
                - getattr(
                    config, type_, RunningBusinessModel.GoBackModel()
                ).cut_price.percentage
                + tax_rate
            )
        )  # 砍价后的价格
        return new_price, new_num

    def get_good_sell_price(
        self, buy_price: int, city_name: str, good_name: str, type_="go"
    ):
        """
        说明:
            获取出售商品的价格
        参数:
            :param buy_price: 购买价格
            :param city_name: 城市名称
            :param good_name: 商品名称
            :param type_: 列车方向 go/back
        """
        base_sell_price = self.sell_goods[city_name][
            good_name
        ].price  # 不带税的售价，砍抬前
        no_revenue_sell_price = round5(
            base_sell_price
            * (
                1
                + getattr(
                    config, type_, RunningBusinessModel.GoBackModel()
                ).raise_price.percentage
            )
        )  # 不带税的售价, 抬价后
        tax_rate = self.all_city_info[city_name].revenue  # 税率
        no_tax_profit = no_revenue_sell_price - buy_price  # 不带税的利润, 单个商品
        revenue = (no_revenue_sell_price - buy_price) * tax_rate  # 税收

        new_sell_price = round5((no_revenue_sell_price - revenue))
        return new_sell_price, no_tax_profit

    def get_pending_purchase(self, buy_city_name: str, sell_city_name: str, type_="go"):
        """
        说明:
            获取需要购买的物品的信息
        参数:
            :param buy_city_name: 购买城市名称
            :param sell_city_name: 出售城市名称
        """
        goods = self.buy_goods[buy_city_name]
        sorted_goods = sorted(
            goods.items(), key=lambda item: item[1].isSpeciality, reverse=True
        )
        # 总疲劳
        city_tired = (
            city_tired_data.get(f"{buy_city_name}-{sell_city_name}", 99999)
            + getattr(
                config, type_, RunningBusinessModel.GoBackModel()
            ).raise_price.profit
            + getattr(
                config, type_, RunningBusinessModel.GoBackModel()
            ).cut_price.profit
        )
        target: RouteModel = RouteModel(
            buy_city_name=buy_city_name,
            sell_city_name=sell_city_name,
            city_tired=city_tired,
        )
        while (
            target.num < self.max_goods_num
            and target.book < self.city_book[buy_city_name]
        ):  # 直到货仓被装满
            target.book += 1
            for name, good in sorted_goods:
                if name not in self.sell_goods[sell_city_name]:
                    # logger.error(f"{sell_city_name}没有{name}的数据")
                    continue
                buy_price, buy_num = self.get_good_buy_price(
                    good.price, good.num, buy_city_name, name
                )
                num = min(
                    buy_num,
                    self.max_goods_num - target.num,
                )  # 确保购买数量不超过最大商品数量
                # print(f"{buy_city_name}:{name}=>{buy_price} {buy_num}")
                sell_price, profit = self.get_good_sell_price(
                    buy_price, sell_city_name, name
                )
                all_profit = profit * num
                # print(f"{buy_city_name}<=>{sell_city_name}:{name}=>{sell_price} {rate_price}")
                if profit >= self.city_book["priceThreshold"] or good.isSpeciality:
                    target.buy_goods.append(name)
                    target.goods_data.setdefault(name, RouteModel.GoodsData())
                    target.goods_data[name].num += num
                    target.goods_data[name].buy_price += buy_price
                    target.goods_data[name].sell_price += sell_price
                    target.goods_data[name].profit += all_profit
                    target.num += num
                    target.profit += all_profit
                    target.buy_price += buy_price * num
                    target.sell_price += sell_price * num
                else:
                    target.normal_goods.setdefault(name, 0)
                    target.normal_goods[name] += all_profit
        target.tired_profit = round5(target.profit / city_tired)
        target.book_profit = target.book and round5(target.profit / target.book)
        return target

    def get_route_profit(self, type_="go"):
        """
        说明:
            获取路线利润
        参数:
            :param type_: 列车方向 go/back
            :return: 路线数据
        """
        routes: List[RoutesModel] = []
        for city1, city2 in itertools.combinations(set(self.buy_goods.keys()), 2):
            if city1 not in self.all_city_info or city2 not in self.all_city_info:
                continue
            city_routes = RoutesModel()
            target1 = self.get_pending_purchase(city1, city2)
            target2 = self.get_pending_purchase(city2, city1)
            city_routes.city_data = [target1, target2]
            # 总计
            city_routes.book = (
                city_routes.city_data[0].book + city_routes.city_data[1].book
            )
            city_routes.city_tired = (
                city_routes.city_data[0].city_tired
                + city_routes.city_data[1].city_tired
            )
            city_routes.profit = (
                city_routes.city_data[0].profit + city_routes.city_data[1].profit
            )
            city_routes.tired_profit = round5(
                city_routes.profit / city_routes.city_tired
            )
            city_routes.book_profit = round5(city_routes.profit / city_routes.book)
            routes.append(city_routes)
        return routes

    def get_optimal_route(self):
        """
        说明:
            获取往返路线的最优路线
        """
        # TODO 也许需要改成异步
        routes = self.get_route_profit("back")
        benchmark_profit = sum(route.book_profit for route in routes) / len(routes)

        optimal_route = max(
            (route for route in routes if route.book_profit > benchmark_profit),
            key=lambda route: route.tired_profit,
            default=RoutesModel(),  # 如果没有符合条件的对象，返回None
        )
        """
        for good in routes:
            logger.info(show(good))
        """
        optimal_route.city_data[0].normal_goods = {
            k: v
            for k, v in sorted(
                optimal_route.city_data[0].normal_goods.items(),
                key=lambda item: item[1],
            )
        }
        optimal_route.city_data[1].normal_goods = {
            k: v
            for k, v in sorted(
                optimal_route.city_data[1].normal_goods.items(),
                key=lambda item: item[1],
            )
        }
        return optimal_route