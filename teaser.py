"""A real interactive recording rehearsal, not the audience-selected mission."""
import math
import random
import time
import tkinter as tk

W, H = 1000, 740
root = tk.Tk()
root.title('ASTRA LAB — 구슬 놀이터 · 녹화 테스트')
root.geometry(f'{W}x{H}')
root.resizable(False, False)
root.configure(bg='#10121f')
canvas = tk.Canvas(root, width=W, height=H, bg='#10121f', highlightthickness=0)
canvas.pack()
FONT = '맑은 고딕'
colors = ['#ffc373', '#8edbdc', '#c1a4ff', '#fd93ad', '#a5df9b']
balls = []
gravity = 1
last = time.perf_counter()
elapsed = 0
flash = 0
frames = 0


def text(x, y, value, size=12, color='#b7bdcf', weight='normal', **kw):
    return canvas.create_text(x, y, text=value, fill=color, font=(FONT, size, weight), **kw)


def spawn(n=20):
    for _ in range(min(n, 140-len(balls))):
        r = random.uniform(10, 16)
        balls.append({'x': random.uniform(365, 700), 'y': random.uniform(168, 295),
                      'vx': random.uniform(-95, 95), 'vy': random.uniform(-40, 40),
                      'r': r, 'c': random.choice(colors)})


def flip():
    global gravity, flash
    gravity *= -1
    flash = 1.0


def reset():
    global gravity
    balls.clear()
    gravity = 1
    spawn(55)


def move(event):
    if 335 < event.x < 770 and 150 < event.y < 610:
        for b in balls:
            dx, dy = b['x']-event.x, b['y']-event.y
            d = math.hypot(dx, dy)
            if 1 < d < 160:
                b['vx'] += dx/d*35
                b['vy'] += dy/d*35


def button(x, y, label, fn, primary=False):
    b = tk.Button(root, text=label, command=fn, font=(FONT, 12, 'bold'),
                  bg='#c1a4ff' if primary else '#252b40', fg='#171427' if primary else '#eef0f7',
                  activebackground='#d3bfff', activeforeground='#171427', borderwidth=0,
                  cursor='hand2', padx=20, pady=12, takefocus=True)
    b.place(x=x, y=y, width=195, height=48)


button(50, 429, '구슬 20개 추가', spawn, True)
button(50, 491, '중력 뒤집기  ↕', flip)
button(50, 553, '처음부터', reset)
root.bind('<space>', lambda _: flip())
canvas.bind('<B1-Motion>', move)


def frame():
    global last, elapsed, flash, frames
    now = time.perf_counter()
    dt = min(now-last, 0.033)
    last = now
    elapsed += dt
    flash = max(0, flash-dt*1.7)
    frames += 1
    for _ in range(3):
        step = dt/3
        for b in balls:
            b['vy'] += 680*gravity*step
            b['vx'] *= 0.998
            b['x'] += b['vx']*step
            b['y'] += b['vy']*step
            if b['x'] < 342+b['r']:
                b['x'] = 342+b['r']; b['vx'] = abs(b['vx'])*0.72
            if b['x'] > 767-b['r']:
                b['x'] = 767-b['r']; b['vx'] = -abs(b['vx'])*0.72
            if b['y'] < 158+b['r']:
                b['y'] = 158+b['r']; b['vy'] = abs(b['vy'])*0.64
            if b['y'] > 609-b['r']:
                b['y'] = 609-b['r']; b['vy'] = -abs(b['vy'])*0.64
        for i, a in enumerate(balls):
            for b in balls[i+1:]:
                dx, dy = b['x']-a['x'], b['y']-a['y']
                rr = a['r']+b['r']
                d2 = dx*dx+dy*dy
                if 0.0001 < d2 < rr*rr:
                    d = math.sqrt(d2); nx, ny = dx/d, dy/d
                    overlap = (rr-d)*0.5
                    a['x'] -= nx*overlap; a['y'] -= ny*overlap
                    b['x'] += nx*overlap; b['y'] += ny*overlap
                    speed = (b['vx']-a['vx'])*nx+(b['vy']-a['vy'])*ny
                    if speed < 0:
                        impulse = -speed*0.77
                        a['vx'] -= impulse*nx; a['vy'] -= impulse*ny
                        b['vx'] += impulse*nx; b['vy'] += impulse*ny
    canvas.delete('all')
    # Application UI: all labels and animation are drawn by this running program.
    canvas.create_rectangle(0, 0, W, 91, fill='#191d2d', outline='')
    canvas.create_oval(42, 31, 69, 58, fill='#c1a4ff', outline='')
    text(85, 43, 'ASTRA LAB', 19, '#ffffff', 'bold', anchor='w')
    text(951, 43, 'INTERACTIVE EXPERIMENT  /  00', 11, '#8990a8', anchor='e')
    text(50, 147, '일단, 구슬부터', 23, '#f5f4fd', 'bold', anchor='w')
    text(50, 190, '뒤집어 봤습니다.', 23, '#c1a4ff', 'bold', anchor='w')
    text(50, 247, '여기는 녹화 테스트입니다.\n본 미션은 댓글로 정합니다.', 12, '#afb6cc', anchor='w', justify='left')
    text(50, 346, f'{len(balls):03}', 36, '#ffffff', 'bold', anchor='w')
    text(138, 358, '개의 구슬', 11, '#949cb5', anchor='w')
    # Ground and glass chamber.
    canvas.create_oval(300, 600, 832, 660, fill='#0b0d18', outline='')
    canvas.create_rectangle(326, 142, 783, 625, fill='#1a2437', outline='#495c7b', width=2)
    canvas.create_rectangle(338, 155, 770, 613, fill='#141b2b', outline='#273b54', width=1)
    for x in range(358, 760, 28):
        for y in range(176, 608, 28):
            canvas.create_oval(x, y, x+2, y+2, fill='#263249', outline='')
    for b in balls:
        x, y, r = b['x'], b['y'], b['r']
        canvas.create_oval(x-r+2, y-r+3, x+r+2, y+r+3, fill='#0b101c', outline='')
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=b['c'], outline='')
        canvas.create_oval(x-r*0.51, y-r*0.59, x-r*0.04, y-r*0.12, fill='#effaff', outline='')
    canvas.create_line(344, 171, 344, 592, fill='#687b9b', width=2)
    canvas.create_line(761, 171, 761, 592, fill='#324961', width=1)
    canvas.create_rectangle(318, 136, 791, 154, fill='#52617d', outline='')
    canvas.create_rectangle(318, 614, 791, 634, fill='#52617d', outline='')
    text(875, 212, 'GRAVITY', 10, '#808da8')
    text(875, 277, '↓' if gravity>0 else '↑', 58, '#c1a4ff' if flash<0.1 else '#ffffff')
    text(875, 335, '아래로' if gravity>0 else '위로', 13, '#d2d8e7')
    canvas.create_line(837, 379, 913, 379, fill='#333d54')
    text(875, 425, 'SPACE', 11, '#c1a4ff', 'bold')
    text(875, 452, '중력 반전', 11, '#949cb5')
    text(552, 673, '드래그로 휘젓기  ·  SPACE로 중력 뒤집기', 11, '#949cb5')
    text(50, 701, 'codex-astra  /  직접 실행 화면', 10, '#77809b', anchor='w')
    text(950, 701, '다음에는 무엇을 만들어 볼까요?', 11, '#c1a4ff', anchor='e')
    root.after(16, frame)


reset()
frame()
root.mainloop()
