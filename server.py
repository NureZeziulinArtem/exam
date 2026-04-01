import socket
import threading
import queue
import json
import time

HOST = '127.0.0.1'
PORT = 9999
BOARD_SIZE = 100
WIN_COUNT = 5

board = [[' '] * BOARD_SIZE for _ in range(BOARD_SIZE)]
request_queue = queue.Queue(maxsize=50)
game_over = False

def check_win(row, col, symbol):
    dirs = [(0,1), (1,0), (1,1), (1,-1)]
    for dr, dc in dirs:
        cnt = 1
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == symbol:
            cnt += 1
            r += dr
            c += dc
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == symbol:
            cnt += 1
            r -= dr
            c -= dc
        if cnt >= WIN_COUNT:
            return True
    return False

def process_queue():
    global game_over
    while True:
        item = request_queue.get()
        time.sleep(0.1)
        if game_over:
            resp = {'status': 'error', 'message': 'Гра вже закінчена'}
            item['sock'].sendto(json.dumps(resp).encode(), item['addr'])
            request_queue.task_done()
            continue

        row = item['row']
        col = item['col']
        sym = item['symbol']

        if board[row][col] != ' ':
            resp = {'status': 'error', 'message': 'Клітинка зайнята'}
        else:
            board[row][col] = sym
            if check_win(row, col, sym):
                game_over = True
                resp = {'status': 'win', 'symbol': sym, 'row': row, 'col': col}
                print(f'Виграв {sym} на позиції ({row},{col})')
            else:
                resp = {'status': 'ok', 'symbol': sym, 'row': row, 'col': col, 'queue': request_queue.qsize()}

        item['sock'].sendto(json.dumps(resp, ensure_ascii=False).encode(), item['addr'])
        request_queue.task_done()

def run_server():
    t = threading.Thread(target=process_queue, daemon=True)
    t.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f'Сервер запущено {HOST}:{PORT}')
    print(f'Черга: 50, Дошка: {BOARD_SIZE}x{BOARD_SIZE}, Виграш: {WIN_COUNT} підряд')

    while True:
        data, addr = sock.recvfrom(1024)
        try:
            req = json.loads(data.decode())
            req['addr'] = addr
            req['sock'] = sock

            if request_queue.full():
                resp = {'status': 'queue_full', 'message': 'Черга переповнена, спробуй пізніше'}
                sock.sendto(json.dumps(resp, ensure_ascii=False).encode(), addr)
                print(f'Черга повна! Відхилено від {addr}')
            else:
                request_queue.put(req)
                print(f'Отримано {req["symbol"]} ({req["row"]},{req["col"]}) від {addr} | черга: {request_queue.qsize()}/50')

        except Exception as e:
            print(f'Помилка: {e}')

if __name__ == '__main__':
    run_server()
