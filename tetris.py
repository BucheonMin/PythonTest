import pygame
import random

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 테트리스 블록 모양 정의
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

# 블록 색상
COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# 게임 설정
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# 키 반복 설정
REPEAT_DELAY = 200  # 키를 누르고 있을 때 첫 반복까지의 시간 (ms)
REPEAT_INTERVAL = 50  # 반복 간격 (ms)

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("테트리스")
        self.clock = pygame.time.Clock()
        
        # 키 반복 활성화
        pygame.key.set_repeat(REPEAT_DELAY, REPEAT_INTERVAL)
        
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()  # 다음 블록 추가
        self.game_over = False
        self.score = 0

    def new_piece(self):
        # 새로운 블록 생성
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape_idx],
            'color': COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }

    def valid_move(self, piece, x, y):
        # 이동이 유효한지 확인
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= GRID_WIDTH or
                        y + i >= GRID_HEIGHT or
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True

    def get_ghost_piece(self):
        # 고스트 블록의 위치 계산
        ghost_piece = self.current_piece.copy()
        while self.valid_move(ghost_piece, ghost_piece['x'], ghost_piece['y'] + 1):
            ghost_piece['y'] += 1
        return ghost_piece

    def lock_piece(self, piece):
        # 현재 블록을 그리드에 고정
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[piece['y'] + i][piece['x'] + j] = piece['color']

    def clear_lines(self):
        # 완성된 줄 제거
        lines_cleared = 0
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
        self.score += lines_cleared * 100

    def draw_grid(self):
        # 그리드 그리기
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, GRAY,
                               (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x],
                                   (x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1,
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2))

    def draw_piece(self, piece, offset_x=0, offset_y=0, ghost=False):
        # 블록 그리기
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if ghost:
                        # 고스트 블록은 반투명하게 그리기
                        ghost_surface = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2), pygame.SRCALPHA)
                        ghost_color = (*piece['color'][:3], 128)  # 알파값 128로 설정
                        pygame.draw.rect(ghost_surface, ghost_color, (0, 0, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                        self.screen.blit(ghost_surface, 
                                       ((piece['x'] + j + offset_x) * BLOCK_SIZE + 1,
                                        (piece['y'] + i + offset_y) * BLOCK_SIZE + 1))
                    else:
                        pygame.draw.rect(self.screen, piece['color'],
                                       ((piece['x'] + j + offset_x) * BLOCK_SIZE + 1,
                                        (piece['y'] + i + offset_y) * BLOCK_SIZE + 1,
                                        BLOCK_SIZE - 2, BLOCK_SIZE - 2))

    def draw_next_piece(self):
        # 다음 블록 미리보기 그리기
        next_x = GRID_WIDTH + 1
        next_y = 1
        
        # 미리보기 영역 배경
        pygame.draw.rect(self.screen, GRAY,
                        (next_x * BLOCK_SIZE, next_y * BLOCK_SIZE,
                         5 * BLOCK_SIZE, 5 * BLOCK_SIZE), 1)
        
        # "다음 블록" 텍스트
        font = pygame.font.Font(None, 30)
        text = font.render("다음 블록", True, WHITE)
        self.screen.blit(text, (next_x * BLOCK_SIZE, 5))
        
        # 다음 블록 그리기
        piece_x = next_x + (5 - len(self.next_piece['shape'][0])) // 2
        piece_y = next_y + (5 - len(self.next_piece['shape'])) // 2
        
        for i, row in enumerate(self.next_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece['color'],
                                   ((piece_x + j) * BLOCK_SIZE + 1,
                                    (piece_y + i) * BLOCK_SIZE + 1,
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2))

    def draw_score(self):
        # 점수 표시
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'점수: {self.score}', True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 200))

    def run(self):
        fall_time = 0
        fall_speed = 0.1  # 초당 블록이 떨어지는 속도 (0.2에서 0.1로 변경)

        while not self.game_over:
            fall_time += self.clock.get_rawtime()
            self.clock.tick(60)  # FPS 설정

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                            self.current_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                            self.current_piece['x'] += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                            self.current_piece['y'] += 1
                    elif event.key == pygame.K_UP:
                        # 블록 회전 (반시계 방향)
                        rotated = list(zip(*[row[::-1] for row in self.current_piece['shape']]))
                        if self.valid_move({'shape': rotated, 'x': self.current_piece['x'], 'y': self.current_piece['y']},
                                         self.current_piece['x'], self.current_piece['y']):
                            self.current_piece['shape'] = rotated
                    elif event.key == pygame.K_SPACE:  # 스페이스바로 즉시 떨어뜨리기
                        while self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                            self.current_piece['y'] += 1

            # 블록 자동 하강
            if fall_time >= fall_speed * 1000:
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                else:
                    self.lock_piece(self.current_piece)
                    self.clear_lines()
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
                        self.game_over = True
                fall_time = 0

            # 화면 그리기
            self.screen.fill(BLACK)
            self.draw_grid()
            
            # 고스트 블록 그리기
            ghost_piece = self.get_ghost_piece()
            self.draw_piece(ghost_piece, ghost=True)
            
            # 현재 블록 그리기
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_score()
            pygame.display.flip()

        # 게임 오버 메시지
        font = pygame.font.Font(None, 48)
        game_over_text = font.render('게임 오버!', True, WHITE)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)

if __name__ == '__main__':
    game = Tetris()
    game.run()
    pygame.quit() 