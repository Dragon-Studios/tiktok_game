import time
import threading
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent
from pymongo import MongoClient


def get_database():
   CONNECTION_STRING = "mongodb://localhost:27017"
   client = MongoClient(CONNECTION_STRING)
   return client['tiktok_game']


dbname = get_database()
collection_name = dbname["player"]


# Instantiate the client with the user's username
client: TikTokLiveClient = TikTokLiveClient(unique_id="@juniormanella")


# Define how you want to handle specific events via decorator
@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)

# Notice no decorator?
async def on_comment(event: CommentEvent):
    print(f"{event.user.nickname} -> {event.comment}")


# @client.on("disconnect")
# async def on_disconnect(event: DisconnectEvent):
#     print("Disconnected")
#
#
# @client.on("like")
# async def on_like(event: LikeEvent):
#     print(f"@{event.user.unique_id} liked the stream!")
#
#
# @client.on("join")
# async def on_join(event: JoinEvent):
#     print(f"@{event.user.unique_id} joined the stream!")
#
#
# @client.on("follow")
# async def on_follow(event: FollowEvent):
#     print(f"@{event.user.unique_id} followed the streamer!")
#
#
# @client.on("share")
# async def on_share(event: ShareEvent):
#     print(f"@{event.user.unique_id} shared the stream!")
#
#

users_dict = {}
html = ""

def on_gift(gift):

    damage = 0
    power = 0
    if gift.user.is_subscriber:
        power = 5
        damage = power * float(gift.gift.info.diamond_count)

    elif gift.user.is_following:
        power = 2
        damage = power * float(gift.gift.info.diamond_count)
    else:
        power = 1
        damage = power * float(gift.gift.info.diamond_count)


    if not gift.user.user_id in users_dict:

        users_dict[gift.user.user_id] = {
                "_id": gift.user.user_id,
                'nick': gift.user.nickname,
                'is_following': gift.user.is_following,
                'is_subscriber': gift.user.is_subscriber,
                'is_friend': gift.user.is_friend,
                'hp': 100,
                'damage': 0
        }

    if gift.user.user_id in users_dict:
        users_dict[gift.user.user_id]['damage'] += damage


    player = collection_name.find_one({'_id': users_dict[gift.user.user_id]['_id']})
    if player is not None:
        collection_name.update_one({'_id': users_dict[gift.user.user_id]['_id']}, { "$set": users_dict[gift.user.user_id] })
        print("UPDATED!", users_dict[gift.user.user_id]['nick'])
    else:
        collection_name.insert_one(users_dict[gift.user.user_id])
        print("INSERTED!", users_dict[gift.user.user_id]['nick'])


# Define handling an event via a "callback"
# client.add_listener("comment", on_comment)
client.add_listener("connect", on_connect)
# client.add_listener("disconnect", on_disconnect)
# client.add_listener("like", on_like)
# client.add_listener("join", on_join)
# client.add_listener("follow", on_follow)
# client.add_listener("share", on_share)
client.add_listener("gift", on_gift)


if __name__ == '__main__':
    client.run()
