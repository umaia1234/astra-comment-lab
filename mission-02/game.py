"""Confession Counter: a small fictional campus comedy.

Run: python game.py. Requires Pillow. Character art is in character-sheet.png.
No network, accounts, or save files are used by the game.
"""
import math
import random
import time
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk

HERE = Path(__file__).resolve().parent
W, H = 1100, 800
INK, PAPER, RED = '#282439', '#fff5e8', '#e0506f'

ROUNDS = [
    {
        'name': '복도에서 마주쳤다',
        'line': '“길 좀 비켜. 너, 나 좋아하냐?”',
        'hint': '선배의 허세에 첫 번째 카운터를 날려 보세요.',
        'choices': [
            ('네. 그래서요?', 19, 9, 3, 5, '“...뭐? 보통 여기서 아니라고 하지 않아?”'),
            ('좋아하면 통행료 할인돼요?', 17, 6, 16, 0, '“내가 무슨 톨게이트냐고... 아, 웃으면 안 되는데.”'),
            ('아, 아니요! 절대로요!', 1, -6, 0, 0, '“그렇게까지 부정할 건 없잖아. 뭔가 더 수상한데?”'),
        ],
    },
    {
        'name': '예상 못 한 역질문',
        'line': '“말은 잘하네. 내 어디가 좋은데?”',
        'hint': '농담으로 밀어붙일지, 진심을 섞을지 골라 보세요.',
        'choices': [
            ('센 척해도 길고양이 밥 챙겨주잖아요.', 22, 17, 0, 19, '“그걸... 봤어? 그건 그냥 남은 참치가 있어서...”'),
            ('얼굴이요. 나머지는 알아가는 중.', 17, 8, 13, 3, '“점수 매기지 마. ...그래서 첫인상은 몇 점인데?”'),
            ('잠시만요. 외운 멘트를 까먹었어요.', 2, -4, 4, 0, '“푸흡. 연습까지 했어? 이번엔 내가 이겼네.”'),
        ],
    },
    {
        'name': '마지막 한마디',
        'line': '“그럼 제대로 말해봐. 이번엔 안 놀릴게.”',
        'hint': '마지막 선택이 결말을 바꿉니다. 박자를 잡아 보세요.',
        'choices': [
            ('장난은 끝. 오늘 저랑 같이 걸을래요?', 22, 18, 0, 20, '“...응. 대신 네가 먼저 간다고 했으니까 도망가기 없기.”'),
            ('고백도 예약제예요? 제 번호표는 1번.', 21, 9, 18, 0, '“대체 어디까지 준비해 온 거야! 아 진짜, 졌다 졌어.”'),
            ('사실... 축제 티켓 한 장만 사 주세요.', 12, -5, 20, 0, '“뭐야! 지금까지 영업이었어?! 한 장만 줘 봐.”'),
        ],
    },
]

ENDINGS = {
    'date': ('S', '오늘 저녁, 둘이서', '“너 진짜... 사람 당황하게 하네.”',
             '세게만 보이던 선배가 먼저 보폭을 맞췄습니다.\n고백 공격은, 뜻밖에도 정공법이었습니다.', 3),
    'counter': ('A', '선배, 할 말을 잃다', '“알았어. 내가 졌어. 그러니까 웃지 마!”',
                '허세 가득하던 선배가 웃음을 참지 못했습니다.\n오늘의 승부는 당신의 한마디 승리.', 2),
    'sales': ('?', '고백은 미끼였다', '“축제 끝나고 넌 나 좀 보자.”',
              '고백 대신 티켓 한 장을 팔았습니다.\n매출 +1. 내일의 운명은 미정.', 1),
    'reflect': ('C', '고백이 반사되었습니다', '“다음엔 연습 좀 더 하고 와.”',
                '혼내 주려던 쪽이 오히려 혼났습니다.\n하지만 선배는 웃고 있었습니다. 한 번 더 해 볼까요?', 0),
}


def timing_grade(position):
    distance = abs(position - .5)
    if distance <= .075:
        return 'PERFECT', 13, '#e0506f'
    if distance <= .21:
        return 'GOOD', 7, '#32a184'
    return 'MISS', 0, '#777188'


def decide_ending(history, stats):
    if history[-1] == 2:
        return 'sales'
    if stats['heart'] >= 34 and stats['honesty'] >= 30:
        return 'date'
    if stats['fluster'] >= 44 and stats['wit'] >= 24:
        return 'counter'
    return 'reflect'


