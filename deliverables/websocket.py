#!/usr/bin/env python


import asyncio
import websockets
import time
import pandas as pd 


df = pd.read_csv("five.csv")

print(list(df.columns))

dfloc = df[["coordinates.latitude","coordinates.longitude","order"]]
dfdata = df[["name","location.formatted_address","url","order"]]

# process the information and prepare for sending
# process the position part
ans = ''
for index, row in dfloc.iterrows():
    if row["order"] == None:
        continue
    elif row["order"] == 1 and index != 0:
        ans = ans[0:len(ans)-4]
        ans+='>>'
        ans+=str(row["coordinates.latitude"])+','+str(row["coordinates.longitude"])+'////'
    else:
        ans+=str(row["coordinates.latitude"])+','+str(row["coordinates.longitude"])+'////'
    # print(row["coordinates.latitude"],row["coordinates.longitude"])

ans = ans[0:len(ans)-4]
ans += '>>>>'

# process the name and location part
for index,row in dfdata.iterrows():
    if row["order"] == None:
        continue
    elif row["order"] == 1 and index != 0:
        ans +='>>'
        # ans+= '<p>'+str(row["name"])+'</br>'+str(row["location.formatted_address"])+'</br>'+str(row["url"])+'</p>\n\n\n'
        ans+= '<p>'+str(row["name"])+'</br>'+str(row["location.formatted_address"])+'</br>'+'</p>\n\n\n'
    else:
        ans+= '<p>'+str(row["name"])+'</br>'+str(row["location.formatted_address"])+'</br>'+'</p>\n\n\n'
        
        # ans+= '<p><a herf="'+str(row["url"])+'">'+str(row["name"])+'</a></br>'+str(row["location.formatted_address"])+'</p>\n'
    # print(row["name"],row["location.formatted_address"],row["url"])

ans = ans[0:len(ans)-4]
print(ans)

routinepts = ans

# send infomation to the javascript
async def hello(websocket, order):
    # name = await websocket.recv()
    # print(f"< {name}")
    await websocket.send(routinepts)
    print(f"> {routinepts}")
    
# async def echo_server(stop):
#     async with websockets.serve(echo, "localhost", 8080):
#         await stop

start_server = websockets.serve(hello, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
# asyncio.get_event_loop().run_until_complete(echo_server(stop))
