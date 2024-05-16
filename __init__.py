import numpy as np
import random
from PIL import Image, ImageDraw


# 定义球的类
class Ball:
    def __init__(self, uid, size, color, speed, x, y):
        self.uid = uid
        self.size = size
        self.color = color
        self.speed = speed
        self.x = x  # 球的初始x坐标
        self.y = y  # 球的初始y坐标

    def move_towards(self, target_x, target_y):
        # 计算移动方向
        dx = target_x - self.x
        dy = target_y - self.y
        distance = np.sqrt(dx**2 + dy**2)

        # 防止除以零
        if distance == 0:
            return

        # 计算移动的单位向量
        dx /= distance
        dy /= distance

        # 根据速度移动球
        self.x += dx * self.speed
        self.y += dy * self.speed

    def eat(self, food_size):
        self.size += food_size
        self.speed = self.adjust_speed()

    def adjust_speed(self):
        # 根据大小调整速度
        return max(1, self.speed - 1)


# 定义用户类
class User:
    def __init__(self, uid, avatar_url, x, y):
        self.uid = uid
        self.avatar_url = avatar_url
        self.ball = self.create_ball(x, y)

    def create_ball(self, x, y):
        size = random.randint(1, 10)
        color = random.choice(["red", "green", "blue"])
        speed = random.randint(5, 10)
        return Ball(self.uid, size, color, speed, x, y)


# 地图和食物
class Map:
    def __init__(self, width, height, num_users):
        self.width = width
        self.height = height
        self.foods = self.generate_foods(num_users)
        self.balls = []

    def generate_foods(self, num_users):
        foods = []
        for _ in range(num_users * 2):
            food = (
                random.randint(0, self.width),
                random.randint(0, self.height),
                random.randint(1, 5),
            )
            foods.append(food)
        return np.array(foods)

    def remove_eaten_food(self, index):
        # 移除被吃掉的食物
        self.foods = np.delete(self.foods, index, axis=0)

    def add_ball(self, ball):
        self.balls.append(ball)

    def remove_ball(self, ball):
        self.balls.remove(ball)

    def generate_new_ball(self):
        # 生成新的球
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        size = random.randint(1, 10)
        color = random.choice(["red", "green", "blue"])
        speed = random.randint(1, 5)
        new_ball = Ball("NPC", size, color, speed, x, y)
        self.add_ball(new_ball)

    def add_food(self):
        # 新生成一个食物
        food = (
            random.randint(0, self.width),
            random.randint(0, self.height),
            random.randint(1, 5),
        )
        self.foods = np.vstack([self.foods, np.array(food)])


# 游戏逻辑
class Game:
    def __init__(self):
        self.users = {}
        self.map = Map(100, 100, 1)  # 假设只有一个用户
        self.images = []

    def add_user(self, user):
        self.users[user.uid] = user
        self.map.add_ball(user.ball)

    def simulate(self, num_rounds):
        for round_num in range(num_rounds):
            print(f"Round {round_num}")
            self.move_balls()
            self.eat_food()
            self.check_collisions()
            image = self.draw_map()
            self.images.append(image)

    def move_balls(self):
        for user in self.users.values():
            ball = user.ball
            # 寻找最近的食物
            closest_food_index = self.find_closest_food_index(ball)
            if closest_food_index is not None:
                closest_food = self.map.foods[closest_food_index]
                ball.move_towards(closest_food[0], closest_food[1])
                # 检查是否吃到食物
                print(ball.x,ball.y)
                print(closest_food)
                if self.check_eat_food(ball, closest_food):
                    ball.eat(closest_food[2])
                    self.map.remove_eaten_food(closest_food_index)
                    self.map.add_food()  # 新生成一个食物

    def eat_food(self):
        for user in self.users.values():
            ball = user.ball

            
            ball.eat(self.map.balls[0].size)  # 假设只有一个球
            self.map.remove_ball(self.map.balls[0])
            self.map.add_ball(self.map.generate_new_ball())

    def check_collisions(self):
        # 检查球之间的碰撞，这里简化处理，不做实际检测
        pass

    def draw_map(self):
        # 创建一个新的图像
        image_width = self.map.width  # 假设每个像素代表10个单位
        image_height = self.map.height 
        image = Image.new("RGB", (image_width, image_height), color="white")
        draw = ImageDraw.Draw(image)

        # 绘制食物
        for food in self.map.foods:
            x, y, size = food
            draw.ellipse(
                [
                    x  - size,
                    y  - size ,
                    x  + size ,
                    y  + size ,
                ],
                fill="black",
            )

        # 绘制球
        for ball in self.map.balls:
            if ball:
                x, y = ball.x, ball.y
                draw.ellipse(
                    [x - ball.size, y - ball.size, x + ball.size, y + ball.size],
                    fill=ball.color,
                )

        return image

    def find_closest_food_index(self, ball):
        # 使用NumPy计算最近的食物的索引
        distances = np.sqrt(
            (self.map.foods[:, 0] - ball.x) ** 2 + (self.map.foods[:, 1] - ball.y) ** 2
        )
        if np.any(distances):
            return np.argmin(distances)
        return None

    def check_eat_food(self, ball, food):
        # 检查球是否吃到食物
        distance = np.sqrt((food[0] - ball.x) ** 2 + (food[1] - ball.y) ** 2)
        return distance < ball.size

    def check_eat_ball(self, ball):
        return False


# 创建游戏实例
game = Game()

# 添加用户，提供初始位置
user1 = User("1", "http://example.com/avatar1.jpg", 50, 50)
game.add_user(user1)
# 添加用户，提供初始位置
user2 = User("2", "http://example.com/avatar1.jpg", 50, 50)
game.add_user(user2)
# 开始模拟
game.simulate(100)

# 创建GIF动画
import imageio

images = game.images

imageio.mimsave("game_animation.gif", images, duration=100)