class Game:
    def __init__(self, root):
        self.root = root
        self.c = tk.Canvas(root, width=W, height=H, bg=PAPER, highlightthickness=0)
        self.c.pack()
        self.root.title('ASTRA LAB — 댓글 미션 02')
        self.root.resizable(False, False)
        self.sprites = []
        image_path = HERE / 'character-sheet.png'
        sheet = Image.open(image_path).convert('RGBA')
        # The generated atlas has uneven gutters; use the observed frame bounds
        # so a neighboring sleeve is not sampled into another expression.
        frame_bounds = [(0, .247), (.252, .50), (.516, .750), (.765, 1.0)]
        for left, right in frame_bounds:
            cell = sheet.crop((int(left*sheet.width), 0, int(right*sheet.width), sheet.height))
            bounds = cell.getbbox()
            if bounds:
                cell = cell.crop(bounds)
            cell.thumbnail((400, 460), Image.Resampling.LANCZOS)
            self.sprites.append(ImageTk.PhotoImage(cell))
        self.buttons = []
        self.hover = None
        self.particles = []
        self.seen_endings = set()
        self.last_clock = time.perf_counter()
        self.opened = self.last_clock
        self.mode = 'menu'
        self.pointer = .5
        self.keys_down = set()
        self.ending = None
        self.c.bind('<Motion>', self.motion)
        self.c.bind('<Button-1>', self.click)
        root.bind('<KeyPress>', self.key)
        root.bind('<KeyRelease>', self.key_up)
        self.draw_background()
        self.tick()

    def draw_background(self):
        c = self.c
        c.create_rectangle(0, 0, W, H, fill=PAPER, outline='', tags='back')
        c.create_rectangle(646, 79, 1100, 549, fill='#f9d0bd', outline='', tags='back')
        c.create_oval(709, 105, 1110, 503, fill='#ffc872', outline='', tags='back')
        for i in range(7):
            x = 653 + i * 88
            c.create_line(x, 80, x - 70, 550, fill='#ecb69f', width=2, tags='back')
        c.create_rectangle(0, 0, 1100, 78, fill=INK, outline='', tags='back')
        c.create_line(40, 550, 1060, 550, fill='#e5d4c8', width=2, tags='back')

    def text(self, x, y, value, size=16, color=INK, weight='normal', width=0, anchor='nw', **kwargs):
        return self.c.create_text(x, y, text=value, fill=color, anchor=anchor,
                                  font=('Malgun Gothic', size, weight), width=width,
                                  tags='d', **kwargs)

    def box(self, x, y, w, h, fill, outline='', radius=16):
        r = min(radius, w / 2, h / 2)
        pts = [x+r,y,x+w-r,y,x+w,y,x+w,y+r,x+w,y+h-r,x+w,y+h,x+w-r,y+h,
               x+r,y+h,x,y+h,x,y+h-r,x,y+r,x,y,x+r,y]
        return self.c.create_polygon(pts, smooth=True, splinesteps=12, fill=fill,
                                     outline=outline, width=2, tags='d')

    def button(self, key, x, y, w, h, label, action, filled=False, sub=None):
        hover = self.hover == key
        bg = RED if filled else ('#ffe1df' if hover else '#fffaf3')
        fg = '#fffaf3' if filled else INK
        self.box(x, y, w, h, bg, '' if filled else ('#e0506f' if hover else '#dccdc4'))
        self.text(x+21, y+h/2, label, 17 if h < 65 else 19, fg, 'bold', anchor='w')
        if sub:
            self.text(x+w-20, y+h/2, sub, 12, fg, anchor='e')
        self.buttons.append((key, x, y, x+w, y+h, action))

    def start(self):
        self.stats = {'fluster': 0, 'heart': 0, 'wit': 0, 'honesty': 0}
        self.shown_fluster = 0
        self.history = []
        self.round = 0
        self.selected = None
        self.grade = None
        self.ending = None
        self.mode = 'choice'
        self.opened = time.perf_counter()
        self.particles.clear()

    def choose(self, index):
        if self.mode != 'choice':
            return
        self.selected = index
        self.mode = 'timing'
        self.opened = time.perf_counter()

    def fire(self):
        if self.mode != 'timing':
            return
        self.grade, bonus, self.grade_color = timing_grade(self.pointer)
        choice = ROUNDS[self.round]['choices'][self.selected]
        self.stats['fluster'] = min(100, self.stats['fluster'] + choice[1] + bonus)
        self.stats['heart'] += choice[2] + bonus // 3
        self.stats['wit'] += choice[3]
        self.stats['honesty'] += choice[4]
        self.history.append(self.selected)
        self.mode = 'reaction'
        self.opened = time.perf_counter()
        if bonus:
            for _ in range(24):
                self.particles.append([random.uniform(630, 980), random.uniform(260, 470),
                                       random.uniform(-60, 60), random.uniform(-110, -45),
                                       random.uniform(.6, 1.3), random.choice(['♥', '✦', '+'])])

    def advance(self):
        if self.mode != 'reaction':
            return
        if self.round < 2:
            self.round += 1
            self.mode = 'choice'
        else:
            self.mode = 'ending'
            self.ending = decide_ending(self.history, self.stats)
            self.seen_endings.add(self.ending)
        self.opened = time.perf_counter()

    def motion(self, event):
        self.hover = next((b[0] for b in self.buttons if b[1] <= event.x <= b[3] and b[2] <= event.y <= b[4]), None)
        self.c.configure(cursor='hand2' if self.hover else 'arrow')

    def click(self, event):
        for _, x1, y1, x2, y2, action in self.buttons:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                action()
                return

    def key(self, event):
        key = event.keysym.lower()
        if key in self.keys_down:
            return
        self.keys_down.add(key)
        if key == 'escape':
            self.mode = 'menu'
        elif self.mode == 'menu' and key in ('return', 'space'):
            self.start()
        elif self.mode == 'choice' and key in ('1', '2', '3'):
            self.choose(int(key)-1)
        elif self.mode == 'timing' and key in ('space', 'return'):
            self.fire()
        elif self.mode == 'reaction' and key in ('space', 'return'):
            self.advance()
        elif self.mode == 'ending' and key in ('return', 'r'):
            self.start()

    def key_up(self, event):
        self.keys_down.discard(event.keysym.lower())

    def typewriter(self, value, speed=32):
        return value[:max(1, int((time.perf_counter()-self.opened)*speed))]

    def portrait(self, expression=0):
        bob = math.sin(time.perf_counter()*1.65)*3
        x = 855
        if self.mode == 'reaction' and time.perf_counter()-self.opened < .32:
            x += math.sin((time.perf_counter()-self.opened)*55)*7
        self.c.create_image(x, 547+bob, image=self.sprites[expression], anchor='s', tags='d')

    def draw(self):
        c = self.c
        c.delete('d')
        self.buttons = []
        self.text(39, 23, 'ASTRA LAB 02', 14, '#eeb1c2', 'bold')
        self.text(286, 19, '고백 공격', 22, PAPER, 'bold')
        self.text(1059, 36, '댓글로 고른 1분 로맨틱 코미디', 12, '#ccc5d7', anchor='e')
        if self.mode == 'menu':
            self.portrait(0)
            self.text(47, 110, 'CONFESSION COUNTER', 12, RED, 'bold')
            self.text(45, 162, '오늘은 내가\n당황시킨다.', 43, INK, 'bold', 605)
            self.box(48, 332, 566, 123, '#fffaf3', '#e8d5c7')
            self.text(67, 352, '허세 가득한 선배에게 고백으로 반격!\n할 말을 고르고, 박자에 맞춰 한마디.\n선택과 타이밍이 다른 결말을 만듭니다.', 16, INK, width=525)
            self.text(51, 490, '3번의 대화  /  4가지 결말  /  실패해도 다시 한 판', 13, '#766876')
            self.button('start', 48, 589, 565, 79, '시작하기', self.start, True, 'ENTER')
            self.text(49, 691, '선택: 마우스 또는 1·2·3   |   타이밍: SPACE   |   메뉴: ESC', 12, '#7e7281')
            self.text(49, 751, '가상의 대학생 캐릭터가 등장하는 코미디입니다.', 11, '#91838c')
            self.text(1029, 737, f'발견한 결말 {len(self.seen_endings)} / 4', 13, RED, 'bold', anchor='e')
            return

        expression = 0
        if self.mode == 'timing':
            expression = 1
        elif self.mode == 'reaction':
            expression = 2 if self.stats['fluster'] > 18 else 0
        elif self.mode == 'ending':
            expression = ENDINGS[self.ending][4]
        self.portrait(expression)
        self.text(49, 107, f'ROUND {self.round + 1:02d} / 03', 12, RED, 'bold')
        self.text(49, 145, ROUNDS[self.round]['name'], 28, INK, 'bold')
        self.text(48, 216, '선배 당황도', 13, '#7c6877', 'bold')
        self.box(47, 246, 441, 16, '#eadbd2', radius=8)
        if self.shown_fluster > 0:
            self.box(47, 246, 441*self.shown_fluster/100, 16, RED, radius=7)
        self.text(518, 251, f'{self.stats["fluster"]:02d}', 20, RED, 'bold', anchor='w')
        self.box(47, 311, 576, 192, '#fffdf7', '#e3cfc3')
        self.text(68, 332, '한서린  ·  동아리 선배', 13, RED, 'bold')
        current_line = ROUNDS[self.round]['line']
        if self.mode == 'reaction':
            current_line = ROUNDS[self.round]['choices'][self.selected][5]
        if self.mode == 'ending':
            current_line = ENDINGS[self.ending][2]
        self.text(68, 381, self.typewriter(current_line) if self.mode != 'timing' else current_line,
                  21, INK, 'bold', 527)

        if self.mode == 'choice':
            self.text(49, 526, ROUNDS[self.round]['hint'], 12, '#877580')
            for i, choice in enumerate(ROUNDS[self.round]['choices']):
                self.button(f'choice{i}', 47, 571+i*61, 1006, 51, f'{i+1}   {choice[0]}', lambda i=i:self.choose(i), sub=f'KEY {i+1}')
            self.text(1052, 775, '선택 후 SPACE로 말할 타이밍을 잡으세요.', 11, '#827481', anchor='e')
        elif self.mode == 'timing':
            self.text(51, 561, '내가 고른 한마디', 11, '#94767e')
            self.text(51, 585, ROUNDS[self.round]['choices'][self.selected][0], 18, INK, 'bold')
            self.box(50, 650, 697, 23, '#ded4d0', radius=10)
            self.box(50+697*.29, 650, 697*.42, 23, '#9fd8bf', radius=5)
            self.box(50+697*.425, 648, 697*.15, 27, '#e87e95', radius=3)
            px = 50+697*self.pointer
            c.create_polygon(px, 641, px-9, 627, px+9, 627, fill=INK, tags='d')
            c.create_line(px, 649, px, 677, fill=INK, width=3, tags='d')
            self.button('fire', 787, 632, 263, 59, '지금 말하기', self.fire, True, 'SPACE')
            self.text(52, 708, '분홍색 PERFECT  /  초록색 GOOD  /  바깥쪽 MISS', 13, '#7e6c78')
            self.text(52, 752, '타이밍이 좋으면 당황도가 더 올라갑니다. 선택은 취소할 수 없습니다.', 11, '#91818c')
        elif self.mode == 'reaction':
            self.text(49, 570, self.grade, 36, self.grade_color, 'bold')
            self.text(49, 632, f'“{ROUNDS[self.round]["choices"][self.selected][0]}”', 18, INK, width=680)
            label = '다음 대화' if self.round < 2 else '결말 보기'
            self.button('next', 787, 634, 263, 62, label, self.advance, True, 'ENTER')
            self.text(49, 735, '말 한마디가 분위기를 바꿨습니다.', 13, '#8d7482')
        elif self.mode == 'ending':
            rank, name, _, description, _ = ENDINGS[self.ending]
            self.box(47, 559, 1006, 211, '#fffdf7', '#e3cfc3')
            self.text(71, 582, f'{rank}  /  {name}', 26, RED, 'bold')
            self.text(73, 635, description, 16, INK, width=649)
            self.button('again', 789, 655, 239, 65, '다시 하기', self.start, True, 'R')
            self.text(73, 737, f'발견한 결말 {len(self.seen_endings)} / 4   ·   다른 대사를 골라 보세요.', 12, '#8b7785')

        for x, y, _, _, life, symbol in self.particles:
            self.text(x, y, symbol, int(12+life*8), RED, 'bold', anchor='center')

    def tick(self):
        now = time.perf_counter()
        dt = min(now-self.last_clock, .06)
        self.last_clock = now
        if self.mode == 'timing':
            self.pointer = .5 + .49*math.sin((now-self.opened)*2.4 - math.pi/2)
        if hasattr(self, 'stats'):
            self.shown_fluster += (self.stats['fluster']-self.shown_fluster)*min(1, dt*8)
        for p in self.particles:
            p[0] += p[2]*dt
            p[1] += p[3]*dt
            p[4] -= dt
        self.particles = [p for p in self.particles if p[4] > 0]
        self.draw()
        self.root.after(25, self.tick)


if __name__ == '__main__':
    main_root = tk.Tk()
    main_root.geometry(f'{W}x{H}')
    main_root.game = Game(main_root)
    main_root.mainloop()
