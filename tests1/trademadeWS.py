import websocket
import threading
import time

f = open("webSocketTester.log", "a")

def on_message(ws, message):
    print(message)
    f.write(message + "\n")
    f.flush()

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        ws.send("{\"userKey\":\"wsmROkg7SDuR_q-bQApg\", \"symbol\":\"XAUUSD\"}")
    threading.Thread(target=run).start()

if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://marketdata.tradermade.com/feedadv",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
