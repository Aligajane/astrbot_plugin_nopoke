from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import time

@register("nopoke", "Pudding", "戳一戳的小插件", "1.0.0", "https://github.com/Aligajane/astrbot_plugin_nopoke")
class NoPokePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 用于记录每个用户戳一戳的次数和时间
        self.poke_count = {}

    @filter.poke()  # 监听戳一戳事件
    async def on_poke(self, event: AstrMessageEvent):
        """被戳一戳后根据次数回复不同内容"""
        user_id = event.get_sender_id()  # 获取戳一戳的用户ID
        current_time = time.time()  # 当前时间戳

        if user_id not in self.poke_count:
            # 如果用户第一次戳，初始化计数和时间
            self.poke_count[user_id] = {"count": 1, "last_time": current_time}
            yield event.plain_result("别戳啦！")
        else:
            # 如果用户已经戳过，检查时间间隔和计数
            last_time = self.poke_count[user_id]["last_time"]
            self.poke_count[user_id]["count"] += 1
            self.poke_count[user_id]["last_time"] = current_time

            count = self.poke_count[user_id]["count"]
            if count == 2:
                yield event.plain_result("生气了！")
            elif count == 3:
                yield event.plain_result("戳回去！")
                # 模拟戳回去的操作（具体实现取决于平台适配器）
                await self.poke_back(event)
            elif count == 4:
                yield event.plain_result("还戳！不理你了！")
            elif count >= 5:
                # 第五次及以后不做任何操作
                return

        # 如果超过1分钟没有被戳，重置计数
        if current_time - last_time > 60:
            self.poke_count[user_id]["count"] = 1

    async def poke_back(self, event: AstrMessageEvent):
        """模拟戳回去的操作"""
        if event.get_platform_name() == "aiocqhttp":
            # 如果是 AIoCQHTTP 平台，调用戳一戳的 API
            from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
            assert isinstance(event, AiocqhttpMessageEvent)
            client = event.bot
            await client.call_action(
                "send_msg",
                user_id=event.get_sender_id(),
                message_type="private",
                message="戳回去！"
            )
            await client.call_action(
                "send_msg",
                user_id=event.get_sender_id(),
                message_type="private",
                message="[CQ:poke,qq={}]".format(event.get_sender_id())
            )
        else:
            # 其他平台暂不支持戳回去
            yield event.plain_result("戳回去功能暂不支持当前平台！")
