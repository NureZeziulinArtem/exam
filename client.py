import socket
import json
import time
import threading

HOST = '127.0.0.1'
PORT = 9999

def send_move(row, col, symbol):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        req = {'row': row, 'col': col, 'symbol': symbol}
        sock.sendto(json.dumps(req).encode(), (HOST, PORT))
        data, _ = sock.recvfrom(1024)
        return json.loads(data.decode())
    except socket.timeout:
        return {'status': 'error', 'message': 'timeout'}
    finally:
        sock.close()

def demo_moves():
    print('\nНевпорядковані ходи O,O,X,O,X,X')
    moves = [
        (10, 10, 'O'),
        (20, 10, 'O'),
        (10, 11, 'X'),
        (30, 10, 'O'),
        (10, 12, 'X'),
        (10, 13, 'X'),
    ]
    for row, col, sym in moves:
        resp = send_move(row, col, sym)
        print(f'{sym} -> ({row},{col}) : {resp["status"]} | {resp.get("message", "")}')
        time.sleep(0.2)

def demo_win():
    print('\nВиграш 5 підряд')
    for col in range(50, 55):
        resp = send_move(70, col, 'X')
        print(f'X -> (70,{col}) : {resp["status"]}')
        if resp['status'] == 'win':
            print(f'Виграш: {resp["symbol"]} на ({resp["row"]},{resp["col"]})')
            break
        time.sleep(0.1)

def demo_queue():
    print('\n60 одночасних запитів (черга 50)')
    results = []
    lock = threading.Lock()

    def worker(i):
        r = (i * 3) % 100
        c = (i * 7) % 100
        sym = 'X' if i % 2 == 0 else 'O'
        resp = send_move(r, c, sym)
        with lock:
            results.append(resp['status'])

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(60)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    ok = results.count('ok') + results.count('win')
    full = results.count('queue_full')
    print(f'Оброблено: {ok}, Відхилено (черга): {full}, Всього: {len(results)}')

def interactive():
    print('\nРучний режим')
    print('Приклад: 5 10 X')
    while True:
        inp = input('Хід: ').strip()
        if inp == 'exit':
            break
        try:
            r, c, sym = inp.split()
            resp = send_move(int(r), int(c), sym.upper())
            print(f'Відповідь: {resp}')
            if resp.get('status') == 'win':
                print(f'Виграш {resp["symbol"]}')
        except:
            print('Невірний формат')

if __name__ == '__main__':
    print('1. Невпорядковані ходи')
    print('2. Виграш')
    print('3. Черга (60 запитів)')
    print('4. Ручний режим')
    ch = input('Вибір: ')
    if ch == '1':
        demo_moves()
    elif ch == '2':
        demo_win()
    elif ch == '3':
        demo_queue()
    elif ch == '4':
        interactive()
